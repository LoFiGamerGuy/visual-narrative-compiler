"""Bounded fictional repaint matrix: denoise tradeoff for edit versus no-change."""
from __future__ import annotations
import hashlib,json,shutil,time,uuid
from datetime import UTC,datetime
from pathlib import Path
import requests
from PIL import Image,ImageChops,ImageStat
import illustrious_xl_v2_proxy_control as arm

ROOT=arm.ROOT; COMFY=arm.COMFY;HOST=arm.HOST; SEED=7803
SRC=ROOT/'experiments/outputs/blender_kitchen_control_bundle_v2/g07a-role-id-r1.png'; MASK=ROOT/'experiments/outputs/blender_kitchen_control_bundle_v2/g07a-right-token-context-mask-v2-comfy-alpha.png'
CN='xinsir_controlnet_union_sdxl_promax.safetensors'; OUT='illustrious_xl_v2_xinsir_repaint_replication_v1'; OUTDIR=ROOT/'experiments/outputs'/OUT; RECORDS=ROOT/'experiments/records'/OUT
CONFIGS=[{'id':'d100_s080','denoise':1.0,'strength':0.8}]
def sha(p):return arm.sha(p)
def stamp():return datetime.now(UTC).replace(microsecond=0).isoformat().replace('+00:00','Z')
def input_copy(path):
 dest=COMFY/'input/experiments'/path.parent.name/path.name;dest.parent.mkdir(parents=True,exist_ok=True)
 if not dest.exists():shutil.copy2(path,dest)
 if sha(dest)!=sha(path):raise RuntimeError('input copy hash mismatch')
 return f'experiments/{path.parent.name}/{path.name}'
def graph(image,mask,cfg,mode):
 pos=('Preserve the supplied reference exactly, including both tile colors, positions, table, camera, framing, occlusion, and background. Do not add, remove, recolor, move, restyle, or alter anything.' if mode=='nochange' else 'Edit only the right rectangular tile token from teal to green. Preserve the left orange rectangular tile, shared table, camera, framing, occlusion, background, and all other elements. No people, faces, children, text, extra tokens, or other changes.')
 neg='photorealistic, person, face, child, text, watermark, extra token, duplicate token, role swap, touching, changed camera, changed table placement'
 return {'1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':arm.CKPT}},'2':{'class_type':'CLIPTextEncode','inputs':{'text':pos,'clip':['1',1]}},'3':{'class_type':'CLIPTextEncode','inputs':{'text':neg,'clip':['1',1]}},'4':{'class_type':'LoadImage','inputs':{'image':image}},'5':{'class_type':'LoadImage','inputs':{'image':mask}},'6':{'class_type':'InpaintPreprocessor','inputs':{'image':['4',0],'mask':['5',1],'black_pixel_for_xinsir_cn':True}},'7':{'class_type':'ControlNetLoader','inputs':{'control_net_name':CN}},'8':{'class_type':'SetUnionControlNetType','inputs':{'control_net':['7',0],'type':'repaint'}},'9':{'class_type':'ControlNetApplyAdvanced','inputs':{'positive':['2',0],'negative':['3',0],'control_net':['8',0],'image':['6',0],'strength':cfg['strength'],'start_percent':0.0,'end_percent':1.0,'vae':['1',2]}},'10':{'class_type':'VAEEncodeForInpaint','inputs':{'pixels':['4',0],'vae':['1',2],'mask':['5',1],'grow_mask_by':6}},'11':{'class_type':'KSampler','inputs':{'seed':SEED,'steps':28,'cfg':5.0,'sampler_name':'euler','scheduler':'normal','denoise':cfg['denoise'],'model':['1',0],'positive':['9',0],'negative':['9',1],'latent_image':['10',0]}},'12':{'class_type':'VAEDecode','inputs':{'samples':['11',0],'vae':['1',2]}},'13':{'class_type':'SaveImage','inputs':{'images':['12',0],'filename_prefix':f"{OUT}/{cfg['id']}_{mode}_seed{SEED}"}}}
def frac(a,b,mask,inside):
 d=ImageChops.difference(a,b).convert('RGB');pix=d.load();mp=mask.load();n=c=0
 for y in range(a.height):
  for x in range(a.width):
   if (mp[x,y]>0)==inside:n+=1;c+=pix[x,y]!=(0,0,0)
 return c/n
