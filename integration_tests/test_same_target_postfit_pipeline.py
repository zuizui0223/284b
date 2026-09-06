"""Synthetic-only integration checks for the existing three post-fit CLI stages.

Real predictions, model files and occurrence data are never used. All writes go
into TemporaryDirectory. Frozen repository contracts are read, not modified.
Run with: PYTHONPATH=. python -m unittest discover -s integration_tests -v
"""
from __future__ import annotations

from contextlib import ExitStack, redirect_stdout
import io
import itertools
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from product_b_v5.prediction_opening import read_authorized_prediction_cells
from scripts import audit_same_target_successor_reference_feasibility as feasibility
from scripts import calibrate_same_target_successor_pairing_strict as calibration
from scripts import evaluate_same_target_heldout_crosscheck_strict as heldout

MODES = ("PRESERVED_SPECIMEN", "HUMAN_OBSERVATION")
MS = (150, 300, 500)
PROCEDURES = tuple(
    f"{strategy}|{model}"
    for strategy in ("all", "vif", "predictive_forward", "niche_forward")
    for model in ("logit_l2_C0.1_degree1", "logit_l2_C1_degree2")
)
LOW_N = (150, PROCEDURES[0])
EXACT_N = (150, PROCEDURES[1])
FIT_MISSING = (300, PROCEDURES[2])
INADEQUATE = (300, PROCEDURES[4])
DISCORDANT = (500, PROCEDURES[2])


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, allow_nan=False) + "\n", encoding="utf-8")


def make_artifact(root: Path, index: int, *, successor: bool) -> None:
    """Create small synthetic sealed tables; invalid rows are deliberate sentinels."""
    name = f"synthetic_{'calibration' if successor else 'heldout'}_{index:02d}"
    directory = root / name
    directory.mkdir(parents=True)
    contract = {
        "taxon": name, "taxon_index": index, "expected_fit_cells": 48,
        "result_version": (
            "product_b_same_target_successor_layer1_fit_taxon_v0.1" if successor
            else "product_b_same_target_source_layer1_baseline_fit_taxon_v0.1"
        ),
        "prediction_surfaces_sealed": True, "paired_discordance_computed": False,
        "process_knockout_computed": False, "reference_ceiling_read": False,
        "historical_key_subset_selection_used": False,
    }
    write_json(directory / "contract.json", contract)
    inventory, folds, predictions = [], [], []
    for m, procedure in itertools.product(MS, PROCEDURES):
        key = (m, procedure)
        missing_fit = successor and index == 46 and key == FIT_MISSING
        source_inadequate = (
            (successor and ((key == LOW_N and index >= 29) or (key == EXACT_N and index >= 30)))
            or (not successor and index == 1 and key == INADEQUATE)
        )
        opening_forbidden = key == LOW_N or source_inadequate or missing_fit
        for source in MODES:
            base = {"taxon": name, "source": source, "M_km": m, "procedure": procedure}
            unresolved = missing_fit and source == MODES[1]
            prefix = "successor_layer1_model_fit_" if successor else "layer1_model_fit_"
            inventory.append({**base, "state": prefix + ("unresolved" if unresolved else "sealed")})
            for fold in range(4):
                rank = 0.49 if source_inadequate and source == MODES[1] else 0.8
                folds.append({**base, "fold": fold, "presence_rank": rank})
            scores = [0.75, 0.25] if source == MODES[0] else [0.5, 0.5]
            if not successor and index == 0 and key == DISCORDANT and source == MODES[1]:
                scores = [0.0, 1.0]
            if opening_forbidden:
                scores = [-999.0, -999.0]
            for row_id, score in enumerate(scores):
                predictions.append({**base, "comparison_row_id": f"r{row_id}", "ecological_score": score})
    pd.DataFrame(inventory).to_csv(directory / "fit_inventory.csv", index=False)
    pd.DataFrame(folds).to_csv(directory / "outer_cv_fold_metrics.csv", index=False)
    pd.DataFrame(predictions).to_parquet(directory / "sealed_prediction_surfaces.parquet", index=False)


