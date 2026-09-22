#!/usr/bin/env python3
"""Fail-closed release gate for the BENCAO visual QA register (schema v2).

Approval unit is the per-herb **master photograph**. The seven slots
(hero / specimen / detail-01..05) are 封面 / 远景 / 中景 / 局部放大 of that same
master, so they are *expected* to share it. `independence` therefore lives on the
master, not the slot: every master's sha256 must be unique across herbs — no two
herbs may lean on the same physical photograph.

Every master-related assertion below is conditional on masters existing, so the
current baseline (46 herbs, 0 masters, 0 approved) still passes. That is
deliberate: this gate defines what an approval *requires*, it does not require
approvals to be present.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "scripts"))
from stage_visual_candidates import valid_image  # noqa: E402  (single source of truth for image magic bytes)

data = json.loads((root / "data/visual-qa-register.json").read_text(encoding="utf-8"))
app = (root / "app46.js").read_text(encoding="utf-8")
index = (root / "index.html").read_text(encoding="utf-8")
roles = ["hero", "specimen", "detail-01", "detail-02", "detail-03", "detail-04", "detail-05"]

assert data["schema"] == "bencao-visual-qa-v2", data["schema"]
assert data["roles"] == roles
model = data["model"]
assert model["slots_per_herb"] == 7, model["slots_per_herb"]
assert model["slot_roles"] == roles, model["slot_roles"]
# Guard the definition itself: the whole point of v2 is that independence moved
# from the slot to the master. If someone quietly rewrites this back to
# per-slot independence, the gate must notice.
assert "sha256" in model["independence"], "Independence is no longer defined on the master"
assert "母图" in model["master_source_rule"], "Master source rule lost its wording"

herbs = data["herbs"]
assert len(herbs) == 46, "Expected exactly 46 herbs"
assert [h["id"] for h in herbs] == [f"bc{i:03d}" for i in range(1, 47)], "Herb IDs not continuous"
assert sum(len(h["slots"]) for h in herbs) == 322, "Expected 322 image slots"

groups = {}
for tier, symbol in [("A", "QA_REJECTED_IDS"), ("B", "QA_REVIEW_IDS"), ("C", "QA_REUSE_IDS")]:
    match = re.search(r"const " + symbol + r"=new Set\((\[[^\n]*\])\)", app)
    assert match, f"Public page does not define {symbol}"
    groups[tier] = set(json.loads(match.group(1)))
assert [len(groups[t]) for t in ("A", "B", "C")] == [32, 6, 8]
assert len(groups["A"] | groups["B"] | groups["C"]) == 46
assert not (groups["A"] & groups["B"] or groups["A"] & groups["C"] or groups["B"] & groups["C"])

master_ids: set[str] = set()
master_hashes: dict[str, str] = {}
verified_masters: dict[str, set[str]] = {}

for herb in herbs:
    herb_id, tier = herb["id"], herb["tier"]
    assert tier in groups and herb_id in groups[tier], f"Site/register disagreement: {herb_id}"
    expected_mode = "unverified_preview" if tier == "C" else "hold"
    assert herb["public_mode"] == expected_mode, herb_id
    assert [x["role"] for x in herb["slots"]] == roles, herb_id
    assert isinstance(herb["masters"], list), f"{herb_id}: masters must be a list"

    verified_masters[herb_id] = set()
    for master in herb["masters"]:
        mid = master["master_id"]
        assert mid not in master_ids, f"Duplicate master_id: {mid}"
        assert mid.startswith(herb_id + "-"), f"Master id not namespaced to its herb: {mid}"
        master_ids.add(mid)

        rel = master["file"]
        assert rel.startswith("images/_masters/"), f"Master outside images/_masters/: {rel}"
        path = (root / rel).resolve()
        assert path.is_relative_to(root / "images" / "_masters"), rel
        assert path.is_file(), f"Missing master file: {rel}"
        raw = path.read_bytes()
        assert valid_image(path.name, raw), f"Master is not a real image: {rel}"

        # The recorded hash must describe the file we can actually read, or the
        # cross-herb uniqueness check below would be checking a comment.
        digest = hashlib.sha256(raw).hexdigest()
        assert master["sha256"] == digest, f"Master sha256 mismatch: {rel}"
        assert digest not in master_hashes, (
            f"Master reused across herbs: {rel} also used by {master_hashes.get(digest)}"
        )
        master_hashes[digest] = herb_id

        assert master["width"] > 0 and master["height"] > 0, f"Unmeasured master: {rel}"
        assert master["source_kind"] in ("self_shot", "open_license"), master["source_kind"]
        assert master["photographer"], f"Master without a photographer: {rel}"
        if master["source_kind"] == "open_license":
            for key in ("license", "license_url", "source_page"):
                assert master[key], f"Open-licensed master missing {key}: {rel}"
        assert master["taxon_claimed"] and master["medicinal_part"], f"Master without identity: {rel}"

        assert isinstance(master["verified"], bool), f"{rel}: verified must be a bool"
        if master["verified"]:
            assert master["reviewer"], f"Master verified without a reviewer: {rel}"
            assert master["evidence"], f"Master verified without evidence: {rel}"
            verified_masters[herb_id].add(mid)

    for slot in herb["slots"]:
        approved = slot["approved"]
        role = slot["role"]
        assert isinstance(approved, bool), (herb_id, role)

        derived = slot["derived_from"]
        if derived is not None:
            assert derived in {m["master_id"] for m in herb["masters"]}, (
                f"Slot derives from a master of another herb: {herb_id}/{role} -> {derived}"
            )

        if approved:
            # An approved slot is a *derived view* of an approved master. The
            # master is the thing that was verified; without it the slot has no
            # provenance to point at.
            assert derived in verified_masters[herb_id], (
                f"Approved without a verified master: {herb_id}/{role}"
            )
            needed = ["source_verified", "medicinal_part_verified", "visual_verified"]
            assert all(slot.get(k) is True for k in needed), f"Unverified approval: {herb_id}/{role}"
            assert slot.get("reviewer") and slot.get("reference_file") and slot.get("candidate_file")
            assert slot.get("evidence"), f"Missing approval evidence: {herb_id}/{role}"
            candidate = (root / slot["candidate_file"]).resolve()
            assert candidate.is_relative_to(root / "images"), candidate
            assert candidate.is_file() and candidate.stat().st_size > 20000, candidate
            published = (root / slot["output_file"]).resolve()
            assert published.is_relative_to(root / "images"), published
            assert published.is_file() and published.stat().st_size > 20000, published
        else:
            assert slot["state"] in (
                "rejected_source_or_content", "review_pending", "independence_pending"
            ), (herb_id, role)

    # A herb whose master never passed cannot have passed slots — the reverse
    # direction of the rule above, stated separately so a future refactor cannot
    # accidentally drop it.
    if not verified_masters[herb_id]:
        assert not any(s["approved"] for s in herb["slots"]), (
            f"{herb_id}: slots approved with no verified master"
        )
    # Automatic promotion from 7 files, size, and source labels is forbidden.
    assert herb["public_mode"] != "approved" or all(s["approved"] for s in herb["slots"]), herb_id

assert "h.assetStatus='qc_hold';h.hero=null;h.images=[];" in app, "Quarantine logic missing"
assert "h.assetStatus='qa_preview';" in app, "Unverified preview label missing"
assert "46 味均已接入高清图集" not in index, "False complete-HD claim"
for legacy in ("import-b64-assets.yml", "import-visual-assets.yml", "import-commons-assets.yml"):
    text = (root / ".github/workflows" / legacy).read_text(encoding="utf-8")
    assert "if: ${{ false }}" in text, f"Unreviewed direct importer reenabled: {legacy}"
assert (root / "scripts/stage_visual_candidates.py").is_file(), "Candidate-only importer missing"
assert (root / "images/_candidates/README.md").is_file(), "Candidate evidence policy missing"
assert (root / "images/_masters/README.md").is_file(), "Master source policy missing"

masters_total = len(master_ids)
approved_total = sum(1 for h in herbs for s in h["slots"] if s["approved"])
print(
    f"QA gate passed: 46 herbs / 322 slots; {masters_total} master(s) registered; "
    f"{approved_total} slot(s) approved; A32+B6 held; C8 marked unverified"
)
