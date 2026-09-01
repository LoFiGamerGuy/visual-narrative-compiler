"""Simulate selected-route crash/recovery without a provider executor."""
from __future__ import annotations

import copy

from submission_journal import (
    SubmissionJournalError,
    append_event,
    new_journal,
    retry_errors,
    validate_budget_binding,
    validate_journal,
    validate_journal_set,
)


HASH = "0" * 64


def ref(record_id: str) -> dict:
    return {"record_id": record_id, "path": f"test/{record_id}.json", "sha256": HASH}


def base(journal_id: str = "journal-1", ordinal: int = 1, supersedes: str | None = None) -> dict:
    return new_journal(
        journal_id=journal_id, adapter_id="openai_gpt_image_2", panel_id="ng-ch05-sc01-p036",
        plan_revision_id="ng-ch05-sc01-p036-plan-r1", panel_input_package_sha256=HASH,
        attempt_ordinal=ordinal, supersedes_journal_id=supersedes,
    )


def reserve(journal: dict, reservation_id: str = "reservation-1") -> dict:
    return append_event(journal, to_state="RESERVED", occurred_at="2026-09-01T17:00:00Z", data={
        "reservation_id": reservation_id, "budget_domain": "NORTH_GARDEN_CH05_PRODUCTION",
        "aggregate_ledger": ref("production-ledger"),
        "adapter_id": journal["adapter_id"], "panel_input_package_sha256": journal["panel_input_package_sha256"],
        "reserved_usd": "0.500000",
    })


def must_fail(label: str, action, failures: list[str]) -> None:
    try:
        action()
    except SubmissionJournalError:
        return
    failures.append(f"journal transition passed: {label}")


