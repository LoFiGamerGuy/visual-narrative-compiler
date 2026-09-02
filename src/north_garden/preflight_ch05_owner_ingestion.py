"""Fail-closed CH05 owner-input preflight; never ingests or transitions state."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from validate_ch05_owner_response import validate_document
from validate_ch05_pilot_root_review_event_log import validate_log

ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE = ROOT / "production/comic/run-manifests/ch05-p010-p013-lifecycle-state-machine-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _absolute(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def preflight(response_path: Path, event_log_path: Path) -> dict:
    response_path, event_log_path = _absolute(response_path), _absolute(event_log_path)
    missing = [str(path.relative_to(ROOT)).replace("\\", "/") for path in (response_path, event_log_path) if not path.is_file()]
    base = {
        "record_type": "CH05OwnerIngestionPreflightResult",
        "schema_version": "1.0",
        "ingestion_performed": False,
        "lifecycle_transition_performed": False,
        "production_prompts_compiled": 0,
        "provider_calls": 0,
        "uploads": 0,
        "paid_spend_usd": 0,
        "accepted": 0,
        "commercially_cleared": 0,
        "animation_shot_plan": None,
        "e_conte": None,
    }
    if missing:
        return {**base, "state": "BLOCKED_INPUTS_ABSENT", "eligible_for_future_ingestion": False, "missing_inputs": missing, "failures": ["required live owner inputs absent"]}
    try:
        response = json.loads(response_path.read_text(encoding="utf-8"))
        event_log = json.loads(event_log_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return {**base, "state": "BLOCKED_INVALID_INPUTS", "eligible_for_future_ingestion": False, "missing_inputs": [], "failures": [f"invalid JSON: {error.msg}"]}

    failures = list(validate_document(response, "response"))
    timer_failures, derived = validate_log(event_log)
    failures.extend(timer_failures)
    lifecycle = json.loads(LIFECYCLE.read_text(encoding="utf-8"))
    if lifecycle.get("current", {}).get("state") != "DRAFT_BLUEPRINTED" or lifecycle.get("current_enabled_transition_count") != 0:
        failures.append("lifecycle source is not the expected fail-closed draft")

    seconds, completed = {}, {}
    for event in event_log.get("events", []):
        subject = event.get("subject_id")
        delta = event.get("active_delta_seconds")
        if isinstance(delta, (int, float)) and not isinstance(delta, bool):
            seconds[subject] = seconds.get(subject, 0.0) + float(delta)
        if event.get("event_type") == "REVIEW_COMPLETED":
            completed[subject] = {"decision": event.get("decision"), "reviewer": event.get("reviewer")}
    rows = {row.get("decision_id"): row for row in response.get("decisions", [])}
    if set(rows) != set(completed):
        failures.append("response/timer root coverage differs")
    for root_id in sorted(set(rows) & set(completed)):
        row, event = rows[root_id], completed[root_id]
        if row.get("owner_decision") != event["decision"]:
            failures.append(f"decision parity invalid: {root_id}")
        if row.get("reviewer") != event["reviewer"]:
            failures.append(f"reviewer parity invalid: {root_id}")
        expected_minutes = round(seconds.get(root_id, 0.0) / 60, 6)
        if row.get("human_review_minutes") != expected_minutes:
            failures.append(f"minute parity invalid: {root_id}")
    failures = sorted(set(failures))
    eligible = not failures and derived.get("completed_subjects") == 6 and derived.get("open_active_sessions") == 0
    return {
        **base,
        "state": "PASS_ELIGIBLE_FOR_FUTURE_HASH_CHAINED_INGESTION" if eligible else "BLOCKED_INVALID_INPUTS",
        "eligible_for_future_ingestion": eligible,
        "missing_inputs": [],
        "failures": failures,
        "response": {"path": str(response_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(response_path)},
        "event_log": {"path": str(event_log_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(event_log_path)},
        "derived": derived,
        "root_parity_count": 6 if eligible else 0,
        "current_lifecycle_state": lifecycle["current"]["state"],
        "next_lifecycle_state": "OWNER_ROOTS_RESOLVED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("response", type=Path)
    parser.add_argument("event_log", type=Path)
    args = parser.parse_args()
    result = preflight(args.response, args.event_log)
    print(json.dumps(result, indent=2))
    return 0 if result["eligible_for_future_ingestion"] else 2 if result["state"] == "BLOCKED_INPUTS_ABSENT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
