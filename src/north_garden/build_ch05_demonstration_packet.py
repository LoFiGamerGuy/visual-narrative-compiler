"""Compile a six-panel, no-network CH05 execution/readiness packet."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from comic_input_gate import base_raster_errors, repair_mask_errors


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
ASSERTIONS = ROOT / "production/comic/hard-assertion-manifests/ch05-mill-signal-r1.json"
SLICE = ROOT / "production/comic/demonstration-slices/ch05-p033-p038-r1.json"
PACKET = ROOT / "production/comic/demonstration-packets/ch05-p033-p038-no-network-r1.json"
BASE_TEMPLATE = ROOT / "config/record-templates/comic-panel-base-raster-approval-v1.json"
MASK_TEMPLATE = ROOT / "config/record-templates/comic-panel-repair-mask-review-v1.json"
OUT = ROOT / "experiments/results/ch05-p033-p038-no-network-packet-r1.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)}


def main() -> None:
    plans, assertions, selected, specification = map(read, [PLANS, ASSERTIONS, SLICE, PACKET])
    base_template, mask_template = map(read, [BASE_TEMPLATE, MASK_TEMPLATE])
    plan_by_id = {item["panel_id"]: item for item in plans["plans"]}
    assertion_by_panel = {
        item["applicability"]: item
        for item in assertions["assertions"]
        if item.get("applicability")
    }

    panels = []
    for panel_id in specification["panel_ids"]:
        plan = plan_by_id[panel_id]
        assertion = assertion_by_panel[panel_id]
        base_local = base_raster_errors(base_template, panel_id, plan["plan_revision_id"])
        base_external = base_raster_errors(
            base_template, panel_id, plan["plan_revision_id"], require_external=True
        )
        repair = panel_id == "ng-ch05-sc01-p036"
        mask_local = (
            repair_mask_errors(
                mask_template,
                panel_id,
                plan["plan_revision_id"],
                "MISSING_APPROVED_BASE",
            )
            if repair
            else []
        )
        mask_external = (
            repair_mask_errors(
                mask_template,
                panel_id,
                plan["plan_revision_id"],
                "MISSING_APPROVED_BASE",
                require_external=True,
            )
            if repair
            else []
        )
        panels.append(
            {
                "panel_id": panel_id,
                "plan_revision_id": plan["plan_revision_id"],
                "display_order": plan["display_order"],
                "applicable_hard_assertion": assertion["id"],
                "visible_adult_count": len(plan["visible_adult_cast"]),
                "local_base_gate": {"ready": not base_local, "reasons": base_local},
                "local_repair_mask_gate": {
                    "applicable": repair,
                    "ready": repair and not mask_local,
                    "reasons": mask_local,
                },
                "external_gate": {
                    "ready": not base_external and (not repair or not mask_external),
                    "base_reasons": base_external,
                    "mask_reasons": mask_external,
                },
                "render_record": None,
                "human_review_status": "not_yet_performed",
                "human_minutes": None,
                "accepted": False,
                "executable": False,
            }
        )

    corpus = "\n".join(
        value
        for panel_id in specification["panel_ids"]
        for value in (
            plan_by_id[panel_id]["narrative_beat"],
            plan_by_id[panel_id]["composition_intent"],
            assertion_by_panel[panel_id]["requirement"],
        )
    )
    continuity = []
    for contract in specification["derived_continuity_contracts"]:
        missing = [term for term in contract["required_terms"] if term.casefold() not in corpus.casefold()]
        continuity.append(
            {
                "id": contract["id"],
                "source_panels": contract["source_panels"],
                "target_panels": contract["target_panels"],
                "source_terms_verified": not missing,
                "missing_terms": missing,
                "human_review_status": "not_yet_performed",
                "human_minutes": None,
            }
        )

    per_panel_task_count = len(specification["review_workload_contract"]["per_panel_tasks"])
    repair_task_count = len(specification["review_workload_contract"]["repair_only_tasks"])
    result = {
        "record_type": "ComicPanelDemonstrationPacketPreflight",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p033-p038-no-network-packet-preflight-r1",
        "state": "NON_EXECUTABLE_INPUT_AND_REVIEW_GATES_OPEN",
        "medium": "comic",
        "animation_shot_plan": None,
        "sources": {
            "comic_panel_plans": source(PLANS),
            "hard_assertions": source(ASSERTIONS),
            "demonstration_slice": source(SLICE),
            "packet_specification": source(PACKET),
            "base_approval_template": source(BASE_TEMPLATE),
            "repair_mask_template": source(MASK_TEMPLATE),
        },
        "summary": {
            "panel_count": len(panels),
            "executable_panels": sum(item["executable"] for item in panels),
            "approved_base_rasters": sum(item["local_base_gate"]["ready"] for item in panels),
            "approved_repair_masks": sum(item["local_repair_mask_gate"]["ready"] for item in panels),
            "render_records": 0,
            "accepted_panels": 0,
            "external_uploads": 0,
            "provider_requests": 0,
            "new_external_cost_usd": "0.000000",
        },
        "review_workload": {
            "per_panel_task_kinds": per_panel_task_count,
            "repair_only_task_kinds": repair_task_count,
            "panel_task_instances": per_panel_task_count * len(panels),
            "repair_task_instances": repair_task_count,
            "continuity_task_instances": len(continuity),
            "total_task_instances": per_panel_task_count * len(panels) + repair_task_count + len(continuity),
            "human_minutes": None,
            "measurement_rule": "Record positive elapsed human minutes only after authorized review; do not infer minutes from task counts.",
        },
        "continuity_contracts": continuity,
        "panels": panels,
        "limitations": [
            "Task-instance counts are workload structure, not a time estimate.",
            "Source-term verification is not visual continuity evidence.",
            "No approved base art, repair mask, render, human review, or acceptance exists.",
            "External upload remains a separate exact-scope authority gate under ADR-0026.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