def run(cfg,mode,image,mask):
 RECORDS.mkdir(parents=True,exist_ok=True);OUTDIR.mkdir(parents=True,exist_ok=True);rp=RECORDS/f"{cfg['id']}-{mode}-seed{SEED}.json"
 if rp.exists():return rp
 payload=graph(image,mask,cfg,mode);at=stamp();start=time.time();r=requests.post(f'{HOST}/prompt',json={'prompt':payload,'client_id':str(uuid.uuid4())},timeout=30);r.raise_for_status();pid=r.json()['prompt_id'];hist=None
 while time.time()-start<600:
  d=requests.get(f'{HOST}/history/{pid}',timeout=20).json()
  if pid in d:hist=d[pid];break
  time.sleep(1)
 if hist is None or hist['status']['status_str']!='success':raise RuntimeError(f'generation failed {pid}')
 item=hist['outputs']['13']['images'][0];raw=COMFY/'output'/item['subfolder']/item['filename'];source=Image.open(SRC).convert('RGB');m=Image.open(MASK).convert('L');generated=Image.open(raw).convert('RGB');comp=Image.composite(generated,source,m);out=OUTDIR/f"{cfg['id']}-{mode}-seed{SEED}-composite.png";comp.save(out);rd=ImageChops.difference(source,generated).convert('RGB');cd=ImageChops.difference(source,comp).convert('RGB')
 rec={'schema_version':'1.0','record_type':'NativeRepaintMatrixRecord','record_id':f"ng-xinsir-repaint-{cfg['id']}-{mode}-{SEED}",'state':'LOCAL_FICTIONAL_PROXY_RESEARCH_LICENSE_REVIEW_PENDING','semantic_source_sha256':arm.FROZEN,'variant':cfg,'mode':mode,'seed':SEED,'input_state':{'source':SRC.relative_to(ROOT).as_posix(),'source_sha256':sha(SRC),'mask':MASK.relative_to(ROOT).as_posix(),'mask_sha256':sha(MASK)},'workflow':{'prompt_id':pid,'graph':payload,'xinsir_mode':'repaint','post_composite':'exact exterior measurement'},'sources':{'checkpoint':{'path':(COMFY/'models/checkpoints'/arm.CKPT).relative_to(ROOT).as_posix(),'sha256':sha(COMFY/'models/checkpoints'/arm.CKPT)},'controlnet':{'path':'ComfyUI/models/controlnet/xinsir_controlnet_union_sdxl_promax.safetensors','sha256':sha(COMFY/'models/controlnet'/CN)},'adapter_source':{'path':Path(__file__).relative_to(ROOT).as_posix(),'sha256':sha(Path(__file__))},'profile':{'path':arm.PROFILE.relative_to(ROOT).as_posix(),'sha256':sha(arm.PROFILE)}},'started_at':at,'ended_at':stamp(),'generation_seconds':round(time.time()-start,3),'candidates':{'raw':{'path':raw.relative_to(ROOT).as_posix(),'sha256':sha(raw)},'composite':{'path':out.relative_to(ROOT).as_posix(),'sha256':sha(out)}},'measurements':{'raw_changed_inside_mask_fraction':frac(source,generated,m,True),'raw_changed_outside_mask_fraction':frac(source,generated,m,False),'composite_changed_inside_mask_fraction':frac(source,comp,m,True),'composite_changed_outside_mask_fraction':frac(source,comp,m,False),'raw_mean_abs_channel_difference':ImageStat.Stat(rd).mean,'composite_mean_abs_channel_difference':ImageStat.Stat(cd).mean},'human_review_status':'pending','human_minutes':None,'accepted_output':False,'cost':{'external_api_usd':0,'paid_service_used':False,'local_electricity':'unmeasured'},'limitations':['Fictional proxy only; no identity/final-art/benchmark/commercial claim.','Target semantic review is recorded separately.']};rp.write_text(json.dumps(rec,indent=2)+'\n');return rp
def main():
 arm.verify('G07a');image=input_copy(SRC);mask=input_copy(MASK)
 for cfg in CONFIGS:
  for mode in ('edit','nochange'):print(run(cfg,mode,image,mask))
if __name__=='__main__':main()
