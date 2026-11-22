#!/usr/bin/env python3
"""Build a deterministic, fail-closed coauthor review ZIP (never a submission).

Caller must first render figure1..figure4 using
  scripts/build_invited_m1_m2_figures.py --output-dir <figures-dir>
This script performs no fitting, no biological endpoint opening, and no journal
upload. Its output is intentionally marked REVIEW ONLY / HOLD.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ("figure1_design", "figure2_level_a", "figure3_invalidity", "figure4_fdf")
FORMATS = ("pdf", "svg", "png")

SOURCES = (
    "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_V1.md",
    "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COMPLETE_SI_V1.md",
    "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SOURCE_COMPLETENESS_SI_V1.md",
    "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_FIGURE_CAPTIONS_V1.md",
    "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_FIGURE_QA_20261122.md",
    "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COAUTHOR_DECISION_MEMO_20261123.md",
    "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_CLAIM_LEDGER_V1.md",
    "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COVER_LETTER_V1.md",
    "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_TITLE_PAGE_V1.md",
    "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SUBMISSION_READINESS_V1.md",
    "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SUBMISSION_MANIFEST_V1.json",
    "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_HANDOFF_V1.md",
    "docs/M1_CLASS_DEPENDENT_FDF_AUDIT_20261122.md",
    "docs/EL_METHOD_JOURNAL_PREFLIGHT_20261123.md",
    "docs/GBIF_REPAIRED_LEVEL_A_TERMINAL_DECISION_20261122.md",
    "results/product_b_same_target_core19_v0_4_heldout_final_receipt.json",
    "results/reviewer2_level_a_structure_audit_v0_1.json",
    "results/gbif_repaired_heldout12_sensitivity_v1.json",
    "results/gbif_repaired_heldout12_postterminal_coverage_audit_v1.json",
    "results/gbif_repaired_heldout12_postterminal_cv_switch_v1.json",
    "results/gbif_repaired_heldout12_postterminal_score_drift_v1.json",
    "results/gbif_repaired_heldout12_sensitivity_cells_v1.csv",
    "results/gbif_repaired_reference47_q95_ceiling_v1.csv",
    "results/gbif_repaired_reference47_q95_summary_v1.json",
    "results/pre_field_state_dependent_invalidity_v0_2.json",
    "results/pre_field_identifiability_benchmark_summary_v0_1.json",
)

REVIEW_NOTICE = """284b — Ecology Letters invited Method candidate
COAUTHOR REVIEW ONLY — NOT A JOURNAL SUBMISSION

Status: HOLD_FOR_SENSITIVITY_REVIEW.
Historical prospectively heldout empirical endpoint: 12 taxa; 283 of 288
evaluable; 5 unresolved; 0/12 taxa above frozen source-discordance q95.
Restored GBIF (the SAME 12 taxa): 285 of 288 evaluable, 3 unresolved;
0/12 taxa above independently recalibrated restored q95. Only 282/283
historically evaluable cells remain evaluable, so full-retention robustness
is FALSE. This retrospective repair is NOT a second independent endpoint.

M1 invalid-key identities and qualified-call FDF are analytic, not observed
natural missingness or a validated species-interaction dependency.

