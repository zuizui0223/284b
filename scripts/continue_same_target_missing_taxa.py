#!/usr/bin/env python3
"""M-partition continuation of two timeout-censored taxa, not a rerun of 45 taxa.

Only two statements are injected into the exact original AST: select one M in
memory and fingerprint the prepared common frame. The fitting body is unchanged.
The inherited optimizer random_state=None is NOT a bitwise-replay guarantee.
"""
from __future__ import annotations
import argparse
import ast
import copy
from hashlib import sha1, sha256
import json
import os
from pathlib import Path
import subprocess
import sys

EXECUTION_SHA = '5d16212538d8b25d12235d2bb11b9a5e184a113b'
SCRIPT_BLOB = '504a99a33529dcb05e9838aece9bf84944fdc9e4'
SOURCE_RUN = 34032659571
MISSING = {8: 'Alisma plantago-aquatica', 35: 'Populus tremula'}
M_VALUES = (150, 300, 500)
PART_VERSION = 'product_b_same_target_successor_continuation_partition_v0.1'


def git_blob(data: bytes) -> str:
    return sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def select_m(contract: dict, m_km: int) -> dict:
    if contract.get('M_km') != list(M_VALUES) or m_km not in M_VALUES:
        raise ValueError('frozen M universe or requested partition changed')
    return {**contract, 'M_km': [m_km]}


def partition_ast(data: bytes, m_km: int, *, expected_blob: str = SCRIPT_BLOB) -> ast.Module:
    if git_blob(data) != expected_blob or m_km not in M_VALUES:
        raise ValueError('wrong original source or M partition')
    tree = ast.parse(data.decode('utf-8'))
    original = copy.deepcopy(tree)
    mains = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main']
    if len(mains) != 1:
        raise ValueError('expected exactly one original main')
    body = mains[0].body
    loads = [i for i, n in enumerate(body) if isinstance(n, ast.Assign)
             and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
             and n.targets[0].id == 'fit_contract']
    loops = [n for n in body if isinstance(n, ast.For)
             and isinstance(n.target, ast.Name) and n.target.id == 'm_km']
    if len(loads) != 1 or len(loops) != 1:
        raise ValueError('original main no longer has the audited structure')
    loop = loops[0]
    if ast.unparse(loop.iter) != "[int(v) for v in fit_contract['M_km']]":
        raise ValueError('original M loop changed')
    insertion = ast.parse(f'fit_contract = _continuation_select_m(fit_contract, {m_km})').body[0]
    capture = ast.parse('_continuation_capture(locals())').body[0]
    body.insert(loads[0] + 1, insertion)
    body.insert(body.index(loop), capture)
    # Mechanically prove every other AST node, including the entire fit body,
    # remains identical. Never edit the original source or contracts on disk.
    restored = copy.deepcopy(tree)
    rmain = next(n for n in restored.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    rmain.body = [n for n in rmain.body if ast.dump(n) not in {ast.dump(insertion), ast.dump(capture)}]
    if ast.dump(restored) != ast.dump(original):
        raise ValueError('partition changed code outside the two allowed statements')
    return ast.fix_missing_locations(tree)


def fingerprint_frame(scope: dict) -> dict:
    import pandas as pd
    def frame_digest(frame):
        h = sha256(json.dumps([(str(c), str(t)) for c, t in zip(frame.columns, frame.dtypes)]).encode())
        h.update(pd.util.hash_pandas_object(frame, index=True).values.tobytes())
        return h.hexdigest()
    return {
        'common_geometry': frame_digest(scope['common_geometry']),
        'centers': sha256(scope['centers'].tobytes()).hexdigest(),
        'featured_sources': {m: frame_digest(f) for m, f in scope['featured_source'].items()},
        'source_blocks': {m: sha256(b.tobytes()).hexdigest() for m, b in scope['source_blocks'].items()},
        'predictors': list(scope['predictors']), 'background_seed': int(scope['bg_seed']),
        'historical_keys': list(scope['historical_keys']),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--taxon-index', type=int, choices=sorted(MISSING), required=True)
    p.add_argument('--M-km', type=int, choices=M_VALUES, required=True)
    args = p.parse_args()
    if os.environ.get('GITHUB_RUN_ATTEMPT') != '1':
        raise RuntimeError('only the separately recorded first continuation attempt is allowed')
    root = args.source_root.resolve()
    head = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    if head != EXECUTION_SHA:
        raise RuntimeError('continuation must use the original source checkout')
    subprocess.run(['git', '-C', str(root), 'diff', '--exit-code', 'HEAD', '--'], check=True)
    script = root / 'scripts/run_same_target_successor_layer1_fit_taxon.py'
    data = script.read_bytes()
    tree = partition_ast(data, args.M_km)
    output = Path(os.environ['OUTPUT_DIR']).resolve()
    if output.exists():
        raise RuntimeError('refuse to overwrite an existing continuation partition')
    os.environ['TAXON_INDEX'] = str(args.taxon_index)
    captured = []
    def capture(scope):
        if scope['name'] != MISSING[args.taxon_index]:
            raise RuntimeError('frozen missing-taxon identity changed')
        captured.append(fingerprint_frame(scope))
    namespace = {'__name__': 'frozen_continuation_module', '__file__': str(script),
                 '_continuation_select_m': select_m, '_continuation_capture': capture}
    sys.path.insert(0, str(root))
    exec(compile(tree, str(script), 'exec'), namespace)
    if namespace['main']() != 0 or len(captured) != 1:
        raise RuntimeError('original partition execution failed')
    contract_path = output / 'contract.json'
    contract = json.loads(contract_path.read_text())
    if contract['expected_fit_cells'] != 16 or contract['M_km'] != [args.M_km]:
        raise RuntimeError('partition denominator changed')
    if contract['taxon'] != MISSING[args.taxon_index]:
        raise RuntimeError('partition taxon identity changed')
    contract.update(result_version=PART_VERSION,
        continuation={'original_source_run': SOURCE_RUN, 'original_execution_sha': EXECUTION_SHA,
            'original_runner_blob': SCRIPT_BLOB, 'original_attempt_successful': False,
            'controller_sha': os.environ['GITHUB_SHA'], 'continuation_run_id': int(os.environ['GITHUB_RUN_ID']),
            'continuation_attempt': 1, 'partition_M_km': args.M_km,
            'common_frame_fingerprint': captured[0], 'optimizer_random_state': None,
            'bitwise_replay_of_interrupted_attempt_claimed': False,
            'completed_original_taxa_refitted': False})
    contract_path.write_text(json.dumps(contract, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'taxon': contract['taxon'], 'M_km': args.M_km,
                     'sealed': contract['sealed_fit_cells'], 'unresolved': contract['unresolved_fit_cells']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
