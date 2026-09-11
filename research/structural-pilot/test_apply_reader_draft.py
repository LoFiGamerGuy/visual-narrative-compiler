"""Meaningful validation tests against the actual selected CF reader sources."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import apply_reader_draft as app


class DraftApplicationTests(unittest.TestCase):
    def setUp(self):
        self.input = app.NAMESPACE/'reader-patches/CF-reader-input.json'
        self.input_bytes = self.input.read_bytes()
        self.spec = json.loads(self.input_bytes)
        bundle = json.loads((app.ROOT/'docs/research/structural-pilot/correction-reader/routes.json').read_text())
        data = bundle['datasets']['CF']
        self.draft = {'schema':'SequenceReviewDraft/1','title':data['title'],'plan_sha256':data['plan_sha256'],'exported_at':'validation-fixture','status':'draft-unaccepted','experiment_id':self.spec['experiment_id'],'route_id':'CF','reader_input_sha256':app.digest(self.input_bytes),'reviewer_labels_verified':False,'panels':[{'id':p['id'],'candidate_id':p['candidate']['id'],'candidate_sha256':p['candidate']['sha256'],'lettering':copy.deepcopy(p['lettering']),'protected_regions':copy.deepcopy(p['protected_regions']),'observations':[]} for p in data['panels']]}
        self.temp = tempfile.TemporaryDirectory(prefix='.draft-validation-', dir=app.NAMESPACE)
        self.path = Path(self.temp.name)/'draft.json'

    def tearDown(self):
        self.assertEqual(self.input_bytes, self.input.read_bytes())
        self.temp.cleanup()

    def prepare(self, value=None):
        self.path.write_text(json.dumps(self.draft if value is None else value))
        return app.prepare(self.path,self.input,True)

    def test_concrete_patch_preserves_context_and_notes(self):
        self.draft['panels'][10]['lettering'][0]['x'] += .01
        self.draft['panels'][10]['observations'] = [{'text':'Unverified visual note','reviewer':'Self-described reader','reviewer_kind':'human','flag':'note','source_checks':False}]
        patch, before, draft, after = self.prepare()
        self.assertEqual([p['panel'] for p in patch['changes']], ['P11'])
        self.assertEqual(patch['browser_notes_preserved_only'], 1)
        result = json.loads(after)
        self.assertNotIn('observations', result['routes'][1]['panels']['P11'])
        self.assertFalse(patch['production_eligible'])

    def test_reject_candidate_tamper_all_fourteen(self):
        for i in range(14):
            with self.subTest(panel=i+1):
                bad=copy.deepcopy(self.draft);bad['panels'][i]['candidate_sha256']='0'*64
                with self.assertRaisesRegex(ValueError,'candidate ID/hash'):
                    self.prepare(bad)

    def test_reject_stale_input_plan_route_and_experiment(self):
        for key,value in [('reader_input_sha256','0'*64),('plan_sha256','0'*64),('route_id','B'),('experiment_id','older-experiment')]:
            with self.subTest(field=key):
                bad=copy.deepcopy(self.draft);bad[key]=value
                with self.assertRaises(ValueError):self.prepare(bad)

    def test_reject_copy_drift_and_context_change(self):
        bad=copy.deepcopy(self.draft);bad['panels'][10]['lettering'][0]['text']='AIR BRAKE · PULSE 2 → 0'
        with self.assertRaisesRegex(ValueError,'canonical transcript'):self.prepare(bad)
        bad=copy.deepcopy(self.draft);bad['panels'][0]['lettering'][0]['x']+=.01
        with self.assertRaisesRegex(ValueError,'context layout is protected'):self.prepare(bad)

    def test_reject_nonfinite_bounds_low_fonts_and_acceptance(self):
        for key,value in [('x',float('nan')),('x',float('inf')),('x',1),('w',0),('font_size',11.9),('font_size',True)]:
            bad=copy.deepcopy(self.draft);bad['panels'][10]['lettering'][0][key]=value
            with self.subTest(field=key,value=value):
                with self.assertRaises(ValueError):self.prepare(bad)
        for key,value in [('production_eligible',True),('reviewer_labels_verified',True),('status','approved'),('owner_acceptance',True)]:
            bad=copy.deepcopy(self.draft);bad[key]=value
            with self.subTest(field=key):
                with self.assertRaises(ValueError):self.prepare(bad)

    def test_reference_p14_lettering_only(self):
        bad=copy.deepcopy(self.draft);bad['panels'][13]['protected_regions'][0]['label']='Changed annotation'
        with self.assertRaisesRegex(ValueError,'only lettering may change'):self.prepare(bad)

    def test_rejected_apply_does_not_mutate_or_create_history(self):
        history=app.NAMESPACE/'layout-history'
        existing=set(history.iterdir()) if history.exists() else set()
        self.draft['panels'][13]['candidate_id']='tampered'
        self.path.write_text(json.dumps(self.draft))
        with self.assertRaises(ValueError):app.apply(self.path,self.input,True)
        self.assertEqual(existing,set(history.iterdir()) if history.exists() else set())
        self.assertFalse((app.NAMESPACE/'.reader-layout.lock').exists())

    def test_snapshot_writer_refuses_replacement(self):
        p=Path(self.temp.name)/'immutable.json';app.exclusive(p,b'original')
        with self.assertRaises(FileExistsError):app.exclusive(p,b'replacement')
        self.assertEqual(p.read_bytes(),b'original')

    def test_selected_input_cannot_target_old_namespace(self):
        with self.assertRaisesRegex(ValueError,'production/structural-pilot'):
            app.task_file('docs/research/sequence-pilot/reader/review-data.json',input_file=True)

    def test_selected_input_cannot_target_immutable_history(self):
        snapshots=list((app.NAMESPACE/'layout-history').glob('*/input-before.json'))
        self.assertTrue(snapshots)
        with self.assertRaisesRegex(ValueError,'history/drafts are protected'):
            app.task_file(str(snapshots[0]),input_file=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
