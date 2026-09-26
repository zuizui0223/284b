import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "manuscript" / "PAPER1_REVIEWER_ATTACK_MATRIX_V1.md"


class Paper1ReviewerAttackMatrixV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = MATRIX.read_text(encoding="utf-8")

    def test_all_ten_reviewer_objections_are_present(self):
        self.assertEqual(self.text.count("## Reviewer objection "), 10)
        for i in range(1, 11):
            self.assertIn(f"## Reviewer objection {i} —", self.text)

    def test_closest_prior_art_is_explicitly_conceded(self):
        for phrase in [
            "Adaptive Preregistration",
            "Wilkinson et al. (2021)",
            "Blanchet et al. (2020)",
            "Galiana et al. (2024)",
            "Chadwick et al. (2024)",
            "Getz et al. (2018)",
            "Pacifici et al. (2017)",
            "Structural causal models and DAGs",
        ]:
            self.assertIn(phrase, self.text)

    def test_novelty_is_relation_authorization_not_upstream_methods(self):
        self.assertIn("relation-endpoint authorization layer", self.text)
        self.assertIn("logically subsequent composition step", self.text)
        for forbidden_claim in [
            "not a new occupancy or detection model",
            "not a new JSDM",
            "not a new data-fusion method",
            "not a new causal-identification calculus",
            "not a new preregistration framework",
            "not a new probability theorem",
        ]:
            self.assertIn(forbidden_claim, self.text)

    def test_empirical_boundaries_remain_frozen(self):
        self.assertIn("Level A is the sole completed empirical endpoint", self.text)
        self.assertIn("Level B remains unopened", self.text)
        self.assertIn("focal Level-C outcomes remain sealed", self.text)
        self.assertIn("empirical ledger = 1", self.text)
        self.assertIn("12 taxa", self.text)
        self.assertIn("not 283 cells", self.text)
        self.assertIn("No focal Level-C dependency is confirmed or falsified", self.text)
        self.assertIn("Empirical ledger increment from this audit:** 0", self.text)

    def test_jsdm_and_dag_boundaries_are_not_straw_men(self):
        self.assertIn("Joint models can estimate statistical coupling", self.text)
        self.assertIn("does not imply that joint distributions are statistically unknowable", self.text)
        self.assertIn("DAGs provide a much richer calculus for causal identification", self.text)
        self.assertIn("does **not** claim causal-effect identification", self.text)

    def test_unresolved_state_is_positioned_downstream_of_detection_models(self):
        self.assertIn("the endpoint consumes that qualified answer", self.text)
        self.assertIn("not presented as a replacement for detection-aware modelling", self.text)
        self.assertIn("1-a1", self.text)
        self.assertIn("1-a0", self.text)


if __name__ == "__main__":
    unittest.main()
