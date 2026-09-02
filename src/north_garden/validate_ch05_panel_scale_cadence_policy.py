"""Validate the 50-plan conditional CH05 panel-scale/cadence policy."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-panel-scale-cadence-policy-r1.json";POLICY=ROOT/"production/comic/layout/ch05-panel-scale-cadence-policy-r1.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 s=d.get("summary",{});a=d.get("activity",{});out=[]
 if tuple(s.get(k) for k in ("plan_count","selected_evidence_count","rule_count","minimum_width_px","maximum_width_px","explicit_dialogue_plan_count"))!=(50,14,9,520,1200,1):out.append("policy denominators invalid")
 if any(s.get(k)!=0 for k in ("final_copy_bound_count","layout_accepted_count","comic_panel_plan_revisions","provider_calls","uploads","external_cost_usd")) or s.get("human_review_minutes") is not None:out.append("summary activity fabricated")
 if any(a.get(k)!=0 for k in ("plans_revised","layouts_accepted","copy_bound","provider_calls","uploads","external_cost_usd")):out.append("activity fabricated")
 return out
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));p=json.loads(POLICY.read_text(encoding="utf-8"));fail=errors(d)
 if d["policy"]["sha256"]!=sha(POLICY) or len(p["rows"])!=50 or len(p["rules"])!=9:fail.append("policy binding/rows invalid")
 if p["animation_shot_plan"] is not None or p["e_conte"] is not None or any(r["layout_accepted"] or r["final_copy_bound"] or r["comic_panel_plan_revision_created"] for r in p["rows"]):fail.append("planning/promotion boundary invalid")
 chart=ROOT/d["chart"]["path"]
 if not chart.is_file() or sha(chart)!=d["chart"]["sha256"]:fail.append("chart binding invalid")
 elif subprocess.run(["git","check-ignore","-q",str(chart)],cwd=ROOT,check=False).returncode:fail.append("chart not ignored")
 mutations=[lambda x:x["summary"].update(plan_count=49),lambda x:x["summary"].update(selected_evidence_count=13),lambda x:x["summary"].update(rule_count=8),lambda x:x["summary"].update(minimum_width_px=519),lambda x:x["summary"].update(maximum_width_px=1199),lambda x:x["summary"].update(explicit_dialogue_plan_count=0),lambda x:x["summary"].update(final_copy_bound_count=1),lambda x:x["summary"].update(layout_accepted_count=1),lambda x:x["summary"].update(comic_panel_plan_revisions=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(external_cost_usd=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x["activity"].update(plans_revised=1),lambda x:x["activity"].update(layouts_accepted=1),lambda x:x["activity"].update(copy_bound=1),lambda x:x["activity"].update(provider_calls=1),lambda x:x["activity"].update(uploads=1),lambda x:x["activity"].update(external_cost_usd=1)]
 rejected=0
 for mutation in mutations:y=copy.deepcopy(d);mutation(y);rejected+=bool(errors(y))
 if rejected!=len(mutations):fail.append(f"only {rejected}/{len(mutations)} mutations rejected")
 print(f"CH05 panel-scale/cadence policy: {len(fail)} failures; 50 plans/9 roles/520–1200px; {rejected}/{len(mutations)} mutations rejected")
 print("14 selected evidence rows; 1 explicit-dialogue plan; 0 copy/layout/plan revision/provider/upload/$0")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
