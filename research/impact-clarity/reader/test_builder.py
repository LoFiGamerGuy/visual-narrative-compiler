"""Boundary checks use disposable tiny PNG fixtures, never study artwork."""
from pathlib import Path
import copy, hashlib, importlib.util, json, struct, tempfile, unittest, zlib
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('builder',HERE/'build_reader.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def chunk(k,v):return struct.pack('>I',len(v))+k+v+struct.pack('>I',zlib.crc32(k+v)&0xffffffff)
PNG=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',3,2,8,6,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'\0'*12)*2))+chunk(b'IEND',b'')
class Tests(unittest.TestCase):
 def setUp(self):
  scratch=HERE/'.scratch/tests';scratch.mkdir(parents=True,exist_ok=True);self.tmp=tempfile.TemporaryDirectory(dir=scratch);self.root=Path(self.tmp.name);self.source=self.root/'production/impact-clarity';self.out=self.root/'docs/impact-clarity';self.source.mkdir(parents=True);(self.source/'fixture.png').write_bytes(PNG)
  self.c={'id':'M01','attempt_id':'M01-P','path':'production/impact-clarity/fixture.png','sha256':hashlib.sha256(PNG).hexdigest(),'width':3,'height':2,'status':'reviewable-unaccepted'}
  self.plan={'schema':'ImpactClarityPlan/1','experiment_id':'IC-20260909-01','entries':[{'id':i,'category':c,'group':'radical' if i.startswith('X') else 'comparison' if i.startswith('Y') else 'core','title':i,'caption':'Visible scene caption.','scale':'wide','subjects':['riven'],'references':[]}for c,ids in b.CATEGORY_IDS.items()for i in ids]};self.rows=[];self.selected={};self.write();self.patches=[patch.object(b,'ROOT',self.root),patch.object(b,'SOURCE',self.source),patch.object(b,'OUT',self.out)];[p.start()for p in self.patches]
 def tearDown(self):
  [p.stop()for p in self.patches];self.tmp.cleanup()
 def write(self):
  for n,v in [('plan.json',self.plan),('candidates.json',{'candidates':self.rows}),('selected.json',{'selected':self.selected})]:(self.source/n).write_text(json.dumps(v))
 def one(self):self.rows=[copy.deepcopy(self.c)];self.selected={'M01':'M01-P'};self.write()
 def test_missing_plan_is_explicit(self):
  (self.source/'plan.json').unlink();d=b.build();self.assertEqual(d['entries'],[]);self.assertIsNone(d['plan_sha256'])
  with self.assertRaises(ValueError):b.build(True)
 def test_pending(self):
  d=b.build();self.assertEqual(len(d['entries']),16);self.assertEqual(d['available_count'],0);self.assertTrue(all(e['candidate']is None for e in d['entries']));self.assertIsNone(d['owner_approval'])
 def test_final_requires16(self):
  self.one()
  with self.assertRaises(ValueError):b.build(True)
 def test_complete(self):
  self.rows=[{**self.c,'id':e['id'],'attempt_id':e['id']+'-P'}for e in self.plan['entries']];self.selected={c['id']:c['attempt_id']for c in self.rows};self.write();self.assertEqual(b.build(True)['available_count'],16)
 def test_hash_failure_preserves_output(self):
  self.one();b.build();old=(self.out/'data.js').read_bytes();self.rows[0]['sha256']='0'*64;self.write()
  with self.assertRaises(ValueError):b.build()
  self.assertEqual(old,(self.out/'data.js').read_bytes())
 def test_path_escape(self):
  self.one();self.rows[0]['path']='outside.png';self.write()
  with self.assertRaises(ValueError):b.build()
 def test_native_dimensions(self):
  self.one();self.rows[0]['width']=4;self.write()
  with self.assertRaises(ValueError):b.build()
 def test_selected_wrong_id(self):
  self.one();self.selected={'M02':'M01-P'};self.write()
  with self.assertRaises(ValueError):b.build()
 def test_duplicate_attempt(self):
  self.one();self.rows*=2;self.write()
  with self.assertRaises(ValueError):b.build()
 def test_category_contract(self):
  self.plan['entries'][0]['category']='ability';self.write()
  with self.assertRaises(ValueError):b.build()
 def test_reference_link(self):
  self.plan['entries'][0]['references']=['missing'];self.write()
  with self.assertRaises(ValueError):b.build()
 def test_generated_reference_pending_link(self):
  self.plan['entries'][0]['references']=['@X01'];self.write();self.assertEqual(b.build()['entries'][0]['references'],['@X01'])
 def test_subject_contract(self):
  self.plan['entries'][0]['subjects']=[{}];self.write()
  with self.assertRaises(ValueError):b.build()
 def test_growth_string_and_null(self):
  self.plan['entries'][0]['power']=None;self.plan['entries'][1]['power']={'name':'Power','description':'Effect','growth':'A possible change.'};self.write();d=b.build();self.assertIsNone(d['entries'][0]['power']);self.assertEqual(d['entries'][1]['power']['growth'],['A possible change.'])
 def test_prior_exact(self):
  raw=b'{"choices":{"old":{"character":"like","shortlist":true}}}\n';p=self.source/'prior.json';p.write_bytes(raw);self.plan['prior_choices']={'path':'production/impact-clarity/prior.json','sha256':b.sha(p)};self.write();d=b.build();self.assertEqual(d['previous']['export']['choices']['old']['character'],'like');self.assertNotIn('choices',d['entries'][0]);self.assertEqual(p.read_bytes(),raw);p.write_bytes(raw+b' ')
  with self.assertRaises(ValueError):b.build()
 def test_notes_bound_without_reset(self):
  self.one();before=b.build()['dataset_sha256'];p=self.source/'review-notes.json';notes={'schema':'ImpactClarityReviewNotes/1','experiment_id':self.plan['experiment_id'],'entries':{'M01':{'attempt_id':'M01-P','sha256':self.c['sha256'],'observations':['Inspection pending.']}}};p.write_text(json.dumps(notes));self.assertEqual(before,b.build()['dataset_sha256']);notes['entries']['M01']['sha256']='bad';p.write_text(json.dumps(notes))
  with self.assertRaises(ValueError):b.build()
 def test_old_call_plan_bound_to_preserved_bytes(self):
  self.one();old=b.sha(self.source/'plan.json');history=self.source/'plan-history';history.mkdir();(history/'plan-v2.json').write_bytes((self.source/'plan.json').read_bytes());self.plan['entries'][1]['caption']='Revised ungenerated panel.';self.write();(self.source/'calls').mkdir();call=self.source/'calls/M01-P.json';call.write_text(json.dumps({'id':'M01','attempt_id':'M01-P','plan_sha256':old}));d=b.build();self.assertEqual(d['entries'][0]['history'][0]['plan_sha256'],old);self.assertTrue(d['entries'][0]['history'][0]['plan_path'].endswith('plan-v2.json'));(history/'plan-v2.json').write_text(json.dumps(self.plan))
  with self.assertRaises(ValueError):b.build()
 def test_call_unknown_plan_hash_rejected(self):
  self.one();(self.source/'calls').mkdir();(self.source/'calls/M01-P.json').write_text(json.dumps({'id':'M01','attempt_id':'M01-P','plan_sha256':'unknown'}))
  with self.assertRaises(ValueError):b.build()

 def test_pair_targets_rejected(self):
  self.plan['entries'][0]['paired_ids']=['missing'];self.write()
  with self.assertRaises(ValueError):b.build()
 def test_self_pair_rejected(self):
  self.plan['entries'][0]['paired_ids']=['M01'];self.write()
  with self.assertRaises(ValueError):b.build()
 def test_explicit_pair_only(self):
  self.plan['entries'][0]['paired_ids']=['X01'];self.write();d=b.build();self.assertEqual(d['entries'][0]['paired_ids'],['X01']);self.assertNotIn('paired_ids',d['entries'][1])
 def test_group_contract(self):
  self.plan['entries'][0]['group']='radical';self.write()
  with self.assertRaises(ValueError):b.build()
 def test_prompt_binding(self):
  self.one();p=self.source/'prompt.txt';p.write_text('Exact prompt');(self.source/'calls').mkdir();(self.source/'calls/M01-P.json').write_text(json.dumps({'id':'M01','attempt_id':'M01-P','plan_sha256':b.sha(self.source/'plan.json'),'prompt_path':'production/impact-clarity/prompt.txt','prompt_sha256':b.sha(p),'references':[]}));d=b.build();self.assertEqual(d['entries'][0]['history'][0]['prompt_sha256'],b.sha(p));p.write_text('Changed prompt')
  with self.assertRaises(ValueError):b.build()
 def test_original_twelve_plan_calls_remain_bound(self):
  self.one();original=dict(self.plan,entries=[e for e in self.plan['entries'] if not e['id'].startswith('Y')]);history=self.source/'plan-history';history.mkdir();old=history/'plan-v1.json';old.write_text(json.dumps(original));(self.source/'calls').mkdir();(self.source/'calls/M01-P.json').write_text(json.dumps({'id':'M01','attempt_id':'M01-P','plan_sha256':b.sha(old)}));self.assertEqual(b.build()['entries'][0]['history'][0]['plan_sha256'],b.sha(old))
if __name__=='__main__':unittest.main()
