#!/usr/bin/env python3
"""Scan one deterministic frozen snapshot shard for successor taxonomy tuples only."""
from __future__ import annotations
from dataclasses import asdict
import json, os
from pathlib import Path
import pyarrow.dataset as ds
import pyarrow.fs as pafs
from product_b_v7_2.snapshot_transport import EXPECTED_BUCKET, EXPECTED_OCCURRENCE_PREFIX, EXPECTED_REGION
from product_b_v7_3.taxonomy_identity import ALLOWED_COLUMNS, SnapshotTaxonomyTuple

ROOT=Path(__file__).resolve().parents[1]
CURRENT=ROOT/'results/product_b_same_target_successor_current_taxonomy_v0_1.json'
CONTRACT=ROOT/'config/product_b_same_target_successor_calibration_contract_v0_1.json'
DATASET_PATH=f"{EXPECTED_BUCKET}/{EXPECTED_OCCURRENCE_PREFIX.rstrip('/')}"


def main()->int:
    shard_index=int(os.environ.get('SHARD_INDEX','0')); shard_count=int(os.environ.get('SHARD_COUNT','6'))
    if not 0<=shard_index<shard_count: raise ValueError('invalid shard index/count')
    current=json.loads(CURRENT.read_text()); contract=json.loads(CONTRACT.read_text())
    if current.get('result_version')!='product_b_same_target_successor_current_taxonomy_v0.1': raise RuntimeError('successor current taxonomy result required')
    if current.get('occurrence_counts_opened') is not False or current.get('coordinates_opened') is not False: raise RuntimeError('occurrence boundary crossed')
    names=tuple(sorted(str(r['accepted_name']).strip() for r in current['resolutions'] if r.get('state')=='successor_current_taxonomy_resolved_exact_accepted_species'))
    minimum=int(contract['panel_rule']['minimum_complete_taxa_for_calibration'])
    if len(names)<minimum: raise RuntimeError('successor current taxonomy below frozen minimum; snapshot access remains closed')
    allowed=tuple(contract['taxonomy_concept_closure']['snapshot_taxonomy_fields_allowed'])
    if allowed!=tuple(ALLOWED_COLUMNS): raise RuntimeError('projected taxonomy columns drifted')
    fs=pafs.S3FileSystem(anonymous=True,region=EXPECTED_REGION)
    infos=fs.get_file_info(pafs.FileSelector(DATASET_PATH,recursive=False))
    paths=tuple(sorted(i.path for i in infos if i.type==pafs.FileType.File))
    if len(paths)!=9705: raise RuntimeError(f'frozen snapshot parquet object count changed: {len(paths)}')
    selected=paths[shard_index::shard_count]
    dataset=ds.dataset(list(selected),filesystem=fs,format='parquet')
    scanner=dataset.scanner(columns=list(ALLOWED_COLUMNS),filter=ds.field('species').isin(list(names)),batch_size=65536,use_threads=True)
    by={name:set() for name in names}
    for batch in scanner.to_batches():
        values=batch.to_pydict()
        for i in range(batch.num_rows):
            species=str(values['species'][i] or '').strip()
            if species not in by: raise ValueError('undeclared species returned')
            by[species].add(SnapshotTaxonomyTuple(species=species,specieskey=str(values['specieskey'][i] or '').strip(),taxonkey=str(values['taxonkey'][i] or '').strip(),scientificname=str(values['scientificname'][i] or '').strip(),taxonrank=str(values['taxonrank'][i] or '').strip().upper()))
    out={'result_version':'product_b_same_target_successor_snapshot_concept_fragment_v0.1','shard_index':shard_index,'shard_count':shard_count,'snapshot_date':'2026-08-01','projected_columns':list(ALLOWED_COLUMNS),'frozen_species_names':list(names),'taxonomy_tuples':{n:[asdict(x) for x in sorted(v)] for n,v in sorted(by.items()) if v},'matched_row_counts_persisted':False,'per_file_matched_counts_persisted':False,'raw_rows_persisted':False,'coordinates_opened':False,'occurrence_identifiers_opened':False,'dates_opened':False,'dataset_fields_opened':False,'environmental_values_opened':False,'current_layer1_paired_discordance_read':False,'process_intervention_outcomes_read':False}
    p=ROOT/f'artifacts/product_b_same_target_successor_snapshot_concept_shard_{shard_index}.json'; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'shard_index':shard_index,'species_with_taxonomy_tuples':len(out['taxonomy_tuples']),'matched_row_counts_persisted':False},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
