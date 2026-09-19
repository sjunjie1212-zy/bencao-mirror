#!/usr/bin/env python3
"""Stage uploaded herb pictures as *unapproved* candidates. Never touch images/*.webp."""
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "asset-import" / "candidates"
STAGING = ROOT / "images" / "_candidates"
ROLES = ("hero", "specimen", "detail-01", "detail-02", "detail-03", "detail-04", "detail-05")
EXTS = (".avif", ".webp", ".png", ".jpg", ".jpeg")


def valid_image(filename, content):
    if not 20000 <= len(content) <= 12000000:
        raise ValueError(f"Bad image size: {filename}")
    ext = Path(filename).suffix.lower()
    if ext == ".webp":
        return content[:4] == b"RIFF" and content[8:12] == b"WEBP"
    if ext == ".avif":
        return b"ftypavif" in content[4:24] or b"ftypavis" in content[4:24]
    if ext == ".png":
        return content.startswith(b"\x89PNG\r\n\x1a\n")
    if ext in (".jpg", ".jpeg"):
        return content.startswith(b"\xff\xd8\xff")
    return False


def inspect_archive(archive):
    match = re.fullmatch(r"(bc\d{3})-[a-z0-9-]+\.zip", archive.name)
    if not match or not 1 <= int(match.group(1)[2:]) <= 46:
        raise ValueError(f"Unexpected archive name: {archive.name}")
    herb_id = match.group(1)
    if archive.stat().st_size > 25000000:
        raise ValueError(f"Archive too large: {archive.name}")
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        if not 2 <= len(infos) <= 8 or any(x.is_dir() for x in infos):
            raise ValueError("Expected evidence.json and one to seven flat images")
        names = [x.filename for x in infos]
        if len(names) != len(set(names)) or "evidence.json" not in names:
            raise ValueError("Missing evidence.json or duplicate filenames")
        images = [x for x in infos if x.filename != "evidence.json"]
        if not 1 <= len(images) <= 7:
            raise ValueError("Expected one to seven images")
        if sum(x.file_size for x in infos) > 78000000:
            raise ValueError("Uncompressed archive too large")
        for image in images:
            if not re.fullmatch(r"(hero|specimen|detail-0[1-5])-v[1-9]\d*\.(webp|avif|png|jpe?g)", image.filename):
                raise ValueError(f"Invalid image filename: {image.filename}")
            if image.file_size > 12000000:
                raise ValueError("Oversize image")
        meta = json.loads(z.read("evidence.json"))
        if meta.get("herb_id") != herb_id or not isinstance(meta.get("assets"), list):
            raise ValueError("Evidence herb ID/assets mismatch")
        evidence = {x.get("file"): x for x in meta["assets"]}
        if set(evidence) != {x.filename for x in images}:
            raise ValueError("Every image must have its own evidence record")
        for fn, item in evidence.items():
            needed = ("reference_url", "reference_taxon", "reference_part", "source_author", "source_license", "observed_feature")
            if any(not isinstance(item.get(k), str) or not item[k].strip() for k in needed):
                raise ValueError(f"Missing evidence for {fn}")
            if item.get("approved") is True:
                raise ValueError("Upload cannot grant its own approval")
        staged = STAGING / herb_id
        payload = {x.filename: z.read(x) for x in images}
        for fn, raw in payload.items():
            if not valid_image(fn, raw):
                raise ValueError(f"Invalid image bytes: {fn}")
        meta_name = f"evidence-{archive.stem}.json"
        if (staged / meta_name).exists() or any((staged / fn).exists() for fn in payload):
            raise ValueError("Candidate already exists; use a new version suffix")
        return staged, payload, meta_name, meta


def main():
    archives = sorted(INBOX.glob("bc*.zip")) if INBOX.exists() else []
    if not archives:
        print("No new candidate archives; nothing to stage.")
        return
    plans = [inspect_archive(p) for p in archives]
    paths = []
    for archive, (dest, payload, meta_name, evidence) in zip(archives, plans):
        dest.mkdir(parents=True, exist_ok=True)
        for fn, raw in payload.items():
            out = dest / fn
            out.write_bytes(raw)
            paths.append(out.relative_to(ROOT).as_posix())
        (dest / meta_name).write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths.append((dest / meta_name).relative_to(ROOT).as_posix())
        archive.unlink()
        paths.append(archive.relative_to(ROOT).as_posix())
    print("STAGED_ONLY: " + ", ".join(paths))
    print("No formal image, app mapping, QA approval, or website publication was changed.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        sys.exit(str(exc))
