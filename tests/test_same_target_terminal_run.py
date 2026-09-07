"""Terminal execution audit never substitutes unknown outcomes or opens D."""
import csv
import hashlib
import io
import itertools
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile
import json
from scripts.audit_same_target_terminal_run import (
    REPOSITORY, RUN_ID, EXECUTION_SHA, WORKFLOW_PATH, PREFIX,
    MODES, M_VALUES, PROCEDURES, MEMBERS, UNKNOWN,
    eligibility_bounds, index_terminal_source, summarize_terminal,
)


def fixture(present=45):
    run = {'id':RUN_ID, 'head_sha':EXECUTION_SHA, 'run_attempt':1, 'head_branch':'product-b-v5-obligate-invariant',
           'path':WORKFLOW_PATH, 'event':'push', 'status':'completed', 'conclusion':'cancelled',
           'repository':{'full_name':REPOSITORY}, 'head_repository':{'full_name':REPOSITORY},
           'updated_at':'2026-09-07T01:31:10Z'}
    jobs = [{'id':100+i, 'name':f'fit-taxa ({i})', 'run_id':RUN_ID, 'head_sha':EXECUTION_SHA, 'run_attempt':1,
             'status':'completed', 'conclusion':'success' if i<present else 'cancelled',
             'started_at':'2026-09-06T12:00:00Z','completed_at':'2026-09-06T17:30:00Z'} for i in range(47)]
    arts = [{'id':1+i, 'name':f'{PREFIX}{i}', 'expired':False, 'digest':'sha256:'+'a'*64,
             'workflow_run':{'id':RUN_ID,'head_sha':EXECUTION_SHA}} for i in range(present)]
    return run, {'total_count':47,'jobs':jobs}, {'total_count':present,'artifacts':arts}


class TerminalAuditTests(unittest.TestCase):
    def test_missing_answers_are_not_model_failures(self):
        jobs, arts = index_terminal_source(*fixture())
        self.assertEqual(len(jobs),47); self.assertEqual(len(arts),45)

    def test_missing_successful_job_artifact_rejected(self):
        r,j,a=fixture(); j['jobs'][-1]['conclusion']='success'
        with self.assertRaises(ValueError): index_terminal_source(r,j,a)

    def test_wrong_attempt_and_running_source_rejected(self):
        for k,v in [('run_attempt',2),('status','in_progress'),('head_sha','bad')]:
            r,j,a=fixture(); r[k]=v
            with self.subTest(k=k), self.assertRaises(ValueError): index_terminal_source(r,j,a)

    def test_incomplete_duplicate_and_foreign_artifacts_rejected(self):
        for mode in ('page','duplicate','foreign','expired'):
            r,j,a=fixture()
            if mode=='page': a['total_count']+=1
            if mode=='duplicate': a['artifacts'][-1]=a['artifacts'][0]
            if mode=='foreign': a['artifacts'][0]['workflow_run']['id']=1
            if mode=='expired': a['artifacts'][0]['expired']=True
            with self.subTest(mode=mode), self.assertRaises(ValueError): index_terminal_source(r,j,a)

    def test_bounds_at_27_28_30_do_not_authorize_anything(self):
        states=['floor_unreachable_even_if_missing_all_pass','missing_executions_can_change_floor_decision',
                'observed_floor_met_execution_still_blocked']
        for n,state in zip((27,28,30),states):
            d=eligibility_bounds(n,2)
            self.assertEqual(d['eligible_taxa_upper_bound'],n+2)
            self.assertEqual(d['bound_state'],state)
            self.assertFalse(d['prediction_opening_authorized'])

    def test_invalid_bound_counts_rejected(self):
        for args in [(-1,2),(46,2),(30.5,1),(True,1)]:
            with self.subTest(args=args), self.assertRaises(ValueError): eligibility_bounds(*args)

    def test_full_denominator_with_only_one_artifact_and_no_prediction_reads(self):
        r,j,a=fixture(present=1); names=[f'taxon-{i}' for i in range(47)]
        inv=[]; folds=[]
        for s,m,p in itertools.product(MODES,M_VALUES,PROCEDURES):
            row={'taxon':names[0],'source':s,'M_km':m,'procedure':p}
            inv.append({**row,'state':'successor_layer1_model_fit_sealed'})
            folds.extend({**row,'fold':f,'presence_rank':0.8} for f in range(4))
        def encoded(rows):
            f=io.StringIO(); w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader();w.writerows(rows);return f.getvalue()
        c={'result_version':'product_b_same_target_successor_layer1_fit_taxon_v0.1','taxon':names[0],
           'taxon_index':0,'expected_fit_cells':48,'sealed_fit_cells':48,'unresolved_fit_cells':0,
           'prediction_surfaces_sealed':True,'paired_discordance_computed':False,
           'process_knockout_computed':False,'reference_ceiling_read':False}
        adequacy={'outer_folds':4,'chance_auc':0.5,'minimum_auc_margin':0.01,'auc_sem_multiplier':1.0}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'1.zip'
            with ZipFile(path,'w') as z:
                z.writestr('contract.json',json.dumps(c)); z.writestr('fit_inventory.csv',encoded(inv))
                z.writestr('outer_cv_fold_metrics.csv',encoded(folds))
                z.writestr('sealed_prediction_surfaces.parquet',b'forbidden sentinel')
            a['artifacts'][0]['digest']='sha256:'+hashlib.sha256(path.read_bytes()).hexdigest()
            original=ZipFile.read; opened=[]
            def guarded(z,name,*args,**kwargs):
                self.assertIn(name,MEMBERS);opened.append(name);return original(z,name,*args,**kwargs)
            with patch.object(ZipFile,'read',guarded): result=summarize_terminal(r,j,a,names,adequacy,Path(tmp))
        self.assertEqual(result['source_cells_expected'],2256)
        self.assertEqual(result['source_cell_states_full_denominator'][UNKNOWN],46*48)
        self.assertEqual(result['pre_discordance_eligible_pairs'],24)
        self.assertEqual(result['execution_unknown_pair_cells'],46*24)
        self.assertFalse(result['postfit_authorized']);self.assertEqual(set(opened),set(MEMBERS))

    def test_workflow_is_read_only_and_does_not_call_calibration_or_fit(self):
        text=(Path(__file__).resolve().parents[1]/'.github/workflows/same_target_terminal_audit.yml').read_text()
        self.assertIn('contents: read',text);self.assertIn('actions: read',text)
        for forbidden in ('contents: write','rerun','calibrate_same_target','evaluate_same_target_heldout','git push'):
            self.assertNotIn(forbidden,text)


if __name__=='__main__': unittest.main()
