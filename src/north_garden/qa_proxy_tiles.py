"""Deterministic color-tile QA for fictional geometry proxy controls only."""
from __future__ import annotations
import argparse, json
from collections import deque
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
IN=ROOT/'ComfyUI/output/flux2_klein_geometry_tile_proxy_v1'
OUT=ROOT/'experiments/results/flux2_klein_geometry_tile_proxy_qa_20260901.json'
EXPECTED={'g07a':('orange','teal'),'g07b':('teal','orange')}

def mask_for(rgb, color):
 r,g,b=(rgb[...,i] for i in range(3))
 if color=='orange': m=(r>170)&(g>55)&(g<205)&(b<100)&((r-g)>35)
 else: m=(r<100)&(g>85)&(b>85)&((g-r)>30)
 # Connect a diagnostic marker across its intentional white diagonal highlight.
 return np.asarray(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.MaxFilter(15)))>0

def components(mask):
 h,w=mask.shape; seen=np.zeros_like(mask,bool); out=[]
 for y,x in zip(*np.where(mask)):
  if seen[y,x]: continue
  q=deque([(int(y),int(x))]); seen[y,x]=True; pts=[]
  while q:
   yy,xx=q.popleft(); pts.append((yy,xx))
   for dy,dx in ((0,1),(0,-1),(1,0),(-1,0)):
    ny,nx=yy+dy,xx+dx
    if 0<=ny<h and 0<=nx<w and mask[ny,nx] and not seen[ny,nx]: seen[ny,nx]=True;q.append((ny,nx))
  if len(pts)>=400:
   a=np.asarray(pts); out.append({'pixels':len(pts),'centroid_xy':[round(float(a[:,1].mean()),2),round(float(a[:,0].mean()),2)],'bbox_xyxy':[int(a[:,1].min()),int(a[:,0].min()),int(a[:,1].max()),int(a[:,0].max())]})
 return out

def roi(mask, side):
 h,w=mask.shape; out=np.zeros_like(mask); x0,x1=((260,500) if side=='left' else (720,980)); out[370:640,x0:x1]=mask[370:640,x0:x1]; return out

def assess(path):
 rgb=np.asarray(Image.open(path).convert('RGB')); key=path.name[:4]
 raw_orange=mask_for(rgb,'orange'); raw_teal=mask_for(rgb,'teal')
 expected_left,expected_right=EXPECTED[key]
 orange=components(roi(raw_orange, 'left' if expected_left=='orange' else 'right'))
 teal=components(roi(raw_teal, 'left' if expected_left=='teal' else 'right'))
 one_each=len(orange)==len(teal)==1
 centres={'orange':orange[0]['centroid_xy'][0] if len(orange)==1 else None,'teal':teal[0]['centroid_xy'][0] if len(teal)==1 else None}
 order=one_each and centres[expected_left] < centres[expected_right]
 return {'candidate':str(path.relative_to(ROOT)).replace('\\','/'),'expected_left':expected_left,'expected_right':expected_right,'components':{'orange':orange,'teal':teal},'assertions':{'one_orange_component': 'pass' if len(orange)==1 else 'fail','one_teal_component':'pass' if len(teal)==1 else 'fail','left_right_order':'pass' if order else 'fail'},'proxy_qa_pass':bool(one_each and order)}

def main():
 parser=argparse.ArgumentParser(); parser.add_argument('--input-dir',type=Path,default=IN); parser.add_argument('--output',type=Path,default=OUT); args=parser.parse_args()
 args.input_dir=args.input_dir.resolve(); args.output=args.output.resolve()
 runs=[assess(p) for p in sorted(args.input_dir.glob('*.png'))]
 payload={'record_type':'DeterministicProxyTileQA','state':'NON_GATING_PROXY_SENSOR_ONLY','method':{'orange_rule':'r>170, 55<g<205, b<100, r-g>35','teal_rule':'r<100, g>85, b>85, g-r>30','roi':'expected marker side x=260..500 or 720..980, y=370..640, derived from fixed proxy-stage anchors','morphology':'15px max-filter then 4-connected components, min 400 pixels'},'runs':runs,'measurements':{'runs':len(runs),'passes':sum(x['proxy_qa_pass'] for x in runs)},'limitations':['Color-coded fictional tiles only; cannot evaluate real identity, pose, set semantics, or production quality.','This deterministic sensor is non-gating until calibrated with control/injection data.']}
 args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(payload,indent=2)+'\n');print(args.output)
if __name__=='__main__':main()
