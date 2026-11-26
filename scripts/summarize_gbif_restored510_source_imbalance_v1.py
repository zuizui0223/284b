#!/usr/bin/env python3
"""Descriptive 284b GBIF missing20 raw source-mode restoration asymmetry.

Input files are original signed source-mode sampling summaries plus the two
repaired-510-file aggregate GBIF receipts. No model fitting, species re-selection,
NEON plot observations, or taxon-wise statistical significance testing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL_HELD=ROOT/"results/product_b_same_target_source_mode_sampling_v0_1.json"
ORIGINAL_REF=ROOT/"results/product_b_same_target_successor_source_mode_sampling_v0_1.json"
RESTORED_HELD=ROOT/"results/gbif_restored510_heldout12_exposure_v1.json"
RESTORED_REF=ROOT/"results/gbif_restored510_reference47_exposure_v1.json"

MODES={"PRESERVED_SPECIMEN":"preserved_specimen","HUMAN_OBSERVATION":"human_observation"}


def load_source():
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in (ORIGINAL_HELD,ORIGINAL_REF,RESTORED_HELD,RESTORED_REF)]


def fraction(original:int, added:int)->float:
    if original<=0 or added<0:raise ValueError("unqualified raw denominator")
    return added/original


def audit()->dict:
    original_held,original_ref,restored_held,restored_ref=load_source()
    assert original_held["result_version"]=="product_b_same_target_source_mode_sampling_v0.1"
    assert original_ref["result_version"]=="product_b_same_target_successor_source_mode_sampling_v0.1"
    assert restored_held["status"]=="restored_510_focal_occurrence_exposure_scanned"
    assert restored_ref["status"]=="restored_files_scanned_for_frozen_47_reference_taxa"
    x=original_held["results"];y=original_ref["results"]
    fixed_h={t["requested_name"]:t for t in x if t["state"]=="source_mode_sampling_passed"}
    fixed_r={t["requested_name"]:t for t in y if t["state"]=="successor_source_mode_sampling_passed"}
    assert len(fixed_h)==12 and len(fixed_r)==47 and not set(fixed_h)&set(fixed_r)
    added_h={t["taxon"]:t for t in restored_held["specieskey_mode_raw_row_counts"]}
    added_r={t["taxon"]:t for t in restored_ref["taxon_level_raw_restored_counts"]}
    assert set(added_h)==set(fixed_h) and set(added_r)==set(fixed_r)

    summary={}
    for name,source,added,expected in [
        ("heldout12",fixed_h,restored_held["totals_by_source_mode"],12),
        ("reference47",fixed_r,restored_ref["raw_restored_present_counts_by_source"],47)
    ]:
        base={mode:sum(v[field]["raw_records"] for v in source.values())
              for mode,field in MODES.items()}
        assert len(source)==expected
        exposure={mode:int(added[mode]) for mode in MODES}
        summary[name]={
          "taxa":len(source),
          "original_raw_present_records_by_mode":base,
          "newly_restored_raw_present_records_by_mode":exposure,
          "extra_fraction_over_original_raw_by_mode":{
             mode:fraction(base[mode],exposure[mode]) for mode in MODES},
          "original_raw_total":sum(base.values()),
          "restored_raw_total":sum(exposure.values()),
          "restored_fraction_of_original_raw_total":
            sum(exposure.values())/sum(base.values())
        }
    contrasts=[]
    for taxon,old in sorted(fixed_h.items()):
        added=added_h[taxon]
        parts={}
        for mode,field in MODES.items():
            before=int(old[field]["raw_records"])
            new=int(added["modes"][mode]["restored_raw_present_occurrence_rows"])
            parts[mode]={"original_raw_count":before,"restored_raw_count":new,
                         "additional_vs_original_raw_fraction":fraction(before,new)}
        contrasts.append({
          "taxon":taxon,
          "sources":parts,
          "human_minus_preserved_fraction_pp":
             100*(parts["HUMAN_OBSERVATION"]["additional_vs_original_raw_fraction"]-
                  parts["PRESERVED_SPECIMEN"]["additional_vs_original_raw_fraction"])
        })
    assert all(z["sources"]["PRESERVED_SPECIMEN"]["restored_raw_count"]+
               z["sources"]["HUMAN_OBSERVATION"]["restored_raw_count"]>0 for z in contrasts)
    assert sum(z["sources"]["HUMAN_OBSERVATION"]["restored_raw_count"] for z in contrasts)==15329
    assert sum(z["sources"]["PRESERVED_SPECIMEN"]["restored_raw_count"] for z in contrasts)==2688

    return {
      "schema":"284b.gbif_missing20_raw_source_mode_imbalance.v1",
      "status":"retrospective_descriptive_only",
      "panels":summary,
      "heldout12_taxon_source_contrasts":contrasts,
      "notable_heldout":{
        "largest_human_restoration_fraction_taxon":
          max(contrasts,key=lambda z:z["sources"]["HUMAN_OBSERVATION"]["additional_vs_original_raw_fraction"])["taxon"],
        "largest_preserved_restoration_fraction_taxon":
          max(contrasts,key=lambda z:z["sources"]["PRESERVED_SPECIMEN"]["additional_vs_original_raw_fraction"])["taxon"],
        "taxa_human_relative_restoration_exceeds_preserved":
          sum(z["human_minus_preserved_fraction_pp"]>0 for z in contrasts),
        "taxa_preserved_relative_restoration_exceeds_human":
          sum(z["human_minus_preserved_fraction_pp"]<0 for z in contrasts)
      },
      "do_not_infer":[
        "admitted spatially thinned additions; source-specific model input change magnitude",
        "statistically independent observation counts; model refit response; ecological truth",
        "whether original q95 frozen-envelope conclusion persists in repaired-source experiment",
        "model fitting overlap with independent NEON plot labels",
      ],
      "frozen_original_Level_A_unchanged":True,
      "empirical_ledger_increment":0,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    d=audit()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":d["status"],
                      "panels":d["panels"],
                      "notable_heldout":d["notable_heldout"]}))


if __name__=="__main__":
    main()
