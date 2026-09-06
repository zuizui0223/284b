#!/usr/bin/env python3
"""Check the fixed Actions source before running already-frozen post-fit stages.

Transport/execution checks only. No fitted values, thresholds or biological
answers are inspected here. A running source is not a scientific failure.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

REPOSITORY = 'zuizui0223/284b'
RUN_ID = 34032659571
EXECUTION_SHA = '5d16212538d8b25d12235d2bb11b9a5e184a113b'
ANALYSIS_SHA = '89f1a01386d5906420cb625dbf87ee18d60672e5'
WORKFLOW_PATH = '.github/workflows/same_target_successor_layer1_fit.yml'
PREFIX = 'product-b-successor-layer1-fit-taxon-'


def verify_source(run: dict, inventory: dict) -> dict:
    expected = {'id': RUN_ID, 'head_sha': EXECUTION_SHA,
                'head_branch': 'product-b-v5-obligate-invariant',
                'path': WORKFLOW_PATH, 'event': 'push'}
    for key, value in expected.items():
        if run.get(key) != value:
            raise ValueError(f'wrong frozen source: {key}')
    for key in ('repository', 'head_repository'):
        if run.get(key, {}).get('full_name') != REPOSITORY:
            raise ValueError(f'wrong source repository: {key}')
    if run.get('run_attempt') != 1:
        raise ValueError('source execution attempt differs from frozen first attempt')
    result = {'source_run_id': RUN_ID, 'source_execution_sha': EXECUTION_SHA,
              'analysis_sha': ANALYSIS_SHA, 'postfit_authorized': False,
              'expected_taxon_artifacts': 47, 'heldout_opening_authorized': False,
              'source_status': run.get('status'), 'source_conclusion': run.get('conclusion')}
    if run.get('status') != 'completed':
        return {**result, 'state': 'source_run_not_complete'}
    if run.get('conclusion') != 'success':
        return {**result, 'state': 'source_run_not_successful'}
    artifacts = inventory.get('artifacts', [])
    if inventory.get('total_count') != len(artifacts):
        raise ValueError('artifact inventory is paginated or incomplete')
    required = {f'{PREFIX}{i}' for i in range(47)} | {'product-b-successor-layer1-fit-audit'}
    if len(artifacts) != len(required) or {a.get('name') for a in artifacts} != required:
        raise ValueError('not exactly all 47 taxon artifacts plus the aggregate')
    if len({a.get('id') for a in artifacts}) != len(artifacts):
        raise ValueError('duplicate artifact identity')
    for artifact in artifacts:
        if artifact.get('expired') is not False:
            raise ValueError('expired artifact')
        if not re.fullmatch(r'sha256:[0-9a-f]{64}', str(artifact.get('digest', ''))):
            raise ValueError('artifact lacks a SHA256 digest')
        source = artifact.get('workflow_run', {})
        if source.get('id') != RUN_ID or source.get('head_sha') != EXECUTION_SHA:
            raise ValueError('artifact belongs to another execution')
    return {**result, 'state': 'fixed_full_run_postfit_authorized',
            'postfit_authorized': True, 'taxon_artifacts_present': 47,
            'artifact_digests': {a['name']: a['digest'] for a in artifacts}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--artifacts', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    receipt = verify_source(json.loads(args.run.read_text()), json.loads(args.artifacts.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
