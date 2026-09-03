"""Compile the CH10-CH11 faction-and-siege ComicPanelPlan batch."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = ROOT / "production/canon/story-arcs/north-garden-ch06-ch13-progression-r1.json"
CONTRACT_PATH = ROOT / "production/comic/contracts/complete-chapter-comicpanelplan-authoring-contract-r1.json"
CH09_PATH = ROOT / "production/comic/ch09-sc01-panel-plans-r1.json"
BOUND_HASHES = {
    ARC_PATH: "04d0933b07cfc2c11d15c05ebabc1d6695b0ed73ca328fc1659e53f33f107539",
    CONTRACT_PATH: "e112fcd5d2b450746a6a6ad827ba6dff4ff77a0bf10c212f4718a334dc3e9d4e",
    CH09_PATH: "4a86ffc8b2d9517477168040391cecc971b4f57f117a42fbcabaf71fe893d743",
}
OUTPUTS = {chapter: ROOT / f"production/comic/{chapter.lower()}-sc01-panel-plans-r1.json" for chapter in ("CH10", "CH11")}
STORY_OUTPUTS = {chapter: ROOT / f"production/canon/story-state/{chapter.lower()}-sc01-r1.json" for chapter in ("CH10", "CH11")}
BEAT_OUTPUTS = {
    "CH10": ROOT / "production/scene-beats/ch10-sc01-iron-name-r1.json",
    "CH11": ROOT / "production/scene-beats/ch11-sc01-orchard-siege-r1.json",
}
MARKDOWN_OUTPUT = ROOT / "docs/research/ch10-ch11-comicpanelplan-authoring-r1.md"
ADR_OUTPUT = ROOT / "docs/adr/ADR-0202-author-ch10-ch11-as-faction-and-siege-continuity-batch.md"

PHASE_FUNCTIONS = {
    "phase01": "opening_state_and_orientation", "phase02": "movement_and_escalation",
    "phase03": "threshold_and_entry", "phase04": "causal_interaction_and_evidence",
    "phase05": "deduction_choice_and_consequence", "phase06": "reversal_return_or_closure",
}
SEQUENCES = {
    "CH10": [
        ("s01-brackenwake-gate", "The forge without breath", "phase01"),
        ("s02-price-of-entry", "Iron, medicine, and the key", "phase02"),
        ("s03-failed-bellows", "Diagnose the silent forge", "phase02"),
        ("s04-seated-repair", "Work around the injury", "phase03"),
        ("s05-map-hearing", "Prove who turned the plate", "phase04"),
        ("s06-iron-for-names", "Forge practical reach", "phase04"),
        ("s07-compact-bargain", "Terms before trust", "phase05"),
        ("s08-all-wards-flare", "The terraces answer", "phase06"),
    ],
    "CH11": [
        ("s01-siege-alarm", "All orchards flare", "phase01"),
        ("s02-adult-defense", "Route the defenders", "phase02"),
        ("s03-terrace-contact", "Three rising fronts", "phase02"),
        ("s04-water-firebreak", "Yield ground deliberately", "phase03"),
        ("s05-sequential-gates", "A warden who cannot run", "phase04"),
        ("s06-opposite-heights", "Expose the brood root", "phase04"),
        ("s07-two-hands", "Let the settlement strike", "phase05"),
        ("s08-cost-and-map", "What survival costs", "phase06"),
    ],
}


def B(narrative: str, composition: str, cast: list[str], assets: list[str], scale: str,
      density: str, motion: str, updates: dict[str, dict[str, list[str]]] | None = None) -> dict[str, Any]:
    return {"narrative": narrative, "composition": composition, "cast": cast, "assets": assets,
            "scale": scale, "density": density, "motion": motion, "updates": updates or {}}


S, G, T, K, W = "ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE", "ADULT_HALVOR_KEST", "ADULT_BRIAR_COMPACT_WORKER"
SG, SGK, SGKW = [S, G], [S, G, K], [S, G, K, W]

# Forty beats per chapter are declared below. Each state update persists through the generated continuity graph.
CH10_BEATS: list[dict[str, Any]] = [
    B("Before dawn Sigrid leads from the Black Weir with the reversed bronze plate while Soren follows on a shortened left-leg stride, using damaged Warden's Reach only for balance.", "wide north-bank departure with leadership order, visible brace, plate, and uphill route", SG, ["ng-prop-reversed-map-plate-r1", "ng-prop-rigid-weir-leg-brace-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "injured_departure"),
    B("When the iron splint chafes, Sigrid stops and re-pads rather than heals Soren's swollen lower leg while he sits on a route milestone.", "medium first-aid action preserving face, padding hands, brace, and swollen leg", SG, ["ng-prop-gate-iron-leg-brace-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "brace_repadding", {"clues": {"add": ["soren_injury_requires_repadding_and_reduced_pace"]}}),
    B("The dawn quarry road reveals lit Brackenwake above and dark outer cottages below as haul ruts confirm Sigrid's route across real wet stone.", "wide climb with lit center, dark outer nodes, haul ruts, and two evolved silhouettes", SG, ["ng-set-brackenwake-quarry-road-r1", "ng-progression-ui-wayfinder-route-line-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "route_climb", {"locations": {"set": ["farmhouse_boundary_node_tamsin_rear_guard", "brackenwake_quarry_road_day_three"]}, "weather": {"set": ["cold_misted_day_three_dawn"]}, "clues": {"add": ["brackenwake_center_lit_while_outer_nodes_dark"]}}),
    B("Sigrid compares the thorn-and-hammer seal on the reversed plate with the identical stamp cut into a real quarry toll weight.", "quiet physical-evidence insert with bronze seal, iron weight, and adult hand", [G], ["ng-prop-reversed-map-plate-r1", "ng-clue-brackenwake-toll-seal-r1"], "MEDIUM_CHARACTER_CLUE", "LOW", "evidence_comparison", {"clues": {"add": ["brackenwake_seal_matches_quarry_authority"]}}),
    B("Halvor Kest and adult Compact workers close the iron gate; he recognizes plate and key while Sigrid holds the lead and Soren visibly unloads his injured leg.", "wide gate interception with Halvor's quarry armor, adult workers, and injured stance", SGKW, ["ng-set-brackenwake-gate-r1", "ng-faction-briar-compact-adults-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "gate_intercept", {"characters": {"add": [K, W]}, "locations": {"set": ["farmhouse_boundary_node_tamsin_rear_guard", "brackenwake_quarry_gate_day_three"]}, "clues": {"add": ["halvor_kest_recognizes_plate_and_key"]}}),

    B("A silent iron tally shows the central gate ward burning steady while scratched outer-node markers remain dark beneath Halvor's seal.", "small ward tally insert with physical contrast and no people", [], ["ng-clue-brackenwake-ward-tally-r1"], "SMALL_OBJECT_INSERT", "LOW", "ward_contrast", {"clues": {"add": ["iron_tally_records_dark_outer_nodes"]}}),
    B("Sigrid presents scrape arcs and the matched seal; Halvor admits the office mark but calls the reroute necessary defense without admitting authorship.", "medium confrontation with plate centered and faces separated by evidence", [G, K], ["ng-prop-reversed-map-plate-r1"], "MEDIUM_TWO_SHOT", "LOW", "accusation_and_defense"),
    B("Soren attempts the gate stair, his left knee buckles against the crude brace, and he catches the rail before Halvor calls an adult medic.", "tall injury consequence showing stair, buckling knee, rail catch, and adult reactions", [S, K, W], ["ng-set-brackenwake-gate-r1", "ng-prop-gate-iron-leg-brace-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "injury_buckle", {"clues": {"add": ["soren_cannot_climb_gate_stairs_unassisted"]}}),
    B("Halvor offers medicine, forge iron, and entry for the brass key; Sigrid refuses while Soren proposes paying through measured repair work.", "balanced bargaining three-shot with key retained in Sigrid's open hand", SGK, ["ng-prop-brass-boundary-key-r1", "ng-prop-medicine-case-r1"], "MEDIUM_TWO_SHOT", "LOW", "conditional_bargain", {"clues": {"add": ["key_for_entry_demand_refused", "repair_for_terms_counteroffer"]}}),
    B("The forge bellows coughs out of rhythm, gate light dips, and hammer crews stop as seated Soren identifies a counterweight double-strike by sound.", "wide gate-to-forge causal chain with bellows, light, workers, and listening adult", [S, G, K, W], ["ng-set-brackenwake-forge-r1", "ng-clue-bellows-double-strike-r1"], "WIDE_ENVIRONMENTAL_MOTION", "MEDIUM", "mechanical_stall", {"clues": {"add": ["forge_counterweight_double_strike_diagnosed_by_sound", "provisional_forge_access_earned"]}}),

    B("Halvor unlocks a narrow service gate; Sigrid crosses first to hold the route while Soren climbs one rail-assisted step at a time.", "tall guarded threshold with role order, handrail, brace, and gate geometry", SGK, ["ng-set-brackenwake-service-gate-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "guarded_threshold", {"locations": {"set": ["farmhouse_boundary_node_tamsin_rear_guard", "brackenwake_forge_service_entry"]}}),
    B("The forge and council yard open beyond: adult workers drive bellows linked to a ward engine whose central pipe glows while outbound branches stay dark.", "wide industrial reveal with workers, bellows, engine, and branch pipes", [S, G, K, W], ["ng-set-brackenwake-forge-r1", "ng-faction-briar-compact-adults-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "forge_reveal"),
    B("An adult medic checks circulation and rewraps the existing gate-iron brace, leaving Soren's pain and speed limitation visibly unresolved.", "medium medical triage with adult medic role, fingers, brace, and face clear", [S, W], ["ng-prop-gate-iron-leg-brace-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "medical_triage", {"clues": {"add": ["existing_brace_rewrapped_not_healed"]}}),
    B("Seated beside the bellows, Soren chalks two stroke endpoints and watches one chain land short while cracked counterweight chips jump on return.", "small mechanical diagnostic with chalk marks, chain endpoints, and stone chips", [S], ["ng-clue-cracked-counterweight-r1"], "MEDIUM_SINGLE_CAUSAL", "LOW", "counterweight_misfire", {"clues": {"add": ["broken_counterweight_shortens_every_second_stroke"]}}),
    B("After the measured test, frost-green letters condense on the real brass engine gauge—DRAFT LOST / OUTER DRAW ACTIVE—then fade.", "silent physical brass-gauge inscription with condensation and no floating interface", [], ["ng-progression-ui-forge-bargain-inscription-r1"], "SMALL_OBJECT_INSERT", "LOW", "physical_inscription", {"clues": {"add": ["ledger_confirms_draft_loss_and_outer_draw"]}}),

    B("Soren remains seated and uses recovered boundary wire as a removable chain-travel gauge, proving the broken weight starves alternate strokes.", "medium seated diagnosis with wire gauge, chain travel, brace, and important hands", [S], ["ng-prop-boundary-wire-coil-r1", "ng-set-brackenwake-forge-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "seated_diagnosis"),
    B("A stress line appears only in damp forge-floor scale; Sigrid verifies it with soot drift and gutter flow before naming the overfed central branch.", "medium Wayfinder evidence panel with real damp floor, soot, water, and tied dark hair", [G], ["ng-progression-class-sigrid-wayfinder-r1", "ng-progression-ui-wayfinder-route-line-r1"], "MEDIUM_CHARACTER_CLUE", "LOW", "surface_route_check", {"clues": {"add": ["forge_center_overfed_while_outer_branches_starve"]}}),
    B("Counterweight fragments fit a quarry-cut void while an iron collar template proves compression repair can reuse the stone rather than conjure a replacement.", "small object study with matched fractures, collar measure, and chalk dimensions", [], ["ng-clue-counterweight-fracture-fit-r1"], "SMALL_OBJECT_INSERT", "LOW", "fracture_fit", {"clues": {"add": ["counterweight_repair_requires_compression_collar"]}}),
    B("Sigrid routes adult workers moving a replacement block on rollers and diverts them around the weak floor seam before the load reaches it.", "wide causal haul with rollers, route signal, weak seam, and adult weight shifts", [G, W], ["ng-faction-briar-compact-adults-r1", "ng-set-brackenwake-forge-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "haul_with_rollers", {"clues": {"add": ["sigrid_routes_quarry_load_around_weak_floor"]}}),
    B("Seated Soren holds the collar jig and calls quarter turns while Halvor strikes heated iron at the forgekeeper's anvil, closing it around the measured template.", "dual-causal forge action with jig, hammer arc, hot collar, and brace clear", [S, K, W], ["ng-set-brackenwake-forge-r1", "ng-faction-briar-compact-adults-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "forge_cadence", {"clues": {"add": ["soren_halvor_rival_cooperation_at_anvil"]}}),

    B("Anchored from the bench, Soren uses damaged Warden's Reach as a lever instead of leg support and ratchets the collared weight into its cradle.", "low seated leverage with bench anchor, ratchet, tool, brace, and chain", [S], ["ng-prop-damaged-system-recognized-wardens-reach-r1"], "MEDIUM_SINGLE_CAUSAL", "HIGH", "seated_ratcheting"),
    B("Sigrid plumbs the chain with recovered wire, Halvor takes the haul line, and Soren calls the stop so three adult roles align the weight.", "wide three-role alignment with plumb wire, haul rope, and protected hands", SGK, ["ng-prop-boundary-wire-coil-r1", "ng-set-brackenwake-forge-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "alignment_teamwork"),
    B("One synchronized cycle drops the weight, fills the bellows, lifts forge flame, steadies the central ward, and returns faint flow to one outer branch.", "wide mechanical sequence frozen at linked causes from stone to distant pipe", [S, G, K, W], ["ng-set-brackenwake-forge-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "engine_restart", {"clues": {"add": ["forge_engine_repaired", "first_outer_branch_flow_partially_restored"]}}),
    B("Only after successful service, frost-green letters appear across the real anvil face—SERVICE SHARED / IRON CLAIM EARNED—and cool away.", "small hot-iron anvil inscription on a physical tool surface", [], ["ng-progression-ui-forge-bargain-inscription-r1"], "SMALL_OBJECT_INSERT", "LOW", "physical_inscription", {"clues": {"add": ["ledger_records_shared_service_and_earned_iron_claim"]}}),
    B("Before adult witnesses Sigrid names the exchange: repaired engine for medicine, gear, map truth, passage, and key retention; Halvor accepts without touching brass.", "medium witnessed terms with both faces, key, repaired engine, and workers behind", [G, K, W], ["ng-prop-brass-boundary-key-r1", "ng-set-brackenwake-forge-r1"], "MEDIUM_TWO_SHOT", "LOW", "terms_declared", {"clues": {"add": ["witnessed_repair_bargain_terms_declared"]}}),

    B("The medic removes the crude splints and fits a padded rigid quarry brace; Soren bears controlled partial weight but still cannot run or take stairs.", "medium brace fitting with straps, swelling, oatmeal hem, and adult hands", [S, W], ["ng-prop-rigid-brackenwake-leg-brace-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "rigid_brace_fitting", {"injuries": {"remove": ["soren_left_lower_leg_crush_sprain_braced"], "add": ["soren_left_lower_leg_crush_sprain_rigid_brace_movement_limited"]}, "props": {"remove": ["gate_iron_lower_leg_brace"], "add": ["rigid_brackenwake_lower_leg_brace"]}, "clues": {"add": ["rigid_brace_allows_partial_weight_not_running"]}}),
    B("The forgekeeper drives a socket over Warden's Reach's split shaft and pins a new hook while seated Soren keeps the damaged grain aligned.", "tight tool repair with socket, pin, split wood, hammer, and steadying hands", [S, W], ["ng-progression-weapon-wardens-reach-forged-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "tool_socketing", {"props": {"remove": ["damaged_system_recognized_wardens_reach"], "add": ["forged_socket_and_hook_wardens_reach"]}, "clues": {"add": ["wardens_reach_forged_socket_and_hook_earned"]}}),
    B("Sigrid checks her own compact bow's draw and utility seax sheath while Tamsin's loan bow remains wrapped and labeled for return.", "medium gear check with two distinct bows, seax lock, plaid cape, and clear hands", [G], ["ng-progression-weapon-sigrid-compact-bow-r1", "ng-progression-weapon-sigrid-utility-seax-r1"], "MEDIUM_CHARACTER_CLUE", "MEDIUM", "owned_gear_check", {"props": {"add": ["sigrid_owned_compact_bow", "sigrid_utility_seax"]}, "clues": {"add": ["sigrid_owns_bow_and_seax", "tamsin_loan_bow_retained_for_return"]}}),
    B("Removable leather and iron guards buckle over—not instead of—the oatmeal quilted coat and plaid cape; both adults test full tool and bow motion.", "balanced armor fit with signature cloth, buckles, tool grip, bow draw, and fixed hair", SG, ["ng-progression-armor-soren-quarry-leather-r1", "ng-progression-armor-sigrid-quarry-leather-r1", "ng-progression-clothing-soren-quilted-coat-r1", "ng-progression-clothing-sigrid-weather-cape-r1"], "MEDIUM_TWO_SHOT", "MEDIUM", "armor_fit_test", {"wardrobe": {"set": ["soren_oatmeal_coat_quilted_shoulders_repaired_with_removable_leather_iron_guards", "sigrid_plaid_weather_cape_secured_scorched_edge_with_removable_leather_iron_guards"]}, "clues": {"add": ["work_derived_quarry_armor_fitted_without_erasing_signatures"]}}),
    B("Sigrid carries the plate toward council while Soren follows brace-limited on the forged tool and Halvor walks opposite them toward the same hearing.", "wide evidence procession with unresolved sides and common council destination", SGK, ["ng-prop-reversed-map-plate-r1", "ng-progression-weapon-wardens-reach-forged-r1"], "WIDE_DIRECTIONAL_ANCHOR", "MEDIUM", "evidence_procession", {"locations": {"set": ["farmhouse_boundary_node_tamsin_rear_guard", "brackenwake_council_yard"]}}),

    B("Scrape arcs, old mineral silhouette, stamped seal, and bolt wear on the plate demonstrate a recent deliberate reversal under Brackenwake authority.", "small forensic layout with four physical evidence types and no people", [], ["ng-prop-reversed-map-plate-r1", "ng-clue-map-plate-sabotage-r1"], "SMALL_OBJECT_INSERT", "LOW", "forensic_orientation"),
    B("Sigrid's Wayfinder trace appears only in rainwater on real drainage stones; she verifies it with quarry dust and gutter fall before marking direction.", "medium physical route verification with wet stones, dust, gutter, and adult hand", [G], ["ng-progression-class-sigrid-wayfinder-r1", "ng-progression-ui-wayfinder-route-line-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "route_verification"),
    B("The plate, iron ward tally, and real branch pipes align to prove several outer-node feeds were diverted into Brackenwake's center.", "wide network reconstruction across council table and visible pipe yard", [G, K, W], ["ng-prop-reversed-map-plate-r1", "ng-clue-brackenwake-ward-tally-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "network_reconstruction", {"clues": {"add": ["compact_diverted_outer_nodes_to_brackenwake_center"]}}),
    B("Before adult council workers, Halvor admits ordering the reversal to buy winter light; the motive is protective and the concealed cost remains unacceptable.", "medium public confession with Halvor, adult witnesses, and evidence unobscured", [G, K, W], ["ng-faction-briar-compact-adults-r1"], "MEDIUM_SENSORY_REACTION", "MEDIUM", "public_confession", {"clues": {"add": ["halvor_admits_outer_node_sacrifice_for_winter_light"]}}),
    B("In a private aside Soren acknowledges emergency load shedding while Sigrid rejects secret sacrifice; they unite on warning and consent for isolated adults.", "quiet two-shot with readable disagreement, brace, and shared public demand", SG, ["ng-set-brackenwake-council-yard-r1"], "MEDIUM_TWO_SHOT", "LOW", "private_disagreement_united_front", {"clues": {"add": ["pair_disagree_privately_but_bargain_publicly_as_one", "no_isolated_adults_abandoned_without_warning_or_consent"]}}),

    B("The adult council accepts iron, medicine, exposed maps, outer warnings, and passage while the pair retains key and plate and commits to node repair.", "wide public bargain tableau with adult council, retained objects, and repaired forge", SGKW, ["ng-faction-briar-compact-adults-r1", "ng-prop-brass-boundary-key-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "public_bargain", {"props": {"add": ["iron_service_tally"]}, "clues": {"add": ["briar_compact_bargain_struck", "mission_expands_to_prevent_abandonment"]}}),
    B("Halvor stamps the accord into a real iron service tally beside the repaired engine while the brass key remains separate in Sigrid's hand.", "small physical tally stamping with stamp, iron, key separation, and no HUD", [G, K], ["ng-progression-ui-forge-bargain-inscription-r1", "ng-prop-iron-service-tally-r1"], "SMALL_OBJECT_INSERT", "LOW", "terms_stamped"),
    B("Halvor returns the plate and names the abandoned route; Sigrid accepts information rather than absolution while Soren stands on brace and forged tool.", "medium rival alignment with plate handoff, firm faces, brace, and tool", SGK, ["ng-prop-reversed-map-plate-r1", "ng-progression-weapon-wardens-reach-forged-r1"], "MEDIUM_TWO_SHOT", "LOW", "rival_alignment", {"clues": {"add": ["halvor_kest_rival_not_yet_enemy"]}}),
    B("An adult Compact cart brings Tamsin from the farmhouse under the bargain's medicine clause, her injured leg supported and route notes intact.", "wide adult-only cart arrival with Tamsin seated, medic, farmhouse supplies, and council gate", [T, W, G], ["ng-identity-tamsin-fictional-adult-r1", "ng-prop-damaged-node-map-r1"], "WIDE_DIRECTIONAL_ANCHOR", "MEDIUM", "supported_transport", {"locations": {"set": ["brackenwake_forge_and_council_yard"]}, "clues": {"add": ["tamsin_transported_to_brackenwake_under_medicine_clause"]}}),
    B("Every brass orchard ward cap flares frost-green at once, drainage water reverses, and packed terrace soil domes as adult workers pull back.", "wide cliffhanger mechanics with ward caps, water reversal, rising soil, and retreat", [S, G, T, K, W], ["ng-progression-ui-orchard-alarm-r1", "ng-progression-monster-mireback-r1", "ng-set-brackenwake-orchards-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "terrace_rising", {"weather": {"set": ["cold_clear_day_three_evening"]}, "clues": {"add": ["all_brackenwake_orchard_wards_flare", "mirebacks_rise_from_drainage_terraces"]}}),
]
CH11_BEATS: list[dict[str, Any]] = [
    B("Before dawn every orchard ward flares on real stone while Mirebacks rise through terraced drains between the forge, granary, lower homes, and retreat heights.", "wide settlement geography with multiple physical threats and adult retreat vectors", [S, G, T, K, W], ["ng-progression-ui-orchard-alarm-r1", "ng-progression-monster-mireback-r1", "ng-set-brackenwake-orchards-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "flare_and_emergence", {"locations": {"set": ["brackenwake_terraced_orchards_predawn"]}, "weather": {"set": ["cold_day_four_predawn"]}, "clues": {"add": ["orchard_siege_begins_on_multiple_terraces"]}}),
    B("Peat rootlets drink frost-green light directly from a cracked irrigation seam, proving the attackers still feed on defended ground.", "small physical root, wardstone, water, and light transfer insert without people", [], ["ng-progression-monster-mireback-r1", "ng-progression-ui-orchard-alarm-r1"], "SMALL_OBJECT_INSERT", "LOW", "capillary_draw", {"clues": {"add": ["siege_mirebacks_draw_light_through_irrigation_seams"]}}),
    B("Halvor orders quarry-armored adults to contract around forge and granary, visibly leaving lower-terrace crews outside his line.", "medium command group with Halvor, adult workers, protected faces, and abandoned lower lane", [K, W], ["ng-faction-briar-compact-adults-r1"], "MEDIUM_TWO_SHOT", "MEDIUM", "conflicting_order", {"clues": {"add": ["kest_withdrawal_order_abandons_lower_terrace_crews"]}}),
    B("From the council stair Sigrid compares real water flow, terrace walls, and frost lines on wet stone to find the stranded adults' only uphill route.", "tall route-reading anchor with dark tied hair, walls, water, and lower adults", [G, W], ["ng-progression-class-sigrid-thornpath-wayfinder-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "evidence_scan", {"clues": {"add": ["sigrid_identifies_lower_crew_escape_route"]}}),
    B("Unable to descend quickly, Soren locks his rigid brace, plants forged Warden's Reach, and identifies three linked irrigation gates as sequential thresholds.", "medium causal mechanism read with brace lock, tool, numbered gates, and no implied sprint", [S], ["ng-progression-weapon-wardens-reach-forged-r1", "ng-prop-rigid-brackenwake-leg-brace-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "brace_lock_and_mechanism_read", {"clues": {"add": ["three_irrigation_gates_can_sequence_defense"]}}),

    B("Sigrid chalks adult-only evacuation, bow-sight, and gate-crew lanes onto a real council map before any ally-visible route ability exists.", "wide planning table with three distinct physical lanes and adult hands", [G, K, W], ["ng-prop-brackenwake-defense-map-r1"], "WIDE_DIRECTIONAL_ANCHOR", "MEDIUM", "route_drafting", {"props": {"add": ["brackenwake_defense_map"]}}),
    B("Soren numbers three releases on the brass manifold and assigns adult crews to ropes, wedges, and warning bells from his fixed wall position.", "medium mechanical assignment with brass numbers, ropes, brace, and adult crews", [S, W], ["ng-set-brackenwake-irrigation-manifold-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "crew_assignment"),
    B("Halvor blocks the reservoir valve with his marshal seal, arguing outer water must remain reserved for the inner ward.", "quiet confrontation at physical valve with seal between Halvor and Sigrid", [G, K], ["ng-prop-halvor-marshal-seal-r1"], "MEDIUM_TWO_SHOT", "LOW", "seal_interception"),
    B("A Mireback-driven wall crack isolates an adult orchard crew and sends soil sliding toward winter stores, making withdrawal immediately untenable.", "wide retaining-wall shear with stranded adults, moving soil, creature weight, and stores", [G, K, W], ["ng-progression-monster-mireback-r1", "ng-set-brackenwake-orchards-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "wall_shear", {"clues": {"add": ["mireback_wall_shear_threatens_adults_and_winter_stores"]}}),
    B("Before crossing the orchard threshold Soren declares he will hold the wall, Sigrid declares she will keep a road, adult captains assent, and Halvor releases the valve as DEFENDERS DECLARED briefly forms on its real brass manifold.", "wide ensemble declaration with physical brass valve inscription, role order, and protected speech space", [S, G, K, W], ["ng-progression-ui-defenders-declared-r1", "ng-set-brackenwake-irrigation-manifold-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "declared_complementary_plan", {"clues": {"add": ["adult_defense_roles_publicly_declared_and_assented"]}}),

    B("Sigrid climbs the first retaining stair, cuts only a snagged gate chain with her seax, and lays bright lime arrows on stone for following adults.", "tall climb with seax cut, lime marks, secured plaid cape, and fixed dark hair", [G, W], ["ng-progression-weapon-sigrid-utility-seax-r1", "ng-prop-lime-route-marks-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "climb_and_mark", {"props": {"add": ["lime_route_markers"]}}),
    B("She shoots a support cord so empty harvest baskets fall as a noise decoy, turning one Mireback away from the evacuation lane.", "wide causal action linking arrow, severed cord, falling baskets, sound, and creature turn", [G, W], ["ng-progression-weapon-sigrid-compact-bow-r1", "ng-progression-monster-mireback-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "cord_sever_and_load_fall", {"props": {"remove": ["two_arrows"], "add": ["one_arrow_remaining"]}, "clues": {"add": ["basket_noise_decoy_turns_mireback_from_escape_lane"]}}),
    B("Halvor's straight-moving forge cohort exposes its flank when another Mireback pivots through an espalier gap.", "medium action reversal with shield line, gap, creature turn, and adult flank", [K, W], ["ng-progression-monster-mireback-r1", "ng-faction-briar-compact-adults-r1"], "MEDIUM_SENSORY_REACTION", "MEDIUM", "flank_reversal"),
    B("Sigrid calls a sharp switchback; Halvor visibly chooses to obey and moves his adults behind a wall before the creature strikes.", "medium command acceptance with Sigrid above, Halvor turning line, and wall cover", [G, K, W], ["ng-prop-lime-route-marks-r1"], "MEDIUM_TWO_SHOT", "MEDIUM", "command_accepted", {"clues": {"add": ["kest_accepts_sigrid_route_command_under_attack"]}}),
    B("The isolated orchard crew reaches the forge along physical lime marks while Sigrid remains last through the lane, establishing public route leadership.", "wide protected withdrawal with adult crew order, lime line, and Sigrid rear position", [G, W], ["ng-prop-lime-route-marks-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "protected_withdrawal", {"clues": {"add": ["sigrid_publicly_leads_adult_escape_route"]}}),

    B("From the central wall Soren aligns gate crews, rope angles, Mireback positions, and terrace slopes into one readable numbered mechanism.", "wide mechanical defense diagram embodied by real gates, ropes, people, and terrain", [S, K, W], ["ng-set-brackenwake-irrigation-manifold-r1", "ng-progression-monster-mireback-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "load_mapping"),
    B("Gate One releases a shallow water sheet that draws a lesser Mireback onto the saturated upper bed exactly as declared.", "wide water release with gate motion, flow path, creature footing, and crew rope", [S, W], ["ng-progression-monster-mireback-r1", "ng-set-brackenwake-irrigation-manifold-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "controlled_release"),
    B("At Gate Two Soren's injured leg buckles under lever recoil; an adult worker catches the beam while he shifts to seated leverage.", "medium injury consequence with recoil, brace, collective catch, and safe hand geometry", [S, W], ["ng-prop-rigid-brackenwake-leg-brace-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "recoil_and_collective_catch", {"clues": {"add": ["soren_moves_to_seated_gate_control_after_brace_buckle"]}}),
    B("The forged hook seats in the ratchet, allowing Soren to multiply the crew's pull without pretending his mobility has returned.", "tight hook-and-ratchet leverage with seated adult, brace, rope, and gear teeth", [S, W], ["ng-progression-weapon-wardens-reach-forged-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "hook_and_ratchet_leverage"),
    B("Gate Three shears the mud bank beneath two Mirebacks while adult crews pin exposed root-knots with ropes and pruning hooks.", "wide action anchor with sequential water, collapsing mud, rooted creatures, and adult tools", [S, W], ["ng-progression-monster-mireback-r1", "ng-set-brackenwake-orchards-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "sequential_mud_collapse", {"clues": {"add": ["three_gate_sequence_exposes_lesser_root_knots"]}}),

    B("The apparent victory ruptures when a brood Mireback rises beneath the root cellar, its peat-and-slate mass physically joined to several orchard wardstones.", "large creature reveal with root cellar, connected stones, adult scale, and food stores", [S, G, K, W], ["ng-progression-monster-brood-mireback-r1", "ng-set-brackenwake-root-cellar-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "subsurface_heave", {"clues": {"add": ["brood_mireback_joined_to_multiple_wardstones"]}}),
    B("Living feeder roots bridge earlier mud traps and pull ward light through trellis anchors into the brood's slate armor.", "small physical root, trellis wire, wardstone, and armor-transfer evidence", [], ["ng-progression-monster-brood-mireback-r1", "ng-progression-ui-orchard-alarm-r1"], "SMALL_OBJECT_INSERT", "LOW", "root_bridge_and_light_draw", {"clues": {"add": ["brood_feeder_roots_bridge_traps_and_draw_ward_light"]}}),
    B("A root lash tears through apple bins and collapses a store wall, spilling winter food while blocking Sigrid's first safe lane.", "wide consequence with root impact, collapsing masonry, rolling apples, and blocked route", [G, W], ["ng-progression-monster-brood-mireback-r1", "ng-set-brackenwake-winter-stores-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "impact_and_spill", {"clues": {"add": ["winter_food_and_store_wall_damaged"]}}),
    B("Halvor orders pitch fire; Sigrid holds an ash ribbon into the uphill draft and proves flame would run toward granary and sheltered adults.", "medium physical wind test with ash ribbon, fire vessel, granary vector, and adult faces", [G, K, W], ["ng-clue-ash-wind-test-r1"], "MEDIUM_CHARACTER_CLUE", "LOW", "wind_test", {"clues": {"add": ["pitch_fire_rejected_because_draft_threatens_granary"]}}),
    B("Halvor powers the inner wardstone instead; the brood thickens its slate armor as the forge roof dims, forcing him to accept the physical feed relationship.", "wide causal reveal linking real wardstone valve, dim roof, root glow, and thickening creature armor", [G, K, W], ["ng-progression-monster-brood-mireback-r1", "ng-progression-ui-orchard-alarm-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "power_transfer", {"clues": {"add": ["concentrated_inner_ward_power_feeds_brood_armor"]}}),

    B("Sigrid reaches the forge roof and traces pulses across wet slate, gutters, trellis wire, and wardstones to identify the brood's three physical feed lines.", "tall elevated evidence map with real wet surfaces, fixed hair, and three route vectors", [G], ["ng-progression-class-sigrid-thornpath-wayfinder-r1", "ng-progression-monster-brood-mireback-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "elevated_route_tracing", {"clues": {"add": ["sigrid_identifies_three_brood_feed_lines"]}}),
    B("Soren mechanically anchors Warden's Reach and the brass key into the central valve threshold while adult crews brace the shaft and his injured leg stays unloaded.", "medium threshold anchoring with key, forged socket, crew hands, seated brace-safe posture", [S, W], ["ng-progression-weapon-wardens-reach-forged-r1", "ng-prop-brass-boundary-key-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "threshold_anchoring"),
    B("Across opposite heights Sigrid declares she will mark what feeds it, Soren declares he will close it, and adult crews acknowledge both before moving.", "wide split-elevation declaration with roof, valve, adults, and protected lettering fields", [S, G, K, W], ["ng-faction-briar-compact-adults-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "complementary_declaration", {"clues": {"add": ["opposite_height_roles_declared_and_acknowledged"]}}),
    B("In Sigrid's called order, adult arrows and her seax sever trellis-bound feed lines while crews below pull the marked dead vines clear.", "tall ordered severance with bow teams, seax cut, falling vines, and clear hand safety", [G, W], ["ng-progression-weapon-sigrid-utility-seax-r1", "ng-progression-weapon-sigrid-compact-bow-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "ordered_severance"),
    B("Soren reverses the gate sequence; crew counterweight and water pressure peel peat from the disconnected brood as the physical key socket records THRESHOLD HELD.", "wide reverse-release action with water, counterweight, peeling peat, and brass inscription", [S, W], ["ng-progression-monster-brood-mireback-r1", "ng-progression-ui-defenders-declared-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "reverse_release", {"clues": {"add": ["reversed_gate_sequence_strips_disconnected_brood_armor", "physical_key_socket_records_threshold_held"]}}),

    B("The exposed brood climbs the central wall toward movement-limited Soren, and Halvor braces the gate beside him with a quarry shield instead of reclaiming command.", "medium high-threat partnership with wall climb, seated Soren, shield, and clear tool lines", [S, K], ["ng-progression-monster-brood-mireback-r1", "ng-progression-armor-soren-quarry-leather-r1"], "MEDIUM_SENSORY_REACTION", "HIGH", "shield_brace", {"clues": {"add": ["kest_defends_without_reclaiming_unilateral_command"]}}),
    B("From the opposite height Sigrid uses lime flags and spoken calls, not unexplained magic, to position adult bow and rope teams around the brood's blind side.", "tall adult command geometry with visible lime marks, teams, roof, and creature", [G, W], ["ng-prop-lime-route-marks-r1", "ng-progression-class-sigrid-thornpath-wayfinder-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "coordinated_redeployment"),
    B("Sigrid's final arrow cuts a loaded trellis cable; the weighted espalier frame rotates against the brood's raised forelimb and opens its root-knot guard.", "wide causal action with arrow, cable tension, rotating frame, forelimb, and exposed knot", [G, W], ["ng-progression-weapon-sigrid-compact-bow-r1", "ng-progression-monster-brood-mireback-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "counterweighted_rotation", {"props": {"remove": ["one_arrow_remaining"], "add": ["empty_quiver"]}, "clues": {"add": ["trellis_counterweight_opens_brood_root_knot_guard"]}}),
    B("Soren hooks the exposed lower joint and calls the final release; adult crews haul together, rolling the brood into the irrigation wall with water and leverage.", "wide action anchor with hook joint, haul ropes, gate water, and collective weight", [S, K, W], ["ng-progression-weapon-wardens-reach-forged-r1", "ng-progression-monster-brood-mireback-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "collective_pull"),
    B("Adult orchard crews capstan a harvest cable across the exposed root-knot and sever it from the feeding bed while Sigrid routes and Soren holds.", "large collective hero panel crediting adult crews, capstan, cable, route, and threshold", [S, G, K, W], ["ng-progression-monster-brood-mireback-r1", "ng-faction-briar-compact-adults-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "collective_severance", {"clues": {"add": ["brackenwake_collectively_defeats_brood_mireback"]}}),

    B("Muddy dawn finds injured adults receiving care and surviving crews counting ruined bins and terraces while Sigrid directs safe movement and seated Soren's brace remains conspicuous.", "wide aftermath with triage, food accounting, damaged orchard, and persistent injury", [S, G, T, K, W], ["ng-set-brackenwake-orchards-r1", "ng-prop-rigid-brackenwake-leg-brace-r1"], "WIDE_ENVIRONMENTAL_MOTION", "MEDIUM", "triage_and_accounting", {"wardrobe": {"set": ["soren_oatmeal_quilted_coat_and_quarry_guards_mud_scored", "sigrid_plaid_weather_cape_and_quarry_guards_mud_scored"]}, "injuries": {"remove": ["soren_left_lower_leg_crush_sprain_rigid_brace_movement_limited"], "add": ["soren_left_lower_leg_crush_sprain_rigid_brace_aggravated_movement_limited"]}, "weather": {"set": ["cold_day_four_muddy_dawn"]}, "clues": {"add": ["brackenwake_survives_with_orchards_and_winter_food_damaged"]}}),
    B("On Warden's Reach's real forged socket, frost-green letters record HEARTH WARDEN—EARNED: HELD A COMMON THRESHOLD without curing Soren's leg.", "small physical forged-socket inscription beside visible brace and no floating HUD", [S], ["ng-progression-class-soren-hearth-warden-r1", "ng-progression-weapon-wardens-reach-forged-r1"], "SMALL_OBJECT_INSERT", "LOW", "physical_inscription", {"clues": {"add": ["soren_earns_hearth_warden_through_common_threshold_defense"]}}),
    B("On a brass orchard route plate beneath Sigrid's hand, frost-green letters record THORNPATH WAYFINDER—EARNED: MADE SAFE PASSAGE SHARED.", "small physical brass-plate inscription with Sigrid's hand and route marks", [G], ["ng-progression-class-sigrid-thornpath-wayfinder-r1"], "SMALL_OBJECT_INSERT", "LOW", "physical_inscription", {"clues": {"add": ["sigrid_advances_to_thornpath_wayfinder_through_shared_safe_passage"]}}),
    B("At the repaired council threshold the pair restate complementary roles, adult captains vote, Halvor places his seal among—not above—the tally, and the lintel records TWO HANDS, ONE THRESHOLD.", "wide civic tableau with consent tokens, physical lintel inscription, equal pair, and adult council", [S, G, K, W], ["ng-progression-ui-two-hands-one-threshold-r1", "ng-faction-briar-compact-adults-r1"], "WIDE_DIRECTIONAL_ANCHOR", "MEDIUM", "consent_tally_and_bond", {"clues": {"add": ["two_hands_one_threshold_shared_bond_earned", "majority_compact_supports_northward_mission", "kest_loses_unilateral_control", "pair_become_publicly_accountable_co_leaders"]}}),
    B("Still visibly leg-limited after her documented cart arrival, Tamsin unfolds a concealed final map section and admits it leads to the sealed North Garden and the thing rooted beneath it.", "medium closing clue with adult Tamsin, hidden physical map, readable faces, and no teleportation", [T, S, G], ["ng-prop-concealed-north-garden-map-r1", "ng-prop-damaged-node-map-r1"], "MEDIUM_CHARACTER_CLUE", "LOW", "map_reveal", {"props": {"add": ["concealed_north_garden_map_section"]}, "locations": {"set": ["brackenwake_repaired_council_threshold"]}, "clues": {"add": ["tamsin_reveals_hidden_north_garden_route", "sealed_north_garden_contains_rooted_threat"]}}),
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
    mapping = {
        S: "ng-identity-soren-fictional-design-r1", G: "ng-identity-sigrid-fictional-design-r1",
        T: "ng-identity-tamsin-fictional-adult-r1", K: "ng-identity-halvor-kest-fictional-adult-r1",
        W: "ng-identity-briar-compact-worker-fictional-adult-r1",
    }
    return [mapping[role] for role in cast]


def progression(chapter_id: str) -> dict[str, Any]:
    clothing = ["ng-progression-clothing-soren-quilted-coat-r1", "ng-progression-clothing-sigrid-weather-cape-r1"]
    armor = ["ng-progression-armor-soren-quarry-leather-r1", "ng-progression-armor-sigrid-quarry-leather-r1"]
    weapons = ["ng-progression-weapon-wardens-reach-forged-r1", "ng-progression-weapon-sigrid-compact-bow-r1", "ng-progression-weapon-sigrid-utility-seax-r1"]
    if chapter_id == "CH10":
        return {
            "armor": {"canon_decision": "ADR-0196", "asset_ids": armor},
            "weapons": {"canon_decision": "ADR-0196", "asset_ids": weapons},
            "upgraded_clothing": {"canon_decision": "ADR-0196", "asset_ids": clothing},
            "monsters": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-monster-mireback-r1"]},
            "classes": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-class-sigrid-wayfinder-r1"]},
            "system_ui": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-ui-wayfinder-route-line-r1", "ng-progression-ui-forge-bargain-inscription-r1", "ng-progression-ui-orchard-alarm-r1"]},
        }
    return {
        "armor": {"canon_decision": "ADR-0196", "asset_ids": armor},
        "weapons": {"canon_decision": "ADR-0196", "asset_ids": weapons},
        "upgraded_clothing": {"canon_decision": "ADR-0196", "asset_ids": clothing},
        "monsters": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-monster-mireback-r1", "ng-progression-monster-brood-mireback-r1"]},
        "classes": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-class-soren-hearth-warden-r1", "ng-progression-class-sigrid-thornpath-wayfinder-r1"]},
        "system_ui": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-ui-orchard-alarm-r1", "ng-progression-ui-defenders-declared-r1", "ng-progression-ui-two-hands-one-threshold-r1"]},
    }


def build_chapter(chapter_id: str, arc: dict[str, Any], initial: dict[str, list[str]]) -> dict[str, Any]:
    beats = CH10_BEATS if chapter_id == "CH10" else CH11_BEATS
    if len(beats) != 40:
        raise ValueError(f"{chapter_id} must define exactly forty beats")
    state = copy.deepcopy(initial)
    plans: list[dict[str, Any]] = []
    for index, source in enumerate(beats, start=1):
        sequence_slug, _, phase_id = SEQUENCES[chapter_id][(index - 1) // 5]
        carry_in = copy.deepcopy(state)
        state = apply_updates(state, source["updates"])
        carry_out = copy.deepcopy(state)
        panel_id = f"ng-{chapter_id.lower()}-sc01-p{index:03d}"
        anchor = "top_left" if index % 2 else "top_right"
        rect = [0.04, 0.04, 0.34, 0.20] if anchor == "top_left" else [0.66, 0.04, 0.96, 0.20]
        plans.append({
            "panel_id": panel_id, "plan_revision_id": f"{panel_id}-plan-r1", "display_order": index,
            "scene_beat_id": f"ng-beat-{chapter_id.lower()}-sc01-r1", "narrative_phase_id": phase_id,
            "narrative_beat": source["narrative"], "composition_intent": source["composition"],
            "visible_adult_cast": source["cast"], "asset_ids": list(dict.fromkeys(identity_assets(source["cast"]) + source["assets"])),
            "spatial_mode": "2d_only", "spatial_stage_contract_id": None, "spatial_assignments": [],
            "sequence_id": f"ng-{chapter_id.lower()}-{sequence_slug}", "scale_role": source["scale"], "density_class": source["density"],
            "continuity_carry_in": carry_in, "continuity_carry_out": carry_out,
            "comic_direction": {"motion_mode": source["motion"], "direction_note": f"Render the named physical cause and response literally: {source['narrative']}", "lettering": {"state": "SAFE_ZONE_PLANNED_COPY_NOT_YET_AUTHORED", "placement_policy": "safe_zone", "safe_zones": [{"anchor": anchor, "rect_norm": rect}], "protected_subjects": ["faces", "adult silhouettes", "important hands", "weapons and tools", "story objects", "physical Garden Ledger surfaces", "injury and load geometry"]}},
        })
    sequences = []
    for order, (slug, title, phase_id) in enumerate(SEQUENCES[chapter_id], start=1):
        subset = plans[(order - 1) * 5:order * 5]
        sequences.append({"sequence_id": f"ng-{chapter_id.lower()}-{slug}", "narrative_order": order, "title": title, "narrative_functions": [PHASE_FUNCTIONS[phase_id]], "panel_ids": [row["panel_id"] for row in subset], "continuity_entry": copy.deepcopy(subset[0]["continuity_carry_in"]), "continuity_exit": copy.deepcopy(subset[-1]["continuity_carry_out"])})
    roles = [S, G, T, K, W]
    return {
        "record_type": "ComicPanelPlanCollection", "schema_version": "2.0", "record_id": f"ng-comic-plans-{chapter_id.lower()}-sc01-r1", "state": "AUTHORING_COMPLETE_NOT_PROMOTED_PROVISIONAL_CANON", "medium": "comic", "planning_structure": "ComicPanelPlan", "animation_shot_plan": None, "e_conte": None,
        "chapter_title": arc["title"], "chapter_logline": arc["logline"], "story_state_id": f"ng-story-{chapter_id.lower()}-sc01-r1", "opening_state": arc["opening_state_key"], "closing_changed_state": arc["closing_state_key"], "declared_target_panel_count": 40,
        "fictional_adult_roles": roles,
        "identity_contract": {
            "SOREN": "clearly fictional mature adult; light-brown to dark-blond short-to-medium wavy swept-back hair, never black or bright blond; pale oatmeal quilted work coat under removable quarry leather and iron protection; persistent braced left-leg gait",
            "SIGRID": "clearly fictional mature adult; dark-brown to near-black hair in compact low bun or practical braid, never blond or loose red curls; dark blue-brown plaid secured weather cape over removable quarry leather",
            "TAMSIN_REEVE": "clearly fictional adult courier-cartographer with practical non-sexualized field clothing and persistent recovering lower-leg injury",
            "HALVOR_KEST": "clearly fictional adult Briar Compact marshal; dark iron-brown close-cropped hair with gray temples and short matching beard; practical non-sexualized quarry armor; no real-person reference",
            "BRIAR_COMPACT_WORKER": "clearly fictional mature adult settlement workers and defenders in practical work clothing; no real-person reference",
        },
        "continuity_contract": {"initial_state": copy.deepcopy(plans[0]["continuity_carry_in"]), "final_state": copy.deepcopy(plans[-1]["continuity_carry_out"])},
        "progression_contract": progression(chapter_id),
        "narrative_phases": [{"phase_id": phase, "narrative_function": function} for phase, function in PHASE_FUNCTIONS.items()],
        "sequences": sequences, "plans": plans, "promotion_decision": None, "execution_ready": False, "authoring_complete": True,
        "anti_duplication": {"default_candidates_per_panel": 1, "alternate_style_before_complete_chapter": False, "targeted_repair_cap_per_failed_panel": 2},
    }


def story_state(chapter_id: str, arc: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    return {"record_type": "StoryState", "schema_version": "1.0", "record_id": f"ng-story-{chapter_id.lower()}-sc01-r1", "scope": f"{chapter_id}_SC01_PROVISIONAL_CANON_AUTHORING_COMPLETE_NOT_RENDER_PROMOTED", "fictional_cast": plan["fictional_adult_roles"], "set": arc["primary_location"], "timeline_state": arc["timeline"], "opening_state": arc["opening_state_key"], "closing_changed_state": arc["closing_state_key"], "narrative_state": arc["logline"], "state_delta": arc["state_delta"], "continuity_final_state": plan["continuity_contract"]["final_state"], "promotion_decision": None, "source_limit": "Provisional canon-development authoring under ADR-0196 and ADR-0202; no render, acceptance, rights, exact-base, ingestion, or cross-medium authority."}


def scene_beat(chapter_id: str, arc: dict[str, Any]) -> dict[str, Any]:
    return {"record_type": "SceneBeat", "schema_version": "1.0", "record_id": f"ng-beat-{chapter_id.lower()}-sc01-r1", "story_state_id": f"ng-story-{chapter_id.lower()}-sc01-r1", "chapter_question": arc["chapter_question"], "narrative_intent": arc["logline"], "causal_setpieces": arc["causal_setpieces"], "closing_hook": arc["closing_hook"], "comic_direction_boundary": "Direction is contained in ComicPanelPlan; AnimationShotPlan and E-Conte are absent/null."}


def authoring_markdown(plans: dict[str, dict[str, Any]]) -> str:
    return "\n".join([
        "# CH10–CH11 complete ComicPanelPlan authoring r1", "",
        "The third Bell Road batch adds 80 unique chronological plans before any render promotion.", "",
        "| Chapter | Panels | Sequences | Opening | Closing |", "| --- | ---: | ---: | --- | --- |",
        *[f"| {chapter_id} — {plan['chapter_title']} | 40 | 8 | {plan['opening_state']} | {plan['closing_changed_state']} |" for chapter_id, plan in plans.items()], "",
        "CH10 makes Soren's braced gait materially constrain every repair and negotiation, exposes Kest's protective sabotage, earns medicine and forged work-derived gear, and brings Tamsin forward without erasing her injury. CH11 turns those gains into public responsibility and collective defense: Sigrid routes adult defenders, Soren sequences irrigation traps from a fixed position, Brackenwake completes the takedown, and formal classes plus Two Hands, One Threshold follow declared complementary action.", "",
        "All Ledger effects remain on brass, iron, stone, water, tools, arrows, or condensation. All 16 sequences are contiguous five-panel units with exact CH09→CH10→CH11 carry, adult-only roles, fixed hair anchors, practical armor, protected lettering, and literal causal action.", "",
        "ADR-0202 accepts this faction-and-siege authoring batch only. Prompt/render promotion remains a separate future gate.", "",
        "No prompt, provider call, upload, image, generated candidate, acceptance, commercial decision, exact-base decision, AnimationShotPlan, or E-Conte record is created.", "",
    ])


def adr_markdown() -> str:
    return "\n".join([  # noqa: FLY002 - prose is intentionally represented as ordered lines
        "# ADR-0202: Author CH10 and CH11 as one faction-and-siege continuity batch", "", "## Status", "", "Accepted for provisional canon-development authoring only.", "", "## Context", "",
        "CH09 leaves Soren injured, Sigrid operationally leading, Warden's Reach damaged, and Brackenwake implicated in deliberate map sabotage. The next two chapters must convert those facts into political and settlement-scale consequences without granting render authority or erasing fixed continuity.", "", "## Decision", "",
        "1. Author CH10–CH11 as one 80-panel, 16-sequence ComicPanelPlan batch with exact CH09→CH10→CH11 continuity.",
        "2. Make Soren's braced lower leg constrain movement, stance, repair posture, and defense placement until the arc changes it explicitly.",
        "3. Introduce Halvor Kest and Briar Compact workers only as clearly fictional adults in practical, non-sexualized work or quarry protection.",
        "4. Earn forged gear through visible repair and bargaining; earn formal classes and the shared bond through declared complementary collective defense.",
        "5. Keep every Garden Ledger manifestation on physical brass, iron, stone, water, tools, arrows, or condensation; never use a persistent floating HUD.",
        "6. Keep prompt, provider, upload, spend, acceptance, commercial, rights, exact-base, and cross-medium authority outside this authoring decision.", "", "## Consequences", "",
        "The story gains two complete chronological chapters, an adult faction conflict, persistent practical equipment, a settlement-scale siege, formal role names, and explicit co-leadership. CH12 must inherit the damaged orchards, political split, Tamsin's disclosure, Soren's injury, and the negotiated partnership state exactly.", "",
        "This ADR grants no prompt, provider, upload, paid API, cloud GPU, model, ingestion, rendering, acceptance, commercial, rights, exact-production-base, AnimationShotPlan, or E-Conte authority.", "",
    ])


def main() -> int:
    verify_sources()
    arc_doc = json.loads(ARC_PATH.read_text(encoding="utf-8"))
    chapters = {row["chapter_id"]: row for row in arc_doc["chapters"]}
    ch09 = json.loads(CH09_PATH.read_text(encoding="utf-8"))
    plans: dict[str, dict[str, Any]] = {}
    plans["CH10"] = build_chapter("CH10", chapters["CH10"], ch09["continuity_contract"]["final_state"])
    plans["CH11"] = build_chapter("CH11", chapters["CH11"], plans["CH10"]["continuity_contract"]["final_state"])
    for chapter_id in ("CH10", "CH11"):
        for path, payload in ((OUTPUTS[chapter_id], plans[chapter_id]), (STORY_OUTPUTS[chapter_id], story_state(chapter_id, chapters[chapter_id], plans[chapter_id])), (BEAT_OUTPUTS[chapter_id], scene_beat(chapter_id, chapters[chapter_id]))):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    MARKDOWN_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_OUTPUT.write_text(authoring_markdown(plans), encoding="utf-8", newline="\n")
    ADR_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ADR_OUTPUT.write_text(adr_markdown(), encoding="utf-8", newline="\n")
    paths = [*OUTPUTS.values(), *STORY_OUTPUTS.values(), *BEAT_OUTPUTS.values(), MARKDOWN_OUTPUT, ADR_OUTPUT]
    print(json.dumps({"chapters": 2, "panels": 80, "sequences": 16, "files": 8, "hashes": {path.relative_to(ROOT).as_posix(): sha256(path) for path in paths}, "activity": {"pixels": 0, "provider_calls": 0, "uploads": 0, "spend_usd": 0.0}}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
