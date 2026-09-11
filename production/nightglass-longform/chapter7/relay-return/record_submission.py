from pathlib import Path
import json,hashlib,datetime,sys
r=Path(__file__).parent
workspace=r.parents[3]
gate_path=workspace/'research/nightglass-longform/CHAPTER7-PRODUCTION-GATE.json'
gate=json.loads(gate_path.read_text())
script_path=workspace/gate['script_path']
script_sha=hashlib.sha256(script_path.read_bytes()).hexdigest()
assert script_sha==gate['script_sha256'],'Authoritative script must match current production gate'
call_id,kind=sys.argv[1:]
target=r/'calls'/f'{call_id}.json'
assert not target.exists(),'Never overwrite a submitted attempt'
existing=[]
for p in (r/'calls').glob('*.json'):
 x=json.loads(p.read_text())
 if 'attempt_id' in x:existing.append(x)
assert len(existing)<18,'Worker ceiling includes every submission/failure'
assert kind in ('primary','structural_repair'),'No automatic finishing/support calls authorized by preparation'
assert call_id.endswith('-P' if kind=='primary' else '-R1'),'Original unit permits one P and at most one R1'
a=json.loads((r/'requests'/f'{call_id}.json').read_text())
assert a.get('referenced_image_paths'),'Actually viewed selected references required'
x={'attempt_id':call_id,'kind':kind,'status':'submitted','tool':'image_gen.imagegen','submitted_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'args':a,'references':[{'path':p,'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p in a['referenced_image_paths']],'model_snapshot':None,'seed':None,'billing':None}
x['authoritative_script']={'path':gate['script_path'],'sha256':script_sha}
x['production_gate']={'path':str(gate_path.relative_to(workspace)),'sha256':hashlib.sha256(gate_path.read_bytes()).hexdigest(),'worker_ceiling':gate['scope_ceilings']['relay-return'],'caps_reset':False}
target.write_text(json.dumps(x,indent=2))
