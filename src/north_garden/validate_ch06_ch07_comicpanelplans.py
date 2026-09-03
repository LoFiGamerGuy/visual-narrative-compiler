"""Validate the complete CH06 and CH07 ComicPanelPlan authoring graphs."""

from __future__ import annotations

import argparse
import copy
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from validate_complete_chapter_semantic_graph import validate as validate_semantic_graph

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "production/comic/contracts/complete-chapter-comicpanelplan-authoring-contract-r1.json"
ARC = ROOT / "production/canon/story-arcs/north-garden-ch06-ch13-progression-r1.json"
PLANS = {
    "CH06": ROOT / "production/comic/ch06-sc01-panel-plans-r1.json",
    "CH07": ROOT / "production/comic/ch07-sc01-panel-plans-r1.json",
}
STORIES = {
    "CH06": ROOT / "production/canon/story-state/ch06-sc01-r1.json",
    "CH07": ROOT / "production/canon/story-state/ch07-sc01-r1.json",
}
BEATS = {
    "CH06": ROOT / "production/scene-beats/ch06-sc01-house-answered-r1.json",
    "CH07": ROOT / "production/scene-beats/ch07-sc01-mireback-gate-r1.json",
}


def validate_batch(documents: dict[str, dict[str, Any]]) -> list[str]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    arc = json.loads(ARC.read_text(encoding="utf-8"))
    arc_chapters = {chapter["chapter_id"]: chapter for chapter in arc["chapters"]}
    found: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            found.append(message)

    for chapter_id, document in documents.items():
        for message in validate_semantic_graph(document, contract):
            found.append(f"{chapter_id}: {message}")
        arc_chapter = arc_chapters[chapter_id]
        check(document.get("declared_target_panel_count") == 40, f"{chapter_id}: 40 panels")
        check(len(document.get("sequences", [])) == 8, f"{chapter_id}: eight sequences")
        check(all(len(sequence.get("panel_ids", [])) == 5 for sequence in document.get("sequences", [])), f"{chapter_id}: five-panel sequences")
        check(document.get("opening_state") == arc_chapter["opening_state_key"], f"{chapter_id}: arc opening")
        check(document.get("closing_changed_state") == arc_chapter["closing_state_key"], f"{chapter_id}: arc closing")
        check(document.get("anti_duplication", {}).get("default_candidates_per_panel") == 1, f"{chapter_id}: candidate cap")
        check(document.get("anti_duplication", {}).get("alternate_style_before_complete_chapter") is False, f"{chapter_id}: alternate gate")
        check(document.get("anti_duplication", {}).get("targeted_repair_cap_per_failed_panel") == 2, f"{chapter_id}: repair cap")
        beats = [panel.get("narrative_beat", "") for panel in document.get("plans", [])]
        check(len(set(beats)) == 40 and all(len(value) >= 30 for value in beats), f"{chapter_id}: substantive unique beats")
        check(all("child" not in json.dumps(panel).lower() for panel in document.get("plans", [])), f"{chapter_id}: no child-coded material")
        check(all(panel.get("comic_direction", {}).get("lettering", {}).get("protected_subjects") for panel in document.get("plans", [])), f"{chapter_id}: protected lettering subjects")
        story = json.loads(STORIES[chapter_id].read_text(encoding="utf-8"))
        scene = json.loads(BEATS[chapter_id].read_text(encoding="utf-8"))
        check(story.get("opening_state") == document.get("opening_state"), f"{chapter_id}: story opening binding")
        check(story.get("closing_changed_state") == document.get("closing_changed_state"), f"{chapter_id}: story closing binding")
        check(story.get("continuity_final_state") == document.get("continuity_contract", {}).get("final_state"), f"{chapter_id}: story continuity binding")
        check(scene.get("story_state_id") == document.get("story_state_id"), f"{chapter_id}: scene/story binding")
        check(len(scene.get("causal_setpieces", [])) >= 2, f"{chapter_id}: causal setpiece binding")
        check(story.get("promotion_decision") is None, f"{chapter_id}: story not promoted")
    ch06 = documents["CH06"]
    ch07 = documents["CH07"]
    check(ch06.get("closing_changed_state") == ch07.get("opening_state"), "CH06-to-CH07 state carry")
    check(ch06.get("continuity_contract", {}).get("final_state") == ch07.get("continuity_contract", {}).get("initial_state"), "CH06-to-CH07 continuity carry")
    check(sum(len(document.get("plans", [])) for document in documents.values()) == 80, "batch panel total")
    check(sum(len(document.get("sequences", [])) for document in documents.values()) == 16, "batch sequence total")
    return found


