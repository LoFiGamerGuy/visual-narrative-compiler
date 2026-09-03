"""Compile a reusable, non-executable full-chapter ComicPanelPlan authoring contract."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_OUT = ROOT / "production/comic/contracts/complete-chapter-comicpanelplan-authoring-contract-r1.json"
TEMPLATE_OUT = ROOT / "production/comic/templates/complete-chapter-comicpanelplan-template-r1.json"
SOURCES = [
    ROOT / "production/comic/ch05-sc01-panel-plans-v1.json",
    ROOT / "production/comic/run-manifests/ch05-chapter-sequence-production-batches-r1.json",
    ROOT / "production/comic/layout/ch05-panel-scale-cadence-policy-r1.json",
    ROOT / "docs/research/evidence/ch05-complete-chapter-release-r6.json",
    ROOT / "production/comic/style-direction/north-garden-cross-chapter-continuity-r1.json",
]
PHASES = [
    ("phase01", "opening_state_and_orientation", "Establish current state, goal, geography, and departure or initiating change."),
    ("phase02", "movement_and_escalation", "Advance through causal travel/action beats with at least one readable obstacle or warning."),
    ("phase03", "threshold_and_entry", "Cross or refuse a meaningful threshold; preserve role order and spatial consequence."),
    ("phase04", "causal_interaction_and_evidence", "Use hands, tools, terrain, and story objects to produce or reveal evidence."),
    ("phase05", "deduction_choice_and_consequence", "Let characters interpret evidence and make a consequential choice through readable action/dialogue."),
    ("phase06", "reversal_return_or_closure", "Deliver a changed-state reveal, return vector, cliffhanger, or earned closure."),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def binding(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def main() -> int:
    plan, batches, cadence, release, continuity = [load(path) for path in SOURCES]
    if len(plan["plans"]) != 50 or batches["summary"]["sequence_count"] != 12:
        raise ValueError("CH05 measured baseline changed")
    if release["measured_summary"]["selected_chapter_panels"] != 50:
        raise ValueError("CH05 release baseline changed")
    contract: dict[str, Any] = {
        "record_type": "CompleteChapterComicPanelPlanAuthoringContract",
        "schema_version": "1.0",
        "record_id": "ng-complete-chapter-comicpanelplan-authoring-contract-r1",
        "state": "REUSABLE_AUTHORING_CONTRACT_NON_EXECUTABLE",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "evidence_sources": [binding(path) for path in SOURCES],
        "measured_baseline": {
            "chapter": "CH05",
            "panel_count": 50,
            "sequence_count": 12,
            "panels_per_sequence_min": batches["summary"]["minimum_panels_per_sequence"],
            "panels_per_sequence_max": batches["summary"]["maximum_panels_per_sequence"],
            "selected_panels": 50,
            "agent_triage": release["measured_summary"]["agent_triage"],
            "scale_role_count": cadence["rule_count"],
            "result_interpretation": "Evidence baseline only; not a mandatory chapter length or accepted-art claim.",
        },
        "collection_requirements": {
            "record_type": "ComicPanelPlanCollection",
            "story_state_id": "required_nonempty",
            "declared_target_panel_count": "required_positive_integer_equal_to_plan_count",
            "chapter_title": "required_nonempty",
            "chapter_logline": "required_nonempty",
            "opening_state": "required_nonempty",
            "closing_changed_state": "required_nonempty_and_distinct_from_opening_state",
            "continuity_contract": "required",
            "progression_contract": "required_even_when_all_categories_are_absent",
            "promotion_decision": "required_before_prompt_or_render_execution",
        },
        "required_narrative_phases": [
            {"phase_id": phase_id, "narrative_function": function, "requirement": requirement, "minimum_panel_count": 1}
            for phase_id, function, requirement in PHASES
        ],
        "panel_required_fields": [
            "panel_id", "plan_revision_id", "display_order", "scene_beat_id", "narrative_phase_id",
            "narrative_beat", "composition_intent", "visible_adult_cast", "asset_ids", "spatial_mode",
            "spatial_stage_contract_id", "spatial_assignments", "sequence_id", "scale_role",
            "density_class", "continuity_carry_in", "continuity_carry_out", "comic_direction",
        ],
        "panel_rules": {
            "identity": "panel_id is stable; plan_revision_id changes whenever intent changes",
            "display_order": "contiguous positive integers beginning at 1",
            "adult_cast": "only explicitly named fictional adults; zero-person inserts use an empty list",
            "causal_action": "name body/tool/terrain/object relationships; generic speed-line texture cannot substitute",
            "lettering": "at least one normalized safe zone or explicit outside-art/gutter policy; never cover faces, people, important hands, or story objects",
            "continuity": "every carried prop, injury, garment, weather state, location vector, and clue must have explicit carry-in/out",
            "progression": "armor, weapons, upgraded clothing, monsters, classes, and system UI require explicit story/canon bindings",
        },
        "sequence_rules": {
            "recommended_panel_range_from_ch05": [3, 5],
            "required_fields": ["sequence_id", "narrative_order", "title", "narrative_functions", "panel_ids", "continuity_entry", "continuity_exit"],
            "coverage": "every panel appears in exactly one sequence and every sequence is contiguous in display order",
            "generation_strategy": "coherent sequence-first generation may be proposed only after plan/prompt/upload preflight; deterministic crops and panel-local repair preserve non-target hashes",
        },
        "cadence_classes": ["ANCHOR_OR_ACTION", "CHARACTER_OR_REACTION", "INSERT_OR_PAUSE"],
        "scale_roles": cadence["rules"],
        "chapter_acceptance_gates": [
            "all declared ComicPanelPlans present exactly once",
            "all six narrative phases represented",
            "opening and closing states are materially different",
            "continuity carry-in/out graph is closed or explicitly cliffhanging",
            "variable cadence contains action/reveal anchors and lower-density relief beats",
            "all lettering placements preserve protected subjects at phone width",
            "every provider execution has a complete RenderRecord",
            "human review minutes and decisions are explicit",
            "commercial clearance and exact-production-base decisions remain separate",
        ],
        "current_identity_direction": continuity["future_generation_identity_contract"],
        "non_executable_boundary": {
            "story_beats_authored": 0,
            "comic_panel_plans_created": 0,
            "prompts_created": 0,
            "provider_calls": 0,
            "uploads": 0,
            "generated_candidates": 0,
            "accepted_candidates": 0,
            "commercial_decisions": 0,
        },
    }
    template = {
        "record_type": "ComicPanelPlanAuthoringTemplate",
        "schema_version": "1.0",
        "record_id": None,
        "state": "EMPTY_TEMPLATE_NOT_A_COMICPANELPLAN_COLLECTION",
        "contract": binding(CONTRACT_OUT) if CONTRACT_OUT.is_file() else {"path": CONTRACT_OUT.relative_to(ROOT).as_posix(), "sha256": None},
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "chapter_title": None,
        "chapter_logline": None,
        "story_state_id": None,
        "opening_state": None,
        "closing_changed_state": None,
        "declared_target_panel_count": None,
        "continuity_contract": {"characters": [], "wardrobe": [], "injuries": [], "props": [], "locations": [], "weather": [], "clues": []},
        "progression_contract": {"armor": None, "weapons": None, "upgraded_clothing": None, "monsters": None, "classes": None, "system_ui": None},
        "narrative_phases": [{"phase_id": phase_id, "narrative_function": function, "story_beats": [], "completion_state": "UNAUTHORED"} for phase_id, function, _ in PHASES],
        "sequences": [],
        "plans": [],
        "promotion_decision": None,
        "execution_ready": False,
        "authoring_complete": False,
    }
    CONTRACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    TEMPLATE_OUT.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT_OUT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    template["contract"] = binding(CONTRACT_OUT)
    TEMPLATE_OUT.write_text(json.dumps(template, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"contract": CONTRACT_OUT.relative_to(ROOT).as_posix(), "contract_sha256": sha256(CONTRACT_OUT), "template": TEMPLATE_OUT.relative_to(ROOT).as_posix(), "template_sha256": sha256(TEMPLATE_OUT), "phases": len(PHASES), "scale_roles": cadence["rule_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
