"""Validate clear-line watercolor crop manifest and split report."""
from __future__ import annotations
import argparse,copy,hashlib,json
from pathlib import Path
from typing import Any
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];MANIFEST=ROOT/"production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-crops-r1.json";REPORT=ROOT/"experiments/review-packets/ch05-complete-chapter-clear-line-watercolor-r1/panels/panel-split-report.json";PLANS=ROOT/"production/comic/ch05-sc01-panel-plans-v1.json"
def sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(d:dict[str,Any],report:dict[str,Any]|None,files=True)->list[str]:
 e=[];c=lambda x,m:None if x else e.append(m);seqs=d.get("sequences",[]);crops=[x for s in seqs for x in s.get("crops",[])];ids=[x["panel_id"] for x in json.loads(PLANS.read_text(encoding="utf-8"))["plans"]]
 c(d.get("record_type")=="CH05SequenceStripCropManifest","record_type");c(d.get("planning_structure")=="ComicPanelPlan" and d.get("animation_shot_plan") is None and d.get("e_conte") is None,"planning boundary");c(d.get("output_filename_template")=="p{panel_number:03d}-clear-line-watercolor-r1.png","template");c(len(seqs)==11 and [len(s["crops"]) for s in seqs]==[5,4,5,5,5,5,5,5,5,3,3] and [x["panel_id"] for x in crops]==ids,"coverage")
 for s in seqs:
  boxes=[x["box"] for x in s["crops"]];c(len(s["gutter_detection"]["detected_internal_gutter_extents_inclusive"])==len(boxes)-1,"gutters");c(all(len(b)==4 and all(isinstance(v,int) for v in b) and b[0]>=0 and b[1]>=0 and b[0]<b[2]<=s["source"]["width"] and b[1]<b[3]<=s["source"]["height"] for b in boxes),"bounds");c(all(boxes[i][3]<=boxes[i+1][1] for i in range(len(boxes)-1)),"monotonic")
  if files:
   p=ROOT/s["source"]["path"];c(p.is_file() and sha256(p)==s["source"]["sha256"],"source binding")
 if report:
  c(report.get("summary")=={"sequence_sources":11,"panels_produced":50,"complete_plan_coverage":True,"source_hashes_verified":11,"crop_bounds_verified":50},"report summary");outs=[x["output"] for x in report.get("panels",[])];c(len(outs)==50,"output count")
  if files:
   for n,(crop,o) in enumerate(zip(crops,outs,strict=True),1):
    p=ROOT/o["path"];box=crop["box"];c(Path(o["path"]).name==f"p{n:03d}-clear-line-watercolor-r1.png" and p.is_file() and sha256(p)==o["sha256"] and [o["width"],o["height"]]==[box[2]-box[0],box[3]-box[1]],f"crop output {n}")
    if p.is_file():
     with Image.open(p) as im:c(im.format=="PNG" and [im.width,im.height]==[o["width"],o["height"]],f"decode {n}")
 return e
def self_test(d):
 muts=[lambda x:x.__setitem__("planning_structure","AnimationShotPlan"),lambda x:x["sequences"].pop(),lambda x:x["sequences"][0]["crops"].pop(),lambda x:x["sequences"][0]["crops"][0].__setitem__("panel_id","bad"),lambda x:x["sequences"][0]["crops"][0].__setitem__("box",[0,2,1,1]),lambda x:x["sequences"][0]["gutter_detection"]["detected_internal_gutter_extents_inclusive"].pop(),lambda x:x.__setitem__("output_filename_template","bad.png")];n=0
 for m in muts:q=copy.deepcopy(d);m(q);n+=bool(validate(q,None,False))
 return n,len(muts)
def main():
 p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true");a=p.parse_args();d=json.loads(MANIFEST.read_text(encoding="utf-8"));r=json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.is_file() else None;e=validate(d,r);n=t=0
 if a.self_test:n,t=self_test(d);e+=[] if n==t else [f"self-test {n}/{t}"]
 print(json.dumps({"status":"PASS" if not e else "FAIL","errors":e,"report_present":r is not None,"self_test":f"{n}/{t}" if a.self_test else None},sort_keys=True));return 0 if not e else 1
if __name__=="__main__":raise SystemExit(main())
