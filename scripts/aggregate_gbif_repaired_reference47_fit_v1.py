#!/usr/bin/env python3
"""Metadata-only, fail-closed 47-reference repaired-GBIF fit audit.

This does NOT calculate paired source D, q95, or a held-out endpoint.
It checks signed source and original-center identities, unchanged 48-cell
inventories, and counts the possible two-source paired model states per M/method.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import defaultdict
from pathlib import Path

MODES=("PRESERVED_SPECIMEN","HUMAN_OBSERVATION")
M=(150,300,500)
FIT="284b.gbif_repaired_reference47_fixed_old_centers_fit_v1"
GEOMETRY="ALL_47_ORIGINAL_SIGNED_REFERENCE_GEOMETRIES_VERIFIED_NO_MODELS"

def aggregate(manifest,source_audit,original_geometry,fitsets):
    entries=manifest.get("entries",[])
    if (manifest.get("status")!="PREDECLARED_REFERENCE47_ORIGINAL_GEOMETRY_ONLY"
        or len(entries)!=47 or [x.get("index") for x in entries]!=list(range(47))
        or source_audit.get("status")!="all_47_original_reference_source_input_parity_and_restoration_qualified"
        or original_geometry.get("status")!=GEOMETRY
        or original_geometry.get("reference_taxa_original_geometry_exactly_reproduced")!=47
        or len(fitsets)!=47):
        raise RuntimeError("All 47 original/source inputs are not qualified")
    older={row["index"]:row for row in original_geometry["reference_taxa"]}
    inputs={row["taxon_index"]:row for row in source_audit["fixed_taxon_input_deltas"]}
    selected={}
    joint=defaultdict(set)
    sealed_total=0
    unresolved_total=0
    procedure_names=None
    for c,rows in fitsets:
        idx=c.get("taxon_index")
        if type(idx) is not int or idx not in range(47) or idx in selected:
            raise RuntimeError("Expected exactly one original repaired fit per reference taxon")
        e=entries[idx];old=older[idx];ad=inputs[idx]
        if (c.get("result_version")!=FIT
            or c.get("core19_contract_version")!="product_b_same_target_core19_requalification_v0.4"
            or c.get("taxon")!=e["taxon"] or c.get("panel")!="successor"
            or c.get("historical_specieskeys")!=e["historical_specieskeys"]
            or c.get("original_qualification_artifact_id")!=e["original_qualification_artifact_id"]
            or c.get("original_fit_artifact_id")!=e["original_fit_artifact_id"]
            or c.get("original_12_block_centers_sha256")!=old["original_center_sha256"]
            or c.get("GBIF_source_arm")!="repaired_2026-08-01_10215_parquet_files"
            or c.get("repaired_source_thinned_presence_count")!=ad["repaired_thinned_n"]
            or c.get("active_predictors")!=[f"bio{i}" for i in range(1,20)]
            or c.get("M_km")!=[150,300,500] or c.get("procedure_count")!=8
            or c.get("source_modes")!=list(MODES)
            or c.get("expected_fit_cells")!=48 or len(rows)!=48
            or c.get("original_signed_comparison_frames_unchanged") is not True
            or c.get("background_rows_resampled_during_refit") is not False
            or c.get("posthoc_prediction_row_drop_used") is not False
            or c.get("counts_as_empirical_conclusion") is not False):
            raise RuntimeError("Signed reference fit identity or source design drift: "+str(idx))
        for field in ("paired_discordance_computed","reference_ceiling_opened_or_read",
                      "heldout_pairing_opened","process_knockout_computed"):
            if c.get(field) is not False:
                raise RuntimeError("Reference fit crossed forbidden endpoint")
        for field in ("original_12_block_centers_sha256","prediction_surface_sha256"):
            v=c[field]
            if not isinstance(v,str) or len(v)!=64:
                raise RuntimeError("Reference prediction/center SHA malformed")
        if c["core19_frame_sha256_by_M"]!=old["original_comparison_frame_sha256_by_M"]:
            raise RuntimeError("Original signed comparison frames not preserved")
        by={}
        for row in rows:
            source=row["source"];m=int(row["M_km"]);proc=row["procedure"]
            key=(m,proc,source)
            if source not in MODES or m not in M or key in by or int(row["n_background"])!=2000:
                raise RuntimeError("Source/procedure/M universe or fixed background changed")
            if (int(row["n_presence_thinned"])!=ad["repaired_thinned_n"][source]
                or row["core19_frame_sha256"]!=c["core19_frame_sha256_by_M"][str(m)]
                or row["state"] not in ("core19_layer1_model_fit_sealed","core19_layer1_model_fit_unresolved")):
                raise RuntimeError("Reference fit inventory source or state changed")
            by[key]=row
        procset={p for m,p,s in by}
        if len(procset)!=8 or len(by)!=48 or {m for m,p,s in by}!=set(M):
            raise RuntimeError("Incomplete model method/source inventory")
        if procedure_names is None:procedure_names=procset
        elif procset!=procedure_names:raise RuntimeError("Procedure names changed among reference taxa")
        sealed=sum(x["state"]=="core19_layer1_model_fit_sealed" for x in rows)
        if sealed!=c["sealed_fit_cells"] or 48-sealed!=c["unresolved_fit_cells"]:
            raise RuntimeError("Reference fitted-cell denominator discrepancy")
        sealed_total+=sealed;unresolved_total+=48-sealed
        for m in M:
            for proc in procset:
                if all(by[(m,proc,source)]["state"]=="core19_layer1_model_fit_sealed" for source in MODES):
                    joint[(m,proc)].add(idx)
        selected[idx]={"index":idx,"taxon":e["taxon"],"sealed_cells":sealed,
                       "unresolved_cells":48-sealed,"repaired_thinned_presence":ad["repaired_thinned_n"],
                       "prediction_sha256":c["prediction_surface_sha256"]}
    if sorted(selected)!=list(range(47)) or sealed_total+unresolved_total!=2256:
        raise RuntimeError("Full 47-reference fit denominator not preserved")
    joint_counts=[{"M_km":m,"procedure":proc,"two_source_fitted_taxa":len(joint[(m,proc)])}
                  for m in M for proc in sorted(procedure_names)]
    n_min=min(x["two_source_fitted_taxa"] for x in joint_counts)
    return {
      "schema":"284b.gbif_repaired_reference47_fit_metadata_audit.v1",
      "status":"REFERENCE47_FITS_ACCOUNTED_NO_PAIRED_SCORES_OR_Q95" if n_min>=30 else "STOP_REFERENCE47_PRE_D_MINIMUM_MODEL_FITS",
      "reference_taxa":47,"frozen_cells":2256,
      "sealed_source_model_fit_cells":sealed_total,
      "unresolved_source_model_fit_cells":unresolved_total,
      "reference_two_source_fitted_by_procedure_M":joint_counts,
      "minimum_two_source_fitted_taxa_per_method_M":n_min,
      "necessary_pre_D_30_taxon_fit_coverage":n_min>=30,
      "sufficient_for_reference_q95":False,
      "taxon_fit_receipts":[selected[i] for i in range(47)],
      "paired_prediction_surfaces_read":False,"reference_schoener_D_computed":False,
      "reference_q95_computed":False,"heldout12_opened":False,
      "NEON_field_outcomes_read":False,"empirical_ledger_increment":0,
      "submission_status":"HOLD",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fit-root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--source-audit",type=Path,required=True)
    p.add_argument("--original-geometry",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    args=p.parse_args()
    fitsets=[]
    for f in sorted(args.fit_root.rglob("contract.json")):
        c=json.loads(f.read_text(encoding="utf-8"))
        if c.get("result_version")!=FIT:continue
        inventory=f.parent/"fit_inventory.csv"
        with inventory.open(newline="",encoding="utf-8") as x:
            rows=list(csv.DictReader(x))
        raw=f.parent/"sealed_prediction_surfaces.parquet"
        if hashlib.sha256(raw.read_bytes()).hexdigest()!=c["prediction_surface_sha256"]:
            raise RuntimeError("Sealed repaired reference score-file bytes differ from fit receipt")
        fitsets.append((c,rows))
    d=aggregate(*[json.loads(path.read_text(encoding="utf-8")) for path in
                 (args.manifest,args.source_audit,args.original_geometry)],fitsets)
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:d[k] for k in ("status","sealed_source_model_fit_cells",
                    "unresolved_source_model_fit_cells","minimum_two_source_fitted_taxa_per_method_M")}))
    if d["necessary_pre_D_30_taxon_fit_coverage"] is not True:
        raise SystemExit("STOP: fewer than 30 paired source fits in at least one reference procedure/M cell")

if __name__=="__main__":main()