def main() -> int:
    failures = []
    # Proven pre-submit abort may release its reservation and become retryable.
    aborted = append_event(
        reserve(base("aborted"), "reservation-abort"), to_state="ABORTED_UNSUBMITTED",
        occurred_at="2026-09-01T17:01:00Z",
        data={"released_reservation": ref("release-abort"), "reason": "synthetic local failure before submission"},
    )
    retry = base("retry-after-abort", 2, "aborted")
    if retry_errors(aborted, retry):
        failures.append("known unsubmitted abort did not permit a bound retry")
    aborted_cost = {
        "record_type": "ProductionCostLedger", "record_id": "production-ledger", "budget_domain": "NORTH_GARDEN_CH05_PRODUCTION",
        "entries": [{
            "reservation_id": "reservation-abort", "adapter_id": "openai_gpt_image_2",
            "panel_input_package_sha256": HASH, "reserved_usd": "0.500000", "state": "released",
        }],
    }
    if validate_budget_binding(aborted, aborted_cost):
        failures.append("aborted reservation did not bind to released aggregate entry")

    # After submission starts, a crash enters OUTCOME_UNKNOWN and cannot retry.
    unknown = reserve(base("unknown"), "reservation-unknown")
    unknown = append_event(unknown, to_state="SUBMISSION_STARTED", occurred_at="2026-09-01T17:01:00Z", data={
        "started_at": "2026-09-01T17:01:00Z", "idempotency_key": unknown["idempotency_key"],
    })
    unknown = append_event(unknown, to_state="OUTCOME_UNKNOWN", occurred_at="2026-09-01T17:02:00Z", data={
        "held_reservation": ref("held-unknown"), "reason": "synthetic crash after submission boundary",
    })
    prohibited_retry = base("retry-while-unknown", 2, "unknown")
    if "unknown provider outcome blocks retry" not in retry_errors(unknown, prohibited_retry):
        failures.append("unknown outcome did not block retry")
    unknown_cost = {
        "record_type": "ProductionCostLedger", "record_id": "production-ledger", "budget_domain": "NORTH_GARDEN_CH05_PRODUCTION",
        "entries": [{
            "reservation_id": "reservation-unknown", "adapter_id": "openai_gpt_image_2",
            "panel_input_package_sha256": HASH, "reserved_usd": "0.500000", "state": "awaiting_reconciliation",
            "provider_request_id": None,
        }],
    }
    if validate_budget_binding(unknown, unknown_cost):
        failures.append("unknown outcome did not retain aggregate hold")
    must_fail("repeat submission while unknown", lambda: append_event(
        unknown, to_state="SUBMISSION_STARTED", occurred_at="2026-09-01T17:03:00Z",
        data={"started_at": "2026-09-01T17:03:00Z", "idempotency_key": unknown["idempotency_key"]},
    ), failures)

    # Recovery binds the original provider ID, output, cost, and RenderRecord.
    recovered = append_event(unknown, to_state="PROVIDER_ACKNOWLEDGED", occurred_at="2026-09-01T17:03:00Z", data={"provider_request_id": "request-1"})
    recovered = append_event(recovered, to_state="RESPONSE_CAPTURED", occurred_at="2026-09-01T17:04:00Z", data={
        "provider_request_id": "request-1", "output_sha256": [HASH], "timing_seconds": 12.5,
    })
    recovered = append_event(recovered, to_state="COST_RECONCILED", occurred_at="2026-09-01T17:05:00Z", data={
        "cost_reconciliation": ref("cost-1"), "actual_cost_usd": "0.100000",
    })
    recovered = append_event(recovered, to_state="RENDER_RECORD_PERSISTED", occurred_at="2026-09-01T17:06:00Z", data={"render_record": ref("render-1")})
    recovered = append_event(recovered, to_state="COMPLETED", occurred_at="2026-09-01T17:07:00Z", data={})
    if validate_journal(recovered):
        failures.append("recovered journal did not validate")
    recovered_cost = copy.deepcopy(unknown_cost)
    recovered_cost["entries"][0].update(
        state="committed", provider_request_id="request-1", actual_cost_usd="0.100000"
    )
    if validate_budget_binding(recovered, recovered_cost):
        failures.append("recovered completion did not bind to committed aggregate cost")
    must_fail("terminal replay", lambda: append_event(recovered, to_state="SUBMISSION_STARTED", occurred_at="2026-09-01T17:08:00Z", data={}), failures)

    duplicate = copy.deepcopy(recovered)
    duplicate["journal_id"] = "duplicate-key"
    if "duplicate idempotency_key" not in validate_journal_set([recovered, duplicate]):
        failures.append("duplicate idempotency key was not detected")

    mutations = [
        ("chain data", lambda x: x["events"][0]["data"].update(reserved_usd="9")),
        ("journal package", lambda x: x.update(panel_input_package_sha256="1" * 64)),
        ("response request", lambda x: x["events"][4]["data"].update(provider_request_id="wrong")),
        ("state", lambda x: x.update(state="OUTCOME_UNKNOWN")),
    ]
    for label, mutate in mutations:
        changed = copy.deepcopy(recovered)
        mutate(changed)
        if not validate_journal(changed):
            failures.append(f"journal mutation passed: {label}")

    for label, mutate in [
        ("aggregate held released", lambda x: x["entries"][0].update(state="released")),
        ("aggregate request", lambda x: x["entries"][0].update(provider_request_id="wrong")),
        ("aggregate cost", lambda x: x["entries"][0].update(actual_cost_usd="0.200000")),
    ]:
        changed = copy.deepcopy(recovered_cost)
        mutate(changed)
        if not validate_budget_binding(recovered, changed):
            failures.append(f"journal budget mutation passed: {label}")

    must_fail("wrong reservation package", lambda: append_event(base("bad-reserve"), to_state="RESERVED", occurred_at="2026-09-01T17:00:00Z", data={
        "reservation_id": "r", "budget_domain": "NORTH_GARDEN_CH05_PRODUCTION", "adapter_id": "openai_gpt_image_2",
        "aggregate_ledger": ref("production-ledger"),
        "panel_input_package_sha256": "1" * 64, "reserved_usd": "0.5",
    }), failures)
    must_fail("wrong start key", lambda: append_event(reserve(base("bad-key")), to_state="SUBMISSION_STARTED", occurred_at="2026-09-01T17:01:00Z", data={
        "started_at": "2026-09-01T17:01:00Z", "idempotency_key": "wrong",
    }), failures)

    for failure in failures:
        print(f"failure: {failure}")
    if failures:
        return 1
    print("0 failures, 0 warnings (abort retryable; unknown held/non-retryable; recovered completion/cost; duplicate key + 11/11 transitions/tampers/budget mutations blocked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
