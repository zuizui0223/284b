#!/usr/bin/env python3
"""Strict source-only source-balance audit for all 59 originally fixed taxa."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
from hashlib import sha256
from statistics import median

MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")
EXPECT={
 "heldout":(12,"284b.gbif_repaired_source_input_thinning_results.v1","REPAIRED_SOURCE_THINNING_QUANTIFIED_12_TAXA_NO_MODEL_REFIT"),
 "reference":(47,"284b.gbif_repaired_reference47_thinning_results.v1","all_47_original_reference_source_input_parity_and_restoration_qualified"),
}
ORIGINAL={
 "heldout":{"PRESERVED_SPECIMEN":15654,"HUMAN_OBSERVATION":31727},
 "reference":{"PRESERVED_SPECIMEN":87979,"HUMAN_OBSERVATION":978446},
}

def require(ok,message):
    if not ok:raise ValueError(message)

def extract(panel,receipt):
    n,schema,status=EXPECT[panel]
    require(receipt.get("schema")==schema and receipt.get("status")==status,panel+" invalid receipt")
    neon_key="NEON_plot_species_outcomes_read" if panel=="heldout" else "NEON_plant_plot_outcomes_read"
    require(receipt.get(neon_key) is False and receipt.get("empirical_ledger_increment")==0,panel+" endpoint boundary")
    if panel=="heldout":
        require(receipt.get("frozen_original_heldout_taxa")==12 and receipt.get("taxa_qualified_repaired_raw_parity")==12
                and receipt.get("original_fit_ZIP_SHA_verified")==12
                and receipt.get("repaired_prediction_scores_opened") is False
                and receipt.get("repaired_reference_q95_opened") is False
                and receipt.get("repaired_SDM_models_fit") is False
                and (receipt.get("historical_complete_S3_subset_file_count"),receipt.get("repaired_S3_file_count"),receipt.get("repaired_restored_file_count"))==(9705,10215,510),
                "heldout provenance not complete")
        data=receipt.get("per_taxon_source_mode_result",[])
    else:
        require(receipt.get("completed_and_verified_shards")==8 and receipt.get("signed_original_fit_artifact_inputs_verified")==47
                and receipt.get("prespecified_reference_taxa")==47
                and receipt.get("source_repair_check_against_exact_9705_and_10215_object_manifests") is True
                and receipt.get("reference_envelopes_and_heldout_robustness_tested") is False
                and receipt.get("original_24_calibration_q95_refitted") is False,
                "reference provenance not complete")
        data=receipt.get("fixed_taxon_input_deltas",[])
    require(len(data)==n,panel+" taxon denominator")
    rows=[];names=set()
    for x in data:
        taxon=x.get("taxon")
        require(isinstance(taxon,str) and bool(taxon.strip()) and taxon not in names,panel+" taxon duplication")
        names.add(taxon)
        if panel=="heldout":
            old=x["original_signed_source_thinned_model_presence"]
            new=x["repaired_source_thinned_presence"]
            require(all(x["raw_reconstruction_integrity"][m]["matched"] is True for m in MODES),"heldout raw parity")
            delta=x["repaired_minus_original_source_thinned_presence"]
        else:
            old=x["original_signed_thinned_n"];new=x["repaired_thinned_n"]
            require(x.get("repaired_raw_count_parity_passed") is True,"reference raw parity")
            delta=x["repaired_minus_original_thinned_n"]
        require(all(type(old[m]) is int and type(new[m]) is int and old[m]>0 and new[m]>=old[m] and delta[m]==new[m]-old[m] for m in MODES),
                taxon+" count integrity failed")
        if panel=="heldout":
            require(all(abs(x["repaired_over_original_thinned_presence_ratio"][m]-new[m]/old[m])<1e-12 for m in MODES),
                    taxon+" ratio mismatch")
        p0,p1=old[MODES[0]],new[MODES[0]]
        h0,h1=old[MODES[1]],new[MODES[1]]
        rows.append(dict(panel=panel,taxon=taxon,old_specimen=p0,new_specimen=p1,
                         old_human=h0,new_human=h1,specimen_fraction=(p1-p0)/p0,
                         human_fraction=(h1-h0)/h0,balance_multiplier=(h1*p0)/(h0*p1)))
    require(all(sum(r["old_specimen" if m==MODES[0] else "old_human"] for r in rows)==ORIGINAL[panel][m] for m in MODES),
            panel+" signed original totals changed")
    return rows

def summarize(rows):
    require(bool(rows),"No source taxa")
    mode={}
    for short in ("specimen","human"):
        old=sum(r["old_"+short] for r in rows);new=sum(r["new_"+short] for r in rows)
        mode[short]=dict(original=old,repaired=new,increment=new-old,
                         weighted_increment_pct=round(100*(new-old)/old,10),
                         taxon_equal_weight_median_increment_pct=round(100*median(r[short+"_fraction"] for r in rows),10))
    return dict(taxa=len(rows),per_mode=mode,
                taxa_with_any_source_increment_at_least_5pct=sum(max(r["specimen_fraction"],r["human_fraction"])>=.05 for r in rows),
                human_to_specimen_ratio_up=sum(r["balance_multiplier"]>1 for r in rows),
                human_to_specimen_ratio_down=sum(r["balance_multiplier"]<1 for r in rows),
                human_to_specimen_ratio_equal=sum(r["balance_multiplier"]==1 for r in rows),
                max_specimen_gain_taxon=max(rows,key=lambda r:(r["specimen_fraction"],r["taxon"]))["taxon"],
                max_specimen_gain_pct=round(100*max(r["specimen_fraction"] for r in rows),10))

def build(heldout,reference,sha):
    rows=extract("heldout",heldout)+extract("reference",reference)
    require(len(rows)==59 and len({r["taxon"] for r in rows})==59,"59 distinct taxon names required")
    panels={p:summarize([r for r in rows if r["panel"]==p]) for p in ("heldout","reference")}
    panels["combined"]=summarize(rows)
    require(panels["combined"]["per_mode"]["specimen"]["original"]==103633 and
            panels["combined"]["per_mode"]["human"]["original"]==1010173,"original overall count identity")
    out=dict(schema="284b.gbif_repaired_59taxa_source_balance.v1",
             status="VERIFIED_SOURCE_ONLY_NO_MODEL_OR_ECOLOGICAL_OUTCOME",
             input_receipt_sha256=sha,panels=panels,original_taxa_fixed=True,
             raw_occurrences_read=False,NEON_plot_species_outcomes_read=False,
             repaired_model_predictions_read=False,q95_reference_read=False,
             independent_biological_validation_performed=False,empirical_ledger_increment=0,
             interpretation="Source-specific changes in spatially-thinned admitted model inputs, not ecological predictions or source agreement.")
    return out,sorted(rows,key=lambda r:(r["panel"],r["taxon"]))

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--heldout",type=Path,default=Path("results/gbif_repaired_heldout12_thinning_v1.json"))
    a.add_argument("--reference",type=Path,default=Path("results/gbif_repaired_reference47_thinning_v1.json"))
    a.add_argument("--out-json",type=Path,required=True)
    a.add_argument("--out-csv",type=Path,required=True)
    opt=a.parse_args()
    source=[];digest={}
    for name,path in (("heldout",opt.heldout),("reference",opt.reference)):
        b=path.read_bytes();source.append(json.loads(b));digest[name]=sha256(b).hexdigest()
    summary,rows=build(source[0],source[1],digest)
    opt.out_json.parent.mkdir(parents=True,exist_ok=True)
    opt.out_csv.parent.mkdir(parents=True,exist_ok=True)
    opt.out_json.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    with opt.out_csv.open("w",newline="",encoding="utf-8") as f:
        keys=list(rows[0]);w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
    print(json.dumps(summary["panels"]["combined"],sort_keys=True))

if __name__=="__main__":
    main()
