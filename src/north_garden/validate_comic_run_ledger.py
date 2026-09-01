"""Validate CH05 preflight ledgers and adversarial lifecycle transitions."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from comic_run_ledger import (
    RunLedgerError,
    append_event,
    new_ledger,
    validate_ledger,
    validate_review_binding,
    validate_reservation_bindings,
)
from review_session import append_event as append_review_event
from review_session import session_digest, start_session


ROOT = Path(__file__).resolve().parents[2]
COLLECTION = ROOT / "production/comic/run-ledgers/ch05-p033-p038-local-preflight-r1.json"
STAMP = "2026-09-01T16:12:20Z"
HASH = "0" * 64
SCOPE = {
    "external_provider": "test-provider",
    "external_model_snapshot": "test-model-snapshot",
    "external_endpoint": "https://example.invalid/v1/edit",
}


def ref(record_id: str) -> dict:
    return {"record_id": record_id, "path": f"test/{record_id}.json", "sha256": HASH}


def advance(ledger: dict, index: int, state: str, data: dict) -> dict:
    return append_event(
        ledger,
        event_id=f"test-event-{index}-{state.lower()}",
        occurred_at=STAMP,
        to_state=state,
        data=data,
    )


def complete_control(timed_session_ref: dict) -> dict:
    ledger = new_ledger(ledger_id="test-ledger", panel_id="test-panel", plan_revision_id="test-plan-r1")
    steps = [
        ("BASE_APPROVAL_PENDING", {"reason": "test pending"}),
        ("LOCAL_BASE_APPROVED", {"base_approval": ref("base-approval")}),
        ("MASK_REVIEW_PENDING", {"base_approval_id": "base-approval"}),
        ("LOCAL_REPAIR_READY", {"mask_review": ref("mask-review")}),
        ("EXTERNAL_AUTHORITY_PENDING", {"proposed_scope": SCOPE}),
        ("BUDGET_RESERVED", {
            "authority_record": ref("external-authority"),
            "authorized_scope": SCOPE,
            "reservation": {
                "aggregate_ledger": ref("aggregate-ledger"), "reservation_id": "reservation-1",
                "adapter_id": "test-adapter", "reserved_usd": "0.50",
            },
        }),
        ("SUBMITTED", {"request": {
            "reservation_id": "reservation-1", "provider_request_id": "request-1",
            "request_sha256": HASH, "submitted_at": STAMP,
        }}),
        ("COMPLETED", {
            "provider_request_id": "request-1",
            "render_record": ref("render-record-1"), "output_sha256": [HASH],
            "timing_seconds": 1.0, "actual_cost_usd": "0.10", "cost_reconciliation": ref("cost-reconciliation-1"),
        }),
        ("HUMAN_REVIEW_PENDING", {"review_subject": ref("render-record-1")}),
        ("ACCEPTED", {"review": {
            "review_subject_id": "render-record-1", "human_review_status": "completed",
            "reviewer_id": "synthetic-reviewer", "human_minutes": 1.0, "accepted": True,
            "hard_assertions": [{"id": "test-assertion", "passed": True}], "failure_tags": [],
            "timed_review_session": timed_session_ref,
        }}),
    ]
    for index, (state, data) in enumerate(steps, 1):
        ledger = advance(ledger, index, state, data)
    return ledger


def must_reject(label: str, action, failures: list[str]) -> None:
    try:
        action()
    except RunLedgerError:
        return
    failures.append(f"adversarial transition passed: {label}")


def main() -> int:
    failures = []
    collection = json.loads(COLLECTION.read_text(encoding="utf-8"))
    if collection.get("medium") != "comic" or collection.get("animation_shot_plan") is not None:
        failures.append("collection medium boundary invalid")
    if collection["panel_ids"] != [f"ng-ch05-sc01-p{value:03d}" for value in range(33, 39)]:
        failures.append("collection panel IDs are not contiguous P033-P038")
    for ledger in collection["ledgers"]:
        errors = validate_ledger(ledger)
        if errors:
            failures.append(f"tracked ledger invalid: {ledger['panel_id']}:{errors}")
        if ledger["current_state"] != "BASE_APPROVAL_PENDING":
            failures.append(f"tracked ledger advanced unexpectedly: {ledger['panel_id']}")
    aggregate = collection["aggregate"]
    if aggregate["BASE_APPROVAL_PENDING"] != 6 or aggregate["executable_panels"] != 0:
        failures.append("tracked aggregate readiness mismatch")
    if any(aggregate[field] != 0 for field in ("provider_requests", "external_uploads", "accepted_panels")):
        failures.append("tracked aggregate execution/acceptance is nonzero")
    if aggregate["external_cost_usd"] != "0.000000" or aggregate["human_minutes"] is not None:
        failures.append("tracked aggregate cost/minutes invalid")

    timed_session = start_session(
        session_id="timed-session-1", reviewer_id="synthetic-reviewer",
        subjects=[ref("render-record-1")], started_at="2026-09-01T16:00:00Z", validation_fixture=True,
    )
    timed_session = append_review_event(
        timed_session, event_type="COMPLETE", occurred_at="2026-09-01T16:01:00Z",
        data={"decisions": [{
            "subject_record_id": "render-record-1", "accepted": True,
            "hard_assertions": [{"id": "test-assertion", "passed": True}], "failure_tags": [],
        }]},
    )
    timed_ref = {"record_id": "timed-session-1", "path": "test/timed-session-1.json", "sha256": session_digest(timed_session)}
    completed = complete_control(timed_ref)
    if validate_ledger(completed) or completed["current_state"] != "ACCEPTED":
        failures.append("valid full lifecycle control did not reach ACCEPTED")
    aggregate = {
        "record_id": "aggregate-ledger",
        "entries": [{
            "reservation_id": "reservation-1", "adapter_id": "test-adapter", "state": "committed",
            "reserved_usd": "0.50", "actual_cost_usd": "0.10", "provider_request_id": "request-1",
        }],
    }
    if validate_reservation_bindings(completed, aggregate):
        failures.append("valid aggregate reservation binding did not pass")
    if validate_review_binding(completed, timed_session, validation_mode=True):
        failures.append("valid timed review binding did not pass")
    if not validate_review_binding(completed, timed_session):
        failures.append("validation fixture counted as real review evidence")

    planned = new_ledger(ledger_id="mutation", panel_id="panel", plan_revision_id="plan")
    pending = advance(planned, 1, "BASE_APPROVAL_PENDING", {"reason": "test"})
    base = advance(pending, 2, "LOCAL_BASE_APPROVED", {"base_approval": ref("base")})
    external = advance(base, 3, "EXTERNAL_AUTHORITY_PENDING", {"proposed_scope": SCOPE})
    reserved = advance(external, 4, "BUDGET_RESERVED", {
        "authority_record": ref("authority"), "authorized_scope": SCOPE,
        "reservation": {
            "aggregate_ledger": ref("aggregate"), "reservation_id": "reservation",
            "adapter_id": "test-adapter", "reserved_usd": "1",
        },
    })
    submitted = advance(reserved, 5, "SUBMITTED", {"request": {
        "reservation_id": "reservation", "provider_request_id": "request", "request_sha256": HASH, "submitted_at": STAMP,
    }})

    must_reject("skip approvals", lambda: advance(planned, 1, "SUBMITTED", {}), failures)
    must_reject("base missing hash", lambda: advance(pending, 2, "LOCAL_BASE_APPROVED", {"base_approval": {}}), failures)
    must_reject("scope mismatch", lambda: advance(external, 4, "BUDGET_RESERVED", {
        "authority_record": ref("authority"), "authorized_scope": {**SCOPE, "external_model_snapshot": "wrong"},
        "reservation": {
            "aggregate_ledger": ref("aggregate"), "reservation_id": "reservation",
            "adapter_id": "test-adapter", "reserved_usd": "1",
        },
    }), failures)
    must_reject("reservation absent", lambda: advance(external, 4, "BUDGET_RESERVED", {
        "authority_record": ref("authority"), "authorized_scope": SCOPE,
    }), failures)
    must_reject("submission reservation mismatch", lambda: advance(reserved, 5, "SUBMITTED", {"request": {
        "reservation_id": "wrong", "provider_request_id": "request", "request_sha256": HASH, "submitted_at": STAMP,
    }}), failures)
    must_reject("completion missing RenderRecord", lambda: advance(submitted, 6, "COMPLETED", {
        "provider_request_id": "request", "output_sha256": [HASH], "timing_seconds": 1, "actual_cost_usd": "0.1",
    }), failures)
    must_reject("completion request mismatch", lambda: advance(submitted, 6, "COMPLETED", {
        "provider_request_id": "wrong", "render_record": ref("render"), "output_sha256": [HASH],
        "timing_seconds": 1, "actual_cost_usd": "0.1", "cost_reconciliation": ref("cost"),
    }), failures)

    for label, mutate in [
        ("aggregate reservation missing", lambda x: x.update(entries=[])),
        ("aggregate adapter mismatch", lambda x: x["entries"][0].update(adapter_id="wrong")),
        ("aggregate request mismatch", lambda x: x["entries"][0].update(provider_request_id="wrong")),
        ("aggregate cost mismatch", lambda x: x["entries"][0].update(actual_cost_usd="0.11")),
    ]:
        candidate = copy.deepcopy(aggregate)
        mutate(candidate)
        if not validate_reservation_bindings(completed, candidate):
            failures.append(f"aggregate binding mutation passed: {label}")

    before_accept = copy.deepcopy(completed)
    accept_event = before_accept["events"].pop()
    before_accept["current_state"] = "HUMAN_REVIEW_PENDING"
    before_accept["events"][-1]["event_sha256"] = before_accept["events"][-1]["event_sha256"]
    must_reject("untimed acceptance", lambda: advance(before_accept, 10, "ACCEPTED", {"review": {
        "review_subject_id": "render-record-1", "human_review_status": "completed", "human_minutes": None,
        "reviewer_id": "synthetic-reviewer", "accepted": True,
        "hard_assertions": [{"id": "test", "passed": True}], "failure_tags": [], "timed_review_session": timed_ref,
    }}), failures)
    must_reject("failed assertion acceptance", lambda: advance(before_accept, 10, "ACCEPTED", {"review": {
        "review_subject_id": "render-record-1", "human_review_status": "completed", "human_minutes": 1,
        "reviewer_id": "synthetic-reviewer", "accepted": True,
        "hard_assertions": [{"id": "test", "passed": False}], "failure_tags": [], "timed_review_session": timed_ref,
    }}), failures)
    must_reject("terminal advance", lambda: advance(completed, 11, "HUMAN_REVIEW_PENDING", {"review_subject": ref("render")}), failures)

    for label, mutate in [
        ("event hash tamper", lambda x: x["events"][0]["data"].update(reason="tampered")),
        ("sequence tamper", lambda x: x["events"][0].update(sequence=2)),
        ("current state tamper", lambda x: x.update(current_state="COMPLETED")),
        ("previous hash tamper", lambda x: x["events"][0].update(previous_event_sha256=HASH)),
    ]:
        candidate = copy.deepcopy(pending)
        mutate(candidate)
        if not validate_ledger(candidate):
            failures.append(f"ledger tamper passed: {label}")

    for label, mutate in [
        ("timed reviewer mismatch", lambda x: x.update(reviewer_id="wrong")),
        ("timed minutes mismatch", lambda x: x["summary"].update(human_minutes=2.0)),
        ("timed subject mismatch", lambda x: x["subjects"][0].update(record_id="wrong")),
    ]:
        candidate = copy.deepcopy(timed_session)
        mutate(candidate)
        if not validate_review_binding(completed, candidate, validation_mode=True):
            failures.append(f"timed review binding mutation passed: {label}")

    for failure in failures:
        print(f"failure: {failure}")
    if failures:
        return 1
    print("0 failures, 0 warnings (6 ledgers pending; 22/22 transition, tamper, aggregate, and timed-review mutations rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