class SameTargetPostfitIntegrationTests(unittest.TestCase):
    def test_three_stage_pipeline_preserves_denominators_and_opening_rules(self):
        with tempfile.TemporaryDirectory(prefix="284b-synthetic-postfit-") as tmp:
            root = Path(tmp)
            sources, holdouts = root / "calibration", root / "heldout"
            for i in range(47):
                make_artifact(sources, i, successor=True)
            for i in range(12):
                make_artifact(holdouts, i, successor=False)
            sampling = root / "sampling.json"
            write_json(sampling, {"source_mode_sampling_passed": 47, "results": [
                {"requested_name": f"synthetic_calibration_{i:02d}", "state": "successor_source_mode_sampling_passed"}
                for i in range(47)
            ]})
            fit_audit = root / "fit_audit.json"
            write_json(fit_audit, {"prediction_surfaces_opened_for_pairing": False,
                                  "paired_discordance_opened": False, "process_knockout_opened": False})
            pre_d = root / "feasibility.json"
            reference = root / "reference.csv"
            calibration_summary = root / "calibration_summary.json"
            calibration_cells = root / "calibration_cells.csv"
            heldout_cells = root / "heldout_cells.csv"
            heldout_summary = root / "heldout_summary.json"
            with ExitStack() as stack:
                stack.enter_context(patch.object(feasibility, "SAMPLING", sampling))
                stack.enter_context(patch.object(calibration, "SAMPLING", sampling))
                stack.enter_context(patch.object(calibration, "FEASIBILITY", pre_d))
                stack.enter_context(patch.object(heldout, "REFERENCE_SUMMARY", calibration_summary))
                stack.enter_context(patch.object(heldout, "REFERENCE_TABLE", reference))
                stack.enter_context(redirect_stdout(io.StringIO()))
                with patch("pyarrow.dataset.dataset", side_effect=AssertionError("pre-D prediction read")):
                    with patch.object(sys, "argv", ["feasibility", "--input-root", str(sources),
                            "--fit-audit", str(fit_audit), "--output", str(pre_d)]):
                        self.assertEqual(feasibility.main(), 0)
                gate = json.loads(pre_d.read_text())
                self.assertEqual(gate["candidate_pair_cells"], 1128)
                self.assertEqual(gate["reference_cells_authorized_to_open_discordance"], 23)
                by_key = {(r["M_km"], r["procedure"]): r for r in gate["reference_cells"]}
                self.assertEqual(by_key[LOW_N]["eligible_distinct_taxa_pre_discordance"], 29)
                self.assertFalse(by_key[LOW_N]["discordance_opening_authorized"])
                self.assertEqual(by_key[EXACT_N]["eligible_distinct_taxa_pre_discordance"], 30)
                self.assertTrue(by_key[EXACT_N]["discordance_opening_authorized"])

                real_reader = read_authorized_prediction_cells
                reads = []
                def checked_reader(path, allowed):
                    path = Path(path)
                    self.assertTrue(path.is_relative_to(root))
                    allowed = set(allowed)
                    self.assertNotIn(LOW_N, allowed)
                    idx = int(path.parent.name.rsplit("_", 1)[1])
                    if path.is_relative_to(sources):
                        if idx >= 30:
                            self.assertNotIn(EXACT_N, allowed)
                        if idx == 46:
                            self.assertNotIn(FIT_MISSING, allowed)
                    elif idx == 1:
                        self.assertNotIn(INADEQUATE, allowed)
                    frame = real_reader(path, allowed)
                    self.assertFalse((frame["ecological_score"] < 0).any())
                    reads.append((path, allowed))
                    return frame
                with patch.object(calibration, "read_authorized_prediction_cells", side_effect=checked_reader):
                    with patch.object(sys, "argv", ["calibration", "--input-root", str(sources),
                            "--fit-audit", str(fit_audit), "--output-cells", str(calibration_cells),
                            "--output-reference", str(reference), "--output-summary", str(calibration_summary)]):
                        self.assertEqual(calibration.main(), 0)
                ref = pd.read_csv(reference)
                self.assertEqual(len(ref), 24)
                self.assertEqual(len(pd.read_csv(calibration_cells)), 1128)
                exact = ref[(ref.M_km == EXACT_N[0]) & (ref.procedure == EXACT_N[1])].iloc[0]
                self.assertEqual(exact.authorized_distinct_calibration_taxa, 30)
                self.assertEqual(exact.nearest_rank_index_1_based, 29)
                self.assertAlmostEqual(exact.one_minus_schoener_d_reference_ceiling, 0.25)
                cs = json.loads(calibration_summary.read_text())
                self.assertEqual(cs["reference_cells_frozen"], 23)
                self.assertEqual(cs["reference_cells_unresolved"], 1)
                self.assertEqual(cs["paired_surfaces_opened_authorized_cells"], 1063)
                self.assertFalse(cs["current_12_taxon_paired_discordance_read"])
                self.assertFalse(cs["process_knockout_opened"])
                frozen_reference_bytes = reference.read_bytes()
                with patch.object(heldout, "read_authorized_prediction_cells", side_effect=checked_reader):
                    with patch.object(sys, "argv", ["heldout", "--input-root", str(holdouts),
                            "--fit-audit", str(fit_audit), "--output-cells", str(heldout_cells),
                            "--output-summary", str(heldout_summary)]):
                        self.assertEqual(heldout.main(), 0)
                self.assertEqual(reference.read_bytes(), frozen_reference_bytes)
                hs = json.loads(heldout_summary.read_text())
                self.assertEqual(hs["heldout_cells_audited"], 288)
                self.assertEqual(hs["paired_crosscheck_consistent"], 274)
                self.assertEqual(hs["paired_crosscheck_attention_required"], 1)
                self.assertEqual(hs["paired_crosscheck_calibration_unresolved"], 12)
                self.assertEqual(hs["paired_crosscheck_unresolved"], 1)
                self.assertEqual(hs["paired_prediction_surfaces_opened_cells"], 275)
                hf = pd.read_csv(heldout_cells)
                self.assertEqual(len(hf), 288)
                self.assertTrue(hf.loc[hf.paired_state.str.contains("unresolved"), "schoener_d"].isna().all())
                self.assertFalse(hs["process_knockout_opened"])
                self.assertEqual(len(reads), 47 + 12)

    def test_empty_authorization_does_not_open_a_parquet_file(self):
        with patch("pyarrow.dataset.dataset", side_effect=AssertionError("unpermitted read")):
            result = read_authorized_prediction_cells("/nonexistent/synthetic.parquet", set())
        self.assertTrue(result.empty)

    def test_incomplete_panel_is_rejected_before_prediction_access(self):
        with tempfile.TemporaryDirectory(prefix="284b-synthetic-incomplete-") as tmp:
            root = Path(tmp)
            make_artifact(root, 0, successor=True)
            expected = {f"synthetic_calibration_{i:02d}" for i in range(47)}
            with patch("pyarrow.dataset.dataset", side_effect=AssertionError("unpermitted read")):
                with self.assertRaises(RuntimeError):
                    feasibility._load_artifacts(root, expected)
                with self.assertRaises(RuntimeError):
                    calibration._load_taxon_artifacts(root, expected)


if __name__ == "__main__":
    unittest.main()
