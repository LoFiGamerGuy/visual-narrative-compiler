"""Run a small, pinned Illustrious XL v2 local proxy control without altering frozen semantics."""
from __future__ import annotations
import argparse, hashlib, json, shutil, time, uuid
from datetime import UTC, datetime
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[2]
COMFY=ROOT/'ComfyUI'; HOST='http://127.0.0.1:8188'
GAUNTLET=ROOT/'research/authoritative/v2.1.1/bench/gauntlet.json'; FROZEN='f826b0f1d06ed5a999667bde23ba0d04f8ebb22f516095034dab62c7541ae9ae'
STAGES=ROOT/'experiments/outputs/blender_kitchen_control_bundle_v2'
RECORDS=ROOT/'experiments/records/illustrious_xl_v2_blender_kitchen_g07_v1'; OUT='illustrious_xl_v2_blender_kitchen_g07_v1'
PROFILE=ROOT/'experiments/render-profiles/illustrious-xl-v2-local-r1.json'; MANIFEST=ROOT/'manifests/experiments/illustrious-xl-v2-blender-kitchen-g07-r1.json'
CKPT='illustrious-xl-v2.0\\Illustrious-XL-v2.0.safetensors'
CASES={'G07a':{'reference':'g07a-role-id-r1.png','left':'orange rectangular tile','right':'teal rectangular tile'},'G07b':{'reference':'g07b-role-id-r1.png','left':'teal rectangular tile','right':'orange rectangular tile'}}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()
def stamp(): return datetime.now(UTC).replace(microsecond=0).isoformat().replace('+00:00','Z')
def verify(case):
 if sha(GAUNTLET)!=FROZEN: raise RuntimeError('frozen gauntlet hash differs; refusing execution')
 c={x['id']:x for x in json.loads(GAUNTLET.read_text())['render_cases']}[case]
 expected=('SOREN','SIGRID') if case=='G07a' else ('SIGRID','SOREN')
 if c['spatial_mode']!='grounded' or tuple(c['manifest']['layout'][s] for s in ('left','right'))!=expected: raise RuntimeError('unexpected G07 semantics')
def ensure_input(case):
 src=STAGES/CASES[case]['reference']; dst=COMFY/'input/experiments'/STAGES.name/src.name; dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists(): shutil.copy2(src,dst)
 if sha(src)!=sha(dst): raise RuntimeError('reference copy hash mismatch')
 return f'experiments/{STAGES.name}/{src.name}'
def graph(case,seed,image_name,no_change):
 layout=CASES[case]
 pos=("Preserve the supplied reference control exactly: retain its two abstract rectangular tokens, their left/right color order, common table, camera, framing, occlusion, background, and every visual element. Do not add, remove, move, recolor, restyle, or alter anything." if no_change else f"Draw a clean comic-style kitchen control panel using the reference composition. Show exactly two abstract rectangular tile tokens: {layout['left']} on the left and {layout['right']} on the right, seated at one shared table without touching. Preserve the camera, table occlusion, and left/right order. No people, faces, children, text, or extra tokens.")
 neg='photorealistic, person, face, child, text, watermark, extra token, duplicate token, role swap, touching, changed camera, changed table placement'
 suffix='-nochange' if no_change else ''
 return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':CKPT}},'2':{'class_type':'CLIPTextEncode','inputs':{'text':pos,'clip':['1',1]}},'3':{'class_type':'CLIPTextEncode','inputs':{'text':neg,'clip':['1',1]}},'4':{'class_type':'LoadImage','inputs':{'image':image_name}},'5':{'class_type':'VAEEncode','inputs':{'pixels':['4',0],'vae':['1',2]}},'6':{'class_type':'KSampler','inputs':{'seed':seed,'steps':28,'cfg':5.0,'sampler_name':'euler','scheduler':'normal','denoise':0.65,'model':['1',0],'positive':['2',0],'negative':['3',0],'latent_image':['5',0]}},'7':{'class_type':'VAEDecode','inputs':{'samples':['6',0],'vae':['1',2]}},'8':{'class_type':'SaveImage','inputs':{'images':['7',0],'filename_prefix':f'{OUT}/{case.lower()}_seed{seed}{suffix}'}}}
def run(case,seed,no_change=False):
 verify(case); RECORDS.mkdir(parents=True,exist_ok=True); suffix='-nochange' if no_change else ''
 record_path=RECORDS/f'{case.lower()}-seed-{seed}{suffix}.json'
 if record_path.exists(): return record_path
 image=ensure_input(case); payload=graph(case,seed,image,no_change); at=stamp(); started=time.time()
 response=requests.post(f'{HOST}/prompt',json={'prompt':payload,'client_id':str(uuid.uuid4())},timeout=30); response.raise_for_status(); prompt_id=response.json()['prompt_id']; history=None
 while time.time()-started<600:
  found=requests.get(f'{HOST}/history/{prompt_id}',timeout=20).json()
  if prompt_id in found: history=found[prompt_id];break
  time.sleep(1)
 if history is None or history['status']['status_str']!='success': raise RuntimeError(f'generation did not complete: {prompt_id}')
 item=history['outputs']['8']['images'][0]; candidate=COMFY/'output'/item['subfolder']/item['filename']
 record={'schema_version':'1.0','record_type':'RenderRecord','record_id':f'ng-illustrious-xl-v2-{case.lower()}-{seed}{suffix}','state':'LOCAL_FICTIONAL_PROXY_RESEARCH_LICENSE_REVIEW_PENDING','case_id':case,'seed':seed,'semantic_source_sha256':FROZEN,'input_state':{'spatial_mode':'grounded_geometry_proxy_reference','stage_reference':image,'proxy_layout':CASES[case],'control_type':'renderer_no_change' if no_change else 'paired_composition'},'workflow':{'prompt_id':prompt_id,'graph':payload,'steps':28,'sampler':'euler','cfg':5.0,'denoise':0.65},'sources':{'checkpoint':{'path':(COMFY/'models/checkpoints'/CKPT).relative_to(ROOT).as_posix(),'sha256':sha(COMFY/'models/checkpoints'/CKPT)},'adapter_source':{'path':Path(__file__).relative_to(ROOT).as_posix(),'sha256':sha(Path(__file__))},'profile':{'path':PROFILE.relative_to(ROOT).as_posix(),'sha256':sha(PROFILE)},'manifest':{'path':MANIFEST.relative_to(ROOT).as_posix(),'sha256':sha(MANIFEST)}},'started_at':at,'ended_at':stamp(),'generation_seconds':round(time.time()-started,3),'candidate':{'path':candidate.relative_to(ROOT).as_posix(),'sha256':sha(candidate)},'hard_assertion_manifest':({'reference_visual_preservation':'required'} if no_change else {'exactly_two_tokens':'required','role_order':'required','common_table_non_touching':'required','kitchen_proxy':'required'}),'human_review_status':'pending','human_minutes':None,'accepted_output':False,'cost':{'external_api_usd':0,'paid_service_used':False,'local_electricity':'unmeasured'},'limitations':['Fictional proxy only; no identity or production-grounding claim.','No commercial claim; declared license requires separate intended-use review.','Agent or human review must be recorded separately.']}
 record_path.write_text(json.dumps(record,indent=2)+'\n'); return record_path
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('--case',choices=sorted(CASES),required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--no-change',action='store_true');a=p.parse_args();print(run(a.case,a.seed,a.no_change))
