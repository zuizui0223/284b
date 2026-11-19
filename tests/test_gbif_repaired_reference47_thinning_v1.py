"""Offline fixed-index shard accounting and full reference47 aggregation tests."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from audit_gbif_repaired_reference47_thinning_shard_v1 import choose_shard
from aggregate_gbif_repaired_reference47_thinning_v1 import aggregate
CONFIG=json.loads((ROOT/"config/gbif_repaired_reference47_thinning_v1.json").read_text())


def mock_shards():
    shards=[]
    for shard in range(8):
        part=choose_shard(CONFIG["taxon_fit_entries"],shard,8)
        rows=[]
        for entry in part:
            old={"PRESERVED_SPECIMEN":300+entry["index"],"HUMAN_OBSERVATION":500+entry["index"]}
            repaired={mode:n+2 for mode,n in old.items()}
            oldraw=sum(entry["original_raw_by_mode"].values())
            added=entry["restored_raw_total_all_modes"]
            rows.append({
                "taxon":entry["taxon"],"taxon_index":entry["index"],
                "historical_specieskeys":entry["historical_specieskeys"],
                "original_signed_fit_artifact_id":entry["signed_original_fit_artifact_id"],
                "repaired_raw_count_parity_passed":True,
                "original_raw_present_count":oldraw,"restored_510_only_raw_count":added,
                "expected_repaired_raw_present_count":oldraw+added,
                "actual_repaired_raw_present_count":oldraw+added,
                "original_signed_thinned_n":old,"repaired_thinned_n":repaired,
                "repaired_minus_original_thinned_n":{mode:2 for mode in old}
            })
        shards.append({
            "schema":"284b.gbif_repaired_reference47_thinning_shard.v1",
            "status":"repaired_reference_source_thinning_shard_qualified",
            "shard_index":shard,"shard_count":8,
            "original_repair_manifest_verified":True,
            "original_signed_fit_artifacts_verified":len(part),
            "taxon_results":rows
        })
    return shards


class Reference47ThinningTests(unittest.TestCase):
    def test_exact_shards_and_79_fixed_specieskeys(self):
        entries=CONFIG["taxon_fit_entries"]
        self.assertEqual(len(entries),47)
        self.assertEqual(sum(map(lambda e:len(e["historical_specieskeys"]),entries)),79)
        self.assertEqual(len({e["signed_original_fit_artifact_id"] for e in entries}),47)
        self.assertEqual([len(choose_shard(entries,i,8)) for i in range(8)],[6]*7+[5])
        self.assertTrue(CONFIG["no_panel_replacement"])
        self.assertFalse(CONFIG["full_q95_reference_recalibration"])

    def test_merge_full_47_taxa_preserves_each_source_denominator(self):
        result=aggregate(mock_shards(),CONFIG)
        self.assertEqual(result["prespecified_reference_taxa"],47)
        self.assertEqual(result["taxa_with_any_repaired_thinned_input_count_change"],47)
        self.assertEqual(result["source_mode_input_totals"]["PRESERVED_SPECIMEN"]["delta_source_inputs"],94)
        self.assertEqual(result["source_mode_input_totals"]["HUMAN_OBSERVATION"]["delta_source_inputs"],94)
        self.assertFalse(result["original_24_calibration_q95_refitted"])
        self.assertEqual(result["empirical_ledger_increment"],0)

    def test_missing_shard_wrong_taxon_or_bad_raw_parity_fail_closed(self):
        data=mock_shards()
        with self.assertRaises(ValueError):
            aggregate(data[:-1],CONFIG)
        bad=copy.deepcopy(data)
        bad[0]["taxon_results"][0]["taxon"]="after_outcome_substitution"
        with self.assertRaises(ValueError):
            aggregate(bad,CONFIG)
        bad=copy.deepcopy(data)
        bad[0]["taxon_results"][0]["repaired_raw_count_parity_passed"]=False
        with self.assertRaises(ValueError):
            aggregate(bad,CONFIG)


if __name__=="__main__":
    unittest.main()
