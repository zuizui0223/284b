#!/usr/bin/env python3
"""Trace a mixed-provenance continuation; never decode model/prediction files."""
from __future__ import annotations
import argparse
import csv
from hashlib import sha256
import io
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
from zipfile import ZipFile

from scripts.continue_same_target_missing_taxa import (
    EXECUTION_SHA, SOURCE_RUN, MISSING, M_VALUES, PART_VERSION,
)
REPO = 'zuizui0223/284b'
AUDIT_ID = 10002365752
AUDIT_SHA = 'ee03b5ef5bad16fa16456ed1ad8c3324f4e812a15aa184c44c332e6a08221df7'
PREFIX = 'product-b-successor-layer1-fit-taxon-'
MODES = ('PRESERVED_SPECIMEN', 'HUMAN_OBSERVATION')
PROCEDURES = tuple(f'{s}|{m}' for s in ('all', 'vif', 'predictive_forward', 'niche_forward')
                   for m in ('logit_l2_C0.1_degree1', 'logit_l2_C1_degree2'))


def api(path):
    return subprocess.check_output(['gh', 'api', f'repos/{REPO}/{path}'])


def verify_gate(run, current, frozen):
    expected = {'id': SOURCE_RUN, 'head_sha': EXECUTION_SHA, 'run_attempt': 1,
                'status': 'completed', 'conclusion': 'cancelled', 'event': 'push',
                'path': '.github/workflows/same_target_successor_layer1_fit.yml',
                'head_branch': 'product-b-v5-obligate-invariant'}
    if any(run.get(k) != v for k, v in expected.items()):
        raise ValueError('original cancelled first attempt changed')
    if any(run.get(k, {}).get('full_name') != REPO for k in ('repository', 'head_repository')):
        raise ValueError('wrong original repository')
    def identities(payload):
        rows = payload['artifacts']
        if payload['total_count'] != len(rows) or len(rows) != 45:
            raise ValueError('expected the complete frozen inventory of 45 artifacts')
        if len({r['id'] for r in rows}) != 45:
            raise ValueError('duplicate artifact ID')
        result = {}
        for r in rows:
            if r.get('expired') is not False or r['workflow_run']['head_sha'] != EXECUTION_SHA or r['workflow_run']['id'] != SOURCE_RUN:
                raise ValueError('expired or different source artifact')
            if r['name'] in result:
                raise ValueError('duplicate artifact name')
            result[r['name']] = (r['id'], r['digest'])
        return result
    known = identities(frozen)
    if identities(current) != known:
        raise ValueError('completed original artifacts changed after terminal audit')
    names = {f'{PREFIX}{i}' for i in range(47) if i not in MISSING}
    if set(known) != names:
        raise ValueError('missing executions are not exactly indices 8 and 35')
    return {'original_source_run_id': SOURCE_RUN, 'original_execution_sha': EXECUTION_SHA,
            'original_attempt_status': 'cancelled', 'continuation_execution_authorized': True,
            'original_artifacts': {n: {'id': v[0], 'digest': v[1]} for n, v in sorted(known.items())},
            'tasks': [{'taxon_index': i, 'M_km': m} for i, m in itertools.product(sorted(MISSING), M_VALUES)],
            'original_45_refit_authorized': False, 'paired_prediction_opening_authorized': False,
            'completed_continuation_requires': 'all_45_original_artifacts_plus_all_6_M_partitions',
            'minimum_reference_taxa_unchanged': 30}


def read_rows(path):
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def join_csv(paths, output):
    fields, rows = [], []
    for path in paths:
        columns, data = read_rows(path)
        fields += [c for c in columns if c not in fields]
        rows.extend(data)
    with output.open('w', newline='', encoding='utf-8') as f:
        if fields:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    return rows


