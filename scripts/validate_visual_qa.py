#!/usr/bin/env python3
"""Fail-closed release gate for the BENCAO visual QA register."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
data = json.loads((root / "data/visual-qa-register.json").read_text(encoding="utf-8"))
app = (root / "app46.js").read_text(encoding="utf-8")
index = (root / "index.html").read_text(encoding="utf-8")
roles = ["hero", "specimen", "detail-01", "detail-02", "detail-03", "detail-04", "detail-05"]
assert data["schema"] == "bencao-visual-qa-v1"
assert data["roles"] == roles
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

for herb in herbs:
    herb_id, tier = herb["id"], herb["tier"]
    assert tier in groups and herb_id in groups[tier], f"Site/register disagreement: {herb_id}"
    expected_mode = "unverified_preview" if tier == "C" else "hold"
    assert herb["public_mode"] == expected_mode, herb_id
    assert [x["role"] for x in herb["slots"]] == roles, herb_id
    for slot in herb["slots"]:
        approved = slot["approved"]
        assert isinstance(approved, bool), (herb_id, slot["role"])
        if approved:
            needed = ["source_verified", "medicinal_part_verified", "visual_verified", "independence_verified"]
            assert all(slot.get(k) is True for k in needed), f"Unverified approval: {herb_id}/{slot['role']}"
            assert slot.get("reviewer") and slot.get("reference_file") and slot.get("candidate_file")
            assert slot.get("evidence"), f"Missing approval evidence: {herb_id}/{slot['role']}"
            p = (root / slot["candidate_file"]).resolve()
            assert p.is_relative_to(root / "images"), p
            assert p.is_file() and p.stat().st_size > 20000, p
        else:
            assert slot["state"] in (
                "rejected_source_or_content", "review_pending", "independence_pending"
            ), (herb_id, slot["role"])
    # Automatic promotion from 7 files, size, and source labels is forbidden.
    assert herb["public_mode"] != "approved" or all(s["approved"] for s in herb["slots"]), herb_id

assert "h.assetStatus='qc_hold';h.hero=null;h.images=[];" in app, "Quarantine logic missing"
assert "h.assetStatus='qa_preview';" in app, "Unverified preview label missing"
assert "46 味均已接入高清图集" not in index, "False complete-HD claim"
print("QA gate passed: 46 herbs / 322 slots; A32+B6 held; C8 marked unverified")
