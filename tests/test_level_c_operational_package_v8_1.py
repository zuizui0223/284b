import csv
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "level_c_v8_1_eval", ROOT / "scripts" / "evaluate_level_c_field_calibration_v8_1.py"
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
CONTRACT = ROOT / "config" / "product_b_level_c_operational_package_v8_1.json"

FIELDS = [
    "candidate_id","calibration_unit_id","date_time","site_or_tree_id","gold_state","observer_state",
    "missing","device_failure","observer_failure","occlusion","unresolved_adjudication","notes"
]


def write_rows(rows):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8")
    with f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return Path(f.name)


def row(cid, gold, observed, **flags):
    result = {k: "false" for k in FIELDS}
    result.update({
        "candidate_id": cid,
        "calibration_unit_id": "u",
        "date_time": "2026-01-01T00:00:00",
        "site_or_tree_id": "s",
        "gold_state": gold,
        "observer_state": observed,
        "notes": "",
    })
    for key, value in flags.items():
        result[key] = "true" if value else "false"
    return result


class LevelCOperationalPackageV81Tests(unittest.TestCase):
    def test_repair_contract_changes_only_confidence_implementation_scope(self):
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(contract["repair_scope"], "confidence_bound_implementation_only")
        self.assertFalse(contract["field_calibration_data_seen_before_repair"])
        self.assertEqual(contract["scientific_thresholds_unchanged"]["sensitivity_min"], 0.80)
        self.assertEqual(contract["scientific_thresholds_unchanged"]["hard_fnr_max"], 0.20)
        self.assertEqual(contract["scientific_thresholds_unchanged"]["specificity_min"], 0.95)
        self.assertEqual(contract["minimum_clean_design_unchanged"]["gold_positive_required"], 30)
        self.assertEqual(contract["minimum_clean_design_unchanged"]["gold_negative_required"], 60)
        self.assertEqual(contract["empirical_ledger_increment"], 0)

    def test_exact_all_success_lower_bounds_match_closed_form(self):
        self.assertTrue(math.isclose(
            MOD.exact_one_sided_lower_bound(30, 30),
            0.05 ** (1.0 / 30.0),
            rel_tol=0.0,
            abs_tol=1e-12,
        ))
        self.assertTrue(math.isclose(
            MOD.exact_one_sided_lower_bound(60, 60),
            0.05 ** (1.0 / 60.0),
            rel_tol=0.0,
            abs_tol=1e-12,
        ))

    def test_minimum_clean_design_passes(self):
        rows = [row("CREMV3-007", "positive", "positive") for _ in range(30)]
        rows += [row("CREMV3-007", "negative", "negative") for _ in range(60)]
        result = MOD.evaluate(write_rows(rows), "CREMV3-007")
        self.assertTrue(result["opening_authorized"])
        self.assertEqual(result["confidence_method"], "exact_clopper_pearson_one_sided_95_percent")
        self.assertEqual(result["empirical_ledger_increment"], 0)

    def test_28_of_30_is_minimum_sensitivity_pass_at_minimum_positive_n(self):
        passing = [row("CREMV3-007", "positive", "positive") for _ in range(28)]
        passing += [row("CREMV3-007", "positive", "negative") for _ in range(2)]
        passing += [row("CREMV3-007", "negative", "negative") for _ in range(60)]
        result = MOD.evaluate(write_rows(passing), "CREMV3-007")
        self.assertTrue(result["sensitivity_pass"])
        self.assertGreaterEqual(result["one_sided_95_sensitivity_lower"], 0.80)

        failing = [row("CREMV3-007", "positive", "positive") for _ in range(27)]
        failing += [row("CREMV3-007", "positive", "negative") for _ in range(3)]
        failing += [row("CREMV3-007", "negative", "negative") for _ in range(60)]
        result = MOD.evaluate(write_rows(failing), "CREMV3-007")
        self.assertFalse(result["sensitivity_pass"])

    def test_one_false_positive_at_minimum_negative_n_fails_specificity(self):
        rows = [row("BELV3-012", "positive", "positive") for _ in range(30)]
        rows += [row("BELV3-012", "negative", "negative") for _ in range(59)]
        rows += [row("BELV3-012", "negative", "positive")]
        result = MOD.evaluate(write_rows(rows), "BELV3-012")
        self.assertFalse(result["specificity_pass"])
        self.assertFalse(result["opening_authorized"])

    def test_failure_or_missingness_never_becomes_biological_negative(self):
        rows = [row("CREMV3-007", "positive", "positive") for _ in range(30)]
        rows += [row("CREMV3-007", "negative", "negative") for _ in range(60)]
        rows.append(row("CREMV3-007", "negative", "negative", device_failure=True))
        result = MOD.evaluate(write_rows(rows), "CREMV3-007")
        self.assertFalse(result["qc_pass"])
        self.assertFalse(result["opening_authorized"])
        self.assertTrue(any("cannot carry biological observer_state" in item for item in result["invalid_rows"]))


if __name__ == "__main__":
    unittest.main()
