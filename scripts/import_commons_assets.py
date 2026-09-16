#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import sys
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

import requests
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "data" / "commons-asset-plan.json"
OUT_DIR = ROOT / "images"
MANIFEST_DIR = OUT_DIR / "_manifests"
API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "BENCAO-Mirror/4.0 (+https://github.com/sjunjie1212-zy/bencao-mirror; contact via repository issues)"
ROLES = ["hero", "specimen", "detail-01", "detail-02", "detail-03", "detail-04", "detail-05"]
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
BAD_WORDS = {
    "map", "distribution", "range", "logo", "icon", "stamp", "coin", "painting",
    "drawing", "illustration", "diagram", "herbarium", "specimen sheet", "pdf", "karyotype",
    "chromosome", "idiogram", "journal", "catalogue", "catalog", "woodcut", "refrigerator",
}
GENERIC_MATERIAL = {
    "dried", "dry", "slice", "slices", "seed", "seeds", "kernel", "kernels", "root", "rhizome",
    "fruit", "fruits", "berry", "berries", "bark", "cortex", "wood", "heartwood", "stem", "vine",
    "bud", "buds", "bulb", "tuber", "sclerotium", "drug", "medicine", "medicinal", "herb", "spice",
}
ALIASES = {
    "bc009": ["Glycyrrhiza inflata", "Glycyrrhiza glabra"],
    "bc011": ["Astragalus membranaceus", "Astragalus membranaceus var. mongholicus"],
    "bc012": ["Poria cocos", "Wolfiporia extensa"],
    "bc013": ["Coix lacryma-jobi"],
    "bc015": ["Cassia obtusifolia", "Cassia tora"],
    "bc022": ["Lilium pumilum", "Lilium brownii var. viridulum"],
    "bc023": ["Cinnamomum aromaticum"],
    "bc024": ["Eugenia caryophyllata", "Caryophyllus aromaticus"],
    "bc025": ["Amomum villosum var. xanthioides", "Wurfbainia villosa"],
    "bc027": ["Coptis deltoidea", "Coptis teeta", "Coptis japonica"],
    "bc029": ["Alisma plantago-aquatica", "Alisma plantago-aquatica subsp. orientale"],
    "bc034": ["Saussurea lappa"],
    "bc035": ["Spatholobus suberectus", "Spatholobi Caulis"],
    "bc036": ["Caesalpinia sappan"],
    "bc038": ["Aurantii Fructus Immaturus", "bitter orange"],
    "bc039": ["Citrus medica var. sarcodactylus"],
}

