"""Compile the CH08-CH09 chronological ComicPanelPlan authoring batch."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = ROOT / "production/canon/story-arcs/north-garden-ch06-ch13-progression-r1.json"
CONTRACT_PATH = ROOT / "production/comic/contracts/complete-chapter-comicpanelplan-authoring-contract-r1.json"
CH07_PATH = ROOT / "production/comic/ch07-sc01-panel-plans-r1.json"
BOUND_HASHES = {
    ARC_PATH: "04d0933b07cfc2c11d15c05ebabc1d6695b0ed73ca328fc1659e53f33f107539",
    CONTRACT_PATH: "e112fcd5d2b450746a6a6ad827ba6dff4ff77a0bf10c212f4718a334dc3e9d4e",
    CH07_PATH: "229f95285a7dbb8734bc458f1266702d79ce3de309e99921bde990fdf57400ea",
}
OUTPUTS = {
    "CH08": ROOT / "production/comic/ch08-sc01-panel-plans-r1.json",
    "CH09": ROOT / "production/comic/ch09-sc01-panel-plans-r1.json",
}
STORY_OUTPUTS = {
    "CH08": ROOT / "production/canon/story-state/ch08-sc01-r1.json",
    "CH09": ROOT / "production/canon/story-state/ch09-sc01-r1.json",
}
BEAT_OUTPUTS = {
    "CH08": ROOT / "production/scene-beats/ch08-sc01-root-road-r1.json",
    "CH09": ROOT / "production/scene-beats/ch09-sc01-black-weir-r1.json",
}
MARKDOWN_OUTPUT = ROOT / "docs/research/ch08-ch09-comicpanelplan-authoring-r1.md"
ADR_OUTPUT = ROOT / "docs/adr/ADR-0200-author-ch08-ch09-as-cross-chapter-continuity-batch.md"

PHASE_FUNCTIONS = {
    "phase01": "opening_state_and_orientation",
    "phase02": "movement_and_escalation",
    "phase03": "threshold_and_entry",
    "phase04": "causal_interaction_and_evidence",
    "phase05": "deduction_choice_and_consequence",
    "phase06": "reversal_return_or_closure",
}
SEQUENCES = {
    "CH08": [
        ("s01-road-kit", "Repair for the road", "phase01"),
        ("s02-warden-cairns", "Cairns that answer", "phase02"),
        ("s03-windthrow", "The warning in the windthrow", "phase02"),
        ("s04-hollow-stag", "Driven toward the ravine", "phase03"),
        ("s05-root-bridge", "Hold the root bridge", "phase04"),
        ("s06-bound-antler", "Cut the boundary wire", "phase04"),
        ("s07-mark-not-enemy", "A mark is not a verdict", "phase05"),
        ("s08-black-weir", "Choose the north road", "phase06"),
    ],
    "CH09": [
        ("s01-weir-face", "The drowned node", "phase01"),
        ("s02-current-reading", "Read what moves", "phase02"),
        ("s03-false-passage", "The map is physically wrong", "phase03"),
        ("s04-sluice-collapse", "Iron, water, and a pinned leg", "phase04"),
        ("s05-make-the-brace", "Hold long enough", "phase04"),
        ("s06-submerged-line", "Walk the drowned boundary", "phase05"),
        ("s07-wayfinder", "A route earned under pressure", "phase05"),
        ("s08-brackenwake-seal", "The human mark", "phase06"),
    ],
}


def B(narrative: str, composition: str, cast: list[str], assets: list[str], scale: str,
      density: str, motion: str, updates: dict[str, dict[str, list[str]]] | None = None) -> dict[str, Any]:
    return {"narrative": narrative, "composition": composition, "cast": cast, "assets": assets,
            "scale": scale, "density": density, "motion": motion, "updates": updates or {}}


S = "ADULT_SOREN"
G = "ADULT_SIGRID"
T = "ADULT_TAMSIN_REEVE"
SG = [S, G]
SGT = [S, G, T]

CH08_BEATS = [
    B("At first dawn Tamsin remains beside the cracked farmhouse ward while Soren and Sigrid state the northward plan and step beyond the gate together.", "wide gate tableau with three adults, cracked wardstone, and north road vector", SGT, ["ng-set-farmhouse-gate-r1", "ng-prop-damaged-node-map-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "declared_departure", {"locations": {"set": ["farmhouse_boundary_node_tamsin_rear_guard", "farmhouse_gate_pair_departure"]}, "weather": {"set": ["cold_clear_day_two_dawn"]}, "clues": {"add": ["tamsin_sheltered_at_cracked_farmhouse", "northward_route_begun"]}}),
    B("Soren lays the torn oatmeal sleeve flat while Sigrid measures quilted sacking across his shoulder without obscuring either adult's face or working hands.", "overhead workbench geometry with oatmeal cloth, quilted panel, needle, and four hands", SG, ["ng-prop-road-repair-kit-r1", "ng-progression-clothing-soren-quilted-coat-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "MEDIUM", "measured_repair", {"props": {"add": ["road_repair_kit"]}}),
    B("Sigrid folds the scorched plaid edge inward, threads it through two horn toggles, and tests a secured weather-cape closure across her practical gray-green layers.", "medium hand-and-toggle action preserving plaid pattern and tied dark hair", [G], ["ng-progression-clothing-sigrid-weather-cape-r1", "ng-prop-horn-toggles-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "cloth_tension"),
    B("They buckle thin boiled-leather forearm guards over work sleeves, checking that bow draw, polehook grip, and signature garment silhouettes remain free.", "balanced two-shot with evolved work-derived armor and readable weapon grips", SG, ["ng-progression-armor-quilted-road-kit-r1", "ng-progression-weapon-wardens-reach-r1", "ng-progression-weapon-compact-bow-loan-r1"], "MEDIUM_TWO_SHOT", "MEDIUM", "fit_test", {"wardrobe": {"set": ["soren_oatmeal_coat_quilted_shoulders_and_torn_sleeve_repaired", "sigrid_plaid_weather_cape_secured_scorched_edge"]}, "clues": {"add": ["work_derived_road_armor_completed"]}}),
    B("Sigrid shoulders the compact bow, Soren balances Warden's Reach, and they leave the repair kit with Tamsin as the farmhouse recedes behind them.", "long road departure with distinct oatmeal and plaid silhouettes and farmhouse small behind", SG, ["ng-progression-armor-quilted-road-kit-r1", "ng-progression-weapon-wardens-reach-r1", "ng-progression-weapon-compact-bow-loan-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "walking_departure", {"props": {"remove": ["road_repair_kit"]}, "locations": {"set": ["farmhouse_boundary_node_tamsin_rear_guard", "old_root_road_south_marker"]}}),

    B("The old road narrows between exposed roots, and Sigrid keeps the damaged node map low enough to compare its ink with real cairn spacing.", "wide travel composition with map, road, and repeating stone cairns in one depth axis", SG, ["ng-set-old-root-road-r1", "ng-prop-damaged-node-map-r1"], "WIDE_DIRECTIONAL_ANCHOR", "MEDIUM", "paced_travel"),
    B("A silent insert shows moss scraped from the north face of one cairn while three deliberate boot scuffs point toward its buried base.", "small object clue of moss, scuffs, and cairn edge with no people", [], ["ng-clue-warden-cairn-r1"], "SMALL_OBJECT_INSERT", "LOW", "surface_change", {"clues": {"add": ["warden_cairn_north_face_exposed"]}}),
    B("Soren levers the cairn cap only a finger-width with Warden's Reach while Sigrid blocks the loose stones with her braced boot.", "low dual-causal angle showing polehook leverage, boot block, and shifting stone", SG, ["ng-progression-weapon-wardens-reach-r1", "ng-set-warden-cairn-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "lever_and_block"),
    B("The brass boundary key touches the revealed stone socket and a brief frost-green ROAD TENDED inscription travels across real brass before fading.", "tight brass-key and stone-socket insert with physical inscription only", [], ["ng-prop-brass-boundary-key-r1", "ng-progression-ui-road-tended-inscription-r1"], "SMALL_OBJECT_INSERT", "LOW", "physical_inscription", {"clues": {"add": ["garden_ledger_road_tended_on_brass", "cairns_are_boundary_maintenance_points"]}}),
    B("Sigrid rotates the damaged map to align the cairn chain, proving the printed north line is offset but the physical road still continues.", "medium clue portrait with map edge below face and cairn chain behind shoulder", [G], ["ng-prop-damaged-node-map-r1", "ng-set-warden-cairn-r1"], "MEDIUM_CHARACTER_CLUE", "LOW", "evidence_alignment", {"clues": {"add": ["map_line_offset_from_physical_root_road"]}}),

    B("Beyond the cairns, snapped trunks lie downhill in one direction while fresh hoof cuts climb against the prevailing fall line.", "wide environmental evidence field separating windthrow vector from hoof vector", SG, ["ng-set-windthrown-forest-r1", "ng-clue-hollow-hoof-cuts-r1"], "WIDE_ENVIRONMENTAL_MOTION", "MEDIUM", "windthrow_vector", {"locations": {"set": ["windthrown_forest_margin"]}, "clues": {"add": ["fresh_hollow_hoof_cuts_against_fall_line"]}}),
    B("Sigrid kneels without loosening her dark hair and presses two fingers into a hoof cut, reading compacted soil that shows deliberate braking rather than pursuit.", "low single-adult track-reading panel with tied hair, hand, and soil fully readable", [G], ["ng-clue-hollow-hoof-cuts-r1"], "MEDIUM_SINGLE_CAUSAL", "LOW", "pressure_reading", {"clues": {"add": ["hoof_marks_show_controlled_braking"]}}),
    B("Soren sights along a split beech and notices root plates lifting in sequence toward a hidden ravine as the ground settles under their weight.", "medium adult reaction with sightline connecting split trunk to rising root plates", [S], ["ng-set-windthrown-forest-r1"], "MEDIUM_CHARACTER_CLUE", "MEDIUM", "weight_shift"),
    B("The pair shorten their spacing and cross one at a time, Sigrid marking firm roots while Soren probes hollow soil ahead with the polehook butt.", "tall staggered crossing with route markers, probing tool, and separated footfalls", SG, ["ng-progression-weapon-wardens-reach-r1", "ng-prop-route-markers-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "probe_and_step", {"clues": {"add": ["windthrow_crossing_protocol_adopted"]}}),
    B("A resonant antler knock sounds uphill, and every loose root fiber trembles a heartbeat before the nearest earth shelf drops away.", "small sensory insert of vibrating root fibers and falling soil with off-panel antler sound", [], ["ng-clue-antler-warning-r1"], "SMALL_SENSORY_INSERT", "LOW", "object_vibration", {"clues": {"add": ["antler_knock_precedes_ground_failure"]}}),

    B("A tall Hollow Stag steps between white trunks, mature in scale and bark-thin, with a frost-green mark confined to boundary wire tangled on one antler.", "hero creature reveal with adults small below, mark visibly on real wire rather than floating HUD", SG, ["ng-progression-monster-hollow-stag-r1", "ng-progression-ui-stressed-route-wire-mark-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "creature_intercept", {"clues": {"add": ["hollow_stag_encountered", "ledger_mark_attached_to_boundary_wire"]}}),
    B("Soren lowers Warden's Reach into a guard while Sigrid nocks one of two arrows, both holding position instead of striking first.", "medium defensive two-shot with clear weapon hands and Hollow Stag sightline", SG, ["ng-progression-weapon-wardens-reach-r1", "ng-progression-weapon-compact-bow-loan-r1"], "MEDIUM_TWO_SHOT", "MEDIUM", "held_guard"),
    B("The stag stamps left, lunges short, and forces them sideways exactly as the root shelf behind Soren shears into the ravine.", "wide causal action showing stamp vector, adult sidestep, and collapsing shelf in one frame", SG, ["ng-progression-monster-hollow-stag-r1", "ng-set-windthrow-ravine-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "forced_evasion", {"locations": {"set": ["windthrow_ravine_edge"]}, "clues": {"add": ["stag_displaced_pair_before_shelf_collapse"]}}),
    B("Sigrid follows the stag's repeated shoulder turns and sees each apparent charge end on stable ground, contradicting Soren's threat assumption.", "medium Sigrid deduction with repeated hoof placements and Soren readable behind", [G], ["ng-progression-monster-hollow-stag-r1", "ng-clue-stable-hoof-route-r1"], "MEDIUM_CHARACTER_CLUE", "LOW", "pattern_reading", {"clues": {"add": ["stag_is_steering_not_hunting"]}}),
    B("Soren opens his guard and follows Sigrid's indicated line as the stag backs toward a root bridge stretched across the ravine.", "wide changed-course movement with open polehook posture and Sigrid leading route", SG, ["ng-progression-monster-hollow-stag-r1", "ng-progression-weapon-wardens-reach-r1"], "WIDE_DIRECTIONAL_ANCHOR", "MEDIUM", "evidence_led_course_change", {"clues": {"add": ["soren_changes_course_on_sigrid_evidence"]}}),

    B("The root bridge twists under the stag's weight, one load-bearing root peeling loose while the trapped boundary wire pulls its antler downhill.", "wide bridge mechanics with root tension, wire vector, stag weight, and ravine depth", SG, ["ng-progression-monster-hollow-stag-r1", "ng-set-root-bridge-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "torsion_and_pull", {"clues": {"add": ["root_bridge_failing_under_wire_tension"]}}),
    B("Soren plants Warden's Reach across two living roots and drops his weight through the shaft to make a temporary cross-brace.", "low adult leverage panel with polehook shaft, two roots, boot stance, and bending shoulders", [S], ["ng-progression-weapon-wardens-reach-r1", "ng-set-root-bridge-r1"], "MEDIUM_SINGLE_CAUSAL", "HIGH", "load_bearing_brace", {"clues": {"add": ["soren_shapes_temporary_load_bearing_ward"]}}),
    B("Sigrid crawls along the stable root named by Soren, keeping her plaid cape toggled close so no loose cloth catches the wire.", "tall crawl axis with secured plaid silhouette, supporting root, and clear hand placement", [G], ["ng-progression-clothing-sigrid-weather-cape-r1", "ng-set-root-bridge-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "controlled_crawl"),
    B("A close insert shows the cross-brace biting deeper as Soren's repaired oatmeal shoulder compresses and the bridge load transfers into firm soil.", "tight load-transfer insert of wood, quilted shoulder, root, and compressed mud", [S], ["ng-progression-clothing-soren-quilted-coat-r1", "ng-progression-weapon-wardens-reach-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "compression_transfer"),
    B("Sigrid reaches the stag's bound side while Soren calls the remaining brace time, turning their declared timing into the only safe rescue window.", "wide dual-causal bridge tableau with verbal timing space clear above ravine", SG, ["ng-progression-monster-hollow-stag-r1", "ng-set-root-bridge-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "declared_timing", {"clues": {"add": ["temporary_bridge_brace_holds_for_declared_window"]}}),

    B("Sigrid slides the pocket knife under the taut boundary wire without touching living antler, using her leather guard as a wedge.", "close hand-tool-antler geometry with knife edge and guard clearly separated from creature", [G], ["ng-prop-pocket-knife-r1", "ng-progression-armor-quilted-road-kit-r1", "ng-progression-monster-hollow-stag-r1"], "MEDIUM_SINGLE_CAUSAL", "HIGH", "wedge_and_cut"),
    B("The first wire strand parts, whipping into the mud while the stag shifts its weight uphill instead of striking Sigrid.", "directional action panel with wire recoil, mud impact, and readable creature weight shift", [G], ["ng-progression-monster-hollow-stag-r1", "ng-clue-boundary-wire-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "wire_recoil"),
    B("Soren rotates the polehook brace a quarter turn to catch a slipping root, sacrificing reach but preserving the bridge beneath all three bodies.", "low mechanical action showing shaft rotation, hooked root, and grounded boot triangle", [S], ["ng-progression-weapon-wardens-reach-r1", "ng-set-root-bridge-r1"], "MEDIUM_SINGLE_CAUSAL", "HIGH", "rotational_catch"),
    B("Sigrid cuts the final loop and folds the freed wire under her boot before the stag pulls its antler clear.", "medium causal finish with cut loop, pinned wire, freed antler, and protected hands", [G], ["ng-prop-pocket-knife-r1", "ng-progression-monster-hollow-stag-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "cut_and_pin", {"props": {"add": ["recovered_boundary_wire"]}, "clues": {"add": ["hollow_stag_antler_freed", "boundary_wire_recovered"]}}),
    B("The Hollow Stag crosses to firm ground, pauses within bow range, and lowers its unbound antler rather than attacking.", "quiet wide release with lowered antler, lowered bow, and ravine between silhouettes", SG, ["ng-progression-monster-hollow-stag-r1", "ng-progression-weapon-compact-bow-loan-r1"], "WIDE_DIRECTIONAL_ANCHOR", "LOW", "mutual_release", {"clues": {"add": ["hollow_stag_spared_after_rescue"]}}),

    B("The brass key rests against recovered wire and shows a brief frost-green ROUTE KEEPER inscription on those physical surfaces, then goes dark.", "small brass-and-wire Ledger insert without floating interface", [], ["ng-prop-brass-boundary-key-r1", "ng-progression-ui-route-keeper-inscription-r1"], "SMALL_OBJECT_INSERT", "LOW", "physical_inscription", {"clues": {"add": ["ledger_marks_ecological_route_role", "system_mark_not_hostility_verdict"]}}),
    B("Sigrid sets the stag's stable hoof line beside the damaged map and identifies the old road as a chain of cultivated safe zones called Gardens.", "overhead evidence layout of hoof line, map, cairn rubbing, and adult hands", [G], ["ng-prop-damaged-node-map-r1", "ng-clue-garden-road-r1"], "MEDIUM_SINGLE_CAUSAL", "LOW", "evidence_synthesis", {"clues": {"add": ["old_road_links_cultivated_safe_zones_called_gardens"]}}),
    B("Soren coils the recovered wire instead of taking a trophy and admits his raised weapon misread the Ledger mark.", "medium adult two-shot with coiled wire centered and both faces readable", SG, ["ng-prop-boundary-wire-coil-r1", "ng-progression-weapon-wardens-reach-r1"], "MEDIUM_TWO_SHOT", "LOW", "accountable_choice", {"clues": {"add": ["threat_assumption_revised_on_evidence"]}}),
    B("They mark all seven nodes on the physical map and state a voluntary mission to stabilize the chain rather than chase marked creatures.", "balanced two-shot over map with seven physical marks and clear upper lettering field", SG, ["ng-prop-damaged-node-map-r1", "ng-prop-route-markers-r1"], "MEDIUM_TWO_SHOT", "MEDIUM", "declared_commitment", {"clues": {"add": ["seven_node_stabilization_mission_voluntarily_adopted"]}}),
    B("The stag stamps once on a buried route stone; frost-green moisture gathers inside a carved glyph pointing downhill, then evaporates.", "small hoof-stone-water insert with the glyph physically cut into stone", [], ["ng-progression-monster-hollow-stag-r1", "ng-progression-ui-black-weir-route-glyph-r1"], "SMALL_SENSORY_INSERT", "LOW", "hoof_impact_and_moisture", {"clues": {"add": ["stag_route_glyph_points_to_black_weir"]}}),

    B("At dusk the repaired pair descend from the root road with Sigrid choosing each foothold and Soren testing each load before following.", "wide downhill travel emphasizing evolved silhouettes and shared route/load roles", SG, ["ng-progression-armor-quilted-road-kit-r1", "ng-set-black-weir-approach-r1"], "WIDE_DIRECTIONAL_ANCHOR", "MEDIUM", "guided_descent", {"locations": {"set": ["black_weir_upper_approach"]}, "weather": {"set": ["cold_day_two_dusk"]}}),
    B("The Hollow Stag remains on the ridge behind them, neither companion nor target, while its outline merges with the white trunks.", "quiet long-lens environmental panel with stag distant and adults moving away", SG, ["ng-progression-monster-hollow-stag-r1", "ng-set-windthrown-forest-r1"], "WIDE_ENVIRONMENTAL_MOTION", "LOW", "separation"),
    B("A silent map insert shows the northern route newly aligned with the stag's glyph while the underwater node circle bleeds dark ink.", "small map clue with aligned route, carved-glyph rubbing, and wet node circle", [], ["ng-prop-damaged-node-map-r1", "ng-clue-underwater-node-r1"], "SMALL_OBJECT_INSERT", "LOW", "ink_spread", {"clues": {"add": ["next_node_pulses_under_black_weir"]}}),
    B("Sigrid hears the weir before it appears and raises a closed fist; Soren stops on the same footfall without questioning her lead.", "medium partnership beat with hand signal, checked step, and dark water beyond", SG, ["ng-set-black-weir-approach-r1"], "MEDIUM_TWO_SHOT", "MEDIUM", "halt_signal", {"clues": {"add": ["sigrid_route_intent_lead_recognized"]}}),
    B("The black weir fills the final wide panel as the physical node pulses beneath churning water and both adults commit to descend before night deepens.", "large dusk weir reveal with two small adult silhouettes, underwater pulse, and descent vector", SG, ["ng-set-black-weir-r1", "ng-progression-ui-underwater-node-pulse-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "water_pressure", {"locations": {"set": ["farmhouse_boundary_node_tamsin_rear_guard", "black_weir_overlook_at_dusk"]}, "clues": {"add": ["pair_committed_to_northward_node_route", "hollow_stag_spared"]}}),
]

CH09_BEATS = [
    B("Night settles over the black weir as Sigrid maps the spillway, Soren anchors their rope, and the drowned node pulses against real wet stone below.", "wide weir geography with spillway, rope anchor, two adults, and underwater destination", SG, ["ng-set-black-weir-r1", "ng-progression-ui-underwater-node-pulse-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "water_pressure", {"locations": {"set": ["farmhouse_boundary_node_tamsin_rear_guard", "black_weir_spillway_night"]}, "weather": {"set": ["cold_misted_day_two_night"]}}),
    B("Sigrid secures her plaid weather cape high, checks her compact low braid, and passes the bowstring under oilcloth before entering spray.", "medium preparation portrait preserving dark hair, plaid anchor, bow, and fastening hands", [G], ["ng-progression-clothing-sigrid-weather-cape-r1", "ng-progression-weapon-compact-bow-loan-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "gear_securing"),
    B("Soren wraps the oatmeal coat's quilted shoulder under the descent rope and tests Warden's Reach against a corroded gate ring.", "low tool-load test with oatmeal quilting, rope friction, polehook, and gate iron", [S], ["ng-progression-clothing-soren-quilted-coat-r1", "ng-progression-weapon-wardens-reach-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "load_test"),
    B("They touch the brass key to the weir capstone, where frost-green letters form BELOW / ROUTE UNCONFIRMED and vanish under runoff.", "small capstone, brass, and runoff inscription insert; no floating interface", [], ["ng-prop-brass-boundary-key-r1", "ng-progression-ui-route-unconfirmed-inscription-r1"], "SMALL_OBJECT_INSERT", "LOW", "physical_inscription", {"clues": {"add": ["ledger_reports_below_route_unconfirmed"]}}),
    B("Sigrid declares she will choose the passage while Soren will hold the return line, making leadership and retreat responsibility explicit before descent.", "balanced two-shot above spillway with rope between them and protected speech field", SG, ["ng-prop-descent-rope-r1", "ng-set-black-weir-r1"], "MEDIUM_TWO_SHOT", "LOW", "declared_roles", {"props": {"add": ["descent_rope"]}, "clues": {"add": ["weir_descent_roles_declared"]}}),

    B("Sigrid drops dry chaff into three surface channels and watches two circles stall while the third draws steadily beneath the western arch.", "overhead water experiment with three chaff paths and one true current", [G], ["ng-prop-dry-chaff-r1", "ng-set-weir-channels-r1"], "WIDE_ENVIRONMENTAL_MOTION", "MEDIUM", "current_trace", {"props": {"add": ["dry_chaff"]}, "clues": {"add": ["western_arch_has_true_inflow_current"]}}),
    B("A silent insert follows chaff turning backward beside a wall seam, proving one apparent inlet is only a recirculating pocket.", "small water-surface clue with chaff spiral and masonry seam", [], ["ng-prop-dry-chaff-r1", "ng-clue-recirculating-pocket-r1"], "SMALL_SENSORY_INSERT", "LOW", "current_spiral"),
    B("Sigrid presses her palm to three walls and compares condensation: the coldest stripe climbs toward the hidden water feed.", "medium hand-on-stone causal study with three moisture bands and clear face", [G], ["ng-clue-condensation-stripes-r1"], "MEDIUM_SINGLE_CAUSAL", "LOW", "temperature_comparison", {"clues": {"add": ["condensation_identifies_hidden_feed"]}}),
    B("Soren strikes the gate ring once; Sigrid counts the returning echoes and points past the loud false chamber toward a deeper narrow void.", "dual-causal panel linking ring strike, listening posture, and passage depth", SG, ["ng-progression-weapon-wardens-reach-r1", "ng-clue-echo-delay-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "MEDIUM", "impact_and_echo", {"clues": {"add": ["echo_delay_identifies_deep_western_passage"]}}),
    B("She removes the spent chaff from her route choice, aligning current, condensation, and echo as three independent signs of the western passage.", "overhead evidence triad with map, wet-stone rubbing, and three marked observations", [G], ["ng-prop-damaged-node-map-r1", "ng-prop-route-markers-r1"], "MEDIUM_CHARACTER_CLUE", "LOW", "evidence_alignment", {"props": {"remove": ["dry_chaff"]}, "clues": {"add": ["true_flooded_passage_triangulated"]}}),

    B("They descend through the western arch with Sigrid leading along the wall and Soren feeding rope through the iron ring above.", "tall threshold crossing with wall contact, rope tension, and vertical water depth", SG, ["ng-prop-descent-rope-r1", "ng-set-weir-western-arch-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "controlled_descent", {"locations": {"set": ["weir_western_arch_passage"]}}),
    B("The damaged paper map promises a dry landing, but Sigrid's boot finds waist-deep water where the drawn floor should be.", "medium threshold contradiction with boot entering water and map held above spray", [G], ["ng-prop-damaged-node-map-r1", "ng-set-flooded-weir-tunnel-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "water_entry", {"clues": {"add": ["paper_map_floor_is_physically_wrong"]}}),
    B("Soren finds a bronze map plate bolted backward into the wall, its raised channel pattern mirrored against the real current.", "small bronze plate and current-direction insert with adult hand indicating mirror error", [S], ["ng-clue-reversed-map-plate-r1"], "SMALL_OBJECT_INSERT", "LOW", "surface_comparison", {"clues": {"add": ["bronze_map_plate_installed_in_reverse"]}}),
    B("Sigrid rotates the damaged map rather than the plate and reconstructs a narrow service ledge behind the loud false chamber.", "medium clue portrait with rotated map, hidden ledge line, and tied hair clear", [G], ["ng-prop-damaged-node-map-r1", "ng-clue-service-ledge-r1"], "MEDIUM_CHARACTER_CLUE", "LOW", "map_rotation", {"clues": {"add": ["hidden_service_ledge_reconstructed"]}}),
    B("They choose the ledge one at a time, leaving the rope tied through both the outer ring and a second inner eye so retreat remains possible.", "wide passage decision with two anchor points and one-at-a-time movement", SG, ["ng-prop-descent-rope-r1", "ng-set-service-ledge-r1"], "WIDE_DIRECTIONAL_ANCHOR", "MEDIUM", "anchored_traverse", {"clues": {"add": ["two_point_retreat_line_established"]}}),

    B("The inner sluice shudders when Soren transfers his weight, and rust flakes jump from one loaded hinge before the gate drops.", "tight pre-failure mechanics with boot load, hinge movement, and rust fall", [S], ["ng-set-inner-sluice-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "load_transfer"),
    B("Sigrid lunges clear as the gate slams sideways, but the lower iron bar catches Soren's left leg against the submerged curb.", "wide causal impact showing gate path, Sigrid escape, and precise lower-leg pin", SG, ["ng-set-inner-sluice-r1", "ng-progression-armor-quilted-road-kit-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "gate_collapse", {"injuries": {"add": ["soren_left_lower_leg_pinned_by_sluice"]}, "clues": {"add": ["inner_sluice_hinge_failed_under_load"]}}),
    B("Soren catches the descending gate with Warden's Reach crosswise, bowing its shaft while water climbs over his quilted knee.", "low action with bowed polehook shaft, iron gate, planted hands, and rising water", [S], ["ng-progression-weapon-wardens-reach-r1", "ng-set-inner-sluice-r1"], "MEDIUM_SINGLE_CAUSAL", "HIGH", "compression_hold", {"props": {"remove": ["improvised_wardens_reach"], "add": ["damaged_wardens_reach"]}, "clues": {"add": ["wardens_reach_shaft_damaged_holding_gate"]}}),
    B("Sigrid tests the bar with her shoulder, sees it tighten on Soren's leg, and stops before force worsens the crush.", "medium two-shot with bar-leg relationship, restrained push, and readable reaction", SG, ["ng-set-inner-sluice-r1"], "MEDIUM_TWO_SHOT", "MEDIUM", "diagnostic_pressure"),
    B("A waterline insert shows the failed gate diverting the whole current toward them and emptying the boundary chamber beyond.", "small environmental flow diagram made by real foam and iron edges", [], ["ng-clue-diverted-current-r1"], "SMALL_SENSORY_INSERT", "LOW", "water_diversion", {"locations": {"set": ["flooded_boundary_chamber_threshold"]}, "clues": {"add": ["sluice_failure_redirects_current_into_passage"]}}),

    B("Soren loops his belt around the bowed polehook and a gate upright, making a triangular brace that can hold without both hands.", "close mechanical triangle of belt, tool shaft, gate iron, and protected hands", [S], ["ng-progression-weapon-wardens-reach-r1", "ng-prop-belt-brace-r1"], "MEDIUM_SINGLE_CAUSAL", "HIGH", "triangular_bracing", {"props": {"add": ["belt_and_gate_iron_brace"]}, "clues": {"add": ["self_holding_gate_brace_built"]}}),
    B("Sigrid wedges recovered boundary wire beneath the lower bar, giving Soren enough clearance to drag his trapped leg free.", "dual-causal low angle with wire wedge, bar lift, leg withdrawal, and hand safety", SG, ["ng-prop-boundary-wire-coil-r1", "ng-set-inner-sluice-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "wedge_and_extract", {"injuries": {"remove": ["soren_left_lower_leg_pinned_by_sluice"], "add": ["soren_left_lower_leg_crush_sprain_braced"]}, "clues": {"add": ["soren_leg_freed_by_wire_wedge"]}}),
    B("She binds two flat gate splints around his lower leg while he keeps the brace tension steady through his belt.", "medium first-aid action with splints, knots, injured leg, and tool load all legible", SG, ["ng-prop-gate-iron-leg-brace-r1", "ng-progression-armor-quilted-road-kit-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "MEDIUM", "splint_binding", {"props": {"add": ["gate_iron_lower_leg_brace"]}}),
    B("Soren tests one painful step and cannot carry full weight, so he hands route command and the brass key to Sigrid without argument.", "medium leadership handoff with key transfer, braced stance, and both faces visible", SG, ["ng-prop-brass-boundary-key-r1", "ng-prop-gate-iron-leg-brace-r1"], "MEDIUM_TWO_SHOT", "LOW", "explicit_handoff", {"clues": {"add": ["operational_leadership_passes_to_sigrid"]}}),
    B("Sigrid opens a side spill notch with the pocket knife and recovered wire, redirecting enough current to expose the submerged boundary line.", "wide causal water action with notch, wire pull, current bend, and revealed floor line", [G], ["ng-prop-pocket-knife-r1", "ng-prop-boundary-wire-coil-r1", "ng-set-boundary-chamber-r1"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", "current_redirection", {"clues": {"add": ["side_notch_redirects_current", "submerged_boundary_line_exposed"]}}),

    B("Leaving bow and map above water, Sigrid ties the return rope to her waist and steps onto the first submerged boundary stone.", "tall entry panel with rope, waterline, first stone, and secured plaid cape", [G], ["ng-progression-clothing-sigrid-weather-cape-r1", "ng-prop-descent-rope-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", "submerged_entry"),
    B("She releases one carved wood chip and follows its bend around a collapsed pillar rather than trusting the straight engraved line.", "small water-and-chip insert showing current bending around stone obstruction", [], ["ng-clue-current-route-chip-r1"], "SMALL_SENSORY_INSERT", "LOW", "current_trace", {"clues": {"add": ["current_bends_around_collapsed_pillar"]}}),
    B("The brass key in Sigrid's hand casts a brief frost-green line across wet stone only after her boot seats on each true route mark.", "low route-walking image with boot, key, and physical wet-stone line", [G], ["ng-prop-brass-boundary-key-r1", "ng-progression-ui-wayfinder-route-line-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "step_activated_inscription", {"clues": {"add": ["ledger_route_line_responds_to_verified_steps"]}}),
    B("Behind her, Soren shifts the belt brace one notch at a time so the current falls without releasing the gate onto his injured leg.", "medium mechanical counter-action with braced leg, belt notch, and dropping waterline", [S], ["ng-progression-weapon-wardens-reach-r1", "ng-prop-gate-iron-leg-brace-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "incremental_release"),
    B("Sigrid reaches the far marker, turns the brass key in a real stone socket, and completes an unbroken route back to Soren's rope anchor.", "wide chamber geometry connecting socket, lit wet-stone path, rope, and injured partner", SG, ["ng-prop-brass-boundary-key-r1", "ng-progression-ui-wayfinder-route-line-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "route_completion", {"clues": {"add": ["submerged_boundary_route_completed_under_pressure"]}}),

    B("Frost-green letters rise in condensation on the socket—WAYFINDER PATH / EARNED BY RETURN—then begin to bead away.", "small condensation inscription on stone with no floating HUD", [], ["ng-progression-class-sigrid-wayfinder-r1", "ng-progression-ui-wayfinder-earned-inscription-r1"], "SMALL_OBJECT_INSERT", "LOW", "condensation_inscription", {"clues": {"add": ["sigrid_wayfinder_path_earned_by_navigation_and_rescue"]}}),
    B("Sigrid refuses to follow the brightest line until she checks it against current and echo, proving the new perception does not replace evidence.", "medium Sigrid clue portrait with three surface lines and listening posture", [G], ["ng-progression-class-sigrid-wayfinder-r1", "ng-progression-ui-wayfinder-route-line-r1"], "MEDIUM_CHARACTER_CLUE", "LOW", "ability_verification", {"clues": {"add": ["wayfinder_perception_requires_physical_verification"]}}),
    B("She marks one safe return route on the wet wall; Soren follows it with a shortened injured stride while the rope stays taut between them.", "wide return action with visible route mark, limp cadence, rope, and adult silhouettes", SG, ["ng-progression-class-sigrid-wayfinder-r1", "ng-prop-gate-iron-leg-brace-r1"], "WIDE_DIRECTIONAL_ANCHOR", "MEDIUM", "guided_withdrawal", {"clues": {"add": ["sigrid_can_perceive_stressed_routes_on_real_surfaces"]}}),
    B("The restored node sends one pressure pulse through the chamber, seating the damaged polehook's hook into its split shaft instead of repairing it.", "tight tool-and-stone reaction showing hook seated, split shaft retained, and water pulse", [S], ["ng-progression-weapon-wardens-reach-recognized-r1", "ng-progression-ui-weir-node-stable-inscription-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "pressure_seating", {"props": {"remove": ["damaged_wardens_reach", "belt_and_gate_iron_brace"], "add": ["damaged_system_recognized_wardens_reach"]}, "clues": {"add": ["wardens_reach_recognized_but_not_repaired", "weir_node_stabilized"]}}),
    B("Soren accepts Sigrid's shoulder on the climb and repeats her route calls, making the leadership shift visible in pace rather than ceremony.", "medium uphill two-shot with supported weight, braced leg, and Sigrid leading", SG, ["ng-prop-gate-iron-leg-brace-r1", "ng-progression-class-sigrid-wayfinder-r1"], "MEDIUM_TWO_SHOT", "MEDIUM", "supported_climb", {"clues": {"add": ["sigrid_leads_while_soren_injury_limits_speed"]}}),

    B("At the upper ledge Sigrid unbolts the reversed bronze map plate while Soren braces it with his good leg and damaged tool.", "dual-causal removal with bolt, plate weight, stable stance, and protected hands", SG, ["ng-clue-reversed-map-plate-r1", "ng-progression-weapon-wardens-reach-recognized-r1"], "TALL_OR_WIDE_DUAL_CAUSAL", "MEDIUM", "plate_removal", {"props": {"add": ["reversed_bronze_map_plate"]}}),
    B("Clean scrape arcs beneath the plate prove it was turned recently, while older mineral stain preserves its correct former orientation.", "small forensic insert of scrape arcs, bolt head, and mineral silhouette", [], ["ng-clue-map-plate-sabotage-r1"], "SMALL_OBJECT_INSERT", "LOW", "surface_comparison", {"clues": {"add": ["map_plate_deliberately_reversed_recently"]}}),
    B("Sigrid rubs silt from the plate's back and reveals a stamped thorn-and-hammer seal that the damaged paper map labels Brackenwake.", "tight hand, silt, bronze seal, and paper label evidence composition", [G], ["ng-prop-reversed-map-plate-r1", "ng-prop-damaged-node-map-r1"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", "silt_wipe", {"clues": {"add": ["brackenwake_seal_on_false_map_plate", "human_sabotage_enters_node_failures"]}}),
    B("They compare the altered plate with the stabilized physical route and conclude someone redirected travelers away from the only forge north of the weir.", "balanced deduction two-shot with plate and wet route between readable faces", SG, ["ng-prop-reversed-map-plate-r1", "ng-prop-damaged-node-map-r1"], "MEDIUM_TWO_SHOT", "LOW", "causal_deduction", {"clues": {"add": ["brackenwake_controls_only_northern_forge"]}}),
    B("Sigrid leads onto the north bank as Soren follows on the braced leg, the stable weir behind them and Brackenwake's seal carried forward as the next question.", "wide night departure with leadership order, visible limp, physical plate, and north vector", SG, ["ng-progression-class-sigrid-wayfinder-r1", "ng-prop-gate-iron-leg-brace-r1", "ng-prop-reversed-map-plate-r1"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", "injured_departure", {"locations": {"set": ["farmhouse_boundary_node_tamsin_rear_guard", "black_weir_north_bank_night"]}, "clues": {"add": ["northward_route_continues_toward_brackenwake"]}}),
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
    mapping = {S: "ng-identity-soren-fictional-design-r1", G: "ng-identity-sigrid-fictional-design-r1", T: "ng-identity-tamsin-fictional-adult-r1"}
    return [mapping[role] for role in cast]


def progression(chapter_id: str) -> dict[str, Any]:
    common = {
        "armor": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-armor-quilted-road-kit-r1"]},
        "weapons": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-weapon-wardens-reach-r1", "ng-progression-weapon-compact-bow-loan-r1"]},
        "upgraded_clothing": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-clothing-soren-quilted-coat-r1", "ng-progression-clothing-sigrid-weather-cape-r1"]},
    }
    if chapter_id == "CH08":
        common.update({
            "monsters": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-monster-hollow-stag-r1"]},
            "classes": None,
            "system_ui": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-ui-road-tended-inscription-r1", "ng-progression-ui-stressed-route-wire-mark-r1", "ng-progression-ui-route-keeper-inscription-r1", "ng-progression-ui-black-weir-route-glyph-r1", "ng-progression-ui-underwater-node-pulse-r1"]},
        })
    else:
        common.update({
            "monsters": None,
            "classes": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-class-sigrid-wayfinder-r1"]},
            "system_ui": {"canon_decision": "ADR-0196", "asset_ids": ["ng-progression-ui-underwater-node-pulse-r1", "ng-progression-ui-route-unconfirmed-inscription-r1", "ng-progression-ui-wayfinder-route-line-r1", "ng-progression-ui-wayfinder-earned-inscription-r1", "ng-progression-ui-weir-node-stable-inscription-r1"]},
        })
        common["weapons"]["asset_ids"].append("ng-progression-weapon-wardens-reach-recognized-r1")
    return common


def build_chapter(chapter_id: str, arc: dict[str, Any], initial: dict[str, list[str]]) -> dict[str, Any]:
    beats = CH08_BEATS if chapter_id == "CH08" else CH09_BEATS
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
            "panel_id": panel_id,
            "plan_revision_id": f"{panel_id}-plan-r1",
            "display_order": index,
            "scene_beat_id": f"ng-beat-{chapter_id.lower()}-sc01-r1",
            "narrative_phase_id": phase_id,
            "narrative_beat": source["narrative"],
            "composition_intent": source["composition"],
            "visible_adult_cast": source["cast"],
            "asset_ids": list(dict.fromkeys(identity_assets(source["cast"]) + source["assets"])),
            "spatial_mode": "2d_only",
            "spatial_stage_contract_id": None,
            "spatial_assignments": [],
            "sequence_id": f"ng-{chapter_id.lower()}-{sequence_slug}",
            "scale_role": source["scale"],
            "density_class": source["density"],
            "continuity_carry_in": carry_in,
            "continuity_carry_out": carry_out,
            "comic_direction": {
                "motion_mode": source["motion"],
                "direction_note": f"Render the named physical cause and response literally: {source['narrative']}",
                "lettering": {"state": "SAFE_ZONE_PLANNED_COPY_NOT_YET_AUTHORED", "placement_policy": "safe_zone", "safe_zones": [{"anchor": anchor, "rect_norm": rect}], "protected_subjects": ["faces", "adult silhouettes", "important hands", "weapons and tools", "story objects", "physical Garden Ledger surfaces"]},
            },
        })
    sequences = []
    for order, (slug, title, phase_id) in enumerate(SEQUENCES[chapter_id], start=1):
        subset = plans[(order - 1) * 5:order * 5]
        sequences.append({"sequence_id": f"ng-{chapter_id.lower()}-{slug}", "narrative_order": order, "title": title, "narrative_functions": [PHASE_FUNCTIONS[phase_id]], "panel_ids": [row["panel_id"] for row in subset], "continuity_entry": copy.deepcopy(subset[0]["continuity_carry_in"]), "continuity_exit": copy.deepcopy(subset[-1]["continuity_carry_out"])})
    roles = [S, G, T]
    return {
        "record_type": "ComicPanelPlanCollection", "schema_version": "2.0", "record_id": f"ng-comic-plans-{chapter_id.lower()}-sc01-r1", "state": "AUTHORING_COMPLETE_NOT_PROMOTED_PROVISIONAL_CANON", "medium": "comic", "planning_structure": "ComicPanelPlan", "animation_shot_plan": None, "e_conte": None,
        "chapter_title": arc["title"], "chapter_logline": arc["logline"], "story_state_id": f"ng-story-{chapter_id.lower()}-sc01-r1", "opening_state": arc["opening_state_key"], "closing_changed_state": arc["closing_state_key"], "declared_target_panel_count": 40,
        "fictional_adult_roles": roles,
        "identity_contract": {
            "SOREN": "clearly fictional mature adult; light-brown to dark-blond short-to-medium wavy swept-back hair, never black or bright blond; pale oatmeal work coat with quilted shoulder reinforcement",
            "SIGRID": "clearly fictional mature adult; dark-brown to near-black hair in compact low bun or practical braid, never blond or loose red curls; dark blue-brown plaid secured weather cape",
            "TAMSIN_REEVE": "clearly fictional adult courier-cartographer; practical non-sexualized field clothing; remains sheltered at the farmhouse after CH08 panel one",
        },
        "continuity_contract": {"initial_state": copy.deepcopy(plans[0]["continuity_carry_in"]), "final_state": copy.deepcopy(plans[-1]["continuity_carry_out"])},
        "progression_contract": progression(chapter_id),
        "narrative_phases": [{"phase_id": phase, "narrative_function": function} for phase, function in PHASE_FUNCTIONS.items()],
        "sequences": sequences, "plans": plans, "promotion_decision": None, "execution_ready": False, "authoring_complete": True,
        "anti_duplication": {"default_candidates_per_panel": 1, "alternate_style_before_complete_chapter": False, "targeted_repair_cap_per_failed_panel": 2},
    }


def story_state(chapter_id: str, arc: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    return {"record_type": "StoryState", "schema_version": "1.0", "record_id": f"ng-story-{chapter_id.lower()}-sc01-r1", "scope": f"{chapter_id}_SC01_PROVISIONAL_CANON_AUTHORING_COMPLETE_NOT_RENDER_PROMOTED", "fictional_cast": plan["fictional_adult_roles"], "set": arc["primary_location"], "timeline_state": arc["timeline"], "opening_state": arc["opening_state_key"], "closing_changed_state": arc["closing_state_key"], "narrative_state": arc["logline"], "state_delta": arc["state_delta"], "continuity_final_state": plan["continuity_contract"]["final_state"], "promotion_decision": None, "source_limit": "Provisional canon-development authoring under ADR-0196; no render, acceptance, rights, exact-base, ingestion, or cross-medium authority."}


def scene_beat(chapter_id: str, arc: dict[str, Any]) -> dict[str, Any]:
    return {"record_type": "SceneBeat", "schema_version": "1.0", "record_id": f"ng-beat-{chapter_id.lower()}-sc01-r1", "story_state_id": f"ng-story-{chapter_id.lower()}-sc01-r1", "chapter_question": arc["chapter_question"], "narrative_intent": arc["logline"], "causal_setpieces": arc["causal_setpieces"], "closing_hook": arc["closing_hook"], "comic_direction_boundary": "Direction is contained in ComicPanelPlan; AnimationShotPlan and E-Conte are absent/null."}


def authoring_markdown(plans: dict[str, dict[str, Any]]) -> str:
    return "\n".join([
        "# CH08–CH09 complete ComicPanelPlan authoring r1", "",
        "The second Bell Road batch adds 80 unique chronological plans before any render promotion.", "",
        "| Chapter | Panels | Sequences | Opening | Closing |", "| --- | ---: | ---: | --- | --- |",
        *[f"| {chapter_id} — {plan['chapter_title']} | 40 | 8 | {plan['opening_state']} | {plan['closing_changed_state']} |" for chapter_id, plan in plans.items()], "",
        "CH08 repairs the oatmeal coat and plaid wrap into recognizable work-derived road gear, changes a marked Hollow Stag from presumed enemy to spared ecological guide, and makes the seven-node journey voluntary. CH09 makes Sigrid lead through evidence, current, and echo; the earned physical-surface Wayfinder inscription follows rescue, while Soren's braced lower-leg injury and damaged Warden's Reach persist into CH10.", "",
        "Every Garden Ledger appearance is attached to brass, stone, wire, water, or condensation. All 16 sequences are contiguous five-panel units with literal causal mechanics, fixed adult hair anchors, protected lettering subjects, and exact CH07→CH08→CH09 continuity carry.", "",
        "ADR-0200 accepts the cross-chapter authoring decision while keeping prompt/render promotion as a separate gate after this batch passes semantic and production-boundary review.", "",
        "No prompt, provider call, upload, image, generated candidate, acceptance, commercial decision, exact-base decision, AnimationShotPlan, or E-Conte record is created.", "",
    ])


def adr_markdown() -> str:
    return "\n".join([  # noqa: FLY002 - prose is intentionally represented as ordered lines
        "# ADR-0200: Author CH08 and CH09 as one evidence-led journey batch", "", "## Status", "",
        "Accepted for provisional canon-development authoring. Prompt/render promotion, art acceptance, commercial clearance, and exact-production-base selection remain separate.", "", "## Context", "",
        "ADR-0196 prioritizes chronological breadth, and ADR-0197 establishes exact cross-chapter continuity. CH08 must inherit CH07's post-defense state; CH09 must then inherit CH08 byte-for-byte while changing threat interpretation, leadership, injury, class, equipment, and knowledge through visible causes.", "", "## Decision", "",
        "1. Treat CH08–CH09 as one 80-panel, 16-sequence ComicPanelPlan authoring batch.",
        "2. Require exact CH07→CH08→CH09 continuity, adult-only fictional cast, fixed hair anchors, and persistent evolved practical gear.",
        "3. Depict the Garden Ledger only on physical brass, stone, wire, water, glass, or repaired tools; never as a persistent floating HUD.",
        "4. Earn Hollow Stag stewardship and Sigrid's Wayfinder path through evidence, rescue, and route completion rather than kill points.",
        "5. Carry Soren's lower-leg injury and damaged system-recognized Warden's Reach into the next chapter.",
        "6. Keep the batch non-executable until a separate prompt-manifest promotion passes policy, provenance, continuity, and budget preflight.", "", "## Consequences", "",
        "The arc gains two complete chronological chapters with drastic persistent progression and no duplicate whole-chapter style arms. The next decision is whether to promote one default-house-route candidate per panel, not whether the authoring record itself grants execution.", "",
        "This decision grants no provider, upload, paid API, cloud GPU, model, ingestion, rendering, acceptance, commercial, rights, exact-base, or cross-medium authority.", "",
    ])


def main() -> int:
    verify_sources()
    arc_doc = json.loads(ARC_PATH.read_text(encoding="utf-8"))
    chapters = {row["chapter_id"]: row for row in arc_doc["chapters"]}
    ch07 = json.loads(CH07_PATH.read_text(encoding="utf-8"))
    plans: dict[str, dict[str, Any]] = {}
    plans["CH08"] = build_chapter("CH08", chapters["CH08"], ch07["continuity_contract"]["final_state"])
    plans["CH09"] = build_chapter("CH09", chapters["CH09"], plans["CH08"]["continuity_contract"]["final_state"])
    for chapter_id in ("CH08", "CH09"):
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
