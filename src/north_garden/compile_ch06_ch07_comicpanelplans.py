"""Compile complete CH06 and CH07 ComicPanelPlan authoring graphs."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = ROOT / "production/canon/story-arcs/north-garden-ch06-ch13-progression-r1.json"
OUTPUTS = {
    "CH06": ROOT / "production/comic/ch06-sc01-panel-plans-r1.json",
    "CH07": ROOT / "production/comic/ch07-sc01-panel-plans-r1.json",
}
STORY_OUTPUTS = {
    "CH06": ROOT / "production/canon/story-state/ch06-sc01-r1.json",
    "CH07": ROOT / "production/canon/story-state/ch07-sc01-r1.json",
}
BEAT_OUTPUTS = {
    "CH06": ROOT / "production/scene-beats/ch06-sc01-house-answered-r1.json",
    "CH07": ROOT / "production/scene-beats/ch07-sc01-mireback-gate-r1.json",
}
MARKDOWN_OUTPUT = ROOT / "docs/research/ch06-ch07-comicpanelplan-authoring-r1.md"


PHASE_FUNCTIONS = {
    "phase01": "opening_state_and_orientation",
    "phase02": "movement_and_escalation",
    "phase03": "threshold_and_entry",
    "phase04": "causal_interaction_and_evidence",
    "phase05": "deduction_choice_and_consequence",
    "phase06": "reversal_return_or_closure",
}

CH06_SEQUENCES = [
    ("s01-ridge-return", "The smoking house", "phase01"),
    ("s02-encirclement", "Read the perimeter", "phase02"),
    ("s03-two-entries", "Two entries, one plan", "phase03"),
    ("s04-hearth-stranger", "The adult at the hearth", "phase03"),
    ("s05-counterweight", "Free the trapped courier", "phase04"),
    ("s06-cellar-node", "The house below the house", "phase04"),
    ("s07-terms", "Terms of shelter", "phase05"),
    ("s08-gate-omen", "The orchard answers", "phase06"),
]

CH07_SEQUENCES = [
    ("s01-storm-prep", "Read the coming weight", "phase01"),
    ("s02-field-weapons", "Tools become reach", "phase02"),
    ("s03-first-contact", "Mireback at the wall", "phase02"),
    ("s04-mud-trap", "Make the ground choose", "phase03"),
    ("s05-counterattack", "Expose the root-knot", "phase04"),
    ("s06-shelter-held", "Two hands on one lever", "phase04"),
    ("s07-cost", "The price at the gate", "phase05"),
    ("s08-road-north", "Seven failing lights", "phase06"),
]


def beat(
    narrative: str,
    composition: str,
    cast: list[str],
    scale: str,
    density: str,
    assets: list[str],
    motion: str = "held_observation",
    updates: dict[str, dict[str, list[str]]] | None = None,
) -> dict[str, Any]:
    return {
        "narrative": narrative,
        "composition": composition,
        "cast": cast,
        "scale": scale,
        "density": density,
        "assets": assets,
        "motion": motion,
        "updates": updates or {},
    }


CH06_BEATS = [
    beat("The pair crest the ridge and see deliberate smoke rising from their farmhouse chimney.", "wide downhill reveal with farmhouse below and both adults held small against the path", ["ADULT_SOREN", "ADULT_SIGRID"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", ["ng-set-farmhouse-ridge-r1", "ng-prop-folded-map-r1"], "directional_motion", {"locations": {"set": ["farmhouse_ridge_approach"]}}),
    beat("Sigrid compares the new chimney smoke with the dead mill mark on the folded map.", "over-shoulder map and smoke alignment with her face clear at frame edge", ["ADULT_SIGRID"], "MEDIUM_CHARACTER_CLUE", "MEDIUM", ["ng-set-farmhouse-ridge-r1", "ng-prop-folded-map-r1"], "held_observation"),
    beat("Sigrid closes one fist and Soren stops before his next downhill step lands.", "medium two-shot with the interrupted footfall and her signal readable", ["ADULT_SOREN", "ADULT_SIGRID"], "MEDIUM_TWO_SHOT", "MEDIUM", ["ng-set-wet-farm-trail-r1"], "weight_shift"),
    beat("Fresh boot prints climb toward the house, one heel gouging as if the walker dragged a leg.", "small mud insert with uphill toe direction and one uneven heel channel", [], "SMALL_OBJECT_INSERT", "LOW", ["ng-clue-dragging-bootprints-r1"], "held_observation", {"clues": {"add": ["single_injured_adult_boot_track"]}}),
    beat("They state the plan aloud: Soren holds the visible door while Sigrid circles to the pantry.", "calm profile two-shot divided by the farmhouse in the distance", ["ADULT_SOREN", "ADULT_SIGRID"], "MEDIUM_TWO_SHOT", "LOW", ["ng-set-farmhouse-ridge-r1", "ng-prop-folded-map-r1"], "held_observation", {"clues": {"add": ["declared_threshold_plan"]}}),
    beat("They descend on separate lines while keeping each other in sight.", "wide forked travel composition with one shared destination", ["ADULT_SOREN", "ADULT_SIGRID"], "WIDE_DIRECTIONAL_ANCHOR", "MEDIUM", ["ng-set-farmhouse-yard-r1"], "directional_motion", {"locations": {"set": ["farmhouse_outer_wall"]}}),
    beat("At the stone wall, Soren finds the same soot-stained twine used at the mill.", "hand and wall insert with twine protected from lettering", ["ADULT_SOREN"], "MEDIUM_SINGLE_CAUSAL", "LOW", ["ng-clue-soot-twine-r1", "ng-set-farmhouse-wall-r1"], "held_observation", {"clues": {"add": ["mill_twine_at_farmhouse"]}}),
    beat("A fogged window holds the print of an adult hand braced from inside.", "small sensory insert of condensation, palm print, and warm interior beyond", [], "SMALL_SENSORY_INSERT", "LOW", ["ng-clue-window-handprint-r1"], "held_observation", {"clues": {"add": ["adult_handprint_inside"]}}),
    beat("Soren lifts the door latch only until the twine begins to tighten under it.", "close causal hand-latch-twine geometry", ["ADULT_SOREN"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", ["ng-prop-farmhouse-door-latch-r1", "ng-clue-soot-twine-r1"], "controlled_tension"),
    beat("Around the corner, Sigrid finds the pantry latch already raised with a wooden spoon.", "medium clue view with spoon, latch, and her dark tied hair readable", ["ADULT_SIGRID"], "MEDIUM_CHARACTER_CLUE", "MEDIUM", ["ng-prop-pantry-latch-r1", "ng-set-farmhouse-pantry-entry-r1"], "held_observation", {"clues": {"add": ["improvised_pantry_entry"]}}),
    beat("Soren calls into the front room without crossing the threshold.", "exterior-to-interior two-depth frame, Soren outside and doorway empty", ["ADULT_SOREN"], "MEDIUM_CHARACTER_CLUE", "LOW", ["ng-set-farmhouse-front-door-r1"], "held_observation"),
    beat("No voice answers; a kettle lid chatters once on the stove.", "silent object insert with kettle vibration and no visible person", [], "SMALL_SENSORY_INSERT", "LOW", ["ng-prop-kettle-r1", "ng-set-farmhouse-hearth-r1"], "object_vibration", {"clues": {"add": ["occupied_warm_hearth"]}}),
    beat("Sigrid slips through the pantry with her plaid wrap pinned close to avoid the shelves.", "tall careful entry showing weight placement, cloth control, and clear hands", ["ADULT_SIGRID"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", ["ng-set-farmhouse-pantry-r1"], "controlled_entry", {"locations": {"set": ["farmhouse_pantry_and_front_threshold"]}}),
    beat("She sees the mill twine tied from a chair leg to the cellar latch.", "diagonal twine clue crossing negative floor space, Sigrid held back", ["ADULT_SIGRID"], "MEDIUM_CHARACTER_CLUE", "LOW", ["ng-clue-chair-cellar-twine-r1", "ng-set-farmhouse-kitchen-r1"], "held_observation", {"clues": {"add": ["cellar_counterweight_trap"]}}),
    beat("At Sigrid's spoken count, Soren eases the front door while she pins the chair with her boot.", "dual causal split-depth action with door, twine, chair, boot, and both roles literal", ["ADULT_SOREN", "ADULT_SIGRID"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", ["ng-prop-farmhouse-door-latch-r1", "ng-clue-chair-cellar-twine-r1"], "synchronized_leverage"),
    beat("The door opens on an unfamiliar clearly adult figure seated beside the stove.", "wide interior reveal with Tamsin backlit, Soren at door, Sigrid at pantry", ["ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", ["ng-set-farmhouse-hearth-r1", "ng-identity-tamsin-fictional-adult-r1"], "held_reveal", {"characters": {"add": ["ADULT_TAMSIN_REEVE"]}}),
    beat("Sigrid lowers her empty hand first but keeps the pantry exit clear.", "medium profile triangle with open hand and preserved exits", ["ADULT_SIGRID", "ADULT_TAMSIN_REEVE"], "MEDIUM_TWO_SHOT", "LOW", ["ng-set-farmhouse-hearth-r1"], "controlled_deescalation"),
    beat("The stranger identifies herself as Tamsin Reeve and reveals a swollen, wrapped lower leg.", "mature adult two-shot with practical field clothing and non-graphic injury", ["ADULT_TAMSIN_REEVE", "ADULT_SIGRID"], "MEDIUM_TWO_SHOT", "MEDIUM", ["ng-prop-tamsin-field-wrap-r1"], "held_observation", {"injuries": {"add": ["tamsin_lower_leg_crush_injury"]}}),
    beat("Soren recognizes mill soot on Tamsin's gloves and asks who lit their hearth.", "medium interrogation without looming; soot gloves and faces readable", ["ADULT_SOREN", "ADULT_TAMSIN_REEVE"], "MEDIUM_TWO_SHOT", "MEDIUM", ["ng-clue-mill-soot-gloves-r1"], "held_observation", {"clues": {"add": ["tamsin_linked_to_mill_signal"]}}),
    beat("Tamsin shows a brass key under the chair just as the cellar beam drops against her trapped boot.", "low-angle causal reveal of key, chair, boot, and descending beam", ["ADULT_TAMSIN_REEVE"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", ["ng-prop-brass-boundary-key-r1", "ng-prop-cellar-counterweight-beam-r1"], "weight_drop", {"props": {"add": ["brass_boundary_key"]}}),
    beat("The beam loads the chair and Tamsin cannot pull her injured leg free.", "tight mechanical geometry with beam pressure, chair skew, and boot path", ["ADULT_TAMSIN_REEVE"], "MEDIUM_SINGLE_CAUSAL", "HIGH", ["ng-prop-cellar-counterweight-beam-r1"], "controlled_tension"),
    beat("Soren slides the kitchen table leg beneath the beam to make a temporary fulcrum.", "clear hand-table-beam leverage chain", ["ADULT_SOREN"], "MEDIUM_SINGLE_CAUSAL", "HIGH", ["ng-prop-kitchen-table-r1", "ng-prop-cellar-counterweight-beam-r1"], "leverage"),
    beat("Sigrid follows the taut twine behind the chair and finds its hidden release knot.", "hand and knot insert with twine route fully visible", ["ADULT_SIGRID"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", ["ng-clue-chair-cellar-twine-r1"], "held_observation"),
    beat("Soren lifts on the table lever while Sigrid releases one turn of knot.", "dual action with grounded feet and continuous force path", ["ADULT_SOREN", "ADULT_SIGRID"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", ["ng-prop-kitchen-table-r1", "ng-prop-cellar-counterweight-beam-r1"], "synchronized_leverage"),
    beat("Tamsin drags clear and the unweighted cellar latch opens into cold green darkness.", "wide release with Tamsin clear, beam held, and cellar opening behind", ["ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", ["ng-set-farmhouse-cellar-r1"], "release_and_reveal", {"injuries": {"remove": ["tamsin_lower_leg_crush_injury"], "add": ["tamsin_lower_leg_crush_injury_freed"]}, "locations": {"set": ["farmhouse_kitchen_open_cellar"]}}),
    beat("They descend with Sigrid leading, Soren carrying the lamp, and Tamsin supported at the stair.", "tall three-adult stair descent with explicit role order", ["ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE"], "TALL_OR_WIDE_DUAL_CAUSAL", "MEDIUM", ["ng-set-farmhouse-cellar-r1", "ng-prop-oil-lamp-r1"], "controlled_descent", {"locations": {"set": ["farmhouse_boundary_cellar"]}, "props": {"add": ["oil_lamp"]}}),
    beat("Below the hearth, a stone wheel repeats the mill marker's eight-spoke design.", "environmental clue anchor with wheel, hearth footing, and scale reference", [], "WIDE_ENVIRONMENTAL_MOTION", "MEDIUM", ["ng-clue-boundary-wheel-r1"], "held_reveal", {"clues": {"add": ["mill_wheel_is_boundary_symbol"]}}),
    beat("Tamsin unfolds a damaged map whose farmhouse square connects to seven northern circles.", "map insert with square, seven circles, and torn missing route", ["ADULT_TAMSIN_REEVE"], "MEDIUM_CHARACTER_CLUE", "LOW", ["ng-prop-damaged-node-map-r1"], "held_observation", {"props": {"add": ["damaged_node_map"]}, "clues": {"add": ["seven_node_chain"]}}),
    beat("Sigrid seats the brass key in the wheel only after Soren braces its seized axle.", "dual hand-tool-key action with no obscured contact points", ["ADULT_SOREN", "ADULT_SIGRID"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", ["ng-prop-brass-boundary-key-r1", "ng-clue-boundary-wheel-r1"], "synchronized_leverage"),
    beat("Frost-green words appear across the real brass and stone: GARDEN LEDGER — NODE WAKING.", "small physical inscription insert, restrained light, no floating interface", [], "SMALL_SENSORY_INSERT", "LOW", ["ng-progression-ui-garden-ledger-inscription-r1"], "surface_inscription", {"clues": {"add": ["garden_ledger_observed"]}}),
    beat("The Ledger offers a single keeper seal and names the farmhouse a shelter node.", "stone-and-brass text with one empty hand-shaped recess", [], "SMALL_OBJECT_INSERT", "LOW", ["ng-progression-ui-garden-ledger-inscription-r1"], "surface_inscription", {"clues": {"add": ["single_keeper_demand"]}}),
    beat("Soren reaches toward the recess; Sigrid catches his wrist before contact.", "tight two-hand interruption with both expressions visible", ["ADULT_SOREN", "ADULT_SIGRID"], "MEDIUM_TWO_SHOT", "MEDIUM", ["ng-clue-boundary-wheel-r1"], "target_change"),
    beat("Tamsin warns that the last keeper entered alone and never returned from the North Garden.", "low-density three-adult dialogue triangle with clear faces", ["ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE"], "MEDIUM_TWO_SHOT", "LOW", ["ng-prop-damaged-node-map-r1"], "held_observation", {"clues": {"add": ["last_keeper_missing_in_north_garden"]}}),
    beat("Soren and Sigrid refuse ownership and jointly declare the house a shelter under their care.", "balanced two-shot with both hands on opposite sides of the wheel", ["ADULT_SOREN", "ADULT_SIGRID"], "MEDIUM_TWO_SHOT", "MEDIUM", ["ng-clue-boundary-wheel-r1"], "declared_action"),
    beat("The wheel turns under two hands and the inscription changes from KEEPER to CUSTODIANS PENDING.", "wide causal resolution with both adults, turning wheel, and restrained surface text", ["ADULT_SOREN", "ADULT_SIGRID"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", ["ng-progression-ui-garden-ledger-inscription-r1", "ng-clue-boundary-wheel-r1"], "synchronized_leverage", {"clues": {"add": ["shared_custodian_exception"]}}),
    beat("Back upstairs, Sigrid rewraps Tamsin's leg while Soren banks the borrowed mill coal safely.", "calm three-adult recovery with medical hands and hearth objects unobscured", ["ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE"], "MEDIUM_SENSORY_REACTION", "LOW", ["ng-prop-tamsin-field-wrap-r1", "ng-set-farmhouse-hearth-r1"], "held_observation", {"locations": {"set": ["farmhouse_hearth"]}}),
    beat("They adopt a new rule: no one crosses an unknown threshold without stating the plan.", "quiet seated three-shot with visual space for short dialogue above", ["ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE"], "MEDIUM_TWO_SHOT", "LOW", ["ng-set-farmhouse-hearth-r1"], "held_observation", {"clues": {"add": ["threshold_rule_adopted"]}}),
    beat("The damaged map answers the active cellar wheel by lighting seven faint northern nodes.", "small map insert with seven physical frost-green points", [], "SMALL_SENSORY_INSERT", "LOW", ["ng-prop-damaged-node-map-r1", "ng-progression-ui-garden-ledger-inscription-r1"], "surface_inscription"),
    beat("A new mark ignites just outside the farmhouse gate and crawls toward the orchard.", "map-to-window composition linking physical mark and exterior geography", ["ADULT_SIGRID"], "MEDIUM_CHARACTER_CLUE", "MEDIUM", ["ng-prop-damaged-node-map-r1", "ng-set-farmhouse-window-r1"], "directional_motion", {"clues": {"add": ["approaching_orchard_weight"]}}),
    beat("Beyond the glass, orchard mud bulges under something heavy moving toward the house.", "wide exterior omen with moving mud ridge, gate, and no creature reveal", [], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", ["ng-set-farmhouse-orchard-r1", "ng-clue-moving-mud-ridge-r1"], "ground_displacement", {"wardrobe": {"set": ["soren_oatmeal_coat_damp_and_torn", "sigrid_plaid_wrap_damp_and_scorched_edge"]}, "locations": {"set": ["farmhouse_hearth_orchard_threat"]}}),
]


CH07_BEATS = [
    beat("Storm rain strikes the orchard while the moving mud ridge turns toward the stone gate.", "wide farmhouse-to-gate geography with threat vector and three adults at shelter", ["ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", ["ng-set-farmhouse-orchard-r1", "ng-clue-moving-mud-ridge-r1"], "directional_motion", {"locations": {"set": ["farmhouse_orchard_gate"]}, "weather": {"set": ["hard_afternoon_storm"]}}),
    beat("Tamsin names the buried shape a Mireback and warns that active ward ground feeds its peat armor.", "three-adult interior-exterior line with Tamsin pointing from support", ["ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE"], "MEDIUM_TWO_SHOT", "MEDIUM", ["ng-progression-monster-mireback-r1", "ng-prop-damaged-node-map-r1"], "held_observation", {"clues": {"add": ["mireback_feeds_on_active_ward_ground"]}}),
    beat("Sigrid maps a retreat lane, a firing lane, and one drainage ditch that crosses both.", "overhead yard plan scratched in ash with three route lines", ["ADULT_SIGRID"], "MEDIUM_CHARACTER_CLUE", "LOW", ["ng-prop-yard-ash-map-r1"], "held_observation", {"clues": {"add": ["orchard_defense_routes"]}}),
    beat("Soren tests the hay fork, pruning hook, gatepost, and ditch bank as one mechanical system.", "medium causal inventory with each tool and fulcrum relation readable", ["ADULT_SOREN"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", ["ng-prop-hay-fork-r1", "ng-prop-pruning-hook-r1", "ng-set-stone-gate-r1"], "held_observation"),
    beat("They declare the defense: Sigrid controls its path, Soren controls the ground, and Tamsin guards the threshold.", "balanced three-shot with each adult assigned a visible station", ["ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE"], "MEDIUM_TWO_SHOT", "LOW", ["ng-set-farmhouse-yard-r1"], "declared_action", {"clues": {"add": ["declared_mireback_defense_plan"]}}),
    beat("Soren slides the pruning hook over the hay-fork shaft to gain reach without adding dead weight.", "close hands and nested tool geometry", ["ADULT_SOREN"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", ["ng-progression-weapon-wardens-reach-r1"], "tool_assembly"),
    beat("He wedges the joint with a split roof peg and binds it using the recovered mill twine.", "object insert with wedge, wrap direction, and knot sequence", ["ADULT_SOREN"], "SMALL_OBJECT_INSERT", "LOW", ["ng-progression-weapon-wardens-reach-r1", "ng-clue-soot-twine-r1"], "tool_assembly"),
    beat("Soren loads the polehook against the gatepost and proves the shaft will carry his weight.", "tall leverage test with feet, shaft, hook, and gatepost aligned", ["ADULT_SOREN"], "MEDIUM_SINGLE_CAUSAL", "HIGH", ["ng-progression-weapon-wardens-reach-r1", "ng-set-stone-gate-r1"], "weight_shift", {"props": {"add": ["improvised_wardens_reach"]}}),
    beat("Tamsin lends Sigrid a compact recurved bow and exactly five usable arrows.", "clear handoff with bow, five shafts, and both adult faces visible", ["ADULT_SIGRID", "ADULT_TAMSIN_REEVE"], "MEDIUM_TWO_SHOT", "MEDIUM", ["ng-progression-weapon-compact-bow-loan-r1"], "object_handoff", {"props": {"add": ["tamsin_compact_bow", "five_arrows"]}}),
    beat("Sigrid plants two cloth markers that keep Soren out of her firing lane.", "wide tactical yard view with markers, lane, and separated roles", ["ADULT_SOREN", "ADULT_SIGRID"], "WIDE_DIRECTIONAL_ANCHOR", "MEDIUM", ["ng-prop-route-cloth-markers-r1"], "directional_motion", {"props": {"add": ["two_route_markers"]}}),
    beat("The Mireback erupts from the orchard in a mass of peat, root, and slate-heavy forelimbs.", "large creature reveal with mature adults small but readable behind the gate", ["ADULT_SOREN", "ADULT_SIGRID"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", ["ng-progression-monster-mireback-r1", "ng-set-farmhouse-orchard-r1"], "ground_displacement"),
    beat("Rain sheets off overlapping peat plates while root fibers tighten across its joints.", "monster material insert showing construction rather than gore", [], "SMALL_SENSORY_INSERT", "MEDIUM", ["ng-progression-monster-mireback-r1"], "material_tension", {"clues": {"add": ["mireback_material_layers"]}}),
    beat("Sigrid's first arrow strikes slate and glances away without slowing it.", "longitudinal action line with arrow impact and safe silhouette separation", ["ADULT_SIGRID"], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", ["ng-progression-monster-mireback-r1", "ng-progression-weapon-compact-bow-loan-r1"], "projectile_impact", {"props": {"remove": ["five_arrows"], "add": ["four_arrows"]}}),
    beat("Soren hooks a dead branch and drags it across the creature's path to turn its head.", "dual causal frame with polehook, branch drag, and changed monster vector", ["ADULT_SOREN"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", ["ng-progression-monster-mireback-r1", "ng-progression-weapon-wardens-reach-r1"], "leverage"),
    beat("The Mireback hits the stone gate instead of the farmhouse door and cracks the outer pier.", "wide impact with displaced stones, clear gate geometry, and no generic speed lines", [], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", ["ng-progression-monster-mireback-r1", "ng-set-stone-gate-r1"], "impact", {"clues": {"add": ["outer_gate_pier_cracked"]}}),
    beat("Soren opens the upper irrigation gate and sends storm water down the orchard furrow.", "hand-gate-water causal close with flow direction visible", ["ADULT_SOREN"], "MEDIUM_SINGLE_CAUSAL", "MEDIUM", ["ng-prop-irrigation-gate-r1"], "water_release"),
    beat("The water reaches the drainage ditch and turns its packed edge into sliding mud.", "people-free environmental motion insert linking channel to ditch bank", [], "WIDE_ENVIRONMENTAL_MOTION", "MEDIUM", ["ng-set-orchard-drainage-r1"], "water_flow", {"clues": {"add": ["ditch_bank_saturated"]}}),
    beat("Sigrid moves the nearer cloth marker two paces, narrowing the creature's safe route.", "tall action with her grounded reach, marker, and approaching mass separated", ["ADULT_SIGRID"], "MEDIUM_SINGLE_CAUSAL", "HIGH", ["ng-prop-route-cloth-markers-r1", "ng-progression-monster-mireback-r1"], "target_change"),
    beat("She lands an arrow in the soft peat beside its eye, turning it toward the marked gap.", "medium action with exact soft target and visible turn response", ["ADULT_SIGRID"], "MEDIUM_SINGLE_CAUSAL", "HIGH", ["ng-progression-monster-mireback-r1", "ng-progression-weapon-compact-bow-loan-r1"], "projectile_impact", {"props": {"remove": ["four_arrows"], "add": ["three_arrows"]}}),
    beat("Its slate forelimb crosses the ditch and the saturated bank collapses under the load.", "wide ground-failure anchor with weight transfer and sinking limb", [], "WIDE_ENVIRONMENTAL_MOTION", "HIGH", ["ng-progression-monster-mireback-r1", "ng-set-orchard-drainage-r1"], "weight_drop"),
    beat("The trapped forelimb exposes a pale root-knot behind the slate shoulder.", "medium monster clue with knot location and joint relationship explicit", [], "MEDIUM_CHARACTER_CLUE", "MEDIUM", ["ng-progression-monster-mireback-r1"], "held_reveal", {"clues": {"add": ["mireback_root_knot_exposed"]}}),
    beat("Soren seats the polehook behind the root-knot and braces the shaft against the gatepost.", "continuous hook-knot-shaft-post leverage path", ["ADULT_SOREN"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", ["ng-progression-monster-mireback-r1", "ng-progression-weapon-wardens-reach-r1", "ng-set-stone-gate-r1"], "leverage"),
    beat("The Mireback twists and drags Soren one boot-length through mud, tearing his coat sleeve.", "grounded resistance with mud furrow, taut shaft, and cloth tear", ["ADULT_SOREN"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", ["ng-progression-monster-mireback-r1", "ng-progression-weapon-wardens-reach-r1"], "weight_shift", {"wardrobe": {"set": ["soren_oatmeal_coat_torn_sleeve", "sigrid_plaid_wrap_damp"]}}),
    beat("Sigrid shoots the tension root above Soren's hook rather than the armored body.", "targeted arrow close with root under tension and Soren clear of line", ["ADULT_SOREN", "ADULT_SIGRID"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", ["ng-progression-monster-mireback-r1", "ng-progression-weapon-compact-bow-loan-r1", "ng-progression-weapon-wardens-reach-r1"], "projectile_impact", {"props": {"remove": ["three_arrows"], "add": ["two_arrows"]}}),
    beat("At Sigrid's count, Soren shifts from pulling the creature to levering the knot against stone.", "dual reaction-action panel with spoken timing and changed force direction", ["ADULT_SOREN", "ADULT_SIGRID"], "MEDIUM_SENSORY_REACTION", "HIGH", ["ng-progression-monster-mireback-r1", "ng-progression-weapon-wardens-reach-r1"], "synchronized_leverage"),
    beat("Sigrid plants both boots on the gate brace and adds her weight to the polehook shaft.", "tall dual leverage with both adults, grounded feet, and unobscured hands", ["ADULT_SOREN", "ADULT_SIGRID"], "TALL_OR_WIDE_DUAL_CAUSAL", "HIGH", ["ng-progression-monster-mireback-r1", "ng-progression-weapon-wardens-reach-r1"], "synchronized_leverage"),
    beat("The cracked gatepost becomes a fulcrum and the exposed root-knot lifts clear of the peat plates.", "mechanical reveal with post, shaft, hook, knot, and lifted armor layers", [], "MEDIUM_SINGLE_CAUSAL", "HIGH", ["ng-progression-monster-mireback-r1", "ng-set-stone-gate-r1"], "leverage"),
    beat("They rotate together; the root-knot tears free and the Mireback's weight settles harmlessly into mud.", "wide climax with rotational force, collapsing peat mass, and no gore", ["ADULT_SOREN", "ADULT_SIGRID"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", ["ng-progression-monster-mireback-r1", "ng-progression-weapon-wardens-reach-r1"], "weight_release", {"clues": {"add": ["first_mireback_defeated_by_leverage"]}}),
    beat("Rain washes loose peat from the still slate frame while new shoots uncurl from the severed knot.", "quiet aftermath insert suggesting ecology rather than trophy violence", [], "SMALL_SENSORY_INSERT", "LOW", ["ng-progression-monster-mireback-r1"], "environmental_change", {"clues": {"add": ["mireback_regrowth_after_defeat"]}}),
    beat("Frost-green words form on Warden's Reach and the wet gate: SHELTER HELD — AFFINITIES OBSERVED.", "physical inscription across tool and stone with restrained glow", ["ADULT_SOREN", "ADULT_SIGRID"], "MEDIUM_SENSORY_REACTION", "LOW", ["ng-progression-ui-shelter-held-r1", "ng-progression-weapon-wardens-reach-r1"], "surface_inscription", {"clues": {"add": ["shelter_held_affinities_observed"]}}),
    beat("Tamsin confirms the Mireback is dormant, not cleanly dead, and marks its regrowing roots.", "adult kneeling inspection with hands away from the root-knot", ["ADULT_TAMSIN_REEVE"], "MEDIUM_CHARACTER_CLUE", "MEDIUM", ["ng-progression-monster-mireback-r1", "ng-prop-damaged-node-map-r1"], "held_observation"),
    beat("Soren binds his torn oatmeal sleeve around the cracked polehook grip.", "quiet hand-and-cloth repair insert preserving oatmeal color identity", ["ADULT_SOREN"], "MEDIUM_SINGLE_CAUSAL", "LOW", ["ng-progression-weapon-wardens-reach-r1"], "tool_repair"),
    beat("Sigrid finds a scorched edge on her plaid where the gate lantern burst during the struggle.", "medium wardrobe continuity check with face and damaged plaid edge clear", ["ADULT_SIGRID"], "MEDIUM_CHARACTER_CLUE", "LOW", ["ng-prop-gate-lantern-r1"], "held_observation", {"wardrobe": {"set": ["soren_oatmeal_coat_torn_sleeve", "sigrid_plaid_wrap_scorched_edge"]}}),
    beat("Inside the wall, the farmhouse wardstone opens a crack from top to base.", "small stone fracture insert with no exaggerated light", [], "SMALL_OBJECT_INSERT", "LOW", ["ng-clue-cracked-farmhouse-wardstone-r1"], "material_failure", {"clues": {"add": ["farmhouse_wardstone_cracked"]}}),
    beat("Tamsin says the next attack will feed through that crack unless they repair the northern chain.", "three-adult consequence frame with cracked stone between them", ["ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE"], "MEDIUM_TWO_SHOT", "MEDIUM", ["ng-clue-cracked-farmhouse-wardstone-r1", "ng-prop-damaged-node-map-r1"], "held_observation"),
    beat("The damaged node map brightens as rainwater connects its farmhouse square to seven circles.", "map insert with physical water track and seven distinct nodes", [], "SMALL_SENSORY_INSERT", "LOW", ["ng-prop-damaged-node-map-r1", "ng-progression-ui-shelter-held-r1"], "surface_inscription"),
    beat("Six lights remain faint; the nearest northern circle pulses hard enough to shake a drop from the page.", "tight map detail with one pulsing circle and six faint marks", [], "SMALL_SENSORY_INSERT", "LOW", ["ng-prop-damaged-node-map-r1"], "object_vibration"),
    beat("The nearest light gutters while Soren and Sigrid watch from opposite sides of the map.", "balanced reaction two-shot with map centered and both faces readable", ["ADULT_SOREN", "ADULT_SIGRID"], "MEDIUM_TWO_SHOT", "MEDIUM", ["ng-prop-damaged-node-map-r1"], "held_observation"),
    beat("The northern light goes dark, leaving a root-shaped stain across the route.", "silent map insert with extinguished circle and spreading stain", [], "SMALL_OBJECT_INSERT", "LOW", ["ng-prop-damaged-node-map-r1"], "surface_change", {"clues": {"add": ["nearest_northern_node_failed"]}}),
    beat("They decide to leave at dawn: Sigrid will choose the road, Soren will carry the means to hold it, and Tamsin will guide them north.", "wide storm-clearing threshold tableau with three adults, repaired tool, bow, and northward map vector", ["ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE"], "WIDE_DIRECTIONAL_ANCHOR", "HIGH", ["ng-progression-weapon-wardens-reach-r1", "ng-progression-weapon-compact-bow-loan-r1", "ng-prop-damaged-node-map-r1"], "declared_action", {"locations": {"set": ["farmhouse_gate_after_first_defense"]}, "clues": {"add": ["northward_departure_committed"]}}),
]


def initial_state(chapter_id: str) -> dict[str, list[str]]:
    if chapter_id == "CH06":
        return {
            "characters": ["ADULT_SOREN", "ADULT_SIGRID"],
            "wardrobe": ["soren_oatmeal_coat_damp", "sigrid_plaid_wrap_damp"],
            "injuries": [],
            "props": ["folded_map", "pocket_knife"],
            "locations": ["ridge_return_from_mill"],
            "weather": ["clearing_wet_morning"],
            "clues": ["mill_signal", "farmhouse_chimney_newly_smoking"],
        }
    return {
        "characters": ["ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE"],
        "wardrobe": ["soren_oatmeal_coat_damp_and_torn", "sigrid_plaid_wrap_damp_and_scorched_edge"],
        "injuries": ["tamsin_lower_leg_crush_injury_freed"],
        "props": ["folded_map", "pocket_knife", "brass_boundary_key", "damaged_node_map", "oil_lamp"],
        "locations": ["farmhouse_hearth_orchard_threat"],
        "weather": ["storm_arriving"],
        "clues": [
            "garden_ledger_observed",
            "seven_node_chain",
            "shared_custodian_exception",
            "approaching_orchard_weight",
            "threshold_rule_adopted",
        ],
    }


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
        "ADULT_SOREN": "ng-identity-soren-fictional-design-r1",
        "ADULT_SIGRID": "ng-identity-sigrid-fictional-design-r1",
        "ADULT_TAMSIN_REEVE": "ng-identity-tamsin-fictional-adult-r1",
    }
    return [mapping[role] for role in cast]


def build_chapter(
    chapter_id: str,
    arc_chapter: dict[str, Any],
    initial_override: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    beats = CH06_BEATS if chapter_id == "CH06" else CH07_BEATS
    sequence_specs = CH06_SEQUENCES if chapter_id == "CH06" else CH07_SEQUENCES
    roles = ["ADULT_SOREN", "ADULT_SIGRID", "ADULT_TAMSIN_REEVE"]
    state = copy.deepcopy(initial_override) if initial_override is not None else initial_state(chapter_id)
    plans: list[dict[str, Any]] = []
    for index, source in enumerate(beats, start=1):
        sequence_index = (index - 1) // 5
        sequence_slug, _, phase_id = sequence_specs[sequence_index]
        carry_in = copy.deepcopy(state)
        state = apply_updates(state, source["updates"])
        carry_out = copy.deepcopy(state)
        panel_id = f"ng-{chapter_id.lower()}-sc01-p{index:03d}"
        safe_anchor = "top_left" if index % 2 else "top_right"
        safe_zone = [0.04, 0.04, 0.34, 0.20] if safe_anchor == "top_left" else [0.66, 0.04, 0.96, 0.20]
        plans.append(
            {
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
                    "lettering": {
                        "state": "SAFE_ZONE_PLANNED_COPY_NOT_YET_AUTHORED",
                        "placement_policy": "safe_zone",
                        "safe_zones": [{"anchor": safe_anchor, "rect_norm": safe_zone}],
                        "protected_subjects": ["faces", "adult silhouettes", "important hands", "weapons and tools", "story objects"],
                    },
                },
            }
        )
    sequences = []
    for order, (slug, title, phase_id) in enumerate(sequence_specs, start=1):
        subset = plans[(order - 1) * 5 : order * 5]
        sequences.append(
            {
                "sequence_id": f"ng-{chapter_id.lower()}-{slug}",
                "narrative_order": order,
                "title": title,
                "narrative_functions": [PHASE_FUNCTIONS[phase_id]],
                "panel_ids": [panel["panel_id"] for panel in subset],
                "continuity_entry": copy.deepcopy(subset[0]["continuity_carry_in"]),
                "continuity_exit": copy.deepcopy(subset[-1]["continuity_carry_out"]),
            }
        )
    progression = {key: None for key in ("armor", "weapons", "upgraded_clothing", "monsters", "classes", "system_ui")}
    if chapter_id == "CH06":
        progression["system_ui"] = {
            "canon_decision": "ADR-0196",
            "asset_ids": ["ng-progression-ui-garden-ledger-inscription-r1"],
        }
    else:
        progression["weapons"] = {
            "canon_decision": "ADR-0196",
            "asset_ids": ["ng-progression-weapon-wardens-reach-r1", "ng-progression-weapon-compact-bow-loan-r1"],
        }
        progression["monsters"] = {
            "canon_decision": "ADR-0196",
            "asset_ids": ["ng-progression-monster-mireback-r1"],
        }
        progression["system_ui"] = {
            "canon_decision": "ADR-0196",
            "asset_ids": ["ng-progression-ui-shelter-held-r1"],
        }
    return {
        "record_type": "ComicPanelPlanCollection",
        "schema_version": "2.0",
        "record_id": f"ng-comic-plans-{chapter_id.lower()}-sc01-r1",
        "state": "AUTHORING_COMPLETE_NOT_PROMOTED_PROVISIONAL_CANON",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "chapter_title": arc_chapter["title"],
        "chapter_logline": arc_chapter["logline"],
        "story_state_id": f"ng-story-{chapter_id.lower()}-sc01-r1",
        "opening_state": arc_chapter["opening_state_key"],
        "closing_changed_state": arc_chapter["closing_state_key"],
        "declared_target_panel_count": 40,
        "fictional_adult_roles": roles,
        "identity_contract": {
            "SOREN": "light-brown/dark-blond swept-back hair; pale oatmeal work coat",
            "SIGRID": "dark-brown/near-black tied-back hair; dark blue-brown plaid wrap",
            "TAMSIN_REEVE": "clearly fictional adult courier-cartographer; practical non-sexualized field clothing",
        },
        "continuity_contract": {
            "initial_state": copy.deepcopy(plans[0]["continuity_carry_in"]),
            "final_state": copy.deepcopy(plans[-1]["continuity_carry_out"]),
        },
        "progression_contract": progression,
        "narrative_phases": [
            {"phase_id": phase_id, "narrative_function": narrative_function}
            for phase_id, narrative_function in PHASE_FUNCTIONS.items()
        ],
        "sequences": sequences,
        "plans": plans,
        "promotion_decision": None,
        "execution_ready": False,
        "authoring_complete": True,
        "anti_duplication": {
            "default_candidates_per_panel": 1,
            "alternate_style_before_complete_chapter": False,
            "targeted_repair_cap_per_failed_panel": 2,
        },
    }


def story_state(chapter_id: str, arc_chapter: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_type": "StoryState",
        "schema_version": "1.0",
        "record_id": f"ng-story-{chapter_id.lower()}-sc01-r1",
        "scope": f"{chapter_id}_SC01_PROVISIONAL_CANON_AUTHORING_COMPLETE_NOT_RENDER_PROMOTED",
        "fictional_cast": plan["fictional_adult_roles"],
        "set": arc_chapter["primary_location"],
        "timeline_state": arc_chapter["timeline"],
        "opening_state": arc_chapter["opening_state_key"],
        "closing_changed_state": arc_chapter["closing_state_key"],
        "narrative_state": arc_chapter["logline"],
        "state_delta": arc_chapter["state_delta"],
        "continuity_final_state": plan["continuity_contract"]["final_state"],
        "promotion_decision": None,
        "source_limit": "Provisional canon-development authoring record under ADR-0196; no render, acceptance, rights, exact-base, or cross-medium authority.",
    }


def scene_beat(chapter_id: str, arc_chapter: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_type": "SceneBeat",
        "schema_version": "1.0",
        "record_id": f"ng-beat-{chapter_id.lower()}-sc01-r1",
        "story_state_id": f"ng-story-{chapter_id.lower()}-sc01-r1",
        "chapter_question": arc_chapter["chapter_question"],
        "narrative_intent": arc_chapter["logline"],
        "causal_setpieces": arc_chapter["causal_setpieces"],
        "closing_hook": arc_chapter["closing_hook"],
        "comic_direction_boundary": "Direction is contained in ComicPanelPlan; AnimationShotPlan and E-Conte are absent/null.",
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    arc = json.loads(ARC_PATH.read_text(encoding="utf-8"))
    chapter_sources = {chapter["chapter_id"]: chapter for chapter in arc["chapters"]}
    plans: dict[str, dict[str, Any]] = {}
    for chapter_id in ("CH06", "CH07"):
        initial_override = plans["CH06"]["continuity_contract"]["final_state"] if chapter_id == "CH07" else None
        plans[chapter_id] = build_chapter(chapter_id, chapter_sources[chapter_id], initial_override)
        for path, payload in (
            (OUTPUTS[chapter_id], plans[chapter_id]),
            (STORY_OUTPUTS[chapter_id], story_state(chapter_id, chapter_sources[chapter_id], plans[chapter_id])),
            (BEAT_OUTPUTS[chapter_id], scene_beat(chapter_id, chapter_sources[chapter_id])),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    lines = [
        "# CH06–CH07 complete ComicPanelPlan authoring r1",
        "",
        "The first Bell Road batch contains two complete chronological chapter graphs before any render prompt promotion.",
        "",
        "| Chapter | Panels | Sequences | Opening | Closing |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for chapter_id in ("CH06", "CH07"):
        plan = plans[chapter_id]
        lines.append(
            f"| {chapter_id} — {plan['chapter_title']} | {len(plan['plans'])} | {len(plan['sequences'])} | {plan['opening_state']} | {plan['closing_changed_state']} |"
        )
    lines.extend(
        [
            "",
            "CH06 continues directly from CH05's smoking-farmhouse reversal, reveals the Garden Ledger through a physical cellar mechanism, and ends with a threat moving through the orchard. CH07 carries that exact state into a practical Mireback defense and ends with an irreversible ward crack plus a northward departure decision.",
            "",
            "Both chapters use eight contiguous five-panel sequences, all six required narrative phases, explicit panel-to-panel continuity, fixed adult hair/wardrobe anchors, normalized lettering-safe zones, one-candidate-per-panel defaults, and no render/provider fields.",
            "",
            "No prompt, provider call, upload, generated candidate, acceptance, commercial decision, exact-base decision, AnimationShotPlan, or E-Conte record is created.",
            "",
        ]
    )
    MARKDOWN_OUTPUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "chapters": 2,
                "panels": sum(len(plan["plans"]) for plan in plans.values()),
                "sequences": sum(len(plan["sequences"]) for plan in plans.values()),
                "hashes": {path.relative_to(ROOT).as_posix(): sha256(path) for path in [*OUTPUTS.values(), *STORY_OUTPUTS.values(), *BEAT_OUTPUTS.values(), MARKDOWN_OUTPUT]},
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