# Exact Commons files used only where normal taxonomic search is sparse or noisy.
# These are high-resolution references with a clear medicinal-material or crude-drug relationship.
MANUAL_TITLES = {
    "bc012": [
        "File:Tuckahoe.jpg",
        "File:Wolfiporia extensa cube.jpg",
    ],
    "bc025": [
        "File:Dried amomum villosum.jpg",
        "File:Sa nhân (Amomum villosum).JPG",
    ],
    "bc027": [
        "File:Coptis japonica、5026696、黄蓮・丹波市立薬草薬樹公園.JPG",
    ],
    "bc035": [
        "File:Spatholobus stem slices.jpg",
    ],
    "bc038": [
        "File:Citrus-aurantium-fruit.JPG",
        "File:Citrus × aurantium - fruits cut.jpg",
        "File:Citrus aurantium.jpg",
    ],
    # BC046 is overwritten by the separately validated formal seed set before final release.
    # These seed photographs keep the bulk importer complete without ever falling back to whole-plant imagery.
    "bc046": [
        "File:Plantain seeds.jpg",
        "File:Grote weegbree zaden (Plantago major subsp. major seeds).jpg",
        "File:Starr-130318-2625-Plantago major-seeds-Kilauea Pt NWR-Kauai (25207733525).jpg",
    ],
}


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = html.unescape(value)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def norm(value: str) -> str:
    value = clean_text(value).lower().replace("×", " ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def raw_norm(value: str) -> str:
    return re.sub(r"\s+", " ", clean_text(value).lower()).strip()


def meta_value(meta: dict, key: str) -> str:
    obj = meta.get(key) or {}
    return clean_text(obj.get("value") if isinstance(obj, dict) else str(obj))


def request_with_retry(session: requests.Session, url: str, *, params=None, timeout=(10, 45)) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(7):
        try:
            r = session.get(url, params=params, timeout=timeout)
            if r.status_code == 429:
                retry_after = r.headers.get("Retry-After")
                try:
                    delay = float(retry_after) if retry_after else 2.0 + attempt * 2.0
                except ValueError:
                    delay = 2.0 + attempt * 2.0
                time.sleep(min(delay, 15.0))
                continue
            r.raise_for_status()
            return r
        except Exception as exc:
            last_error = exc
            if attempt >= 6:
                break
            time.sleep(min(1.5 * (attempt + 1), 8.0))
    if last_error:
        raise last_error
    raise RuntimeError("request failed")


def taxa_for(herb: dict) -> list[str]:
    raw = [x.strip() for x in herb.get("plant", "").split("/") if x.strip()]
    raw.extend(ALIASES.get(herb["id"], []))
    out: list[str] = []
    for taxon in raw:
        n = norm(taxon)
        if n and n not in out:
            out.append(n)
    return out


def part_terms(herb: dict) -> tuple[set[str], set[str]]:
    part = herb.get("part", "")
    if "菌核" in part:
        return {"sclerotium", "poria"}, {"flower", "leaf", "leaves", "fruit"}
    if "心材" in part:
        return {"wood", "heartwood", "stem"}, {"flower", "leaf", "leaves", "fruit", "seed"}
    if any(x in part for x in ("树皮", "干皮", "根皮", "枝皮")):
        return {"bark", "cortex"}, {"flower", "leaf", "leaves", "fruit", "seed"}
    if "藤茎" in part:
        return {"stem", "vine", "caulis"}, {"flower", "leaf", "leaves", "fruit"}
    if "花蕾" in part or "初开的花" in part or part == "花":
        return {"flower", "flowers", "bud", "buds", "flos", "clove"}, {"root", "rhizome", "bark", "fruit", "seed"}
    if "种子" in part or "种仁" in part:
        return {"seed", "seeds", "kernel", "kernels", "semen"}, {"flower", "leaf", "leaves", "root", "bark"}
    if "幼果" in part:
        return {"fruit", "fruits", "immature", "unripe", "aurantium"}, {"flower", "leaf", "leaves", "root"}
    if "果实" in part or "果穗" in part:
        return {"fruit", "fruits", "berry", "berries", "plum", "jujube", "hawthorn", "citron"}, {"flower", "leaf", "leaves", "root", "bark"}
    if "鳞叶" in part:
        return {"bulb", "bulbs", "rhizome"}, {"flower", "fruit", "seed"}
    if "块根" in part or "块茎" in part:
        return {"tuber", "root", "rhizome"}, {"flower", "leaf", "leaves", "fruit", "seed"}
    if "根" in part or "根茎" in part:
        return {"root", "roots", "rhizome", "rhizomes", "radix"}, {"flower", "leaf", "leaves", "fruit", "seed"}
    return set(), set()


def search_expression(query: str, taxa: list[str]) -> str:
    qn = norm(query)
    chosen = next((t for t in taxa if t in qn or " ".join(t.split()[:2]) in qn), taxa[0] if taxa else "")
    genus_species = " ".join(chosen.split()[:2])
    extras = qn
    if chosen and chosen in extras:
        extras = extras.replace(chosen, " ")
    elif genus_species and genus_species in extras:
        extras = extras.replace(genus_species, " ")
    extras = re.sub(r"\s+", " ", extras).strip()
    return f'"{genus_species}" {extras}'.strip() if genus_species else query


def commons_search(session: requests.Session, query: str, limit: int = 50) -> list[dict]:
    params = {
        "action": "query", "format": "json", "formatversion": "2", "generator": "search",
        "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo|categories", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1800", "cllimit": "max",
    }
    r = request_with_retry(session, API, params=params, timeout=(10, 35))
    pages = (r.json().get("query") or {}).get("pages") or []
    pages.sort(key=lambda p: p.get("index", 999999))
    return pages


def commons_titles(session: requests.Session, titles: list[str]) -> list[dict]:
    if not titles:
        return []
    params = {
        "action": "query", "format": "json", "formatversion": "2", "titles": "|".join(titles),
        "prop": "imageinfo|categories", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1800", "cllimit": "max",
    }
    r = request_with_retry(session, API, params=params, timeout=(10, 35))
    return (r.json().get("query") or {}).get("pages") or []


def source_page(title: str) -> str:
    return "https://commons.wikimedia.org/wiki/" + quote(title.replace(" ", "_"), safe=":()_',.-、×")


def candidate_from_page(page: dict, herb: dict, query: str, qi: int, *, manual: bool = False) -> dict | None:
    info_list = page.get("imageinfo") or []
    if not info_list:
        return None
    info = info_list[0]
    mime = info.get("mime") or ""
    if mime not in ALLOWED_MIME:
        return None
    width = int(info.get("width") or 0)
    height = int(info.get("height") or 0)
    if max(width, height) < 700:
        return None
    title = page.get("title") or ""
    if not title.startswith("File:"):
        return None
    meta = info.get("extmetadata") or {}
    description = meta_value(meta, "ImageDescription")
    categories = " ".join(c.get("title", "") for c in (page.get("categories") or []))
    raw_combined = raw_norm(" ".join([title, description, categories]))
    combined = norm(raw_combined)
    if any(norm(word) in combined for word in BAD_WORDS):
        return None

    taxa = taxa_for(herb)
    taxon_match = manual or not taxa or any(t in combined or " ".join(t.split()[:2]) in combined for t in taxa)
    if not taxon_match:
        return None

    prefer, avoid = part_terms(herb)
    part_hits = sorted(w for w in prefer if w in combined)
    generic_hits = sorted(w for w in GENERIC_MATERIAL if w in combined)
    avoid_hits = sorted(w for w in avoid if w in combined)
    strong_hits = sorted(w for w in ("dried", "slice", "slices", "root", "roots", "rhizome", "seed", "seeds", "bark", "cortex", "stem", "wood", "tuber", "bulb", "sclerotium") if w in combined)

    score = min((width * height) / 1_500_000, 8.0)
    score += max(0, 5 - qi) * 2.0
    score += len(part_hits) * 12.0 + len(generic_hits) * 3.0 + len(strong_hits) * 5.0 - len(avoid_hits) * 8.0
    if manual:
        score += 80.0
    if "dried" in combined or "slice" in combined or "slices" in combined:
        score += 10.0

    return {
        "title": title,
        "url": info.get("thumburl") or info.get("url") or "",
        "original_url": info.get("url") or "",
        "description_url": info.get("descriptionurl") or source_page(title),
        "width": width, "height": height, "mime": mime,
        "author": meta_value(meta, "Artist"),
        "license": meta_value(meta, "LicenseShortName") or meta_value(meta, "UsageTerms"),
        "license_url": meta_value(meta, "LicenseUrl"),
        "description": description, "categories": categories, "query": query, "query_index": qi,
        "score": score, "manual": manual, "part_hits": part_hits, "generic_hits": generic_hits,
        "avoid_hits": avoid_hits, "strong_hits": strong_hits,
    }


def collect_candidates(session: requests.Session, herb: dict) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []

    def add(page: dict, query: str, qi: int, manual: bool = False) -> None:
        c = candidate_from_page(page, herb, query, qi, manual=manual)
        if not c or not c["url"] or c["title"] in seen:
            return
        seen.add(c["title"])
        out.append(c)

    manual_titles = MANUAL_TITLES.get(herb["id"], [])
    for page in commons_titles(session, manual_titles):
        add(page, "manual exact title", -20, manual=True)

    taxa = taxa_for(herb)
    queries = [q.strip() for q in (herb.get("queries") or []) if q and q.strip()]
    for qi, query in enumerate(queries):
        try:
            pages = commons_search(session, search_expression(query, taxa))
        except Exception as exc:
            print(f"WARN search failed {herb['id']} {query!r}: {exc}", file=sys.stderr)
            continue
        for page in pages:
            add(page, query, qi)
        if len(out) >= 35:
            break
        time.sleep(0.15)

    # Material-first: keep exact manual references and images whose metadata clearly mentions the medicinal part.
    material = [c for c in out if c["manual"] or c["part_hits"] or c["strong_hits"]]
    material = [c for c in material if c["manual"] or not (c["avoid_hits"] and not c["strong_hits"])]
    pool = material if material else out
    pool.sort(key=lambda x: (-x["score"], -(x["width"] * x["height"]), x["title"]))
    return pool


CENTERS = [(0.50, 0.50), (0.48, 0.50), (0.52, 0.48), (0.43, 0.52), (0.57, 0.52), (0.50, 0.43), (0.50, 0.57)]
ZOOMS = [1.00, 1.04, 1.13, 1.23, 1.34, 1.46, 1.58]


def save_variant(session: requests.Session, c: dict, dst: Path, target_w: int, target_h: int, quality: int, variant: int) -> None:
    r = request_with_retry(session, c["url"], timeout=(10, 55))
    with Image.open(BytesIO(r.content)) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode == "RGBA":
            bg = Image.new("RGB", im.size, (244, 240, 231))
            bg.paste(im, mask=im.getchannel("A"))
            im = bg
        else:
            im = im.convert("RGB")
        zoom = ZOOMS[variant % len(ZOOMS)]
        cx, cy = CENTERS[variant % len(CENTERS)]
        cw = max(1, int(im.width / zoom))
        ch = max(1, int(im.height / zoom))
        left = int((im.width - cw) * cx)
        top = int((im.height - ch) * cy)
        left = max(0, min(left, im.width - cw))
        top = max(0, min(top, im.height - ch))
        cropped = im.crop((left, top, left + cw, top + ch))
        fitted = ImageOps.fit(cropped, (target_w, target_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        dst.parent.mkdir(parents=True, exist_ok=True)
        fitted.save(dst, "WEBP", quality=quality, method=6)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    target_w = int(plan.get("target_width", 1122))
    target_h = int(plan.get("target_height", 1402))
    quality = int(plan.get("quality", 88))
    herbs = plan["herbs"]
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json,image/*;q=0.9,*/*;q=0.7"})
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    manifest_rows: list[dict] = []
    attribution: dict[str, list[dict]] = {}
    failures: list[str] = []

    for herb in herbs:
        hid, slug = herb["id"], herb["slug"]
        print(f"\n=== {hid} {herb['name']} ===", flush=True)
        candidates = collect_candidates(session, herb)
        print(f"material-first candidates: {len(candidates)}", flush=True)
        if not candidates:
            failures.append(f"{hid} {herb['name']}: no usable high-resolution source")
            continue

        anchors = candidates[: min(3, len(candidates))]
        attribution[hid] = []
        for i, role in enumerate(ROLES):
            c = anchors[i % len(anchors)]
            filename = f"{hid}-{slug}-{role}-v1.webp"
            dst = OUT_DIR / filename
            try:
                save_variant(session, c, dst, target_w, target_h, quality, i)
                if dst.stat().st_size < 20_000:
                    raise RuntimeError("normalized asset unexpectedly small")
            except Exception as exc:
                failures.append(f"{hid} {herb['name']} {role}: {exc}")
                if dst.exists():
                    dst.unlink()
                break
            print(f"  {role}: {c['title']} -> {filename}", flush=True)
            row = {
                "code": hid.upper().replace("BC", "BC."), "chinese_name": herb["name"],
                "latin_name": herb["latin"], "plant": herb["plant"], "part": herb["part"],
                "role": role, "filename": filename, "width_px": target_w, "height_px": target_h,
                "format": "WEBP", "status": "formal_hd_asset", "formal_hd_asset": "yes",
                "sha256": sha256_file(dst), "source_title": c["title"], "source_page": c["description_url"],
                "source_width": c["width"], "source_height": c["height"], "author": c["author"],
                "license": c["license"], "license_url": c["license_url"], "source_query": c["query"],
            }
            manifest_rows.append(row)
            attribution[hid].append({k: row[k] for k in ("role", "filename", "source_title", "source_page", "author", "license", "license_url")})
            time.sleep(0.2)

    if failures:
        print("\nIMPORT FAILED:", file=sys.stderr)
        for failure in failures:
            print(" - " + failure, file=sys.stderr)
        return 2

    csv_path = MANIFEST_DIR / "manifest-bc007-bc040-bc046.csv"
    json_path = MANIFEST_DIR / "manifest-bc007-bc040-bc046.json"
    attr_path = MANIFEST_DIR / "commons-attribution-bc007-bc040-bc046.json"
    fields = [
        "code", "chinese_name", "latin_name", "plant", "part", "role", "filename", "width_px", "height_px",
        "format", "status", "formal_hd_asset", "sha256", "source_title", "source_page", "source_width", "source_height",
        "author", "license", "license_url", "source_query",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(manifest_rows)
    json_path.write_text(json.dumps(manifest_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    attr_path.write_text(json.dumps(attribution, ensure_ascii=False, indent=2), encoding="utf-8")
    expected = len(herbs) * 7
    if len(manifest_rows) != expected:
        print(f"Expected {expected} rows, got {len(manifest_rows)}", file=sys.stderr)
        return 3
    print(f"\nImported {len(herbs)} herbs / {expected} normalized HD assets.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
