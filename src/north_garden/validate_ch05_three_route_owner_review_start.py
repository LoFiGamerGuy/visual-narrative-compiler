"""Validate CH05 three-route owner review navigation."""
from __future__ import annotations
import argparse,copy,hashlib,json,subprocess
from pathlib import Path
from typing import Any
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];DOC=ROOT/"docs/research/evidence/ch05-three-route-owner-review-start-r1.json"
def sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(d:dict[str,Any],files=True)->list[str]:
 e=[];c=lambda x,m:None if x else e.append(m);s=d.get("summary",{});c(d.get("record_type")=="CH05ThreeRouteOwnerReviewStart" and d.get("state")=="OWNER_REVIEW_READY_NO_DECISIONS_RECORDED","identity/state");c(d.get("planning_structure")=="ComicPanelPlan" and d.get("animation_shot_plan") is None and d.get("e_conte") is None,"planning boundary");c((s.get("complete_chapter_routes"),s.get("panels_per_route"),s.get("new_complete_chapter_arms"),s.get("new_sequence_outputs"),s.get("new_panel_crops"),s.get("review_artifacts"),s.get("strong_clear_line_candidates"))==(3,50,2,22,100,13,12),"counts");c(s.get("clear_line_triage")=={"pass":45,"warn":2,"fail":3},"triage");c(all(s.get(k)==0 for k in ("human_reviewed","accepted","commercially_cleared","exact_production_base")) and s.get("built_in_product_cost_usd") is None,"decisions/cost");c(len(d.get("review_order",[]))==7 and len(d.get("artifacts",[]))==13 and len(d.get("strongest_clear_line_candidates",[]))==12,"collections");c(all(v is None for v in d.get("owner_decisions",{}).values()),"owner decisions")
 if files:
  for x in d.get("inputs",[]):p=ROOT/x["path"];c(p.is_file() and sha256(p)==x["sha256"],f"input {x['path']}")
  for x in d.get("artifacts",[])+d.get("strongest_clear_line_candidates",[]):
   p=ROOT/x["path"];c(p.is_file() and sha256(p)==x["sha256"] and p.stat().st_size==x["bytes"],f"artifact {x['path']}")
   if p.is_file():
    with Image.open(p) as im:c(im.format=="PNG" and [im.width,im.height]==[x["width"],x["height"]],f"decode {x['path']}")
    c(subprocess.run(["git","check-ignore","--quiet","--",x["path"]],cwd=ROOT).returncode==0,f"ignored {x['path']}")
 return e
def self_test(d):
 muts=[lambda x:x.__setitem__("state","ACCEPTED"),lambda x:x.__setitem__("planning_structure","AnimationShotPlan"),lambda x:x["summary"].__setitem__("new_panel_crops",50),lambda x:x["summary"]["clear_line_triage"].__setitem__("fail",0),lambda x:x["summary"].__setitem__("accepted",1),lambda x:x["artifacts"].pop(),lambda x:x["strongest_clear_line_candidates"].pop(),lambda x:x["owner_decisions"].__setitem__("visual_dispositions",[])];n=0
 for m in muts:q=copy.deepcopy(d);m(q);n+=bool(validate(q,False))
 return n,len(muts)
def main():
 p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true");a=p.parse_args();d=json.loads(DOC.read_text(encoding="utf-8"));e=validate(d);n=t=0
 if a.self_test:n,t=self_test(d);e+=[] if n==t else [f"self-test {n}/{t}"]
 print(json.dumps({"status":"PASS" if not e else "FAIL","errors":e,"self_test":f"{n}/{t}" if a.self_test else None},sort_keys=True));return 0 if not e else 1
if __name__=="__main__":raise SystemExit(main())
