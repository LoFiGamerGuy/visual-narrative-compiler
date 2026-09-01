"""Full-denominator progress rollup for append-only comic panel run ledgers."""
from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal

from comic_run_ledger import (
    canonical_sha256,
    validate_ledger,
    validate_reservation_bindings,
    validate_review_binding,
)


class ChapterProgressError(ValueError):
    """Raised when chapter progress inputs are incomplete or inconsistent."""


def has_state(ledger: dict, state: str) -> bool:
    return any(event.get("to_state") == state for event in ledger.get("events", []))


def compile_progress(
    *,
    baseline_manifest: dict,
    ledgers: list[dict],
    timed_sessions: list[dict],
    production_cost_ledger: dict,
    validation_fixture_mode: bool = False,
) -> dict:
    planned_rows = baseline_manifest["panels"]
    planned = {item["panel_id"]: item for item in planned_rows}
    if len(planned) != 50:
        raise ChapterProgressError("baseline must contain the full 50-panel denominator")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for ledger in ledgers:
        errors = validate_ledger(ledger)
        if errors:
            raise ChapterProgressError(f"invalid ledger {ledger.get('ledger_id')}: {errors}")
        panel_id = ledger["panel_id"]
        if panel_id not in planned or ledger["plan_revision_id"] != planned[panel_id]["plan_revision_id"]:
            raise ChapterProgressError(f"ledger plan binding mismatch: {panel_id}")
        grouped[panel_id].append(ledger)
    if set(grouped) != set(planned):
        raise ChapterProgressError("every planned panel needs at least one current run ledger")

    sessions = {item.get("record_id"): item for item in timed_sessions}
    cost_entries = {item.get("reservation_id"): item for item in production_cost_ledger.get("entries", [])}
    current = {}
    for panel_id, attempts in grouped.items():
        current[panel_id] = max(
            attempts,
            key=lambda item: (
                item["events"][-1]["occurred_at"] if item["events"] else "",
                len(item["events"]),
                item["ledger_id"],
            ),
        )
        for ledger in attempts:
            if has_state(ledger, "BUDGET_RESERVED"):
                errors = validate_reservation_bindings(ledger, production_cost_ledger)
                if errors:
                    raise ChapterProgressError(f"budget binding invalid {ledger['ledger_id']}: {errors}")
            if ledger["current_state"] in {"ACCEPTED", "REJECTED"}:
                review = ledger["events"][-1]["data"]["review"]
                session = sessions.get(review["timed_review_session"]["record_id"])
                if session is None:
                    raise ChapterProgressError(f"timed review session missing: {ledger['ledger_id']}")
                errors = validate_review_binding(ledger, session, validation_mode=validation_fixture_mode)
                if errors:
                    raise ChapterProgressError(f"review binding invalid {ledger['ledger_id']}: {errors}")

    state_counts = Counter(item["current_state"] for item in current.values())
    submitted_attempts = [item for item in ledgers if has_state(item, "SUBMITTED")]
    submitted_panels = {item["panel_id"] for item in submitted_attempts}
    completed_attempts = [item for item in ledgers if has_state(item, "COMPLETED")]
    failed_attempts = [item for item in ledgers if has_state(item, "FAILED")]
    accepted_attempts = [item for item in ledgers if item["current_state"] == "ACCEPTED"]
    rejected_attempts = [item for item in ledgers if item["current_state"] == "REJECTED"]
    accepted_panels = {panel_id for panel_id, item in current.items() if item["current_state"] == "ACCEPTED"}
    rejected_panels = {panel_id for panel_id, item in current.items() if item["current_state"] == "REJECTED"}
    real_minutes = Decimal("0")
    fixture_minutes = Decimal("0")
    for session in timed_sessions:
        minutes = session.get("summary", {}).get("human_minutes")
        if minutes is None:
            continue
        if session.get("summary", {}).get("review_evidence_eligible") is True:
            real_minutes += Decimal(str(minutes))
        elif validation_fixture_mode and session.get("validation_fixture") is True:
            fixture_minutes += Decimal(str(minutes))

    completion_cost = sum(
        (
            Decimal(str(event["data"]["actual_cost_usd"]))
            for ledger in completed_attempts
            for event in ledger["events"]
            if event["to_state"] == "COMPLETED"
        ),
        Decimal("0"),
    )
    committed_cost = sum(
        (Decimal(str(item["actual_cost_usd"])) for item in cost_entries.values() if item.get("state") == "committed"),
        Decimal("0"),
    )
    if completion_cost != committed_cost:
        raise ChapterProgressError("completed RenderRecord costs do not equal committed production ledger cost")

    root_material = [
        {
            "panel_id": panel_id,
            "plan_revision_id": planned[panel_id]["plan_revision_id"],
            "applicable_hard_assertion_sha256": planned[panel_id]["applicable_hard_assertion_sha256"],
            "chain_head_sha256": current[panel_id]["events"][-1]["event_sha256"],
        }
        for panel_id in sorted(planned, key=lambda value: planned[value]["display_order"])
    ]
    panel_count = len(planned)
    accepted_count = len(accepted_panels)
    return {
        "record_type": "ComicChapterProgressRollup",
        "schema_version": "1.0",
        "record_id": "ng-ch05-progress-rollup-r1" if not validation_fixture_mode else "ng-ch05-progress-rollup-synthetic-validation-r1",
        "state": "REAL_EVIDENCE" if not validation_fixture_mode else "SYNTHETIC_VALIDATION_ONLY",
        "medium": "comic",
        "animation_shot_plan": None,
        "baseline_chapter_root_sha256": baseline_manifest["chapter_root_sha256"],
        "current_chapter_root_sha256": canonical_sha256({"panels": root_material}),
        "denominators": {
            "planned_panels": panel_count,
            "panels_with_run_ledgers": len(grouped),
            "submitted_panels": len(submitted_panels),
            "submitted_attempts": len(submitted_attempts),
            "retry_attempts": max(0, len(submitted_attempts) - len(submitted_panels)),
            "completed_attempts": len(completed_attempts),
            "failed_attempts": len(failed_attempts),
            "accepted_attempts": len(accepted_attempts),
            "rejected_attempts": len(rejected_attempts),
            "accepted_panels": accepted_count,
            "rejected_panels": len(rejected_panels),
        },
        "current_state_distribution": dict(sorted(state_counts.items())),
        "rates": {
            "accepted_per_planned": round(accepted_count / panel_count, 6),
            "accepted_per_submitted_panel": round(accepted_count / len(submitted_panels), 6) if submitted_panels else None,
        },
        "human_review": {
            "eligible_session_count": sum(item.get("summary", {}).get("review_evidence_eligible") is True for item in timed_sessions),
            "measured_human_minutes": float(real_minutes) if real_minutes else None,
            "synthetic_fixture_minutes": float(fixture_minutes) if fixture_minutes else None,
        },
        "production_cost": {
            "committed_actual_cost_usd": f"{committed_cost:.6f}",
            "held_reservations_usd": production_cost_ledger.get("held_reservations_usd", "0.000000"),
        },
        "boundary": "All rates retain the 50-panel denominator. Synthetic fixture metrics are isolated from real human/cost evidence.",
    }
