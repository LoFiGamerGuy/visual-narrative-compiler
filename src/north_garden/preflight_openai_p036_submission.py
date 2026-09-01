"""Offline-only prerequisite compiler for selected-route CH05 P036 repair."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from comic_input_gate import base_raster_errors, repair_mask_errors
from comic_run_ledger import canonical_sha256
from production_budget import DOMAIN, ProductionBudgetError, preflight_production_budget


ROOT = Path(__file__).resolve().parents[2]
READINESS = ROOT / "production/comic/repair-readiness/ch05-p036-openai-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
OUT = ROOT / "experiments/results/ch05-p036-openai-offline-preflight-r1.json"
ADAPTER = "openai_gpt_image_2"
PROVIDER = "OpenAI API"
MODEL = "gpt-image-2-2026-04-21"
ENDPOINT = "https://api.openai.com/v1/images/edits"
PANEL_ID = "ng-ch05-sc01-p036"
PLAN_REVISION_ID = "ng-ch05-sc01-p036-plan-r1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_package_sha256(base: dict, mask: dict, readiness: dict) -> str:
    return canonical_sha256({
        "panel_id": PANEL_ID,
        "plan_revision_id": PLAN_REVISION_ID,
        "base_raster_sha256": base["raster"]["sha256"],
        "repair_mask_sha256": mask["mask"]["sha256"],
        "target_semantics": mask["mask"]["target_semantics"],
        "protected_semantics": mask["mask"]["protected_semantics"],
        "intent_snapshot": readiness["intent_snapshot"],
    })


def exact_scope() -> dict:
    return {
        "external_provider": PROVIDER,
        "external_model_snapshot": MODEL,
        "external_endpoint": ENDPOINT,
    }


def compile_offline_preflight(
    *,
    base: dict | None,
    mask: dict | None,
    authority: dict | None,
    reservation: dict | None,
    validation_fixture_mode: bool = False,
) -> dict:
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    blockers = []
    if readiness["comic_panel_plan"]["panel_id"] != PANEL_ID or readiness["comic_panel_plan"]["plan_revision_id"] != PLAN_REVISION_ID:
        blockers.append("READINESS_PLAN_BINDING_MISMATCH")
    selected = readiness["selected_mechanism"]
    if selected.get("adapter_id") != ADAPTER or selected.get("model_snapshot") != MODEL or selected.get("endpoint") != "/v1/images/edits":
        blockers.append("SELECTED_ROUTE_MISMATCH")

    scope = exact_scope()
    base_errors = ["base_record_missing"] if base is None else base_raster_errors(
        base, PANEL_ID, PLAN_REVISION_ID, require_external=True, external_scope=scope
    )
    if base_errors:
        blockers.append("APPROVED_BASE_RASTER_MISSING_OR_INVALID")
    base_approval_id = base.get("record_id") if base else "MISSING"
    mask_errors = ["mask_record_missing"] if mask is None else repair_mask_errors(
        mask, PANEL_ID, PLAN_REVISION_ID, base_approval_id, require_external=True, external_scope=scope
    )
    if mask_errors:
        blockers.append("APPROVED_REPAIR_MASK_MISSING_OR_INVALID")

    package_hash = None
    if not base_errors and not mask_errors:
        package_hash = input_package_sha256(base, mask, readiness)
    authority_errors = []
    if authority is None:
        authority_errors.append("authority_record_missing")
    else:
        if authority.get("record_type") != "ComicPanelExternalUploadAuthority" or authority.get("state") != "AUTHORIZED":
            authority_errors.append("authority_state_invalid")
        if authority.get("external_scope") != scope:
            authority_errors.append("authority_scope_mismatch")
        if authority.get("panel_id") != PANEL_ID or authority.get("plan_revision_id") != PLAN_REVISION_ID:
            authority_errors.append("authority_panel_mismatch")
        if package_hash is None or authority.get("panel_input_package_sha256") != package_hash:
            authority_errors.append("authority_input_package_hash_mismatch")
    if authority_errors:
        blockers.append("EXACT_EXTERNAL_AUTHORITY_MISSING_OR_INVALID")

    reservation_errors = []
    if reservation is None:
        reservation_errors.append("production_reservation_missing")
    else:
        expected = {
            "budget_domain": DOMAIN,
            "adapter_id": ADAPTER,
            "authority_record_id": authority.get("record_id") if authority else None,
            "panel_input_package_sha256": package_hash,
            "state": "reserved",
        }
        for field, value in expected.items():
            if reservation.get(field) != value:
                reservation_errors.append(f"production_reservation_mismatch:{field}")
        if not reservation.get("reservation_id"):
            reservation_errors.append("production_reservation_id_missing")
    if reservation_errors:
        blockers.append("DISTINCT_PRODUCTION_RESERVATION_MISSING_OR_INVALID")

    ready = not blockers
    envelope = None
    if ready:
        envelope = {
            "record_type": "OfflineProviderRequestEnvelope",
            "state": "SYNTHETIC_VALIDATION_ONLY" if validation_fixture_mode else "OFFLINE_PREREQUISITES_COMPLETE_NO_EXECUTOR_IMPLEMENTED",
            "adapter_id": ADAPTER,
            "provider": PROVIDER,
            "model_snapshot": MODEL,
            "endpoint": ENDPOINT,
            "panel_id": PANEL_ID,
            "plan_revision_id": PLAN_REVISION_ID,
            "panel_input_package_sha256": package_hash,
            "base_raster_sha256": base["raster"]["sha256"],
            "repair_mask_sha256": mask["mask"]["sha256"],
            "compiled_intent": {
                "narrative_beat": readiness["intent_snapshot"]["narrative_beat"],
                "composition_intent": readiness["intent_snapshot"]["composition_intent"],
                "target_semantics": readiness["targeted_repair_contract"]["target_semantics"],
                "protected_semantics": readiness["targeted_repair_contract"]["protected_semantics"],
                "lettering_safe_zone": readiness["intent_snapshot"]["lettering_safe_zone"],
            },
            "authority_record_id": authority["record_id"],
            "production_reservation_id": reservation["reservation_id"],
            "request_body": None,
            "network_submission_implemented": False,
        }
    return {
        "record_type": "OpenAIP036OfflineSubmissionPreflight",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p036-openai-offline-submission-preflight-r1",
        "state": "OFFLINE_PREREQUISITES_COMPLETE_NO_EXECUTOR" if ready else "BLOCKED_OFFLINE_NO_REQUEST_CONSTRUCTION",
        "validation_fixture_mode": validation_fixture_mode,
        "medium": "comic",
        "animation_shot_plan": None,
        "sources": {
            "repair_readiness": {"path": READINESS.relative_to(ROOT).as_posix(), "sha256": sha256(READINESS)},
            "comic_panel_plans": {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha256(PLANS)},
        },
        "selected_route": {"adapter_id": ADAPTER, "provider": PROVIDER, "model_snapshot": MODEL, "endpoint": ENDPOINT},
        "blockers": blockers,
        "details": {
            "base_gate_errors": base_errors,
            "mask_gate_errors": mask_errors,
            "authority_errors": authority_errors,
            "reservation_errors": reservation_errors,
        },
        "panel_input_package_sha256": package_hash,
        "request_envelope": envelope,
        "network": {
            "network_capability_present": False,
            "request_body_constructed": False,
            "provider_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        },
        "boundary": "This compiler has no network executor. A complete offline envelope would still require a separately reviewed implementation milestone before submission.",
    }


def main() -> None:
    try:
        preflight_production_budget(ADAPTER, {})
        budget_state = "UNEXPECTEDLY_PASSED"
    except ProductionBudgetError as error:
        budget_state = str(error)
    record = compile_offline_preflight(base=None, mask=None, authority=None, reservation=None)
    record["production_budget_preflight"] = {
        "passed": False,
        "reason": budget_state,
        "bakeoff_budget_not_considered": True,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
