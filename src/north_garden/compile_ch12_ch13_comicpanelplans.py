"""Compile the CH12-CH13 rupture-and-co-keeper ComicPanelPlan batch."""
# ruff: noqa: FLY002 - deterministic long-form prose assembly is intentional
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = ROOT / "production/canon/story-arcs/north-garden-ch06-ch13-progression-r1.json"
CONTRACT_PATH = ROOT / "production/comic/contracts/complete-chapter-comicpanelplan-authoring-contract-r1.json"
CH11_PATH = ROOT / "production/comic/ch11-sc01-panel-plans-r1.json"
BOUND_HASHES = {
    ARC_PATH: "04d0933b07cfc2c11d15c05ebabc1d6695b0ed73ca328fc1659e53f33f107539",
    CONTRACT_PATH: "e112fcd5d2b450746a6a6ad827ba6dff4ff77a0bf10c212f4718a334dc3e9d4e",
    CH11_PATH: "68f0be123a1af3c98f2135e85054a08565fbc0373fc4ecc1876fa1cdc4f1e831",
}
OUTPUTS = {chapter: ROOT / f"production/comic/{chapter.lower()}-sc01-panel-plans-r1.json" for chapter in ("CH12", "CH13")}
STORY_OUTPUTS = {chapter: ROOT / f"production/canon/story-state/{chapter.lower()}-sc01-r1.json" for chapter in ("CH12", "CH13")}
BEAT_OUTPUTS = {
    "CH12": ROOT / "production/scene-beats/ch12-sc01-map-lied-r1.json",
    "CH13": ROOT / "production/scene-beats/ch13-sc01-north-garden-r1.json",
}
MARKDOWN_OUTPUT = ROOT / "docs/research/ch12-ch13-comicpanelplan-authoring-r1.md"
ADR_OUTPUT = ROOT / "docs/adr/ADR-0204-author-ch12-ch13-as-rupture-and-co-keeper-continuity-batch.md"

PHASE_FUNCTIONS = {
    "phase01": "opening_state_and_orientation", "phase02": "movement_and_escalation",
    "phase03": "threshold_and_entry", "phase04": "causal_interaction_and_evidence",
    "phase05": "deduction_choice_and_consequence", "phase06": "reversal_return_or_closure",
}
SEQUENCES = {
    "CH12": [
        ("s01-hidden-section", "The map Tamsin hid", "phase01"),
        ("s02-ash-cut", "One route, two readings", "phase02"),
        ("s03-false-cairn", "The pass divides", "phase02"),
        ("s04-separate-paths", "Control cannot cross the gap", "phase03"),
        ("s05-sacrificed-cloth", "Leave a signal, lose protection", "phase04"),
        ("s06-truth-at-camp", "What happened to the last keeper", "phase04"),
        ("s07-negotiated-return", "State intent without command", "phase05"),
        ("s08-gate-consent", "Open without consuming one", "phase06"),
    ],
    "CH13": [
        ("s01-summer-under-winter", "The impossible Garden", "phase01"),
        ("s02-moving-glass", "Two roles through one maze", "phase02"),
        ("s03-crownroot-demand", "The keeper who was consumed", "phase02"),
        ("s04-soil-water-load", "Fight the Garden's mechanisms", "phase03"),
        ("s05-seven-node-circle", "Make the system share", "phase04"),
        ("s06-boundary-heart", "Both names at the heart", "phase04"),
        ("s07-co-keeper-choice", "Consent changes the covenant", "phase05"),
        ("s08-wider-branches", "A sanctuary and a larger failure", "phase06"),
    ],
}


def B(narrative: str, composition: str, cast: list[str], assets: list[str], scale: str,
      density: str, motion: str, updates: dict[str, dict[str, list[str]]] | None = None) -> dict[str, Any]:
    return {"narrative": narrative, "composition": composition, "cast": cast, "assets": assets,
            "scale": scale, "density": density, "motion": motion, "updates": updates or {}}


