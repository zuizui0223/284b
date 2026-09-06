import csv
import hashlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from scripts.audit_same_target_progress_receipt import (
    MEMBERS, MODES, M_VALUES, PROCEDURES, reproduce, summarize_archive,
)

QA = {"outer_folds": 4, "chance_auc": 0.5, "minimum_auc_margin": 0.01, "auc_sem_multiplier": 1.0}


def csv_text(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


class ProgressReceiptTests(unittest.TestCase):
    def fixture(self, root, edit=None):
        contract = {
            "result_version": "product_b_same_target_successor_layer1_fit_taxon_v0.1",
            "taxon": "Fixture taxon", "taxon_index": 0, "expected_fit_cells": 48,
            "sealed_fit_cells": 48, "unresolved_fit_cells": 0,
            "paired_discordance_computed": False, "process_knockout_computed": False,
            "reference_ceiling_read": False, "prediction_surfaces_sealed": True,
        }
        inv, folds = [], []
        for source in MODES:
            for m in M_VALUES:
                for procedure in PROCEDURES:
                    base = {"taxon": "Fixture taxon", "source": source, "M_km": m, "procedure": procedure}
                    inv.append({**base, "state": "successor_layer1_model_fit_sealed"})
                    folds.extend({**base, "fold": f, "presence_rank": 0.8} for f in range(4))
        if edit:
            edit(inv, folds)
        path = Path(root) / "fixture.zip"
        with ZipFile(path, "w") as z:
            z.writestr("contract.json", json.dumps(contract))
            z.writestr("fit_inventory.csv", csv_text(inv))
            z.writestr("outer_cv_fold_metrics.csv", csv_text(folds))
            z.writestr("sealed_prediction_surfaces.parquet", b"Do not decode this member")
        receipt = {"taxon": "Fixture taxon", "taxon_index": 0, "artifact_id": 1,
                   "archive_filename": "fixture.zip", "archive_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        return path, receipt

    def test_all_adequate_without_reading_prediction_member(self):
        with TemporaryDirectory() as root:
            path, r = self.fixture(root)
            read = ZipFile.read
            observed = []
            def guarded(archive, name, *args, **kwargs):
                self.assertIn(name, MEMBERS)
                observed.append(name)
                return read(archive, name, *args, **kwargs)
            with patch.object(ZipFile, "read", guarded):
                result = summarize_archive(path, r, QA)
            self.assertEqual(observed, list(MEMBERS))
            self.assertEqual(result["source_cell_states"]["answer_adequate"], 48)
            self.assertEqual(result["pre_discordance_eligible_pairs"], 24)

    def test_validation_missingness_is_not_low_performance(self):
        def edit(inv, folds):
            folds.pop(0)  # one cell has three folds
            folds[3]["presence_rank"] = ""  # the next cell has one nonfinite metric
        with TemporaryDirectory() as root:
            path, r = self.fixture(root, edit)
            result = summarize_archive(path, r, QA)
            self.assertEqual(result["source_cell_states"]["outer_fold_rows_incomplete"], 1)
            self.assertEqual(result["source_cell_states"]["validation_metric_nonfinite"], 1)
            self.assertEqual(result["source_cell_states"]["prediction_performance_below_floor"], 0)
            self.assertEqual(result["pre_discordance_eligible_pairs"], 22)

    def test_duplicate_inventory_cannot_pass_by_row_count(self):
        with TemporaryDirectory() as root:
            path, r = self.fixture(root, lambda inv, folds: inv.__setitem__(1, dict(inv[0])))
            with self.assertRaisesRegex(ValueError, "48 cells"):
                summarize_archive(path, r, QA)

    def test_archive_digest_must_match(self):
        with TemporaryDirectory() as root:
            path, r = self.fixture(root)
            r["archive_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "SHA256"):
                summarize_archive(path, r, QA)

    def test_partial_receipt_is_never_reference_authorization(self):
        with TemporaryDirectory() as root:
            path, r = self.fixture(root)
            result = reproduce({"artifacts": [r], "expected_successor_taxa": 47,
                                "frozen_prediction_adequacy": QA}, Path(root))
            self.assertEqual(result["taxa_not_audited_in_this_receipt"], 46)
            self.assertFalse(result["reference_calibration_authorized_by_this_receipt"])
            self.assertFalse(result["paired_discordance_computed"])


if __name__ == "__main__":
    unittest.main()