def load_documents() -> dict[str, dict[str, Any]]:
    return {chapter_id: json.loads(path.read_text(encoding="utf-8")) for chapter_id, path in PLANS.items()}


def self_test(documents: dict[str, dict[str, Any]]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, dict[str, Any]]], None]] = [
        lambda value: value["CH06"].update(planning_structure="AnimationShotPlan"),
        lambda value: value["CH06"].update(animation_shot_plan={}),
        lambda value: value["CH07"].update(e_conte={}),
        lambda value: value["CH06"].update(execution_ready=True),
        lambda value: value["CH06"].update(declared_target_panel_count=39),
        lambda value: value["CH07"]["plans"].pop(),
        lambda value: value["CH06"]["plans"][1].update(panel_id=value["CH06"]["plans"][0]["panel_id"]),
        lambda value: value["CH07"]["plans"][5].update(display_order=99),
        lambda value: value["CH06"]["plans"][0].update(visible_adult_cast=["CHILD_A"]),
        lambda value: value["CH07"]["plans"][10].update(asset_ids=["child-coded-asset"]),
        lambda value: value["CH06"]["plans"][0]["comic_direction"].update(lettering={}),
        lambda value: value["CH07"]["plans"][0]["comic_direction"]["lettering"].update(protected_subjects=[]),
        lambda value: value["CH06"]["plans"][3]["continuity_carry_out"]["clues"].append("broken"),
        lambda value: value["CH07"]["continuity_contract"].update(initial_state={}),
        lambda value: value["CH07"].update(opening_state="BROKEN"),
        lambda value: value["CH06"].update(closing_changed_state="BROKEN"),
        lambda value: value["CH06"]["sequences"].pop(),
        lambda value: value["CH07"]["sequences"][0].update(panel_ids=value["CH07"]["sequences"][0]["panel_ids"][:4]),
        lambda value: value["CH06"]["anti_duplication"].update(default_candidates_per_panel=6),
        lambda value: value["CH07"]["anti_duplication"].update(alternate_style_before_complete_chapter=True),
        lambda value: value["CH06"]["anti_duplication"].update(targeted_repair_cap_per_failed_panel=99),
        lambda value: value["CH07"]["plans"][0].update(narrative_beat="short"),
        lambda value: value["CH06"]["plans"][1].update(narrative_beat=value["CH06"]["plans"][0]["narrative_beat"]),
        lambda value: value["CH07"]["plans"][0].update(prompt="forbidden"),
        lambda value: value["CH06"].update(model="forbidden"),
    ]
    rejected = 0
    for mutation in mutations:
        candidate = copy.deepcopy(documents)
        mutation(candidate)
        rejected += bool(validate_batch(candidate))
    return rejected, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    documents = load_documents()
    found = validate_batch(documents)
    result: dict[str, Any] = {
        "status": "PASS" if not found else "FAIL",
        "errors": found,
        "chapters": 2,
        "panels": sum(len(document.get("plans", [])) for document in documents.values()),
        "sequences": sum(len(document.get("sequences", [])) for document in documents.values()),
    }
    if args.self_test:
        rejected, total = self_test(documents)
        result["self_test"] = f"{rejected}/{total}"
        if rejected != total:
            found.append(f"only {rejected}/{total} mutations rejected")
            result["status"] = "FAIL"
    print(json.dumps(result, sort_keys=True))
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
