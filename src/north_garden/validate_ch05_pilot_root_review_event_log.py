"""Validate live timer events for the six CH05 pilot roots without ingestion."""
from __future__ import annotations
import argparse,hashlib,json,re
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; CONTRACT=ROOT/"production/comic/review/ch05-pilot-root-review-time-contract-r1.json"; UTC_RE=re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def validate_log(payload,contract=None):
    contract=contract or json.loads(CONTRACT.read_text(encoding="utf-8")); failures=[]
    if payload.get("record_type")!="ComicPilotRootReviewTimeEventLog" or payload.get("schema_version")!="1.0": failures.append("record type/schema invalid")
    if payload.get("contract_record_id")!=contract["record_id"] or payload.get("contract_sha256")!=sha(CONTRACT): failures.append("contract binding invalid")
    if payload.get("capture_mode")!="LIVE_TIMER_ONLY" or "human_review_minutes" in payload: failures.append("capture/derived-field boundary invalid")
    known=contract["subjects"]; states={}; active={}; event_ids=set(); last=None; completed=0; seconds=0.0
    for i,event in enumerate(payload.get("events",[])):
        pre=f"event[{i}]"; eid=event.get("event_id"); subject=event.get("subject_id"); reviewer=event.get("reviewer"); timestamp=event.get("occurred_at_utc")
        if not isinstance(eid,str) or not eid or eid in event_ids: failures.append(f"{pre} event id invalid/duplicate")
        event_ids.add(eid)
        if subject not in known: failures.append(f"{pre} unknown subject"); continue
        if not isinstance(reviewer,str) or not reviewer.strip(): failures.append(f"{pre} reviewer invalid"); continue
        if not isinstance(timestamp,str) or not UTC_RE.match(timestamp): failures.append(f"{pre} UTC timestamp invalid"); continue
        moment=datetime.fromisoformat(timestamp.replace("Z","+00:00"))
        if last is not None and moment<last: failures.append(f"{pre} chronology reversed")
        last=moment; kind=event.get("event_type"); delta=event.get("active_delta_seconds"); decision=event.get("decision"); state=states.setdefault(subject,{"state":"NOT_STARTED","reviewer":None,"seconds":0.0})
        if kind=="REVIEW_STARTED":
            if state["state"]!="NOT_STARTED" or delta is not None or decision is not None or reviewer in active: failures.append(f"{pre} invalid start transition")
            else: state.update(state="ACTIVE",reviewer=reviewer); active[reviewer]=subject
        elif kind=="REVIEW_PAUSED":
            if state["state"]!="ACTIVE" or state["reviewer"]!=reviewer or not isinstance(delta,(int,float)) or isinstance(delta,bool) or delta<=0 or decision is not None: failures.append(f"{pre} invalid pause transition")
            else: state["state"]="PAUSED"; state["seconds"]+=float(delta); seconds+=float(delta); active.pop(reviewer,None)
        elif kind=="REVIEW_RESUMED":
            if state["state"]!="PAUSED" or state["reviewer"]!=reviewer or delta is not None or decision is not None or reviewer in active: failures.append(f"{pre} invalid resume transition")
            else: state["state"]="ACTIVE"; active[reviewer]=subject
        elif kind=="REVIEW_COMPLETED":
            if state["state"]!="ACTIVE" or state["reviewer"]!=reviewer or not isinstance(delta,(int,float)) or isinstance(delta,bool) or delta<0 or decision not in known[subject]["allowed_decisions"]: failures.append(f"{pre} invalid complete transition/decision")
            else: state["state"]="COMPLETED"; state["seconds"]+=float(delta); seconds+=float(delta); active.pop(reviewer,None); completed+=1
        else: failures.append(f"{pre} event type invalid")
    return sorted(set(failures)),{"event_count":len(payload.get("events",[])),"completed_subjects":completed,"active_seconds":round(seconds,6),"human_review_minutes":round(seconds/60,6) if completed else None,"open_active_sessions":len(active)}
def main():
    p=argparse.ArgumentParser(); p.add_argument("event_log",type=Path); a=p.parse_args(); path=a.event_log if a.event_log.is_absolute() else ROOT/a.event_log; payload=json.loads(path.read_text(encoding="utf-8")); failures,derived=validate_log(payload); print(json.dumps({"valid":not failures,"failures":failures,"derived":derived},indent=2)); return 1 if failures else 0
if __name__=="__main__": raise SystemExit(main())
