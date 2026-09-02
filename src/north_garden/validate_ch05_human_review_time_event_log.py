"""Validate live-timer-only CH05 human-review event logs without writing decisions."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "production/comic/review/ch05-human-review-time-instrumentation-contract-r1.json"
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_log(payload: dict, contract: dict | None = None) -> tuple[list[str], dict]:
    contract = contract or json.loads(CONTRACT.read_text(encoding="utf-8"))
    failures = []
    if payload.get("record_type") != "ComicHumanReviewTimeEventLog" or payload.get("schema_version") != "1.0":
        failures.append("record type/schema invalid")
    if payload.get("contract_record_id") != contract["record_id"] or payload.get("contract_sha256") != sha(CONTRACT):
        failures.append("contract binding invalid")
    if payload.get("capture_mode") != "LIVE_TIMER_ONLY" or "human_review_minutes" in payload:
        failures.append("capture/derived-field boundary invalid")
    known = contract["subjects"]
    states: dict[str, dict] = {}
    active_by_reviewer: dict[str, str] = {}
    event_ids = set()
    last_time = None
    completed = 0
    active_seconds = 0.0
    for index, event in enumerate(payload.get("events", [])):
        prefix = f"event[{index}]"
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id or event_id in event_ids:
            failures.append(f"{prefix} event id invalid/duplicate")
        event_ids.add(event_id)
        subject = event.get("subject_id")
        if subject not in known:
            failures.append(f"{prefix} unknown subject")
            continue
        reviewer = event.get("reviewer")
        if not isinstance(reviewer, str) or not reviewer.strip():
            failures.append(f"{prefix} reviewer invalid")
            continue
        timestamp = event.get("occurred_at_utc")
        if not isinstance(timestamp, str) or not UTC_RE.match(timestamp):
            failures.append(f"{prefix} UTC timestamp invalid")
            continue
        moment = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if last_time is not None and moment < last_time:
            failures.append(f"{prefix} chronology reversed")
        last_time = moment
        event_type = event.get("event_type")
        delta = event.get("active_delta_seconds")
        decision = event.get("decision")
        state = states.setdefault(subject, {"state": "NOT_STARTED", "reviewer": None, "seconds": 0.0})
        if event_type == "REVIEW_STARTED":
            if state["state"] != "NOT_STARTED" or delta is not None or decision is not None or reviewer in active_by_reviewer:
                failures.append(f"{prefix} invalid start transition")
            else:
                state.update(state="ACTIVE", reviewer=reviewer)
                active_by_reviewer[reviewer] = subject
        elif event_type == "REVIEW_PAUSED":
            if state["state"] != "ACTIVE" or state["reviewer"] != reviewer or not isinstance(delta, (int, float)) or delta <= 0 or decision is not None:
                failures.append(f"{prefix} invalid pause transition")
            else:
                state["state"] = "PAUSED"
                state["seconds"] += float(delta)
                active_seconds += float(delta)
                active_by_reviewer.pop(reviewer, None)
        elif event_type == "REVIEW_RESUMED":
            if state["state"] != "PAUSED" or state["reviewer"] != reviewer or delta is not None or decision is not None or reviewer in active_by_reviewer:
                failures.append(f"{prefix} invalid resume transition")
            else:
                state["state"] = "ACTIVE"
                active_by_reviewer[reviewer] = subject
        elif event_type == "REVIEW_COMPLETED":
            allowed = known[subject]["allowed_decisions"]
            if state["state"] != "ACTIVE" or state["reviewer"] != reviewer or not isinstance(delta, (int, float)) or delta < 0 or decision not in allowed:
                failures.append(f"{prefix} invalid complete transition/decision")
            else:
                state["state"] = "COMPLETED"
                state["seconds"] += float(delta)
                active_seconds += float(delta)
                active_by_reviewer.pop(reviewer, None)
                completed += 1
        else:
            failures.append(f"{prefix} event type invalid")
    derived = {"event_count": len(payload.get("events", [])), "completed_subjects": completed, "active_seconds": round(active_seconds, 6), "human_review_minutes": round(active_seconds / 60, 6) if completed else None, "open_active_sessions": len(active_by_reviewer)}
    return sorted(set(failures)), derived


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("event_log")
    args = parser.parse_args()
    payload = json.loads(Path(args.event_log).read_text(encoding="utf-8"))
    failures, derived = validate_log(payload)
    print(json.dumps({"valid": not failures, "failures": failures, "derived": derived}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
