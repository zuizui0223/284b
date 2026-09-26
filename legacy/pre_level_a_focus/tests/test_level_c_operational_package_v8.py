import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "level_c_v8_eval", ROOT / "scripts" / "evaluate_level_c_field_calibration_v8.py"
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
CONTRACT = ROOT / "config" / "product_b_level_c_operational_package_v8.json"

FIELDS = [
    "candidate_id","calibration_unit_id","date_time","site_or_tree_id","gold_state","observer_state",
    "missing","device_failure","observer_failure","occlusion","unresolved_adjudication","notes"
]


def write_rows(rows):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8")
    with f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    return Path(f.name)


def row(cid, gold, observed, **flags):
    r = {k: "false" for k in FIELDS}
    r.update({
        "candidate_id": cid,
        "calibration_unit_id": "u",
        "date_time": "2026-01-01T00:00:00",
        "site_or_tree_id": "s",
        "gold_state": gold,
        "observer_state": observed,
        "notes": "",
    })
    for k, v in flags.items(): r[k] = "true" if v else "false"
    return r


class LevelCOperationalPackageV8Tests(unittest.TestCase):
    def test_contract_preserves_v7_thresholds_and_ledger(self):
        c = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(c["scientific_thresholds_unchanged"]["sensitivity_min"], 0.80)
        self.assertEqual(c["scientific_thresholds_unchanged"]["hard_fnr_max"], 0.20)
        self.assertEqual(c["scientific_thresholds_unchanged"]["specificity_min"], 0.95)
        self.assertEqual(c["minimum_clean_design"]["gold_positive_required"], 30)
        self.assertEqual(c["minimum_clean_design"]["gold_negative_required"], 60)
        self.assertFalse(c["focal_cross_role_values_opening_before_gate"])
        self.assertEqual(c["empirical_ledger_increment"], 0)
        self.assertEqual(c["global_284b_empirical_ledger_at_v8_freeze"], 1)

    def test_clean_30_60_pass_authorizes_opening(self):
        rows = [row("CREMV3-007", "positive", "positive") for _ in range(30)]
        rows += [row("CREMV3-007", "negative", "negative") for _ in range(60)]
        p = write_rows(rows)
        res = MOD.evaluate(p, "CREMV3-007")
        self.assertTrue(res["opening_authorized"])
        self.assertEqual(res["state"], "calibration_pass")
        self.assertEqual(res["empirical_ledger_increment"], 0)

    def test_under_minimum_counts_do_not_open(self):
        rows = [row("BELV3-012", "positive", "positive") for _ in range(29)]
        rows += [row("BELV3-012", "negative", "negative") for _ in range(59)]
        p = write_rows(rows)
        res = MOD.evaluate(p, "BELV3-012")
        self.assertFalse(res["counts_pass"])
        self.assertFalse(res["opening_authorized"])

    def test_failure_row_cannot_carry_biological_negative(self):
        rows = [row("CREMV3-007", "positive", "positive") for _ in range(30)]
        rows += [row("CREMV3-007", "negative", "negative") for _ in range(59)]
        rows.append(row("CREMV3-007", "negative", "negative", device_failure=True))
        p = write_rows(rows)
        res = MOD.evaluate(p, "CREMV3-007")
        self.assertFalse(res["qc_pass"])
        self.assertFalse(res["opening_authorized"])
        self.assertTrue(any("cannot carry biological observer_state" in x for x in res["invalid_rows"]))

    def test_one_false_positive_blocks_specificity_confidence_rule(self):
        rows = [row("BELV3-012", "positive", "positive") for _ in range(30)]
        rows += [row("BELV3-012", "negative", "negative") for _ in range(59)]
        rows += [row("BELV3-012", "negative", "positive")]
        p = write_rows(rows)
        res = MOD.evaluate(p, "BELV3-012")
        self.assertFalse(res["specificity_pass"])
        self.assertFalse(res["opening_authorized"])


if __name__ == "__main__":
    unittest.main()
