"""Adversarial validation of measured, immutable human-review session records."""
from __future__ import annotations

import copy

from review_session import ReviewSessionError, append_event, start_session, validate_session


SUBJECTS = [
    {"record_id": "subject-1", "path": "test/subject-1.json", "sha256": "0" * 64},
    {"record_id": "subject-2", "path": "test/subject-2.json", "sha256": "1" * 64},
]
DECISIONS = [
    {"subject_record_id": "subject-1", "accepted": True, "hard_assertions": [{"id": "a", "passed": True}], "failure_tags": []},
    {"subject_record_id": "subject-2", "accepted": False, "hard_assertions": [{"id": "b", "passed": False}], "failure_tags": ["TEST_REJECT"]},
]


def must_fail(label: str, action, failures: list[str]) -> None:
    try:
        action()
    except ReviewSessionError:
        return
    failures.append(f"review mutation passed: {label}")


def main() -> int:
    failures = []
    session = start_session(
        session_id="synthetic-session", reviewer_id="synthetic-validator-not-human",
        subjects=SUBJECTS, started_at="2026-09-01T16:00:00Z", validation_fixture=True,
    )
    session = append_event(session, event_type="PAUSE", occurred_at="2026-09-01T16:05:00Z", data={"reason": "synthetic pause"})
    session = append_event(session, event_type="RESUME", occurred_at="2026-09-01T16:15:00Z", data={})
    session = append_event(session, event_type="COMPLETE", occurred_at="2026-09-01T16:25:00Z", data={"decisions": DECISIONS})
    if validate_session(session):
        failures.append("valid synthetic review session did not validate")
    summary = session["summary"]
    if summary["active_seconds"] != 900 or summary["human_minutes"] != 15 or summary["review_evidence_eligible"]:
        failures.append("active review time or fixture eligibility is incorrect")

    active = start_session(
        session_id="mutation-session", reviewer_id="synthetic-validator-not-human",
        subjects=SUBJECTS, started_at="2026-09-01T16:00:00Z", validation_fixture=True,
    )
    must_fail("backward time", lambda: append_event(active, event_type="COMPLETE", occurred_at="2026-09-01T15:59:00Z", data={"decisions": DECISIONS}), failures)
    must_fail("pause then complete", lambda: append_event(
        append_event(active, event_type="PAUSE", occurred_at="2026-09-01T16:01:00Z", data={}),
        event_type="COMPLETE", occurred_at="2026-09-01T16:02:00Z", data={"decisions": DECISIONS},
    ), failures)
    missing = copy.deepcopy(DECISIONS[:-1])
    must_fail("missing subject", lambda: append_event(active, event_type="COMPLETE", occurred_at="2026-09-01T16:01:00Z", data={"decisions": missing}), failures)
    duplicate = [DECISIONS[0], DECISIONS[0]]
    must_fail("duplicate subject", lambda: append_event(active, event_type="COMPLETE", occurred_at="2026-09-01T16:01:00Z", data={"decisions": duplicate}), failures)
    accepted_failure = copy.deepcopy(DECISIONS)
    accepted_failure[0]["hard_assertions"][0]["passed"] = False
    must_fail("accepted failed assertion", lambda: append_event(active, event_type="COMPLETE", occurred_at="2026-09-01T16:01:00Z", data={"decisions": accepted_failure}), failures)
    no_tags = copy.deepcopy(DECISIONS)
    no_tags[1]["failure_tags"] = []
    must_fail("rejection no tags", lambda: append_event(active, event_type="COMPLETE", occurred_at="2026-09-01T16:01:00Z", data={"decisions": no_tags}), failures)
    must_fail("terminal append", lambda: append_event(session, event_type="PAUSE", occurred_at="2026-09-01T16:30:00Z", data={}), failures)

    for label, mutate in [
        ("event data", lambda x: x["events"][0]["data"].update(tampered=True)),
        ("previous hash", lambda x: x["events"][1].update(previous_event_sha256="f" * 64)),
        ("summary minutes", lambda x: x["summary"].update(human_minutes=999)),
    ]:
        changed = copy.deepcopy(session)
        mutate(changed)
        if not validate_session(changed):
            failures.append(f"session tamper passed: {label}")

    for failure in failures:
        print(f"failure: {failure}")
    if failures:
        return 1
    print("0 failures, 0 warnings (15 active minutes computed; fixture ineligible; 10/10 mutations rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
