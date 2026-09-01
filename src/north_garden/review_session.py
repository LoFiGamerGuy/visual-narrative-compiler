"""Immutable timed human-review sessions with pause/resume and hash chaining."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import datetime


SHA256 = re.compile(r"^[0-9a-f]{64}$")
GENESIS = "GENESIS"


class ReviewSessionError(ValueError):
    """Raised when a review timer or decision record is invalid."""


def canonical_sha256(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def session_digest(session: dict) -> str:
    """Canonical exact-record digest used by run-ledger review references."""
    return canonical_sha256(session)


def parse_time(value: object) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ReviewSessionError("review timestamps must be UTC Z strings")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ReviewSessionError("review timestamp is invalid") from error


def subject_errors(subject: dict) -> list[str]:
    errors = []
    if not subject.get("record_id") or not subject.get("path"):
        errors.append("subject identity/path missing")
    if not SHA256.fullmatch(str(subject.get("sha256", ""))):
        errors.append("subject sha256 missing or invalid")
    return errors


def decision_errors(decisions: object, subjects: list[dict]) -> list[str]:
    if not isinstance(decisions, list):
        return ["decisions missing"]
    errors = []
    expected = [item["record_id"] for item in subjects]
    actual = [item.get("subject_record_id") for item in decisions]
    if sorted(actual) != sorted(expected) or len(actual) != len(set(actual)):
        errors.append("decisions must cover every subject exactly once")
    for decision in decisions:
        if not isinstance(decision.get("accepted"), bool):
            errors.append("decision accepted flag missing")
        assertions = decision.get("hard_assertions")
        if not isinstance(assertions, list) or not assertions:
            errors.append("decision hard assertions missing")
        elif decision.get("accepted") and any(item.get("passed") is not True for item in assertions):
            errors.append("accepted decision contains failed assertion")
        if decision.get("accepted") is False and not decision.get("failure_tags"):
            errors.append("rejected decision failure tags missing")
    return sorted(set(errors))


def active_seconds(events: list[dict]) -> float | None:
    if not events or events[0].get("event_type") != "START":
        return None
    active_start = parse_time(events[0]["occurred_at"])
    total = 0.0
    for event in events[1:]:
        instant = parse_time(event["occurred_at"])
        if event["event_type"] in {"PAUSE", "COMPLETE"}:
            total += (instant - active_start).total_seconds()
        elif event["event_type"] == "RESUME":
            active_start = instant
    return total if events[-1].get("event_type") == "COMPLETE" else None


def refresh_summary(session: dict) -> None:
    events = session["events"]
    completed = bool(events and events[-1]["event_type"] == "COMPLETE")
    seconds = active_seconds(events)
    session["summary"] = {
        "started_at": events[0]["occurred_at"] if events else None,
        "completed_at": events[-1]["occurred_at"] if completed else None,
        "active_seconds": round(seconds, 3) if seconds is not None else None,
        "human_minutes": round(seconds / 60, 3) if seconds is not None else None,
        "decision_count": len(events[-1].get("data", {}).get("decisions", [])) if completed else 0,
        "review_evidence_eligible": completed and not session.get("validation_fixture", False),
    }


def start_session(
    *, session_id: str, reviewer_id: str, subjects: list[dict], started_at: str, validation_fixture: bool = False
) -> dict:
    if not session_id or not reviewer_id or not subjects:
        raise ReviewSessionError("session, reviewer, and subjects are required")
    errors = [error for subject in subjects for error in subject_errors(subject)]
    if errors or len({item["record_id"] for item in subjects}) != len(subjects):
        raise ReviewSessionError("invalid or duplicate review subjects: " + "; ".join(errors))
    parse_time(started_at)
    session = {
        "record_type": "TimedHumanReviewSession",
        "schema_version": "1.0",
        "session_id": session_id,
        "record_id": session_id,
        "state": "ACTIVE",
        "reviewer_id": reviewer_id,
        "validation_fixture": validation_fixture,
        "subjects": copy.deepcopy(subjects),
        "events": [],
        "summary": {},
    }
    refresh_summary(session)
    return append_event(session, event_type="START", occurred_at=started_at, data={})


def append_event(session: dict, *, event_type: str, occurred_at: str, data: dict) -> dict:
    existing_errors = validate_session(session, allow_empty_events=True)
    if existing_errors:
        raise ReviewSessionError("invalid existing session: " + "; ".join(existing_errors))
    state = session.get("state")
    allowed = {
        "ACTIVE": {"PAUSE", "COMPLETE"},
        "PAUSED": {"RESUME"},
        "COMPLETED": set(),
    }
    if not session["events"]:
        if event_type != "START" or state != "ACTIVE":
            raise ReviewSessionError("first event must START an active session")
    elif event_type not in allowed.get(state, set()):
        raise ReviewSessionError(f"review transition not allowed: {state}->{event_type}")
    instant = parse_time(occurred_at)
    if session["events"] and instant <= parse_time(session["events"][-1]["occurred_at"]):
        raise ReviewSessionError("review event timestamps must increase")
    if event_type == "COMPLETE":
        errors = decision_errors(data.get("decisions"), session["subjects"])
        if errors:
            raise ReviewSessionError("; ".join(errors))
    event = {
        "sequence": len(session["events"]) + 1,
        "event_type": event_type,
        "occurred_at": occurred_at,
        "data": copy.deepcopy(data),
        "previous_event_sha256": session["events"][-1]["event_sha256"] if session["events"] else GENESIS,
    }
    event["event_sha256"] = canonical_sha256(event)
    updated = copy.deepcopy(session)
    updated["events"].append(event)
    updated["state"] = {"START": "ACTIVE", "PAUSE": "PAUSED", "RESUME": "ACTIVE", "COMPLETE": "COMPLETED"}[event_type]
    refresh_summary(updated)
    errors = validate_session(updated)
    if errors:
        raise ReviewSessionError("invalid resulting session: " + "; ".join(errors))
    return updated


def validate_session(session: dict, *, allow_empty_events: bool = False) -> list[str]:
    errors = []
    if session.get("record_type") != "TimedHumanReviewSession" or session.get("schema_version") != "1.0":
        errors.append("session schema invalid")
    if not session.get("session_id") or session.get("record_id") != session.get("session_id") or not session.get("reviewer_id"):
        errors.append("session/reviewer identity missing")
    subjects = session.get("subjects", [])
    if not subjects or any(subject_errors(item) for item in subjects):
        errors.append("review subjects invalid")
    events = session.get("events", [])
    if not events and not allow_empty_events:
        errors.append("review events missing")
    previous, prior_time, expected_state = GENESIS, None, "ACTIVE"
    for index, event in enumerate(events, 1):
        copy_event = copy.deepcopy(event)
        claimed = copy_event.pop("event_sha256", None)
        if event.get("sequence") != index:
            errors.append(f"event {index} sequence invalid")
        if event.get("previous_event_sha256") != previous:
            errors.append(f"event {index} previous hash mismatch")
        if claimed != canonical_sha256(copy_event):
            errors.append(f"event {index} hash mismatch")
        try:
            instant = parse_time(event.get("occurred_at"))
            if prior_time is not None and instant <= prior_time:
                errors.append(f"event {index} timestamp not increasing")
            prior_time = instant
        except ReviewSessionError:
            errors.append(f"event {index} timestamp invalid")
        event_type = event.get("event_type")
        if index == 1 and event_type != "START":
            errors.append("first event is not START")
        elif index > 1:
            allowed = {"ACTIVE": {"PAUSE", "COMPLETE"}, "PAUSED": {"RESUME"}, "COMPLETED": set()}
            if event_type not in allowed.get(expected_state, set()):
                errors.append(f"event {index} transition invalid")
        if event_type == "COMPLETE":
            errors.extend(decision_errors(event.get("data", {}).get("decisions"), subjects))
        expected_state = {"START": "ACTIVE", "PAUSE": "PAUSED", "RESUME": "ACTIVE", "COMPLETE": "COMPLETED"}.get(event_type, "INVALID")
        previous = claimed
    if events and session.get("state") != expected_state:
        errors.append("session state mismatch")
    expected_summary = copy.deepcopy(session)
    refresh_summary(expected_summary)
    if session.get("summary") != expected_summary.get("summary"):
        errors.append("session summary mismatch")
    return sorted(set(errors))
