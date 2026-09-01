"""Completeness validators for comic repair RenderRecords and unknown incidents."""
from __future__ import annotations

import hashlib
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from submission_journal import journal_digest, validate_budget_binding, validate_journal


ROOT = Path(__file__).resolve().parents[2]
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def sha_ref_errors(value: object, label: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{label}:missing"]
    errors = []
    if not value.get("record_id") or not value.get("path"):
        errors.append(f"{label}:identity_or_path_missing")
    if not SHA256.fullmatch(str(value.get("sha256", ""))):
        errors.append(f"{label}:sha256_missing_or_invalid")
    return errors


def file_errors(value: object, label: str) -> list[str]:
    if not isinstance(value, dict) or not value.get("path") or not SHA256.fullmatch(str(value.get("sha256", ""))):
        return [f"{label}:path_or_sha256_missing"]
    path = (ROOT / value["path"]).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        return [f"{label}:file_missing_or_outside_root"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != value["sha256"]:
        return [f"{label}:sha256_mismatch"]
    if not isinstance(value.get("width"), int) or not isinstance(value.get("height"), int):
        return [f"{label}:dimensions_missing"]
    try:
        with Image.open(path) as image:
            if image.size != (value["width"], value["height"]):
                return [f"{label}:dimensions_mismatch"]
            image.verify()
    except (OSError, UnidentifiedImageError):
        return [f"{label}:invalid_image_payload"]
    return []


def money_equal(left: object, right: object) -> bool:
    try:
        return Decimal(str(left)) == Decimal(str(right))
    except (InvalidOperation, ValueError):
        return False


def render_record_errors(record: dict, journal: dict, cost_ledger: dict) -> list[str]:
    errors = []
    errors.extend(f"journal:{item}" for item in validate_journal(journal))
    errors.extend(f"budget:{item}" for item in validate_budget_binding(journal, cost_ledger))
    if record.get("record_type") != "RenderRecord" or record.get("schema_version") != "2.0" or record.get("render_profile") != "comic_targeted_repair_v1":
        errors.append("render_record_schema_invalid")
    if record.get("medium") != "comic" or record.get("animation_shot_plan") is not None:
        errors.append("medium_or_animation_boundary")
    if record.get("comic_panel_plan") != {"panel_id": journal.get("panel_id"), "plan_revision_id": journal.get("plan_revision_id")}:
        errors.append("comic_panel_plan_mismatch")
    journal_ref = record.get("submission_journal", {})
    if journal_ref.get("record_id") != journal.get("journal_id") or journal_ref.get("sha256") != journal_digest(journal):
        errors.append("submission_journal_reference_mismatch")
    if journal_ref.get("chain_head_sha256") != journal.get("events", [{}])[-1].get("event_sha256") or journal_ref.get("idempotency_key") != journal.get("idempotency_key"):
        errors.append("submission_journal_head_or_key_mismatch")
    provider = record.get("provider", {})
    if provider.get("adapter_id") != journal.get("adapter_id") or not provider.get("provider") or not provider.get("model_snapshot") or not provider.get("endpoint"):
        errors.append("provider_identity_incomplete")
    acknowledged = next((item for item in journal.get("events", []) if item.get("to_state") == "PROVIDER_ACKNOWLEDGED"), None)
    provider_request_id = acknowledged.get("data", {}).get("provider_request_id") if acknowledged else None
    if provider.get("provider_request_id") != provider_request_id:
        errors.append("provider_request_id_mismatch")
    request = record.get("request", {})
    if request.get("panel_input_package_sha256") != journal.get("panel_input_package_sha256") or not SHA256.fullmatch(str(request.get("request_metadata_sha256", ""))):
        errors.append("request_hashes_incomplete_or_mismatch")
    if not request.get("submitted_at") or not request.get("completed_at"):
        errors.append("request_timestamps_missing")
    inputs = record.get("inputs", {})
    if set(inputs) != {"base_raster", "repair_mask"}:
        errors.append("required_inputs_missing_or_extra")
    for label, value in inputs.items():
        errors.extend(file_errors(value, f"input:{label}"))
    timing = record.get("timing", {})
    if any(not isinstance(timing.get(field), (int, float)) or timing.get(field, 0) <= 0 for field in ("provider_seconds", "end_to_end_seconds")):
        errors.append("timing_missing_or_invalid")
    if record.get("provider_usage") is None and not record.get("provider_usage_unavailable_reason"):
        errors.append("provider_usage_or_unavailable_reason_missing")
    cost = record.get("cost", {})
    reconciliation = next((item for item in journal.get("events", []) if item.get("to_state") in {"COST_RECONCILED", "FAILED_RECONCILED"}), None)
    if reconciliation is None or not money_equal(cost.get("actual_cost_usd"), reconciliation["data"].get("actual_cost_usd")):
        errors.append("actual_cost_mismatch")
    errors.extend(sha_ref_errors(cost.get("cost_reconciliation"), "cost_reconciliation"))
    if reconciliation and cost.get("cost_reconciliation") != reconciliation["data"].get("cost_reconciliation"):
        errors.append("cost_reconciliation_reference_mismatch")
    reservation_event = next((item for item in journal.get("events", []) if item.get("to_state") == "RESERVED"), None)
    if not reservation_event or cost.get("reservation_id") != reservation_event["data"].get("reservation_id"):
        errors.append("cost_reservation_id_mismatch")
    if not cost.get("reservation_id") or not cost.get("reconciliation_method"):
        errors.append("cost_provenance_incomplete")

    state = record.get("state")
    candidates = record.get("outputs", {}).get("candidates", [])
    if journal.get("state") == "COMPLETED":
        if state not in {"COMPLETED_PENDING_HUMAN_REVIEW", "SYNTHETIC_COMPLETED_PENDING_HUMAN_REVIEW"}:
            errors.append("completed_render_state_invalid")
        if not candidates or record.get("outputs", {}).get("candidate_count") != len(candidates):
            errors.append("completed_candidates_missing_or_count_mismatch")
        for index, candidate in enumerate(candidates):
            errors.extend(file_errors(candidate, f"candidate:{index}"))
        response = next((item for item in journal.get("events", []) if item.get("to_state") == "RESPONSE_CAPTURED"), None)
        if response is None or [item.get("sha256") for item in candidates] != response["data"].get("output_sha256"):
            errors.append("candidate_hashes_do_not_match_journal_response")
        if record.get("failure") is not None:
            errors.append("completed_render_has_failure")
    elif journal.get("state") == "FAILED_RECONCILED":
        if state not in {"FAILED_COST_RECONCILED", "SYNTHETIC_FAILED_COST_RECONCILED"}:
            errors.append("failed_render_state_invalid")
        if candidates or record.get("outputs", {}).get("candidate_count") != 0:
            errors.append("failed_render_fabricated_candidates")
        errors.extend(sha_ref_errors(record.get("failure"), "failure"))
        if reconciliation and record.get("failure") != reconciliation["data"].get("failure_record"):
            errors.append("failure_reference_mismatch")
    else:
        errors.append("journal_state_cannot_emit_render_record")
    review = record.get("review", {})
    acceptance = record.get("acceptance", {})
    if review.get("human_review_status") != "not_yet_performed" or review.get("human_minutes") is not None or review.get("accepted") is not False:
        errors.append("new_render_record_review_state_invalid")
    if acceptance.get("decision") != "PENDING_HUMAN_REVIEW" or acceptance.get("accepted") is not False:
        errors.append("new_render_record_acceptance_invalid")
    if record.get("synthetic_validation_fixture") is True and not str(state).startswith("SYNTHETIC_"):
        errors.append("synthetic_fixture_state_not_marked")
    return sorted(set(errors))


def incident_errors(record: dict, journal: dict, cost_ledger: dict) -> list[str]:
    errors = []
    errors.extend(f"journal:{item}" for item in validate_journal(journal))
    errors.extend(f"budget:{item}" for item in validate_budget_binding(journal, cost_ledger))
    if record.get("record_type") != "ProviderSubmissionIncident" or record.get("schema_version") != "1.0" or record.get("state") != "OUTCOME_UNKNOWN_RESERVATION_HELD":
        errors.append("incident_schema_or_state_invalid")
    if journal.get("state") != "OUTCOME_UNKNOWN":
        errors.append("incident_journal_not_unknown")
    if record.get("medium") != "comic" or record.get("animation_shot_plan") is not None:
        errors.append("medium_or_animation_boundary")
    if record.get("comic_panel_plan") != {"panel_id": journal.get("panel_id"), "plan_revision_id": journal.get("plan_revision_id")}:
        errors.append("incident_panel_mismatch")
    reference = record.get("submission_journal", {})
    if reference.get("record_id") != journal.get("journal_id") or reference.get("sha256") != journal_digest(journal):
        errors.append("incident_journal_reference_mismatch")
    if reference.get("chain_head_sha256") != journal.get("events", [{}])[-1].get("event_sha256") or reference.get("idempotency_key") != journal.get("idempotency_key"):
        errors.append("incident_journal_head_or_key_mismatch")
    if record.get("panel_input_package_sha256") != journal.get("panel_input_package_sha256"):
        errors.append("incident_input_package_mismatch")
    held = record.get("held_reservation", {})
    if held.get("state") != "awaiting_reconciliation" or not held.get("reservation_id") or not held.get("aggregate_ledger_id"):
        errors.append("incident_held_reservation_incomplete")
    if not record.get("detected_at") or not record.get("reason") or not record.get("recovery_actions"):
        errors.append("incident_detection_or_recovery_missing")
    if record.get("render_record") is not None or record.get("candidate_files") != []:
        errors.append("unknown_incident_fabricated_render_or_candidates")
    if record.get("cost_state") != "AWAITING_RECONCILIATION_DO_NOT_RELEASE_OR_RETRY":
        errors.append("incident_cost_state_invalid")
    return sorted(set(errors))
