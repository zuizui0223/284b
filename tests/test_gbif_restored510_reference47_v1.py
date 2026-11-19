"""Guard the original 47 reference taxa and complete key-set scan."""
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_gbif_restored510_reference47_v1 import fixed_reference_key_map


class ReferenceRestorationTests(unittest.TestCase):
    def test_frozen_predeclared_47_taxa_all_keys(self):
        m=fixed_reference_key_map()
        self.assertEqual(len(m),79)
        self.assertEqual(len(set(m.values())),47)
        self.assertTrue("Abies amabilis" in set(m.values()))
        self.assertTrue("Atriplex confertifolia" in set(m.values()))
        self.assertNotIn("Artemisia tridentata",set(m.values()))


if __name__=="__main__":
    unittest.main()
