"""Validate the breadth-first North Garden CH06-CH13 progression arc."""

from __future__ import annotations

import argparse
import copy
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "production/canon/story-arcs/north-garden-ch06-ch13-progression-r1.json"
EXPECTED_CHAPTERS = [f"CH{number:02d}" for number in range(6, 14)]
STATE_DELTA_CATEGORIES = {
    "goal",
    "relationship",
    "ally",
    "world_knowledge",
    "system",
    "equipment",
    "wardrobe",
    "capability",
    "weapons",
    "monster_knowledge",
    "consequence",
    "armor",
    "injury",
    "class",
    "threat",
    "faction",
    "party",
    "leadership",
    "home",
}


def errors(data: dict[str, Any]) -> list[str]:
    found: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            found.append(message)

    check(data.get("record_type") == "MultiChapterComicProgressionArc", "record type")
    check(data.get("state") == "PROVISIONAL_CANON_DEVELOPMENT_AUTHORED_NOT_RENDER_PROMOTED", "state")
    check(data.get("planning_structure") == "ComicPanelPlan", "planning structure")
    check(data.get("animation_shot_plan") is None, "AnimationShotPlan boundary")
    check(data.get("e_conte") is None, "E-Conte boundary")
    chapters = data.get("chapters", [])
    check([chapter.get("chapter_id") for chapter in chapters] == EXPECTED_CHAPTERS, "chapter order/coverage")
    check(len({chapter.get("title") for chapter in chapters}) == 8, "unique chapter titles")
    target = data.get("production_target", {})
    check(target.get("required_complete_chapters") == 8, "required chapter count")
    check(target.get("target_panels_per_chapter") == 40, "panels per chapter")
    check(target.get("target_sequences_per_chapter") == 8, "sequences per chapter")
    check(target.get("target_total_panels") == 320, "total panel target")
    check(target.get("narrative_phases_required_per_chapter") == 6, "phase target")
    for index, chapter in enumerate(chapters):
        prefix = chapter.get("chapter_id", f"index-{index}")
        check(bool(chapter.get("logline")), f"{prefix} logline")
        check(bool(chapter.get("chapter_question")), f"{prefix} chapter question")
        check(chapter.get("opening_state_key") != chapter.get("closing_state_key"), f"{prefix} changed state")
        check(len(chapter.get("causal_setpieces", [])) >= 2, f"{prefix} causal setpieces")
        delta = chapter.get("state_delta", {})
        check(len(delta) >= 5, f"{prefix} material delta count")
        check(set(delta).issubset(STATE_DELTA_CATEGORIES), f"{prefix} state delta vocabulary")
        check(all(isinstance(value, str) and value.strip() for value in delta.values()), f"{prefix} state delta values")
        check(bool(chapter.get("primary_location")), f"{prefix} primary location")
        check(bool(chapter.get("closing_hook")), f"{prefix} closing hook")
        if index:
            check(
                chapter.get("opening_state_key") == chapters[index - 1].get("closing_state_key"),
                f"{prefix} cross-chapter carry",
            )
    anti_duplication = data.get("anti_duplication_contract", {})
    check(anti_duplication.get("complete_story_before_alternate_style") is True, "story-before-style gate")
    check(anti_duplication.get("maximum_default_render_candidates_per_panel") == 1, "default candidate cap")
    check(anti_duplication.get("maximum_targeted_repairs_per_failed_panel") == 2, "repair cap")
    check(anti_duplication.get("maximum_alternate_style_share_after_complete_chapter") == 0.10, "alternate share cap")
    check(anti_duplication.get("alternate_route_requires_named_chapter_level_question") is True, "alternate question gate")
    check(anti_duplication.get("style_only_change_does_not_count_as_chapter_progress") is True, "style progress exclusion")
    identity = data.get("identity_contract", {})
    check(set(identity) == {"SOREN", "SIGRID"}, "identity cast")
    check("never black" in identity.get("SOREN", {}).get("hair", ""), "Soren hair control")
    check("never blond" in identity.get("SIGRID", {}).get("hair", ""), "Sigrid hair control")
    additions = data.get("fictional_adult_cast_additions", {})
    check(set(additions) == {"TAMSIN_REEVE", "HALVOR_KEST"}, "adult cast additions")
    check(all("fictional adult" in value for value in additions.values()), "adult cast declarations")
    authority = data.get("authority_boundary", {})
    check(authority.get("story_authoring_only") is True, "story-only authority")
    for key in (
        "render_prompts_created",
        "provider_calls",
        "uploads",
        "generated_candidates",
        "accepted_candidates",
        "commercial_decisions",
        "exact_base_decisions",
    ):
        check(authority.get(key) == 0, f"authority zero {key}")
    milestones = data.get("milestones", [])
    check(len(milestones) == 4, "milestone count")
    check(
        [chapter for milestone in milestones for chapter in milestone.get("chapters", [])] == EXPECTED_CHAPTERS,
        "milestone chapter coverage",
    )
    check([chapter.get("chapter_id") for chapter in data.get("stretch_outline", [])] == ["CH14", "CH15", "CH16", "CH17"], "stretch order")
    return found


def self_test(data: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.update(record_type="Wrong"),
        lambda value: value.update(state="RENDER_READY"),
        lambda value: value.update(planning_structure="AnimationShotPlan"),
        lambda value: value.update(animation_shot_plan={}),
        lambda value: value.update(e_conte={}),
        lambda value: value["chapters"].pop(),
        lambda value: value["chapters"][1].update(opening_state_key="BROKEN_CARRY"),
        lambda value: value["chapters"][2].update(closing_state_key=value["chapters"][2]["opening_state_key"]),
        lambda value: value["chapters"][3].update(causal_setpieces=[]),
        lambda value: value["chapters"][4].update(state_delta={"goal": "only one"}),
        lambda value: value["production_target"].update(target_total_panels=319),
        lambda value: value["anti_duplication_contract"].update(complete_story_before_alternate_style=False),
        lambda value: value["anti_duplication_contract"].update(maximum_default_render_candidates_per_panel=6),
        lambda value: value["anti_duplication_contract"].update(maximum_alternate_style_share_after_complete_chapter=1.0),
        lambda value: value["identity_contract"]["SOREN"].update(hair="black"),
        lambda value: value["identity_contract"]["SIGRID"].update(hair="blond"),
        lambda value: value["fictional_adult_cast_additions"].update(TAMSIN_REEVE="unspecified person"),
        lambda value: value["authority_boundary"].update(render_prompts_created=1),
        lambda value: value["authority_boundary"].update(provider_calls=1),
        lambda value: value["authority_boundary"].update(uploads=1),
        lambda value: value["authority_boundary"].update(accepted_candidates=1),
        lambda value: value["milestones"].pop(),
        lambda value: value["stretch_outline"].reverse(),
    ]
    rejected = 0
    for mutate in mutations:
        candidate = copy.deepcopy(data)
        mutate(candidate)
        rejected += bool(errors(candidate))
    return rejected, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    data = json.loads(RECORD.read_text(encoding="utf-8"))
    found = errors(data)
    result: dict[str, Any] = {
        "status": "PASS" if not found else "FAIL",
        "errors": found,
        "chapters": len(data.get("chapters", [])),
        "target_panels": data.get("production_target", {}).get("target_total_panels"),
    }
    if args.self_test:
        rejected, total = self_test(data)
        result["self_test"] = f"{rejected}/{total}"
        if rejected != total:
            found.append(f"only {rejected}/{total} mutations rejected")
            result["status"] = "FAIL"
    print(json.dumps(result, sort_keys=True))
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
