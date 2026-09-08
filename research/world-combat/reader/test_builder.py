"""Boundary tests use only disposable3×2 PNG fixtures under the new reader scratch."""
from pathlib import Path
import copy, hashlib, importlib.util, json, struct, tempfile, unittest, zlib
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('world_combat_builder',HERE/'build_reader.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def encode(value):return json.dumps(value).encode()
def chunk(kind,payload):return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
PNG=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',3,2,8,6,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'\0'*12)*2))+chunk(b'IEND',b'')
class Tests(unittest.TestCase):
 def setUp(self):
  scratch=HERE/'.scratch/tests';scratch.mkdir(parents=True,exist_ok=True);self.tmp=tempfile.TemporaryDirectory(dir=scratch);self.root=Path(self.tmp.name);self.source=self.root/'production/world-combat';self.out=self.root/'docs/world-combat';self.source.mkdir(parents=True);(self.source/'fixture.png').write_bytes(PNG)
  self.c={'id':'S01','attempt_id':'S01-P','path':'production/world-combat/fixture.png','sha256':hashlib.sha256(PNG).hexdigest(),'width':3,'height':2,'status':'reviewable-unaccepted'}
  self.plan={'schema':'WorldCombatPlan/1','experiment_id':'fixture','styles':[{'id':s,'title':s}for s in ['01','02','06']],'entries':[{'id':id,'category':category,'style_id':'01','title':id,'caption':'A visible design caption.','related_ids':[]}for category,ids in b.CATEGORY_IDS.items()for id in ids]};self.rows=[];self.selected={};self.refs=[{'id':s,'path':self.c['path'],'sha256':self.c['sha256']}for s in b.STYLES];self.write()
  prev=self.source/'previous';prev.mkdir();(prev/'fixture.png').write_bytes(PNG);(prev/'plan.json').write_bytes(encode({'previous':'frozen'}));plan_sha=b.sha(prev/'plan.json');ids=[s+'-'+c for s in b.STYLES for c in ['C1','C2']];bindings=[{'id':id,'attempt_id':id+'-P','sha256':self.c['sha256']}for id in ids];sources=[{**v,'path':'production/world-combat/previous/fixture.png'}for v in bindings];old={'schema':'CombatExplorationReader/1','experiment_id':'previous','dataset_sha256':'a'*64,'plan_sha256':plan_sha,'source_bindings':bindings,'styles':[{'id':s,'title':s}for s in b.STYLES],'entries':[{'id':id,'style_id':id[:2],'title':id,'candidate':{'attempt_id':id+'-P','sha256':self.c['sha256']}}for id in ids]};selection={'schema':'CombatExplorationChoices/1',**{k:old[k]for k in ['experiment_id','dataset_sha256','plan_sha256','source_bindings']},'exported_at':'2026-09-08T00:00:00Z','choices':{id:{'character':'like','style':'like','weapon':None,'power':None,'comfort':None,'note':'','shortlist':True}for id in ids}}
  for name,value in [('data.json',old),('selection.json',selection),('manifest.json',{'schema':'WorldCombatPreviousSources/1','selection_path':'production/world-combat/previous/selection.json','sources':sources})]:(prev/name).write_bytes(encode(value))
  report=self.root/'research/world-combat';report.mkdir(parents=True);(report/'previous-validation.json').write_bytes(encode({'schema':'WorldCombatPreviousValidation/1','export_sha256':b.sha(prev/'selection.json'),'data_sha256':b.sha(prev/'data.json'),'plan_sha256':plan_sha}))
  self.patches=[patch.object(b,'ROOT',self.root),patch.object(b,'SOURCE',self.source),patch.object(b,'OUT',self.out)];[p.start()for p in self.patches]
 def tearDown(self):
  [p.stop()for p in self.patches];self.tmp.cleanup()
 def write(self):
  for name,value in [('world-combat-plan.json',self.plan),('references.json',self.refs),('candidates.json',{'candidates':self.rows}),('selected.json',{'selected':self.selected})]:(self.source/name).write_bytes(encode(value))
 def one(self):self.rows=[copy.deepcopy(self.c)];self.selected={'S01':'S01-P'};self.write()
 def test_pending24_and_separate_previous18(self):
  d=b.build();self.assertEqual(d['available_count'],0);self.assertEqual(len(d['entries']),24);self.assertTrue(all(e['candidate']is None for e in d['entries']));self.assertEqual(len(d['previous']['entries']),18);self.assertTrue(d['previous']['entries'][0]['choices']['shortlist']);self.assertNotIn('choices',d['entries'][0]);self.assertIsNone(d['owner_approval'])
 def test_final_requires_all24(self):
  self.one()
  with self.assertRaises(ValueError):b.build(True)
 def test_exact24_final(self):
  self.rows=[{**self.c,'id':e['id'],'attempt_id':e['id']+'-P'}for e in self.plan['entries']];self.selected={c['id']:c['attempt_id']for c in self.rows};self.write();self.assertEqual(b.build(True)['available_count'],24)
 def test_failed_hash_preserves_previous_output(self):
  self.one();b.build();before=(self.out/'data.js').read_bytes();self.rows[0]['sha256']='0'*64;self.write()
  with self.assertRaises(ValueError):b.build()
  self.assertEqual((self.out/'data.js').read_bytes(),before)
 def test_source_namespace_escape(self):
  self.one();self.rows[0]['path']='outside.png';self.write()
  with self.assertRaises(ValueError):b.build()
 def test_native_dimensions(self):
  self.one();self.rows[0]['width']=4;self.write()
  with self.assertRaises(ValueError):b.build()
 def test_selected_id_binding(self):
  self.one();self.selected={'C01':'S01-P'};self.write()
  with self.assertRaises(ValueError):b.build()
 def test_duplicate_attempt(self):
  self.one();self.rows.append(self.rows[0]);self.write()
  with self.assertRaises(ValueError):b.build()
 def test_category_identity(self):
  self.plan['entries'][0]['category']='character';self.write()
  with self.assertRaises(ValueError):b.build()
 def test_related_must_be_new_round(self):
  self.plan['entries'][0]['related_ids']=['01-C1'];self.write()
  with self.assertRaises(ValueError):b.build()
 def test_optional_growth_plain_list(self):
  self.plan['entries'][0]['power']={'name':'Pulse','description':'Push','growth':[{}]};self.write()
  with self.assertRaises(ValueError):b.build()
 def test_adult_age(self):
  self.plan['entries'][6]['age']=17;self.write()
  with self.assertRaises(ValueError):b.build()
 def test_preserved_export_exact_bytes(self):
  p=self.source/'previous/selection.json';p.write_text(p.read_text()+'\n')
  with self.assertRaises(ValueError):b.build()
 def test_previous_native_hash(self):
  (self.source/'previous/fixture.png').write_bytes(PNG+b'changed')
  with self.assertRaises(ValueError):b.build()
 def test_notes_do_not_reset_dataset(self):
  self.one();before=b.build()['dataset_sha256'];(self.source/'review-notes.json').write_bytes(encode({'schema':'WorldCombatReviewNotes/1','experiment_id':'fixture','entries':{'S01':{'attempt_id':'S01-P','sha256':self.c['sha256'],'observations':['Source-bound observation.']}}}));self.assertEqual(b.build()['dataset_sha256'],before)
 def test_stale_notes(self):
  self.one();(self.source/'review-notes.json').write_bytes(encode({'schema':'WorldCombatReviewNotes/1','experiment_id':'fixture','entries':{'S01':{'attempt_id':'S01-R1','sha256':self.c['sha256'],'observations':[]}}}))
  with self.assertRaises(ValueError):b.build()
 def test_retry_needs_call_and_retained_source(self):
  self.one();self.rows.append({**self.c,'attempt_id':'S01-R1','retry_of':'S01-P','retry_reason':'Defect'});self.selected['S01']='S01-R1';self.write()
  with self.assertRaises(ValueError):b.build()
 def test_history_preserved_selection_changes_identity(self):
  self.one();before=b.build()['dataset_sha256'];self.rows.append({**self.c,'attempt_id':'S01-R1'});self.selected['S01']='S01-R1';self.write();calls=self.source/'calls';calls.mkdir();(calls/'S01-R1.json').write_bytes(encode({'retry_of':'S01-P','retry_reason':'Defect'}));d=b.build();self.assertNotEqual(d['dataset_sha256'],before);self.assertEqual(len(d['entries'][0]['history']),2);self.assertEqual(d['entries'][0]['history'][1]['call_sha256'],b.sha(calls/'S01-R1.json'))
if __name__=='__main__':unittest.main()
