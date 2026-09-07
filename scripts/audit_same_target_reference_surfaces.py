#!/usr/bin/env python3
"""Diagnose only already-authorized successor predictions; never repair or fit.

The two archives and analysis checkout are fixed. Recover pre-D authorization
from the original helpers and reconcile it with the original calibration table.
Decode no model, held-out prediction, or unauthorized prediction cell. Report
finite-support counts only; do not compute D on an altered support.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import io
import json
from math import isfinite
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
from zipfile import ZipFile

REFERENCE_ID = 10006933587
REFERENCE_SHA = '2607ffb09c2236821edb95907f842a44b4a6abb437855c227a479fa92b43570c'
BUNDLE_ID = 10006924897
BUNDLE_SHA = '28fdf3e39c7e41d2250bf8ce9ea4636837ed662951da60bd8eb466747df88615'
ANALYSIS_SHA = '89f1a01386d5906420cb625dbf87ee18d60672e5'
MODES = ('PRESERVED_SPECIMEN', 'HUMAN_OBSERVATION')
BASE = 'analysis/fit_artifacts/'
RESULTS = 'analysis/results/'


def checked_zip(path: Path, expected: str) -> ZipFile:
    if sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('archive digest mismatch')
    archive = ZipFile(path)
    names = archive.namelist()
    if len(names) != len(set(names)):
        raise ValueError('duplicate archive member')
    for name in names:
        p = PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts:
            raise ValueError('unsafe archive member')
    return archive


def diagnose(ids_a, scores_a, ids_b, scores_b):
    """Replay strict vector preconditions and count support, without computing D."""
    a = [float(v) for v in scores_a]
    b = [float(v) for v in scores_b]
    fa = sum(isfinite(v) for v in a)
    fb = sum(isfinite(v) for v in b)
    same = set(ids_a) == set(ids_b)
    unique = len(ids_a) == len(set(ids_a)) and len(ids_b) == len(set(ids_b))
    joint = None
    if same and unique and len(ids_a) == len(a) and len(ids_b) == len(b):
        bm = dict(zip(ids_b, b))
        joint = sum(isfinite(v) and isfinite(bm[k]) for k, v in zip(ids_a, a))
    reason = 'strict_surface_complete'
    if len(ids_a) != len(a) or len(ids_b) != len(b):
        reason = 'row_score_alignment_failure'
    elif not a or not b:
        reason = 'empty_vector'
    elif not unique:
        reason = 'duplicate_row_ids'
    elif not same:
        reason = 'row_set_mismatch'
    elif fa != len(a) or fb != len(b):
        reason = 'nonfinite_prediction_scores'
    elif any(v < 0 for v in a + b):
        reason = 'negative_prediction_scores'
    elif sum(a) <= 0 or sum(b) <= 0:
        reason = 'nonpositive_prediction_mass'
    return dict(integrity_state=reason, rows_a=len(a), rows_b=len(b),
                finite_a=fa, finite_b=fb, joint_finite_rows=joint,
                row_sets_equal=same, row_ids_unique=unique)


def audit(reference_zip: Path, bundle_zip: Path, analysis_root: Path, output: Path):
    head = subprocess.check_output(['git', '-C', str(analysis_root), 'rev-parse', 'HEAD'], text=True).strip()
    if head != ANALYSIS_SHA:
        raise ValueError('analysis checkout is not the frozen implementation')
    subprocess.run(['git', '-C', str(analysis_root), 'diff', '--exit-code', 'HEAD', '--'], check=True)
    sys.path.insert(0, str(analysis_root.resolve()))
    import pandas as pd
    from scripts.calibrate_same_target_successor_pairing_strict import _preaudit_taxon, _feasibility_map
    from product_b_v5.prediction_opening import read_authorized_prediction_cells
    with checked_zip(reference_zip, REFERENCE_SHA) as ref, checked_zip(bundle_zip, BUNDLE_SHA) as bundle:
        feasibility = json.loads(ref.read(RESULTS + 'product_b_same_target_successor_reference_feasibility_v0_1.json'))
        summary = json.loads(ref.read(RESULTS + 'product_b_same_target_successor_pairing_calibration_v0_1.json'))
        source_fit = json.loads(ref.read(RESULTS + 'product_b_same_target_successor_layer1_fit_v0_1.json'))
        original = pd.read_csv(io.BytesIO(ref.read(RESULTS + 'product_b_same_target_successor_pairing_cells_v0_1.csv')))
        contract = json.loads((analysis_root / 'config/product_b_same_target_source_model_fit_contract_v0_1.json').read_text())
        gates = _feasibility_map(feasibility)
        keys = ['taxon', 'M_km', 'procedure']
        if len(original) != 1128 or original.duplicated(keys).any():
            raise ValueError('original pair inventory incomplete or duplicated')
        original = original.set_index(keys)
        if source_fit['taxa_with_prediction_artifacts'] != 47 or source_fit['expected_fit_cells'] != 2256:
            raise ValueError('source denominator changed')
        names = sorted(n for n in bundle.namelist() if n.startswith(BASE) and n.endswith('/contract.json'))
        if len(names) != 47:
            raise ValueError('bundle must have exactly 47 taxon contracts')
        output_rows = []
        prediction_members = {}
        metadata_members = {}
        with tempfile.TemporaryDirectory() as temp:
            for name in names:
                c = json.loads(bundle.read(name))
                expected_c = next(t for t in source_fit['taxa'] if t['taxon'] == c['taxon'])
                if c != expected_c:
                    raise ValueError('bundle contract differs from source aggregate')
                prefix = name.rsplit('/', 1)[0] + '/'
                directory = Path(temp) / str(c['taxon_index']); directory.mkdir()
                for leaf in ('contract.json', 'fit_inventory.csv', 'outer_cv_fold_metrics.csv'):
                    raw = bundle.read(prefix + leaf)
                    (directory / leaf).write_bytes(raw)
                    metadata_members[prefix + leaf] = sha256(raw).hexdigest()
                prelim, allowed = _preaudit_taxon(c, directory, contract, gates)
                for row in prelim:
                    key = (row['taxon'], row['M_km'], row['procedure'])
                    saved = original.loc[key]
                    for flag in ('taxon_pre_discordance_eligible', 'reference_pre_discordance_opening_authorized', 'prediction_materialization_authorized'):
                        if bool(saved[flag]) != row[flag]:
                            raise ValueError('pre-D authorization differs from completed calibration')
                surface = directory / 'sealed_prediction_surfaces.parquet'
                if allowed:
                    if c.get('prediction_surface_layout') == 'opaque_parquet_dataset':
                        surface.mkdir()
                        for leaf, expected in c['prediction_surface_parts_sha256'].items():
                            if Path(leaf).name != leaf or not leaf.endswith('.parquet'):
                                raise ValueError('unsafe prediction part')
                            raw = bundle.read(prefix + 'sealed_prediction_surfaces.parquet/' + leaf)
                            if sha256(raw).hexdigest() != expected:
                                raise ValueError('prediction part seal mismatch')
                            (surface / leaf).write_bytes(raw)
                            prediction_members[prefix + 'sealed_prediction_surfaces.parquet/' + leaf] = expected
                    else:
                        raw = bundle.read(prefix + 'sealed_prediction_surfaces.parquet')
                        if sha256(raw).hexdigest() != c['prediction_surface_sha256']:
                            raise ValueError('prediction seal mismatch')
                        surface.write_bytes(raw)
                        prediction_members[prefix + 'sealed_prediction_surfaces.parquet'] = c['prediction_surface_sha256']
                predictions = read_authorized_prediction_cells(surface, allowed)
                if len(predictions) and set(predictions['taxon']) != {c['taxon']}:
                    raise ValueError('prediction taxon mismatch')
                for row in prelim:
                    key = (row['taxon'], row['M_km'], row['procedure'])
                    item = {k: row[k] for k in keys}
                    item['prediction_materialization_authorized'] = row['prediction_materialization_authorized']
                    item['prediction_rows_materialized'] = False
                    item['d_available_in_original_calibration'] = bool(original.loc[key, 'paired_prediction_surface_opened'])
                    item['integrity_state'] = 'kept_closed_by_original_authorization'
                    if row['prediction_materialization_authorized']:
                        group = predictions[(predictions['M_km'] == row['M_km']) & (predictions['procedure'] == row['procedure'])]
                        item['prediction_rows_materialized'] = not group.empty
                        if set(group['source']) != set(MODES):
                            item['integrity_state'] = 'missing_source_rows'
                        else:
                            a = group[group['source'] == MODES[0]]; b = group[group['source'] == MODES[1]]
                            item.update(diagnose(a['comparison_row_id'].astype(str).tolist(), a['ecological_score'],
                                                 b['comparison_row_id'].astype(str).tolist(), b['ecological_score']))
                        if (item['integrity_state'] == 'strict_surface_complete') != item['d_available_in_original_calibration']:
                            raise ValueError('strict support diagnosis differs from original D availability')
                    output_rows.append(item)
        counts = Counter(r['integrity_state'] for r in output_rows)
        authorized = sum(r['prediction_materialization_authorized'] for r in output_rows)
        materialized = sum(r['prediction_rows_materialized'] for r in output_rows)
        d_available = sum(r['d_available_in_original_calibration'] for r in output_rows)
        if len(output_rows) != 1128 or authorized != materialized or d_available != summary['paired_surfaces_opened_authorized_cells']:
            raise ValueError('opening accounting did not reconcile')
        receipt = dict(result_version='same_target_reference_surface_diagnostic_v0.1',
            source_run_id=34078855468, analysis_sha=ANALYSIS_SHA,
            input_artifacts={str(REFERENCE_ID): REFERENCE_SHA, str(BUNDLE_ID): BUNDLE_SHA},
            scheduled_taxa=47, source_cells=2256, paired_cells=1128,
            prediction_cells_authorized=authorized, prediction_cells_materialized=materialized,
            prediction_cells_kept_closed=1128-materialized,
            d_available_cells=d_available, integrity_counts=dict(sorted(counts.items())),
            reference_cells_frozen=summary['reference_cells_frozen'],
            legacy_opened_flag_means='D_available_not_prediction_materialized',
            new_distinct_prediction_cells_opened=0, new_D_computed=False,
            finite_row_intersection_used_to_recompute_D=False, missing_scores_imputed=False,
            models_refitted=False, heldout_opening_authorized=False, heldout_predictions_read=False,
            process_knockout_opened=False, metadata_member_sha256=metadata_members,
            prediction_member_sha256=prediction_members)
        output.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(output_rows).sort_values(keys).to_csv(output / 'surface_cells.csv', index=False)
        receipt['surface_cells_sha256'] = sha256((output / 'surface_cells.csv').read_bytes()).hexdigest()
        (output / 'surface_summary.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
        print(json.dumps({k:v for k,v in receipt.items() if not k.endswith('member_sha256')}, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference-zip', type=Path, required=True)
    p.add_argument('--bundle-zip', type=Path, required=True)
    p.add_argument('--analysis-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); audit(a.reference_zip, a.bundle_zip, a.analysis_root, a.output)

if __name__ == '__main__':
    main()
