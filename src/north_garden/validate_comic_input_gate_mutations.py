"""Adversarial mutation checks for the comic input gate."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from PIL import Image

from comic_input_gate import ROOT, base_raster_errors, repair_mask_errors


PANEL = "ng-ch05-sc01-p036"
REVISION = "ng-ch05-sc01-p036-plan-r1"
BASE_PATH = ROOT / "experiments/outputs/ch05_p036_layout_control_r1/ch05-p036-layout-control-r1.png"
MASK_PATH = ROOT / "experiments/outputs/ch05_p036_layout_control_r1/ch05-p036-target-context-mask-r1.png"
NON_IMAGE_PATH = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_item(path: Path) -> dict:
    with Image.open(path) as image:
        width, height = image.size
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest(path),
        "width": width,
        "height": height,
    }


def valid_base() -> dict:
    return {
        "record_type": "ComicPanelBaseRasterApproval",
        "state": "APPROVED_FOR_LOCAL_REPAIR_INPUT",
        "medium": "comic",
        "animation_shot_plan": None,
        "comic_panel_plan": {"panel_id": PANEL, "plan_revision_id": REVISION},
        "raster": image_item(BASE_PATH),
        "data_classification": {
            "fictional_adults_only": True,
            "real_person_likeness": False,
            "child_material": False,
            "personal_or_biometric_data": False,
            "lora_output": False,
        },
        "review": {"human_review_status": "completed", "human_minutes": 1.0, "accepted": True},
        "permissions": {
            "local_repair_input_authorized": True,
            "external_upload_authorized": False,
            "external_provider": None,
            "external_model_snapshot": None,
            "external_endpoint": None,
        },
    }


def valid_mask() -> dict:
    item = image_item(MASK_PATH)
    return {
        "record_type": "ComicPanelRepairMaskReview",
        "state": "APPROVED_FOR_LOCAL_TARGET_REPAIR",
        "medium": "comic",
        "animation_shot_plan": None,
        "comic_panel_plan": {"panel_id": PANEL, "plan_revision_id": REVISION},
        "base_raster_approval_id": "test-base-approval",
        "mask": {
            **item,
            "target_semantics": "plank, reaching hand proxy, and tin context",
            "protected_semantics": ["two role proxies", "lettering safe zone"],
            "lettering_safe_zone_overlap_fraction": 0,
            "mask_fraction": 0.052881877,
        },
        "review": {
            "human_review_status": "completed",
            "human_minutes": 1.0,
            "target_context_sufficient": True,
            "seam_boundary_reviewed": True,
            "accepted": True,
        },
        "permissions": {
            "local_target_repair_authorized": True,
            "external_upload_authorized": False,
            "external_provider": None,
            "external_model_snapshot": None,
            "external_endpoint": None,
        },
    }


def main() -> int:
    failures = []
    base, mask = valid_base(), valid_mask()
    if base_raster_errors(base, PANEL, REVISION):
        failures.append("valid local base control did not pass")
    if repair_mask_errors(mask, PANEL, REVISION, "test-base-approval"):
        failures.append("valid local mask control did not pass")
    if not base_raster_errors(base, PANEL, REVISION, require_external=True):
        failures.append("local base approval incorrectly implied external permission")
    if not repair_mask_errors(mask, PANEL, REVISION, "test-base-approval", require_external=True):
        failures.append("local mask approval incorrectly implied external permission")

    declared = copy.deepcopy(base)
    declared["permissions"].update(
        external_upload_authorized=True,
        external_provider="declared-provider",
        external_model_snapshot="declared-model",
        external_endpoint="https://example.invalid/v1/edit",
    )
    if not base_raster_errors(declared, PANEL, REVISION, require_external=True):
        failures.append("self-declared external scope passed without a separate authority scope")
    matching_scope = {
        "external_provider": "declared-provider",
        "external_model_snapshot": "declared-model",
        "external_endpoint": "https://example.invalid/v1/edit",
    }
    if base_raster_errors(
        declared, PANEL, REVISION, require_external=True, external_scope=matching_scope
    ):
        failures.append("matching record and explicit authority scope did not pass")
    mismatched_scope = {**matching_scope, "external_model_snapshot": "different-model"}
    if not base_raster_errors(
        declared, PANEL, REVISION, require_external=True, external_scope=mismatched_scope
    ):
        failures.append("mismatched external authority scope passed")

    mutations = []
    for label, record, mutate, gate in [
        ("base_hash", base, lambda x: x["raster"].update(sha256="0" * 64), "base"),
        ("base_child", base, lambda x: x["data_classification"].update(child_material=True), "base"),
        ("base_review", base, lambda x: x["review"].update(human_minutes=None), "base"),
        ("base_panel", base, lambda x: x["comic_panel_plan"].update(panel_id="wrong"), "base"),
        ("base_dimensions", base, lambda x: x["raster"].update(width=1), "base"),
        ("mask_overlap", mask, lambda x: x["mask"].update(lettering_safe_zone_overlap_fraction=0.01), "mask"),
        ("mask_fraction", mask, lambda x: x["mask"].update(mask_fraction=0), "mask"),
        ("mask_seam", mask, lambda x: x["review"].update(seam_boundary_reviewed=False), "mask"),
        ("mask_base", mask, lambda x: x.update(base_raster_approval_id="wrong"), "mask"),
    ]:
        candidate = copy.deepcopy(record)
        mutate(candidate)
        errors = (
            base_raster_errors(candidate, PANEL, REVISION)
            if gate == "base"
            else repair_mask_errors(candidate, PANEL, REVISION, "test-base-approval")
        )
        mutations.append({"label": label, "rejected": bool(errors), "errors": errors})
        if not errors:
            failures.append(f"mutation passed unexpectedly: {label}")

    fake = copy.deepcopy(base)
    fake["raster"] = {
        "path": NON_IMAGE_PATH.relative_to(ROOT).as_posix(),
        "sha256": digest(NON_IMAGE_PATH),
        "width": 1536,
        "height": 1024,
    }
    fake_errors = base_raster_errors(fake, PANEL, REVISION)
    mutations.append({"label": "non_image_payload", "rejected": bool(fake_errors), "errors": fake_errors})
    if not fake_errors:
        failures.append("hash-valid non-image payload passed as a raster")

    for failure in failures:
        print(f"failure: {failure}")
    if failures:
        return 1
    print(json.dumps({"mutations": len(mutations), "rejected": sum(item["rejected"] for item in mutations)}, indent=2))
    print("0 failures, 0 warnings (10/10 partial or malformed comic inputs rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
