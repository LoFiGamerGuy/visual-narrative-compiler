"""Validate CH05 failure/repair matrix and zero-execution next experiment."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-failure-class-repair-matrix-r1.json";MATRIX=ROOT/"production/comic/review/ch05-failure-class-repair-matrix-r1.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 s=d.get("summary",{});a=d.get("activity",{});out=[]
 if tuple(s.get(k) for k in ("candidate_count","engineering_pass","engineering_warn","engineering_fail","nonpass_candidate_count","repair_link_count","repair_all_dimension_pass_count","repair_target_fixed_count"))!=(26,17,3,6,9,6,4,5):out.append("candidate/repair denominators invalid")
 if tuple(s.get(k) for k in ("next_plan_count","next_initial_candidates","next_maximum_candidates","next_prompt_count"))!=(4,4,6,0):out.append("next-experiment denominator invalid")
 if any(s.get(k)!=0 for k in ("plans_revised","provider_calls","uploads","external_cost_usd")) or s.get("human_review_minutes") is not None:out.append("summary activity fabricated")
 if any(a.get(k)!=0 for k in ("prompts","renders","provider_calls","uploads","plans_revised","acceptances","external_cost_usd")):out.append("activity fabricated")
 return out
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));m=json.loads(MATRIX.read_text(encoding="utf-8"));fail=errors(d)
 if d["matrix"]["sha256"]!=sha(MATRIX) or len(m["repair_links"])!=6 or len(m["next_experiment"]["comic_panel_plan_ids"])!=4:fail.append("matrix binding/content invalid")
 if m["animation_shot_plan"] is not None or m["e_conte"] is not None or m["next_experiment"]["prompt_count"]!=0:fail.append("planning/execution boundary invalid")
 chart=ROOT/d["chart"]["path"]
 if not chart.is_file() or sha(chart)!=d["chart"]["sha256"]:fail.append("chart binding invalid")
 elif subprocess.run(["git","check-ignore","-q",str(chart)],cwd=ROOT,check=False).returncode:fail.append("chart not ignored")
 mutations=[lambda x:x["summary"].update(candidate_count=25),lambda x:x["summary"].update(engineering_pass=16),lambda x:x["summary"].update(engineering_warn=2),lambda x:x["summary"].update(engineering_fail=5),lambda x:x["summary"].update(nonpass_candidate_count=8),lambda x:x["summary"].update(repair_link_count=5),lambda x:x["summary"].update(repair_all_dimension_pass_count=3),lambda x:x["summary"].update(repair_target_fixed_count=4),lambda x:x["summary"].update(next_plan_count=3),lambda x:x["summary"].update(next_initial_candidates=3),lambda x:x["summary"].update(next_maximum_candidates=5),lambda x:x["summary"].update(next_prompt_count=1),lambda x:x["summary"].update(plans_revised=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(external_cost_usd=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x["activity"].update(prompts=1),lambda x:x["activity"].update(renders=1),lambda x:x["activity"].update(provider_calls=1),lambda x:x["activity"].update(uploads=1),lambda x:x["activity"].update(plans_revised=1),lambda x:x["activity"].update(acceptances=1),lambda x:x["activity"].update(external_cost_usd=1)]
 rejected=0
 for mutation in mutations:y=copy.deepcopy(d);mutation(y);rejected+=bool(errors(y))
 if rejected!=len(mutations):fail.append(f"only {rejected}/{len(mutations)} mutations rejected")
 print(f"CH05 failure-class repair matrix: {len(fail)} failures; 9 nonpass/6 repair links/5 fixed/4 all-pass; {rejected}/{len(mutations)} mutations rejected")
 print("next P010–P013: 4 initial/2 repair slots; 0 prompts/renders/plans/provider/uploads/$0")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
