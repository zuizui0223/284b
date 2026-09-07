"""Continuation partitioning/provenance tests; no empirical paired scores."""
import ast
import copy
import importlib.util
import itertools
import json
from pathlib import Path
import tempfile
import unittest

from scripts.continue_same_target_missing_taxa import (
    partition_ast, select_m, git_blob, EXECUTION_SHA, SOURCE_RUN, MISSING,
    M_VALUES, PART_VERSION, SCRIPT_BLOB,
)
from scripts.assemble_same_target_continuation import (
    verify_gate, assemble_taxon, PREFIX, MODES, PROCEDURES, REPO,
)


def metadata():
    run = {'id': SOURCE_RUN, 'head_sha': EXECUTION_SHA, 'run_attempt': 1,
           'status': 'completed', 'conclusion': 'cancelled', 'event': 'push',
           'path': '.github/workflows/same_target_successor_layer1_fit.yml',
           'head_branch': 'product-b-v5-obligate-invariant',
           'repository': {'full_name': REPO}, 'head_repository': {'full_name': REPO}}
    inv = {'total_count': 45, 'artifacts': [
        {'id': i+1, 'name': f'{PREFIX}{i}', 'expired': False, 'digest': 'sha256:'+'a'*64,
         'workflow_run': {'id': SOURCE_RUN, 'head_sha': EXECUTION_SHA}}
        for i in range(47) if i not in MISSING]}
    return run, inv


def parts(root, *, empty_first=False):
    from hashlib import sha256
    import csv
    result = []
    for m in M_VALUES:
        p = root / str(m); p.mkdir()
        sealed = 0 if (empty_first and m == 150) else 16
        c = {'result_version': PART_VERSION, 'taxon_index': 8, 'taxon': MISSING[8],
             'M_km': [m], 'expected_fit_cells': 16, 'procedure_count': 8, 'source_modes': list(MODES),
             'sealed_fit_cells': sealed, 'unresolved_fit_cells': 16-sealed,
             'errors': [{'M_km': m} for _ in range(16-sealed)], 'historical_specieskeys': ['123'],
             'prediction_surfaces_sealed': True,
             'continuation': {'original_execution_sha': EXECUTION_SHA, 'original_source_run': SOURCE_RUN,
                              'controller_sha': 'controller', 'continuation_run_id': 42, 'continuation_attempt': 1,
                              'partition_M_km': m, 'common_frame_fingerprint': {'fixture': 'same'}}}
        for k in ('paired_discordance_computed', 'process_knockout_computed', 'reference_ceiling_read',
                  'raw_occurrence_rows_persisted', 'occurrence_coordinates_persisted'):
            c[k] = False
        blob = b'opaque sealed bytes not decoded ' + str(m).encode()
        (p/'sealed_prediction_surfaces.parquet').write_bytes(blob)
        c['prediction_surface_sha256'] = sha256(blob).hexdigest()
        (p/'contract.json').write_text(json.dumps(c))
        with (p/'fit_inventory.csv').open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['taxon','source','M_km','procedure','state']); w.writeheader()
            for s, pr in itertools.product(MODES, PROCEDURES):
                w.writerow({'taxon': MISSING[8], 'source': s, 'M_km': m, 'procedure': pr,
                            'state': 'successor_layer1_model_fit_sealed' if sealed else 'successor_layer1_model_fit_unresolved'})
        (p/'outer_cv_fold_metrics.csv').write_text('')
        result.append(p)
    return result


