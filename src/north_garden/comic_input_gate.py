"""Fail-closed gate for comic base rasters and target-repair masks."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from PIL import Image, UnidentifiedImageError


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


def image_errors(item: dict, label: str, *, mask: bool = False) -> list[str]:
    """Validate that a hash-addressed input is actually a supported raster."""
    path_value = item.get("path")
    if not path_value:
        return []  # file_errors owns missing-path reporting.
    path = (ROOT / path_value).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        return []  # file_errors owns missing/out-of-root reporting.
    errors = []
    if path.suffix.casefold() not in {".png", ".jpg", ".jpeg", ".webp"}:
        errors.append(f"{label}:unsupported_image_extension")
    try:
        with Image.open(path) as image:
            width, height = image.size
            image_format = image.format
            mode = image.mode
            image.verify()
    except (OSError, UnidentifiedImageError):
        return [*errors, f"{label}:invalid_image_payload"]
    if image_format not in {"PNG", "JPEG", "WEBP"}:
        errors.append(f"{label}:unsupported_image_format")
    if item.get("width") != width or item.get("height") != height:
        errors.append(f"{label}:declared_dimensions_mismatch")
    if mask and (image_format != "PNG" or mode not in {"1", "L"}):
        errors.append(f"{label}:mask_must_be_grayscale_png")
    return errors


def common_errors(record: dict, panel_id: str, plan_revision_id: str) -> list[str]:
    errors = []
    if record.get("synthetic_validation_fixture") is True:
        errors.append("synthetic_validation_fixture_not_approvable")
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


def external_permission_errors(
    permissions: dict, require_external: bool, external_scope: dict | None = None
) -> list[str]:
    if not require_external:
        return []
    errors = []
    if permissions.get("external_upload_authorized") is not True:
        errors.append("external_upload_not_authorized")
    scope_fields = ("external_provider", "external_model_snapshot", "external_endpoint")
    for field in scope_fields:
        if not permissions.get(field):
            errors.append(f"external_scope_missing:{field}")
    if external_scope is None:
        errors.append("external_authority_scope_missing")
    else:
        for field in scope_fields:
            if permissions.get(field) != external_scope.get(field):
                errors.append(f"external_scope_mismatch:{field}")
    return errors


def base_raster_errors(
    record: dict,
    panel_id: str,
    plan_revision_id: str,
    *,
    require_external: bool = False,
    external_scope: dict | None = None,
) -> list[str]:
    errors = common_errors(record, panel_id, plan_revision_id)
    if record.get("record_type") != "ComicPanelBaseRasterApproval" or record.get("state") != "APPROVED_FOR_LOCAL_REPAIR_INPUT":
        errors.append("base_raster_state_not_approved")
    errors.extend(file_errors(record.get("raster", {}), "base_raster"))
    errors.extend(image_errors(record.get("raster", {}), "base_raster"))
    data = record.get("data_classification", {})
    if data.get("fictional_adults_only") is not True or any(data.get(field) is not False for field in ("real_person_likeness", "child_material", "personal_or_biometric_data", "lora_output")):
        errors.append("data_classification_not_permitted")
    permissions = record.get("permissions", {})
    if permissions.get("local_repair_input_authorized") is not True:
        errors.append("local_repair_input_not_authorized")
    errors.extend(external_permission_errors(permissions, require_external, external_scope))
    return sorted(set(errors))


def repair_mask_errors(
    record: dict,
    panel_id: str,
    plan_revision_id: str,
    base_approval_id: str,
    *,
    require_external: bool = False,
    external_scope: dict | None = None,
) -> list[str]:
    errors = common_errors(record, panel_id, plan_revision_id)
    if record.get("record_type") != "ComicPanelRepairMaskReview" or record.get("state") != "APPROVED_FOR_LOCAL_TARGET_REPAIR":
        errors.append("repair_mask_state_not_approved")
    if record.get("base_raster_approval_id") != base_approval_id:
        errors.append("base_raster_approval_mismatch")
    errors.extend(file_errors(record.get("mask", {}), "repair_mask"))
    mask = record.get("mask", {})
    errors.extend(image_errors(mask, "repair_mask", mask=True))
    if not mask.get("target_semantics") or not mask.get("protected_semantics"):
        errors.append("target_or_protected_semantics_missing")
    if not isinstance(mask.get("mask_fraction"), (int, float)) or not 0 < mask.get("mask_fraction", 0) <= 1:
        errors.append("mask_fraction_invalid")
    if mask.get("lettering_safe_zone_overlap_fraction") != 0:
        errors.append("lettering_safe_zone_overlap")
    review = record.get("review", {})
    if review.get("target_context_sufficient") is not True or review.get("seam_boundary_reviewed") is not True:
        errors.append("mask_context_or_seam_review_missing")
    permissions = record.get("permissions", {})
    if permissions.get("local_target_repair_authorized") is not True:
        errors.append("local_target_repair_not_authorized")
    errors.extend(external_permission_errors(permissions, require_external, external_scope))
    return sorted(set(errors))
