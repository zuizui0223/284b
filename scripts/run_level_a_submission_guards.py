from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "LEVEL_A_SHORT_REPORT_V0_1.md"
CLAIMS = ROOT / "manuscript" / "LEVEL_A_CLAIM_LEDGER_V0_1.md"
RESULT = ROOT / "results" / "product_b_same_target_core19_v0_4_heldout_final_receipt.json"
AUDIT = ROOT / "results" / "reviewer2_level_a_structure_audit_v0_1.json"

required = [MANUSCRIPT, CLAIMS, RESULT, AUDIT]
missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    raise SystemExit(f"missing active Level-A files: {missing}")

text = MANUSCRIPT.read_text(encoding="utf-8")

anchors = [
    "12 prospectively held-out",
    "283",
    "five remained unresolved",
    "not treated as independent replicates",
    "does not imply universal source invariance",
]
for anchor in anchors:
    if anchor not in text:
        raise SystemExit(f"missing Level-A manuscript anchor: {anchor}")

for forbidden in ["Cremastra", "Belonocnema", "SMIL001", "hard dependency"]:
    if forbidden in text:
        raise SystemExit(f"legacy/non-Level-A content leaked into active manuscript: {forbidden}")

print("Level-A submission guards passed")