class ContinuationTests(unittest.TestCase):
    def test_gate_only_exact_45_and_two_missing(self):
        run, inv = metadata()
        out = verify_gate(run, inv, copy.deepcopy(inv))
        self.assertEqual(len(out['tasks']), 6)
        self.assertFalse(out['original_45_refit_authorized'])
        self.assertFalse(out['paired_prediction_opening_authorized'])
        for mutate in ('rerun', 'changed_artifact', 'wrong_missing'):
            r, i = metadata(); frozen = copy.deepcopy(i)
            if mutate == 'rerun': r['run_attempt'] = 2
            if mutate == 'changed_artifact': i['artifacts'][0]['digest'] = 'sha256:'+'b'*64
            if mutate == 'wrong_missing': i['artifacts'][0]['name'] = PREFIX+'8'
            with self.subTest(mutate=mutate), self.assertRaises(ValueError): verify_gate(r, i, frozen)

    def test_selector_keeps_original_contract_unchanged(self):
        c = {'M_km': list(M_VALUES), 'procedure_library': {'frozen': True}}
        self.assertEqual(select_m(c, 300)['M_km'], [300])
        self.assertEqual(c['M_km'], list(M_VALUES))
        with self.assertRaises(ValueError): select_m(c, 400)

    def test_actual_original_runner_ast_is_pinned(self):
        path = Path(__file__).resolve().parents[1]/'scripts/run_same_target_successor_layer1_fit_taxon.py'
        if not path.exists(): self.skipTest('actual source verified by repository CI')
        data = path.read_bytes()
        self.assertEqual(git_blob(data), SCRIPT_BLOB)
        for m in M_VALUES: compile(partition_ast(data, m), str(path), 'exec')
        with self.assertRaises(ValueError): partition_ast(data+b'\n', 150)

    def test_partitioned_calls_equal_monolithic_calls_on_instrumented_fixture(self):
        data = b'''def main():
    fit_contract = {'M_km': [150, 300, 500]}
    calls = []
    for m_km in [int(v) for v in fit_contract["M_km"]]:
        for source in ("P", "H"):
            for procedure in range(8):
                calls.append((m_km, source, procedure))
    return calls
'''
        original = {}; exec(data, original)
        all_calls = []
        for m in M_VALUES:
            ns = {'_continuation_select_m': select_m, '_continuation_capture': lambda scope: None}
            exec(compile(partition_ast(data, m, expected_blob=git_blob(data)), '<fixture>', 'exec'), ns)
            all_calls += ns['main']()
        self.assertEqual(all_calls, original['main']())
        self.assertEqual(len(all_calls), 48)

    def test_opaque_assembly_retains_all_48_and_censored_history(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); inputs = parts(root); out = root/'merged'
            c = assemble_taxon(inputs, out, 8, 'controller', 42)
            self.assertEqual(c['expected_fit_cells'], 48)
            self.assertEqual(c['sealed_fit_cells'], 48)
            self.assertEqual(len(list((out/'sealed_prediction_surfaces.parquet').iterdir())), 3)
            self.assertFalse(c['continuation']['predictions_decoded_for_assembly'])
            with self.assertRaises(ValueError): assemble_taxon(inputs, out, 8, 'controller', 42)

    def test_assembly_rejects_missing_drift_and_different_attempt(self):
        for mode in ('missing','geometry','provenance','checksum','duplicate_inventory'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as d:
                root=Path(d); inputs=parts(root)
                if mode == 'missing': inputs.pop()
                elif mode == 'checksum': (inputs[0]/'sealed_prediction_surfaces.parquet').write_bytes(b'changed')
                elif mode == 'duplicate_inventory':
                    f=inputs[0]/'fit_inventory.csv'; lines=f.read_text().splitlines(); lines[-1]=lines[1]; f.write_text('\n'.join(lines)+'\n')
                else:
                    f=inputs[0]/'contract.json'; c=json.loads(f.read_text())
                    if mode == 'geometry': c['continuation']['common_frame_fingerprint']={'fixture':'changed'}
                    else: c['continuation']['continuation_run_id']=43
                    f.write_text(json.dumps(c))
                with self.assertRaises(ValueError): assemble_taxon(inputs, root/'merged', 8, 'controller', 42)

    @unittest.skipUnless(importlib.util.find_spec('pyarrow'), 'Arrow dataset compatibility runs in CI')
    def test_existing_reader_accepts_opaque_dataset_including_empty_partition(self):
        import pandas as pd
        from hashlib import sha256
        from product_b_v5.prediction_opening import read_authorized_prediction_cells
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); inputs=parts(root, empty_first=True)
            for p in inputs:
                m=int(p.name)
                frame = pd.DataFrame() if m == 150 else pd.DataFrame([
                    {'taxon':MISSING[8], 'source':s, 'M_km':m, 'procedure':PROCEDURES[0],
                     'comparison_row_id':'one', 'ecological_score':0.5}
                    for s in MODES])
                path=p/'sealed_prediction_surfaces.parquet'; frame.to_parquet(path,index=False)
                c=json.loads((p/'contract.json').read_text()); c['prediction_surface_sha256']=sha256(path.read_bytes()).hexdigest()
                (p/'contract.json').write_text(json.dumps(c))
            out=root/'merged'; assemble_taxon(inputs,out,8,'controller',42)
            frame=read_authorized_prediction_cells(out/'sealed_prediction_surfaces.parquet',{(300,PROCEDURES[0])})
            self.assertEqual(len(frame),2)
            self.assertEqual(set(frame.M_km),{300})


if __name__ == '__main__': unittest.main()
