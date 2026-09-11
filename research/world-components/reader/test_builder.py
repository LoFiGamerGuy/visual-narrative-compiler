"""Source-boundary checks in disposable new-reader fixtures only."""
from pathlib import Path
import copy,hashlib,importlib.util,json,struct,tempfile,unittest
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('world_builder',HERE/'build_reader.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
class BuilderTests(unittest.TestCase):
 def setUp(self):
  scratch=HERE/'.scratch/tests';scratch.mkdir(parents=True,exist_ok=True);self.tmp=tempfile.TemporaryDirectory(dir=scratch);self.root=Path(self.tmp.name);self.source=self.root/'production/world-components';self.source.mkdir(parents=True);self.out=self.root/'docs/world-components'
  ref=json.loads((b.SOURCE/'references.json').read_text())[0];raw=(b.ROOT/ref['path']).read_bytes();(self.source/'fixture.png').write_bytes(raw);w,h=struct.unpack('>II',raw[16:24]);self.c={'id':'01-C1','attempt_id':'01-C1-P','path':'production/world-components/fixture.png','sha256':hashlib.sha256(raw).hexdigest(),'width':w,'height':h,'status':'reviewable-unaccepted'}
  self.plan={'schema':'WorldComponentPlan/1','experiment_id':'fixture','styles':[{'id':s,'title':s}for s in b.STYLES],'categories':[{'id':c,'title':c}for c in b.CATEGORIES],'entries':[{'id':s+'-'+c,'style_id':s,'category_id':c,'title':s+' '+c}for s in b.STYLES for c in b.CATEGORIES]};self.rows=[];self.selected={};self.refs=[{'id':s,'path':self.c['path'],'sha256':self.c['sha256']}for s in b.STYLES];self.write();self.patches=[patch.object(b,'ROOT',self.root),patch.object(b,'SOURCE',self.source),patch.object(b,'OUT',self.out)];[p.start()for p in self.patches]
 def tearDown(self):
  [p.stop()for p in self.patches];self.tmp.cleanup()
 def write(self):
  for name,data in [('kit-plan.json',self.plan),('references.json',self.refs),('candidates.json',{'candidates':self.rows}),('selected.json',{'selected':self.selected})]:(self.source/name).write_text(json.dumps(data))
 def one(self):self.rows=[copy.deepcopy(self.c)];self.selected={'01-C1':'01-C1-P'};self.write()
 def test_pending_images_are_explicit_and_not_anchor_substitutes(self):
  d=b.build();self.assertEqual(d['available_count'],0);self.assertEqual(len(d['entries']),54);self.assertTrue(all(e['candidate']is None for e in d['entries']));self.assertIsNone(d['canon'])
 def test_final_requires_all54(self):
  self.one()
  with self.assertRaises(ValueError):b.build(True)
  self.assertFalse((self.out/'data.js').exists())
 def test_hash_failure_preserves_last_output(self):
  self.one();b.build();before=(self.out/'data.js').read_bytes();self.rows[0]['sha256']='0'*64;self.write()
  with self.assertRaises(ValueError):b.build()
  self.assertEqual(before,(self.out/'data.js').read_bytes())
 def test_namespace_escape_rejected(self):
  self.one();self.rows[0]['path']='outside.png';self.write()
  with self.assertRaises(ValueError):b.build()
 def test_declared_dimensions_bound_to_png(self):
  self.one();self.rows[0]['width']+=1;self.write()
  with self.assertRaises(ValueError):b.build()
 def test_selected_attempt_must_belong_to_component(self):
  self.one();self.selected={'01-C2':'01-C1-P'};self.write()
  with self.assertRaises(ValueError):b.build()
 def test_duplicate_attempt_rejected(self):
  self.one();self.rows.append(self.rows[0]);self.write()
  with self.assertRaises(ValueError):b.build()
 def test_original_anchor_hash_verified(self):
  self.refs[0]['sha256']='0'*64;self.write()
  with self.assertRaises(ValueError):b.build()
 def test_all_nine_original_style_ids_required(self):
  self.plan['styles'][0]['id']='20';self.write()
  with self.assertRaises(ValueError):b.build()
 def test_category_identity_cannot_drift(self):
  self.plan['entries'][0]['category_id']='C2';self.write()
  with self.assertRaises(ValueError):b.build()
 def test_gear_caps_at_three_with_function_captions(self):
  self.plan['entries'][5]['items']=[{'name':'thing','function':'use'}]*4;self.write()
  with self.assertRaises(ValueError):b.build()
 def test_notes_do_not_reset_choices_dataset(self):
  self.one();before=b.build()['dataset_sha256'];notes={'schema':'WorldComponentReviewNotes/1','experiment_id':'fixture','entries':{'01-C1':{'attempt_id':self.c['attempt_id'],'sha256':self.c['sha256'],'observations':['Technical note.']}}};(self.source/'review-notes.json').write_text(json.dumps(notes));after=b.build();self.assertEqual(before,after['dataset_sha256']);self.assertEqual(after['entries'][0]['ai_observations'],['Technical note.'])
 def test_stale_notes_rejected(self):
  self.one();(self.source/'review-notes.json').write_text(json.dumps({'schema':'WorldComponentReviewNotes/1','experiment_id':'fixture','entries':{'01-C1':{'attempt_id':'old','sha256':self.c['sha256'],'observations':[]}}}))
  with self.assertRaises(ValueError):b.build()
 def test_history_keeps_primary_and_retry_with_hashed_call(self):
  self.one();retry={**self.c,'attempt_id':'01-C1-R'};self.rows.append(retry);self.selected['01-C1']='01-C1-R';self.write();calls=self.source/'calls';calls.mkdir();(calls/'01-C1-R.json').write_text(json.dumps({'id':'01-C1','attempt_id':'01-C1-R','retry_of':'01-C1-P','retry_reason':'Unwanted duplicate hand.'}));d=b.build();h=d['entries'][0]['history'];self.assertEqual([c['attempt_id']for c in h],['01-C1-P','01-C1-R']);self.assertEqual(h[1]['call_sha256'],b.sha(calls/'01-C1-R.json'))
 def test_retry_without_exact_call_proof_rejected(self):
  self.one();self.rows.append({**self.c,'attempt_id':'01-C1-R','retry_of':'01-C1-P','retry_reason':'Defect'});self.selected['01-C1']='01-C1-R';self.write()
  with self.assertRaises(ValueError):b.build()
 def test_display_cleanup_preserves_raw_plan_and_choice_identity(self):
  self.plan['entries'][2]['caption']='An environment; no extra objects.';self.write();original=(self.source/'kit-plan.json').read_bytes();path=self.source/'display.json';path.write_text(json.dumps({'schema':'WorldComponentDisplayTextOverrides/1','entries':{}}))
  with patch.object(b,'DISPLAY_OVERRIDES',path):
   before=b.build()['dataset_sha256'];path.write_text(json.dumps({'schema':'WorldComponentDisplayTextOverrides/1','entries':{'01-E1':{'caption':{'source':'An environment; no extra objects.','display':'An environment.'}}}}));after=b.build()
  self.assertEqual(before,after['dataset_sha256']);self.assertEqual(after['entries'][2]['caption'],'An environment; no extra objects.');self.assertEqual(after['entries'][2]['display_caption'],'An environment.');self.assertEqual(original,(self.source/'kit-plan.json').read_bytes())
 def test_stale_display_override_rejected(self):
  self.plan['entries'][2]['caption']='Changed brief.';self.write();path=self.source/'display.json';path.write_text(json.dumps({'schema':'WorldComponentDisplayTextOverrides/1','entries':{'01-E1':{'caption':{'source':'Old brief.','display':'A description.'}}}}))
  with patch.object(b,'DISPLAY_OVERRIDES',path):
   with self.assertRaises(ValueError):b.build()
if __name__=='__main__':unittest.main()
