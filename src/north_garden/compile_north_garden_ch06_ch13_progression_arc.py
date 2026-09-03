"""Compile the breadth-first North Garden CH06-CH13 progression arc."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
JSON_OUTPUT = ROOT / "production/canon/story-arcs/north-garden-ch06-ch13-progression-r1.json"
MARKDOWN_OUTPUT = ROOT / "docs/research/north-garden-ch06-ch13-progression-plan-r1.md"


IDENTITY_CONTRACT = {
    "SOREN": {
        "presentation": "clearly fictional adult with mature proportions",
        "hair": "light-brown to dark-blond, short-to-medium wavy and swept back; never black or bright blond",
        "visual_anchor": "pale oatmeal work coat evolves visibly through repairs and protective reinforcement",
    },
    "SIGRID": {
        "presentation": "clearly fictional adult with mature proportions",
        "hair": "dark-brown to near-black, compact low bun or practical braid; never blond or loose red curls",
        "visual_anchor": "dark blue-brown plaid wrap remains recognizable as it evolves into a weather cape",
    },
}


CHAPTERS: list[dict[str, Any]] = [
    {
        "chapter_id": "CH06",
        "title": "The House That Answered",
        "timeline": "DAY_01_LATE_MORNING_IMMEDIATELY_AFTER_CH05",
        "primary_location": "SMOKING_FARMHOUSE_AND_DORMANT_THRESHOLD_CELLAR",
        "opening_state_key": "CH05_RETURN_TO_UNEXPECTEDLY_ACTIVE_FARMHOUSE",
        "closing_state_key": "FARMHOUSE_IDENTIFIED_AS_BOUNDARY_NODE_TAMSIN_SHELTERED",
        "logline": "Soren and Sigrid return to a smoking farmhouse, outmaneuver its bell-and-twine defenses, and find wounded adult courier Tamsin Reeve beside a brass boundary key that makes the house answer them.",
        "chapter_question": "Who entered their home, and why did the mill signal lead them back?",
        "causal_setpieces": [
            "Sigrid reads wet boot pressure and enters through the pantry while Soren holds the visible door.",
            "The mill twine pattern triggers a cellar latch; both must release the counterweighted beam without crushing Tamsin's trapped leg.",
            "The brass key touches the cold hearthstone and produces the first restrained Garden Ledger inscription.",
        ],
        "state_delta": {
            "goal": "Protect the farmhouse becomes learn why it is one node in a failing boundary network.",
            "relationship": "They replace unspoken assumptions with an explicit rule: state the plan before crossing a threshold.",
            "ally": "TAMSIN_REEVE, a clearly fictional adult courier-cartographer, becomes a guarded temporary ally.",
            "world_knowledge": "The mill signal was a maintenance alarm for linked boundary sites.",
            "system": "The Garden Ledger becomes observable through brass, hearthstone, and shared custodial action.",
            "equipment": "They acquire a brass boundary key and Tamsin's damaged node map.",
            "wardrobe": "Existing oatmeal coat and plaid wrap remain unchanged but become wet, torn, and narratively repairable.",
        },
        "closing_hook": "A second boundary mark ignites on the map just beyond the farmhouse gate while something heavy moves in the orchard mud.",
    },
    {
        "chapter_id": "CH07",
        "title": "Mireback at the Gate",
        "timeline": "DAY_01_AFTERNOON_STORM",
        "primary_location": "FARMHOUSE_ORCHARD_STONE_GATE_AND_DRAINAGE_DITCH",
        "opening_state_key": "FARMHOUSE_IDENTIFIED_AS_BOUNDARY_NODE_TAMSIN_SHELTERED",
        "closing_state_key": "FIRST_MIREBACK_DEFEATED_FARMHOUSE_WARD_CRACKED",
        "logline": "A peat-root Mireback follows the activated key to the farmhouse, forcing the pair to turn farm tools, drainage, mud, and each other's timing into their first deliberate monster defense.",
        "chapter_question": "Can practical cooperation defeat a creature that grows stronger on defended ground?",
        "causal_setpieces": [
            "Soren converts a hay fork and pruning hook into a long-reach polehook while Sigrid marks safe firing lanes.",
            "Sigrid draws the Mireback across a saturated ditch; Soren collapses the bank so its slate-heavy forelimb sinks.",
            "They lever the exposed root-knot against the gatepost instead of winning through generic spectacle.",
        ],
        "state_delta": {
            "capability": "Soren demonstrates field engineering under attack; Sigrid establishes tactical path control.",
            "weapons": "Soren gains an improvised polehook; Sigrid recovers Tamsin's compact recurved bow under explicit loan.",
            "monster_knowledge": "Mirebacks carry peat armor, slate joints, a vulnerable root-knot, and can feed on active boundary ground.",
            "system": "Ledger records Shelter Held and offers affinities rather than unexplained levels.",
            "relationship": "They trust spoken timing during lethal action for the first time.",
            "consequence": "The farmhouse wardstone cracks; staying home is no longer safe.",
            "wardrobe": "Soren's coat sleeve tears and Sigrid's plaid edge is scorched, creating visible continuity into repair.",
        },
        "closing_hook": "The node map reveals seven failing lights leading north, and the nearest extinguishes while they watch.",
    },
    {
        "chapter_id": "CH08",
        "title": "The Root Road",
        "timeline": "DAY_02_DAWN_TO_DUSK",
        "primary_location": "OLD_ROOT_ROAD_WARDEN_CAIRNS_AND_WINDTHROWN_FOREST",
        "opening_state_key": "FIRST_MIREBACK_DEFEATED_FARMHOUSE_WARD_CRACKED",
        "closing_state_key": "PAIR_COMMITTED_TO_NORTHWARD_NODE_ROUTE_HOLLOW_STAG_SPARED",
        "logline": "Leaving the damaged farmhouse behind, Soren and Sigrid follow the failing node road, test repaired field armor, and learn that not every system-marked creature is an enemy.",
        "chapter_question": "Will they treat the Ledger as a hunting system or learn what its marks actually mean?",
        "causal_setpieces": [
            "They repair Soren's coat with quilted shoulder panels and re-cut Sigrid's plaid into a secured weather cape without losing either silhouette.",
            "A Hollow Stag drives them toward a windthrown ravine; Sigrid notices it is steering them away from a collapsing root bridge.",
            "Soren braces the bridge with the polehook while Sigrid cuts a trapped antler free from boundary wire.",
        ],
        "state_delta": {
            "goal": "Following one alarm becomes a voluntary northward mission to stabilize the seven-node chain.",
            "wardrobe": "Oatmeal coat gains quilted reinforcement; plaid wrap becomes a mobile weather cape over dark practical layers.",
            "armor": "Both gain light, work-derived protection rather than knightly costume.",
            "capability": "Sigrid begins reading route intent; Soren begins shaping temporary load-bearing wards.",
            "monster_knowledge": "Ledger marks indicate ecological role and boundary stress, not automatic hostility.",
            "relationship": "Sigrid challenges Soren's threat assumption and he changes course on evidence.",
            "world_knowledge": "The old road was built to connect cultivated safe zones called Gardens.",
        },
        "closing_hook": "The spared stag stamps a route glyph pointing below the black weir, where the next node pulses underwater.",
    },
    {
        "chapter_id": "CH09",
        "title": "Below the Black Weir",
        "timeline": "DAY_02_NIGHT",
        "primary_location": "FLOODED_WEIR_TUNNELS_AND_SUBMERGED_BOUNDARY_CHAMBER",
        "opening_state_key": "PAIR_COMMITTED_TO_NORTHWARD_NODE_ROUTE_HOLLOW_STAG_SPARED",
        "closing_state_key": "WEIR_NODE_STABILIZED_SOREN_INJURED_SIGRID_WAYFINDER_AWAKENED",
        "logline": "At the drowned node beneath the weir, Sigrid must navigate by current and echo while an injured Soren holds a failing gate long enough for her to redraw the route.",
        "chapter_question": "Can Sigrid lead them through a place where the map is physically wrong?",
        "causal_setpieces": [
            "Sigrid uses floating chaff, wall condensation, and echo delay to identify the true flooded passage.",
            "A sluice collapse pins Soren's lower leg; he builds a brace from polehook, belt, and gate iron while she redirects the current.",
            "Sigrid walks the submerged boundary line and awakens Wayfinder only after completing the route under pressure.",
        ],
        "state_delta": {
            "injury": "Soren leaves with a painful braced lower-leg injury that affects stance and speed in later chapters.",
            "class": "Sigrid earns the provisional Wayfinder path through navigation and rescue, not combat points.",
            "capability": "She can perceive stressed routes as brief frost-green lines on real surfaces.",
            "equipment": "The polehook becomes a damaged but system-recognized Warden's Reach tool.",
            "relationship": "Operational leadership shifts to Sigrid while Soren is injured.",
            "world_knowledge": "Someone deliberately altered the physical map plates beneath the weir.",
            "threat": "Human sabotage enters the causal chain alongside monsters.",
        },
        "closing_hook": "The false map bears the stamped seal of Brackenwake, the settlement controlling the only forge north of the weir.",
    },
    {
        "chapter_id": "CH10",
        "title": "Iron for a Name",
        "timeline": "DAY_03",
        "primary_location": "BRACKENWAKE_QUARRY_SETTLEMENT_FORGE_AND_COUNCIL_YARD",
        "opening_state_key": "WEIR_NODE_STABILIZED_SOREN_INJURED_SIGRID_WAYFINDER_AWAKENED",
        "closing_state_key": "BRIAR_COMPACT_BARGAIN_STRUCK_Kest_EXPOSED_AS_RIVAL_NOT_YET_ENEMY",
        "logline": "At Brackenwake, the pair trade a repaired ward engine for medicine and iron, while Sigrid forces Compact marshal Halvor Kest to admit he redirected the weir map to protect the settlement.",
        "chapter_question": "What are protection and truth worth when a whole settlement is afraid?",
        "causal_setpieces": [
            "Soren works seated around his injury, diagnosing a forge bellows whose failed counterweight is starving the ward engine.",
            "Sigrid reconstructs Kest's route deception in the council yard using the damaged plates and her new surface-line perception.",
            "They negotiate iron, medicine, and passage by repairing the engine without surrendering the brass key.",
        ],
        "state_delta": {
            "faction": "The Briar Compact becomes an uneasy political actor; HALVOR_KEST is established as a clearly fictional adult rival.",
            "equipment": "Warden's Reach gains a forged socket and hook; Sigrid gains her own compact bow and utility seax.",
            "armor": "Work-derived kits gain removable leather and iron protection while retaining oatmeal/plaid identity anchors.",
            "injury": "Soren receives a rigid brace but remains movement-limited.",
            "relationship": "They present a united bargaining position despite disagreeing privately about Kest.",
            "world_knowledge": "The Compact has been sacrificing outer nodes to keep Brackenwake lit.",
            "goal": "Stabilize nodes expands to prevent the Compact from abandoning isolated adults along the route.",
        },
        "closing_hook": "Every orchard ward in Brackenwake flares at once as Mirebacks rise from the drainage terraces.",
    },
    {
        "chapter_id": "CH11",
        "title": "The Orchard Siege",
        "timeline": "DAY_04_PREDAWN",
        "primary_location": "BRACKENWAKE_TERRACED_ORCHARDS_IRRIGATION_WALLS_AND_FORGE_ROOF",
        "opening_state_key": "BRIAR_COMPACT_BARGAIN_STRUCK_Kest_EXPOSED_AS_RIVAL_NOT_YET_ENEMY",
        "closing_state_key": "SIEGE_BROKEN_FORMAL_CLASSES_AND_SHARED_PARTY_BOND_EARNED",
        "logline": "Mirebacks attack across Brackenwake's terraces, and the pair must coordinate workers, water, firebreaks, and elevation into a defense large enough to earn names for what they have become.",
        "chapter_question": "Can two outsiders turn private competence into collective survival?",
        "causal_setpieces": [
            "Sigrid routes clearly fictional adult defenders through orchard lanes while keeping bow sightlines and retreat paths readable.",
            "Soren converts irrigation gates into sequential mud traps despite his brace, using leverage and timed releases.",
            "They expose the brood Mireback's root-knot from opposite elevations and let the settlement complete the takedown.",
        ],
        "state_delta": {
            "class": "Soren earns Hearth Warden; Sigrid advances to Thornpath Wayfinder.",
            "party": "They earn the shared bond Two Hands, One Threshold, which rewards declared complementary actions.",
            "leadership": "Both become publicly accountable leaders rather than solitary problem-solvers.",
            "faction": "A majority of the Briar Compact supports their northward mission; Kest loses unilateral control.",
            "capability": "Soren can anchor one temporary ward; Sigrid can mark one safe route visible to allies.",
            "consequence": "Brackenwake survives but its orchards and stored winter food are badly damaged.",
            "relationship": "Their trust becomes explicit and system-recognized, while remaining a partnership rather than an assumed romance.",
        },
        "closing_hook": "Tamsin admits the final map section was hidden because it leads to the sealed North Garden and the thing rooted beneath it.",
    },
    {
        "chapter_id": "CH12",
        "title": "The Map That Lied",
        "timeline": "DAY_04_NIGHT_TO_DAY_05_DAWN",
        "primary_location": "ASH_CUT_PASS_ABANDONED_WARDEN_CAMP_AND_SPLIT_BOUNDARY_TRAILS",
        "opening_state_key": "SIEGE_BROKEN_FORMAL_CLASSES_AND_SHARED_PARTY_BOND_EARNED",
        "closing_state_key": "TAMSIN_TRUTH_REVEALED_PARTNERS_RECONCILED_NORTH_GARDEN_GATE_OPEN",
        "logline": "Tamsin's concealed route splits the new alliance, and Soren and Sigrid must survive separate paths, confront why each mistakes control for protection, and reunite before the North Garden gate consumes its key.",
        "chapter_question": "Does their new bond survive the first truth neither partner can solve for the other?",
        "causal_setpieces": [
            "A false cairn sends Soren's heavier route across unstable ash while Sigrid's marked line enters a thorn maze.",
            "Soren sacrifices the reinforced oatmeal shoulder panel to splint a collapsing gate lever; Sigrid cuts and reties her plaid cape into route flags.",
            "They reunite by combining his audible hammer pattern with her visible path marks across the divided pass.",
        ],
        "state_delta": {
            "relationship": "A serious rupture over secrecy and control resolves into negotiated leadership boundaries, not instant forgiveness.",
            "ally": "Tamsin confesses she served the last North Garden keeper and concealed the route after that keeper was consumed.",
            "wardrobe": "Both signature garments acquire irreversible functional changes and visible damage before the climax.",
            "equipment": "The brass key fuses into Warden's Reach, making the tool the only remaining gate interface.",
            "system": "Two Hands, One Threshold temporarily breaks, then returns only after both state their intent without coercion.",
            "world_knowledge": "The Garden Ledger can turn a failed keeper into a rooted guardian rather than simply killing them.",
            "threat": "The Crownroot is identified as the transformed last keeper controlling the sealed Garden.",
        },
        "closing_hook": "The gate opens onto green summer beneath a winter sky, and the Crownroot speaks Soren's newly earned class name.",
    },
    {
        "chapter_id": "CH13",
        "title": "The North Garden",
        "timeline": "DAY_05",
        "primary_location": "SEALED_NORTH_GARDEN_GLASSHOUSE_ROOT_CISTERN_AND_BOUNDARY_HEART",
        "opening_state_key": "TAMSIN_TRUTH_REVEALED_PARTNERS_RECONCILED_NORTH_GARDEN_GATE_OPEN",
        "closing_state_key": "CROWNROOT_BOUND_PAIR_BECOME_CO_KEEPERS_WIDER_FAILURE_REVEALED",
        "logline": "Inside the impossible North Garden, Soren and Sigrid reject the Ledger's demand for one sacrificial keeper, bind the Crownroot through complementary craft and pathwork, and emerge as co-keepers of a living sanctuary.",
        "chapter_question": "Can they change a system built to consume one protector at a time?",
        "causal_setpieces": [
            "Sigrid navigates moving glasshouse paths while Soren anchors doors against root pressure, with each action enabling the other.",
            "The Crownroot attacks through soil, irrigation, and structural load; the fight is solved by redirecting water and tension rather than glowing force.",
            "Soren seats Warden's Reach in the boundary heart while Sigrid closes a seven-node route around both of them, forcing a shared-keeper outcome.",
        ],
        "state_delta": {
            "class": "Soren becomes Boundarywright Warden; Sigrid becomes Thornpath Marshal.",
            "party": "Two Hands, One Threshold matures into a persistent co-keeper covenant with explicit consent from both.",
            "leadership": "They take responsibility for North Garden and its connected adult settlements.",
            "home": "The farmhouse is no longer their only home; North Garden becomes a recoverable sanctuary and operational base.",
            "monster_knowledge": "Crownroot and Mirebacks are consequences of failed stewardship, allowing future threats to be fought, healed, or bargained with.",
            "equipment": "Warden's Reach becomes a boundary tool/weapon; Sigrid's bow and path marks become a command system for coordinated movement.",
            "relationship": "They end the arc as equal co-leaders with earned trust, defined conflict rules, and a shared future commitment.",
            "world_knowledge": "The seven local nodes are one branch of a much larger failing network, opening the next arc beyond North Garden.",
        },
        "closing_hook": "Distant branches appear across the restored map—one burning, one dark, and one moving toward them.",
    },
]


STRETCH_CHAPTERS = [
    {
        "chapter_id": "CH14",
        "title": "The Ash Census",
        "purpose": "Count the cost of restoration, recruit an adult core party, and make leadership materially burdensome.",
    },
    {
        "chapter_id": "CH15",
        "title": "The Road of Teeth",
        "purpose": "Leave the restored sanctuary, encounter a mobile predator ecology, and test whether co-keeper power works beyond owned ground.",
    },
    {
        "chapter_id": "CH16",
        "title": "The Lantern Court",
        "purpose": "Enter a major faction center where social leverage, class law, and competing Ledger interpretations matter more than monster strength.",
    },
    {
        "chapter_id": "CH17",
        "title": "Second Dawn",
        "purpose": "Force a public allegiance decision and launch the next large-scale conflict without erasing the consequences of CH06-CH13.",
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def document() -> dict[str, Any]:
    return {
        "record_type": "MultiChapterComicProgressionArc",
        "schema_version": "1.0",
        "record_id": "ng-story-arc-ch06-ch13-progression-r1",
        "state": "PROVISIONAL_CANON_DEVELOPMENT_AUTHORED_NOT_RENDER_PROMOTED",
        "arc_title": "The Bell Road",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "starts_from": {
            "chapter": "CH05",
            "story_state_id": "ng-story-ch05-sc01-r1",
            "closing_fact": "Soren and Sigrid return toward a farmhouse whose chimney has unexpectedly begun to smoke.",
        },
        "identity_contract": IDENTITY_CONTRACT,
        "system_direction": {
            "name": "Garden Ledger",
            "principle": "Land-bound progression responds to stewardship, declared cooperation, repair, navigation, and protection rather than unexplained kill points.",
            "visual_language": "Brief frost-green inscriptions appear on real brass, stone, water, glass, or repaired tools; no persistent floating HUD.",
            "progression_rule": "Every class, skill, bond, and item change must be earned by a visible causal action and persist afterward.",
        },
        "arc_outcome": "Across eight complete chapters, two isolated investigators become scarred, equipped, classed co-leaders responsible for a restored sanctuary and a wider failing network.",
        "production_target": {
            "required_complete_chapters": 8,
            "chapter_ids": [chapter["chapter_id"] for chapter in CHAPTERS],
            "target_panels_per_chapter": 40,
            "target_sequences_per_chapter": 8,
            "target_total_panels": 320,
            "narrative_phases_required_per_chapter": 6,
        },
        "anti_duplication_contract": {
            "default_house_route": "R6_SEMANTIC_BACKBONE_WITH_SEQUENCE_LEVEL_DENSITY_CADENCE",
            "complete_story_before_alternate_style": True,
            "maximum_default_render_candidates_per_panel": 1,
            "maximum_targeted_repairs_per_failed_panel": 2,
            "maximum_alternate_style_share_after_complete_chapter": 0.10,
            "alternate_route_requires_named_chapter_level_question": True,
            "style_only_change_does_not_count_as_chapter_progress": True,
        },
        "chapter_acceptance_contract": {
            "complete_comic_panel_plan_collection": True,
            "opening_and_closing_state_distinct": True,
            "minimum_material_state_delta_categories": 5,
            "minimum_causal_setpieces": 2,
            "cross_chapter_carry_exact": True,
            "phone_readable_assembly_required": True,
            "lettering_protected_subjects_required": True,
            "human_review_state_required": True,
            "commercial_clearance_separate": True,
            "exact_production_base_separate": True,
        },
        "fictional_adult_cast_additions": {
            "TAMSIN_REEVE": "clearly fictional adult courier-cartographer; practical, non-sexualized field clothing; no real-person reference",
            "HALVOR_KEST": "clearly fictional adult Briar Compact marshal; practical quarry armor; no real-person reference",
        },
        "chapters": CHAPTERS,
        "stretch_outline": STRETCH_CHAPTERS,
        "milestones": [
            {"batch": "B1", "chapters": ["CH06", "CH07"], "purpose": "system reveal and first monster defense"},
            {"batch": "B2", "chapters": ["CH08", "CH09"], "purpose": "journey commitment, earned path ability, and lasting injury"},
            {"batch": "B3", "chapters": ["CH10", "CH11"], "purpose": "faction bargain, gear advancement, siege, and formal classes"},
            {"batch": "B4", "chapters": ["CH12", "CH13"], "purpose": "betrayal, relationship rupture, climax, and co-keeper transformation"},
        ],
        "authority_boundary": {
            "story_authoring_only": True,
            "render_prompts_created": 0,
            "provider_calls": 0,
            "uploads": 0,
            "generated_candidates": 0,
            "accepted_candidates": 0,
            "commercial_decisions": 0,
            "exact_base_decisions": 0,
        },
    }


def markdown(data: dict[str, Any]) -> str:
    lines = [
        "# North Garden CH06–CH13 progression plan r1",
        "",
        "This is a breadth-first provisional canon-development plan. It creates story direction, not render, upload, acceptance, rights, or exact-production-base authority.",
        "",
        "## Outcome",
        "",
        data["arc_outcome"],
        "",
        "Eight chapters × 40 target panels = **320 new chronological panels**. The default is one production candidate per panel; repeated style arms do not count as chapter progress.",
        "",
        "## Chapter spine",
        "",
        "| Chapter | Title | Primary change | Closing hook |",
        "| --- | --- | --- | --- |",
    ]
    for chapter in data["chapters"]:
        delta = next(iter(chapter["state_delta"].values()))
        lines.append(f"| {chapter['chapter_id']} | {chapter['title']} | {delta} | {chapter['closing_hook']} |")
    lines.extend(
        [
            "",
            "## Progression shape",
            "",
            "- **CH06–CH07:** the farmhouse answers, the Garden Ledger appears, and the first Mireback forces practical monster combat.",
            "- **CH08–CH09:** the pair leave home, upgrade clothing into work-derived armor, spare a marked creature, enter a drowned node, and carry forward Soren's injury plus Sigrid's earned Wayfinder path.",
            "- **CH10–CH11:** Brackenwake introduces faction politics, owned weapons, stronger armor, collective defense, formal classes, and a shared party bond.",
            "- **CH12–CH13:** concealment breaks the partnership, irreversible garment/tool changes expose the cost, and the North Garden climax transforms them into consenting co-keepers rather than feeding one person to the system.",
            "",
            "## Production rule",
            "",
            "Finish the chronological ComicPanelPlan chapter and its phone assembly before any alternate style arm. A variant is allowed only for a named chapter-scale question and may cover at most 10% of a completed chapter. Failed panels receive at most two targeted repairs; passing panels are not rerolled.",
            "",
            "## Identity and progression",
            "",
            "- Soren retains light-brown/dark-blond swept-back hair and the pale oatmeal coat, which visibly evolves through tears, quilting, removable protection, and eventual sacrifice/repair.",
            "- Sigrid retains dark tied-back hair and the plaid wrap, which becomes a secured weather cape and later functional route flags without losing its recognizable pattern.",
            "- Armor remains practical and work-derived. Weapons have causal functions: Soren's Warden's Reach supports leverage and anchoring; Sigrid's compact bow and seax support path control and utility.",
            "- The Garden Ledger appears briefly on physical surfaces and rewards stewardship, repair, navigation, protection, and declared cooperation.",
            "",
            "## Stretch direction",
            "",
        ]
    )
    for chapter in data["stretch_outline"]:
        lines.append(f"- **{chapter['chapter_id']} — {chapter['title']}:** {chapter['purpose']}")
    lines.extend(
        [
            "",
            "## Next bounded milestone",
            "",
            "Compile CH06 and CH07 as complete 40-panel ComicPanelPlan collections with closed continuity edges, explicit lettering-safe regions, eight sequences each, promotion decisions, and zero render prompts until semantic validation passes.",
            "",
            f"Machine-readable arc: `{JSON_OUTPUT.relative_to(ROOT).as_posix()}`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    data = document()
    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    MARKDOWN_OUTPUT.write_text(markdown(data), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "chapters": len(data["chapters"]),
                "target_panels": data["production_target"]["target_total_panels"],
                "json_sha256": sha256(JSON_OUTPUT),
                "markdown_sha256": sha256(MARKDOWN_OUTPUT),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
