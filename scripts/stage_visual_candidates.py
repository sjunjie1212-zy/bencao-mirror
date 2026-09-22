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
MASTERS = ROOT / "images" / "_masters"
ROLES = ("hero", "specimen", "detail-01", "detail-02", "detail-03", "detail-04", "detail-05")
EXTS = (".avif", ".webp", ".png", ".jpg", ".jpeg")

SLOT_RE = re.compile(r"(hero|specimen|detail-0[1-5])-v[1-9]\d*\.(webp|avif|png|jpe?g)")
MASTER_RE = re.compile(r"master-v[1-9]\d*\.(webp|avif|png|jpe?g)")


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


def _require_str(item, keys, label):
    if any(not isinstance(item.get(k), str) or not item[k].strip() for k in keys):
        raise ValueError(f"Missing evidence for {label}")


def check_master(meta, master_name):
    """母图是整味的来源，不是七个图位之一，所以它自带一套来源字段。"""
    block = meta.get("master")
    if not isinstance(block, dict) or block.get("file") != master_name:
        raise ValueError("Master file without a matching evidence.master record")
    kind = block.get("source_kind")
    if kind not in ("self_shot", "open_license"):
        raise ValueError(f"Bad master source_kind: {kind}")
    if kind == "self_shot":
        _require_str(block, ("photographer",), master_name)
    else:
        _require_str(block, ("photographer", "license", "license_url", "source_page"), master_name)
    _require_str(block, ("taxon_claimed", "medicinal_part", "observed_feature"), master_name)
    # 母图必须自有或开放许可：仅授权内部比对的第三方图不得进公开仓库。
    if block.get("third_party_review_only") is True:
        raise ValueError("Master is review-only material and cannot be staged into a public repo")
    if block.get("verified") is True:
        raise ValueError("Upload cannot grant its own verification")
    if block.get("approved") is True:
        raise ValueError("Upload cannot grant its own approval")


def inspect_archive(archive):
    match = re.fullmatch(r"(bc\d{3})-[a-z0-9-]+\.zip", archive.name)
    if not match or not 1 <= int(match.group(1)[2:]) <= 46:
        raise ValueError(f"Unexpected archive name: {archive.name}")
    herb_id = match.group(1)
    if archive.stat().st_size > 25000000:
        raise ValueError(f"Archive too large: {archive.name}")
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        if not 2 <= len(infos) <= 9 or any(x.is_dir() for x in infos):
            raise ValueError("Expected evidence.json, one to seven flat images, and at most one master")
        names = [x.filename for x in infos]
        if len(names) != len(set(names)) or "evidence.json" not in names:
            raise ValueError("Missing evidence.json or duplicate filenames")
        entries = [x for x in infos if x.filename != "evidence.json"]
        masters = [x for x in entries if MASTER_RE.fullmatch(x.filename)]
        images = [x for x in entries if not MASTER_RE.fullmatch(x.filename)]
        if len(masters) > 1:
            raise ValueError("At most one master per archive")
        if not 1 <= len(images) <= 7:
            raise ValueError("Expected one to seven images")
        if sum(x.file_size for x in infos) > 78000000:
            raise ValueError("Uncompressed archive too large")
        for image in images:
            if not SLOT_RE.fullmatch(image.filename):
                raise ValueError(f"Invalid image filename: {image.filename}")
            if image.file_size > 12000000:
                raise ValueError("Oversize image")
        for master in masters:
            if master.file_size > 12000000:
                raise ValueError("Oversize master")
        meta = json.loads(z.read("evidence.json"))
        if meta.get("herb_id") != herb_id or not isinstance(meta.get("assets"), list):
            raise ValueError("Evidence herb ID/assets mismatch")
        evidence = {x.get("file"): x for x in meta["assets"]}
        if set(evidence) != {x.filename for x in images}:
            raise ValueError("Every image must have its own evidence record")
        for fn, item in evidence.items():
            _require_str(
                item,
                ("reference_url", "reference_taxon", "reference_part", "source_author", "source_license", "observed_feature"),
                fn,
            )
            if item.get("approved") is True:
                raise ValueError("Upload cannot grant its own approval")
        if masters and meta.get("master") is None:
            raise ValueError("Master file present but evidence.json has no master record")
        if not masters and meta.get("master") is not None:
            raise ValueError("evidence.json declares a master but no master file was uploaded")
        if masters:
            check_master(meta, masters[0].filename)

        staged = STAGING / herb_id
        payload = {x.filename: z.read(x) for x in images}
        master_payload = {x.filename: z.read(x) for x in masters}
        for fn, raw in {**payload, **master_payload}.items():
            if not valid_image(fn, raw):
                raise ValueError(f"Invalid image bytes: {fn}")
        meta_name = f"evidence-{archive.stem}.json"
        if (staged / meta_name).exists() or any((staged / fn).exists() for fn in payload):
            raise ValueError("Candidate already exists; use a new version suffix")
        if any((MASTERS / fn).exists() for fn in master_payload):
            raise ValueError("Master already exists; use a new version suffix")
        return staged, payload, meta_name, meta, master_payload


def main():
    archives = sorted(INBOX.glob("bc*.zip")) if INBOX.exists() else []
    if not archives:
        print("No new candidate archives; nothing to stage.")
        return
    plans = [inspect_archive(p) for p in archives]
    paths = []
    for archive, (dest, payload, meta_name, evidence, master_payload) in zip(archives, plans):
        dest.mkdir(parents=True, exist_ok=True)
        if master_payload:
            MASTERS.mkdir(parents=True, exist_ok=True)
            for fn, raw in master_payload.items():
                out = MASTERS / fn
                out.write_bytes(raw)
                paths.append(out.relative_to(ROOT).as_posix())
        for fn, raw in payload.items():
            out = dest / fn
            out.write_bytes(raw)
            paths.append(out.relative_to(ROOT).as_posix())
        (dest / meta_name).write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths.append((dest / meta_name).relative_to(ROOT).as_posix())
        archive.unlink()
        paths.append(archive.relative_to(ROOT).as_posix())
    print("STAGED_ONLY: " + ", ".join(paths))
    print(
        "No formal image, app mapping, QA approval, or website publication was changed. "
        "Masters stage unverified; register entries stay the reviewer's call."
    )


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        sys.exit(str(exc))