def assemble_taxon(parts, output, index, controller_sha, run_id):
    if index not in MISSING or output.exists() or len(parts) != 3:
        raise ValueError('invalid missing-taxon assembly or attempted overwrite')
    rows = [(json.loads((p / 'contract.json').read_text()), p) for p in parts]
    by_m = {}
    for c, p in rows:
        prov = c.get('continuation', {})
        m = prov.get('partition_M_km')
        if m in by_m or m not in M_VALUES:
            raise ValueError('duplicate or unexpected M partition')
        if (c.get('result_version') != PART_VERSION or c.get('taxon_index') != index
            or c.get('taxon') != MISSING[index] or c.get('M_km') != [m]
            or c.get('expected_fit_cells') != 16 or c.get('procedure_count') != 8
            or c.get('source_modes') != list(MODES)):
            raise ValueError('wrong partition type, identity, or denominator')
        for key in ('paired_discordance_computed', 'process_knockout_computed', 'reference_ceiling_read',
                    'raw_occurrence_rows_persisted', 'occurrence_coordinates_persisted'):
            if c.get(key) is not False:
                raise ValueError('partition crossed its information boundary')
        if c.get('prediction_surfaces_sealed') is not True:
            raise ValueError('unsealed partition')
        if (prov.get('original_execution_sha') != EXECUTION_SHA or prov.get('original_source_run') != SOURCE_RUN
            or prov.get('controller_sha') != controller_sha or prov.get('continuation_run_id') != run_id
            or prov.get('continuation_attempt') != 1):
            raise ValueError('mixed or untraced continuation attempts')
        if any(x.is_symlink() for x in p.rglob('*')):
            raise ValueError('artifact symlinks are forbidden')
        if sha256((p / 'sealed_prediction_surfaces.parquet').read_bytes()).hexdigest() != c['prediction_surface_sha256']:
            raise ValueError('sealed partition checksum mismatch')
        _, inv = read_rows(p / 'fit_inventory.csv')
        expected = set(itertools.product(MODES, (m,), PROCEDURES))
        keys = [(r['source'], int(r['M_km']), r['procedure']) for r in inv]
        if len(inv) != 16 or set(keys) != expected or any(r['taxon'] != MISSING[index] for r in inv):
            raise ValueError('incomplete or duplicate partition fit inventory')
        sealed = sum(r['state'] == 'successor_layer1_model_fit_sealed' for r in inv)
        unresolved = sum(r['state'] == 'successor_layer1_model_fit_unresolved' for r in inv)
        if sealed + unresolved != 16 or sealed != c['sealed_fit_cells'] or unresolved != c['unresolved_fit_cells'] or len(c['errors']) != unresolved:
            raise ValueError('partition fit/error accounting mismatch')
        by_m[m] = (c, p)
    if set(by_m) != set(M_VALUES):
        raise ValueError('M partitions missing')
    fingerprints = [c['continuation']['common_frame_fingerprint'] for c, _ in rows]
    if not fingerprints[0] or any(f != fingerprints[0] for f in fingerprints):
        raise ValueError('common source features, geometry, blocks, or seed drifted across partitions')
    if len({tuple(c['historical_specieskeys']) for c, _ in rows}) != 1:
        raise ValueError('historical species concept changed between partitions')
    output.mkdir(parents=True)
    dataset = output / 'sealed_prediction_surfaces.parquet'; dataset.mkdir()
    hashes = {}
    ordered_m = sorted(by_m, key=lambda m: (by_m[m][0]['sealed_fit_cells'] == 0, m))
    for order, m in enumerate(ordered_m):
        c, p = by_m[m]
        # Put a known nonempty schema first, retaining even empty partition files.
        # Opaque copies only: no Arrow reader or joblib deserializer is used.
        dest = dataset / f'{order}_M{m}.parquet'
        shutil.copyfile(p / 'sealed_prediction_surfaces.parquet', dest)
        hashes[dest.name] = sha256(dest.read_bytes()).hexdigest()
        if (p / 'models').exists():
            shutil.copytree(p / 'models', output / 'models', dirs_exist_ok=True)
        aux = output / 'partition_auxiliary' / f'M{m}'; aux.mkdir(parents=True)
        for name in ('selection_trace.csv', 'raster_provenance.csv', 'chelsa_resolution_ledger.csv', 'continuation_environment.txt'):
            if (p / name).exists(): shutil.copyfile(p / name, aux / name)
    paths = [by_m[m][1] for m in M_VALUES]
    for name in ('fit_inventory.csv', 'outer_cv_fold_metrics.csv'):
        join_csv([p / name for p in paths], output / name)
    full = dict(by_m[150][0])
    full.update(result_version='product_b_same_target_successor_layer1_fit_taxon_v0.1',
                M_km=list(M_VALUES), expected_fit_cells=48,
                sealed_fit_cells=sum(c['sealed_fit_cells'] for c, _ in rows),
                unresolved_fit_cells=sum(c['unresolved_fit_cells'] for c, _ in rows),
                errors=[e for m in M_VALUES for e in by_m[m][0]['errors']],
                prediction_surface_sha256=None, prediction_surface_layout='opaque_parquet_dataset',
                prediction_surface_parts_sha256=hashes)
    full['continuation'] = {**full['continuation'], 'partition_M_km': list(M_VALUES),
        'partition_contract_sha256': {str(m): sha256((p / 'contract.json').read_bytes()).hexdigest() for m, (_, p) in by_m.items()},
        'predictions_decoded_for_assembly': False, 'all_48_fit_cells_accounted': True}
    (output / 'contract.json').write_text(json.dumps(full, indent=2, sort_keys=True) + '\n')
    return full


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    gate = sub.add_parser('gate'); gate.add_argument('--output', type=Path, required=True)
    asm = sub.add_parser('assemble')
    asm.add_argument('--parts', type=Path, required=True)
    asm.add_argument('--fit-root', type=Path, required=True)
    asm.add_argument('--gate', type=Path, required=True)
    asm.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.command == 'gate':
        raw = api(f'actions/artifacts/{AUDIT_ID}/zip')
        if sha256(raw).hexdigest() != AUDIT_SHA:
            raise ValueError('terminal audit archive identity mismatch')
        with ZipFile(io.BytesIO(raw)) as archive:
            frozen = json.loads(archive.read('source_artifacts.json'))
        result = verify_gate(json.loads(api(f'actions/runs/{SOURCE_RUN}')),
                             json.loads(api(f'actions/runs/{SOURCE_RUN}/artifacts?per_page=100')), frozen)
    else:
        gate = json.loads(args.gate.read_text())
        if gate.get('continuation_execution_authorized') is not True:
            raise ValueError('continuation not authorized')
        # Revalidate immutable original inventory, never replace an old artifact.
        current = json.loads(api(f'actions/runs/{SOURCE_RUN}/artifacts?per_page=100'))
        expected = gate['original_artifacts']
        if current['total_count'] != 45 or len(current['artifacts']) != 45 or {
            a['name']: {'id': a['id'], 'digest': a['digest']} for a in current['artifacts']} != expected:
            raise ValueError('original artifact inventory drifted during continuation')
        if {p.name for p in args.fit_root.iterdir()} != set(expected):
            raise ValueError('downloaded original artifact directory inventory changed')
        contracts = list(args.parts.rglob('contract.json'))
        if len(contracts) != 6:
            raise ValueError('all six partition artifacts are required')
        restored = []
        for index in sorted(MISSING):
            dirs = [p.parent for p in contracts if json.loads(p.read_text()).get('taxon_index') == index]
            restored.append(assemble_taxon(dirs, args.fit_root / f'{PREFIX}{index}', index,
                                          os.environ['GITHUB_SHA'], int(os.environ['GITHUB_RUN_ID'])))
        if len(list(args.fit_root.rglob('contract.json'))) != 47:
            raise ValueError('completed continuation lacks exactly 47 taxon contracts')
        result = {**gate, 'continuation_run_id': int(os.environ['GITHUB_RUN_ID']),
                  'controller_sha': os.environ['GITHUB_SHA'], 'completed_taxa': 47,
                  'expected_source_cells': 2256, 'original_artifact_taxa_retained': 45,
                  'restored_taxa': sorted(MISSING.values()), 'existing_strict_postfit_authorized': True,
                  'heldout_opening_authorized': False, 'predictions_decoded_for_assembly': False,
                  'original_run_relabelled_success': False,
                  'assembled_contracts_sha256': {c['taxon']: sha256((args.fit_root / f"{PREFIX}{c['taxon_index']}" / 'contract.json').read_bytes()).hexdigest() for c in restored}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('original_artifacts', 'tasks')}, indent=2))


if __name__ == '__main__':
    main()
