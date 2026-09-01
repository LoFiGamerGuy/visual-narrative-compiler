"""Fail-closed gate for comic base rasters and target-repair masks."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def file_errors(item: dict, label: str) -> list[str]:
    errors = []
    path_value, expected = item.get("path"), item.get("sha256")
    if not path_value or not expected or not SHA256.fullmatch(str(expected)):
        return [f"{label}:missing_path_or_sha256"]
    path = (ROOT / path_value).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        return [f"{label}:file_missing_or_outside_root"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        errors.append(f"{label}:sha256_mismatch")
    return errors


def common_errors(record: dict, panel_id: str, plan_revision_id: str) -> list[str]:
    errors = []
    if record.get("medium") != "comic" or record.get("animation_shot_plan") is not None:
        errors.append("medium_or_animation_boundary")
    link = record.get("comic_panel_plan", {})
    if link.get("panel_id") != panel_id or link.get("plan_revision_id") != plan_revision_id:
        errors.append("comic_panel_plan_mismatch")
    review = record.get("review", {})
    if review.get("human_review_status") != "completed" or not isinstance(review.get("human_minutes"), (int, float)) or review.get("human_minutes", 0) <= 0:
        errors.append("authorized_timed_human_review_missing")
    if review.get("accepted") is not True:
        errors.append("human_acceptance_missing")
    return errors


def external_permission_errors(permissions: dict, require_external: bool) -> list[str]:
    if not require_external:
        return []
    errors = []
    if permissions.get("external_upload_authorized") is not True:
        errors.append("external_upload_not_authorized")
    for field in ("external_provider", "external_model_snapshot", "external_endpoint"):
        if not permissions.get(field):
            errors.append(f"external_scope_missing:{field}")
    return errors


def base_raster_errors(record: dict, panel_id: str, plan_revision_id: str, *, require_external: bool = False) -> list[str]:
    errors = common_errors(record, panel_id, plan_revision_id)
    if record.get("record_type") != "ComicPanelBaseRasterApproval" or record.get("state") != "APPROVED_FOR_LOCAL_REPAIR_INPUT":
        errors.append("base_raster_state_not_approved")
    errors.extend(file_errors(record.get("raster", {}), "base_raster"))
    data = record.get("data_classification", {})
    if data.get("fictional_adults_only") is not True or any(data.get(field) is not False for field in ("real_person_likeness", "child_material", "personal_or_biometric_data", "lora_output")):
        errors.append("data_classification_not_permitted")
    permissions = record.get("permissions", {})
    if permissions.get("local_repair_input_authorized") is not True:
        errors.append("local_repair_input_not_authorized")
    errors.extend(external_permission_errors(permissions, require_external))
    return sorted(set(errors))


def repair_mask_errors(record: dict, panel_id: str, plan_revision_id: str, base_approval_id: str, *, require_external: bool = False) -> list[str]:
    errors = common_errors(record, panel_id, plan_revision_id)
    if record.get("record_type") != "ComicPanelRepairMaskReview" or record.get("state") != "APPROVED_FOR_LOCAL_TARGET_REPAIR":
        errors.append("repair_mask_state_not_approved")
    if record.get("base_raster_approval_id") != base_approval_id:
        errors.append("base_raster_approval_mismatch")
    errors.extend(file_errors(record.get("mask", {}), "repair_mask"))
    mask = record.get("mask", {})
    if not mask.get("target_semantics") or not mask.get("protected_semantics"):
        errors.append("target_or_protected_semantics_missing")
    if mask.get("lettering_safe_zone_overlap_fraction") != 0:
        errors.append("lettering_safe_zone_overlap")
    review = record.get("review", {})
    if review.get("target_context_sufficient") is not True or review.get("seam_boundary_reviewed") is not True:
        errors.append("mask_context_or_seam_review_missing")
    permissions = record.get("permissions", {})
    if permissions.get("local_target_repair_authorized") is not True:
        errors.append("local_target_repair_not_authorized")
    errors.extend(external_permission_errors(permissions, require_external))
    return sorted(set(errors))
