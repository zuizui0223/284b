"""Scientific-method invariance guards for the repaired-GBIF Artemisia fit pilot.

No data access. Assert that original all 48 model/adequacy iterations are
lexically unchanged in the derived fixed-spatial-geometry runner.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/"scripts/run_same_target_core19_layer1_fit_taxon_v0_4.py"
NEW=ROOT/"scripts/fit_gbif_repaired_Artemisia_fixed_original_centers_v1.py"


def model_body(path:Path)->str:
    code=path.read_text(encoding="utf-8")
    start="    for m in (150, 300, 500):\n        background = backgrounds[m]"
    stop="    predictions=pd.DataFrame(prediction_rows)"
    if code.count(start)!=1 or code.count(stop)!=1:
        raise ValueError("Original model fitting body could not be isolated")
    return code.split(start,1)[1].split(stop,1)[0]


class OriginalFittingInvarianceTests(unittest.TestCase):
    def test_all_8procedures_and_3M_fit_and_adequacy_body_byte_identical(self):
        self.assertEqual(model_body(OLD),model_body(NEW))

    def test_separate_result_version_and_original_geometry(self):
        code=NEW.read_text(encoding="utf-8")
        self.assertIn('HELDOUT_RESULT = "284b.gbif_repaired_Artemisia_fixed_old_centers_fit_v1"',code)
        self.assertIn("centers = np.load(centers_file, allow_pickle=False)",code)
        self.assertIn("if panel != \"heldout\" or taxon_index != 0",code)
        self.assertIn("source_entry",code) if "source_entry" in code else self.assertIn("prior_taxon",code)
        self.assertIn('"reference_ceiling_opened_or_read":False',code)
        self.assertIn('"paired_discordance_computed":False',code)


if __name__=="__main__":
    unittest.main()
