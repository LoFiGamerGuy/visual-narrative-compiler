"""Append-only, crash-safe journal for future provider submissions."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation


SHA256 = re.compile(r"^[0-9a-f]{64}$")
GENESIS = "GENESIS"
ALLOWED = {
    "PREPARED": {"RESERVED"},
    "RESERVED": {"SUBMISSION_STARTED", "ABORTED_UNSUBMITTED"},
    "SUBMISSION_STARTED": {"PROVIDER_ACKNOWLEDGED", "OUTCOME_UNKNOWN"},
    "OUTCOME_UNKNOWN": {"PROVIDER_ACKNOWLEDGED", "FAILED_RECONCILED"},
    "PROVIDER_ACKNOWLEDGED": {"RESPONSE_CAPTURED", "OUTCOME_UNKNOWN", "FAILED_RECONCILED"},
    "RESPONSE_CAPTURED": {"COST_RECONCILED"},
    "COST_RECONCILED": {"RENDER_RECORD_PERSISTED"},
    "RENDER_RECORD_PERSISTED": {"COMPLETED"},
    "ABORTED_UNSUBMITTED": set(),
    "FAILED_RECONCILED": set(),
    "COMPLETED": set(),
}


class SubmissionJournalError(ValueError):
    """Raised when submission intent, recovery, or reconciliation is unsafe."""


def canonical_sha256(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def make_idempotency_key(
    *, adapter_id: str, panel_id: str, plan_revision_id: str, panel_input_package_sha256: str, attempt_ordinal: int
) -> str:
    if not SHA256.fullmatch(panel_input_package_sha256) or not isinstance(attempt_ordinal, int) or attempt_ordinal <= 0:
        raise SubmissionJournalError("input package hash and positive attempt ordinal are required")
    return "ng-submit-" + canonical_sha256({
        "adapter_id": adapter_id,
        "panel_id": panel_id,
        "plan_revision_id": plan_revision_id,
        "panel_input_package_sha256": panel_input_package_sha256,
        "attempt_ordinal": attempt_ordinal,
    })


def sha_ref_errors(value: object, label: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{label}:missing"]
    errors = []
    if not value.get("record_id") or not value.get("path"):
        errors.append(f"{label}:identity_or_path_missing")
    if not SHA256.fullmatch(str(value.get("sha256", ""))):
        errors.append(f"{label}:sha256_missing_or_invalid")
    return errors


def event_data_errors(state: str, data: dict) -> list[str]:
    errors = []
    if state == "RESERVED":
        errors.extend(sha_ref_errors(data.get("aggregate_ledger"), "reservation:aggregate_ledger"))
        for field in ("reservation_id", "budget_domain", "adapter_id", "panel_input_package_sha256", "reserved_usd"):
            if not data.get(field):
                errors.append(f"reservation:{field}_missing")
    elif state == "SUBMISSION_STARTED":
        if not data.get("started_at") or not data.get("idempotency_key"):
            errors.append("submission_start_identity_missing")
    elif state == "PROVIDER_ACKNOWLEDGED":
        if not data.get("provider_request_id"):
            errors.append("provider_request_id_missing")
    elif state == "OUTCOME_UNKNOWN":
        errors.extend(sha_ref_errors(data.get("held_reservation"), "held_reservation"))
        if not data.get("reason"):
            errors.append("unknown_outcome_reason_missing")
    elif state == "RESPONSE_CAPTURED":
        if not data.get("provider_request_id"):
            errors.append("response_provider_request_id_missing")
        outputs = data.get("output_sha256")
        if not isinstance(outputs, list) or not outputs or any(not SHA256.fullmatch(str(item)) for item in outputs):
            errors.append("response_output_sha256_missing_or_invalid")
        if not isinstance(data.get("timing_seconds"), (int, float)) or data.get("timing_seconds", 0) <= 0:
            errors.append("response_timing_missing_or_invalid")
    elif state in {"COST_RECONCILED", "FAILED_RECONCILED"}:
        errors.extend(sha_ref_errors(data.get("cost_reconciliation"), "cost_reconciliation"))
        try:
            cost = Decimal(str(data.get("actual_cost_usd")))
            if not cost.is_finite() or cost < 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            errors.append("actual_cost_missing_or_invalid")
        if state == "FAILED_RECONCILED":
            errors.extend(sha_ref_errors(data.get("failure_record"), "failure_record"))
    elif state == "RENDER_RECORD_PERSISTED":
        errors.extend(sha_ref_errors(data.get("render_record"), "render_record"))
    elif state == "ABORTED_UNSUBMITTED":
        errors.extend(sha_ref_errors(data.get("released_reservation"), "released_reservation"))
        if not data.get("reason"):
            errors.append("abort_reason_missing")
    return sorted(set(errors))


def new_journal(
    *, journal_id: str, adapter_id: str, panel_id: str, plan_revision_id: str,
    panel_input_package_sha256: str, attempt_ordinal: int, supersedes_journal_id: str | None = None,
) -> dict:
    key = make_idempotency_key(
        adapter_id=adapter_id, panel_id=panel_id, plan_revision_id=plan_revision_id,
        panel_input_package_sha256=panel_input_package_sha256, attempt_ordinal=attempt_ordinal,
    )
    return {
        "record_type": "ProviderSubmissionJournal", "schema_version": "1.0",
        "journal_id": journal_id, "state": "PREPARED", "adapter_id": adapter_id,
        "panel_id": panel_id, "plan_revision_id": plan_revision_id,
        "panel_input_package_sha256": panel_input_package_sha256,
        "attempt_ordinal": attempt_ordinal, "supersedes_journal_id": supersedes_journal_id,
        "idempotency_key": key, "events": [],
    }


def append_event(journal: dict, *, to_state: str, occurred_at: str, data: dict) -> dict:
    errors = validate_journal(journal)
    if errors:
        raise SubmissionJournalError("invalid existing journal: " + "; ".join(errors))
    from_state = journal["state"]
    if to_state not in ALLOWED.get(from_state, set()):
        raise SubmissionJournalError(f"transition not allowed: {from_state}->{to_state}")
    data_errors = event_data_errors(to_state, data)
    if data_errors:
        raise SubmissionJournalError("invalid event data: " + "; ".join(data_errors))
    if to_state == "RESERVED":
        if data.get("adapter_id") != journal["adapter_id"] or data.get("panel_input_package_sha256") != journal["panel_input_package_sha256"]:
            raise SubmissionJournalError("reservation does not bind journal adapter/input package")
    if to_state == "SUBMISSION_STARTED" and data.get("idempotency_key") != journal["idempotency_key"]:
        raise SubmissionJournalError("submission idempotency key mismatch")
    event = {
        "sequence": len(journal["events"]) + 1, "occurred_at": occurred_at,
        "from_state": from_state, "to_state": to_state, "data": copy.deepcopy(data),
        "previous_event_sha256": journal["events"][-1]["event_sha256"] if journal["events"] else GENESIS,
    }
    event["event_sha256"] = canonical_sha256(event)
    updated = copy.deepcopy(journal)
    updated["events"].append(event)
    updated["state"] = to_state
    errors = validate_journal(updated)
    if errors:
        raise SubmissionJournalError("invalid resulting journal: " + "; ".join(errors))
    return updated


def validate_journal(journal: dict) -> list[str]:
    errors = []
    if journal.get("record_type") != "ProviderSubmissionJournal" or journal.get("schema_version") != "1.0":
        errors.append("journal schema invalid")
    try:
        expected_key = make_idempotency_key(
            adapter_id=journal.get("adapter_id"), panel_id=journal.get("panel_id"),
            plan_revision_id=journal.get("plan_revision_id"),
            panel_input_package_sha256=journal.get("panel_input_package_sha256"),
            attempt_ordinal=journal.get("attempt_ordinal"),
        )
        if journal.get("idempotency_key") != expected_key:
            errors.append("journal idempotency key invalid")
    except SubmissionJournalError:
        errors.append("journal identity invalid")
    state, previous = "PREPARED", GENESIS
    reservation_id = None
    provider_request_id = None
    reconciled = False
    render_record_id = None
    for index, event in enumerate(journal.get("events", []), 1):
        copied = copy.deepcopy(event)
        claimed = copied.pop("event_sha256", None)
        if event.get("sequence") != index or event.get("previous_event_sha256") != previous or claimed != canonical_sha256(copied):
            errors.append(f"event {index} chain invalid")
        if event.get("from_state") != state or event.get("to_state") not in ALLOWED.get(state, set()):
            errors.append(f"event {index} transition invalid")
        errors.extend(f"event {index}:{item}" for item in event_data_errors(event.get("to_state"), event.get("data", {})))
        data = event.get("data", {})
        if event.get("to_state") == "RESERVED":
            reservation_id = data.get("reservation_id")
            if data.get("adapter_id") != journal.get("adapter_id") or data.get("panel_input_package_sha256") != journal.get("panel_input_package_sha256"):
                errors.append(f"event {index} reservation binding mismatch")
        elif event.get("to_state") == "SUBMISSION_STARTED":
            if data.get("idempotency_key") != journal.get("idempotency_key"):
                errors.append(f"event {index} idempotency key mismatch")
        elif event.get("to_state") == "PROVIDER_ACKNOWLEDGED":
            if provider_request_id and provider_request_id != data.get("provider_request_id"):
                errors.append(f"event {index} provider request changed")
            provider_request_id = data.get("provider_request_id")
        elif event.get("to_state") == "RESPONSE_CAPTURED":
            if data.get("provider_request_id") != provider_request_id:
                errors.append(f"event {index} response request mismatch")
        elif event.get("to_state") in {"COST_RECONCILED", "FAILED_RECONCILED"}:
            reconciled = True
        elif event.get("to_state") == "RENDER_RECORD_PERSISTED":
            if not reconciled:
                errors.append(f"event {index} RenderRecord before reconciliation")
            render_record_id = data.get("render_record", {}).get("record_id")
        elif event.get("to_state") == "COMPLETED" and not render_record_id:
            errors.append(f"event {index} completed without RenderRecord")
        state, previous = event.get("to_state"), claimed
    if journal.get("state") != state:
        errors.append("journal state mismatch")
    return sorted(set(errors))


def validate_journal_set(journals: list[dict]) -> list[str]:
    errors = []
    ids, keys = set(), set()
    for journal in journals:
        errors.extend(f"{journal.get('journal_id')}:{item}" for item in validate_journal(journal))
        if journal.get("journal_id") in ids:
            errors.append("duplicate journal_id")
        if journal.get("idempotency_key") in keys:
            errors.append("duplicate idempotency_key")
        ids.add(journal.get("journal_id"))
        keys.add(journal.get("idempotency_key"))
    return sorted(set(errors))


def retry_errors(previous: dict, candidate: dict) -> list[str]:
    errors = []
    if previous.get("state") == "OUTCOME_UNKNOWN":
        errors.append("unknown provider outcome blocks retry")
    if previous.get("state") not in {"ABORTED_UNSUBMITTED", "FAILED_RECONCILED"}:
        errors.append("previous attempt is not a known retryable terminal state")
    if candidate.get("attempt_ordinal") != previous.get("attempt_ordinal", 0) + 1:
        errors.append("retry attempt ordinal is not consecutive")
    if candidate.get("supersedes_journal_id") != previous.get("journal_id"):
        errors.append("retry supersedes binding missing")
    for field in ("adapter_id", "panel_id", "plan_revision_id", "panel_input_package_sha256"):
        if candidate.get(field) != previous.get(field):
            errors.append(f"retry identity mismatch: {field}")
    return sorted(set(errors))


def validate_budget_binding(journal: dict, aggregate_ledger: dict) -> list[str]:
    """Bind journal crash/recovery states to the aggregate production ledger."""
    errors = validate_journal(journal)
    if errors:
        return errors
    reservation_event = next((item for item in journal["events"] if item["to_state"] == "RESERVED"), None)
    if reservation_event is None:
        return []
    declared = reservation_event["data"]
    if aggregate_ledger.get("record_type") != "ProductionCostLedger" or aggregate_ledger.get("budget_domain") != declared.get("budget_domain"):
        errors.append("aggregate production ledger schema/domain mismatch")
    if declared.get("aggregate_ledger", {}).get("record_id") != aggregate_ledger.get("record_id"):
        errors.append("aggregate production ledger record mismatch")
    entry = next((item for item in aggregate_ledger.get("entries", []) if item.get("reservation_id") == declared.get("reservation_id")), None)
    if entry is None:
        return sorted(set([*errors, "aggregate reservation missing"]))
    for field in ("adapter_id", "panel_input_package_sha256"):
        if entry.get(field) != declared.get(field):
            errors.append(f"aggregate reservation mismatch: {field}")
    try:
        if Decimal(str(entry.get("reserved_usd"))) != Decimal(str(declared.get("reserved_usd"))):
            errors.append("aggregate reservation amount mismatch")
    except (InvalidOperation, ValueError):
        errors.append("aggregate reservation amount invalid")
    journal_state = journal["state"]
    if journal_state == "ABORTED_UNSUBMITTED" and entry.get("state") != "released":
        errors.append("aborted-unsubmitted reservation not released")
    if journal_state in {"SUBMISSION_STARTED", "OUTCOME_UNKNOWN", "PROVIDER_ACKNOWLEDGED", "RESPONSE_CAPTURED"} and entry.get("state") not in {"awaiting_reconciliation", "committed"}:
        errors.append("submitted/unknown reservation is not held")
    if journal_state in {"COST_RECONCILED", "FAILED_RECONCILED", "RENDER_RECORD_PERSISTED", "COMPLETED"}:
        if entry.get("state") != "committed":
            errors.append("reconciled journal cost is not committed")
        cost_event = next((item for item in journal["events"] if item["to_state"] in {"COST_RECONCILED", "FAILED_RECONCILED"}), None)
        try:
            if Decimal(str(entry.get("actual_cost_usd"))) != Decimal(str(cost_event["data"]["actual_cost_usd"])):
                errors.append("aggregate actual cost mismatch")
        except (InvalidOperation, ValueError, TypeError):
            errors.append("aggregate actual cost invalid")
    acknowledged = next((item for item in journal["events"] if item["to_state"] == "PROVIDER_ACKNOWLEDGED"), None)
    if acknowledged is not None and entry.get("provider_request_id") != acknowledged["data"]["provider_request_id"]:
        errors.append("aggregate provider request ID mismatch")
    return sorted(set(errors))
