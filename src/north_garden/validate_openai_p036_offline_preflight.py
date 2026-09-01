"""Validate selected-route P036 prerequisites without network capability."""
from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path

from PIL import Image

from preflight_openai_p036_submission import (
    ADAPTER,
    MODEL,
    PANEL_ID,
    PLAN_REVISION_ID,
    ROOT,
    compile_offline_preflight,
    exact_scope,
    input_package_sha256,
)


BASE_PATH = ROOT / "experiments/outputs/ch05_p036_layout_control_r1/ch05-p036-layout-control-r1.png"
MASK_PATH = ROOT / "experiments/outputs/ch05_p036_layout_control_r1/ch05-p036-target-context-mask-r1.png"
READINESS = ROOT / "production/comic/repair-readiness/ch05-p036-openai-r1.json"
SOURCE = ROOT / "src/north_garden/preflight_openai_p036_submission.py"
FIXTURE_OUT = ROOT / "experiments/results/ch05-p036-openai-offline-preflight-synthetic-validation-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_item(path: Path) -> dict:
    with Image.open(path) as image:
        width, height = image.size
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "width": width, "height": height}


def review() -> dict:
    return {"human_review_status": "completed", "human_minutes": 1.0, "accepted": True, "target_context_sufficient": True, "seam_boundary_reviewed": True}


def permissions() -> dict:
    scope = exact_scope()
    return {
        "local_repair_input_authorized": True,
        "local_target_repair_authorized": True,
        "external_upload_authorized": True,
        **scope,
    }


def fixtures() -> tuple[dict, dict, dict, dict]:
    base = {
        "record_type": "ComicPanelBaseRasterApproval", "state": "APPROVED_FOR_LOCAL_REPAIR_INPUT",
        "medium": "comic", "animation_shot_plan": None,
        "record_id": "synthetic-base-fixture",
        "comic_panel_plan": {"panel_id": PANEL_ID, "plan_revision_id": PLAN_REVISION_ID},
        "raster": image_item(BASE_PATH),
        "data_classification": {
            "fictional_adults_only": True, "real_person_likeness": False, "child_material": False,
            "personal_or_biometric_data": False, "lora_output": False,
        },
        "review": review(), "permissions": permissions(),
    }
    mask = {
        "record_type": "ComicPanelRepairMaskReview", "state": "APPROVED_FOR_LOCAL_TARGET_REPAIR",
        "medium": "comic", "animation_shot_plan": None, "record_id": "synthetic-mask-fixture",
        "comic_panel_plan": {"panel_id": PANEL_ID, "plan_revision_id": PLAN_REVISION_ID},
        "base_raster_approval_id": base["record_id"],
        "mask": {
            **image_item(MASK_PATH),
            "target_semantics": "plank, reaching hand proxy, and tin context",
            "protected_semantics": ["two role proxies", "lettering safe zone"],
            "lettering_safe_zone_overlap_fraction": 0,
            "mask_fraction": 0.052881877,
        },
        "review": review(), "permissions": permissions(),
    }
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    package_hash = input_package_sha256(base, mask, readiness)
    authority = {
        "record_type": "ComicPanelExternalUploadAuthority", "state": "AUTHORIZED",
        "record_id": "synthetic-authority-fixture", "panel_id": PANEL_ID, "plan_revision_id": PLAN_REVISION_ID,
        "external_scope": exact_scope(), "panel_input_package_sha256": package_hash,
    }
    reservation = {
        "reservation_id": "synthetic-production-reservation", "budget_domain": "NORTH_GARDEN_CH05_PRODUCTION",
        "adapter_id": ADAPTER, "authority_record_id": authority["record_id"],
        "panel_input_package_sha256": package_hash, "state": "reserved",
    }
    return base, mask, authority, reservation


