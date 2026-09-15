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
MATERIAL_WORDS = {
    "root", "rhizome", "fruit", "seed", "seeds", "berry", "berries", "bark", "wood", "heartwood",
    "bud", "flower", "tuber", "bulb", "slice", "slices", "dried", "sclerotium", "stem", "vine",
    "cinnamon", "clove", "citron", "plum", "jujube", "hawthorn", "licorice", "ginseng",
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

FALLBACKS = {
    "bc012": {
        "queries": ["Poria cocos medicine", "Wolfiporia extensa", "Poria sclerotium", "茯苓 中药", "Fu ling herb"],
        "accept": ["poria", "wolfiporia", "茯苓", "fu ling"],
    },
    "bc025": {
        "queries": ["Amomum villosum dried fruit", "Amomi Fructus", "砂仁 中药", "sha ren herb", "Amomum fruit spice"],
        "accept": ["amomum", "wurfbainia", "砂仁", "sha ren", "amomi"],
    },
    "bc027": {
        "queries": ["Coptis rhizome dried", "Coptidis Rhizoma", "黄连 中药", "huang lian herb", "Coptis root"],
        "accept": ["coptis", "coptidis", "黄连", "huang lian"],
    },
    "bc035": {
        "queries": ["Spatholobus suberectus stem", "Spatholobi Caulis", "鸡血藤 中药", "ji xue teng herb", "Spatholobus vine slices"],
        "accept": ["spatholobus", "spatholobi", "鸡血藤", "ji xue teng"],
    },
    "bc038": {
        "queries": ["Citrus aurantium immature dried fruit", "Aurantii Fructus Immaturus", "枳实 中药", "zhi shi herb", "bitter orange dried fruit"],
        "accept": ["citrus aurantium", "aurantii", "枳实", "zhi shi", "bitter orange"],
    },
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
                print(f"RATE LIMIT 429; sleeping {delay:.1f}s", file=sys.stderr, flush=True)
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
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo|categories",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1800",
        "cllimit": "max",
    }
    r = request_with_retry(session, API, params=params, timeout=(10, 35))
    pages = (r.json().get("query") or {}).get("pages") or []
    pages.sort(key=lambda p: p.get("index", 999999))
    return pages


def source_page(title: str) -> str:
    return "https://commons.wikimedia.org/wiki/" + quote(title.replace(" ", "_"), safe=":()_',.-")


def part_profile(herb: dict) -> tuple[set[str], set[str]]:
    part = herb.get("part", "")
    if "菌核" in part:
        return {"sclerotium", "poria", "dried", "slice", "slices"}, {"flower", "leaf", "leaves", "fruit"}
    if "心材" in part:
        return {"wood", "heartwood", "stem", "slice", "slices", "dried"}, {"flower", "leaf", "leaves", "fruit", "seed"}
    if "树皮" in part or "干皮" in part or "根皮" in part or "枝皮" in part:
        return {"bark", "cortex", "dried", "slice", "slices"}, {"flower", "leaf", "leaves", "fruit", "seed"}
    if "藤茎" in part:
        return {"stem", "vine", "caulis", "slice", "slices", "dried"}, {"flower", "leaf", "leaves", "fruit"}
    if "花蕾" in part or "初开的花" in part:
        return {"flower", "flowers", "bud", "buds", "dried"}, {"root", "rhizome", "bark", "fruit", "seed"}
    if "种子" in part or "种仁" in part:
        return {"seed", "seeds", "kernel", "kernels", "dried"}, {"flower", "leaf", "leaves", "root", "bark"}
    if "幼果" in part:
        return {"fruit", "immature", "unripe", "dried", "slice", "slices"}, {"flower", "leaf", "leaves", "root"}
    if "果实" in part or "果穗" in part:
        return {"fruit", "fruits", "berry", "berries", "dried", "slice", "slices"}, {"flower", "leaf", "leaves", "root", "bark"}
    if "鳞叶" in part:
        return {"bulb", "bulbs", "lily", "dried", "slice", "slices"}, {"flower", "fruit", "seed"}
    if "块根" in part or "块茎" in part:
        return {"tuber", "root", "rhizome", "dried", "slice", "slices"}, {"flower", "leaf", "leaves", "fruit", "seed"}
    if "根" in part or "根茎" in part:
        return {"root", "rhizome", "dried", "slice", "slices"}, {"flower", "leaf", "leaves", "fruit", "seed"}
    return set(), set()


def candidate_from_page(page: dict, query_index: int, query: str, taxa: list[str], herb: dict, *, loose_accept: list[str] | None = None) -> dict | None:
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
    strict_match = not taxa or any(t in combined or " ".join(t.split()[:2]) in combined for t in taxa)
    loose_match = False
    if loose_accept:
        loose_match = any(term.lower() in raw_combined for term in loose_accept)
    if not strict_match and not loose_match:
        return None
    if any(norm(word) in combined for word in BAD_WORDS):
        return None
    prefer, avoid = part_profile(herb)
    score = 0.0
    score += min((width * height) / 2_000_000, 8.0)
    score += max(0, 6 - query_index) * 3.0
    qwords = [w for w in norm(query).split() if len(w) > 2]
    score += sum(1.4 for w in qwords if w in combined)
    score += sum(0.6 for w in MATERIAL_WORDS if w in combined)
    score += sum(5.0 for w in prefer if w in combined)
    score -= sum(4.0 for w in avoid if w in combined)
    if strict_match:
        score += 5.0
    if loose_match:
        score += 2.0
    if any(w in combined for w in ("dried", "slice", "slices")):
        score += 5.0
    return {
        "title": title,
        "url": info.get("thumburl") or info.get("url") or "",
        "original_url": info.get("url") or "",
        "description_url": info.get("descriptionurl") or source_page(title),
        "width": width,
        "height": height,
        "mime": mime,
        "author": meta_value(meta, "Artist"),
        "license": meta_value(meta, "LicenseShortName") or meta_value(meta, "UsageTerms"),
        "license_url": meta_value(meta, "LicenseUrl"),
        "credit": meta_value(meta, "Credit"),
        "description": description,
        "categories": categories,
        "query": query,
        "query_index": query_index,
        "score": score,
    }


def collect_candidates(session: requests.Session, herb: dict) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    taxa = taxa_for(herb)
    queries = [q.strip() for q in (herb.get("queries") or []) if q and q.strip()]

    def ingest(query: str, qi: int, expr: str, loose_accept: list[str] | None = None) -> None:
        try:
            pages = commons_search(session, expr)
        except Exception as exc:
            print(f"WARN search failed {herb['id']} {expr!r}: {exc}", file=sys.stderr)
            return
        for page in pages:
            c = candidate_from_page(page, qi, query, taxa, herb, loose_accept=loose_accept)
            if not c or not c["url"] or c["title"] in seen:
                continue
            seen.add(c["title"])
            out.append(c)

    for qi, query in enumerate(queries):
        ingest(query, qi, search_expression(query, taxa))
        if len(out) >= 28:
            break
        time.sleep(0.2)

    fallback = FALLBACKS.get(herb["id"])
    if len(out) < 12 and fallback:
        base = len(queries)
        for offset, query in enumerate(fallback["queries"]):
            ingest(query, base + offset, query, loose_accept=fallback["accept"])
            if len(out) >= 20:
                break
            time.sleep(0.2)

    out.sort(key=lambda x: (-x["score"], -(x["width"] * x["height"]), x["title"]))
    return out


def save_webp(session: requests.Session, c: dict, dst: Path, target_w: int, target_h: int, quality: int) -> tuple[int, int]:
    r = request_with_retry(session, c["url"], timeout=(10, 50))
    with Image.open(BytesIO(r.content)) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGB")
        elif im.mode == "RGBA":
            bg = Image.new("RGB", im.size, (244, 240, 231))
            bg.paste(im, mask=im.getchannel("A"))
            im = bg
        fitted = ImageOps.fit(im.convert("RGB"), (target_w, target_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        dst.parent.mkdir(parents=True, exist_ok=True)
        fitted.save(dst, "WEBP", quality=quality, method=6)
    return target_w, target_h


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
        hid = herb["id"]
        slug = herb["slug"]
        print(f"\n=== {hid} {herb['name']} ===", flush=True)
        candidates = collect_candidates(session, herb)
        print(f"matched candidates after strict/fallback filtering: {len(candidates)}", flush=True)
        chosen: list[tuple[dict, Path, str]] = []
        for c in candidates:
            if len(chosen) >= 7:
                break
            role = ROLES[len(chosen)]
            filename = f"{hid}-{slug}-{role}-v1.webp"
            dst = OUT_DIR / filename
            try:
                save_webp(session, c, dst, target_w, target_h, quality)
                if dst.stat().st_size < 20_000:
                    raise RuntimeError("normalized asset unexpectedly small")
            except Exception as exc:
                print(f"WARN download/process failed {c['title']}: {exc}", file=sys.stderr)
                if dst.exists():
                    dst.unlink()
                continue
            chosen.append((c, dst, role))
            print(f"  {role}: {c['title']} -> {filename}", flush=True)
            time.sleep(0.35)
        if len(chosen) != 7:
            failures.append(f"{hid} {herb['name']}: only {len(chosen)}/7 matched high-resolution images")
            continue
        attribution[hid] = []
        for c, dst, role in chosen:
            row = {
                "code": hid.upper().replace("BC", "BC."),
                "chinese_name": herb["name"],
                "latin_name": herb["latin"],
                "plant": herb["plant"],
                "part": herb["part"],
                "role": role,
                "filename": dst.name,
                "width_px": target_w,
                "height_px": target_h,
                "format": "WEBP",
                "status": "formal_hd_asset",
                "formal_hd_asset": "yes",
                "sha256": sha256_file(dst),
                "source_title": c["title"],
                "source_page": c["description_url"],
                "source_width": c["width"],
                "source_height": c["height"],
                "author": c["author"],
                "license": c["license"],
                "license_url": c["license_url"],
                "source_query": c["query"],
            }
            manifest_rows.append(row)
            attribution[hid].append({k: row[k] for k in ("role", "filename", "source_title", "source_page", "author", "license", "license_url")})

    if failures:
        print("\nIMPORT FAILED:", file=sys.stderr)
        for failure in failures:
            print(" - " + failure, file=sys.stderr)
        return 2

    csv_path = MANIFEST_DIR / "manifest-bc007-bc040-bc046.csv"
    json_path = MANIFEST_DIR / "manifest-bc007-bc040-bc046.json"
    attr_path = MANIFEST_DIR / "commons-attribution-bc007-bc040-bc046.json"
    fields = [
        "code", "chinese_name", "latin_name", "plant", "part", "role", "filename",
        "width_px", "height_px", "format", "status", "formal_hd_asset", "sha256",
        "source_title", "source_page", "source_width", "source_height", "author", "license",
        "license_url", "source_query",
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
