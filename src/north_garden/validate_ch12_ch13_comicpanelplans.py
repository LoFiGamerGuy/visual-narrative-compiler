"""Fail closed on the CH12-CH13 rupture-and-co-keeper authoring batch."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Callable
from typing import Any

from compile_ch12_ch13_comicpanelplans import (
    ADR_OUTPUT,
    ARC_PATH,
    BEAT_OUTPUTS,
    CH11_PATH,
    CONTRACT_PATH,
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

FORBIDDEN_KEYS = {
    "prompt", "output", "provider", "service", "model", "endpoint", "request_id",
    "provider_usage", "usage", "cost_usd", "monetary_cost_usd", "seed",
    "input_references", "rendered_candidate", "render_record",
}
PHYSICAL_SUBSTRATES = (
    "physical", "brass", "iron", "stone", "water", "condens", "wet", "glass",
    "socket", "tool", "plate", "lintel", "surface", "ring", "key", "threshold",
)
PROTECTED = [
    "faces", "adult silhouettes", "important hands", "weapons and tools", "story objects",
    "physical Garden Ledger surfaces", "injury and load geometry",
    "consent and role-order geometry",
]
CHAPTERS = ("CH12", "CH13")


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


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
    chapters = {row["chapter_id"]: row for row in arc["chapters"]}
    ch11 = json.loads(CH11_PATH.read_text(encoding="utf-8"))
    plans: dict[str, dict[str, Any]] = {}
    plans["CH12"] = build_chapter("CH12", chapters["CH12"], ch11["continuity_contract"]["final_state"])
    plans["CH13"] = build_chapter("CH13", chapters["CH13"], plans["CH12"]["continuity_contract"]["final_state"])
    return {
        "plans": plans,
        "stories": {chapter: story_state(chapter, chapters[chapter], plans[chapter]) for chapter in CHAPTERS},
        "beats": {chapter: scene_beat(chapter, chapters[chapter]) for chapter in CHAPTERS},
        "markdown": authoring_markdown(plans),
        "adr": adr_markdown(),
    }


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
    plans = package.get("plans", {})
    stories = package.get("stories", {})
    beats = package.get("beats", {})
    check(set(plans) == set(CHAPTERS), "plan chapter set")
    check(set(stories) == set(CHAPTERS), "story chapter set")
    check(set(beats) == set(CHAPTERS), "beat chapter set")
    if not all(chapter in plans and chapter in stories and chapter in beats for chapter in CHAPTERS):
        return errors

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    arc = json.loads(ARC_PATH.read_text(encoding="utf-8"))
    arc_chapters = {row["chapter_id"]: row for row in arc["chapters"]}
    for chapter in CHAPTERS:
        document = plans[chapter]
        rows = document.get("plans", [])
        sequences = document.get("sequences", [])
        arc_chapter = arc_chapters[chapter]
        for message in validate_semantic_graph(document, contract):
            errors.append(f"{chapter}: {message}")
        check(len(rows) == document.get("declared_target_panel_count") == 40, f"{chapter}: forty plans")
        check(len(sequences) == 8 and all(len(row.get("panel_ids", [])) == 5 for row in sequences), f"{chapter}: eight five-panel sequences")
        check([row.get("display_order") for row in rows] == list(range(1, 41)), f"{chapter}: chronological order")
        check(len({row.get("panel_id") for row in rows}) == 40, f"{chapter}: unique panel ids")
        check(len({row.get("narrative_beat") for row in rows}) == 40 and all(len(row.get("narrative_beat", "")) >= 40 for row in rows), f"{chapter}: unique substantive beats")
        check({row.get("narrative_phase_id") for row in rows} == {f"phase0{i}" for i in range(1, 7)}, f"{chapter}: six phases")
        check(document.get("opening_state") == arc_chapter["opening_state_key"], f"{chapter}: arc opening")
        check(document.get("closing_changed_state") == arc_chapter["closing_state_key"], f"{chapter}: arc closing")
        check(document.get("planning_structure") == "ComicPanelPlan" and document.get("animation_shot_plan") is None and document.get("e_conte") is None, f"{chapter}: comic-only planning")
        check(document.get("execution_ready") is False and document.get("promotion_decision") is None, f"{chapter}: not promoted")
        check(not walk_forbidden({"plan": document, "story": stories[chapter], "beat": beats[chapter]}), f"{chapter}: execution field leak")
        check(all(role.startswith("ADULT_") for role in document.get("fictional_adult_roles", [])), f"{chapter}: adult roles")
        check("child" not in json.dumps({"plan": document, "story": stories[chapter], "beat": beats[chapter]}).lower(), f"{chapter}: child-coded content")
        identity = document.get("identity_contract", {})
        check(all(term in identity.get("SOREN", "") for term in ("light-brown to dark-blond", "swept-back", "never black or bright blond", "oatmeal", "brace")), f"{chapter}: Soren identity anchors")
        check(all(term in identity.get("SIGRID", "") for term in ("dark-brown to near-black", "compact low bun or practical braid", "never blond or loose red curls", "plaid")), f"{chapter}: Sigrid identity anchors")
        check(all(row.get("comic_direction", {}).get("lettering", {}).get("protected_subjects") == PROTECTED for row in rows), f"{chapter}: protected lettering")
        ledger = [row for row in rows if any(str(asset).startswith(("ng-progression-ui-", "ng-progression-class-")) for asset in row.get("asset_ids", []))]
        check(bool(ledger), f"{chapter}: physical Ledger present")
        for row in ledger:
            language = (row.get("narrative_beat", "") + " " + row.get("composition_intent", "")).lower()
            check(any(term in language for term in PHYSICAL_SUBSTRATES), f"{chapter}: physical Ledger substrate {row.get('panel_id')}")
            check(not any(term in language for term in ("generic floating hud", "persistent floating hud", "as a floating hud")), f"{chapter}: floating HUD {row.get('panel_id')}")
        progression = document.get("progression_contract", {})
        check(all(progression.get(category) for category in ("armor", "weapons", "upgraded_clothing", "monsters", "classes", "system_ui")), f"{chapter}: progression categories")
        story, scene = stories[chapter], beats[chapter]
        final = document["continuity_contract"]["final_state"]
        check(story.get("opening_state") == document.get("opening_state") and story.get("closing_changed_state") == document.get("closing_changed_state"), f"{chapter}: story state keys")
        check(story.get("continuity_final_state") == final and story.get("promotion_decision") is None, f"{chapter}: story final binding")
        check(scene.get("story_state_id") == document.get("story_state_id"), f"{chapter}: scene/story binding")
        check(scene.get("causal_setpieces") == arc_chapter.get("causal_setpieces") and scene.get("closing_hook") == arc_chapter.get("closing_hook"), f"{chapter}: scene arc binding")

    ch11 = json.loads(CH11_PATH.read_text(encoding="utf-8"))
    ch12, ch13 = plans["CH12"], plans["CH13"]
    ch12_initial = ch12["continuity_contract"]["initial_state"]
    ch12_final = ch12["continuity_contract"]["final_state"]
    ch13_initial = ch13["continuity_contract"]["initial_state"]
    ch13_final = ch13["continuity_contract"]["final_state"]
    check(ch12_initial == ch11["continuity_contract"]["final_state"], "exact CH11-to-CH12 carry")
    check(ch13_initial == ch12_final, "exact CH12-to-CH13 carry")
    check(ch12.get("closing_changed_state") == ch13.get("opening_state"), "CH12-to-CH13 state key")

    rupture = {
        "strategic_rupture_begins_over_unilateral_protection",
        "two_hands_one_threshold_breaks_under_conflicting_intent",
        "partners_rejoin_in_action_before_emotional_resolution",
        "tamsin_falsified_route_to_deter_access_after_keeper_consumption",
        "obsolete_training_fork_became_unstable_after_map_falsification",
        "original_gate_route_isolates_one_key_bearer",
        "sigrid_has_verified_route_authority_and_veto",
        "soren_has_measured_load_authority_and_veto",
        "either_partner_may_halt_without_coercion",
        "material_risk_must_be_disclosed",
        "restart_requires_stated_intent_and_mutual_consent",
        "two_hands_one_threshold_restored_by_explicit_consent",
        "brass_key_fused_into_wardens_reach",
    }
    check(rupture <= set(ch12_final["clues"]), "CH12 rupture, truth, rules, restoration, fusion")
    check(ch12_final["wardrobe"] == [
        "soren_oatmeal_quilted_coat_left_shoulder_panel_sacrificed_quarry_guards_ash_scored",
        "sigrid_plaid_weather_cape_shortened_with_route_flag_ties_quarry_guards_thorn_scored",
    ], "CH12 irreversible wardrobe")
    check(ch12_final.get("injuries") == ch12_initial.get("injuries"), "CH12 persistent injuries")
    check("wardens_reach_with_fused_brass_boundary_key_gate_interface" in ch12_final["props"] and "brass_boundary_key" not in ch12_final["props"], "CH12 fused key prop")
    check(ch12_final["locations"] == ["north_garden_gate_open_threshold"] and ch12_final["weather"] == ["winter_day_five_dawn_green_summer_beyond_gate"], "CH12 gate changed state")

    climax = {
        "north_garden_entry_roles_mutually_assented",
        "moving_glasshouse_crossed_by_declared_complementarity",
        "co_keeper_circuit_mutually_assented_with_stop_rule",
        "explicit_dual_consent_completed_co_keeper_circuit",
        "crownroot_root_knot_spared",
        "crownroot_bound_as_living_guardian",
        "soren_boundarywright_warden_earned",
        "sigrid_thornpath_marshal_earned",
        "two_hands_one_threshold_matured_into_persistent_co_keeper_covenant",
        "distant_branch_burning", "distant_branch_dark", "distant_branch_moving_toward_north_garden",
    }
    check(climax <= set(ch13_final["clues"]), "CH13 consent, mercy, classes, covenant, wider hook")
    check(ch13_final["wardrobe"] == ch12_final["wardrobe"] and ch13_final["injuries"] == ch12_final["injuries"], "CH13 consequence carry")
    check("boundarywright_wardens_reach_fused_key_co_keeper_interface" in ch13_final["props"] and "wardens_reach_with_fused_brass_boundary_key_gate_interface" not in ch13_final["props"], "CH13 co-keeper interface")
    check(ch13_final["locations"] == ["north_garden_restored_boundary_heart_operational_base"], "CH13 operational base")
    check(ch13_final["weather"] == ["day_five_winter_sky_over_stable_north_garden_summer_microclimate"], "CH13 weather continuity")
    check(sum(len(row["plans"]) for row in plans.values()) == 80 and sum(len(row["sequences"]) for row in plans.values()) == 16, "batch totals")
    for token in ("80 unique chronological plans", "CH11→CH12→CH13", "strategic rupture", "co-keeper", "No prompt, provider call, upload, image"):
        check(token in package.get("markdown", ""), f"authoring doc token: {token}")
    adr = package.get("adr", "")
    check("## Status" in adr and "Accepted for provisional canon-development authoring only" in adr, "ADR-0204 accepted status")
    check("This ADR grants no prompt, provider, upload" in adr, "ADR-0204 authority boundary")
    return errors


def self_test(package: dict[str, Any]) -> tuple[int, int]:
    def remove_clue(chapter: str, clue: str) -> Callable[[dict[str, Any]], None]:
        return lambda p: p["plans"][chapter]["continuity_contract"]["final_state"]["clues"].remove(clue)

    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("planning", lambda p: p["plans"]["CH12"].update(planning_structure="AnimationShotPlan")),
        ("animation", lambda p: p["plans"]["CH12"].update(animation_shot_plan={})),
        ("e_conte", lambda p: p["plans"]["CH13"].update(e_conte={})),
        ("execution", lambda p: p["plans"]["CH13"].update(execution_ready=True)),
        ("prompt", lambda p: p["plans"]["CH12"]["plans"][0].update(prompt="forbidden")),
        ("render", lambda p: p["stories"]["CH13"].update(render_record={})),
        ("panel_missing", lambda p: p["plans"]["CH12"]["plans"].pop()),
        ("panel_duplicate", lambda p: p["plans"]["CH13"]["plans"][1].update(panel_id=p["plans"]["CH13"]["plans"][0]["panel_id"])),
        ("display", lambda p: p["plans"]["CH12"]["plans"][2].update(display_order=99)),
        ("beat_duplicate", lambda p: p["plans"]["CH13"]["plans"][1].update(narrative_beat=p["plans"]["CH13"]["plans"][0]["narrative_beat"])),
        ("phase", lambda p: [row.update(narrative_phase_id="phase02") for row in p["plans"]["CH12"]["plans"] if row["narrative_phase_id"] == "phase01"]),
        ("sequence_missing", lambda p: p["plans"]["CH13"]["sequences"].pop()),
        ("sequence_size", lambda p: p["plans"]["CH12"]["sequences"][0].update(panel_ids=p["plans"]["CH12"]["sequences"][0]["panel_ids"][:4])),
        ("arc_opening", lambda p: p["plans"]["CH12"].update(opening_state="BROKEN")),
        ("arc_closing", lambda p: p["plans"]["CH13"].update(closing_changed_state="BROKEN")),
        ("ch11_carry", lambda p: p["plans"]["CH12"]["continuity_contract"].update(initial_state={})),
        ("ch12_carry", lambda p: p["plans"]["CH13"]["continuity_contract"].update(initial_state={})),
        ("continuity_edge", lambda p: p["plans"]["CH12"]["plans"][5]["continuity_carry_out"]["props"].append("drift")),
        ("child", lambda p: p["plans"]["CH13"]["fictional_adult_roles"].append("CHILD_ROLE")),
        ("soren_hair", lambda p: p["plans"]["CH12"]["identity_contract"].update(SOREN="black hair")),
        ("sigrid_hair", lambda p: p["plans"]["CH13"]["identity_contract"].update(SIGRID="loose red curls")),
        ("lettering", lambda p: p["plans"]["CH13"]["plans"][0]["comic_direction"]["lettering"].update(protected_subjects=[])),
        ("safe_zone", lambda p: p["plans"]["CH12"]["plans"][0]["comic_direction"]["lettering"]["safe_zones"][0].update(rect_norm=[0.9, 0.1, 1.2, 0.3])),
        ("floating_ledger", lambda p: p["plans"]["CH12"]["plans"][2].update(narrative_beat="A generic floating HUD appears.")),
        ("armor", lambda p: p["plans"]["CH12"]["progression_contract"].update(armor=None)),
        ("classes", lambda p: p["plans"]["CH13"]["progression_contract"].update(classes=None)),
        ("monsters", lambda p: p["plans"]["CH13"]["progression_contract"].update(monsters=None)),
        ("rupture", remove_clue("CH12", "strategic_rupture_begins_over_unilateral_protection")),
        ("bond_break", remove_clue("CH12", "two_hands_one_threshold_breaks_under_conflicting_intent")),
        ("rejoin", remove_clue("CH12", "partners_rejoin_in_action_before_emotional_resolution")),
        ("tamsin_truth", remove_clue("CH12", "tamsin_falsified_route_to_deter_access_after_keeper_consumption")),
        ("unsafe_route", remove_clue("CH12", "obsolete_training_fork_became_unstable_after_map_falsification")),
        ("single_key", remove_clue("CH12", "original_gate_route_isolates_one_key_bearer")),
        ("route_veto", remove_clue("CH12", "sigrid_has_verified_route_authority_and_veto")),
        ("load_veto", remove_clue("CH12", "soren_has_measured_load_authority_and_veto")),
        ("halt", remove_clue("CH12", "either_partner_may_halt_without_coercion")),
        ("disclose", remove_clue("CH12", "material_risk_must_be_disclosed")),
        ("restart", remove_clue("CH12", "restart_requires_stated_intent_and_mutual_consent")),
        ("restore", remove_clue("CH12", "two_hands_one_threshold_restored_by_explicit_consent")),
        ("fusion", remove_clue("CH12", "brass_key_fused_into_wardens_reach")),
        ("wardrobe", lambda p: p["plans"]["CH12"]["continuity_contract"]["final_state"].update(wardrobe=[])),
        ("ch12_injury", lambda p: p["plans"]["CH12"]["continuity_contract"]["final_state"].update(injuries=[])),
        ("ch13_injury", lambda p: p["plans"]["CH13"]["continuity_contract"]["final_state"].update(injuries=[])),
        ("entry_consent", remove_clue("CH13", "north_garden_entry_roles_mutually_assented")),
        ("circuit_consent", remove_clue("CH13", "co_keeper_circuit_mutually_assented_with_stop_rule")),
        ("dual_consent", remove_clue("CH13", "explicit_dual_consent_completed_co_keeper_circuit")),
        ("spare", remove_clue("CH13", "crownroot_root_knot_spared")),
        ("bind", remove_clue("CH13", "crownroot_bound_as_living_guardian")),
        ("soren_class", remove_clue("CH13", "soren_boundarywright_warden_earned")),
        ("sigrid_class", remove_clue("CH13", "sigrid_thornpath_marshal_earned")),
        ("covenant", remove_clue("CH13", "two_hands_one_threshold_matured_into_persistent_co_keeper_covenant")),
        ("wider_hook", remove_clue("CH13", "distant_branch_moving_toward_north_garden")),
        ("story_final", lambda p: p["stories"]["CH12"].update(continuity_final_state={})),
        ("story_promotion", lambda p: p["stories"]["CH13"].update(promotion_decision=True)),
        ("scene_setpieces", lambda p: p["beats"]["CH12"].update(causal_setpieces=[])),
        ("scene_hook", lambda p: p["beats"]["CH13"].update(closing_hook="changed")),
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
    result = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "chapters": 2,
        "panels": sum(len(row["plans"]) for row in package["plans"].values()),
        "sequences": sum(len(row["sequences"]) for row in package["plans"].values()),
        "ch11_to_ch12_state_sha256": canonical_hash(package["plans"]["CH12"]["continuity_contract"]["initial_state"]),
        "ch12_to_ch13_state_sha256": canonical_hash(package["plans"]["CH13"]["continuity_contract"]["initial_state"]),
        "adversarial": f"{caught}/{total}" if args.self_test else None,
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
