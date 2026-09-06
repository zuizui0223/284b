#!/usr/bin/env python3
"""Union six successor taxonomy-only snapshot shards without matched-row counts."""
from __future__ import annotations
from dataclasses import asdict
import json
from pathlib import Path
from product_b_v7_3.taxonomy_identity import SnapshotTaxonomyTuple

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'artifacts/successor_snapshot_concept_shards'
CURRENT=ROOT/'results/product_b_same_target_successor_current_taxonomy_v0_1.json'
CONTRACT=ROOT/'config/product_b_same_target_successor_calibration_contract_v0_1.json'
OUTPUT=ROOT/'results/product_b_same_target_successor_snapshot_concept_tuples_v0_1.json'

def _t(r): return SnapshotTaxonomyTuple(species=str(r.get('species') or '').strip(),specieskey=str(r.get('specieskey') or '').strip(),taxonkey=str(r.get('taxonkey') or '').strip(),scientificname=str(r.get('scientificname') or '').strip(),taxonrank=str(r.get('taxonrank') or '').strip().upper())

def main()->int:
    current=json.loads(CURRENT.read_text()); contract=json.loads(CONTRACT.read_text()); minimum=int(contract['panel_rule']['minimum_complete_taxa_for_calibration'])
    names=tuple(sorted(str(r['accepted_name']).strip() for r in current['resolutions'] if r.get('state')=='successor_current_taxonomy_resolved_exact_accepted_species'))
    if len(names)<minimum: raise RuntimeError('successor current taxonomy below minimum')
    paths=sorted(INPUT.glob('product_b_same_target_successor_snapshot_concept_shard_*.json'))
    if len(paths)!=6: raise RuntimeError(f'expected 6 successor snapshot shards, found {len(paths)}')
    tuples={n:set() for n in names}; seen=set()
    forbidden=('matched_row_counts_persisted','per_file_matched_counts_persisted','raw_rows_persisted','coordinates_opened','occurrence_identifiers_opened','dates_opened','dataset_fields_opened','environmental_values_opened','current_layer1_paired_discordance_read','process_intervention_outcomes_read')
    for path in paths:
        p=json.loads(path.read_text()); idx=int(p['shard_index'])
        if p.get('result_version')!='product_b_same_target_successor_snapshot_concept_fragment_v0.1' or int(p['shard_count'])!=6 or idx in seen: raise RuntimeError('successor shard identity mismatch')
        seen.add(idx)
        if p.get('projected_columns')!=['species','specieskey','taxonkey','scientificname','taxonrank']: raise RuntimeError('projected columns drifted')
        if any(p.get(flag) is not False for flag in forbidden): raise RuntimeError('taxonomy shard crossed forbidden boundary')
        for name,rows in p.get('taxonomy_tuples',{}).items():
            if name not in tuples: raise RuntimeError('undeclared successor species in shard')
            for row in rows:
                item=_t(row)
                if item.species!=name: raise RuntimeError('tuple species differs from key')
                tuples[name].add(item)
    if seen!=set(range(6)): raise RuntimeError('successor shard coverage incomplete')
    taxa=[]; all_names=set(); nonempty=0
    for name in names:
        ordered=tuple(sorted(tuples[name])); keys=tuple(sorted({r.specieskey for r in ordered if r.specieskey})); hist=tuple(sorted({r.scientificname for r in ordered if r.scientificname})); ranks=tuple(sorted({r.taxonrank for r in ordered if r.taxonrank}))
        if ordered: nonempty+=1
        all_names.update(hist)
        taxa.append({'current_accepted_species':name,'taxonomy_tuples':[asdict(r) for r in ordered],'historical_specieskeys_preclosure':list(keys),'snapshot_scientific_names_for_review':list(hist),'observed_taxonranks':list(ranks),'taxonomy_tuple_present':bool(ordered)})
    authorized=nonempty>=minimum
    out={'result_version':'product_b_same_target_successor_snapshot_concept_tuples_v0.1','snapshot_date':'2026-08-01','successor_current_taxonomy_resolved':len(names),'taxa_with_nonempty_snapshot_taxonomy_tuples':nonempty,'taxa_without_snapshot_taxonomy_tuple':len(names)-nonempty,'frozen_calibration_minimum_taxa':minimum,'current_name_review_authorized':authorized,'if_below_minimum_state':None if authorized else 'successor_cross_source_calibration_unresolved','taxa':taxa,'distinct_snapshot_scientific_names_for_review':sorted(all_names),'taxonrank_used_as_exclusion_gate':False,'matched_row_counts_persisted':False,'raw_occurrence_rows_persisted':False,'coordinates_opened':False,'occurrence_identifiers_opened':False,'dates_opened':False,'dataset_fields_opened':False,'occurrence_sampling_authorized':False,'environmental_values_opened':False,'current_layer1_paired_discordance_read':False,'process_intervention_outcomes_read':False}
    OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'successor_current_taxonomy_resolved':len(names),'taxa_with_nonempty_snapshot_taxonomy_tuples':nonempty,'taxa_without_snapshot_taxonomy_tuple':len(names)-nonempty,'current_name_review_authorized':authorized},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
