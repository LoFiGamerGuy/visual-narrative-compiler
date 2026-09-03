"""Fail-closed semantic validation for a future full-chapter ComicPanelPlan graph."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "production/comic/contracts/complete-chapter-comicpanelplan-authoring-contract-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/complete-chapter-semantic-graph-validator-r1.json"
FORBIDDEN_KEYS = {"prompt", "output", "provider", "service", "model", "endpoint", "request_id", "provider_usage", "cost_usd", "monetary_cost_usd", "seed", "input_references", "rendered_candidate"}
CONTINUITY_CATEGORIES = ("characters", "wardrobe", "injuries", "props", "locations", "weather", "clues")
PROGRESSION_PREFIXES = {
    "armor": "ng-progression-armor-",
    "weapons": "ng-progression-weapon-",
    "upgraded_clothing": "ng-progression-clothing-",
    "monsters": "ng-progression-monster-",
    "classes": "ng-progression-class-",
    "system_ui": "ng-progression-ui-",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def semantic_fixture() -> dict[str, Any]:
    phases = [
        "phase01", "phase02", "phase03", "phase04", "phase05", "phase06",
    ]
    functions = [
        "opening_state_and_orientation", "movement_and_escalation", "threshold_and_entry",
        "causal_interaction_and_evidence", "deduction_choice_and_consequence", "reversal_return_or_closure",
    ]
    scale_roles = [
        "WIDE_DIRECTIONAL_ANCHOR", "MEDIUM_TWO_SHOT", "SMALL_SENSORY_INSERT",
        "TALL_OR_WIDE_DUAL_CAUSAL", "MEDIUM_CHARACTER_CLUE", "WIDE_ENVIRONMENTAL_MOTION",
    ]
    densities = ["MEDIUM", "MEDIUM", "LOW", "HIGH", "LOW", "HIGH"]
    cast = [["ADULT_A", "ADULT_B"], ["ADULT_A", "ADULT_B"], [], ["ADULT_A", "ADULT_B"], ["ADULT_B"], ["ADULT_A", "ADULT_B"]]
    shared_state = {
        "characters": ["ADULT_A", "ADULT_B"], "wardrobe": ["base_practical_clothing"],
        "injuries": [], "props": ["folded_map"], "locations": ["test_route"],
        "weather": ["light_rain"], "clues": [],
    }
    plans = []
    for index in range(6):
        panel_id = f"synthetic-comic-p{index + 1:03d}"
        plans.append({
            "panel_id": panel_id,
            "plan_revision_id": f"{panel_id}-plan-r1",
            "display_order": index + 1,
            "scene_beat_id": f"synthetic-beat-{index + 1:02d}",
            "narrative_phase_id": phases[index],
            "narrative_beat": f"Synthetic adult-only causal beat {index + 1}; no North Garden canon.",
            "composition_intent": f"Synthetic {densities[index].lower()}-density composition with protected quiet upper field.",
            "visible_adult_cast": cast[index],
            "asset_ids": ["synthetic-fictional-adult-a", "synthetic-fictional-adult-b"] if cast[index] else ["synthetic-object-insert"],
            "spatial_mode": "2d_only",
            "spatial_stage_contract_id": None,
            "spatial_assignments": [],
            "sequence_id": "synthetic-seq01" if index < 3 else "synthetic-seq02",
            "scale_role": scale_roles[index],
            "density_class": densities[index],
            "continuity_carry_in": copy.deepcopy(shared_state),
            "continuity_carry_out": copy.deepcopy(shared_state),
            "comic_direction": {
                "motion_mode": "held_observation" if densities[index] == "LOW" else "directional_motion",
                "direction_note": "Synthetic physical or observational direction; no renderer prompt.",
                "lettering": {"placement_policy": "safe_zone", "safe_zones": [{"anchor": "top_left", "rect_norm": [0.04, 0.04, 0.30, 0.18]}]},
            },
        })
    return {
        "record_type": "ComicPanelPlanCollection",
        "schema_version": "2.0",
        "record_id": "synthetic-comic-full-chapter-r1",
        "state": "AUTHORING_COMPLETE_NOT_PROMOTED_SYNTHETIC",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "chapter_title": "Synthetic validator fixture",
        "chapter_logline": "Two fictional adults traverse an abstract test route; this is not North Garden canon.",
        "story_state_id": "synthetic-story-state-r1",
        "opening_state": "fictional adults at test route origin",
        "closing_changed_state": "fictional adults reach a distinct test route destination",
        "declared_target_panel_count": 6,
        "fictional_adult_roles": ["ADULT_A", "ADULT_B"],
        "continuity_contract": {"initial_state": copy.deepcopy(shared_state), "final_state": copy.deepcopy(shared_state)},
        "progression_contract": {key: None for key in PROGRESSION_PREFIXES},
        "narrative_phases": [{"phase_id": phase, "narrative_function": function} for phase, function in zip(phases, functions)],
        "sequences": [
            {"sequence_id": "synthetic-seq01", "narrative_order": 1, "title": "Synthetic opening", "narrative_functions": functions[:3], "panel_ids": [row["panel_id"] for row in plans[:3]], "continuity_entry": copy.deepcopy(shared_state), "continuity_exit": copy.deepcopy(shared_state)},
            {"sequence_id": "synthetic-seq02", "narrative_order": 2, "title": "Synthetic consequence", "narrative_functions": functions[3:], "panel_ids": [row["panel_id"] for row in plans[3:]], "continuity_entry": copy.deepcopy(shared_state), "continuity_exit": copy.deepcopy(shared_state)},
        ],
        "plans": plans,
        "promotion_decision": None,
        "execution_ready": False,
        "authoring_complete": True,
    }


def walk_forbidden(value: Any, location: str = "root") -> list[str]:
    errors = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_KEYS:
                errors.append(f"forbidden pre-promotion field {location}.{key}")
            errors.extend(walk_forbidden(child, f"{location}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(walk_forbidden(child, f"{location}[{index}]"))
    return errors


def valid_state(value: Any) -> bool:
    return isinstance(value, dict) and set(value) == set(CONTINUITY_CATEGORIES) and all(isinstance(value[key], list) for key in CONTINUITY_CATEGORIES)


def validate(document: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors = walk_forbidden(document)
    check = lambda condition, message: None if condition else errors.append(message)
    check(document.get("record_type") == "ComicPanelPlanCollection", "record_type")
    check(document.get("medium") == "comic" and document.get("planning_structure") == "ComicPanelPlan", "medium/planning")
    check(document.get("animation_shot_plan") is None and document.get("e_conte") is None, "cross-medium fields")
    check(document.get("execution_ready") is False and document.get("promotion_decision") is None, "pre-promotion state")
    check(isinstance(document.get("opening_state"), str) and bool(document["opening_state"]), "opening state")
    check(isinstance(document.get("closing_changed_state"), str) and document.get("closing_changed_state") != document.get("opening_state"), "closing changed state")
    plans = document.get("plans", [])
    check(isinstance(plans, list) and bool(plans), "plans")
    check(document.get("declared_target_panel_count") == len(plans), "declared panel count")
    required_fields = set(contract["panel_required_fields"])
    if not isinstance(plans, list):
        plans = []
    check(all(required_fields <= set(row) for row in plans if isinstance(row, dict)), "panel required fields")
    panel_ids = [row.get("panel_id") for row in plans if isinstance(row, dict)]
    revisions = [row.get("plan_revision_id") for row in plans if isinstance(row, dict)]
    check(len(panel_ids) == len(set(panel_ids)) and None not in panel_ids, "unique panel ids")
    check(len(revisions) == len(set(revisions)) and None not in revisions, "unique plan revisions")
    check([row.get("display_order") for row in plans] == list(range(1, len(plans) + 1)), "contiguous display order")
    required_phases = {row["phase_id"] for row in contract["required_narrative_phases"]}
    declared_phases = {row.get("phase_id") for row in document.get("narrative_phases", [])}
    used_phases = {row.get("narrative_phase_id") for row in plans}
    check(declared_phases == required_phases and used_phases == required_phases, "six-phase coverage")
    expected_functions = {row["phase_id"]: row["narrative_function"] for row in contract["required_narrative_phases"]}
    actual_functions = {row.get("phase_id"): row.get("narrative_function") for row in document.get("narrative_phases", [])}
    check(actual_functions == expected_functions, "narrative phase functions")
    roles = set(document.get("fictional_adult_roles", []))
    check(bool(roles) and all(isinstance(role, str) and role.startswith("ADULT_") for role in roles), "fictional adult role declarations")
    check(all(isinstance(row.get("visible_adult_cast"), list) and set(row["visible_adult_cast"]) <= roles for row in plans), "visible adult cast")
    scale_roles = set(contract["scale_roles"])
    check(all(row.get("scale_role") in scale_roles for row in plans), "scale roles")
    check(any(str(row.get("scale_role", "")).startswith(("WIDE", "TALL")) for row in plans), "anchor scale present")
    check(any(str(row.get("scale_role", "")).startswith("SMALL") for row in plans), "small insert present")
    check({row.get("density_class") for row in plans} >= {"LOW", "HIGH"}, "density cadence")
    for row in plans:
        lettering = row.get("comic_direction", {}).get("lettering", {})
        zones = lettering.get("safe_zones", [])
        outside = lettering.get("placement_policy") in {"outside_art", "gutter_only"}
        check(bool(zones) or outside, f"lettering policy {row.get('panel_id')}")
        for zone in zones:
            rect = zone.get("rect_norm")
            valid = isinstance(rect, list) and len(rect) == 4 and all(isinstance(value, (int, float)) for value in rect)
            check(valid and 0 <= rect[0] < rect[2] <= 1 and 0 <= rect[1] < rect[3] <= 1, f"lettering zone {row.get('panel_id')}")
        check(valid_state(row.get("continuity_carry_in")) and valid_state(row.get("continuity_carry_out")), f"continuity shape {row.get('panel_id')}")
    continuity = document.get("continuity_contract", {})
    check(valid_state(continuity.get("initial_state")) and valid_state(continuity.get("final_state")), "chapter continuity shape")
    if plans and valid_state(continuity.get("initial_state")):
        check(plans[0].get("continuity_carry_in") == continuity["initial_state"], "opening continuity")
    if plans and valid_state(continuity.get("final_state")):
        check(plans[-1].get("continuity_carry_out") == continuity["final_state"], "closing continuity")
    for left, right in zip(plans, plans[1:]):
        check(left.get("continuity_carry_out") == right.get("continuity_carry_in"), f"continuity edge {left.get('panel_id')}->{right.get('panel_id')}")
    sequences = document.get("sequences", [])
    check([row.get("narrative_order") for row in sequences] == list(range(1, len(sequences) + 1)), "sequence order")
    flattened = []
    for sequence in sequences:
        ids = sequence.get("panel_ids", [])
        check(3 <= len(ids) <= 5, f"sequence size {sequence.get('sequence_id')}")
        flattened.extend(ids)
        positions = [panel_ids.index(panel_id) for panel_id in ids if panel_id in panel_ids]
        check(len(positions) == len(ids) and positions == list(range(min(positions), max(positions) + 1)) if positions else False, f"sequence contiguity {sequence.get('sequence_id')}")
        first = next((row for row in plans if row.get("panel_id") == ids[0]), None) if ids else None
        last = next((row for row in plans if row.get("panel_id") == ids[-1]), None) if ids else None
        check(first is not None and sequence.get("continuity_entry") == first.get("continuity_carry_in"), f"sequence entry {sequence.get('sequence_id')}")
        check(last is not None and sequence.get("continuity_exit") == last.get("continuity_carry_out"), f"sequence exit {sequence.get('sequence_id')}")
        check(all(row.get("sequence_id") == sequence.get("sequence_id") for row in plans if row.get("panel_id") in ids), f"panel sequence ids {sequence.get('sequence_id')}")
    check(flattened == panel_ids, "sequence exact coverage")
    progression = document.get("progression_contract", {})
    check(set(progression) == set(PROGRESSION_PREFIXES), "progression categories")
    all_assets = {asset for row in plans for asset in row.get("asset_ids", [])}
    for category, prefix in PROGRESSION_PREFIXES.items():
        matching = {asset for asset in all_assets if isinstance(asset, str) and asset.startswith(prefix)}
        declaration = progression.get(category)
        if matching:
            check(isinstance(declaration, dict) and declaration.get("canon_decision") and set(declaration.get("asset_ids", [])) >= matching, f"progression binding {category}")
        if declaration is not None:
            check(isinstance(declaration, dict) and isinstance(declaration.get("canon_decision"), str) and bool(declaration.get("asset_ids")), f"progression declaration {category}")
    return errors


def mutations() -> list[tuple[str, Callable[[dict[str, Any]], None]]]:
    return [
        ("cross_medium", lambda d: d.__setitem__("animation_shot_plan", {})),
        ("execution", lambda d: d.__setitem__("execution_ready", True)),
        ("prompt_leak", lambda d: d["plans"][0].__setitem__("prompt", "forbidden")),
        ("provider_leak", lambda d: d.__setitem__("model", "forbidden")),
        ("same_closing", lambda d: d.__setitem__("closing_changed_state", d["opening_state"])),
        ("count", lambda d: d.__setitem__("declared_target_panel_count", 5)),
        ("duplicate_panel", lambda d: d["plans"][1].__setitem__("panel_id", d["plans"][0]["panel_id"])),
        ("display_gap", lambda d: d["plans"][2].__setitem__("display_order", 9)),
        ("phase_missing", lambda d: d["plans"][5].__setitem__("narrative_phase_id", "phase05")),
        ("phase_function", lambda d: d["narrative_phases"][0].__setitem__("narrative_function", "beauty_shot")),
        ("undeclared_role", lambda d: d["plans"][0]["visible_adult_cast"].append("ADULT_C")),
        ("child_role", lambda d: d["fictional_adult_roles"].append("CHILD_A")),
        ("scale", lambda d: d["plans"][0].__setitem__("scale_role", "BEAUTY_SHOT")),
        ("density", lambda d: [row.__setitem__("density_class", "MEDIUM") for row in d["plans"]]),
        ("lettering_absent", lambda d: d["plans"][0]["comic_direction"].__setitem__("lettering", {})),
        ("lettering_bounds", lambda d: d["plans"][0]["comic_direction"]["lettering"]["safe_zones"][0].__setitem__("rect_norm", [0.9, 0.1, 1.2, 0.3])),
        ("continuity_edge", lambda d: d["plans"][2]["continuity_carry_out"]["props"].append("new_prop")),
        ("sequence_size", lambda d: d["sequences"][0].__setitem__("panel_ids", d["sequences"][0]["panel_ids"][:2])),
        ("sequence_order", lambda d: d["sequences"][1].__setitem__("narrative_order", 1)),
        ("sequence_overlap", lambda d: d["sequences"][1]["panel_ids"].__setitem__(0, d["sequences"][0]["panel_ids"][-1])),
        ("sequence_id_mismatch", lambda d: d["plans"][0].__setitem__("sequence_id", "synthetic-seq02")),
        ("progression_leak", lambda d: d["plans"][0]["asset_ids"].append("ng-progression-weapon-synthetic-sword")),
        ("progression_weak", lambda d: d["progression_contract"].__setitem__("monsters", {"canon_decision": "", "asset_ids": []})),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    fixture = semantic_fixture()
    errors = validate(fixture, contract)
    caught = total = 0
    categories = []
    if args.self_test or args.emit:
        tests = mutations()
        total = len(tests)
        for name, mutation in tests:
            candidate = copy.deepcopy(fixture)
            mutation(candidate)
            if validate(candidate, contract):
                caught += 1
                categories.append(name)
        if caught != total:
            errors.append(f"adversarial {caught}/{total}")
    if args.emit:
        evidence = {
            "record_type": "CompleteChapterSemanticGraphValidatorEvidence",
            "schema_version": "1.0",
            "record_id": "ng-complete-chapter-semantic-graph-validator-r1",
            "state": "SYNTHETIC_VALIDATION_ONLY_NO_CANON_CREATED",
            "planning_structure": "ComicPanelPlan",
            "animation_shot_plan": None,
            "e_conte": None,
            "contract": {"path": CONTRACT.relative_to(ROOT).as_posix(), "sha256": sha256(CONTRACT)},
            "synthetic_positive_fixture": {"sha256": canonical_hash(fixture), "panel_count": 6, "sequence_count": 2, "phase_count": 6, "north_garden_canon": False, "validation_errors": validate(fixture, contract)},
            "adversarial": {"total": total, "rejected": caught, "categories": categories},
            "checks": ["planning_boundary", "pre_promotion_forbidden_fields", "opening_closing_change", "panel_identity_and_order", "six_phase_coverage", "fictional_adult_roles", "scale_and_density_cadence", "lettering_safe_zones", "panel_continuity_edges", "sequence_order_contiguity_and_coverage", "progression_canon_binding"],
            "boundary": {"north_garden_story_beats_created": 0, "north_garden_panel_plans_created": 0, "prompts_created": 0, "provider_calls": 0, "uploads": 0, "generated_candidates": 0, "acceptance_or_rights_decisions": 0},
        }
        EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "positive": "1/1" if not validate(fixture, contract) else "0/1", "adversarial": f"{caught}/{total}" if total else None, "emitted": args.emit}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
