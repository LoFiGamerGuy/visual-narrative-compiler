"""Validate synthetic success/failure/unknown production evidence without provider calls."""
from __future__ import annotations

import copy
import hashlib

from PIL import Image

from render_record import ROOT, incident_errors, render_record_errors
from submission_journal import append_event, journal_digest, new_journal


BASE = ROOT / "experiments/outputs/ch05_p036_layout_control_r1/ch05-p036-layout-control-r1.png"
MASK = ROOT / "experiments/outputs/ch05_p036_layout_control_r1/ch05-p036-target-context-mask-r1.png"
HASH = "0" * 64


def sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_ref(path) -> dict:
    with Image.open(path) as image:
        width, height = image.size
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "width": width, "height": height}


def ref(record_id: str) -> dict:
    return {"record_id": record_id, "path": f"test/{record_id}.json", "sha256": HASH}


def begin(journal_id: str, package_hash: str, reservation_id: str) -> dict:
    journal = new_journal(
        journal_id=journal_id, adapter_id="openai_gpt_image_2", panel_id="ng-ch05-sc01-p036",
        plan_revision_id="ng-ch05-sc01-p036-plan-r1", panel_input_package_sha256=package_hash, attempt_ordinal=1,
    )
    journal = append_event(journal, to_state="RESERVED", occurred_at="2026-09-01T18:00:00Z", data={
        "aggregate_ledger": ref("synthetic-production-ledger"), "reservation_id": reservation_id,
        "budget_domain": "NORTH_GARDEN_CH05_PRODUCTION", "adapter_id": "openai_gpt_image_2",
        "panel_input_package_sha256": package_hash, "reserved_usd": "0.500000",
    })
    return append_event(journal, to_state="SUBMISSION_STARTED", occurred_at="2026-09-01T18:01:00Z", data={
        "started_at": "2026-09-01T18:01:00Z", "idempotency_key": journal["idempotency_key"],
    })


def success() -> tuple[dict, dict, dict]:
    output_hash = sha256(BASE)
    journal = begin("success-journal", "1" * 64, "reservation-success")
    journal = append_event(journal, to_state="PROVIDER_ACKNOWLEDGED", occurred_at="2026-09-01T18:02:00Z", data={"provider_request_id": "request-success"})
    journal = append_event(journal, to_state="RESPONSE_CAPTURED", occurred_at="2026-09-01T18:03:00Z", data={"provider_request_id": "request-success", "output_sha256": [output_hash], "timing_seconds": 12.5})
    journal = append_event(journal, to_state="COST_RECONCILED", occurred_at="2026-09-01T18:04:00Z", data={"cost_reconciliation": ref("cost-success"), "actual_cost_usd": "0.100000"})
    journal = append_event(journal, to_state="RENDER_RECORD_PERSISTED", occurred_at="2026-09-01T18:05:00Z", data={"render_record": ref("render-success")})
    journal = append_event(journal, to_state="COMPLETED", occurred_at="2026-09-01T18:06:00Z", data={})
    ledger = {
        "record_type": "ProductionCostLedger", "record_id": "synthetic-production-ledger", "budget_domain": "NORTH_GARDEN_CH05_PRODUCTION",
        "entries": [{
            "reservation_id": "reservation-success", "adapter_id": "openai_gpt_image_2",
            "panel_input_package_sha256": "1" * 64, "reserved_usd": "0.500000", "actual_cost_usd": "0.100000",
            "state": "committed", "provider_request_id": "request-success",
        }],
    }
    record = {
        "record_type": "RenderRecord", "schema_version": "2.0", "render_profile": "comic_targeted_repair_v1",
        "record_id": "render-success", "state": "SYNTHETIC_COMPLETED_PENDING_HUMAN_REVIEW",
        "synthetic_validation_fixture": True, "medium": "comic", "animation_shot_plan": None,
        "comic_panel_plan": {"panel_id": "ng-ch05-sc01-p036", "plan_revision_id": "ng-ch05-sc01-p036-plan-r1"},
        "submission_journal": {
            "record_id": journal["journal_id"], "path": "test/success-journal.json", "sha256": journal_digest(journal),
            "chain_head_sha256": journal["events"][-1]["event_sha256"], "idempotency_key": journal["idempotency_key"],
        },
        "provider": {
            "adapter_id": "openai_gpt_image_2", "provider": "OpenAI API", "model_snapshot": "gpt-image-2-2026-04-21",
            "endpoint": "https://api.openai.com/v1/images/edits", "provider_request_id": "request-success",
        },
        "request": {
            "panel_input_package_sha256": "1" * 64, "request_metadata_sha256": "2" * 64,
            "submitted_at": "2026-09-01T18:01:00Z", "completed_at": "2026-09-01T18:03:00Z",
        },
        "inputs": {"base_raster": image_ref(BASE), "repair_mask": image_ref(MASK)},
        "outputs": {"candidates": [image_ref(BASE)], "candidate_count": 1},
        "timing": {"provider_seconds": 12.5, "end_to_end_seconds": 13.0},
        "provider_usage": {"synthetic_image_count": 1}, "provider_usage_unavailable_reason": None,
        "cost": {
            "reservation_id": "reservation-success", "actual_cost_usd": "0.100000",
            "reconciliation_method": "synthetic_exact_fixture", "cost_reconciliation": ref("cost-success"),
        },
        "failure": None,
        "review": {"human_review_status": "not_yet_performed", "human_minutes": None, "accepted": False},
        "acceptance": {"decision": "PENDING_HUMAN_REVIEW", "accepted": False},
    }
    return record, journal, ledger


