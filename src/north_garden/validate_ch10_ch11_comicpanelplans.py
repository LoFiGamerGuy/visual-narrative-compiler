"""Validate the CH10-CH11 faction-and-siege ComicPanelPlan batch."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Callable
from typing import Any

from compile_ch10_ch11_comicpanelplans import (
    ADR_OUTPUT,
    ARC_PATH,
    BEAT_OUTPUTS,
    CH09_PATH,
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

ROOT = ARC_PATH.parents[3]
CONTRACT = ROOT / "production/comic/contracts/complete-chapter-comicpanelplan-authoring-contract-r1.json"
FORBIDDEN_KEYS = {"prompt", "output", "provider", "service", "model", "endpoint", "request_id", "provider_usage", "cost_usd", "monetary_cost_usd", "seed", "input_references", "rendered_candidate", "render_record"}
PHYSICAL_SUBSTRATES = ("physical", "brass", "iron", "stone", "water", "condense", "wet", "anvil", "socket", "lintel", "tally", "tool")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def walk_forbidden(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_KEYS:
                found.append(key)
            found.extend(walk_forbidden(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(walk_forbidden(child))
    return found


def expected_package() -> dict[str, Any]:
    verify_sources()
    arc = json.loads(ARC_PATH.read_text(encoding="utf-8"))
    sources = {row["chapter_id"]: row for row in arc["chapters"]}
    ch09 = json.loads(CH09_PATH.read_text(encoding="utf-8"))
    plans: dict[str, dict[str, Any]] = {}
    plans["CH10"] = build_chapter("CH10", sources["CH10"], ch09["continuity_contract"]["final_state"])
    plans["CH11"] = build_chapter("CH11", sources["CH11"], plans["CH10"]["continuity_contract"]["final_state"])
    stories = {chapter: story_state(chapter, sources[chapter], plans[chapter]) for chapter in plans}
    beats = {chapter: scene_beat(chapter, sources[chapter]) for chapter in plans}
    return {"plans": plans, "stories": stories, "beats": beats, "markdown": authoring_markdown(plans), "adr": adr_markdown()}


def load_package() -> dict[str, Any]:
    return {
        "plans": {chapter: json.loads(path.read_text(encoding="utf-8")) for chapter, path in OUTPUTS.items()},
        "stories": {chapter: json.loads(path.read_text(encoding="utf-8")) for chapter, path in STORY_OUTPUTS.items()},
        "beats": {chapter: json.loads(path.read_text(encoding="utf-8")) for chapter, path in BEAT_OUTPUTS.items()},
        "markdown": MARKDOWN_OUTPUT.read_text(encoding="utf-8"),
        "adr": ADR_OUTPUT.read_text(encoding="utf-8"),
    }


def validate_batch(package: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    plans, stories, beats = package.get("plans", {}), package.get("stories", {}), package.get("beats", {})
    check(set(plans) == {"CH10", "CH11"}, "plan chapter set")
    check(set(stories) == {"CH10", "CH11"}, "story chapter set")
    check(set(beats) == {"CH10", "CH11"}, "beat chapter set")
    if not all(chapter in plans and chapter in stories and chapter in beats for chapter in ("CH10", "CH11")):
        return errors
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    arc = json.loads(ARC_PATH.read_text(encoding="utf-8"))
    arc_chapters = {row["chapter_id"]: row for row in arc["chapters"]}
    protected = ["faces", "adult silhouettes", "important hands", "weapons and tools", "story objects", "physical Garden Ledger surfaces", "injury and load geometry"]
    for chapter in ("CH10", "CH11"):
        document = plans[chapter]
        for message in validate_semantic_graph(document, contract):
            errors.append(f"{chapter}: {message}")
        rows, sequences = document.get("plans", []), document.get("sequences", [])
        arc_chapter = arc_chapters[chapter]
        check(len(rows) == document.get("declared_target_panel_count") == 40, f"{chapter}: forty plans")
        check(len(sequences) == 8 and all(len(row.get("panel_ids", [])) == 5 for row in sequences), f"{chapter}: eight five-panel sequences")
        check([row.get("display_order") for row in rows] == list(range(1, 41)), f"{chapter}: chronological order")
        check(len({row.get("narrative_beat") for row in rows}) == 40 and all(len(row.get("narrative_beat", "")) >= 40 for row in rows), f"{chapter}: unique substantive beats")
        check({row.get("narrative_phase_id") for row in rows} == {f"phase0{i}" for i in range(1, 7)}, f"{chapter}: six phases")
        check(document.get("opening_state") == arc_chapter["opening_state_key"], f"{chapter}: arc opening")
        check(document.get("closing_changed_state") == arc_chapter["closing_state_key"], f"{chapter}: arc closing")
        check(len(arc_chapter.get("state_delta", {})) >= 5, f"{chapter}: drastic arc delta")
        initial, final = document["continuity_contract"]["initial_state"], document["continuity_contract"]["final_state"]
        check(sum(initial[key] != final[key] for key in initial) >= 5, f"{chapter}: material continuity delta")
        check(document.get("planning_structure") == "ComicPanelPlan" and document.get("animation_shot_plan") is None and document.get("e_conte") is None, f"{chapter}: comic-only planning")
        check(document.get("execution_ready") is False and document.get("promotion_decision") is None, f"{chapter}: not promoted")
        check(not walk_forbidden({"plan": document, "story": stories[chapter], "beat": beats[chapter]}), f"{chapter}: execution field leak")
        check(all(role.startswith("ADULT_") for role in document.get("fictional_adult_roles", [])), f"{chapter}: adult roles")
        check("child" not in json.dumps({"plan": document, "story": stories[chapter], "beat": beats[chapter]}).lower(), f"{chapter}: child-coded content")
        identity = document.get("identity_contract", {})
        check(all(term in identity.get("SOREN", "") for term in ("light-brown to dark-blond", "swept-back", "never black or bright blond", "oatmeal", "braced left-leg gait")), f"{chapter}: Soren anchors")
        check(all(term in identity.get("SIGRID", "") for term in ("dark-brown to near-black", "compact low bun or practical braid", "never blond or loose red curls", "plaid", "weather cape")), f"{chapter}: Sigrid anchors")
        check(all(term in identity.get("HALVOR_KEST", "") for term in ("fictional adult", "dark iron-brown close-cropped hair", "gray temples", "quarry armor")), f"{chapter}: Halvor anchors")
        check(all(row.get("comic_direction", {}).get("lettering", {}).get("protected_subjects") == protected for row in rows), f"{chapter}: protected lettering")
        ledger = [row for row in rows if any(str(asset).startswith("ng-progression-ui-") for asset in row.get("asset_ids", []))]
        check(bool(ledger), f"{chapter}: physical Ledger present")
        for row in ledger:
            language = (row.get("narrative_beat", "") + " " + row.get("composition_intent", "")).lower()
            check(any(term in language for term in PHYSICAL_SUBSTRATES), f"{chapter}: physical Ledger substrate {row.get('panel_id')}")
            check("generic floating hud" not in language and "persistent floating hud" not in language and "as a floating hud" not in language, f"{chapter}: floating HUD {row.get('panel_id')}")
        progression = document.get("progression_contract", {})
        check(all(progression.get(category) for category in ("armor", "weapons", "upgraded_clothing", "classes", "system_ui")), f"{chapter}: progression bindings")
        story, scene = stories[chapter], beats[chapter]
        check(story.get("opening_state") == document.get("opening_state") and story.get("closing_changed_state") == document.get("closing_changed_state"), f"{chapter}: story state keys")
        check(story.get("continuity_final_state") == final and story.get("promotion_decision") is None, f"{chapter}: story final binding")
        check(scene.get("story_state_id") == document.get("story_state_id"), f"{chapter}: scene/story binding")
        check(scene.get("causal_setpieces") == arc_chapter.get("causal_setpieces") and scene.get("closing_hook") == arc_chapter.get("closing_hook"), f"{chapter}: scene arc binding")

    ch09 = json.loads(CH09_PATH.read_text(encoding="utf-8"))
    ch10, ch11 = plans["CH10"], plans["CH11"]
    check(ch10["continuity_contract"]["initial_state"] == ch09["continuity_contract"]["final_state"], "exact CH09-to-CH10 carry")
    check(ch11["continuity_contract"]["initial_state"] == ch10["continuity_contract"]["final_state"], "exact CH10-to-CH11 carry")
    check(ch10.get("closing_changed_state") == ch11.get("opening_state"), "CH10-to-CH11 state key")
    ch10_final, ch11_final = ch10["continuity_contract"]["final_state"], ch11["continuity_contract"]["final_state"]
    check("soren_left_lower_leg_crush_sprain_rigid_brace_movement_limited" in ch10_final["injuries"], "CH10 persistent brace injury")
    for sequence in ch10["sequences"]:
        subset = [row for row in ch10["plans"] if row["panel_id"] in sequence["panel_ids"]]
        language = " ".join(row["narrative_beat"] + " " + row["composition_intent"] for row in subset).lower()
        check(any(term in language for term in ("brace", "injur", "seated", "leg support", "limp")), f"CH10: injury consequence {sequence['sequence_id']}")
    check("forged_socket_and_hook_wardens_reach" in ch10_final["props"] and "sigrid_owned_compact_bow" in ch10_final["props"] and "sigrid_utility_seax" in ch10_final["props"], "CH10 practical weapons persist")
    check("tamsin_transported_to_brackenwake_under_medicine_clause" in ch10_final["clues"] and ch10_final["locations"] == ["brackenwake_forge_and_council_yard"], "CH10 Tamsin causal transport")
    check("halvor_admits_outer_node_sacrifice_for_winter_light" in ch10_final["clues"] and "halvor_kest_rival_not_yet_enemy" in ch10_final["clues"], "CH10 adult faction conflict")
    check("soren_left_lower_leg_crush_sprain_rigid_brace_aggravated_movement_limited" in ch11_final["injuries"], "CH11 injury not erased by class")
    check("brackenwake_collectively_defeats_brood_mireback" in ch11_final["clues"], "CH11 collective defense")
    check(all(clue in ch11_final["clues"] for clue in ("two_hands_one_threshold_shared_bond_earned", "majority_compact_supports_northward_mission", "kest_loses_unilateral_control", "pair_become_publicly_accountable_co_leaders")), "CH11 leadership/faction/relationship progression")
    check(all(clue in ch11_final["clues"] for clue in ("soren_earns_hearth_warden_through_common_threshold_defense", "sigrid_advances_to_thornpath_wayfinder_through_shared_safe_passage")), "CH11 formal classes")
    check("tamsin_reveals_hidden_north_garden_route" in ch11_final["clues"] and "concealed_north_garden_map_section" in ch11_final["props"], "CH11 closing map hook")
    check((ch11["progression_contract"].get("monsters") or {}).get("asset_ids") == ["ng-progression-monster-mireback-r1", "ng-progression-monster-brood-mireback-r1"], "CH11 monster bindings")
    check((ch11["progression_contract"].get("classes") or {}).get("asset_ids") == ["ng-progression-class-soren-hearth-warden-r1", "ng-progression-class-sigrid-thornpath-wayfinder-r1"], "CH11 class bindings")
    check(sum(len(row["plans"]) for row in plans.values()) == 80 and sum(len(row["sequences"]) for row in plans.values()) == 16, "batch totals")
    for token in ("80 unique chronological plans", "CH09→CH10→CH11", "collective defense", "No prompt, provider call, upload, image"):
        check(token in package.get("markdown", ""), f"authoring doc token: {token}")
    adr = package.get("adr", "")
    check("## Status" in adr and "Accepted for provisional canon-development authoring only" in adr, "ADR-0202 accepted status")
    check("This ADR grants no prompt, provider, upload" in adr, "ADR-0202 authority boundary")
    return errors


def self_test(package: dict[str, Any]) -> tuple[int, int]:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("planning", lambda p: p["plans"]["CH10"].update(planning_structure="AnimationShotPlan")),
        ("animation", lambda p: p["plans"]["CH10"].update(animation_shot_plan={})),
        ("e_conte", lambda p: p["plans"]["CH11"].update(e_conte={})),
        ("execution", lambda p: p["plans"]["CH11"].update(execution_ready=True)),
        ("prompt", lambda p: p["plans"]["CH10"]["plans"][0].update(prompt="forbidden")),
        ("render", lambda p: p["stories"]["CH11"].update(render_record={})),
        ("panel_missing", lambda p: p["plans"]["CH10"]["plans"].pop()),
        ("panel_duplicate", lambda p: p["plans"]["CH11"]["plans"][1].update(panel_id=p["plans"]["CH11"]["plans"][0]["panel_id"])),
        ("display", lambda p: p["plans"]["CH10"]["plans"][2].update(display_order=99)),
        ("beat_duplicate", lambda p: p["plans"]["CH11"]["plans"][1].update(narrative_beat=p["plans"]["CH11"]["plans"][0]["narrative_beat"])),
        ("phase", lambda p: [row.update(narrative_phase_id="phase02") for row in p["plans"]["CH10"]["plans"] if row["narrative_phase_id"] == "phase01"]),
        ("sequence_missing", lambda p: p["plans"]["CH11"]["sequences"].pop()),
        ("sequence_size", lambda p: p["plans"]["CH10"]["sequences"][0].update(panel_ids=p["plans"]["CH10"]["sequences"][0]["panel_ids"][:4])),
        ("arc_opening", lambda p: p["plans"]["CH10"].update(opening_state="BROKEN")),
        ("arc_closing", lambda p: p["plans"]["CH11"].update(closing_changed_state="BROKEN")),
        ("ch09_carry", lambda p: p["plans"]["CH10"]["continuity_contract"].update(initial_state={})),
        ("ch10_carry", lambda p: p["plans"]["CH11"]["continuity_contract"].update(initial_state={})),
        ("continuity_edge", lambda p: p["plans"]["CH10"]["plans"][5]["continuity_carry_out"]["props"].append("drift")),
        ("child", lambda p: p["plans"]["CH11"]["fictional_adult_roles"].append("CHILD_ROLE")),
        ("soren_hair", lambda p: p["plans"]["CH10"]["identity_contract"].update(SOREN="black hair")),
        ("sigrid_hair", lambda p: p["plans"]["CH11"]["identity_contract"].update(SIGRID="loose red curls")),
        ("halvor_hair", lambda p: p["plans"]["CH10"]["identity_contract"].update(HALVOR_KEST="blond")),
        ("lettering", lambda p: p["plans"]["CH11"]["plans"][0]["comic_direction"]["lettering"].update(protected_subjects=[])),
        ("safe_zone", lambda p: p["plans"]["CH10"]["plans"][0]["comic_direction"]["lettering"]["safe_zones"][0].update(rect_norm=[0.9, 0.1, 1.2, 0.3])),
        ("floating_ledger", lambda p: p["plans"]["CH10"]["plans"][14].update(narrative_beat="A generic floating HUD appears.")),
        ("armor", lambda p: p["plans"]["CH10"]["progression_contract"].update(armor=None)),
        ("classes", lambda p: p["plans"]["CH11"]["progression_contract"].update(classes=None)),
        ("monsters", lambda p: p["plans"]["CH11"]["progression_contract"].update(monsters=None)),
        ("brace", lambda p: p["plans"]["CH10"]["continuity_contract"]["final_state"]["injuries"].remove("soren_left_lower_leg_crush_sprain_rigid_brace_movement_limited")),
        ("transport", lambda p: p["plans"]["CH10"]["continuity_contract"]["final_state"]["clues"].remove("tamsin_transported_to_brackenwake_under_medicine_clause")),
        ("faction", lambda p: p["plans"]["CH10"]["continuity_contract"]["final_state"]["clues"].remove("halvor_kest_rival_not_yet_enemy")),
        ("injury_cure", lambda p: p["plans"]["CH11"]["continuity_contract"]["final_state"]["injuries"].remove("soren_left_lower_leg_crush_sprain_rigid_brace_aggravated_movement_limited")),
        ("collective", lambda p: p["plans"]["CH11"]["continuity_contract"]["final_state"]["clues"].remove("brackenwake_collectively_defeats_brood_mireback")),
        ("bond", lambda p: p["plans"]["CH11"]["continuity_contract"]["final_state"]["clues"].remove("two_hands_one_threshold_shared_bond_earned")),
        ("map_hook", lambda p: p["plans"]["CH11"]["continuity_contract"]["final_state"]["props"].remove("concealed_north_garden_map_section")),
        ("story_final", lambda p: p["stories"]["CH10"].update(continuity_final_state={})),
        ("story_promotion", lambda p: p["stories"]["CH11"].update(promotion_decision=True)),
        ("scene_setpieces", lambda p: p["beats"]["CH10"].update(causal_setpieces=[])),
        ("scene_hook", lambda p: p["beats"]["CH11"].update(closing_hook="changed")),
        ("doc", lambda p: p.update(markdown=p["markdown"].replace("80 unique chronological plans", "79 plans"))),
        ("adr", lambda p: p.update(adr=p["adr"].replace("Accepted for provisional canon-development authoring only", "Proposed"))),
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
    errors = validate_batch(package)
    if package != expected_package():
        errors.append("compiled outputs are stale or nondeterministic")
    caught = total = 0
    if args.self_test:
        caught, total = self_test(package)
        if caught != total:
            errors.append(f"adversarial {caught}/{total}")
    result = {"status": "PASS" if not errors else "FAIL", "errors": errors, "chapters": 2, "panels": sum(len(row["plans"]) for row in package["plans"].values()), "sequences": sum(len(row["sequences"]) for row in package["plans"].values()), "ch09_to_ch10_state_sha256": canonical_hash(package["plans"]["CH10"]["continuity_contract"]["initial_state"]), "ch10_to_ch11_state_sha256": canonical_hash(package["plans"]["CH11"]["continuity_contract"]["initial_state"]), "adversarial": f"{caught}/{total}" if args.self_test else None}
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
