"""Validate zero-prompt P010-P013 microsequence preflight contract evidence."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-p010-p013-preflight-contract-r1.json";CONTRACT=ROOT/"production/comic/repair-readiness/ch05-p010-p013-preflight-contract-r1.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 s=d.get("summary",{});a=d.get("activity",{});g=d.get("gate_state",{});out=[]
 if tuple(s.get(k) for k in ("plan_count","initial_candidate_hypotheses","maximum_repair_slots","maximum_candidate_envelope","prompt_count","reference_hypothesis_uses","reference_uploads","final_copy_bound","owner_decisions_bound","execution_ready_rows","plan_revisions","repair_slots_unallocated"))!=(4,4,2,6,0,3,0,0,0,0,0,2):out.append("preflight denominators invalid")
 if any(s.get(k)!=0 for k in ("provider_calls","uploads","external_cost_usd")) or s.get("human_review_minutes") is not None:out.append("summary activity fabricated")
 if any(a.get(k)!=0 for k in ("prompts","renders","provider_calls","uploads","spend_usd","plans_revised","acceptances")):out.append("activity fabricated")
 if g.get("prompts_may_be_compiled_now") is not False or g.get("owner_completed_decisions")!=0:out.append("gate promotion invalid")
 return out
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));c=json.loads(CONTRACT.read_text(encoding="utf-8"));fail=errors(d)
 if d["contract"]["sha256"]!=sha(CONTRACT) or [r["display_order"] for r in c["rows"]]!=[10,11,12,13]:fail.append("contract binding/order invalid")
 if any(r["prompt"] is not None or r["source_path"] is not None or r["reference_uploads"]!=0 or r["execution_ready"] for r in c["rows"]):fail.append("row execution boundary invalid")
 if c["animation_shot_plan"] is not None or c["e_conte"] is not None or any(s["state"]!="UNALLOCATED" for s in c["repair_slots"]):fail.append("planning/repair boundary invalid")
 chart=ROOT/d["chart"]["path"]
 if not chart.is_file() or sha(chart)!=d["chart"]["sha256"]:fail.append("chart binding invalid")
 elif subprocess.run(["git","check-ignore","-q",str(chart)],cwd=ROOT,check=False).returncode:fail.append("chart not ignored")
 mutations=[lambda x:x["summary"].update(plan_count=3),lambda x:x["summary"].update(initial_candidate_hypotheses=3),lambda x:x["summary"].update(maximum_repair_slots=1),lambda x:x["summary"].update(maximum_candidate_envelope=5),lambda x:x["summary"].update(prompt_count=1),lambda x:x["summary"].update(reference_hypothesis_uses=2),lambda x:x["summary"].update(reference_uploads=1),lambda x:x["summary"].update(final_copy_bound=1),lambda x:x["summary"].update(owner_decisions_bound=1),lambda x:x["summary"].update(execution_ready_rows=1),lambda x:x["summary"].update(plan_revisions=1),lambda x:x["summary"].update(repair_slots_unallocated=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(external_cost_usd=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x["activity"].update(prompts=1),lambda x:x["activity"].update(renders=1),lambda x:x["activity"].update(provider_calls=1),lambda x:x["activity"].update(uploads=1),lambda x:x["activity"].update(spend_usd=1),lambda x:x["activity"].update(plans_revised=1),lambda x:x["activity"].update(acceptances=1),lambda x:x["gate_state"].update(prompts_may_be_compiled_now=True),lambda x:x["gate_state"].update(owner_completed_decisions=1)]
 rejected=0
 for mutation in mutations:y=copy.deepcopy(d);mutation(y);rejected+=bool(errors(y))
 if rejected!=len(mutations):fail.append(f"only {rejected}/{len(mutations)} mutations rejected")
 print(f"CH05 P010-P013 preflight: {len(fail)} failures; 4 plans/4 hypotheses/2 repair slots/0 prompts; {rejected}/{len(mutations)} mutations rejected")
 print("owner decisions/copy/executable/reference uploads/provider calls/spend 0/0/0/0/0/$0")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
