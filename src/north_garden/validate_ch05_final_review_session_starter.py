"""Validate CH05 final review-session starter and fail-closed state."""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-final-review-session-starter-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]; keys=("steps","ready_steps","owner_action_steps","blocked_steps","intentionally_unimplemented_steps","pilot_root_subjects","legacy_full_review_subjects","strongest_candidates","generated_sequences","priority_review_links","response_files_present","event_logs_present","owner_decisions_ingested","review_events","production_prompts","renders","provider_calls","uploads","paid_spend_usd","accepted","commercially_cleared","executable"); expected=(8,1,4,2,1,6,39,14,3,67,0,0,0,0,0,0,0,0,0,0,0,0)
    if tuple(s.get(k) for k in keys)!=expected or s.get("human_review_minutes") is not None or d.get("state")!="PASS_LOCAL_INPUTS_ABSENT": out.append("state/denominator invalid")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    for key in ("starter","guide"):
        p=ROOT/d[key]["path"]
        if not p.is_file() or sha(p)!=d[key]["sha256"]: fail.append(f"binding invalid: {key}")
    for item in d["inputs"]:
        p=ROOT/item["path"]
        if not p.is_file() or sha(p)!=item["sha256"]: fail.append(f"input invalid: {item['path']}")
    if any((ROOT/p).exists() for p in d["absent_local_inputs"]): fail.append("planned local input unexpectedly exists")
    starter=json.loads((ROOT/d["starter"]["path"]).read_text(encoding="utf-8")); steps=starter.get("steps",[])
    if [x["order"] for x in steps]!=list(range(1,9)) or steps[6]["status"]!="INTENTIONALLY_NOT_IMPLEMENTED" or starter["current_lifecycle"]!={"state":"DRAFT_BLUEPRINTED","enabled_transitions":0,"next_state":"OWNER_ROOTS_RESOLVED","production_prompt_state":"ABSENT"}: fail.append("step/lifecycle boundary invalid")
    muts=[lambda x:x.update(state="FAIL")]+[lambda x,k=k:x["summary"].update({k:-1}) for k in ("steps","ready_steps","owner_action_steps","blocked_steps","intentionally_unimplemented_steps","pilot_root_subjects","legacy_full_review_subjects","strongest_candidates","generated_sequences","priority_review_links","response_files_present","event_logs_present","owner_decisions_ingested","review_events","production_prompts","renders","provider_calls","uploads","paid_spend_usd","accepted","commercially_cleared","executable")]+[lambda x:x["summary"].update(human_review_minutes=1),lambda x:x.update(animation_shot_plan={})]; rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 review starter: {len(fail)} failures; 8 steps/1 ready/4 owner/2 blocked/1 absent; {rejected}/{len(muts)} mutations rejected")
    for x in fail: print(f"FAIL: {x}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
