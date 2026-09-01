"""One fictional, mask-limited repair control for the pinned Illustrious XL v2 arm."""
from __future__ import annotations
import hashlib,json,time,uuid
from datetime import UTC,datetime
from pathlib import Path
import requests
from PIL import Image,ImageChops,ImageStat
import illustrious_xl_v2_proxy_control as arm

ROOT=arm.ROOT; COMFY=arm.COMFY; HOST=arm.HOST
SRC=ROOT/'experiments/outputs/blender_kitchen_control_bundle_v2/g07a-role-id-r1.png'
MASK=ROOT/'experiments/outputs/blender_kitchen_control_bundle_v2/g07a-right-token-context-mask-v1.png'
OUT_DIR=ROOT/'experiments/outputs/illustrious_xl_v2_masked_proxy_edit_v1'
RECORD=ROOT/'experiments/records/illustrious_xl_v2_masked_proxy_edit_v1/g07a-seed-7703.json'
OUT='illustrious_xl_v2_masked_proxy_edit_v1'
def sha(p): return arm.sha(p)
def stamp(): return datetime.now(UTC).replace(microsecond=0).isoformat().replace('+00:00','Z')
def graph(image_name):
 pos=('Edit only the right rectangular tile token from teal to green. Preserve the left orange rectangular tile, their shared table, camera, framing, occlusion, background, and all other elements. No people, faces, children, text, extra tokens, or other changes.')
 neg='photorealistic, person, face, child, text, watermark, extra token, duplicate token, role swap, touching, changed camera, changed table placement'
 return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':arm.CKPT}},'2':{'class_type':'CLIPTextEncode','inputs':{'text':pos,'clip':['1',1]}},'3':{'class_type':'CLIPTextEncode','inputs':{'text':neg,'clip':['1',1]}},'4':{'class_type':'LoadImage','inputs':{'image':image_name}},'5':{'class_type':'VAEEncode','inputs':{'pixels':['4',0],'vae':['1',2]}},'6':{'class_type':'KSampler','inputs':{'seed':7703,'steps':28,'cfg':5.0,'sampler_name':'euler','scheduler':'normal','denoise':0.65,'model':['1',0],'positive':['2',0],'negative':['3',0],'latent_image':['5',0]}},'7':{'class_type':'VAEDecode','inputs':{'samples':['6',0],'vae':['1',2]}},'8':{'class_type':'SaveImage','inputs':{'images':['7',0],'filename_prefix':f'{OUT}/g07a_seed7703_raw'}}}
def fraction_changed(a,b,mask,inside):
 d=ImageChops.difference(a,b).convert('RGB'); pix=d.load(); mp=mask.load(); total=changed=0
 for y in range(a.height):
  for x in range(a.width):
   selected=(mp[x,y]>0) if inside else (mp[x,y]==0)
   if selected:
    total+=1; changed+=pix[x,y]!=(0,0,0)
 return changed/total if total else None
def main():
 arm.verify('G07a'); OUT_DIR.mkdir(parents=True,exist_ok=True); RECORD.parent.mkdir(parents=True,exist_ok=True)
 if RECORD.exists(): print(RECORD);return
 image_name=arm.ensure_input('G07a'); payload=graph(image_name); at=stamp(); started=time.time()
 r=requests.post(f'{HOST}/prompt',json={'prompt':payload,'client_id':str(uuid.uuid4())},timeout=30);r.raise_for_status(); pid=r.json()['prompt_id']; hist=None
 while time.time()-started<600:
  data=requests.get(f'{HOST}/history/{pid}',timeout=20).json()
  if pid in data: hist=data[pid];break
  time.sleep(1)
 if hist is None or hist['status']['status_str']!='success': raise RuntimeError(f'generation did not complete: {pid}')
 item=hist['outputs']['8']['images'][0]; raw=COMFY/'output'/item['subfolder']/item['filename']
 source=Image.open(SRC).convert('RGB'); generated=Image.open(raw).convert('RGB'); mask=Image.open(MASK).convert('L')
 composite=Image.composite(generated,source,mask); out=OUT_DIR/'g07a-right-teal-to-green-composited-r1.png'; composite.save(out)
 raw_diff=ImageChops.difference(source,generated).convert('RGB'); comp_diff=ImageChops.difference(source,composite).convert('RGB')
 record={'schema_version':'1.0','record_type':'MaskedRepairControlRecord','record_id':'ng-illustrious-xl-v2-masked-proxy-g07a-7703','state':'LOCAL_FICTIONAL_PROXY_RESEARCH_LICENSE_REVIEW_PENDING','semantic_source_sha256':arm.FROZEN,'input_state':{'source':SRC.relative_to(ROOT).as_posix(),'source_sha256':sha(SRC),'mask':MASK.relative_to(ROOT).as_posix(),'mask_sha256':sha(MASK),'spatial_mode':'grounded_geometry_proxy_reference'},'requested_change':'right teal rectangular token to green; preserve all else','workflow':{'prompt_id':pid,'graph':payload,'steps':28,'cfg':5.0,'sampler':'euler','denoise':0.65,'mask_application':'deterministic post-render composite; raw renderer is not mask-constrained'},'sources':{'checkpoint':{'path':(COMFY/'models/checkpoints'/arm.CKPT).relative_to(ROOT).as_posix(),'sha256':sha(COMFY/'models/checkpoints'/arm.CKPT)},'adapter_source':{'path':Path(__file__).relative_to(ROOT).as_posix(),'sha256':sha(Path(__file__))},'profile':{'path':arm.PROFILE.relative_to(ROOT).as_posix(),'sha256':sha(arm.PROFILE)}},'started_at':at,'ended_at':stamp(),'generation_seconds':round(time.time()-started,3),'candidates':{'raw_renderer':{'path':raw.relative_to(ROOT).as_posix(),'sha256':sha(raw)},'masked_composite':{'path':out.relative_to(ROOT).as_posix(),'sha256':sha(out)}},'measurements':{'raw_changed_pixel_fraction':fraction_changed(source,generated,Image.new('L',source.size,255),True),'composite_changed_inside_mask_fraction':fraction_changed(source,composite,mask,True),'composite_changed_outside_mask_fraction':fraction_changed(source,composite,mask,False),'raw_mean_abs_channel_difference':ImageStat.Stat(raw_diff).mean,'composite_mean_abs_channel_difference':ImageStat.Stat(comp_diff).mean},'human_review_status':'pending','human_minutes':None,'accepted_output':False,'cost':{'external_api_usd':0,'paid_service_used':False,'local_electricity':'unmeasured'},'limitations':['Post-render masking guarantees only exterior preservation, not semantic success inside the mask.','Fictional proxy only; no identity, adult likeness, final-art, benchmark, or commercial claim.']}
 RECORD.write_text(json.dumps(record,indent=2)+'\n');print(RECORD)
if __name__=='__main__':main()
