"""Validate the P010-P013 lifecycle and exhaust every state pair."""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; EVIDENCE=ROOT/"docs/research/evidence/ch05-p010-p013-lifecycle-state-machine-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]; expected=(11,11,121,110,"DRAFT_BLUEPRINTED",0,2,6,0,0,0,0,0,0,0)
    actual=tuple(s.get(k) for k in ("states","legal_transitions","state_pairs","illegal_or_unconfigured_pairs","current_state","current_enabled_transitions","repair_slots","invariants","prompts","renders","packet_artifacts","review_events","accepted","commercially_cleared","executable"))
    if d.get("state")!="PASS_FAIL_CLOSED" or actual!=expected or s.get("human_review_minutes") is not None: out.append("state/denominator invalid")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); fail=errors(d)
    for x in [d["state_machine"],*d["inputs"]]:
        p=ROOT/x["path"]
        if not p.is_file() or sha(p)!=x["sha256"]: fail.append(f"binding invalid: {x['path']}")
    m=json.loads((ROOT/d["state_machine"]["path"]).read_text(encoding="utf-8")); states=m.get("states",[]); edges=m.get("transitions",[]); edge_pairs={(x["from"],x["to"]) for x in edges}; activity=m.get("activity",{}); current=m.get("current",{}); sep=m.get("promotion_separation",{})
    if len(states)!=11 or len(set(states))!=11 or len(edges)!=11 or len(edge_pairs)!=11 or any(x["from"] not in states or x["to"] not in states or x["currently_enabled"] is not False for x in edges): fail.append("state/edge graph invalid")
    evaluated={(a,b):(a,b) in edge_pairs for a in states for b in states}
    if len(evaluated)!=121 or sum(evaluated.values())!=11 or sum(not x for x in evaluated.values())!=110: fail.append("pair exhaustion invalid")
    required_loop={("HUMAN_REVIEW_COMPLETE","REPAIR_ALLOCATED"),("REPAIR_ALLOCATED","TARGETED_REPAIR_RENDERED"),("TARGETED_REPAIR_RENDERED","REPAIRED_PACKET_BUILT"),("REPAIRED_PACKET_BUILT","HUMAN_REVIEW_COMPLETE")}
    if not required_loop<=edge_pairs or m.get("repair_loop")!={"entry":"HUMAN_REVIEW_COMPLETE -> REPAIR_ALLOCATED","maximum_total_slots":2,"one_failure_class_per_slot":True,"broad_reroll":False,"passing_rows_preserved":True,"exit":"REPAIRED_PACKET_BUILT -> HUMAN_REVIEW_COMPLETE"}: fail.append("repair loop invalid")
    if current.get("state")!="DRAFT_BLUEPRINTED" or any(v not in (0,False,None,"DRAFT_BLUEPRINTED") for v in current.values()): fail.append("current state fabricated")
    if sep.get("commercial_and_exact_base_automatic") is not False or sep.get("exact_base_implies_commercial_clearance") is not False or sep.get("commercial_clearance_implies_exact_base") is not False: fail.append("promotion separation invalid")
    if any(activity.get(k)!=0 for k in ("prompts_compiled","provider_calls","uploads","renders","packet_artifacts","review_events","accepted_candidates","commercially_cleared","executable_panels")) or activity.get("human_review_minutes") is not None: fail.append("activity fabricated")
    muts=[lambda x:x.update(state="PASS_TRANSITIONED"),lambda x:x["summary"].update(states=10),lambda x:x["summary"].update(legal_transitions=10),lambda x:x["summary"].update(state_pairs=120),lambda x:x["summary"].update(illegal_or_unconfigured_pairs=109),lambda x:x["summary"].update(current_state="BASE_RENDERED"),lambda x:x["summary"].update(current_enabled_transitions=1),lambda x:x["summary"].update(repair_slots=3),lambda x:x["summary"].update(invariants=5),lambda x:x["summary"].update(prompts=1),lambda x:x["summary"].update(renders=1),lambda x:x["summary"].update(packet_artifacts=1),lambda x:x["summary"].update(review_events=1),lambda x:x["summary"].update(accepted=1),lambda x:x["summary"].update(commercially_cleared=1),lambda x:x["summary"].update(executable=1),lambda x:x["summary"].update(human_review_minutes=1),lambda x:x.update(animation_shot_plan={})]
    rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"P010-P013 lifecycle: {len(fail)} failures; 11 states/11 legal/110 illegal pairs; repair loop 4 edges; {rejected}/{len(muts)} mutations rejected")
    print("current DRAFT/0 enabled; prompts/renders/review/promotion/minutes 0/0/0/0/null")
    for item in fail: print(f"FAIL: {item}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