def main() -> int:
    failures = []
    default_path = ROOT / "experiments/results/ch05-p036-openai-offline-preflight-r1.json"
    default = json.loads(default_path.read_text(encoding="utf-8"))
    expected_blockers = {
        "APPROVED_BASE_RASTER_MISSING_OR_INVALID",
        "APPROVED_REPAIR_MASK_MISSING_OR_INVALID",
        "EXACT_EXTERNAL_AUTHORITY_MISSING_OR_INVALID",
        "DISTINCT_PRODUCTION_RESERVATION_MISSING_OR_INVALID",
    }
    if default["state"] != "BLOCKED_OFFLINE_NO_REQUEST_CONSTRUCTION" or set(default["blockers"]) != expected_blockers:
        failures.append("default preflight blockers are incomplete")
    if default["request_envelope"] is not None or any(default["network"][key] for key in ("network_capability_present", "request_body_constructed", "provider_requests", "external_uploads")):
        failures.append("default preflight constructed or submitted a request")
    if default["network"]["external_cost_usd"] != "0.000000" or default["production_budget_preflight"]["passed"]:
        failures.append("default preflight cost/budget state is invalid")

    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in (node.names if isinstance(node, ast.Import) else [ast.alias(name=node.module or "")])
    }
    prohibited_imports = imported & {"requests", "urllib", "httpx", "openai", "socket", "aiohttp"}
    if prohibited_imports or "OPENAI_API_KEY" in SOURCE.read_text(encoding="utf-8"):
        failures.append(f"offline preflight contains network/client capability: {sorted(prohibited_imports)}")

    base, mask, authority, reservation = fixtures()
    fixture = compile_offline_preflight(
        base=base, mask=mask, authority=authority, reservation=reservation, validation_fixture_mode=True
    )
    FIXTURE_OUT.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    if fixture["blockers"] or fixture["request_envelope"] is None:
        failures.append("complete synthetic prerequisite fixture did not compile an offline envelope")
    elif fixture["request_envelope"]["request_body"] is not None or fixture["request_envelope"]["network_submission_implemented"]:
        failures.append("synthetic fixture produced a request body or executor")
    if fixture["selected_route"]["model_snapshot"] != MODEL:
        failures.append("synthetic fixture selected-route pin changed")

    mutations = [
        ("base hash", lambda b, m, a, r: b["raster"].update(sha256="0" * 64), "APPROVED_BASE_RASTER_MISSING_OR_INVALID"),
        ("mask overlap", lambda b, m, a, r: m["mask"].update(lettering_safe_zone_overlap_fraction=0.1), "APPROVED_REPAIR_MASK_MISSING_OR_INVALID"),
        ("authority scope", lambda b, m, a, r: a["external_scope"].update(external_model_snapshot="wrong"), "EXACT_EXTERNAL_AUTHORITY_MISSING_OR_INVALID"),
        ("authority package", lambda b, m, a, r: a.update(panel_input_package_sha256="0" * 64), "EXACT_EXTERNAL_AUTHORITY_MISSING_OR_INVALID"),
        ("reservation domain", lambda b, m, a, r: r.update(budget_domain="G07_BAKEOFF"), "DISTINCT_PRODUCTION_RESERVATION_MISSING_OR_INVALID"),
        ("reservation package", lambda b, m, a, r: r.update(panel_input_package_sha256="0" * 64), "DISTINCT_PRODUCTION_RESERVATION_MISSING_OR_INVALID"),
    ]
    for label, mutate, expected in mutations:
        b, m, a, r = map(copy.deepcopy, fixtures())
        mutate(b, m, a, r)
        result = compile_offline_preflight(base=b, mask=m, authority=a, reservation=r, validation_fixture_mode=True)
        if expected not in result["blockers"] or result["request_envelope"] is not None:
            failures.append(f"offline preflight mutation passed: {label}")

    for failure in failures:
        print(f"failure: {failure}")
    if failures:
        return 1
    print("0 failures, 0 warnings (4 real blockers; synthetic metadata envelope only; no client/body/network; 6/6 mutations blocked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
