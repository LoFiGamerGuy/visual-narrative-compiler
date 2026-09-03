"""Validate clear-line watercolor CH05 triage."""
from __future__ import annotations
import argparse,copy,hashlib,json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[2];DOC=ROOT/"docs/research/evidence/ch05-complete-chapter-clear-line-watercolor-agent-triage-r1.json";PLAN=ROOT/"production/comic/ch05-sc01-panel-plans-v1.json"
def sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(d:dict[str,Any],files=True)->list[str]:
 e=[];c=lambda x,m:None if x else e.append(m);rows=d.get("rows",[]);ids=[x["panel_id"] for x in json.loads(PLAN.read_text(encoding="utf-8"))["plans"]]
 c(d.get("record_type")=="CH05CompleteChapterAgentTriage" and d.get("state")=="NON_GATING_AGENT_TRIAGE_PENDING_OWNER_REVIEW","identity/state");c(d.get("planning_structure")=="ComicPanelPlan" and d.get("animation_shot_plan") is None and d.get("e_conte") is None,"planning boundary");c(len(rows)==50 and [x.get("panel_id") for x in rows]==ids,"coverage");counts={s:sum(x.get("status")==s for x in rows) for s in ("PASS","WARN","FAIL")};c(counts=={"PASS":45,"WARN":2,"FAIL":3},"counts");c([x["display_order"] for x in rows if x["status"]=="FAIL"]==[1,39,43],"failure set");c(d.get("summary",{}).get("hair_and_wardrobe_pass")==50 and d.get("summary",{}).get("cross_panel_gates_pass")==5,"summary");c(d.get("style_hypothesis_result",{}).get("result")=="PARTIAL","style result");c(all(x.get("human_review_state")=="PENDING" and x.get("accepted") is False and x.get("commercially_cleared") is False and x.get("exact_production_base") is False for x in rows),"decision boundary")
 if files:
  for s in d.get("inputs",[]):p=ROOT/s["path"];c(p.is_file() and sha256(p)==s["sha256"],f"input {s['path']}")
 return e
def self_test(d):
 muts=[lambda x:x.__setitem__("state","ACCEPTED"),lambda x:x.__setitem__("planning_structure","AnimationShotPlan"),lambda x:x["rows"].pop(),lambda x:x["rows"][0].__setitem__("status","PASS"),lambda x:x["rows"][0].__setitem__("accepted",True),lambda x:x["summary"].__setitem__("hair_and_wardrobe_pass",49),lambda x:x["summary"].__setitem__("cross_panel_gates_pass",8),lambda x:x["style_hypothesis_result"].__setitem__("result","WIN")];n=0
 for m in muts:q=copy.deepcopy(d);m(q);n+=bool(validate(q,False))
 return n,len(muts)
def main():
 p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true");a=p.parse_args();d=json.loads(DOC.read_text(encoding="utf-8"));e=validate(d);n=t=0
 if a.self_test:n,t=self_test(d);e+=[] if n==t else [f"self-test {n}/{t}"]
 print(json.dumps({"status":"PASS" if not e else "FAIL","errors":e,"self_test":f"{n}/{t}" if a.self_test else None},sort_keys=True));return 0 if not e else 1
if __name__=="__main__":raise SystemExit(main())