No author consent, final DOI, conflict disclosures or final journal proof is
implied. This package is for scientific review and explicit decision only.
See the coauthor decision memo, complete SI, and source-linked claim ledger.
"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_scientific_gate(root: Path) -> dict:
    m = json.loads((root / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_SUBMISSION_MANIFEST_V1.json").read_text())
    o = json.loads((root / "results/product_b_same_target_core19_v0_4_heldout_final_receipt.json").read_text())
    r = json.loads((root / "results/gbif_repaired_heldout12_sensitivity_v1.json").read_text())
    s = (root / "manuscript/ECOLOGY_LETTERS_INVITED_M1_M2_COMPLETE_SI_V1.md").read_text()
    if m.get("status") != "HOLD_FOR_SENSITIVITY_REVIEW":
        raise RuntimeError("Not a HOLD branch. Refuse to produce review-only bundle.")
    sf = m["postfreeze_repaired_GBIF_source_sensitivity"]
    si = m["complete_supporting_information"]
    jp = m["journal_source_preflight_20261123"]
    if (sf["strict_full_historical_283_cell_retention_robust"] is not False or
        sf["additional_independent_biological_endpoints"] != 0 or
        si["strict_original_cell_coverage_robust"] is not False or
        si["independent_biological_endpoint_increment"] != 0 or
        si["sections"] != 11 or
        jp["source_abstract_words"] > jp["abstract_limit"] or
        jp["source_main_text_words_approx"] > jp["method_main_word_limit"] or
        jp["publisher_format_approved"] is not False or
        jp["doi_present"] is not False or
        jp["author_approval_received"] is not False or
        not si["coauthor_review_only"] or
        m["figure_package_20261122"]["authorship_approval"] is not False):
        raise RuntimeError("Scientific status is not the frozen coverage-limited HOLD.")
    if (o["heldout"]["taxa"] != 12 or o["heldout"]["paired_prediction_surfaces_opened_cells"] != 283 or
        r["paired_prediction_surfaces_opened_cells"] != 285 or
        r["historical_original_opened_cells_retained"] != 282 or
        r["source_completeness_0_of_12_robust"] is not False or
        r["empirical_ledger_increment"] != 0):
        raise RuntimeError("Signed historical or source-repair accounting changed.")
    if (o["final_endpoint_fingerprint"] != r["historical_endpoint_fingerprint"] or
        o["final_endpoint_fingerprint"] != m["scientific_core"]["historical_endpoint_fingerprint"] or
        r["final_endpoint_fingerprint"] != sf["repaired_sensitivity_endpoint_fingerprint"]):
        raise RuntimeError("Signed endpoint fingerprints do not reconcile.")
    if ("## S11." not in s or "HOLD_FOR_SENSITIVITY_REVIEW" not in s or
        "282/283" not in s or "FDF_qualified" not in s):
        raise RuntimeError("Complete SI lacks mandatory science or hold wording.")
    return {
        "submission_status": m["status"],
        "independent_biological_endpoints": 1,
        "repair_new_independent_endpoints": 0,
        "original_evaluable": 283,
        "repaired_evaluable": 285,
        "original_evaluable_retained": 282,
        "strict_original_coverage_robust": False,
        "historical_fingerprint": o["final_endpoint_fingerprint"],
        "restored_sensitivity_fingerprint": r["final_endpoint_fingerprint"],
    }


def collect_payloads(root: Path, figures_dir: Path) -> dict[str, bytes]:
    frozen_gate = verify_scientific_gate(root)
    files = {}
    for path in SOURCES:
        file = root / path
        if not file.is_file():
            raise FileNotFoundError(f"Required review source missing: {path}")
        files[path] = file.read_bytes()
    for stem in FIGURES:
        for fmt in FORMATS:
            asset = figures_dir / f"{stem}.{fmt}"
            if not asset.is_file() or asset.stat().st_size <= 100:
                raise RuntimeError(f"Missing or empty rendered figure {asset}")
            files[f"figures/{asset.name}"] = asset.read_bytes()
    readme = figures_dir / "FIGURE_README.md"
    if not readme.is_file():
        raise FileNotFoundError("Missing source-verified figure README")
    files["figures/FIGURE_README.md"] = readme.read_bytes()
    files["REVIEW_ONLY.txt"] = REVIEW_NOTICE.encode("utf-8")
    index = {
        "schema": "284b.invited_m1_m2_coauthor_review_bundle.v1",
        "purpose": "coauthor scientific review, not journal submission",
        **frozen_gate,
        "figure_files": 12,
        "complete_si_sections": 11,
        "sha256_by_file": {k: sha(data) for k, data in sorted(files.items())},
    }
    files["BUNDLE_MANIFEST.json"] = (json.dumps(index, indent=2, sort_keys=True) + "\n").encode()
    return files


def write_bundle(path: Path, payloads: dict[str, bytes]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(payloads.items()):
            safe = Path(name)
            if safe.is_absolute() or ".." in safe.parts:
                raise ValueError("Unsafe ZIP member")
            item = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.create_system = 3
            item.external_attr = 0o644 << 16
            z.writestr(item, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(path, "r") as z:
        if set(z.namelist()) != set(payloads) or z.testzip() is not None:
            raise RuntimeError("Review ZIP verification failed")
    return sha(path.read_bytes())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--figures-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    contents = collect_payloads(ROOT, args.figures_dir)
    digest = write_bundle(args.output, contents)
    print(json.dumps({"status": "HOLD_FOR_SENSITIVITY_REVIEW",
                      "purpose": "coauthor review only",
                      "file": str(args.output),
                      "members": len(contents),
                      "sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
