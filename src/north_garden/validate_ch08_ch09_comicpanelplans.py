"""Validate CH08-CH09 ComicPanelPlans and their exact cross-chapter carry."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from compile_ch08_ch09_comicpanelplans import (
    ADR_OUTPUT,
    ARC_PATH,
    BEAT_OUTPUTS,
    CH07_PATH,
    MARKDOWN_OUTPUT,
    OUTPUTS,
    STORY_OUTPUTS,
    adr_markdown,
    authoring_markdown,
    build_chapter,
    scene_beat,
    story_state,
    verify_sources,
)
from validate_complete_chapter_semantic_graph import validate as validate_semantic_graph

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "production/comic/contracts/complete-chapter-comicpanelplan-authoring-contract-r1.json"
FORBIDDEN_KEYS = {"prompt", "output", "provider", "service", "model", "endpoint", "request_id", "provider_usage", "cost_usd", "monetary_cost_usd", "seed", "input_references", "rendered_candidate", "render_record"}
HAIR_ANCHORS = {
    "SOREN": ("light-brown to dark-blond", "swept-back", "never black or bright blond"),
    "SIGRID": ("dark-brown to near-black", "compact low bun or practical braid", "never blond or loose red curls"),
}
PHYSICAL_SUBSTRATES = ("physical", "brass", "stone", "wire", "water", "condensation", "wet", "capstone", "surface")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def walk_keys(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_KEYS:
                found.append(key)
            found.extend(walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(walk_keys(child))
    return found


def expected_package() -> dict[str, Any]:
    verify_sources()
    arc = json.loads(ARC_PATH.read_text(encoding="utf-8"))
    source = {row["chapter_id"]: row for row in arc["chapters"]}
    ch07 = json.loads(CH07_PATH.read_text(encoding="utf-8"))
    plans: dict[str, dict[str, Any]] = {}
    plans["CH08"] = build_chapter("CH08", source["CH08"], ch07["continuity_contract"]["final_state"])
    plans["CH09"] = build_chapter("CH09", source["CH09"], plans["CH08"]["continuity_contract"]["final_state"])
    stories = {chapter_id: story_state(chapter_id, source[chapter_id], plans[chapter_id]) for chapter_id in plans}
    beats = {chapter_id: scene_beat(chapter_id, source[chapter_id]) for chapter_id in plans}
    return {"plans": plans, "stories": stories, "beats": beats, "markdown": authoring_markdown(plans), "adr": adr_markdown()}


def load_package() -> dict[str, Any]:
    return {
        "plans": {chapter_id: json.loads(path.read_text(encoding="utf-8")) for chapter_id, path in OUTPUTS.items()},
        "stories": {chapter_id: json.loads(path.read_text(encoding="utf-8")) for chapter_id, path in STORY_OUTPUTS.items()},
        "beats": {chapter_id: json.loads(path.read_text(encoding="utf-8")) for chapter_id, path in BEAT_OUTPUTS.items()},
        "markdown": MARKDOWN_OUTPUT.read_text(encoding="utf-8"),
        "adr": ADR_OUTPUT.read_text(encoding="utf-8"),
    }


def validate_batch(package: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    arc = json.loads(ARC_PATH.read_text(encoding="utf-8"))
    arc_chapters = {row["chapter_id"]: row for row in arc["chapters"]}
    plans = package.get("plans", {})
    stories = package.get("stories", {})
    beats = package.get("beats", {})
    check(set(plans) == {"CH08", "CH09"}, "chapter plan set")
    check(set(stories) == {"CH08", "CH09"}, "story state set")
    check(set(beats) == {"CH08", "CH09"}, "scene beat set")
    if not all(chapter_id in plans and chapter_id in stories and chapter_id in beats for chapter_id in ("CH08", "CH09")):
        return errors

    for chapter_id in ("CH08", "CH09"):
        document = plans[chapter_id]
        for message in validate_semantic_graph(document, contract):
            errors.append(f"{chapter_id}: {message}")
        arc_chapter = arc_chapters[chapter_id]
        rows = document.get("plans", [])
        sequences = document.get("sequences", [])
        check(document.get("declared_target_panel_count") == 40 and len(rows) == 40, f"{chapter_id}: forty plans")
        check(len(sequences) == 8 and all(len(row.get("panel_ids", [])) == 5 for row in sequences), f"{chapter_id}: eight five-panel sequences")
        check([row.get("display_order") for row in rows] == list(range(1, 41)), f"{chapter_id}: chronological order")
        check(len({row.get("narrative_beat") for row in rows}) == 40 and all(len(row.get("narrative_beat", "")) >= 40 for row in rows), f"{chapter_id}: unique substantive beats")
        check(document.get("opening_state") == arc_chapter["opening_state_key"], f"{chapter_id}: arc opening")
        check(document.get("closing_changed_state") == arc_chapter["closing_state_key"], f"{chapter_id}: arc closing")
        check(len(arc_chapter.get("state_delta", {})) >= 5, f"{chapter_id}: drastic arc delta")
        changed_categories = sum(document["continuity_contract"]["initial_state"][key] != document["continuity_contract"]["final_state"][key] for key in document["continuity_contract"]["initial_state"])
        check(changed_categories >= 5, f"{chapter_id}: material continuity delta")
        check(document.get("planning_structure") == "ComicPanelPlan" and document.get("animation_shot_plan") is None and document.get("e_conte") is None, f"{chapter_id}: comic-only boundary")
        check(document.get("execution_ready") is False and document.get("promotion_decision") is None, f"{chapter_id}: not promoted")
        check(not walk_keys(document) and not walk_keys(stories[chapter_id]) and not walk_keys(beats[chapter_id]), f"{chapter_id}: forbidden execution fields")
        check(all(role.startswith("ADULT_") for role in document.get("fictional_adult_roles", [])), f"{chapter_id}: adult roles")
        check("child" not in json.dumps({"plan": document, "story": stories[chapter_id], "beat": beats[chapter_id]}).lower(), f"{chapter_id}: child-coded content")
        identity = document.get("identity_contract", {})
        for role, anchors in HAIR_ANCHORS.items():
            check(all(anchor in identity.get(role, "") for anchor in anchors), f"{chapter_id}: {role} fixed hair anchors")
        check("oatmeal" in identity.get("SOREN", "") and "quilted" in identity.get("SOREN", ""), f"{chapter_id}: Soren evolved gear anchor")
        check("plaid" in identity.get("SIGRID", "") and "weather cape" in identity.get("SIGRID", ""), f"{chapter_id}: Sigrid evolved gear anchor")
        protected = ["faces", "adult silhouettes", "important hands", "weapons and tools", "story objects", "physical Garden Ledger surfaces"]
        check(all(row.get("comic_direction", {}).get("lettering", {}).get("protected_subjects") == protected for row in rows), f"{chapter_id}: protected lettering")
        check(all(row.get("comic_direction", {}).get("lettering", {}).get("placement_policy") in {"safe_zone", "outside_art", "gutter_only"} for row in rows), f"{chapter_id}: lettering placement")
        ledger_panels = [row for row in rows if any(str(asset).startswith("ng-progression-ui-") for asset in row.get("asset_ids", []))]
        check(bool(ledger_panels), f"{chapter_id}: physical Ledger panels")
        for row in ledger_panels:
            language = (row.get("narrative_beat", "") + " " + row.get("composition_intent", "")).lower()
            check(any(term in language for term in PHYSICAL_SUBSTRATES), f"{chapter_id}: physical Ledger substrate {row.get('panel_id')}")
            check("generic floating hud" not in language and "persistent floating hud" not in language and "as a floating hud" not in language, f"{chapter_id}: no floating HUD {row.get('panel_id')}")
        progression = document.get("progression_contract", {})
        check(progression.get("armor") and progression.get("weapons") and progression.get("upgraded_clothing") and progression.get("system_ui"), f"{chapter_id}: practical progression bindings")
        story = stories[chapter_id]
        scene = beats[chapter_id]
        check(story.get("opening_state") == document.get("opening_state"), f"{chapter_id}: story opening binding")
        check(story.get("closing_changed_state") == document.get("closing_changed_state"), f"{chapter_id}: story closing binding")
        check(story.get("continuity_final_state") == document.get("continuity_contract", {}).get("final_state"), f"{chapter_id}: story final binding")
        check(story.get("promotion_decision") is None, f"{chapter_id}: story promotion null")
        check(scene.get("story_state_id") == document.get("story_state_id"), f"{chapter_id}: scene/story binding")
        check(scene.get("causal_setpieces") == arc_chapter.get("causal_setpieces"), f"{chapter_id}: causal setpieces")
        check(scene.get("closing_hook") == arc_chapter.get("closing_hook"), f"{chapter_id}: closing hook")

    ch07 = json.loads(CH07_PATH.read_text(encoding="utf-8"))
    ch08, ch09 = plans["CH08"], plans["CH09"]
    check(ch08["continuity_contract"]["initial_state"] == ch07["continuity_contract"]["final_state"], "exact CH07-to-CH08 continuity")
    check(ch09["continuity_contract"]["initial_state"] == ch08["continuity_contract"]["final_state"], "exact CH08-to-CH09 continuity")
    check(ch08.get("closing_changed_state") == ch09.get("opening_state"), "CH08-to-CH09 state key")
    check("hollow_stag_spared" in ch08["continuity_contract"]["final_state"]["clues"], "CH08 Hollow Stag spared")
    check("ledger_marks_ecological_route_role" in ch08["continuity_contract"]["final_state"]["clues"], "CH08 ecological role learned")
    check((ch08["progression_contract"].get("monsters") or {}).get("asset_ids") == ["ng-progression-monster-hollow-stag-r1"], "CH08 Hollow Stag binding")
    check(ch08["progression_contract"].get("classes") is None, "CH08 class remains null")
    ch09_final = ch09["continuity_contract"]["final_state"]
    check("soren_left_lower_leg_crush_sprain_braced" in ch09_final["injuries"], "CH09 persistent Soren injury")
    check("damaged_system_recognized_wardens_reach" in ch09_final["props"], "CH09 damaged Warden's Reach")
    check("sigrid_wayfinder_path_earned_by_navigation_and_rescue" in ch09_final["clues"], "CH09 earned Wayfinder")
    check("human_sabotage_enters_node_failures" in ch09_final["clues"] and "brackenwake_seal_on_false_map_plate" in ch09_final["clues"], "CH09 sabotage evidence")
    check((ch09["progression_contract"].get("classes") or {}).get("asset_ids") == ["ng-progression-class-sigrid-wayfinder-r1"], "CH09 class binding")
    check(sum(len(document["plans"]) for document in plans.values()) == 80, "batch panel total")
    check(sum(len(document["sequences"]) for document in plans.values()) == 16, "batch sequence total")

    markdown = package.get("markdown", "")
    adr = package.get("adr", "")
    for token in ("80 unique chronological plans", "CH07→CH08→CH09", "physical-surface Wayfinder", "No prompt, provider call, upload, image"):
        check(token in markdown, f"authoring doc token: {token}")
    check("## Status" in adr and "Accepted for provisional canon-development authoring" in adr, "ADR accepted status")
    check("grants no provider, upload, paid API" in adr, "ADR authority boundary")
    return errors


def self_test(package: dict[str, Any]) -> tuple[int, int]:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("planning", lambda p: p["plans"]["CH08"].update(planning_structure="AnimationShotPlan")),
        ("animation", lambda p: p["plans"]["CH08"].update(animation_shot_plan={})),
        ("e_conte", lambda p: p["plans"]["CH09"].update(e_conte={})),
        ("execution", lambda p: p["plans"]["CH09"].update(execution_ready=True)),
        ("prompt", lambda p: p["plans"]["CH08"]["plans"][0].update(prompt="forbidden")),
        ("render_record", lambda p: p["stories"]["CH09"].update(render_record={})),
        ("panel_missing", lambda p: p["plans"]["CH08"]["plans"].pop()),
        ("panel_duplicate", lambda p: p["plans"]["CH09"]["plans"][1].update(panel_id=p["plans"]["CH09"]["plans"][0]["panel_id"])),
        ("display_order", lambda p: p["plans"]["CH08"]["plans"][2].update(display_order=99)),
        ("beat_duplicate", lambda p: p["plans"]["CH09"]["plans"][1].update(narrative_beat=p["plans"]["CH09"]["plans"][0]["narrative_beat"])),
        ("sequence_missing", lambda p: p["plans"]["CH08"]["sequences"].pop()),
        ("sequence_size", lambda p: p["plans"]["CH09"]["sequences"][0].update(panel_ids=p["plans"]["CH09"]["sequences"][0]["panel_ids"][:4])),
        ("chapter_opening", lambda p: p["plans"]["CH08"].update(opening_state="BROKEN")),
        ("chapter_closing", lambda p: p["plans"]["CH09"].update(closing_changed_state="BROKEN")),
        ("ch07_carry", lambda p: p["plans"]["CH08"]["continuity_contract"].update(initial_state={})),
        ("ch08_carry", lambda p: p["plans"]["CH09"]["continuity_contract"].update(initial_state={})),
        ("continuity_edge", lambda p: p["plans"]["CH08"]["plans"][5]["continuity_carry_out"]["props"].append("drift")),
        ("child", lambda p: p["plans"]["CH09"]["fictional_adult_roles"].append("CHILD_ROLE")),
        ("soren_hair", lambda p: p["plans"]["CH08"]["identity_contract"].update(SOREN="black hair")),
        ("sigrid_hair", lambda p: p["plans"]["CH09"]["identity_contract"].update(SIGRID="red curls")),
        ("lettering", lambda p: p["plans"]["CH08"]["plans"][0]["comic_direction"]["lettering"].update(protected_subjects=[])),
        ("safe_zone", lambda p: p["plans"]["CH09"]["plans"][0]["comic_direction"]["lettering"]["safe_zones"][0].update(rect_norm=[0.9, 0.1, 1.2, 0.3])),
        ("floating_ledger", lambda p: p["plans"]["CH08"]["plans"][8].update(narrative_beat="A generic floating HUD appears without any physical substrate.")),
        ("armor_binding", lambda p: p["plans"]["CH08"]["progression_contract"].update(armor=None)),
        ("stag_binding", lambda p: p["plans"]["CH08"]["progression_contract"].update(monsters=None)),
        ("stag_spared", lambda p: p["plans"]["CH08"]["continuity_contract"]["final_state"]["clues"].remove("hollow_stag_spared")),
        ("injury", lambda p: p["plans"]["CH09"]["continuity_contract"]["final_state"]["injuries"].remove("soren_left_lower_leg_crush_sprain_braced")),
        ("wayfinder", lambda p: p["plans"]["CH09"]["progression_contract"].update(classes=None)),
        ("sabotage", lambda p: p["plans"]["CH09"]["continuity_contract"]["final_state"]["clues"].remove("human_sabotage_enters_node_failures")),
        ("story_final", lambda p: p["stories"]["CH08"].update(continuity_final_state={})),
        ("story_promotion", lambda p: p["stories"]["CH09"].update(promotion_decision=True)),
        ("scene_setpieces", lambda p: p["beats"]["CH08"].update(causal_setpieces=[])),
        ("scene_hook", lambda p: p["beats"]["CH09"].update(closing_hook="changed")),
        ("authoring_doc", lambda p: p.update(markdown=p["markdown"].replace("80 unique chronological plans", "79 plans"))),
        ("adr_status", lambda p: p.update(adr=p["adr"].replace("Accepted for provisional canon-development authoring", "Proposed"))),
    ]
    caught = 0
    for name, mutation in mutations:
        candidate = copy.deepcopy(package)
        mutation(candidate)
        if validate_batch(candidate):
            caught += 1
        else:
            raise ValueError(f"mutation was not rejected: {name}")
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    package = load_package()
    expected = expected_package()
    errors = validate_batch(package)
    if package != expected:
        errors.append("compiled files are stale or nondeterministic")
    caught = total = 0
    if args.self_test:
        caught, total = self_test(package)
        if caught != total:
            errors.append(f"adversarial {caught}/{total}")
    result = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "chapters": 2,
        "panels": sum(len(row.get("plans", [])) for row in package["plans"].values()),
        "sequences": sum(len(row.get("sequences", [])) for row in package["plans"].values()),
        "ch07_to_ch08_state_sha256": canonical_hash(package["plans"]["CH08"]["continuity_contract"]["initial_state"]),
        "ch08_to_ch09_state_sha256": canonical_hash(package["plans"]["CH09"]["continuity_contract"]["initial_state"]),
        "adversarial": f"{caught}/{total}" if args.self_test else None,
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
