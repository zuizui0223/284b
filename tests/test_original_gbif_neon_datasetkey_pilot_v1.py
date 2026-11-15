"""DatasetKey provenance accumulator tests with no GBIF/NEON network requests."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_original_gbif_neon_datasetkey_pilot_v1 import tally_retained_datasetkeys

ROOT=Path(__file__).resolve().parents[1]
K="3fed506c-d04f-4cd4-b373-bd602572f39b"


class Col:
    def __init__(self,v):self.v=v
    def astype(self,typ):return list(map(typ,self.v))


class Frame:
    def __init__(self,ids):self.ids=ids
    def __getitem__(self,key):
        assert key=="gbifID"
        return Col(self.ids)
    def __len__(self):return len(self.ids)


class DatasetkeyTests(unittest.TestCase):
    def test_raw_and_thinned_retained_source_neon_counts(self):
        raw={
            "PRESERVED_SPECIMEN":[{"key":"1","datasetKey":K},{"key":"2","datasetKey":"OTHER"}],
            "HUMAN_OBSERVATION":[{"key":"3","datasetKey":"OTHER2"}]
        }
        retained={"PRESERVED_SPECIMEN":Frame(["1","2"]),
                  "HUMAN_OBSERVATION":Frame(["3"])}
        d,missing=tally_retained_datasetkeys(raw,retained,lambda f,cell_size_degrees:f,
                                           cell_degrees=.05)
        self.assertEqual(missing,0)
        self.assertEqual(d["PRESERVED_SPECIMEN"]["source_thinned_known_NEON_dataset_rows"],1)
        self.assertEqual(d["PRESERVED_SPECIMEN"]["source_thinned_model_presence_rows"],2)
        self.assertNotIn("1",str(d))

    def test_mapping_failure_stops(self):
        raw={"PRESERVED_SPECIMEN":[{"key":"1","datasetKey":K}]}
        bad={"PRESERVED_SPECIMEN":Frame(["WRONG"])}
        with self.assertRaises(RuntimeError):
            tally_retained_datasetkeys(raw,bad,lambda f,cell_size_degrees:f,
                                       cell_degrees=.05)

    def test_datasetkey_conflict_stops(self):
        raw={"PRESERVED_SPECIMEN":[
            {"key":"1","datasetKey":K},
            {"key":"1","datasetKey":"OTHER"}]}
        with self.assertRaises(ValueError):
            tally_retained_datasetkeys(raw,{"PRESERVED_SPECIMEN":Frame(["1"])},
                                       lambda f,cell_size_degrees:f,cell_degrees=.05)

    def test_predeclared_taxon_and_counts(self):
        c=json.loads((ROOT/"config/original_gbif_neon_datasetkey_pilot_v1.json").read_text())
        self.assertEqual(c["pilot"]["taxon"],"Artemisia tridentata")
        self.assertEqual(c["pilot"]["original_registry_index"],0)
        self.assertEqual(c["pilot"]["expected_thinned_model_presence_counts"]["PRESERVED_SPECIMEN"],3285)
        self.assertFalse(c["no_plot_species_outcomes_read"])


if __name__=="__main__":
    unittest.main()
