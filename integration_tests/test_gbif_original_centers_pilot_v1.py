"""Original 9705-file spatial block-center reconstruction contract guards."""
import hashlib
import json
import sys
from pathlib import Path
import unittest

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from reconstruct_original_gbif_center_pilot_v1 import hash_centers
CONTRACT=json.loads((ROOT/"config/gbif_original_centers_reconstruction_pilot_v1.json").read_text())


class OldBlockCenterTest(unittest.TestCase):
    def test_np_float64_byte_hash_is_deterministic(self):
        x=np.arange(36,dtype="<f8").reshape(12,3)
        self.assertEqual(hash_centers(x),hashlib.sha256(x.tobytes(order="C")).hexdigest())
        self.assertEqual(hash_centers(x.astype(">f8")),hash_centers(x))

    def test_one_taxon_and_frozen_source_identity(self):
        self.assertEqual(CONTRACT["taxon"],"Artemisia tridentata")
        self.assertEqual(CONTRACT["taxon_index"],0)
        self.assertEqual(CONTRACT["historical_parquet_count"],9705)
        self.assertEqual(CONTRACT["expected_original_common_geometry_cells"],6932)
        self.assertEqual(CONTRACT["expected_original_12block_centers_sha256"],
                         "b9a5db3a5e0324abfdd38626727c170911cfc8994321eb0d24e6d995cd088a15")
        self.assertEqual(CONTRACT["expected_source_thinned_counts"],{
            "PRESERVED_SPECIMEN":3285,"HUMAN_OBSERVATION":4516
        })
        self.assertTrue(CONTRACT["no_biological_prediction_scored"])
        self.assertEqual(CONTRACT["empirical_ledger_increment"],0)


if __name__=="__main__":
    unittest.main()
