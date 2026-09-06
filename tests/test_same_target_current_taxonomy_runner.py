import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_same_target_calibration_current_taxonomy.py"


class SameTargetCurrentTaxonomyRunnerTests(unittest.TestCase):
    def test_runner_reuses_v7_2_current_taxonomy_contract(self):
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("GBIF_CURRENT_SPECIES_MATCH_ENDPOINT", text)
        self.assertIn("build_current_species_match_params", text)
        self.assertIn("parse_current_direct_taxonomy_resolution", text)
        self.assertNotIn('https://api.gbif.org/v1/species/match', text)

    def test_runner_parses_as_python(self):
        ast.parse(RUNNER.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