def failure() -> tuple[dict, dict, dict]:
    journal = begin("failure-journal", "3" * 64, "reservation-failure")
    journal = append_event(journal, to_state="PROVIDER_ACKNOWLEDGED", occurred_at="2026-09-01T18:02:00Z", data={"provider_request_id": "request-failure"})
    journal = append_event(journal, to_state="FAILED_RECONCILED", occurred_at="2026-09-01T18:03:00Z", data={
        "failure_record": ref("failure-explicit"), "cost_reconciliation": ref("cost-failure"), "actual_cost_usd": "0.020000",
    })
    ledger = {
        "record_type": "ProductionCostLedger", "record_id": "synthetic-production-ledger", "budget_domain": "NORTH_GARDEN_CH05_PRODUCTION",
        "entries": [{
            "reservation_id": "reservation-failure", "adapter_id": "openai_gpt_image_2",
            "panel_input_package_sha256": "3" * 64, "reserved_usd": "0.500000", "actual_cost_usd": "0.020000",
            "state": "committed", "provider_request_id": "request-failure",
        }],
    }
    record, _, _ = success()
    record.update({"record_id": "render-failure", "state": "SYNTHETIC_FAILED_COST_RECONCILED"})
    record["submission_journal"] = {
        "record_id": journal["journal_id"], "path": "test/failure-journal.json", "sha256": journal_digest(journal),
        "chain_head_sha256": journal["events"][-1]["event_sha256"], "idempotency_key": journal["idempotency_key"],
    }
    record["provider"]["provider_request_id"] = "request-failure"
    record["request"].update(panel_input_package_sha256="3" * 64, completed_at="2026-09-01T18:03:00Z")
    record["outputs"] = {"candidates": [], "candidate_count": 0}
    record["provider_usage"] = None
    record["provider_usage_unavailable_reason"] = "Synthetic explicit provider failure returned no usage detail."
    record["cost"] = {
        "reservation_id": "reservation-failure", "actual_cost_usd": "0.020000",
        "reconciliation_method": "synthetic_exact_fixture", "cost_reconciliation": ref("cost-failure"),
    }
    record["failure"] = ref("failure-explicit")
    return record, journal, ledger


