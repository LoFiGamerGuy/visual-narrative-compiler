"""Validate the reusable full-chapter ComicPanelPlan authoring contract/template."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "production/comic/contracts/complete-chapter-comicpanelplan-authoring-contract-r1.json"
TEMPLATE = ROOT / "production/comic/templates/complete-chapter-comicpanelplan-template-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(contract: dict[str, Any], template: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    check(contract.get("record_type") == "CompleteChapterComicPanelPlanAuthoringContract", "contract record_type")
    check(contract.get("state") == "REUSABLE_AUTHORING_CONTRACT_NON_EXECUTABLE", "contract state")
    check(contract.get("planning_structure") == "ComicPanelPlan", "contract planning")
    check(contract.get("animation_shot_plan") is None and contract.get("e_conte") is None, "contract cross-medium fields")
    check(len(contract.get("evidence_sources", [])) == 5, "evidence source count")
    baseline = contract.get("measured_baseline", {})
    check(baseline.get("panel_count") == 50 and baseline.get("sequence_count") == 12, "measured baseline")
    check(baseline.get("panels_per_sequence_min") == 3 and baseline.get("panels_per_sequence_max") == 5, "sequence range")
    check(baseline.get("agent_triage") == {"pass": 49, "warn": 1, "fail": 0, "gating": False}, "triage")
    phases = contract.get("required_narrative_phases", [])
    check(len(phases) == 6 and len({row.get("phase_id") for row in phases}) == 6, "narrative phases")
    check(all(row.get("minimum_panel_count") == 1 for row in phases), "phase coverage")
    check(len(contract.get("panel_required_fields", [])) == 18, "panel required fields")
    check(set(contract.get("cadence_classes", [])) == {"ANCHOR_OR_ACTION", "CHARACTER_OR_REACTION", "INSERT_OR_PAUSE"}, "cadence classes")
    check(len(contract.get("scale_roles", {})) == 9, "scale roles")
    check(len(contract.get("chapter_acceptance_gates", [])) == 9, "acceptance gates")
    boundary = contract.get("non_executable_boundary", {})
    check(len(boundary) == 8 and all(value == 0 for value in boundary.values()), "non-executable boundary")
    check(template.get("record_type") == "ComicPanelPlanAuthoringTemplate", "template record_type")
    check(template.get("state") == "EMPTY_TEMPLATE_NOT_A_COMICPANELPLAN_COLLECTION", "template state")
    check(template.get("planning_structure") == "ComicPanelPlan", "template planning")
    check(template.get("animation_shot_plan") is None and template.get("e_conte") is None, "template cross-medium fields")
    check(template.get("record_id") is None and template.get("story_state_id") is None, "template story identity")
    for key in ("chapter_title", "chapter_logline", "opening_state", "closing_changed_state", "declared_target_panel_count", "promotion_decision"):
        check(template.get(key) is None, f"template {key}")
    check(template.get("plans") == [] and template.get("sequences") == [], "template rows")
    check(template.get("execution_ready") is False and template.get("authoring_complete") is False, "template execution")
    check(len(template.get("narrative_phases", [])) == 6 and all(row.get("story_beats") == [] and row.get("completion_state") == "UNAUTHORED" for row in template["narrative_phases"]), "template phases")
    check(all(value is None for value in template.get("progression_contract", {}).values()), "template progression")
    if verify_files:
        for source in contract.get("evidence_sources", []):
            path = ROOT / source.get("path", "")
            check(path.is_file(), f"missing source {source.get('path')}")
            if path.is_file():
                check(sha256(path) == source.get("sha256"), f"source hash {source.get('path')}")
        check(template.get("contract") == {"path": CONTRACT.relative_to(ROOT).as_posix(), "sha256": sha256(CONTRACT)}, "template contract binding")
    return errors


def self_test(contract: dict[str, Any], template: dict[str, Any]) -> tuple[int, int]:
    mutations = [
        ("contract", lambda d: d.__setitem__("state", "EXECUTABLE")),
        ("contract", lambda d: d.__setitem__("planning_structure", "AnimationShotPlan")),
        ("contract", lambda d: d.__setitem__("animation_shot_plan", {})),
        ("contract", lambda d: d["measured_baseline"].__setitem__("panel_count", 49)),
        ("contract", lambda d: d["required_narrative_phases"].pop()),
        ("contract", lambda d: d["scale_roles"].pop(next(iter(d["scale_roles"])))),
        ("contract", lambda d: d["non_executable_boundary"].__setitem__("prompts_created", 1)),
        ("template", lambda d: d.__setitem__("record_type", "ComicPanelPlanCollection")),
        ("template", lambda d: d.__setitem__("record_id", "invented")),
        ("template", lambda d: d.__setitem__("story_state_id", "invented")),
        ("template", lambda d: d["plans"].append({})),
        ("template", lambda d: d["sequences"].append({})),
        ("template", lambda d: d.__setitem__("execution_ready", True)),
        ("template", lambda d: d["progression_contract"].__setitem__("weapons", "invented")),
        ("template", lambda d: d["narrative_phases"][0].__setitem__("completion_state", "COMPLETE")),
    ]
    caught = 0
    for target, mutation in mutations:
        candidate_contract, candidate_template = copy.deepcopy(contract), copy.deepcopy(template)
        mutation(candidate_contract if target == "contract" else candidate_template)
        caught += bool(validate(candidate_contract, candidate_template, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    errors = validate(contract, template)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(contract, template)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "phases": len(contract.get("required_narrative_phases", [])), "scale_roles": len(contract.get("scale_roles", {})), "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
