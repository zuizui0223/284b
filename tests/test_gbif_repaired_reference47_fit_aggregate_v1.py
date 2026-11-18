"""Complete 47-repaired-reference pre-q95 fit accounting tests, no score reading."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from aggregate_gbif_repaired_reference47_fit_v1 import aggregate

SHA="0"*64
class RepairedReference47FitAggregate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads((ROOT/"config/gbif_original_reference47_geometry_manifest_v1.json").read_text())
        cls.a=json.loads((ROOT/"results/gbif_repaired_reference47_thinning_v1.json").read_text())
        cls.geom={
            "status":"ALL_47_ORIGINAL_SIGNED_REFERENCE_GEOMETRIES_VERIFIED_NO_MODELS",
            "reference_taxa_original_geometry_exactly_reproduced":47,
            "reference_taxa":[{
                "index":i,"original_center_sha256":SHA,
                "original_comparison_frame_sha256_by_M":{"150":SHA,"300":SHA,"500":SHA}
            } for i in range(47)]}
        cls.fitsets=[]
        for i,e in enumerate(cls.m["entries"]):
            src=cls.a["fixed_taxon_input_deltas"][i]["repaired_thinned_n"]
            c={
              "result_version":"284b.gbif_repaired_reference47_fixed_old_centers_fit_v1",
              "core19_contract_version":"product_b_same_target_core19_requalification_v0.4",
              "taxon_index":i,"taxon":e["taxon"],"panel":"successor",
              "historical_specieskeys":e["historical_specieskeys"],
              "original_qualification_artifact_id":e["original_qualification_artifact_id"],
              "original_fit_artifact_id":e["original_fit_artifact_id"],
              "original_12_block_centers_sha256":SHA,
              "GBIF_source_arm":"repaired_2026-08-01_10215_parquet_files",
              "repaired_source_thinned_presence_count":src,
              "active_predictors":[f"bio{n}" for n in range(1,20)],
              "M_km":[150,300,500],"procedure_count":8,"source_modes":["PRESERVED_SPECIMEN","HUMAN_OBSERVATION"],
              "expected_fit_cells":48,"sealed_fit_cells":48,"unresolved_fit_cells":0,
              "original_signed_comparison_frames_unchanged":True,
              "background_rows_resampled_during_refit":False,
              "posthoc_prediction_row_drop_used":False,
              "counts_as_empirical_conclusion":False,
              "paired_discordance_computed":False,"reference_ceiling_opened_or_read":False,
              "heldout_pairing_opened":False,"process_knockout_computed":False,
              "prediction_surface_sha256":SHA,
              "core19_frame_sha256_by_M":{"150":SHA,"300":SHA,"500":SHA}
            }
            inv=[{"source":mode,"M_km":str(m),"procedure":f"p{j}",
                  "n_background":"2000","n_presence_thinned":str(src[mode]),
                  "core19_frame_sha256":SHA,"state":"core19_layer1_model_fit_sealed"}
                 for m in (150,300,500) for mode in c["source_modes"] for j in range(8)]
            cls.fitsets.append((c,inv))
    def test_frozen_47_2256_and_no_calibration_open(self):
        a=aggregate(self.m,self.a,self.geom,self.fitsets)
        self.assertEqual(a["frozen_cells"],2256)
        self.assertEqual(a["sealed_source_model_fit_cells"],2256)
        self.assertEqual(a["minimum_two_source_fitted_taxa_per_method_M"],47)
        self.assertEqual(len(a["reference_two_source_fitted_by_procedure_M"]),24)
        self.assertFalse(a["reference_q95_computed"])
        self.assertEqual(a["status"],"REFERENCE47_FITS_ACCOUNTED_NO_PAIRED_SCORES_OR_Q95")
    def test_incomplete_denominator_and_sha_rejected(self):
        with self.assertRaises(RuntimeError):aggregate(self.m,self.a,self.geom,self.fitsets[:-1])
        d=copy.deepcopy(self.fitsets);d[0][0]["original_12_block_centers_sha256"]="bad"
        with self.assertRaises(RuntimeError):aggregate(self.m,self.a,self.geom,d)
        d=copy.deepcopy(self.fitsets);d[0][0]["reference_ceiling_opened_or_read"]=True
        with self.assertRaises(RuntimeError):aggregate(self.m,self.a,self.geom,d)
    def test_low_pre_d_coverage_is_recorded_as_stop_not_rescued(self):
        d=copy.deepcopy(self.fitsets)
        for i in range(18):
            c,inv=d[i]
            for row in inv:
                if row["M_km"]=="150" and row["procedure"]=="p0" and row["source"]=="HUMAN_OBSERVATION":
                    row["state"]="core19_layer1_model_fit_unresolved"
            c["sealed_fit_cells"]=47;c["unresolved_fit_cells"]=1
        a=aggregate(self.m,self.a,self.geom,d)
        self.assertEqual(a["minimum_two_source_fitted_taxa_per_method_M"],29)
        self.assertEqual(a["status"],"STOP_REFERENCE47_PRE_D_MINIMUM_MODEL_FITS")
        self.assertFalse(a["necessary_pre_D_30_taxon_fit_coverage"])
if __name__=="__main__":unittest.main()