def unknown() -> tuple[dict, dict, dict]:
    journal = begin("unknown-journal", "4" * 64, "reservation-unknown")
    journal = append_event(journal, to_state="OUTCOME_UNKNOWN", occurred_at="2026-09-01T18:02:00Z", data={
        "held_reservation": ref("held-unknown"), "reason": "synthetic crash after submission boundary",
    })
    ledger = {
        "record_type": "ProductionCostLedger", "record_id": "synthetic-production-ledger", "budget_domain": "NORTH_GARDEN_CH05_PRODUCTION",
        "entries": [{
            "reservation_id": "reservation-unknown", "adapter_id": "openai_gpt_image_2",
            "panel_input_package_sha256": "4" * 64, "reserved_usd": "0.500000", "actual_cost_usd": None,
            "state": "awaiting_reconciliation", "provider_request_id": None,
        }],
    }
    incident = {
        "record_type": "ProviderSubmissionIncident", "schema_version": "1.0", "record_id": "incident-unknown",
        "state": "OUTCOME_UNKNOWN_RESERVATION_HELD", "medium": "comic", "animation_shot_plan": None,
        "comic_panel_plan": {"panel_id": "ng-ch05-sc01-p036", "plan_revision_id": "ng-ch05-sc01-p036-plan-r1"},
        "submission_journal": {
            "record_id": journal["journal_id"], "path": "test/unknown-journal.json", "sha256": journal_digest(journal),
            "chain_head_sha256": journal["events"][-1]["event_sha256"], "idempotency_key": journal["idempotency_key"],
        },
        "provider": {"adapter_id": "openai_gpt_image_2", "provider_request_id": None},
        "panel_input_package_sha256": "4" * 64,
        "held_reservation": {
            "reservation_id": "reservation-unknown", "aggregate_ledger_id": "synthetic-production-ledger",
            "reserved_usd": "0.500000", "state": "awaiting_reconciliation",
        },
        "detected_at": "2026-09-01T18:02:00Z", "reason": "Synthetic crash after submission boundary.",
        "recovery_actions": ["Query provider by idempotency key before any retry.", "Keep reservation held."],
        "render_record": None, "candidate_files": [],
        "cost_state": "AWAITING_RECONCILIATION_DO_NOT_RELEASE_OR_RETRY",
    }
    return incident, journal, ledger


def main() -> int:
    failures = []
    success_record, success_journal, success_ledger = success()
    failure_record, failure_journal, failure_ledger = failure()
    incident, unknown_journal, unknown_ledger = unknown()
    if render_record_errors(success_record, success_journal, success_ledger):
        failures.append("synthetic success RenderRecord did not validate")
    if render_record_errors(failure_record, failure_journal, failure_ledger):
        failures.append("synthetic failure RenderRecord did not validate")
    if incident_errors(incident, unknown_journal, unknown_ledger):
        failures.append("synthetic unknown incident did not validate")

    mutations = [
        ("success candidate hash", success_record, success_journal, success_ledger, lambda x: x["outputs"]["candidates"][0].update(sha256=HASH), render_record_errors),
        ("success candidate count", success_record, success_journal, success_ledger, lambda x: x["outputs"].update(candidate_count=2), render_record_errors),
        ("success request id", success_record, success_journal, success_ledger, lambda x: x["provider"].update(provider_request_id="wrong"), render_record_errors),
        ("success journal hash", success_record, success_journal, success_ledger, lambda x: x["submission_journal"].update(sha256=HASH), render_record_errors),
        ("success cost", success_record, success_journal, success_ledger, lambda x: x["cost"].update(actual_cost_usd="0.2"), render_record_errors),
        ("success timing", success_record, success_journal, success_ledger, lambda x: x["timing"].update(provider_seconds=0), render_record_errors),
        ("success review promotion", success_record, success_journal, success_ledger, lambda x: x["review"].update(human_minutes=1), render_record_errors),
        ("success usage missing", success_record, success_journal, success_ledger, lambda x: (x.update(provider_usage=None), x.update(provider_usage_unavailable_reason=None)), render_record_errors),
        ("failure fabricated candidate", failure_record, failure_journal, failure_ledger, lambda x: x["outputs"].update(candidates=[image_ref(BASE)], candidate_count=1), render_record_errors),
        ("failure missing failure", failure_record, failure_journal, failure_ledger, lambda x: x.update(failure=None), render_record_errors),
        ("incident fabricated render", incident, unknown_journal, unknown_ledger, lambda x: x.update(render_record=ref("fake")), incident_errors),
        ("incident released cost", incident, unknown_journal, unknown_ledger, lambda x: x.update(cost_state="RELEASED"), incident_errors),
    ]
    for label, source, journal, ledger, mutate, validator in mutations:
        changed = copy.deepcopy(source)
        mutate(changed)
        if not validator(changed, journal, ledger):
            failures.append(f"production evidence mutation passed: {label}")

    for failure_message in failures:
        print(f"failure: {failure_message}")
    if failures:
        return 1
    print("0 failures, 0 warnings (success/failure/unknown fixtures complete; unknown has no RenderRecord/candidates; 12/12 mutations rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
