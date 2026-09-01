"""Native Xinsir repaint smoke for the fictional G07a teal-to-green edit."""
from __future__ import annotations
import hashlib,json,os,time,uuid
from datetime import UTC,datetime
from pathlib import Path
import requests
from PIL import Image,ImageChops,ImageStat
import illustrious_xl_v2_proxy_control as arm

ROOT=arm.ROOT; COMFY=arm.COMFY; HOST=arm.HOST
SRC=ROOT/'experiments/outputs/blender_kitchen_control_bundle_v2/g07a-role-id-r1.png'; MASK=ROOT/'experiments/outputs/blender_kitchen_control_bundle_v2/g07a-right-token-context-mask-v2-comfy-alpha.png'
OUT_DIR=ROOT/'experiments/outputs/illustrious_xl_v2_xinsir_repaint_proxy_edit_v1'; NO_CHANGE=os.getenv('NG_REPAIR_MODE')=='nochange'; RECORD=ROOT/f"experiments/records/illustrious_xl_v2_xinsir_repaint_proxy_edit_v1/g07a-seed-7704-maskv2-xinsirblack{'-nochange' if NO_CHANGE else ''}.json"; OUT='illustrious_xl_v2_xinsir_repaint_proxy_edit_v1'; CN='xinsir_controlnet_union_sdxl_promax.safetensors'
def sha(p): return arm.sha(p)
def stamp(): return datetime.now(UTC).replace(microsecond=0).isoformat().replace('+00:00','Z')
def graph(image_name,mask_name):
 pos=('Preserve the supplied reference exactly, including both tile colors, positions, table, camera, framing, occlusion, and background. Do not add, remove, recolor, move, restyle, or alter anything.' if NO_CHANGE else 'Edit only the right rectangular tile token from teal to green. Preserve the left orange rectangular tile, shared table, camera, framing, occlusion, background, and all other elements. No people, faces, children, text, extra tokens, or other changes.')
 neg='photorealistic, person, face, child, text, watermark, extra token, duplicate token, role swap, touching, changed camera, changed table placement'
 return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':arm.CKPT}},'2':{'class_type':'CLIPTextEncode','inputs':{'text':pos,'clip':['1',1]}},'3':{'class_type':'CLIPTextEncode','inputs':{'text':neg,'clip':['1',1]}},'4':{'class_type':'LoadImage','inputs':{'image':image_name}},'5':{'class_type':'LoadImage','inputs':{'image':mask_name}},'6':{'class_type':'InpaintPreprocessor','inputs':{'image':['4',0],'mask':['5',1],'black_pixel_for_xinsir_cn':False}},'7':{'class_type':'ControlNetLoader','inputs':{'control_net_name':CN}},'8':{'class_type':'SetUnionControlNetType','inputs':{'control_net':['7',0],'type':'repaint'}},'9':{'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['2',0],'negative':['3',0],'control_net':['8',0],'image':['6',0],'strength':0.8,'start_percent':0.0,'end_percent':1.0,'vae':['1',2]}},'10':{'class_type':'VAEEncodeForInpaint','inputs':{'pixels':['4',0],'vae':['1',2],'mask':['5',1],'grow_mask_by':6}},'11':{'class_type':'KSampler','inputs':{'seed':7704,'steps':28,'cfg':5.0,'sampler_name':'euler','scheduler':'normal','denoise':1.0,'model':['1',0],'positive':['9',0],'negative':['9',1],'latent_image':['10',0]}},'12':{'class_type':'VAEDecode','inputs':{'samples':['11',0],'vae':['1',2]}},'13':{'class_type':'SaveImage','inputs':{'images':['12',0],'filename_prefix':f'{OUT}/g07a_seed7704_raw'}}}
def frac(a,b,mask,inside):
 d=ImageChops.difference(a,b).convert('RGB'); pix=d.load();mp=mask.load();tot=chg=0
 for y in range(a.height):
  for x in range(a.width):
   if (mp[x,y]>0)==inside: tot+=1;chg+=pix[x,y]!=(0,0,0)
 return chg/tot
