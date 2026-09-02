"""Validate measured, zero-execution CH05 chapter-scale production envelope."""
from __future__ import annotations
import copy,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];EVIDENCE=ROOT/"docs/research/evidence/ch05-chapter-scale-production-envelope-r1.json";ENVELOPE=ROOT/"production/comic/run-manifests/ch05-chapter-scale-production-envelope-r1.json"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d:dict)->list[str]:
 s=d.get("summary",{});a=d.get("activity",{});out=[]
 if tuple(s.get(k) for k in ("total_plans","selected_existing","remaining_plans","tier_count","plans_per_tier","scenario_count","repair_allowance_slots","recommended_candidate_envelope","row_count","prompt_count","execution_ready_rows"))!=(50,14,36,3,12,3,13,49,36,0,0):out.append("denominators invalid")
 if any(s.get(k)!=0 for k in ("provider_calls","uploads","external_cost_usd")) or s.get("human_review_minutes") is not None:out.append("summary activity fabricated")
 if any(a.get(k)!=0 for k in ("prompts","renders","provider_calls","uploads","plans_revised","acceptances","external_cost_usd")):out.append("activity fabricated")
 counts=[x.get("candidate_count") for x in d.get("scenarios",[])]
 if counts!=[36,49,72] or any(x["timing"].get("monetary_cost_usd") is not None or x["timing"].get("human_review_minutes") is not None for x in d.get("scenarios",[])):out.append("scenarios invalid")
 return out
def main()->int:
 d=json.loads(EVIDENCE.read_text(encoding="utf-8"));e=json.loads(ENVELOPE.read_text(encoding="utf-8"));fail=errors(d)
 if d["envelope"]["sha256"]!=sha(ENVELOPE) or len(e["rows"])!=36 or [x["tier"] for x in e["tiers"]]!=["A","B","C"]:fail.append("envelope binding/content invalid")
 if e["animation_shot_plan"] is not None or e["e_conte"] is not None or any(r["prompt"] is not None or r["execution_ready"] for r in e["rows"]):fail.append("planning/execution boundary invalid")
 chart=ROOT/d["chart"]["path"]
 if not chart.is_file() or sha(chart)!=d["chart"]["sha256"]:fail.append("chart binding invalid")
 elif subprocess.run(["git","check-ignore","-q",str(chart)],cwd=ROOT,check=False).returncode:fail.append("chart not ignored")
 mutations=[lambda x:x["summary"].update(total_plans=49),lambda x:x["summary"].update(selected_existing=13),lambda x:x["summary"].update(remaining_plans=35),lambda x:x["summary"].update(tier_count=2),lambda x:x["summary"].update(plans_per_tier=11),lambda x:x["summary"].update(scenario_count=2),lambda x:x["summary"].update(repair_allowance_slots=12),lambda x:x["summary"].update(recommended_candidate_envelope=48),lambda x:x["summary"].update(row_count=35),lambda x:x["summary"].update(prompt_count=1),lambda x:x["summary"].update(execution_ready_rows=1),lambda x:x["summary"].update(provider_calls=1),lambda x:x["summary"].update(uploads=1),lambda x:x["summary"].update(external_cost_usd=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x["scenarios"][0].update(candidate_count=35),lambda x:x["scenarios"][0]["timing"].update(monetary_cost_usd=1),lambda x:x["scenarios"][0]["timing"].update(human_review_minutes=1),lambda x:x["activity"].update(prompts=1),lambda x:x["activity"].update(renders=1),lambda x:x["activity"].update(provider_calls=1),lambda x:x["activity"].update(uploads=1),lambda x:x["activity"].update(plans_revised=1),lambda x:x["activity"].update(acceptances=1),lambda x:x["activity"].update(external_cost_usd=1)]
 rejected=0
 for mutation in mutations:y=copy.deepcopy(d);mutation(y);rejected+=bool(errors(y))
 if rejected!=len(mutations):fail.append(f"only {rejected}/{len(mutations)} mutations rejected")
 print(f"CH05 chapter-scale envelope: {len(fail)} failures; 50=14+36; scenarios 36/49/72; {rejected}/{len(mutations)} mutations rejected")
 print("13 repair slots; 0 prompts/renders/plans/provider/uploads/$0; money/human time null")
 for item in fail:print(f"FAIL: {item}")
 return 1 if fail else 0
if __name__=="__main__":raise SystemExit(main())
