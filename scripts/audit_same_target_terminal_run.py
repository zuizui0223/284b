#!/usr/bin/env python3
"""Read-only terminal-run audit; never authorize or compute paired predictions.

Retain all 47 scheduled taxa. Missing execution artifacts are unknown answers,
not model failures. Per-reference eligibility bounds show whether completing only
missing executions could meet the unchanged 30-taxon floor. This is diagnostic,
not a replacement for the frozen complete-run authorization.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import io
import itertools
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile

from scripts.audit_same_target_progress_receipt import (
    CATEGORIES, MEMBERS, MODES, M_VALUES, PROCEDURES, summarize_archive,
)
from product_b_v5.same_target_pairing import evaluate_prediction_adequacy
from scripts.verify_same_target_postfit_source import REPOSITORY, RUN_ID, EXECUTION_SHA, WORKFLOW_PATH

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'product-b-successor-layer1-fit-taxon-'
EXPECTED = set(range(47))
UNKNOWN = 'execution_artifact_missing'


def eligibility_bounds(eligible: int, missing: int, total: int = 47) -> dict:
    if any(type(x) is not int for x in (eligible, missing, total)) or min(eligible, missing) < 0 or eligible + missing > total:
        raise ValueError('invalid bounded counts')
    upper = eligible + missing
    return {'eligible_taxa_observed': eligible, 'execution_unknown_taxa': missing,
            'eligible_taxa_upper_bound': upper, 'minimum_required_taxa': 30,
            'bound_state': ('observed_floor_met_execution_still_blocked' if eligible >= 30 else
                            'floor_unreachable_even_if_missing_all_pass' if upper < 30 else
                            'missing_executions_can_change_floor_decision'),
            'prediction_opening_authorized': False}


def index_terminal_source(run: dict, jobs: dict, inventory: dict) -> tuple[dict, dict]:
    expected = {'id': RUN_ID, 'head_sha': EXECUTION_SHA, 'run_attempt': 1,
                'head_branch': 'product-b-v5-obligate-invariant', 'path': WORKFLOW_PATH, 'event': 'push'}
    for k, v in expected.items():
        if run.get(k) != v: raise ValueError(f'wrong frozen run: {k}')
    if any(run.get(k, {}).get('full_name') != REPOSITORY for k in ('repository', 'head_repository')):
        raise ValueError('wrong repository')
    if run.get('status') != 'completed' or run.get('conclusion') not in ('cancelled', 'failure', 'timed_out'):
        raise ValueError('this diagnostic requires a terminal unsuccessful source')
    for payload, key in ((jobs, 'jobs'), (inventory, 'artifacts')):
        if payload.get('total_count') != len(payload.get(key, [])):
            raise ValueError('paginated or incomplete metadata')
    indexed_jobs = {}
    for job in jobs['jobs']:
        match = re.fullmatch(r'fit-taxa \((\d+)\)', job['name'])
        if match:
            i = int(match[1])
            if i in indexed_jobs or i not in EXPECTED: raise ValueError('duplicate or unexpected taxon job')
            if job.get('run_id') != RUN_ID or job.get('head_sha') != EXECUTION_SHA or job.get('run_attempt') != 1:
                raise ValueError('job provenance mismatch')
            if job.get('status') != 'completed': raise ValueError('job not terminal')
            indexed_jobs[i] = job
    if set(indexed_jobs) != EXPECTED: raise ValueError('missing expected taxon job')
    artifacts = {}; ids = set()
    for a in inventory['artifacts']:
        match = re.fullmatch(re.escape(PREFIX) + r'(\d+)', a['name'])
        if not match: raise ValueError('unexpected artifact in terminal source')
        i = int(match[1])
        if i not in EXPECTED or i in artifacts or a['id'] in ids: raise ValueError('duplicate or unknown artifact')
        if a.get('expired') is not False or not re.fullmatch(r'sha256:[0-9a-f]{64}', a.get('digest', '')):
            raise ValueError('expired artifact or invalid digest')
        origin = a.get('workflow_run', {})
        if origin.get('id') != RUN_ID or origin.get('head_sha') != EXECUTION_SHA:
            raise ValueError('artifact execution mismatch')
        if indexed_jobs[i].get('conclusion') != 'success': raise ValueError('artifact/job status mismatch')
        artifacts[i] = a; ids.add(a['id'])
    for i in EXPECTED - set(artifacts):
        if indexed_jobs[i].get('conclusion') not in ('cancelled', 'failure', 'timed_out'):
            raise ValueError('missing artifact not explained by failed execution')
    return indexed_jobs, artifacts


def decoded_states(raw: dict, adequacy: dict) -> dict:
    inv = list(csv.DictReader(io.StringIO(raw['fit_inventory.csv'].decode())))
    folds = list(csv.DictReader(io.StringIO(raw['outer_cv_fold_metrics.csv'].decode())))
    key = lambda r: (r['source'], int(r['M_km']), r['procedure'])
    grouped = defaultdict(list)
    for row in folds: grouped[key(row)].append(row)
    states = {}
    for row in inv:
        k = key(row); evidence = grouped[k]
        if row['state'] == 'successor_layer1_model_fit_unresolved': state = 'final_fit_unresolved'
        elif len(evidence) != adequacy['outer_folds']: state = 'outer_fold_rows_incomplete'
        else:
            values = [float(r['presence_rank']) if r['presence_rank'] else float('nan') for r in evidence]
            qa = evaluate_prediction_adequacy(values, expected_folds=adequacy['outer_folds'],
                chance_auc=adequacy['chance_auc'], minimum_auc_margin=adequacy['minimum_auc_margin'],
                auc_sem_multiplier=adequacy['auc_sem_multiplier'])
            state = ('validation_metric_nonfinite' if not qa.evidence_complete else
                     'answer_adequate' if qa.adequate else 'prediction_performance_below_floor')
        states[k] = state
    return states


def summarize_terminal(run: dict, jobs: dict, inventory: dict, names: list[str], adequacy: dict, archive_dir: Path) -> dict:
    indexed_jobs, artifacts = index_terminal_source(run, jobs, inventory)
    if len(names) != 47 or len(set(names)) != 47: raise ValueError('sampling-pass panel mismatch')
    if adequacy != {'outer_folds': 4, 'chance_auc': 0.5, 'minimum_auc_margin': 0.01, 'auc_sem_multiplier': 1.0}:
        raise ValueError('frozen adequacy rule changed')
    all_states = {}; summaries = []; receipts = []; missing_jobs = []
    for i, name in enumerate(names):
        if i not in artifacts:
            for key in itertools.product(MODES, M_VALUES, PROCEDURES): all_states[(i, *key)] = UNKNOWN
            job = indexed_jobs[i]
            elapsed = (datetime.fromisoformat(job['completed_at'].replace('Z', '+00:00')) -
                       datetime.fromisoformat(job['started_at'].replace('Z', '+00:00'))).total_seconds()
            missing_jobs.append({'taxon_index': i, 'taxon': name, 'job_id': job['id'],
                'conclusion': job['conclusion'], 'started_at': job['started_at'], 'completed_at': job['completed_at'],
                'elapsed_minutes': elapsed / 60, 'source_answer_state': UNKNOWN,
                'biological_or_model_failure_inferred': False})
            continue
        a = artifacts[i]; path = archive_dir / f'{a["id"]}.zip'
        receipt = {'artifact_id': a['id'], 'taxon_index': i, 'taxon': name,
                   'archive_sha256': a['digest'].removeprefix('sha256:'), 'archive_filename': path.name}
        summary = summarize_archive(path, receipt, adequacy)
        with ZipFile(path) as z: raw = {n: z.read(n) for n in MEMBERS}
        states = decoded_states(raw, adequacy)
        if {c: sum(s == c for s in states.values()) for c in CATEGORIES} != summary['source_cell_states']:
            raise ValueError('independent per-cell audit disagrees with existing receipt helper')
        all_states.update({(i, *key): state for key, state in states.items()})
        summaries.append(summary); receipts.append(receipt)
    missing = len(missing_jobs)
    references = []
    for m, p in itertools.product(M_VALUES, PROCEDURES):
        n = sum(all(all_states[(i, s, m, p)] == 'answer_adequate' for s in MODES) for i in EXPECTED)
        references.append({'M_km': m, 'procedure': p, **eligibility_bounds(n, missing)})
    source_states = dict(Counter(all_states.values()))
    eligible_pairs = sum(r['eligible_taxa_observed'] for r in references)
    missing_pairs = missing * 24
    return {'result_version': 'product_b_same_target_successor_terminal_audit_v0.1',
        'source_run_id': RUN_ID, 'source_execution_sha': EXECUTION_SHA,
        'source_conclusion': run['conclusion'], 'source_updated_at': run['updated_at'],
        'expected_taxa': 47, 'completed_artifact_taxa': len(artifacts), 'execution_unknown_taxa': missing,
        'source_cells_expected': 2256, 'source_cells_audited_from_artifacts': len(artifacts)*48,
        'source_cell_states_full_denominator': source_states,
        'source_cells_sealed': sum(r['sealed_source_cells'] for r in summaries),
        'pair_cells_expected': 1128, 'pre_discordance_eligible_pairs': eligible_pairs,
        'known_pre_discordance_ineligible_pairs': len(artifacts)*24 - eligible_pairs,
        'execution_unknown_pair_cells': missing_pairs,
        'pre_discordance_eligible_pairs_upper_bound': eligible_pairs+missing_pairs,
        'reference_bounds': references, 'reference_bound_states': dict(Counter(r['bound_state'] for r in references)),
        'all_24_eligible_taxa': [r['taxon'] for r in summaries if r['pre_discordance_eligible_pairs'] == 24],
        'missing_executions': missing_jobs, 'artifacts': receipts, 'taxa': summaries,
        'frozen_prediction_adequacy': adequacy, 'decoded_archive_members': list(MEMBERS),
        'prediction_members_decoded': [], 'paired_discordance_computed': False,
        'reference_ceiling_computed': False, 'heldout_prediction_opened': False,
        'process_knockout_opened': False, 'postfit_authorized': False,
        'fitting_restarted': False, 'scientific_rules_changed': False,
        'claim_strength': 'terminal_execution_and_pre_discordance_eligibility_bounds_not_biological_agreement'}


def gh_json(endpoint: str) -> dict:
    return json.loads(subprocess.check_output(['gh', 'api', endpoint], text=True))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--archive-dir', type=Path, required=True)
    args = p.parse_args(); out = args.output_dir; out.mkdir(parents=True, exist_ok=True)
    args.archive_dir.mkdir(parents=True, exist_ok=True)
    run = gh_json(f'repos/{REPOSITORY}/actions/runs/{RUN_ID}')
    jobs = gh_json(f'repos/{REPOSITORY}/actions/runs/{RUN_ID}/jobs?per_page=100')
    inventory = gh_json(f'repos/{REPOSITORY}/actions/runs/{RUN_ID}/artifacts?per_page=100')
    _, indexed = index_terminal_source(run, jobs, inventory)
    for name, payload in [('source_run', run), ('source_jobs', jobs), ('source_artifacts', inventory)]:
        (out/f'{name}.json').write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n')
    sampling_path = ROOT/'results/product_b_same_target_successor_source_mode_sampling_v0_1.json'
    fit_path = ROOT/'config/product_b_same_target_source_model_fit_contract_v0_1.json'
    sampling = json.loads(sampling_path.read_text())
    names = [r['requested_name'] for r in sampling['results'] if r['state'] == 'successor_source_mode_sampling_passed']
    frozen = json.loads(fit_path.read_text())['prediction_adequacy']
    adequacy = {k: frozen[k] for k in ('outer_folds','chance_auc','minimum_auc_margin','auc_sem_multiplier')}
    for a in indexed.values():
        path = args.archive_dir/f'{a["id"]}.zip'
        if not path.exists():
            with path.open('wb') as f:
                subprocess.run(['gh','api',f'repos/{REPOSITORY}/actions/artifacts/{a["id"]}/zip'], stdout=f, check=True)
        if hashlib.sha256(path.read_bytes()).hexdigest() != a['digest'].removeprefix('sha256:'):
            raise ValueError('downloaded archive digest mismatch')
    summary = summarize_terminal(run, jobs, inventory, names, adequacy, args.archive_dir)
    summary['audit_implementation_sha'] = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    summary['input_file_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (sampling_path,fit_path)}
    annotations = {}
    for missing in summary['missing_executions']:
        annotations[str(missing['job_id'])] = gh_json(f'repos/{REPOSITORY}/check-runs/{missing["job_id"]}/annotations')
    (out/'cancellation_annotations.json').write_text(json.dumps(annotations,indent=2,sort_keys=True)+'\n')
    (out/'product_b_same_target_successor_terminal_audit_v0_1.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    with (out/'product_b_same_target_successor_terminal_reference_bounds_v0_1.csv').open('w',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=list(summary['reference_bounds'][0])); writer.writeheader(); writer.writerows(summary['reference_bounds'])
    print(json.dumps({k:v for k,v in summary.items() if k not in ('artifacts','taxa')},indent=2,sort_keys=True))
    return 0


if __name__ == '__main__': raise SystemExit(main())