S, G, T, K, W = "ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE", "ADULT_HALVOR_KEST", "ADULT_BRIAR_COMPACT_WORKER"
SG, SGT, SGKW = [S, G], [S, G, T], [S, G, K, W]
CH12_BEATS: list[dict[str, Any]] = [
    B("At muddy dawn Tamsin holds the concealed North Garden map section between Soren and Sigrid at the repaired Brackenwake council threshold.", "wide exact-carry tableau with three injured/equipped adults and hidden map centered", SGT, ["ng-prop-concealed-north-garden-map-r1", "ng-set-brackenwake-council-yard-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "map_disclosure"),
    B("Sigrid aligns the concealed section with the damaged map, and mismatched stitch holes plus absent fold wear prove removal before Tamsin's injury.", "overhead physical map forensics with stitch holes, folds, and adult hands", [G, T], ["ng-prop-concealed-north-garden-map-r1", "ng-prop-damaged-node-map-r1"], "SMALL_OBJECT_INSERT", "LOW", "physical_comparison", {"clues": {"add": ["concealed_section_removed_before_tamsin_injury"]}}),
    B("Soren notes the drawn gate accepts the brass key but lacks load marks while the existing bond remains etched only on the real brass surface.", "medium evidence panel with map, key, forged tool, brace, and readable face", [S, G], ["ng-progression-ui-two-hands-bond-restored-r1", "ng-prop-brass-boundary-key-r1"], "MEDIUM_CHARACTER_CLUE", "LOW", "load_mark_audit", {"clues": {"add": ["concealed_gate_route_omits_structural_load_marks"]}}),
    B("Tamsin admits the gate may consume the key but evades who altered the route, leaving her face and the physical evidence simultaneously readable.", "quiet three-shot with Tamsin isolated behind map edge and two listeners", SGT, ["ng-prop-concealed-north-garden-map-r1"], "MEDIUM_TWO_SHOT", "LOW", "partial_confession"),
    B("After a day of care and work, the adult council majority authorizes supplies and a cart to Ash Cut while Halvor seals the tally among other votes.", "wide civic departure decision with adult tokens, cart, supplies, and Kest's equal seal", [S, G, T, K, W], ["ng-faction-briar-compact-adults-r1", "ng-prop-iron-service-tally-r1"], "WIDE_DIRECTIONAL_ANCHOR", "MEDIUM", "collective_authorization", {"locations": {"set": ["brackenwake_ash_cut_departure"]}, "weather": {"set": ["day_four_cold_evening"]}, "clues": {"add": ["compact_majority_authorizes_north_garden_departure"]}}),

    B("At night Soren leans into the cart on his aggravated brace, Tamsin rides with her leg supported, and Sigrid leads the road toward Ash Cut.", "wide adult-only travel with two persistent injuries, practical gear, and Sigrid lead", SGT, ["ng-set-ash-cut-road-r1", "ng-prop-rigid-brackenwake-leg-brace-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "injured_travel", {"locations": {"set": ["ash_cut_approach_road"]}, "weather": {"set": ["cold_day_four_night"]}}),
    B("The damaged orchard and breached store wall recede behind them while the adult cart driver turns back to rebuilding at the pass marker.", "wide consequence landscape with food damage, cart handoff, and no reset", [S, G, T, W], ["ng-set-brackenwake-damaged-orchards-r1"], "WIDE_ENVIRONMENTAL_MOTION", "MEDIUM", "escort_return", {"clues": {"add": ["compact_driver_returns_to_orchard_rebuilding"]}}),
    B("Physical milestones disagree with the concealed map by one repeated chain length, and Sigrid verifies the offset using wheel ruts and frost.", "medium route evidence with milestone, wheel rut, frost line, and fixed hair", [G], ["ng-prop-concealed-north-garden-map-r1", "ng-set-ash-cut-pass-r1"], "MEDIUM_CHARACTER_CLUE", "LOW", "distance_verification", {"clues": {"add": ["north_garden_map_repeats_one_chain_length_offset"]}}),
    B("Soren measures the same systematic offset with Warden's Reach and brace-limited steps, confirming design rather than copying Sigrid's conclusion.", "medium injured measurement with tool length, shortened stride, and cairn", [S], ["ng-progression-weapon-wardens-reach-forged-r1", "ng-prop-rigid-brackenwake-leg-brace-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "independent_measurement", {"clues": {"add": ["soren_independently_confirms_systematic_route_error"]}}),
    B("At the abandoned Warden camp the map's single ink path becomes two real trails: a load-bearing ash shelf and a narrow thorn maze.", "wide fork reveal with camp, cart, ash route, thorn route, and three adults", SGT, ["ng-set-abandoned-warden-camp-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "fork_reveal", {"locations": {"set": ["abandoned_warden_camp_at_split_routes"]}}),

    B("Pinpricks under the oil lamp reveal an erased original fork beneath Tamsin's darker route ink.", "small silent map-and-lamp forensic insert with layered physical marks", [], ["ng-prop-oil-lamp-r1", "ng-prop-concealed-north-garden-map-r1"], "SMALL_OBJECT_INSERT", "LOW", "lamplit_forensics", {"clues": {"add": ["erased_original_fork_found_under_tamsin_ink"]}}),
    B("On frost-coated boundary stone Sigrid sees two stressed surface lines, then verifies both against root pressure and falling ash.", "medium physical Wayfinder test with stone, roots, ash, and dark tied hair", [G], ["ng-progression-class-sigrid-thornpath-wayfinder-r1"], "MEDIUM_CHARACTER_CLUE", "LOW", "surface_verification"),
    B("Soren load-tests the left cairn and proves it can bear one braced adult but not the cart, while the right gap rejects Warden's Reach width.", "wide dual-obstacle mechanics with cairn load, cart, narrow thorns, tool, and brace", [S, G, T], ["ng-progression-weapon-key-fused-wardens-reach-r1", "ng-set-ash-cut-pass-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "route_load_test", {"clues": {"add": ["neither_fork_carries_whole_group_unchanged"]}}),
    B("A reversed keeper-load glyph matches the earlier Brackenwake plate technique but predates Halvor, and Tamsin admits falsifying this section.", "medium physical glyph comparison with bronze rubbing, map, and Tamsin reaction", [S, G, T], ["ng-prop-reversed-map-plate-r1", "ng-prop-concealed-north-garden-map-r1"], "MEDIUM_SENSORY_REACTION", "MEDIUM", "confession_on_evidence", {"clues": {"add": ["tamsin_admits_falsifying_north_garden_route", "route_falsification_predates_kest_sabotage"]}}),
    B("Soren takes custody of key and declares he alone will test the load route; Sigrid refuses his unilateral claim over route and risk.", "tight conflict two-shot with key/tool held visibly, separate faces, and Tamsin behind", [S, G, T], ["ng-prop-brass-boundary-key-r1", "ng-progression-weapon-wardens-reach-forged-r1"], "MEDIUM_TWO_SHOT", "HIGH", "unilateral_claim", {"clues": {"add": ["strategic_rupture_begins_over_unilateral_protection"]}}),

    B("Sigrid states structural expertise does not grant command of her route or body; Soren answers that unaudited path sight cannot risk Tamsin and key.", "face-readable argument with full evidence field and no obscured injuries or hands", [S, G, T], ["ng-prop-concealed-north-garden-map-r1"], "MEDIUM_TWO_SHOT", "MEDIUM", "explicit_rupture"),
    B("Tamsin says both paths circle to the gate and offers to remain at camp with whistle and rope, but neither partner lets confession settle their dispute.", "three-adult blocked movement tableau with camp, two paths, whistle, and rope", SGT, ["ng-prop-descent-rope-r1", "ng-set-abandoned-warden-camp-r1"], "MEDIUM_SENSORY_REACTION", "LOW", "witnessed_impasse", {"clues": {"add": ["tamsin_shelters_at_camp_with_signal_rope"]}}),
    B("Sigrid declares she will prove the thorn route while Soren declares he will secure the ash route, with no shared intent or consent.", "wide fork with adults turned down opposite paths and Tamsin centered behind", SGT, ["ng-set-ash-cut-pass-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "conflicting_departure"),
    B("The frost-green TWO HANDS mark on the real brass key and stone splits along its engraved seam and goes dark as unilateral plans diverge.", "small physical brass-and-stone bond fracture with no floating interface", [], ["ng-progression-ui-two-hands-bond-broken-r1"], "SMALL_OBJECT_INSERT", "LOW", "physical_bond_break", {"clues": {"add": ["two_hands_one_threshold_breaks_under_conflicting_intent"]}}),
    B("Soren limps left with key and Reach while Sigrid enters the thorn maze with bow, seax, and markers; Tamsin remains at the lamp-lit camp.", "wide split composition with three adult locations, fixed gear, and opposed vectors", SGT, ["ng-set-ash-cut-pass-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "separated_routes", {"locations": {"set": ["ash_cut_soren_left_sigrid_right_tamsin_camp"]}}),

    B("Soren's aggravated gait shifts too much weight onto the mapped cairn, and the ash crust shears beneath his rigid brace.", "low injury-causal panel with brace angle, cairn load, and sliding ash", [S], ["ng-prop-rigid-brackenwake-leg-brace-r1"], "MEDIUM_SINGLE_CAUSAL", "HIGH", "ash_shear", {"clues": {"add": ["false_ash_route_fails_under_braced_load"]}}),
    B("He anchors one temporary ward through the forged Reach into an iron pin, halting the slide but fixing himself in place.", "medium structural anchor with hook, iron pin, waist load, and immobilized injured adult", [S], ["ng-progression-class-soren-hearth-warden-r1", "ng-progression-weapon-wardens-reach-forged-r1"], "MEDIUM_SINGLE_CAUSAL", "HIGH", "fixed_ward_anchor"),
    B("A counterweighted gate lever collapses toward the gap, and Soren cannot cross while simultaneously holding both ward and lever.", "wide impossible load triangle with adult, ward pin, lever, gap, and injured stance", [S], ["ng-set-ash-cut-gate-lever-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "competing_loads"),
    B("Soren cuts the reinforced left oatmeal shoulder panel and splints the lever to the Reach shaft, irreversibly sacrificing protection to free one hand.", "tight practical cloth splint with knife, pale quilted panel, lever, shaft, and abrasion", [S], ["ng-progression-clothing-soren-shoulder-panel-sacrificed-r1", "ng-progression-armor-road-kit-irreversibly-damaged-r1"], "MEDIUM_SINGLE_CAUSAL", "HIGH", "cloth_splint", {"wardrobe": {"set": ["soren_oatmeal_quilted_coat_left_shoulder_panel_sacrificed_quarry_guards_ash_scored", "sigrid_plaid_weather_cape_and_quarry_guards_mud_scored"]}, "clues": {"add": ["soren_sacrifices_oatmeal_shoulder_panel_to_splint_gate"]}}),
    B("Unable to solve the route alone, Soren strikes forged socket against iron pin in their old threshold cadence—an audible request rather than command.", "small sound-and-tool action with repeated impact, taut lever, and isolated adult", [S], ["ng-progression-weapon-wardens-reach-forged-r1"], "SMALL_SENSORY_INSERT", "LOW", "audible_request", {"clues": {"add": ["soren_signals_for_help_without_command"]}}),

    B("Sigrid enters the thorn maze where a marked surface line doubles back while footprints and branch spring show the actual direction.", "tall route contradiction with thorns, footprints, bent branches, and fixed dark hair", [G], ["ng-progression-class-sigrid-thornpath-wayfinder-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "MEDIUM", "route_contradiction"),
    B("She verifies the path with lime on bark, soil compression, taut twine, and frost, keeping Ledger perception subordinate to physical evidence.", "medium evidence array with adult hand touching four physical signals", [G], ["ng-prop-lime-route-marks-r1"], "MEDIUM_CHARACTER_CLUE", "LOW", "multi_signal_verification"),
    B("Thorns seize the plaid hem across a closing root gap, so Sigrid cuts several recognizable flags and reties the shortened cape for mobility.", "wide cloth-tension action with seax cut, plaid flags, roots, and protected body silhouette", [G], ["ng-progression-clothing-sigrid-plaid-route-flags-r1", "ng-progression-armor-road-kit-irreversibly-damaged-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "cape_cut_and_retie", {"wardrobe": {"set": ["soren_oatmeal_quilted_coat_left_shoulder_panel_sacrificed_quarry_guards_ash_scored", "sigrid_plaid_weather_cape_shortened_with_route_flag_ties_quarry_guards_thorn_scored"]}, "props": {"add": ["plaid_route_flags"]}, "clues": {"add": ["sigrid_cuts_plaid_cape_into_persistent_route_flags"]}}),
    B("The flags make a safe line, but a fallen root lintel exceeds Sigrid's leverage, proving route knowledge cannot move every load alone.", "wide blocked route with visible safe flags, heavy lintel, seax, and adult scale", [G], ["ng-set-ash-cut-thorn-maze-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "insufficient_leverage", {"clues": {"add": ["wayfinder_route_alone_cannot_shift_root_lintel"]}}),
    B("Sigrid hears Soren's hammer cadence, times root flex to each strike, and raises plaid flags above thorns so he can see her answer.", "tall cross-gap signal with flags, root flex, sound source, and separated adults", [G], ["ng-progression-clothing-sigrid-plaid-route-flags-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "MEDIUM", "visible_answer", {"clues": {"add": ["sigrid_answers_request_with_verifiable_flag_timing"]}}),

    B("Alternating visible flags and audible strikes expose common stable posts across the divide, with every signal independently verifiable.", "wide split landscape linking cloth, sound, posts, and two isolated adults", SG, ["ng-progression-clothing-sigrid-plaid-route-flags-r1", "ng-progression-weapon-wardens-reach-forged-r1"], "WIDE_ENVIRONMENTAL_MOTION", "MEDIUM", "cross_gap_triangulation", {"clues": {"add": ["common_stable_posts_found_through_two_way_signals"]}}),
    B("Sigrid tensions recovered wire across the posts while Soren ratchets Reach from his fixed ash anchor, remotely rotating the root lintel.", "dual-causal remote leverage with wire tension, ratchet, posts, lintel, and injuries", SG, ["ng-prop-boundary-wire-coil-r1", "ng-progression-weapon-wardens-reach-forged-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "remote_combined_leverage"),
    B("They meet at the divide and catch each other's load—Sigrid routes Soren's injured step while Soren braces her opening—without instant forgiveness.", "medium physical rescue with braced step, root opening, two hands, and guarded faces", SG, ["ng-prop-rigid-brackenwake-leg-brace-r1"], "MEDIUM_TWO_SHOT", "HIGH", "mutual_load_catch", {"locations": {"set": ["ash_cut_central_divide_rejoined"]}, "clues": {"add": ["partners_rejoin_in_action_before_emotional_resolution"]}}),
    B("Together they return to camp and ask Tamsin for every material fact before choosing; the key remains visible with Soren, not hidden.", "quiet three-shot at lamp-lit camp with open key, map, and protected faces", SGT, ["ng-prop-brass-boundary-key-r1", "ng-set-abandoned-warden-camp-r1"], "MEDIUM_TWO_SHOT", "LOW", "full_disclosure_request", {"locations": {"set": ["abandoned_warden_camp_rejoined"]}}),
    B("Tamsin unstitches the lining to reveal a keeper-log brass rubbing and root-grown adult hand impression, confessing the last keeper became Crownroot and she diverted access onto an obsolete training fork.", "medium confession with physical rubbing, adult-scale print, unstitching hands, and three faces", SGT, ["ng-progression-monster-crownroot-r1", "ng-prop-keeper-log-brass-rubbing-r1"], "MEDIUM_CHARACTER_CLUE", "MEDIUM", "complete_confession", {"props": {"remove": ["concealed_north_garden_map_section"], "add": ["annotated_false_north_garden_map_section", "keeper_log_brass_rubbing"]}, "clues": {"add": ["tamsin_falsified_route_to_deter_access_after_keeper_consumption", "obsolete_training_fork_became_unstable_after_map_falsification", "original_gate_route_isolates_one_key_bearer", "last_north_garden_keeper_transformed_into_crownroot", "tamsin_served_last_north_garden_keeper", "tamsin_concealed_route_after_witnessing_keeper_consumption"]}}),

    B("At the sealed gate the pair rejects the single-keeper route but retains Tamsin's annotated false map as evidence rather than erasing her breach.", "wide gate confrontation with false map, three adults, and single-hand socket", SGT, ["ng-prop-annotated-false-map-r1", "ng-set-north-garden-gate-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "evidence_retained", {"clues": {"add": ["single_keeper_route_rejected", "leadership_boundaries_negotiated_not_forgiven"]}}),
    B("On the physical map margin they write separate authority, veto, halt, disclosure, and restart rules covering route, measured load, bodies, and material risk.", "overhead rule-writing on real map with two independent adult hands", SG, ["ng-prop-annotated-false-map-r1"], "SMALL_OBJECT_INSERT", "LOW", "negotiated_rules", {"clues": {"add": ["sigrid_has_verified_route_authority_and_veto", "soren_has_measured_load_authority_and_veto", "either_partner_may_halt_without_coercion", "material_risk_must_be_disclosed", "restart_requires_stated_intent_and_mutual_consent"]}}),
    B("Both adults state intent and assent; only then does TWO HANDS, ONE THRESHOLD return across the real brass key and forged socket.", "medium equal two-shot with physical brass inscription, separate faces, and no forced touch", SG, ["ng-progression-ui-two-hands-bond-restored-r1"], "MEDIUM_TWO_SHOT", "LOW", "explicit_reconsent", {"clues": {"add": ["two_hands_one_threshold_restored_by_explicit_consent"]}}),
    B("Gate roots draw the loose key toward a single-keeper recess; Soren seats it in Reach's socket while Sigrid holds the verified flag line, and pressure permanently fuses brass to iron.", "wide causal fusion with roots, key, forged socket, flag tension, and protected hands", SG, ["ng-progression-weapon-key-fused-wardens-reach-r1", "ng-progression-ui-north-garden-gate-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "pressure_fusion", {"props": {"remove": ["brass_boundary_key", "forged_socket_and_hook_wardens_reach"], "add": ["wardens_reach_with_fused_brass_boundary_key_gate_interface"]}, "clues": {"add": ["brass_key_fused_into_wardens_reach", "wardens_reach_only_remaining_north_garden_gate_interface"]}}),
    B("At day-five dawn injured Soren levers the fused Reach in the real gate socket while Sigrid closes a continuous plaid-flag route; green summer opens under winter sky as Crownroot speaks Hearth Warden.", "largest gate-opening anchor with combined load and route action, three adults, and season contrast", SGT, ["ng-progression-monster-crownroot-r1", "ng-progression-ui-north-garden-gate-r1", "ng-progression-weapon-key-fused-wardens-reach-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "gate_opening", {"locations": {"set": ["north_garden_gate_open_threshold"]}, "weather": {"set": ["winter_day_five_dawn_green_summer_beyond_gate"]}, "clues": {"add": ["north_garden_gate_opened_by_combined_load_and_route_actions", "green_summer_exists_beneath_winter_sky", "crownroot_addresses_soren_as_hearth_warden"]}}),
]
CH13_BEATS: list[dict[str, Any]] = [
    B("Beyond the opened winter gate, summer-green glasshouse alleys unfold as Sigrid leads and brace-limited Soren follows with the key fused into Warden's Reach.", "huge season-contrast Garden reveal with fixed hair, damaged garments, and gate vector", SG, ["ng-set-north-garden-glasshouse-r1", "ng-progression-weapon-key-fused-wardens-reach-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "threshold_reveal", {"locations": {"set": ["north_garden_outer_glasshouse"]}, "weather": {"set": ["day_five_winter_sky_impossible_summer_below"]}}),
    B("The fused brass is visibly grown into the forged socket; Soren's rigid brace and stripped oatmeal shoulder remain damaged beside Sigrid's shortened plaid and route-flag ties.", "tight carried-cost continuity panel with tool, brace, oatmeal, plaid, and adult hands", SG, ["ng-progression-armor-road-kit-irreversibly-damaged-r1", "ng-progression-weapon-key-fused-wardens-reach-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "carried_cost"),
    B("Root pressure travels from Crownroot through floor channels to the fused tool, tugging Soren toward an empty keeper recess while Sigrid holds the verified line.", "low structural tension with root channel, tool pull, brace stance, recess, and Sigrid route", SG, ["ng-progression-monster-crownroot-r1", "ng-progression-weapon-key-fused-wardens-reach-r1"], "MEDIUM_SENSORY_REACTION", "HIGH", "root_pressure_tug", {"clues": {"add": ["crownroot_targets_key_fused_gate_interface"]}}),
    B("Condensation writes SINGLE KEEPER REQUIRED on a real glass door while one adult-hand-shaped brass recess opens beneath it.", "silent physical glass-and-brass inscription with empty hand recess", [], ["ng-progression-ui-single-keeper-demand-r1"], "SMALL_OBJECT_INSERT", "LOW", "physical_inscription", {"clues": {"add": ["north_garden_repeats_single_keeper_demand"]}}),
    B("They declare entry terms—Sigrid routes, Soren anchors, either may call retreat, neither accepts alone—then cross shoulder to shoulder.", "equal adult two-shot avoiding the single-hand recess with clear consent space", SG, ["ng-set-north-garden-gate-r1"], "MEDIUM_TWO_SHOT", "MEDIUM", "mutual_entry_consent", {"clues": {"add": ["north_garden_entry_roles_mutually_assented"]}}),

    B("Roots load a hinged glasshouse door and rotate the path behind them, threatening separation through literal wood, glass, and weight.", "wide moving-door and root-pressure geometry with adult escape vectors", SG, ["ng-set-north-garden-glasshouse-r1", "ng-progression-monster-crownroot-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "root_pressure_rotation"),
    B("Sigrid verifies a frost-green trace in real condensation against gutter drip and tile fall, rejecting a brighter false corridor.", "medium evidence portrait with wet glass, gutter, tile slope, and fixed dark hair", [G], ["ng-progression-class-sigrid-thornpath-wayfinder-r1"], "MEDIUM_CHARACTER_CLUE", "LOW", "surface_route_check", {"clues": {"add": ["moving_paths_follow_water_not_light"]}}),
    B("Soren seats the fused Reach across hinge eyes and braces it to a stone mullion rather than loading his injured leg.", "medium structural load triangle with hook, hinge eyes, mullion, waist, and rigid brace", [S], ["ng-progression-weapon-key-fused-wardens-reach-r1"], "MEDIUM_SINGLE_CAUSAL", "HIGH", "structural_anchor", {"clues": {"add": ["first_glasshouse_door_anchored"]}}),
    B("The held gap lets Sigrid pass, knot one existing plaid route flag to the far latch, and return a tension line without cutting more garment.", "tall causal traverse with one carried flag, latch, line, and protected hands", [G], ["ng-progression-clothing-sigrid-plaid-route-flags-r1", "ng-progression-weapon-sigrid-utility-seax-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "route_flag_thread"),
    B("Sigrid hauls the flag line while Soren unloads the hook; the door rotates into a bridge instead of crushing him, proving complementary action.", "wide dual-action payoff with line tension, hook release, door bridge, and brace", SG, ["ng-set-north-garden-glasshouse-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "counterrotated_crossing", {"clues": {"add": ["moving_glasshouse_crossed_by_declared_complementarity"]}}),

    B("A drained root cistern reveals an adult-scale keeper harness, pruning knife, and maintenance tally grown into Crownroot's trunk without corpse or gore.", "large cistern and non-human Crownroot reveal with adult maintenance objects", SG, ["ng-progression-monster-crownroot-r1", "ng-set-north-garden-root-cistern-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "keeper_evidence_reveal", {"clues": {"add": ["last_keeper_tools_confirm_crownroot_origin"]}}),
    B("Sigrid aligns Tamsin's annotated physical map with seven pinched irrigation channels and finds root growth following the deliberately starved lines.", "quiet evidence layout on stone lip with map, channels, and adult hands", [G], ["ng-prop-annotated-false-map-r1", "ng-set-north-garden-root-cistern-r1"], "SMALL_OBJECT_INSERT", "LOW", "map_channel_match", {"clues": {"add": ["crownroot_growth_follows_starved_irrigation"]}}),
    B("Crownroot constricts a feed pipe; pressure bows roof glass and drives a root slab upward between the pair instead of firing an energy blast.", "wide plumbing-to-structure threat chain with pipe, glass, root slab, and separation", SG, ["ng-progression-monster-crownroot-r1", "ng-set-north-garden-glasshouse-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "pipe_constriction"),
    B("Sigrid wedges her seax under a jammed route shutter while Soren hooks its counterweight, and neither mechanism moves under one adult alone.", "clear opposite-force hand, seax, hook, shutter, and counterweight geometry", SG, ["ng-progression-weapon-sigrid-utility-seax-r1", "ng-progression-weapon-key-fused-wardens-reach-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "coupled_leverage"),
    B("Their combined release drops the shutter, diverts the slab, and admits them into the root-cistern service ring before Crownroot seals the door.", "wide cause-and-effect threshold with moving shutter, deflected slab, and sealed route", SG, ["ng-progression-monster-crownroot-r1", "ng-set-north-garden-root-cistern-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "service_ring_entry", {"locations": {"set": ["boundary_heart_service_ring"]}, "clues": {"add": ["crownroot_controls_irrigation_and_structure"]}}),

    B("Crownroot closes the main sluice, backed water bulges a copper pipe, and one glass roof bay cracks above Sigrid's route.", "wide pressure chain with sluice, pipe bulge, roof crack, and adult route", [G], ["ng-progression-monster-crownroot-r1", "ng-set-north-garden-root-cistern-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "pressure_escalation"),
    B("Sigrid marks true downslope on wet floor plates with lime and carried cloth flags; the surface trace appears only where water reaches.", "medium grounded route verification with wet plates, lime, cloth, and fixed hair", [G], ["ng-progression-class-sigrid-thornpath-wayfinder-r1", "ng-progression-clothing-sigrid-plaid-route-flags-r1"], "MEDIUM_CHARACTER_CLUE", "MEDIUM", "wet_route_marking", {"clues": {"add": ["seven_channel_bypass_route_verified"]}}),
    B("Unable to climb the service ladder on his aggravated leg, Soren pins the fused Reach low and rigs recovered boundary wire as a haul purchase.", "medium injury-constrained rig with low hook, wire, ladder, and unloaded brace", [S], ["ng-progression-weapon-key-fused-wardens-reach-r1", "ng-prop-boundary-wire-coil-r1"], "MEDIUM_SINGLE_CAUSAL", "HIGH", "low_rigging"),
    B("Sigrid climbs marked struts, cuts one rotten tension tie, and threads the freed line through Soren's wire purchase before glass falls.", "tall action with seax cut, tension line, struts, and protected hands", [G], ["ng-progression-weapon-sigrid-utility-seax-r1", "ng-prop-boundary-wire-coil-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "tension_rethread"),
    B("Her pull and his lever stroke open the bypass; water leaves the bulging pipe, loads a sound trellis, and peels soil from Crownroot without severing it.", "large water-tension-structure payoff with two adult actions and nonlethal consequence", SG, ["ng-progression-monster-crownroot-r1", "ng-progression-weapon-key-fused-wardens-reach-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "bypass_release", {"clues": {"add": ["pressure_redirected_without_killing_crownroot", "glasshouse_roof_bay_cracked"]}}),

    B("The drained basin exposes a brass boundary heart where seven channels converge on one adult-hand recess and a root-bound keeper chair.", "ominous wide physical system-machine reveal with brass, channels, and chair", [], ["ng-set-north-garden-boundary-heart-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "heart_reveal", {"clues": {"add": ["boundary_heart_designed_for_single_keeper_consumption"]}}),
    B("Old maintenance tallies show each solo keeper carried the network until bodily rooting, while a shared-custodian mark remains unfinished.", "small brass tally and chair-wear evidence insert without people", [], ["ng-prop-last-keeper-tally-r1"], "SMALL_OBJECT_INSERT", "LOW", "tally_reading", {"clues": {"add": ["solo_keeper_load_caused_rooting", "shared_custodian_exception_incomplete"]}}),
    B("Crownroot yanks the fused Reach toward the heart, dragging movement-limited Soren across wet stone while roots block Sigrid's direct line.", "tall taut tool-root-brace danger with clear pull and blocked rescue path", SG, ["ng-progression-monster-crownroot-r1", "ng-progression-weapon-key-fused-wardens-reach-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "forced_socket_drag"),
    B("Sigrid loops a route-flag line around a sound column and her bow's reinforced grip as a belay, arresting Soren before the socket.", "medium literal belay geometry with flag line, column, bow grip, and stopped slide", SG, ["ng-progression-weapon-sigrid-compact-bow-r1", "ng-progression-clothing-sigrid-plaid-route-flags-r1"], "MEDIUM_SINGLE_CAUSAL", "HIGH", "belay_rescue", {"clues": {"add": ["sigrid_bow_becomes_route_command_anchor"]}}),
    B("Instead of taking the chair or cutting the fused tool, Soren calls their agreed pause; Sigrid honors it and both hold balanced tension.", "close equal adult decision with chair empty, tool intact, and consent readable", SG, ["ng-set-north-garden-boundary-heart-r1"], "MEDIUM_TWO_SHOT", "MEDIUM", "consent_pause", {"clues": {"add": ["unilateral_sacrifice_refused"]}}),

    B("Soren touches the inner brass ring alone and one channel darkens; Sigrid touches the opposite outer ring simultaneously and all seven balance.", "overhead physical hands-rings-channel experiment with separate contact points", SG, ["ng-progression-ui-seven-node-restoration-r1"], "SMALL_OBJECT_INSERT", "LOW", "shared_load_test", {"clues": {"add": ["two_contact_points_balance_seven_channels"]}}),
    B("Sigrid lays a seven-stop route around the cistern with carried plaid flags, lime, and wire, each stop fixed to real brass or stone.", "overhead physical route plan with seven distinct stops and adult work", [G], ["ng-progression-clothing-sigrid-plaid-route-flags-r1", "ng-prop-boundary-wire-coil-r1"], "WIDE_DIRECTIONAL_ANCHOR", "MEDIUM", "route_laying"),
    B("Soren rigs three glass-door counterweights in sequence so opening one bypass transfers load to the next rather than into a human body.", "medium mechanical rig with three weights, labeled sequence, and brace-safe position", [S], ["ng-progression-weapon-key-fused-wardens-reach-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "counterweight_sequence", {"clues": {"add": ["three_stage_boundary_load_bypass_built"]}}),
    B("Crownroot ruptures the highest channel; falling glass and water isolate stop seven and create a visible deadline.", "wide escalation with rupture origin, glass fall, water, and blocked final stop", SG, ["ng-progression-monster-crownroot-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "channel_rupture"),
    B("Face to face, Soren consents to seat the tool only while Sigrid runs; she consents to close the circuit only while he honors her stop call.", "quiet equal consent two-shot with separated adults and protected dialogue fields", SG, ["ng-set-north-garden-boundary-heart-r1"], "MEDIUM_TWO_SHOT", "LOW", "co_keeper_plan_consent", {"clues": {"add": ["co_keeper_circuit_mutually_assented_with_stop_rule"]}}),

    B("Soren seats the fused Reach in the brass heart; his brace buckles, so he transfers load through a waist line to a stone column rather than healing.", "low action load triangle with socket, waist line, column, brace, and tool", [S], ["ng-progression-weapon-key-fused-wardens-reach-r1", "ng-set-north-garden-boundary-heart-r1"], "MEDIUM_SINGLE_CAUSAL", "HIGH", "heart_socket_anchor"),
    B("Sigrid runs stops one through three, stamps wet plates, and calls directions as each counterweight Soren releases sends water outward.", "wide route motion with adult runner, wet plates, three weights, and water paths", [G], ["ng-progression-ui-seven-node-restoration-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "circuit_first_half"),
    B("At stops four through six Crownroot drops a trellis; Sigrid cuts its loaded tie and uses her bow as a flag-line guide to swing it into a bridge.", "tall causal action with seax, bow, line, trellis, and non-human roots", [G], ["ng-progression-monster-crownroot-r1", "ng-progression-weapon-sigrid-utility-seax-r1", "ng-progression-weapon-sigrid-compact-bow-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "trellis_bridge"),
    B("Soren releases the final bypass in her declared order; water exposes Crownroot's root-knot, and he deliberately turns the weapon hook away.", "medium tool-choice panel with release lever, exposed knot, turned hook, and injured stance", [S], ["ng-progression-monster-crownroot-r1", "ng-progression-weapon-key-fused-wardens-reach-r1"], "MEDIUM_SINGLE_CAUSAL", "HIGH", "spare_exposed_root_knot", {"clues": {"add": ["crownroot_root_knot_spared"]}}),
    B("At stop seven roots seize both adults; each presses an opposite ring and independently renews consent before water, tension, and load close the circuit around two.", "largest hero panel with opposite rings, seven channels, roots, equal adults, and no blast", SG, ["ng-progression-monster-crownroot-r1", "ng-progression-ui-co-keeper-covenant-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "co_keeper_completion", {"clues": {"add": ["explicit_dual_consent_completed_co_keeper_circuit"]}}),

    B("Outward water loosens Crownroot from the keeper chair, and it settles as a pruned living cistern guardian with the old adult keeper token exposed.", "wide quiet non-human monster consequence with water, roots, chair, and token", SG, ["ng-progression-monster-crownroot-r1", "ng-set-north-garden-root-cistern-r1"], "WIDE_ENVIRONMENTAL_MOTION", "MEDIUM", "crownroot_bound", {"clues": {"add": ["crownroot_bound_as_living_guardian", "failed_stewardship_monsters_may_be_fought_healed_or_bargained_with"]}}),
    B("Frost-green letters form on the fused tool's real socket—BOUNDARYWRIGHT WARDEN—earned through redirected load without sole ownership or injury cure.", "small physical tool-and-brace class inscription with fused-key provenance", [S], ["ng-progression-class-soren-boundarywright-warden-r1", "ng-progression-weapon-wardens-reach-co-keeper-interface-r1"], "SMALL_OBJECT_INSERT", "LOW", "physical_class_inscription", {"props": {"remove": ["wardens_reach_with_fused_brass_boundary_key_gate_interface"], "add": ["boundarywright_wardens_reach_fused_key_co_keeper_interface"]}, "clues": {"add": ["soren_boundarywright_warden_earned"]}}),
    B("On Sigrid's real bow grip and brass route plate, THORNPATH MARSHAL records that she made the seven-stop route usable by others.", "small physical bow, brass plate, hand, damaged plaid, and fixed-hair class inscription", [G], ["ng-progression-class-sigrid-thornpath-marshal-r1", "ng-progression-weapon-sigrid-compact-bow-r1"], "SMALL_OBJECT_INSERT", "LOW", "physical_class_inscription", {"clues": {"add": ["sigrid_thornpath_marshal_earned"]}}),
    B("The gate opens both ways for Tamsin, Halvor, and adult Compact workers under declared terms while a full-grown Mireback and Hollow Stag drink restored runoff at a distance.", "large adult faction and sanctuary tableau with distant non-humanoid creatures and equal threshold", [S, G, T, K, W], ["ng-progression-ui-co-keeper-covenant-r1", "ng-progression-monster-mireback-r1", "ng-progression-monster-hollow-stag-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "accountable_entry", {"props": {"add": ["north_garden_co_keeper_service_tally", "last_keeper_brass_service_token"]}, "clues": {"add": ["two_hands_one_threshold_matured_into_persistent_co_keeper_covenant", "north_garden_operational_base_opened_under_co_keeper_consent", "connected_adult_settlements_share_stewardship", "compact_subject_to_shared_threshold_terms"]}}),
    B("A real copper-and-root relief map steadies seven local nodes and reveals distant branches—one burning, one dark, and one physically shifting toward North Garden.", "final wide physical network-map hook with equal pair on opposite sides", SG, ["ng-progression-ui-wider-network-map-r1", "ng-set-north-garden-boundary-heart-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "wider_network_reveal", {"locations": {"set": ["north_garden_restored_boundary_heart_operational_base"]}, "weather": {"set": ["day_five_winter_sky_over_stable_north_garden_summer_microclimate"]}, "clues": {"add": ["seven_local_nodes_one_branch_of_wider_network", "distant_branch_burning", "distant_branch_dark", "distant_branch_moving_toward_north_garden"]}}),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_sources() -> None:
    for path, expected in BOUND_HASHES.items():
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"bound source mismatch: {path.relative_to(ROOT).as_posix()}")


def apply_updates(state: dict[str, list[str]], updates: dict[str, dict[str, list[str]]]) -> dict[str, list[str]]:
    result = copy.deepcopy(state)
    for category, operation in updates.items():
        if "set" in operation:
            result[category] = list(operation["set"])
        for value in operation.get("remove", []):
            if value in result[category]:
                result[category].remove(value)
        for value in operation.get("add", []):
            if value not in result[category]:
                result[category].append(value)
    return result


def identity_assets(cast: list[str]) -> list[str]:
    mapping = {S: "ng-identity-soren-fictional-design-r1", G: "ng-identity-sigrid-fictional-design-r1", T: "ng-identity-tamsin-fictional-adult-r1", K: "ng-identity-halvor-kest-fictional-adult-r1", W: "ng-identity-briar-compact-worker-fictional-adult-r1"}
    return [mapping[role] for role in cast]


def progression(chapter: str) -> dict[str, Any]:
    if chapter == "CH12":
        return {
            "armor": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-armor-road-kit-irreversibly-damaged-r1"]},
            "weapons": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-weapon-wardens-reach-forged-r1", "ng-progression-weapon-key-fused-wardens-reach-r1", "ng-progression-weapon-sigrid-compact-bow-r1", "ng-progression-weapon-sigrid-utility-seax-r1"]},
            "upgraded_clothing": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-clothing-soren-shoulder-panel-sacrificed-r1", "ng-progression-clothing-sigrid-plaid-route-flags-r1"]},
            "monsters": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-monster-crownroot-r1"]},
            "classes": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-class-soren-hearth-warden-r1", "ng-progression-class-sigrid-thornpath-wayfinder-r1"]},
            "system_ui": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-ui-two-hands-bond-broken-r1", "ng-progression-ui-two-hands-bond-restored-r1", "ng-progression-ui-north-garden-gate-r1"]},
        }
    return {
        "armor": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-armor-road-kit-irreversibly-damaged-r1"]},
        "weapons": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-weapon-key-fused-wardens-reach-r1", "ng-progression-weapon-wardens-reach-co-keeper-interface-r1", "ng-progression-weapon-sigrid-compact-bow-r1", "ng-progression-weapon-sigrid-utility-seax-r1"]},
        "upgraded_clothing": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-clothing-soren-shoulder-panel-sacrificed-r1", "ng-progression-clothing-sigrid-plaid-route-flags-r1"]},
        "monsters": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-monster-crownroot-r1", "ng-progression-monster-mireback-r1", "ng-progression-monster-hollow-stag-r1"]},
        "classes": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-class-sigrid-thornpath-wayfinder-r1", "ng-progression-class-soren-boundarywright-warden-r1", "ng-progression-class-sigrid-thornpath-marshal-r1"]},
        "system_ui": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-ui-single-keeper-demand-r1", "ng-progression-ui-co-keeper-covenant-r1", "ng-progression-ui-seven-node-restoration-r1", "ng-progression-ui-wider-network-map-r1"]},
    }


def build_chapter(chapter: str, arc: dict[str, Any], initial: dict[str, list[str]]) -> dict[str, Any]:
    beats = CH12_BEATS if chapter == "CH12" else CH13_BEATS
    if len(beats) != 40:
        raise ValueError(f"{chapter} must define exactly forty beats")
    state = copy.deepcopy(initial)
    plans = []
    for index, source in enumerate(beats, start=1):
        sequence_slug, _, phase_id = SEQUENCES[chapter][(index - 1) // 5]
        carry_in = copy.deepcopy(state)
        state = apply_updates(state, source["updates"])
        carry_out = copy.deepcopy(state)
        panel_id = f"ng-{chapter.lower()}-sc01-p{index:03d}"
        anchor = "top_left" if index % 2 else "top_right"
        rect = [0.04, 0.04, 0.34, 0.20] if anchor == "top_left" else [0.66, 0.04, 0.96, 0.20]
        plans.append({
            "panel_id": panel_id, "plan_revision_id": f"{panel_id}-plan-r1", "display_order": index,
            "scene_beat_id": f"ng-beat-{chapter.lower()}-sc01-r1", "narrative_phase_id": phase_id,
            "narrative_beat": source["narrative"], "composition_intent": source["composition"],
            "visible_adult_cast": source["cast"], "asset_ids": list(dict.fromkeys(identity_assets(source["cast"]) + source["assets"])),
            "spatial_mode": "2d_only", "spatial_stage_contract_id": None, "spatial_assignments": [],
            "sequence_id": f"ng-{chapter.lower()}-{sequence_slug}", "scale_role": source["scale"], "density_class": source["density"],
            "continuity_carry_in": carry_in, "continuity_carry_out": carry_out,
            "comic_direction": {
                "motion_mode": source["motion"],
                "direction_note": f"Render the named physical cause and response literally: {source['narrative']}",
                "lettering": {
                    "state": "SAFE_ZONE_PLANNED_COPY_NOT_YET_AUTHORED", "placement_policy": "safe_zone",
                    "safe_zones": [{"anchor": anchor, "rect_norm": rect}],
                    "protected_subjects": ["faces", "adult silhouettes", "important hands", "weapons and tools", "story objects", "physical Garden Ledger surfaces", "injury and load geometry", "consent and role-order geometry"],
                },
            },
        })
    sequences = []
    for order, (slug, title, phase_id) in enumerate(SEQUENCES[chapter], start=1):
        subset = plans[(order - 1) * 5:order * 5]
        sequences.append({"sequence_id": f"ng-{chapter.lower()}-{slug}", "narrative_order": order, "title": title, "narrative_functions": [PHASE_FUNCTIONS[phase_id]], "panel_ids": [row["panel_id"] for row in subset], "continuity_entry": copy.deepcopy(subset[0]["continuity_carry_in"]), "continuity_exit": copy.deepcopy(subset[-1]["continuity_carry_out"])})
    return {"record_type": "ComicPanelPlanCollection", "schema_version": "2.0", "record_id": f"ng-comic-plans-{chapter.lower()}-sc01-r1", "state": "AUTHORING_COMPLETE_NOT_PROMOTED_PROVISIONAL_CANON", "medium": "comic", "planning_structure": "ComicPanelPlan", "animation_shot_plan": None, "e_conte": None, "chapter_title": arc["title"], "chapter_logline": arc["logline"], "story_state_id": f"ng-story-{chapter.lower()}-sc01-r1", "opening_state": arc["opening_state_key"], "closing_changed_state": arc["closing_state_key"], "declared_target_panel_count": 40, "fictional_adult_roles": [S, G, T, K, W], "identity_contract": {"SOREN": "clearly fictional mature adult; light-brown to dark-blond short-to-medium wavy swept-back hair, never black or bright blond; pale oatmeal work coat remains recognizable after shoulder-panel sacrifice; rigid left-leg brace and aggravated movement limit persist", "SIGRID": "clearly fictional mature adult; dark-brown to near-black hair in compact low bun or practical braid, never blond or loose red curls; dark blue-brown plaid remains recognizable after cape sections become route flags", "TAMSIN_REEVE": "clearly fictional adult courier-cartographer in practical non-sexualized field clothing with persistent recovering lower-leg injury", "HALVOR_KEST": "clearly fictional adult marshal with dark iron-brown close-cropped hair, gray temples, short matching beard, and practical quarry armor", "BRIAR_COMPACT_WORKER": "clearly fictional mature adult workers in practical non-sexualized work protection"}, "continuity_contract": {"initial_state": copy.deepcopy(plans[0]["continuity_carry_in"]), "final_state": copy.deepcopy(plans[-1]["continuity_carry_out"])}, "progression_contract": progression(chapter), "narrative_phases": [{"phase_id": phase, "narrative_function": function} for phase, function in PHASE_FUNCTIONS.items()], "sequences": sequences, "plans": plans, "promotion_decision": None, "execution_ready": False, "authoring_complete": True, "anti_duplication": {"default_candidates_per_panel": 1, "alternate_style_before_complete_chapter": False, "targeted_repair_cap_per_failed_panel": 2}}


def story_state(chapter: str, arc: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    return {"record_type": "StoryState", "schema_version": "1.0", "record_id": f"ng-story-{chapter.lower()}-sc01-r1", "scope": f"{chapter}_SC01_PROVISIONAL_CANON_AUTHORING_COMPLETE_NOT_RENDER_PROMOTED", "fictional_cast": plan["fictional_adult_roles"], "set": arc["primary_location"], "timeline_state": arc["timeline"], "opening_state": arc["opening_state_key"], "closing_changed_state": arc["closing_state_key"], "narrative_state": arc["logline"], "state_delta": arc["state_delta"], "continuity_final_state": plan["continuity_contract"]["final_state"], "promotion_decision": None, "source_limit": "Provisional canon-development authoring under ADR-0196 and ADR-0204; no render, acceptance, rights, exact-base, ingestion, or cross-medium authority."}


def scene_beat(chapter: str, arc: dict[str, Any]) -> dict[str, Any]:
    return {"record_type": "SceneBeat", "schema_version": "1.0", "record_id": f"ng-beat-{chapter.lower()}-sc01-r1", "story_state_id": f"ng-story-{chapter.lower()}-sc01-r1", "chapter_question": arc["chapter_question"], "narrative_intent": arc["logline"], "causal_setpieces": arc["causal_setpieces"], "closing_hook": arc["closing_hook"], "comic_direction_boundary": "Direction is contained in ComicPanelPlan; AnimationShotPlan and E-Conte are absent/null."}


def authoring_markdown(plans: dict[str, dict[str, Any]]) -> str:
    return "\n".join(["# CH12–CH13 complete ComicPanelPlan authoring r1", "", "The final required Bell Road batch adds 80 unique chronological plans and completes the first eight-chapter arc before any render promotion.", "", "| Chapter | Panels | Sequences | Opening | Closing |", "| --- | ---: | ---: | --- | --- |", *[f"| {chapter} — {plan['chapter_title']} | 40 | 8 | {plan['opening_state']} | {plan['closing_changed_state']} |" for chapter, plan in plans.items()], "", "CH12 turns hidden route evidence into a consequential strategic rupture, physically damages both signature garments, fuses the brass key into Warden's Reach, reveals the last keeper's transformation, and restores the bond only through negotiated intent. CH13 resolves the Crownroot conflict through route, water, tension, and shared consent; co-keeper leadership changes the one-sacrifice system without erasing injury, faction cost, or prior consequences.", "", "All 16 sequences are contiguous five-panel units with exact CH11→CH12→CH13 carry, adult-only roles, fixed hair anchors, evolved practical gear, physical-surface Ledger effects, protected lettering, and literal causal action.", "", "ADR-0204 accepts this rupture-and-co-keeper authoring batch only. Prompt/render promotion remains a separate future gate.", "", "No prompt, provider call, upload, image, generated candidate, acceptance, commercial decision, exact-base decision, AnimationShotPlan, or E-Conte record is created.", ""])


def adr_markdown() -> str:
    return "\n".join(["# ADR-0204: Author CH12 and CH13 as one rupture-and-co-keeper continuity batch", "", "## Status", "", "Accepted for provisional canon-development authoring only.", "", "## Context", "", "CH11 ends with formal classes, public co-leadership, damaged Brackenwake orchards, persistent adult injuries, and Tamsin's disclosure of the sealed North Garden. The final required batch must test the partnership before resolving the one-keeper system without resetting those consequences.", "", "## Decision", "", "1. Author CH12–CH13 as one 80-panel, 16-sequence ComicPanelPlan batch with exact CH11→CH12→CH13 continuity.", "2. Make the strategic rupture consequential and resolve it through negotiated intent and complementary action rather than instant forgiveness.", "3. Reveal route falsification and keeper transformation through physical maps, cairns, camp records, scars, and gate mechanisms.", "4. Preserve adult-only identity, fixed hair, persistent injuries, and irreversible signature-garment changes through the climax.", "5. Resolve Crownroot through water, tension, structure, route work, and explicit shared consent; no unexplained power spectacle or kill-point progression.", "6. Keep every Ledger manifestation on physical brass, iron, stone, water, glass, tools, or condensation and keep execution authority separate.", "", "## Consequences", "", "The required eight-chapter Bell Road arc ends with earned co-keepers, a recoverable sanctuary, visible faction and monster consequences, durable conflict rules, and a wider failing network for the next arc.", "", "This ADR grants no prompt, provider, upload, paid API, cloud GPU, model, ingestion, rendering, acceptance, commercial, rights, exact-production-base, AnimationShotPlan, or E-Conte authority.", ""])


def main() -> int:
    verify_sources()
    arc_doc = json.loads(ARC_PATH.read_text(encoding="utf-8")); chapters = {row["chapter_id"]: row for row in arc_doc["chapters"]}
    ch11 = json.loads(CH11_PATH.read_text(encoding="utf-8")); plans: dict[str, dict[str, Any]] = {}
    plans["CH12"] = build_chapter("CH12", chapters["CH12"], ch11["continuity_contract"]["final_state"])
    plans["CH13"] = build_chapter("CH13", chapters["CH13"], plans["CH12"]["continuity_contract"]["final_state"])
    for chapter in ("CH12", "CH13"):
        for path, payload in ((OUTPUTS[chapter], plans[chapter]), (STORY_OUTPUTS[chapter], story_state(chapter, chapters[chapter], plans[chapter])), (BEAT_OUTPUTS[chapter], scene_beat(chapter, chapters[chapter]))):
            path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    MARKDOWN_OUTPUT.parent.mkdir(parents=True, exist_ok=True); MARKDOWN_OUTPUT.write_text(authoring_markdown(plans), encoding="utf-8", newline="\n")
    ADR_OUTPUT.parent.mkdir(parents=True, exist_ok=True); ADR_OUTPUT.write_text(adr_markdown(), encoding="utf-8", newline="\n")
    paths = [*OUTPUTS.values(), *STORY_OUTPUTS.values(), *BEAT_OUTPUTS.values(), MARKDOWN_OUTPUT, ADR_OUTPUT]
    print(json.dumps({"chapters": 2, "panels": 80, "sequences": 16, "files": 8, "hashes": {path.relative_to(ROOT).as_posix(): sha256(path) for path in paths}, "activity": {"pixels": 0, "provider_calls": 0, "uploads": 0, "spend_usd": 0.0}}, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
