"""Validate the fail-closed P010-P013 owner unlock contract."""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-p010-p013-owner-unlock-contract-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    out=[]; s=d.get("summary",{})
    expected=(6,0,6,4,14,4,2,5,0,0,0,0,0,0)
    actual=tuple(s.get(k) for k in ("required_decisions","resolved_required_decisions","direct_compile_values","deferred_decisions","existing_candidate_reviews","pilot_candidates","repair_slots","planned_review_artifacts","prompts","renders","owner_decisions","accepted","commercially_cleared","executable"))
    if d.get("state")!="PASS_BLOCKED" or actual!=expected or s.get("human_review_minutes") is not None: out.append("state/denominator invalid")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    for key in ("contract","owner_checklist"):
        p=ROOT/d[key]["path"]
        if not p.is_file() or sha(p)!=d[key]["sha256"]: fail.append(f"binding invalid: {key}")
    for x in d["inputs"]:
        p=ROOT/x["path"]
        if not p.is_file() or sha(p)!=x["sha256"]: fail.append(f"input invalid: {x['path']}")
    c=json.loads((ROOT/d["contract"]["path"]).read_text(encoding="utf-8")); roots=c.get("exact_required_decisions",[]); activity=c.get("current_activity",{}); levels=c.get("unlock_levels",{})
    if len(roots)!=6 or len({x["decision_id"] for x in roots})!=6 or any(x["owner_decision"] is not None or x["reviewer"] is not None or x["human_review_minutes"] is not None or x["resolved"] is not False for x in roots): fail.append("decision roots invalid")
    if any(x["direct_compile_value"] not in x["allowed_decisions"] for x in roots): fail.append("direct decision vocabulary invalid")
    if len(c.get("deferred_decisions",[]))!=4 or len(c.get("existing_candidate_reviews",[]))!=14 or any(x["decision"] is not None for x in c.get("existing_candidate_reviews",[])): fail.append("deferred/candidate state invalid")
    if c.get("broad_prior_approval")!={"recorded_as_positive_creative_direction":True,"structured_decision_ingested":False,"reason":"General approval and permission to continue do not identify exact values for the six dependency roots and do not constitute candidate acceptance, commercial clearance, or an exact-base decision."}: fail.append("broad approval boundary invalid")
    if any(x.get("ready") is not False for x in levels.values()): fail.append("unlock level fabricated")
    zero=("prompts","renders","provider_calls","uploads","paid_spend_usd","owner_decisions","review_events","accepted_candidates","commercially_cleared_candidates","executable_panels","comic_panel_plan_revisions")
    if any(activity.get(k)!=0 for k in zero) or activity.get("human_review_minutes") is not None: fail.append("activity fabricated")
    muts=[lambda x:x.update(state="PASS_UNLOCKED"),lambda x:x["summary"].update(required_decisions=5),lambda x:x["summary"].update(resolved_required_decisions=1),lambda x:x["summary"].update(direct_compile_values=5),lambda x:x["summary"].update(deferred_decisions=3),lambda x:x["summary"].update(existing_candidate_reviews=13),lambda x:x["summary"].update(pilot_candidates=3),lambda x:x["summary"].update(repair_slots=1),lambda x:x["summary"].update(planned_review_artifacts=4),lambda x:x["summary"].update(prompts=1),lambda x:x["summary"].update(renders=1),lambda x:x["summary"].update(owner_decisions=1),lambda x:x["summary"].update(accepted=1),lambda x:x["summary"].update(commercially_cleared=1),lambda x:x["summary"].update(executable=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x.update(animation_shot_plan={})]
    rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"P010-P013 owner unlock: {len(fail)} failures; 6 roots/0 resolved; 4 deferred/14 candidate reviews; {rejected}/{len(muts)} mutations rejected")
    print("prompt/render/promotion/owner decisions/minutes 0/0/0/0/null")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
