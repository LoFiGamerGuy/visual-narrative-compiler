"""Validate CH05 three-complete-chapter route comparison evidence."""
from __future__ import annotations
import argparse,copy,hashlib,json,subprocess
from pathlib import Path
from typing import Any
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];DOC=ROOT/"docs/research/evidence/ch05-three-route-comparison-r1.json"
def sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(d:dict[str,Any],files=True)->list[str]:
 e=[];c=lambda x,m:None if x else e.append(m);c(d.get("record_type")=="CH05CompleteChapterThreeRouteComparison" and d.get("state")=="ENGINEERING_SELECTION_PENDING_OWNER_REVIEW","identity/state");c(d.get("planning_structure")=="ComicPanelPlan" and d.get("animation_shot_plan") is None and d.get("e_conte") is None,"planning boundary");c(d.get("coverage")=={"routes":3,"comic_panel_plans_per_route":50,"paired_panel_ids":50,"total_panel_candidates_compared":150},"coverage");c(d.get("semantic_counts")=={"r6_supplemental":{"pass":47,"warn":1,"fail":2},"alt_graphic":{"pass":36,"warn":7,"fail":7},"clear_line_watercolor":{"pass":45,"warn":2,"fail":3}},"semantic counts");metrics=d.get("visual_complexity",{});c(set(metrics.get("aggregate_equal_panel_weight",{}))=={"r6","alt_graphic","clear_line_watercolor"} and len(metrics.get("per_panel",[]))==50,"metrics");c([x.get("route") for x in d.get("ranking",[])]==["r6_plus_cross_panel_gates","clear_line_watercolor","alt_graphic"],"ranking");rec=d.get("recommendation",{});c(rec.get("current_base")=="r6" and rec.get("leading_style_direction")=="clear_line_watercolor" and rec.get("appearance_only_selection") is False,"recommendation");c(d.get("spend")=={"direct_paid_api_cloud_usd":0.0,"built_in_product_monetary_cost_usd":None},"spend")
 if files:
  for s in d.get("inputs",[]):p=ROOT/s["path"];c(p.is_file() and sha256(p)==s["sha256"],f"input {s['path']}")
  for name,a in d.get("artifacts",{}).items():
   p=ROOT/a["path"];c(p.is_file() and sha256(p)==a["sha256"] and p.stat().st_size==a["bytes"],f"artifact {name}")
   if p.is_file():
    with Image.open(p) as im:c(im.format=="PNG" and [im.width,im.height]==[a["width"],a["height"]],f"decode {name}")
    c(subprocess.run(["git","check-ignore","--quiet","--",a["path"]],cwd=ROOT).returncode==0 and a.get("repository_state")=="IGNORED_LOCAL_REVIEW_ARTIFACT",f"ignored {name}")
 return e
def self_test(d):
 muts=[lambda x:x.__setitem__("state","ACCEPTED"),lambda x:x.__setitem__("planning_structure","AnimationShotPlan"),lambda x:x["coverage"].__setitem__("routes",2),lambda x:x["semantic_counts"]["clear_line_watercolor"].__setitem__("fail",0),lambda x:x["visual_complexity"]["per_panel"].pop(),lambda x:x["ranking"].reverse(),lambda x:x["recommendation"].__setitem__("current_base","alt_graphic"),lambda x:x["recommendation"].__setitem__("appearance_only_selection",True),lambda x:x["spend"].__setitem__("built_in_product_monetary_cost_usd",0.0)];n=0
 for m in muts:q=copy.deepcopy(d);m(q);n+=bool(validate(q,False))
 return n,len(muts)
def main():
 p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true");a=p.parse_args();d=json.loads(DOC.read_text(encoding="utf-8"));e=validate(d);n=t=0
 if a.self_test:n,t=self_test(d);e+=[] if n==t else [f"self-test {n}/{t}"]
 print(json.dumps({"status":"PASS" if not e else "FAIL","errors":e,"self_test":f"{n}/{t}" if a.self_test else None},sort_keys=True));return 0 if not e else 1
if __name__=="__main__":raise SystemExit(main())
