from pathlib import Path
import json,hashlib,base64,datetime,collections
from PIL import Image
r=Path(__file__).resolve().parents[1];b=r.parents[3]
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
records=[json.loads(p.read_text()) for p in sorted((r/'calls').glob('*.json')) if not p.name.endswith('-tool-return.json')]
assert len(records)==19
assert all(x['status']=='returned' for x in records)
phases=collections.Counter(x['phase'] for x in records);assert phases=={'primary':11,'repair':8}
units=collections.defaultdict(list);check=[]
for x in records:
 aid=x['id'];units[aid.rsplit('-',1)[0]].append(x['phase'])
 assert x['args']==json.loads(Path(x['arguments_path']).read_text())
 assert x['args']['prompt']==(r/'requests'/f'{aid}.txt').read_text()
 assert hashlib.sha256(x['args']['prompt'].encode()).hexdigest()==x['prompt_sha256']
 for ref in x['references']:assert h(b/ref['path'])==ref['sha256']
 raw=json.loads(Path(x['raw_return_path']).read_text())
 original=Path(x['source_path']).read_bytes();native=Path(x['path']).read_bytes();decoded=base64.b64decode(raw['image_url'].split(',',1)[1])
 assert original==native==decoded and h(x['path'])==x['sha256']
 assert str(x['source_path']) in raw['output_hint']
 assert x['model_snapshot'] is None and x['seed'] is None and x['billing'] is None
 check.append({'id':aid,'phase':x['phase'],'submitted_utc':x['submitted_utc'],'returned_utc':x['returned_utc'],'native_sha256':x['sha256'],'default_native_raw_bytes_equal':True,'exact_args_prompt_refs_match':True})
for phases_for_unit in units.values():assert phases_for_unit.count('primary')==1 and phases_for_unit.count('repair')<=1
pids=[p for x in records if x['phase']=='primary' for p in x['panels']];assert sorted(pids)==[f'N8-{n:02d}' for n in range(15,33)]
sel=json.loads((r/'selected-records.json').read_text());assert len(sel)==18 and sorted(x['panel_id'] for x in sel)==sorted(pids)
crops=[]
for x in sel:
 c=x['crop'];source=b/c['source_path'];p=b/x['path'];assert h(source)==c['source_sha256'] and h(p)==x['sha256']
 im=Image.open(source);assert list(im.size)==c['source_dimensions']
 expected=im.crop(c['box_xyxy']).convert('RGBA');actual=Image.open(p).convert('RGBA');assert expected.size==actual.size and expected.tobytes()==actual.tobytes()
 crops.append({'panel_id':x['panel_id'],'path':x['path'],'sha256':x['sha256'],'source_sha256':c['source_sha256'],'box_xyxy':c['box_xyxy'],'exact_lossless_pixels':True})
assert h(b/'production/nightglass-longform/scripts/chapter-8.json')=='0a3d3a441efd5017d84347c2e5849c514f313a00f6bfdb0df898cd93ea1982fc'
assert h(b/'research/nightglass-longform/CHAPTER8-PRODUCTION-GATE.json')=='1eb2e36cfc6d334a8dcb05fbfda1acb861ad2023a2e88b102c4683dbf0456f6e'
checkpoint=b/'research/nightglass-longform/CHAPTER8-ORIGINAL320-CHECKPOINT.json';assert h(checkpoint)=='c26c6b9bb5d9fda761c549d5ce893de17af91ac3065eb5c9ccbfecbb3c549959'
result={'status':'PASS','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'N8-15 through N8-32 only','local_ceiling':24,'returned':19,'pending':0,'phase_counts':dict(phases),'unused_local_calls':5,'no_allowance_rollover_or_new_calls_authorized':True,'original_default_artifacts_retained':True,'raw_preservation':'Semantic image_url and output_hint JSON with native payload byte equality; JSON whitespace not asserted original tool transport','checkpoint_sha256':h(checkpoint),'records':check,'selected_derivatives':crops,'visual_gate_limit':'This verifies preservation/provenance, not full lettered chapter reading. Candid visual limitations are retained in selected-records and review notes.'}
(r/'notes/FINAL-PRESERVATION-CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','returned','pending','phase_counts','unused_local_calls']},indent=2))
