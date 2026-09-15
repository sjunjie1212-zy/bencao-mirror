#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "data" / "commons-asset-plan.json"
OUT_DIR = ROOT / "images"
MANIFEST_DIR = OUT_DIR / "_manifests"
API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "BENCAO-Mirror/4.0 (+https://github.com/sjunjie1212-zy/bencao-mirror)"
ROLES = ["hero", "specimen", "detail-01", "detail-02", "detail-03", "detail-04", "detail-05"]
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
BAD_WORDS = {
    "map", "distribution", "range", "logo", "icon", "stamp", "coin", "painting",
    "drawing", "illustration", "diagram", "herbarium", "specimen sheet", "pdf",
}
MATERIAL_WORDS = {
    "root", "rhizome", "fruit", "seed", "berry", "berries", "bark", "wood", "heartwood",
    "bud", "flower", "tuber", "bulb", "slice", "slices", "dried", "sclerotium", "stem",
    "cinnamon", "clove", "citron", "plum", "jujube", "hawthorn", "licorice", "ginseng",
}


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = html.unescape(value)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def meta_value(meta: dict, key: str) -> str:
    obj = meta.get(key) or {}
    return clean_text(obj.get("value") if isinstance(obj, dict) else str(obj))


def commons_search(session: requests.Session, query: str, limit: int = 40) -> list[dict]:
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1800",
    }
    r = session.get(API, params=params, timeout=(10, 25))
    r.raise_for_status()
    pages = (r.json().get("query") or {}).get("pages") or []
    pages.sort(key=lambda p: p.get("index", 999999))
    return pages


def source_page(title: str) -> str:
    return "https://commons.wikimedia.org/wiki/" + quote(title.replace(" ", "_"), safe=":()_',.-")


def candidate_from_page(page: dict, query_index: int, query: str) -> dict | None:
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
    lower = title.lower()
    score = 0.0
    score += min((width * height) / 2_000_000, 8.0)
    score += max(0, 5 - query_index) * 2.0
    qwords = [w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 2]
    score += sum(1.2 for w in qwords if w in lower)
    score += sum(1.0 for w in MATERIAL_WORDS if w in lower)
    score -= sum(5.0 for w in BAD_WORDS if w in lower)
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
        "description": meta_value(meta, "ImageDescription"),
        "query": query,
        "query_index": query_index,
        "score": score,
    }


def collect_candidates(session: requests.Session, herb: dict) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    queries = list(herb.get("queries") or [])
    queries.extend([herb.get("plant", ""), herb.get("name", ""), herb.get("latin", "")])
    queries = [q.strip() for q in queries if q and q.strip()]
    for qi, query in enumerate(queries):
        try:
            pages = commons_search(session, query)
        except Exception as exc:
            print(f"WARN search failed {herb['id']} {query!r}: {exc}", file=sys.stderr)
            continue
        for page in pages:
            c = candidate_from_page(page, qi, query)
            if not c or not c["url"] or c["title"] in seen:
                continue
            seen.add(c["title"])
            out.append(c)
        if len(out) >= 24:
            break
        time.sleep(0.05)
    out.sort(key=lambda x: (-x["score"], -(x["width"] * x["height"]), x["title"]))
    return out


def save_webp(session: requests.Session, c: dict, dst: Path, target_w: int, target_h: int, quality: int) -> tuple[int, int]:
    r = session.get(c["url"], timeout=(10, 45))
    r.raise_for_status()
    from io import BytesIO
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
        print(f"candidates: {len(candidates)}", flush=True)
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
            time.sleep(0.03)

        if len(chosen) != 7:
            failures.append(f"{hid} {herb['name']}: only {len(chosen)}/7 usable high-resolution images")
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
