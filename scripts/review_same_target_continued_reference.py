#!/usr/bin/env python3
"""Review reference outputs, including valid-but-unavailable terminal references.

Opening authorization is permission to inspect a vector, not a promise that it
has finite support or yields D. This review never authorizes held-out opening.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from math import ceil, isfinite
from pathlib import Path
import pandas as pd

EXPECTED_RESTORED = {'Alisma plantago-aquatica', 'Populus tremula'}


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _require_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise RuntimeError(f'{path.name} is not a JSON object')
    return data


def _boolean(value) -> bool:
    if str(value) not in ('True', 'False'):
        raise RuntimeError('invalid boolean in reference evidence')
    return str(value) == 'True'


def _expect(data, values, label):
    for key, value in values.items():
        if data.get(key) != value:
            raise RuntimeError(f'{label}: {key} changed')


def review(continuation_path: Path, fit_audit_path: Path, feasibility_path: Path,
           reference_path: Path, summary_path: Path, pairing_cells_path: Path | None = None) -> dict:
    continuation = _require_json(continuation_path)
    fit = _require_json(fit_audit_path)
    feasibility = _require_json(feasibility_path)
    summary = _require_json(summary_path)
    reference = pd.read_csv(reference_path)
    _expect(continuation, dict(completed_taxa=47, original_artifact_taxa_retained=45,
        original_run_relabelled_success=False, heldout_opening_authorized=False,
        predictions_decoded_for_assembly=False), 'continuation')
    if set(continuation.get('restored_taxa', [])) != EXPECTED_RESTORED:
        raise RuntimeError('continued taxa differ from the two timeout-censored taxa')
    _expect(fit, dict(taxa_expected_from_sampling_pass=47, taxa_with_prediction_artifacts=47,
        expected_fit_cells=2256, paired_discordance_opened=False,
        reference_ceiling_opened=False, process_knockout_opened=False), 'fit audit')
    _expect(feasibility, dict(result_version='product_b_same_target_successor_reference_feasibility_v0.1',
        sampling_pass_taxa=47, candidate_pair_cells=1128, reference_cells_expected=24,
        minimum_eligible_taxa_per_procedure_M=30, paired_prediction_surfaces_read=False,
        schoener_d_computed=False, reference_ceiling_computed=False,
        heldout_12_paired_discordance_read=False, process_knockout_opened=False), 'feasibility')
    gates = {(int(r['M_km']), str(r['procedure'])): r for r in feasibility.get('reference_cells', [])}
    if len(gates) != 24 or len(feasibility['reference_cells']) != 24:
        raise RuntimeError('feasibility must have 24 unique reference cells')
    required = {'M_km','procedure','pre_discordance_eligible_taxa','pre_discordance_opening_authorized',
        'authorized_distinct_calibration_taxa','minimum_required_taxa','quantile','quantile_method',
        'nearest_rank_index_1_based','one_minus_schoener_d_reference_ceiling','reference_state'}
    if len(reference) != 24 or required - set(reference.columns):
        raise RuntimeError('reference table shape changed')
    seen = set(); frozen = 0; post_support_unresolved = 0
    for row in reference.to_dict('records'):
        key = (int(row['M_km']), str(row['procedure']))
        if key not in gates or key in seen:
            raise RuntimeError('reference key duplicate or outside feasibility matrix')
        seen.add(key); gate = gates[key]
        pre_n = int(row['pre_discordance_eligible_taxa'])
        n = int(row['authorized_distinct_calibration_taxa'])
        allowed = _boolean(row['pre_discordance_opening_authorized'])
        if pre_n != int(gate['eligible_distinct_taxa_pre_discordance']) or not 0 <= n <= pre_n <= 47:
            raise RuntimeError('calibration pre-D count differs from sealed feasibility')
        if allowed != _boolean(gate['discordance_opening_authorized']) or allowed != (pre_n >= 30):
            raise RuntimeError('calibration authorization differs from frozen 30-taxon floor')
        if int(row['minimum_required_taxa']) != 30 or float(row['quantile']) != 0.95 or row['quantile_method'] != 'nearest_rank':
            raise RuntimeError('reference quantile rule changed')
        state = row['reference_state']; ceiling = row['one_minus_schoener_d_reference_ceiling']
        rank = row['nearest_rank_index_1_based']
        if state == 'reference_ceiling_frozen':
            if not allowed or n < 30 or pd.isna(ceiling) or not isfinite(float(ceiling)) or not 0 <= float(ceiling) <= 1:
                raise RuntimeError('invalid or unauthorized frozen reference')
            if pd.isna(rank) or float(rank) != ceil(0.95 * n):
                raise RuntimeError('incorrect nearest-rank index')
            frozen += 1
        else:
            if state not in ('reference_ceiling_unresolved', 'paired_crosscheck_calibration_unresolved'):
                raise RuntimeError('unknown reference state')
            # Pre-D adequate taxa can lose D availability at the frozen surface
            # integrity check. Retain that terminal state without inventing q95.
            if n >= 30 or not pd.isna(ceiling) or not pd.isna(rank) or (not allowed and n != 0):
                raise RuntimeError('unresolved reference carries unjustified evidence')
            post_support_unresolved += int(allowed)
    _expect(summary, dict(result_version='product_b_same_target_successor_pairing_calibration_v0.2_strict_opening',
        sampling_pass_taxa_in_audit=47, paired_cells_expected=1128, reference_cells_expected=24,
        minimum_distinct_calibration_taxa_per_reference_cell=30, reference_quantile=0.95,
        quantile_method='nearest_rank', reference_cells_frozen=frozen, reference_cells_unresolved=24-frozen,
        current_12_taxon_paired_discordance_read=False, process_knockout_opened=False,
        successor_consistent_labels_emitted=0, successor_attention_required_labels_emitted=0,
        unauthorized_prediction_cells_materialized=0), 'calibration')
    paths = [continuation_path, fit_audit_path, feasibility_path, reference_path, summary_path]
    accounting = {}
    if pairing_cells_path is not None:
        cells = pd.read_csv(pairing_cells_path)
        keys = ['taxon', 'M_km', 'procedure']
        if len(cells) != 1128 or cells.duplicated(keys).any() or cells['taxon'].nunique() != 47:
            raise RuntimeError('pair inventory changed')
        auth = cells['prediction_materialization_authorized'].map(_boolean)
        observed = cells['paired_prediction_surface_opened'].map(_boolean)
        if (observed & ~auth).any():
            raise RuntimeError('unauthorized D availability')
        for row in reference.to_dict('records'):
            g = cells[(cells['M_km'] == row['M_km']) & (cells['procedure'] == row['procedure'])]
            if len(g) != 47 or int(g['paired_prediction_surface_opened'].map(_boolean).sum()) != int(row['authorized_distinct_calibration_taxa']):
                raise RuntimeError('pair contributions disagree with reference table')
        if summary['paired_surfaces_opened_authorized_cells'] != int(observed.sum()) or summary['paired_surfaces_kept_closed_cells'] != int((~observed).sum()):
            raise RuntimeError('legacy D-availability accounting disagrees')
        accounting = dict(prediction_materialization_authorized_cells=int(auth.sum()),
            d_available_cells=int(observed.sum()),
            legacy_opened_flag_is_D_availability_not_read_status=True)
        paths.append(pairing_cells_path)
    return dict(result_version='product_b_same_target_continued_reference_review_v0.2',
        continued_taxa_complete=47, original_taxa_retained=45, restored_taxa=sorted(EXPECTED_RESTORED),
        reference_cells_expected=24, reference_cells_frozen=frozen, reference_cells_unresolved=24-frozen,
        authorized_but_reference_unavailable_cells=post_support_unresolved,
        review_state='reference_available_for_separate_review' if frozen else 'reference_unavailable',
        minimum_reference_taxa=30, reference_quantile=0.95, quantile_method='nearest_rank',
        heldout_opening_authorized=False, heldout_prediction_opened=False, heldout_crosscheck_opened=False,
        process_knockout_opened=False, input_sha256={p.name: _hash(p) for p in paths}, **accounting)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('continuation', 'fit-audit', 'feasibility', 'reference', 'summary', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--pairing-cells', type=Path)
    a = p.parse_args()
    result = review(a.continuation, a.fit_audit, a.feasibility, a.reference, a.summary, a.pairing_cells)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
