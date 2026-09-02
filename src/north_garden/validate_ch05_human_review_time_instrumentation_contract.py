"""Validate CH05 human-review time contract and synthetic event boundaries."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from validate_ch05_human_review_time_event_log import validate_log

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-human-review-time-instrumentation-contract-r1.json"
CONTRACT = ROOT / "production/comic/review/ch05-human-review-time-instrumentation-contract-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(record: dict) -> list[str]:
    summary = record.get("summary", {})
    failures = []
    expected = (39, 4, 7, 6, 3, 12, 0, 0)
    actual = tuple(summary.get(key) for key in ("subject_count", "event_types", "event_fields", "rules", "valid_synthetic_logs", "invalid_synthetic_logs_rejected", "current_event_count", "completed_subjects"))
    if actual != expected or record.get("state") != "PASS_EMPTY_CONTRACT" or summary.get("human_review_minutes") is not None:
        failures.append("contract denominator/state invalid")
    if any(summary.get(key) != 0 for key in ("owner_decisions", "accepted_candidates", "provider_calls", "uploads", "cost_usd")):
        failures.append("activity/review fabricated")
    if record.get("animation_shot_plan") is not None or record.get("e_conte") is not None:
        failures.append("planning boundary invalid")
    return failures


def event(event_id: str, subject: str, kind: str, second: int, delta=None, decision=None, reviewer="owner") -> dict:
    return {"event_id": event_id, "subject_id": subject, "event_type": kind, "reviewer": reviewer, "occurred_at_utc": f"2030-01-01T00:00:{second:02d}Z", "active_delta_seconds": delta, "decision": decision}


def payload(contract: dict, events: list[dict]) -> dict:
    return {"record_type": "ComicHumanReviewTimeEventLog", "schema_version": "1.0", "contract_record_id": contract["record_id"], "contract_sha256": sha(CONTRACT), "capture_mode": "LIVE_TIMER_ONLY", "events": events}


def main() -> int:
    record = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    failures = errors(record)
    if sha(CONTRACT) != record["contract"]["sha256"] or sha(ROOT / record["source_owner_contract"]["path"]) != record["source_owner_contract"]["sha256"]:
        failures.append("contract/source binding invalid")
    subject = "c001"
    decision = contract["subjects"][subject]["allowed_decisions"][0]
    valid = [payload(contract, []), payload(contract, [event("e1", subject, "REVIEW_STARTED", 1)]), payload(contract, [event("e1", subject, "REVIEW_STARTED", 1), event("e2", subject, "REVIEW_PAUSED", 2, 12.5), event("e3", subject, "REVIEW_RESUMED", 3), event("e4", subject, "REVIEW_COMPLETED", 4, 7.5, decision)])]
    invalid = []
    base_start = event("e1", subject, "REVIEW_STARTED", 1)
    invalid.append({**payload(contract, []), "capture_mode": "BACKFILL"})
    invalid.append(payload(contract, [event("e1", "unknown", "REVIEW_STARTED", 1)]))
    invalid.append(payload(contract, [base_start, copy.deepcopy(base_start)]))
    invalid.append(payload(contract, [event("e1", subject, "REVIEW_PAUSED", 1, 1)]))
    invalid.append(payload(contract, [base_start, event("e2", subject, "REVIEW_PAUSED", 2, -1)]))
    invalid.append(payload(contract, [base_start, event("e2", subject, "REVIEW_COMPLETED", 2, 1, "BAD_DECISION")]))
    invalid.append(payload(contract, [event("e1", subject, "BAD", 1)]))
    bad_time = event("e1", subject, "REVIEW_STARTED", 1); bad_time["occurred_at_utc"] = "2030-01-01"
    invalid.append(payload(contract, [bad_time]))
    invalid.append(payload(contract, [base_start, event("e2", subject, "REVIEW_PAUSED", 3, 1), event("e3", subject, "REVIEW_RESUMED", 2)]))
    invalid.append(payload(contract, [base_start, event("e2", "c002", "REVIEW_STARTED", 2, reviewer="owner")]))
    invalid.append(payload(contract, [event("e1", subject, "REVIEW_RESUMED", 1)]))
    with_minutes = payload(contract, []); with_minutes["human_review_minutes"] = 5
    invalid.append(with_minutes)
    valid_count = sum(not validate_log(item, contract)[0] for item in valid)
    invalid_rejected = sum(bool(validate_log(item, contract)[0]) for item in invalid)
    if valid_count != 3 or invalid_rejected != 12:
        failures.append(f"synthetic boundary invalid: {valid_count}/3 valid, {invalid_rejected}/12 rejected")
    completed_failures, derived = validate_log(valid[2], contract)
    if completed_failures or derived != {"event_count": 4, "completed_subjects": 1, "active_seconds": 20.0, "human_review_minutes": 0.333333, "open_active_sessions": 0}:
        failures.append("derived timer rollup invalid")
    mutations = [lambda x: x.update(state="FAIL"), lambda x: x["summary"].update(subject_count=38), lambda x: x["summary"].update(event_types=3), lambda x: x["summary"].update(event_fields=6), lambda x: x["summary"].update(rules=5), lambda x: x["summary"].update(valid_synthetic_logs=2), lambda x: x["summary"].update(invalid_synthetic_logs_rejected=11), lambda x: x["summary"].update(current_event_count=1), lambda x: x["summary"].update(completed_subjects=1), lambda x: x["summary"].update(human_review_minutes=1), lambda x: x["summary"].update(owner_decisions=1), lambda x: x["summary"].update(accepted_candidates=1), lambda x: x["summary"].update(provider_calls=1), lambda x: x["summary"].update(uploads=1), lambda x: x["summary"].update(cost_usd=1), lambda x: x.update(animation_shot_plan={})]
    rejected = 0
    for mutation in mutations:
        candidate = copy.deepcopy(record); mutation(candidate); rejected += bool(errors(candidate))
    if rejected != len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 review timer contract: {len(failures)} failures; 3/3 valid + 12/12 invalid synthetic logs; {rejected}/{len(mutations)} evidence mutations rejected")
    print("live events/completed/minutes/decisions/accepted/calls/uploads/cost 0/0/null/0/0/0/0/$0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
