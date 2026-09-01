"""Validate full-denominator CH05 progress and synthetic retry/review/cost rollups."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from chapter_progress import ChapterProgressError, compile_progress
from comic_run_ledger import append_event
from compile_ch05_chapter_run_manifest import PLANS, ROOT, initial_ledger
from review_session import append_event as append_review_event
from review_session import session_digest, start_session


BASELINE = ROOT / "experiments/results/ch05-50-panel-run-manifest-r1.json"
COST_LEDGER = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r1.json"
REAL_OUT = ROOT / "experiments/results/ch05-progress-rollup-r1.json"
SYNTHETIC_OUT = ROOT / "experiments/results/ch05-progress-rollup-synthetic-validation-r1.json"
HASH = "0" * 64
SCOPE = {
    "external_provider": "synthetic-provider",
    "external_model_snapshot": "synthetic-model",
    "external_endpoint": "https://example.invalid/v1/edit",
}


def ref(record_id: str, digest: str = HASH) -> dict:
    return {"record_id": record_id, "path": f"test/{record_id}.json", "sha256": digest}


def initial_ledgers() -> list[dict]:
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    return [initial_ledger(item) for item in plans["plans"]]


def synthetic_session(*, session_id: str, render_id: str, assertion_id: str, accepted: bool, start_minute: int) -> dict:
    session = start_session(
        session_id=session_id,
        reviewer_id="synthetic-validator-not-human",
        subjects=[ref(render_id)],
        started_at=f"2026-09-01T17:{start_minute:02d}:00Z",
        validation_fixture=True,
    )
    return append_review_event(
        session,
        event_type="COMPLETE",
        occurred_at=f"2026-09-01T17:{start_minute + 5:02d}:00Z",
        data={"decisions": [{
            "subject_record_id": render_id,
            "accepted": accepted,
            "hard_assertions": [{"id": assertion_id, "passed": accepted}],
            "failure_tags": [] if accepted else ["SYNTHETIC_REJECT"],
        }]},
    )


def advance_attempt(
    ledger: dict,
    *,
    suffix: str,
    reservation_id: str,
    provider_request_id: str,
    render_id: str,
    assertion_id: str,
    actual_cost: str,
    session: dict,
    accepted: bool,
    minute: int,
) -> dict:
    states = [
        ("LOCAL_BASE_APPROVED", {"base_approval": ref(f"base-{suffix}")}),
        ("EXTERNAL_AUTHORITY_PENDING", {"proposed_scope": SCOPE}),
        ("BUDGET_RESERVED", {
            "authority_record": ref(f"authority-{suffix}"), "authorized_scope": SCOPE,
            "reservation": {
                "aggregate_ledger": ref("synthetic-production-ledger"),
                "reservation_id": reservation_id, "adapter_id": "synthetic-adapter", "reserved_usd": "0.500000",
            },
        }),
        ("SUBMITTED", {"request": {
            "reservation_id": reservation_id, "provider_request_id": provider_request_id,
            "request_sha256": HASH, "submitted_at": f"2026-09-01T16:{minute + 3:02d}:00Z",
        }}),
        ("COMPLETED", {
            "provider_request_id": provider_request_id, "render_record": ref(render_id),
            "output_sha256": [HASH], "timing_seconds": 1.0, "actual_cost_usd": actual_cost,
            "cost_reconciliation": ref(f"cost-{suffix}"),
        }),
        ("HUMAN_REVIEW_PENDING", {"review_subject": ref(render_id)}),
        ("ACCEPTED" if accepted else "REJECTED", {"review": {
            "review_subject_id": render_id, "human_review_status": "completed",
            "reviewer_id": "synthetic-validator-not-human", "human_minutes": 5.0,
            "accepted": accepted,
            "hard_assertions": [{"id": assertion_id, "passed": accepted}],
            "failure_tags": [] if accepted else ["SYNTHETIC_REJECT"],
            "timed_review_session": ref(session["record_id"], session_digest(session)),
        }}),
    ]
    current = ledger
    for index, (state, data) in enumerate(states, 2):
        current = append_event(
            current,
            event_id=f"synthetic-{suffix}-{index}-{state.lower()}",
            occurred_at=f"2026-09-01T16:{minute + index:02d}:00Z",
            to_state=state,
            data=data,
        )
    return current


def main() -> int:
    failures = []
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    cost = json.loads(COST_LEDGER.read_text(encoding="utf-8"))
    ledgers = initial_ledgers()
    real = compile_progress(
        baseline_manifest=baseline, ledgers=ledgers, timed_sessions=[], production_cost_ledger=cost
    )
    REAL_OUT.write_text(json.dumps(real, indent=2) + "\n", encoding="utf-8")
    if real["current_chapter_root_sha256"] != baseline["chapter_root_sha256"]:
        failures.append("zero-progress current root differs from baseline")
    if real["current_state_distribution"] != {"BASE_APPROVAL_PENDING": 50}:
        failures.append("zero-progress state distribution is incorrect")
    if real["rates"]["accepted_per_planned"] != 0 or real["rates"]["accepted_per_submitted_panel"] is not None:
        failures.append("zero-progress rates are incorrect")

    assertion_by_panel = {item["panel_id"]: item["applicable_hard_assertion_id"] for item in baseline["panels"]}
    session_a = synthetic_session(session_id="session-a", render_id="render-a", assertion_id=assertion_by_panel["ng-ch05-sc01-p001"], accepted=True, start_minute=0)
    session_b = synthetic_session(session_id="session-b", render_id="render-b", assertion_id=assertion_by_panel["ng-ch05-sc01-p002"], accepted=False, start_minute=10)
    session_c = synthetic_session(session_id="session-c", render_id="render-c", assertion_id=assertion_by_panel["ng-ch05-sc01-p002"], accepted=True, start_minute=20)
    attempts = copy.deepcopy(ledgers)
    attempts[0] = advance_attempt(
        attempts[0], suffix="a", reservation_id="reservation-a", provider_request_id="request-a",
        render_id="render-a", assertion_id=assertion_by_panel["ng-ch05-sc01-p001"], actual_cost="0.100000",
        session=session_a, accepted=True, minute=30,
    )
    attempts[1] = advance_attempt(
        attempts[1], suffix="b", reservation_id="reservation-b", provider_request_id="request-b",
        render_id="render-b", assertion_id=assertion_by_panel["ng-ch05-sc01-p002"], actual_cost="0.150000",
        session=session_b, accepted=False, minute=40,
    )
    retry = initial_ledger(json.loads(PLANS.read_text(encoding="utf-8"))["plans"][1])
    retry["ledger_id"] = "ng-ch05-sc01-p002-chapter-run-ledger-synthetic-retry-r2"
    retry = advance_attempt(
        retry, suffix="c", reservation_id="reservation-c", provider_request_id="request-c",
        render_id="render-c", assertion_id=assertion_by_panel["ng-ch05-sc01-p002"], actual_cost="0.200000",
        session=session_c, accepted=True, minute=50,
    )
    attempts.append(retry)
    synthetic_cost = {
        "record_type": "ProductionCostLedger", "record_id": "synthetic-production-ledger",
        "budget_domain": "NORTH_GARDEN_CH05_PRODUCTION", "held_reservations_usd": "0.000000",
        "entries": [
            {"reservation_id": "reservation-a", "adapter_id": "synthetic-adapter", "state": "committed", "reserved_usd": "0.500000", "actual_cost_usd": "0.100000", "provider_request_id": "request-a"},
            {"reservation_id": "reservation-b", "adapter_id": "synthetic-adapter", "state": "committed", "reserved_usd": "0.500000", "actual_cost_usd": "0.150000", "provider_request_id": "request-b"},
            {"reservation_id": "reservation-c", "adapter_id": "synthetic-adapter", "state": "committed", "reserved_usd": "0.500000", "actual_cost_usd": "0.200000", "provider_request_id": "request-c"},
        ],
    }
    synthetic = compile_progress(
        baseline_manifest=baseline, ledgers=attempts, timed_sessions=[session_a, session_b, session_c],
        production_cost_ledger=synthetic_cost, validation_fixture_mode=True,
    )
    SYNTHETIC_OUT.write_text(json.dumps(synthetic, indent=2) + "\n", encoding="utf-8")
    expected = {
        "planned_panels": 50, "submitted_panels": 2, "submitted_attempts": 3, "retry_attempts": 1,
        "completed_attempts": 3, "accepted_attempts": 2, "rejected_attempts": 1,
        "accepted_panels": 2, "rejected_panels": 0,
    }
    for field, value in expected.items():
        if synthetic["denominators"][field] != value:
            failures.append(f"synthetic denominator mismatch: {field}")
    if synthetic["rates"] != {"accepted_per_planned": 0.04, "accepted_per_submitted_panel": 1.0}:
        failures.append("full-denominator synthetic rates are incorrect")
    if synthetic["human_review"]["measured_human_minutes"] is not None or synthetic["human_review"]["synthetic_fixture_minutes"] != 15.0:
        failures.append("synthetic review minutes leaked into real evidence")
    if synthetic["production_cost"]["committed_actual_cost_usd"] != "0.450000":
        failures.append("synthetic reconciled cost rollup is incorrect")

    mutations = [
        ("missing panel", lambda l, c, s: l.pop()),
        ("cost mismatch", lambda l, c, s: c["entries"][0].update(actual_cost_usd="0.110000")),
        ("missing session", lambda l, c, s: s.pop()),
        ("plan mismatch", lambda l, c, s: l[0].update(plan_revision_id="wrong")),
    ]
    for label, mutate in mutations:
        changed_ledgers, changed_cost, changed_sessions = copy.deepcopy(attempts), copy.deepcopy(synthetic_cost), [copy.deepcopy(session_a), copy.deepcopy(session_b), copy.deepcopy(session_c)]
        mutate(changed_ledgers, changed_cost, changed_sessions)
        try:
            compile_progress(
                baseline_manifest=baseline, ledgers=changed_ledgers, timed_sessions=changed_sessions,
                production_cost_ledger=changed_cost, validation_fixture_mode=True,
            )
            failures.append(f"progress mutation passed: {label}")
        except ChapterProgressError:
            pass

    for failure in failures:
        print(f"failure: {failure}")
    if failures:
        return 1
    print("0 failures, 0 warnings (real 0/50; synthetic 2/50, 3 attempts/1 retry, 15 fixture minutes, $0.45 isolated; 4/4 mutations rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
