"""Validate CH05 P036 repair readiness without rendering or uploading."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
READINESS = ROOT / "production/comic/repair-readiness/ch05-p036-openai-r1.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    readiness = read(READINESS)
    plan_path = ROOT / readiness["comic_panel_plan"]["collection_path"]
    assertion_path = ROOT / readiness["hard_assertion_manifest"]["path"]
    adr_path = ROOT / readiness["selected_mechanism"]["selection_adr"]
    plans = read(plan_path)
    assertions = read(assertion_path)
    panel = next(item for item in plans["plans"] if item["panel_id"] == readiness["comic_panel_plan"]["panel_id"])
    assertion = next(item for item in assertions["assertions"] if item["id"] == readiness["hard_assertion_manifest"]["applicable_panel_assertion"])

    assert readiness["record_type"] == "ComicPanelRepairReadiness"
    assert readiness["state"] == "LOCAL_LAYOUT_CONTROL_COMPLETE_BASE_ART_MISSING_EXTERNAL_EXECUTION_NOT_AUTHORIZED"
    assert readiness["medium"] == plans["medium"] == "comic"
    assert readiness["animation_shot_plan"] is plans["animation_shot_plan"] is None
    assert sha256(plan_path) == readiness["comic_panel_plan"]["collection_sha256"]
    assert sha256(assertion_path) == readiness["hard_assertion_manifest"]["sha256"]
    assert sha256(adr_path) == readiness["selected_mechanism"]["selection_adr_sha256"]
    assert panel["plan_revision_id"] == readiness["comic_panel_plan"]["plan_revision_id"]
    assert panel["display_order"] == readiness["comic_panel_plan"]["display_order"]
    assert panel["visible_adult_cast"] == readiness["intent_snapshot"]["visible_adult_cast"] == ["SOREN", "SIGRID"]
    assert panel["narrative_beat"] == readiness["intent_snapshot"]["narrative_beat"]
    assert panel["composition_intent"] == readiness["intent_snapshot"]["composition_intent"]
    assert panel["comic_direction"]["motion_mode"] == readiness["intent_snapshot"]["motion_mode"] == "practical_action"
    assert panel["comic_direction"]["direction_note"] == readiness["intent_snapshot"]["causal_read"]
    assert panel["comic_direction"]["lettering"]["safe_zones"][0] == readiness["intent_snapshot"]["lettering_safe_zone"]
    assert assertion["applicability"] == panel["panel_id"]
    assert readiness["selected_mechanism"]["execution_authorized"] is False
    assert readiness["targeted_repair_contract"]["base_raster"] is None
    assert readiness["targeted_repair_contract"]["target_mask"] is None
    assert readiness["execution_packet"]["input_uploads"] == []
    assert all(readiness["execution_packet"][field] is None for field in ("request_body", "provider_request_id", "budget_reservation_id", "render_record"))
    smoke = ROOT / readiness["existing_smoke_evidence"]["path"]
    assert sha256(smoke) == readiness["existing_smoke_evidence"]["sha256"]
    assert readiness["existing_smoke_evidence"]["accepted"] is False
    preflight = ROOT / readiness["mask_authoring_preflight"]["path"]
    layout = ROOT / readiness["abstract_layout_control"]["path"]
    assert sha256(preflight) == readiness["mask_authoring_preflight"]["sha256"]
    assert sha256(layout) == readiness["abstract_layout_control"]["sha256"]
    assert readiness["mask_authoring_preflight"]["state"] == "BLOCKED_BASE_COMPOSITION_CONFLICT_NO_MASK_EMITTED"
    assert readiness["mask_authoring_preflight"]["causal_region_lettering_overlap_fraction"] > 0
    assert readiness["abstract_layout_control"]["state"] == "LOCAL_ABSTRACT_COMIC_LAYOUT_CONTROL_NOT_ART"
    assert readiness["abstract_layout_control"]["role_proxy_count"] == 2
    assert readiness["abstract_layout_control"]["target_mask_lettering_safe_zone_overlap_fraction"] == 0
    assert readiness["abstract_layout_control"]["accepted"] is False
    assert readiness["review_contract"]["human_minutes"] is None and readiness["review_contract"]["accepted"] is False
    print("0 failures, 0 warnings (CH05 P036 ComicPanelPlan repair readiness validated; no upload/render authority)")


if __name__ == "__main__":
    main()
