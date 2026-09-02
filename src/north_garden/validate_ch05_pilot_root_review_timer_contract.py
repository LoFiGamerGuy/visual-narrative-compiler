"""Validate six-root timer contract, conflict mapping, and synthetic logs."""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
from validate_ch05_pilot_root_review_event_log import validate_log
ROOT=Path(__file__).resolve().parents[2]; CONTRACT=ROOT/"production/comic/review/ch05-pilot-root-review-time-contract-r1.json"; EVIDENCE=ROOT/"docs/research/evidence/ch05-pilot-root-review-time-contract-r1.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def errors(d):
    s=d.get("summary",{}); out=[]; expected=(6,39,3,3,4,7,6,3,12,0,0,0,0,0,0,0); actual=tuple(s.get(k) for k in ("root_subjects","legacy_subjects","exact_legacy_mappings","missing_legacy_mappings","event_types","event_fields","rules","valid_synthetic_logs","invalid_synthetic_logs_rejected","current_event_count","completed_subjects","owner_decisions","accepted_candidates","provider_calls","uploads","cost_usd"))
    if actual!=expected or s.get("human_review_minutes") is not None or d.get("state")!="PASS_EMPTY_CONTRACT_ARCHITECTURE_CONFLICT_RESOLVED_APPEND_ONLY": out.append("state/denominator invalid")
    if d.get("animation_shot_plan") is not None or d.get("e_conte") is not None: out.append("planning boundary invalid")
    return out
def event(eid,subject,kind,second,delta=None,decision=None,reviewer="owner"): return {"event_id":eid,"subject_id":subject,"event_type":kind,"reviewer":reviewer,"occurred_at_utc":f"2030-01-01T00:00:{second:02d}Z","active_delta_seconds":delta,"decision":decision}
def payload(contract,events): return {"record_type":"ComicPilotRootReviewTimeEventLog","schema_version":"1.0","contract_record_id":contract["record_id"],"contract_sha256":sha(CONTRACT),"capture_mode":"LIVE_TIMER_ONLY","events":events}
def main():
    d=json.loads(EVIDENCE.read_text(encoding="utf-8")); contract=json.loads(CONTRACT.read_text(encoding="utf-8")); fail=errors(d)
    if sha(CONTRACT)!=d["contract"]["sha256"] or any(sha(ROOT/x["path"])!=x["sha256"] for x in d["inputs"]): fail.append("binding invalid")
    conflict=contract["architecture_conflict"]
    if conflict["exact_root_mappings"]!=3 or conflict["missing_root_mappings"]!=3 or set(conflict["missing_root_ids"])!={"lettering_semantics","p010_p013_finish_rhythm","p010_p013_copy"}: fail.append("architecture conflict mapping invalid")
    subject="route_role_aware_hybrid"; decision=contract["subjects"][subject]["allowed_decisions"][0]; start=event("e1",subject,"REVIEW_STARTED",1); valid=[payload(contract,[]),payload(contract,[start]),payload(contract,[start,event("e2",subject,"REVIEW_PAUSED",2,12.5),event("e3",subject,"REVIEW_RESUMED",3),event("e4",subject,"REVIEW_COMPLETED",4,7.5,decision)])]; invalid=[]; invalid.append({**payload(contract,[]),"capture_mode":"BACKFILL"}); invalid.append(payload(contract,[event("e1","unknown","REVIEW_STARTED",1)])); invalid.append(payload(contract,[start,copy.deepcopy(start)])); invalid.append(payload(contract,[event("e1",subject,"REVIEW_PAUSED",1,1)])); invalid.append(payload(contract,[start,event("e2",subject,"REVIEW_PAUSED",2,-1)])); invalid.append(payload(contract,[start,event("e2",subject,"REVIEW_COMPLETED",2,1,"BAD")])); invalid.append(payload(contract,[event("e1",subject,"BAD",1)])); bad=event("e1",subject,"REVIEW_STARTED",1); bad["occurred_at_utc"]="bad"; invalid.append(payload(contract,[bad])); invalid.append(payload(contract,[start,event("e2",subject,"REVIEW_PAUSED",3,1),event("e3",subject,"REVIEW_RESUMED",2)])); invalid.append(payload(contract,[start,event("e2","c005_transition_density","REVIEW_STARTED",2,reviewer="owner")])); invalid.append(payload(contract,[event("e1",subject,"REVIEW_RESUMED",1)])); with_minutes=payload(contract,[]); with_minutes["human_review_minutes"]=1; invalid.append(with_minutes)
    if sum(not validate_log(x,contract)[0] for x in valid)!=3 or sum(bool(validate_log(x,contract)[0]) for x in invalid)!=12: fail.append("synthetic logs invalid")
    muts=[lambda x:x.update(state="FAIL")]+[lambda x,k=k:x["summary"].update({k:-1}) for k in ("root_subjects","legacy_subjects","exact_legacy_mappings","missing_legacy_mappings","event_types","event_fields","rules","valid_synthetic_logs","invalid_synthetic_logs_rejected","current_event_count","completed_subjects","owner_decisions","accepted_candidates","provider_calls","uploads","cost_usd")]+[lambda x:x["summary"].update(human_review_minutes=1),lambda x:x.update(animation_shot_plan={})]; rejected=0
    for mut in muts: y=copy.deepcopy(d); mut(y); rejected+=bool(errors(y))
    if rejected!=len(muts): fail.append(f"only {rejected}/{len(muts)} mutations rejected")
    print(f"CH05 pilot-root timer: {len(fail)} failures; roots 6, legacy exact/missing 3/3; 3 valid/12 invalid; {rejected}/{len(muts)} mutations rejected")
    for x in fail: print(f"FAIL: {x}")
    return 1 if fail else 0
if __name__=="__main__": raise SystemExit(main())
