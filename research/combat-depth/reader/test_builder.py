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
  scratch=HERE/'.scratch/tests';scratch.mkdir(parents=True,exist_ok=True);self.tmp=tempfile.TemporaryDirectory(dir=scratch);self.root=Path(self.tmp.name);self.source=self.root/'production/combat-depth';self.out=self.root/'docs/combat-depth';self.source.mkdir(parents=True);(self.source/'fixture.png').write_bytes(PNG)
  self.c={'id':'D01','attempt_id':'D01-P','path':'production/combat-depth/fixture.png','sha256':hashlib.sha256(PNG).hexdigest(),'width':3,'height':2,'status':'reviewable-unaccepted'}
  self.plan={'schema':'CombatDepthPlan/1','experiment_id':'CD-20260908-01','entries':[{'id':i,'category':c,'title':i,'caption':'Visible scene caption.','scale':'wide','subjects':['riven'],'story_path':'arrival','references':[]}for c,ids in b.CATEGORY_IDS.items()for i in ids]};self.rows=[];self.selected={};self.write();self.patches=[patch.object(b,'ROOT',self.root),patch.object(b,'SOURCE',self.source),patch.object(b,'OUT',self.out)];[p.start()for p in self.patches]
 def tearDown(self):
  [p.stop()for p in self.patches];self.tmp.cleanup()
 def write(self):
  for n,v in [('plan.json',self.plan),('candidates.json',{'candidates':self.rows}),('selected.json',{'selected':self.selected})]:(self.source/n).write_text(json.dumps(v))
 def one(self):self.rows=[copy.deepcopy(self.c)];self.selected={'D01':'D01-P'};self.write()
 def test_missing_plan_is_explicit(self):
  (self.source/'plan.json').unlink();d=b.build();self.assertEqual(d['entries'],[]);self.assertIsNone(d['plan_sha256'])
  with self.assertRaises(ValueError):b.build(True)
 def test_pending(self):
  d=b.build();self.assertEqual(len(d['entries']),24);self.assertEqual(d['available_count'],0);self.assertTrue(all(e['candidate']is None for e in d['entries']));self.assertIsNone(d['owner_approval'])
 def test_final_requires24(self):
  self.one()
  with self.assertRaises(ValueError):b.build(True)
 def test_complete(self):
  self.rows=[{**self.c,'id':e['id'],'attempt_id':e['id']+'-P'}for e in self.plan['entries']];self.selected={c['id']:c['attempt_id']for c in self.rows};self.write();self.assertEqual(b.build(True)['available_count'],24)
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
  self.one();self.selected={'D02':'D01-P'};self.write()
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
  self.plan['entries'][0]['references']=['@G05'];self.write();self.assertEqual(b.build()['entries'][0]['references'],['@G05'])
 def test_subject_contract(self):
  self.plan['entries'][0]['subjects']=[{}];self.write()
  with self.assertRaises(ValueError):b.build()
 def test_growth_string_and_null(self):
  self.plan['entries'][0]['power']=None;self.plan['entries'][1]['power']={'name':'Power','description':'Effect','growth':'A possible change.'};self.write();d=b.build();self.assertIsNone(d['entries'][0]['power']);self.assertEqual(d['entries'][1]['power']['growth'],['A possible change.'])
 def test_prior_exact(self):
  raw=b'{"choices":{"old":{"character":"like","shortlist":true}}}\n';p=self.source/'prior.json';p.write_bytes(raw);self.plan['prior_choices']={'path':'production/combat-depth/prior.json','sha256':b.sha(p)};self.write();d=b.build();self.assertEqual(d['previous']['export']['choices']['old']['character'],'like');self.assertNotIn('choices',d['entries'][0]);self.assertEqual(p.read_bytes(),raw);p.write_bytes(raw+b' ')
  with self.assertRaises(ValueError):b.build()
 def test_notes_bound_without_reset(self):
  self.one();before=b.build()['dataset_sha256'];p=self.source/'review-notes.json';notes={'schema':'CombatDepthReviewNotes/1','experiment_id':self.plan['experiment_id'],'entries':{'D01':{'attempt_id':'D01-P','sha256':self.c['sha256'],'observations':['Inspection pending.']}}};p.write_text(json.dumps(notes));self.assertEqual(before,b.build()['dataset_sha256']);notes['entries']['D01']['sha256']='bad';p.write_text(json.dumps(notes))
  with self.assertRaises(ValueError):b.build()
 def test_old_call_plan_bound_to_preserved_bytes(self):
  self.one();old=b.sha(self.source/'plan.json');history=self.source/'plan-history';history.mkdir();(history/'plan-v2.json').write_bytes((self.source/'plan.json').read_bytes());self.plan['entries'][1]['caption']='Revised ungenerated panel.';self.write();(self.source/'calls').mkdir();call=self.source/'calls/D01-P.json';call.write_text(json.dumps({'id':'D01','attempt_id':'D01-P','plan_sha256':old}));d=b.build();self.assertEqual(d['entries'][0]['history'][0]['plan_sha256'],old);self.assertTrue(d['entries'][0]['history'][0]['plan_path'].endswith('plan-v2.json'));(history/'plan-v2.json').write_text(json.dumps(self.plan))
  with self.assertRaises(ValueError):b.build()
 def test_call_unknown_plan_hash_rejected(self):
  self.one();(self.source/'calls').mkdir();(self.source/'calls/D01-P.json').write_text(json.dumps({'id':'D01','attempt_id':'D01-P','plan_sha256':'unknown'}))
  with self.assertRaises(ValueError):b.build()
 def test_failure_preserved_plan_allowed(self):
  self.failure_fixture();history=self.source/'plan-history';history.mkdir();(history/'plan-v2.json').write_bytes((self.source/'plan.json').read_bytes());self.plan['entries'][1]['caption']='Revised.';self.write();self.assertEqual(len(b.build()['entries'][0]['service_failures']),1)
 def control_fixture(self):
  folder=self.root/'research/combat-depth/controls';folder.mkdir(parents=True);(folder/'map.png').write_bytes(PNG);svg=folder/'map.svg';svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>');manifest={'schema':'CombatDepthControls/1','experiment_id':'CD-20260908-01','controls':[{'id':'map-duel','path':'research/combat-depth/controls/map.png','sha256':self.c['sha256'],'source_path':'research/combat-depth/controls/map.svg','source_sha256':b.sha(svg),'role':'Blocking only'}]};(folder/'manifest.json').write_text(json.dumps(manifest));self.plan['entries'][0]['references']=['map-duel'];self.write();return folder,manifest
 def test_control_is_separate_and_editable(self):
  self.control_fixture();d=b.build();c=next(c for c in d['controls']if c['id']=='map-duel');self.assertFalse(c['pending']);self.assertTrue(c['source_src'].endswith('map.svg'));self.assertEqual(d['references'],[]);self.assertNotIn('choices',c)
 def test_known_control_pending(self):
  self.plan['entries'][0]['references']=['map-duel'];self.write();self.assertTrue(next(c for c in b.build()['controls']if c['id']=='map-duel')['pending'])
 def test_control_svg_tamper(self):
  folder,_=self.control_fixture();(folder/'map.svg').write_text('<svg/>')
  with self.assertRaises(ValueError):b.build()
 def test_control_png_tamper(self):
  folder,_=self.control_fixture();(folder/'map.png').write_bytes(PNG+b'changed')
  with self.assertRaises(ValueError):b.build()
 def test_control_source_escape(self):
  folder,m=self.control_fixture();m['controls'][0]['source_path']='outside.svg';(folder/'manifest.json').write_text(json.dumps(m))
  with self.assertRaises(ValueError):b.build()
 def failure_fixture(self):
  self.one();folder=self.source/'transport-failures';folder.mkdir();prompt=self.source/'prompt.txt';prompt.write_text('Source-only finishing.');path=folder/'D01-F1-service-call-01.json';failure={'id':'D01','attempt_id':'D01-F1','status':'failed-no-artwork-returned','returned_artwork':None,'error':'HTTP503','plan_sha256':b.sha(self.source/'plan.json'),'prompt_path':'production/combat-depth/prompt.txt','prompt_sha256':b.sha(prompt),'retry_of':'D01-P','references':[{'path':self.c['path'],'sha256':self.c['sha256']}]};path.write_text(json.dumps(failure));side=folder/'D01-F1-service-call-01-tool-output.json';side.write_text(json.dumps({'schema':'CombatDepthToolFailure/1','failure_record_path':path.relative_to(self.root).as_posix(),'failure_record_sha256':b.sha(path),'outcome':{'id':'D01-F1','status':'error','error':'HTTP503'}}));return path,side,prompt
 def test_failure_is_not_artwork_or_vote(self):
  self.one();identity=b.build()['dataset_sha256'];self.failure_fixture();d=b.build();self.assertEqual(d['dataset_sha256'],identity);self.assertEqual(d['available_count'],1);self.assertEqual(len(d['entries'][0]['history']),1);self.assertEqual(len(d['entries'][0]['service_failures']),1);self.assertNotEqual(d['entries'][0]['service_failures'][0]['record_path'],d['entries'][0]['service_failures'][0]['tool_output_path'])
 def test_failure_prompt_tamper(self):
  _,_,prompt=self.failure_fixture();prompt.write_text('Changed')
  with self.assertRaises(ValueError):b.build()
 def test_failure_sidecar_tamper(self):
  _,side,_=self.failure_fixture();s=json.loads(side.read_text());s['failure_record_sha256']='bad';side.write_text(json.dumps(s))
  with self.assertRaises(ValueError):b.build()
 def test_failure_reference_tamper(self):
  path,_,_=self.failure_fixture();f=json.loads(path.read_text());f['references'][0]['sha256']='bad';path.write_text(json.dumps(f))
  with self.assertRaises(ValueError):b.build()
 def test_failure_transport_prompt_changed(self):
  path,_,_=self.failure_fixture();f=json.loads(path.read_text());(self.source/'calls').mkdir();(self.source/'calls/D01-F1.json').write_text(json.dumps({**f,'transport_retry_of':path.relative_to(self.root).as_posix(),'transport_retry_sha256':b.sha(path),'prompt_sha256':'wrong'}))
  with self.assertRaises(ValueError):b.build()
 def input_failure_fixture(self):
  self.one();folder=self.source/'input-validation-failures';folder.mkdir();refs=[]
  for i in range(6):
   name='w01.png' if i==4 else f'ref{i}.png';(self.source/name).write_bytes(PNG);refs.append({'path':'production/combat-depth/'+name,'sha256':self.c['sha256'],'role':str(i)})
  self.rows.append({**self.c,'id':'W01','attempt_id':'W01-P','path':'production/combat-depth/w01.png'});self.write();old_hash=b.sha(self.source/'plan.json');history=self.source/'plan-history';history.mkdir();(history/'plan-v6.json').write_bytes((self.source/'plan.json').read_bytes());prompt=self.source/'old-prompt.txt';prompt.write_text('Original six-image prompt.');f={'id':'W06','attempt_id':'W06-P','phase':'primary','status':'failed-no-artwork-returned','returned_artwork':None,'error':'referenced_image_paths must contain at most 5 paths','plan_sha256':old_hash,'prompt_path':'production/combat-depth/old-prompt.txt','prompt_sha256':b.sha(prompt),'references':refs};path=folder/'W06-P.json';path.write_text(json.dumps(f));(folder/'W06-P-tool-output.json').write_text(json.dumps({'schema':'CombatDepthToolFailure/1','failure_record_path':path.relative_to(self.root).as_posix(),'failure_record_sha256':b.sha(path),'outcome':{'id':'W06-P','status':'error','error':f['error']}}));self.plan['revision']='Reference-count correction';self.write();newprompt=self.source/'new-prompt.txt';newprompt.write_text('Changed five-image prompt.');retry={**f,'plan_sha256':b.sha(self.source/'plan.json'),'prompt_path':'production/combat-depth/new-prompt.txt','prompt_sha256':b.sha(newprompt),'references':refs[:4]+refs[5:],'input_validation_retry_of':path.relative_to(self.root).as_posix(),'input_validation_retry_sha256':b.sha(path),'input_validation_retry_reason':'Drop redundant W01; changed inputs.'};(self.source/'calls').mkdir();call=self.source/'calls/W06-P.json';call.write_text(json.dumps(retry));return call,retry,prompt
 def test_input_validation_changed_request_is_not_artwork(self):
  self.input_failure_fixture();d=b.build();e=next(e for e in d['entries']if e['id']=='W06');self.assertIsNone(e['candidate']);self.assertEqual(e['history'],[]);self.assertEqual(e['service_failures'][0]['kind'],'input-validation');self.assertEqual(len(e['service_failures'][0]['references']),6);self.assertIn('retry_request_path',e['service_failures'][0]);self.assertEqual(d['available_count'],1)
 def test_input_validation_must_drop_only_W01(self):
  call,retry,_=self.input_failure_fixture();retry['references']=retry['references'][1:];call.write_text(json.dumps(retry))
  with self.assertRaises(ValueError):b.build()
 def test_input_validation_original_prompt_immutable(self):
  _,_,prompt=self.input_failure_fixture();prompt.write_text('Overwritten')
  with self.assertRaises(ValueError):b.build()
 def test_input_validation_retry_hash_required(self):
  call,retry,_=self.input_failure_fixture();retry['input_validation_retry_sha256']='bad';call.write_text(json.dumps(retry))
  with self.assertRaises(ValueError):b.build()
 def test_retry_retention(self):
  self.one();before=b.build()['dataset_sha256'];self.rows.append({**self.c,'attempt_id':'D01-R1'});self.selected['D01']='D01-R1';self.write()
  with self.assertRaises(ValueError):b.build()
  (self.source/'calls').mkdir();(self.source/'calls/D01-R1.json').write_text(json.dumps({'plan_sha256':b.sha(self.source/'plan.json'),'id':'D01','attempt_id':'D01-R1','retry_of':'D01-P','retry_reason':'Correct a declared defect.'}));d=b.build();self.assertEqual(len(d['entries'][0]['history']),2);self.assertNotEqual(before,d['dataset_sha256']);self.rows.append({**self.c,'attempt_id':'D01-F1'});self.selected['D01']='D01-F1';self.write();(self.source/'calls/D01-F1.json').write_text(json.dumps({'plan_sha256':b.sha(self.source/'plan.json'),'id':'D01','attempt_id':'D01-F1','retry_of':'D01-R1','retry_reason':'Texture finishing.'}));self.assertEqual(len(b.build()['entries'][0]['history']),3)
if __name__=='__main__':unittest.main()