def main():
 arm.verify('G07a'); OUT_DIR.mkdir(parents=True,exist_ok=True);RECORD.parent.mkdir(parents=True,exist_ok=True)
 if RECORD.exists():print(RECORD);return
 image_name=arm.ensure_input('G07a'); mask_dest=COMFY/'input/experiments'/MASK.parent.name/MASK.name;mask_dest.parent.mkdir(parents=True,exist_ok=True);mask_dest.write_bytes(MASK.read_bytes()) if not mask_dest.exists() else None
 if sha(mask_dest)!=sha(MASK):raise RuntimeError('mask copy hash mismatch')
 payload=graph(image_name,f'experiments/{MASK.parent.name}/{MASK.name}');payload['6']['inputs']['black_pixel_for_xinsir_cn']=True;at=stamp();started=time.time();r=requests.post(f'{HOST}/prompt',json={'prompt':payload,'client_id':str(uuid.uuid4())},timeout=30);r.raise_for_status();pid=r.json()['prompt_id'];hist=None
 while time.time()-started<600:
  data=requests.get(f'{HOST}/history/{pid}',timeout=20).json()
  if pid in data:hist=data[pid];break
  time.sleep(1)
 if hist is None or hist['status']['status_str']!='success':raise RuntimeError(f'generation did not complete: {pid}')
 item=hist['outputs']['13']['images'][0];raw=COMFY/'output'/item['subfolder']/item['filename'];source=Image.open(SRC).convert('RGB');generated=Image.open(raw).convert('RGB');mask=Image.open(MASK).convert('L');comp=Image.composite(generated,source,mask);out=OUT_DIR/f"g07a-repaint-{'nochange' if NO_CHANGE else 'edit'}-{raw.stem}.png";comp.save(out)
 rawdiff=ImageChops.difference(source,generated).convert('RGB');compdiff=ImageChops.difference(source,comp).convert('RGB')
 rec={'schema_version':'1.0','record_type':'NativeRepaintControlRecord','record_id':f"ng-illustrious-xl-v2-xinsir-repaint-g07a-7704{'-nochange' if NO_CHANGE else ''}",'state':'LOCAL_FICTIONAL_PROXY_RESEARCH_LICENSE_REVIEW_PENDING','semantic_source_sha256':arm.FROZEN,'input_state':{'source':SRC.relative_to(ROOT).as_posix(),'source_sha256':sha(SRC),'mask':MASK.relative_to(ROOT).as_posix(),'mask_sha256':sha(MASK),'spatial_mode':'grounded_geometry_proxy_reference'},'requested_change':('preserve all visual content unchanged' if NO_CHANGE else 'right teal rectangular token to green; preserve all else'),'workflow':{'prompt_id':pid,'graph':payload,'xinsir_mode':'repaint','strength':0.8,'denoise':1.0,'post_composite':'for exact exterior measurement'},'sources':{'checkpoint':{'path':(COMFY/'models/checkpoints'/arm.CKPT).relative_to(ROOT).as_posix(),'sha256':sha(COMFY/'models/checkpoints'/arm.CKPT)},'controlnet':{'path':'ComfyUI/models/controlnet/xinsir_controlnet_union_sdxl_promax.safetensors','sha256':sha(COMFY/'models/controlnet'/CN)},'adapter_source':{'path':Path(__file__).relative_to(ROOT).as_posix(),'sha256':sha(Path(__file__))},'profile':{'path':arm.PROFILE.relative_to(ROOT).as_posix(),'sha256':sha(arm.PROFILE)}},'started_at':at,'ended_at':stamp(),'generation_seconds':round(time.time()-started,3),'candidates':{'native_repaint_raw':{'path':raw.relative_to(ROOT).as_posix(),'sha256':sha(raw)},'composited':{'path':out.relative_to(ROOT).as_posix(),'sha256':sha(out)}},'measurements':{'raw_changed_inside_mask_fraction':frac(source,generated,mask,True),'raw_changed_outside_mask_fraction':frac(source,generated,mask,False),'composite_changed_inside_mask_fraction':frac(source,comp,mask,True),'composite_changed_outside_mask_fraction':frac(source,comp,mask,False),'raw_mean_abs_channel_difference':ImageStat.Stat(rawdiff).mean,'composite_mean_abs_channel_difference':ImageStat.Stat(compdiff).mean},'human_review_status':'pending','human_minutes':None,'accepted_output':False,'cost':{'external_api_usd':0,'paid_service_used':False,'local_electricity':'unmeasured'},'limitations':['Fictional proxy only; no identity/final-art/benchmark/commercial claim.','Post-composite exact exterior preservation does not establish target semantics.']};RECORD.write_text(json.dumps(rec,indent=2)+'\n');print(RECORD)
if __name__=='__main__':main()
