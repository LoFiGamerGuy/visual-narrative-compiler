"""Hash-chained lifecycle ledger for panel-addressable comic production runs."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation


SHA256 = re.compile(r"^[0-9a-f]{64}$")
GENESIS = "GENESIS"
STATES = {
    "PLANNED",
    "BASE_APPROVAL_PENDING",
    "LOCAL_BASE_APPROVED",
    "MASK_REVIEW_PENDING",
    "LOCAL_REPAIR_READY",
    "EXTERNAL_AUTHORITY_PENDING",
    "BUDGET_RESERVED",
    "SUBMITTED",
    "COMPLETED",
    "FAILED",
    "HUMAN_REVIEW_PENDING",
    "ACCEPTED",
    "REJECTED",
}
ALLOWED = {
    "PLANNED": {"BASE_APPROVAL_PENDING"},
    "BASE_APPROVAL_PENDING": {"LOCAL_BASE_APPROVED"},
    "LOCAL_BASE_APPROVED": {"MASK_REVIEW_PENDING", "EXTERNAL_AUTHORITY_PENDING"},
    "MASK_REVIEW_PENDING": {"LOCAL_REPAIR_READY"},
    "LOCAL_REPAIR_READY": {"EXTERNAL_AUTHORITY_PENDING"},
    "EXTERNAL_AUTHORITY_PENDING": {"BUDGET_RESERVED"},
    "BUDGET_RESERVED": {"SUBMITTED", "EXTERNAL_AUTHORITY_PENDING"},
    "SUBMITTED": {"COMPLETED", "FAILED"},
    "COMPLETED": {"HUMAN_REVIEW_PENDING"},
    "FAILED": {"HUMAN_REVIEW_PENDING"},
    "HUMAN_REVIEW_PENDING": {"ACCEPTED", "REJECTED"},
    "ACCEPTED": set(),
    "REJECTED": set(),
}


class RunLedgerError(ValueError):
    """Raised when a ledger or transition violates production invariants."""


def canonical_sha256(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha_ref_errors(value: object, label: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{label}:missing"]
    errors = []
    if not value.get("record_id"):
        errors.append(f"{label}:record_id_missing")
    if not value.get("path"):
        errors.append(f"{label}:path_missing")
    if not SHA256.fullmatch(str(value.get("sha256", ""))):
        errors.append(f"{label}:sha256_missing_or_invalid")
    return errors


def exact_scope_errors(value: object, label: str = "external_scope") -> list[str]:
    if not isinstance(value, dict):
        return [f"{label}:missing"]
    return [
        f"{label}:{field}_missing"
        for field in ("external_provider", "external_model_snapshot", "external_endpoint")
        if not value.get(field)
    ]


def positive_decimal(value: object, label: str) -> list[str]:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return [f"{label}:not_decimal"]
    if not parsed.is_finite() or parsed <= 0:
        return [f"{label}:not_positive"]
    return []


def transition_data_errors(to_state: str, data: dict) -> list[str]:
    errors = []
    if to_state == "BASE_APPROVAL_PENDING" and not data.get("reason"):
        errors.append("base_pending:reason_missing")
    elif to_state == "LOCAL_BASE_APPROVED":
        errors.extend(sha_ref_errors(data.get("base_approval"), "base_approval"))
    elif to_state == "MASK_REVIEW_PENDING" and not data.get("base_approval_id"):
        errors.append("mask_pending:base_approval_id_missing")
    elif to_state == "LOCAL_REPAIR_READY":
        errors.extend(sha_ref_errors(data.get("mask_review"), "mask_review"))
    elif to_state == "EXTERNAL_AUTHORITY_PENDING":
        errors.extend(exact_scope_errors(data.get("proposed_scope"), "proposed_scope"))
    elif to_state == "BUDGET_RESERVED":
        errors.extend(sha_ref_errors(data.get("authority_record"), "authority_record"))
        errors.extend(exact_scope_errors(data.get("authorized_scope"), "authorized_scope"))
        reservation = data.get("reservation")
        if not isinstance(reservation, dict):
            errors.append("reservation:missing")
        else:
            errors.extend(sha_ref_errors(reservation.get("aggregate_ledger"), "reservation:aggregate_ledger"))
            for field in ("reservation_id", "adapter_id"):
                if not reservation.get(field):
                    errors.append(f"reservation:{field}_missing")
            errors.extend(positive_decimal(reservation.get("reserved_usd"), "reservation:reserved_usd"))
    elif to_state == "SUBMITTED":
        request = data.get("request")
        if not isinstance(request, dict):
            errors.append("request:missing")
        else:
            for field in ("reservation_id", "provider_request_id", "submitted_at"):
                if not request.get(field):
                    errors.append(f"request:{field}_missing")
            if not SHA256.fullmatch(str(request.get("request_sha256", ""))):
                errors.append("request:sha256_missing_or_invalid")
    elif to_state == "COMPLETED":
        errors.extend(sha_ref_errors(data.get("render_record"), "render_record"))
        errors.extend(sha_ref_errors(data.get("cost_reconciliation"), "cost_reconciliation"))
        if not data.get("provider_request_id"):
            errors.append("completion:provider_request_id_missing")
        if not data.get("output_sha256") or any(not SHA256.fullmatch(str(item)) for item in data.get("output_sha256", [])):
            errors.append("completion:output_sha256_missing_or_invalid")
        if not isinstance(data.get("timing_seconds"), (int, float)) or data.get("timing_seconds", 0) <= 0:
            errors.append("completion:timing_missing_or_invalid")
        try:
            cost = Decimal(str(data.get("actual_cost_usd")))
            if not cost.is_finite() or cost < 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            errors.append("completion:actual_cost_missing_or_invalid")
    elif to_state == "FAILED":
        errors.extend(sha_ref_errors(data.get("failure_record"), "failure_record"))
        errors.extend(sha_ref_errors(data.get("cost_reconciliation"), "cost_reconciliation"))
    elif to_state == "HUMAN_REVIEW_PENDING":
        errors.extend(sha_ref_errors(data.get("review_subject"), "review_subject"))
    elif to_state in {"ACCEPTED", "REJECTED"}:
        review = data.get("review")
        if not isinstance(review, dict):
            errors.append("review:missing")
        else:
            if review.get("human_review_status") != "completed":
                errors.append("review:not_completed")
            if not isinstance(review.get("human_minutes"), (int, float)) or review.get("human_minutes", 0) <= 0:
                errors.append("review:positive_minutes_missing")
            expected = to_state == "ACCEPTED"
            if review.get("accepted") is not expected:
                errors.append("review:decision_mismatch")
            assertions = review.get("hard_assertions")
            if not isinstance(assertions, list) or not assertions:
                errors.append("review:hard_assertions_missing")
            elif expected and any(item.get("passed") is not True for item in assertions):
                errors.append("review:accepted_with_failed_assertion")
            if not expected and not review.get("failure_tags"):
                errors.append("review:rejection_failure_tags_missing")
            if not review.get("review_subject_id"):
                errors.append("review:review_subject_id_missing")
            errors.extend(sha_ref_errors(review.get("timed_review_session"), "review:timed_review_session"))
    return sorted(set(errors))


def new_ledger(*, ledger_id: str, panel_id: str, plan_revision_id: str) -> dict:
    if not all((ledger_id, panel_id, plan_revision_id)):
        raise RunLedgerError("ledger identity fields are required")
    return {
        "record_type": "ComicPanelRunLedger",
        "schema_version": "1.0",
        "ledger_id": ledger_id,
        "medium": "comic",
        "animation_shot_plan": None,
        "panel_id": panel_id,
        "plan_revision_id": plan_revision_id,
        "initial_state": "PLANNED",
        "current_state": "PLANNED",
        "events": [],
    }


def append_event(
    ledger: dict,
    *,
    event_id: str,
    occurred_at: str,
    to_state: str,
    data: dict,
) -> dict:
    errors = validate_ledger(ledger)
    if errors:
        raise RunLedgerError("invalid existing ledger: " + "; ".join(errors))
    from_state = ledger["current_state"]
    if to_state not in ALLOWED.get(from_state, set()):
        raise RunLedgerError(f"transition not allowed: {from_state}->{to_state}")
    data_errors = transition_data_errors(to_state, data)
    if data_errors:
        raise RunLedgerError("invalid transition data: " + "; ".join(data_errors))
    if any(item["event_id"] == event_id for item in ledger["events"]):
        raise RunLedgerError(f"duplicate event_id: {event_id}")
    event = {
        "sequence": len(ledger["events"]) + 1,
        "event_id": event_id,
        "occurred_at": occurred_at,
        "from_state": from_state,
        "to_state": to_state,
        "data": copy.deepcopy(data),
        "previous_event_sha256": ledger["events"][-1]["event_sha256"] if ledger["events"] else GENESIS,
    }
    event["event_sha256"] = canonical_sha256(event)
    updated = copy.deepcopy(ledger)
    updated["events"].append(event)
    updated["current_state"] = to_state
    updated_errors = validate_ledger(updated)
    if updated_errors:
        raise RunLedgerError("invalid resulting ledger: " + "; ".join(updated_errors))
    return updated


def validate_ledger(ledger: dict) -> list[str]:
    errors = []
    if ledger.get("record_type") != "ComicPanelRunLedger" or ledger.get("schema_version") != "1.0":
        errors.append("ledger_schema_invalid")
    if ledger.get("medium") != "comic" or ledger.get("animation_shot_plan") is not None:
        errors.append("medium_or_animation_boundary")
    if not all(ledger.get(field) for field in ("ledger_id", "panel_id", "plan_revision_id")):
        errors.append("ledger_identity_missing")
    if ledger.get("initial_state") != "PLANNED":
        errors.append("initial_state_invalid")
    state, previous = "PLANNED", GENESIS
    proposed_scope = None
    reservation_id = None
    provider_request_id = None
    review_subject_id = None
    event_ids = set()
    for expected_sequence, event in enumerate(ledger.get("events", []), 1):
        event_copy = copy.deepcopy(event)
        claimed_hash = event_copy.pop("event_sha256", None)
        if event.get("sequence") != expected_sequence:
            errors.append(f"event_{expected_sequence}:sequence_invalid")
        if not event.get("event_id") or event.get("event_id") in event_ids:
            errors.append(f"event_{expected_sequence}:event_id_missing_or_duplicate")
        if not event.get("occurred_at"):
            errors.append(f"event_{expected_sequence}:occurred_at_missing")
        event_ids.add(event.get("event_id"))
        if event.get("previous_event_sha256") != previous:
            errors.append(f"event_{expected_sequence}:previous_hash_mismatch")
        if claimed_hash != canonical_sha256(event_copy):
            errors.append(f"event_{expected_sequence}:event_hash_mismatch")
        if event.get("from_state") != state or event.get("to_state") not in ALLOWED.get(state, set()):
            errors.append(f"event_{expected_sequence}:transition_invalid")
        errors.extend(f"event_{expected_sequence}:{item}" for item in transition_data_errors(event.get("to_state"), event.get("data", {})))
        data = event.get("data", {})
        if event.get("to_state") == "EXTERNAL_AUTHORITY_PENDING":
            proposed_scope = data.get("proposed_scope")
        elif event.get("to_state") == "BUDGET_RESERVED":
            if data.get("authorized_scope") != proposed_scope:
                errors.append(f"event_{expected_sequence}:authorized_scope_does_not_match_proposal")
            reservation_id = data.get("reservation", {}).get("reservation_id")
        elif event.get("from_state") == "BUDGET_RESERVED" and event.get("to_state") == "EXTERNAL_AUTHORITY_PENDING":
            errors.extend(
                f"event_{expected_sequence}:{item}"
                for item in sha_ref_errors(data.get("released_reservation"), "released_reservation")
            )
        elif event.get("to_state") == "SUBMITTED":
            if data.get("request", {}).get("reservation_id") != reservation_id:
                errors.append(f"event_{expected_sequence}:submission_reservation_mismatch")
            provider_request_id = data.get("request", {}).get("provider_request_id")
        elif event.get("to_state") == "COMPLETED":
            if data.get("provider_request_id") != provider_request_id:
                errors.append(f"event_{expected_sequence}:completion_request_mismatch")
            review_subject_id = data.get("render_record", {}).get("record_id")
        elif event.get("to_state") == "FAILED":
            review_subject_id = data.get("failure_record", {}).get("record_id")
        elif event.get("to_state") == "HUMAN_REVIEW_PENDING":
            if data.get("review_subject", {}).get("record_id") != review_subject_id:
                errors.append(f"event_{expected_sequence}:review_subject_mismatch")
        elif event.get("to_state") in {"ACCEPTED", "REJECTED"}:
            if data.get("review", {}).get("review_subject_id") != review_subject_id:
                errors.append(f"event_{expected_sequence}:review_decision_subject_mismatch")
        state = event.get("to_state")
        previous = claimed_hash
    if ledger.get("current_state") != state:
        errors.append("current_state_mismatch")
    return sorted(set(errors))


def validate_reservation_bindings(ledger: dict, aggregate_ledger: dict) -> list[str]:
    """Bind run events to exact entries in an externally supplied aggregate ledger."""
    errors = validate_ledger(ledger)
    if errors:
        return errors
    entries = {item.get("reservation_id"): item for item in aggregate_ledger.get("entries", [])}
    aggregate_id = aggregate_ledger.get("record_id")
    reservation_event = next((item for item in ledger["events"] if item["to_state"] == "BUDGET_RESERVED"), None)
    if reservation_event is None:
        return []
    declared = reservation_event["data"]["reservation"]
    ledger_ref = declared["aggregate_ledger"]
    if ledger_ref.get("record_id") != aggregate_id:
        errors.append("aggregate_ledger_record_id_mismatch")
    entry = entries.get(declared["reservation_id"])
    if entry is None:
        return sorted(set([*errors, "aggregate_reservation_missing"]))
    if entry.get("adapter_id") != declared.get("adapter_id"):
        errors.append("aggregate_reservation_adapter_mismatch")
    try:
        if Decimal(str(entry.get("reserved_usd"))) != Decimal(str(declared.get("reserved_usd"))):
            errors.append("aggregate_reservation_amount_mismatch")
    except (InvalidOperation, ValueError):
        errors.append("aggregate_reservation_amount_invalid")
    if entry.get("state") == "released":
        errors.append("aggregate_reservation_released")

    submitted = next((item for item in ledger["events"] if item["to_state"] == "SUBMITTED"), None)
    if submitted is not None:
        request_id = submitted["data"]["request"]["provider_request_id"]
        if entry.get("state") not in {"awaiting_reconciliation", "committed"}:
            errors.append("submitted_request_reservation_not_held_or_committed")
        if entry.get("provider_request_id") != request_id:
            errors.append("aggregate_provider_request_id_mismatch")
    completed = next((item for item in ledger["events"] if item["to_state"] == "COMPLETED"), None)
    if completed is not None:
        if entry.get("state") != "committed":
            errors.append("completed_request_cost_not_committed")
        try:
            if Decimal(str(entry.get("actual_cost_usd"))) != Decimal(str(completed["data"]["actual_cost_usd"])):
                errors.append("aggregate_actual_cost_mismatch")
        except (InvalidOperation, ValueError):
            errors.append("aggregate_actual_cost_invalid")
    return sorted(set(errors))


def validate_review_binding(ledger: dict, timed_session: dict, *, validation_mode: bool = False) -> list[str]:
    """Bind a terminal panel decision to an eligible completed timed session."""
    from review_session import session_digest, validate_session

    errors = validate_ledger(ledger)
    if errors:
        return errors
    terminal = next(
        (item for item in reversed(ledger["events"]) if item["to_state"] in {"ACCEPTED", "REJECTED"}),
        None,
    )
    if terminal is None:
        return []
    review = terminal["data"]["review"]
    reference = review["timed_review_session"]
    if reference.get("record_id") != timed_session.get("record_id"):
        errors.append("timed_review_session_record_id_mismatch")
    if reference.get("sha256") != session_digest(timed_session):
        errors.append("timed_review_session_sha256_mismatch")
    session_errors = validate_session(timed_session)
    if session_errors:
        errors.extend(f"timed_session_invalid:{item}" for item in session_errors)
    eligible = timed_session.get("summary", {}).get("review_evidence_eligible") is True
    fixture_allowed = validation_mode and timed_session.get("validation_fixture") is True
    if timed_session.get("state") != "COMPLETED" or not (eligible or fixture_allowed):
        errors.append("timed_review_session_not_completed_or_eligible")
    if timed_session.get("reviewer_id") != review.get("reviewer_id"):
        errors.append("timed_review_reviewer_mismatch")
    if timed_session.get("summary", {}).get("human_minutes") != review.get("human_minutes"):
        errors.append("timed_review_minutes_mismatch")
    subject_ids = {item.get("record_id") for item in timed_session.get("subjects", [])}
    if review.get("review_subject_id") not in subject_ids:
        errors.append("timed_review_subject_missing")
    decision = next(
        (
            item
            for item in timed_session.get("events", [])[-1].get("data", {}).get("decisions", [])
            if item.get("subject_record_id") == review.get("review_subject_id")
        ),
        None,
    )
    if decision is None or decision.get("accepted") is not (terminal["to_state"] == "ACCEPTED"):
        errors.append("timed_review_decision_mismatch")
    return sorted(set(errors))
