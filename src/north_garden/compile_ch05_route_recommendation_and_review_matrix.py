"""Compile measured CH05 pipeline recommendation, style r10, and owner decision matrix."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STYLE_R9 = ROOT / "production/comic/style-direction/ch05-mill-signal-r9.json"
CONTINUITY = ROOT / "production/comic/review/ch05-continuity-style-density-review-r1.json"
REPAIR = ROOT / "production/comic/review/ch05-failure-class-repair-matrix-r1.json"
SCALE = ROOT / "production/comic/layout/ch05-panel-scale-cadence-policy-r1.json"
RENDERRECORDS = ROOT / "production/comic/run-manifests/ch05-built-in-renderrecord-index-r1.json"
CONTRACT = ROOT / "production/comic/review/ch05-owner-decision-contract-r1.json"
LINKS = ROOT / "production/comic/review/ch05-review-artifact-link-manifest-r1.json"
ROUTE = ROOT / "production/comic/recommendations/ch05-pipeline-route-recommendation-r1.json"
MATRIX = ROOT / "production/comic/review/ch05-route-review-decision-matrix-r1.json"
STYLE_R10 = ROOT / "production/comic/style-direction/ch05-mill-signal-r10.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-route-recommendation-and-review-matrix-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def write(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    continuity = json.loads(CONTINUITY.read_text(encoding="utf-8"))
    repair = json.loads(REPAIR.read_text(encoding="utf-8"))
    scale = json.loads(SCALE.read_text(encoding="utf-8"))
    renderrecords = json.loads(RENDERRECORDS.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    links = json.loads(LINKS.read_text(encoding="utf-8"))
    source_bindings = [binding(path) for path in (STYLE_R9, CONTINUITY, REPAIR, SCALE, RENDERRECORDS, CONTRACT, LINKS)]
    style_results = continuity["style_engineering_results_all_26"]
    route = {
        "record_type": "ComicProductionPipelineRouteRecommendation",
        "schema_version": "1.0",
        "record_id": "ng-ch05-pipeline-route-recommendation-r1",
        "state": "MEASURED_ENGINEERING_RECOMMENDATION_OWNER_DECISIONS_PENDING",
        "medium": "comic",
        "comic_panel_plan_revision_created": False,
        "animation_shot_plan": None,
        "e_conte": None,
        "recommended_route": "role-aware premium cel-painted character/emotion/action anchors with mature clear-line causal staging, genuinely simplified inserts, and measured per-panel density",
        "not_based_on": "visual appeal alone",
        "measured_basis": {
            "candidate_count": 29,
            "ch05_candidate_count": 26,
            "selected_sequence_count": 14,
            "comic_panel_plan_count": 50,
            "observed_generation_seconds": renderrecords["summary"]["total_elapsed_seconds"],
            "reference_uses": renderrecords["summary"]["input_reference_uses"],
            "style_results": style_results,
            "manual_selected_hair_wardrobe_pass": "14/14",
            "manual_all_candidate_hair_wardrobe_pass": "26/26",
            "manual_role_order_pass": "25/26",
            "targeted_repairs": {"links": 6, "target_fixed": 5, "all_dimension_pass": 4},
            "highest_selected_edge_occupancy": {"candidate_id": "c005", "value": 0.308471},
            "largest_selected_adjacent_appearance_jump": {"from": "c014", "to": "c015", "distance": 5.6517},
            "lettering": {"minimum_phone_type_px": 13, "tested_in_art_two_line_width_px": 1200, "outside_art_phone_type_px": 13.975, "outside_art_scroll_height_addition_percent": 3.295},
        },
        "role_allocation": [
            {"priority": 1, "mechanism": "cel_painted", "roles": ["character emotion", "deduction", "sensory reaction", "selected wide hero action"], "evidence": "5/6 exact all-dimension passes; h001 closes wide-action coverage; strongest observed role continuity with one retained causal failure."},
            {"priority": 2, "mechanism": "clear_line_watercolor", "roles": ["causal action", "trail movement", "object interaction", "transition", "composition repair"], "evidence": "5/8 exact all-dimension passes plus two warnings; successful literal safe-zone and single-plank corrections; more task coverage than other arms."},
            {"priority": 3, "mechanism": "clean_graphic", "roles": ["selected wide blocking", "reveal", "text-only composition control"], "evidence": "3/6 exact all-dimension passes; useful staging controls but three failures prevent uniform adoption."},
            {"priority": 4, "mechanism": "limited_ink_flat", "roles": ["silent object insert", "quiet sensory punctuation only after exact density check"], "evidence": "4/6 exact all-dimension passes, but c014 edge occupancy 0.275889 proves the label does not guarantee lower density."},
        ],
        "cadence_contract": {
            "wide_directional_anchor_px": [1040, 1200],
            "wide_environmental_motion_px": [880, 1120],
            "dual_causal_px": [700, 1040],
            "medium_character_clue_px": [720, 960],
            "small_object_insert_px": [520, 720],
            "small_sensory_insert_px": [560, 760],
            "principle": "Alternate large action/reveal anchors with medium character logic and silent small inserts; do not impose one ratio or finish.",
        },
        "continuity_mechanism": {
            "minimum": "three authorized fictional-adult reference roles plus per-plan adult/hair/wardrobe/cast assertions, P036 composition-only guard, and full-panel manual atlas review",
            "known_limit": "The built-in product exposes no seed/model/endpoint/request/usage/cost metadata, and image statistics do not verify identity.",
        },
        "lettering_route": {
            "in_art": "Use protected low-detail fields; tested two-line phone copy needs 1200px in the measured cases.",
            "outside_art": "Use the light band only for caption/deduction semantics after ComicPanelPlan revision.",
            "action_and_inserts": "Keep causal action and small inserts silent when text would displace hands, faces, or story objects.",
            "transparent_overlap": "88% is the next measured backing arm, never permission to overlap a face, person, important hand, silhouette, or causal object.",
        },
        "next_high_information_experiment": repair["next_experiment"],
        "source_bindings": source_bindings,
        "owner_acceptance": False,
        "commercial_clearance": False,
        "exact_production_base_selected": False,
    }
    decisions = [
        ("route_role_aware_hybrid", "ROUTE", "Confirm the role-aware cel/clear-line/simplified-insert route versus requesting one uniform finish.", "CONFIRM_ROLE_AWARE_ROUTE", "Unlocks prompt compilation only after candidate and reference choices are separately resolved."),
        ("c005_transition_density", "DENSITY", "Keep c005's foliage density or request one exact density reduction.", "REQUEST_EXACT_DENSITY_REDUCTION", "Targets only c005; no broad transition reroll."),
        ("c014_action_punctuation", "DENSITY", "Treat c014→c015's 5.6517 appearance jump as intentional action punctuation or unify its finish.", "KEEP_AS_ACTION_PUNCTUATION", "Determines whether c014 remains in cadence or receives one finish-density repair."),
        ("lettering_semantics", "LETTERING", "Choose attributed speech, outside-art caption/direct text, or silence for currently copy-unbound beats.", "KEEP_ACTION_AND_INSERT_BEATS_SILENT", "Any caption/speech change requires exact ComicPanelPlan semantics before layout."),
        ("lettering_visual_arm", "LETTERING", "Choose 88% in-art backing, light outside-art band, or another targeted comparison.", "USE_ROLE_DEPENDENT_88_OR_LIGHT_BAND", "Does not permit content overlap; final copy/font/tails/localization remain separate."),
        ("p010_p013_finish_rhythm", "NEXT_EXPERIMENT", "Use the preflight's role-aware four-beat finish or one shared finish.", "USE_ROLE_AWARE_FOUR_BEAT_FINISH", "Controls only the next zero-prompt contract revision."),
        ("p010_p013_copy", "NEXT_EXPERIMENT", "Keep P010–P013 silent or bind plan-level caption semantics.", "KEEP_SILENT_FOR_CAUSAL_TEST", "Separates continuity/causality evidence from unvalidated copy."),
        ("strongest_candidate_shortlist", "CANDIDATES", "Review the 14-candidate engineering shortlist for further production evaluation.", "REVIEW_INDIVIDUALLY", "No group decision can create exact-base or commercial acceptance."),
        ("noncanon_litrpg_direction", "NONCANON", "Identify which practical armor, weapon, and Mireback motifs merit a future canon proposal.", "KEEP_ALL_NONCANON_PENDING_TASTE_REVIEW", "No CH05 wardrobe, equipment, monster, or class state changes."),
        ("commercial_and_exact_base", "AUTHORITY", "Separately decide commercial clearance and whether any candidate is eligible as an exact production base.", "REMAIN_OPEN", "Engineering pass and owner taste approval do not establish provider rights, reproducibility, or exact-base suitability."),
    ]
    matrix = {
        "record_type": "ComicRouteReviewDecisionMatrix",
        "schema_version": "1.0",
        "record_id": "ng-ch05-route-review-decision-matrix-r1",
        "state": "OWNER_DECISIONS_PENDING",
        "source_contract": binding(CONTRACT),
        "source_contract_state": {"subjects": contract["summary"]["subject_count"], "completed_decisions": contract["summary"]["completed_decisions"], "events": contract["summary"]["events"], "human_review_minutes": contract["summary"]["human_review_minutes"]},
        "decision_count": len(decisions),
        "decisions": [
            {"decision_id": decision_id, "class": decision_class, "question": question, "engineering_default": default, "consequence": consequence, "owner_decision": None, "reviewer": None, "human_review_minutes": None}
            for decision_id, decision_class, question, default, consequence in decisions
        ],
        "prompt_count": 0,
        "executable_rows": 0,
        "comic_panel_plan_revision_created": False,
        "animation_shot_plan": None,
        "e_conte": None,
        "boundary": "Decision aid only; does not ingest conversation approval or change the empty append-only owner contract.",
    }
    style_r10 = {
        "record_type": "ComicStyleDirection",
        "schema_version": "1.9",
        "record_id": "ng-comic-style-ch05-mill-signal-r10",
        "state": "MEASURED_CHAPTER_PIPELINE_RECOMMENDATION_OWNER_REVIEW_PENDING",
        "medium": "comic",
        "animation_shot_plan": None,
        "e_conte": None,
        "supersedes": {"record_id": "ng-comic-style-ch05-mill-signal-r9", **binding(STYLE_R9)},
        "selected_engineering_route": route["recommended_route"],
        "role_allocation": route["role_allocation"],
        "cadence_contract": route["cadence_contract"],
        "continuity_mechanism": route["continuity_mechanism"],
        "lettering_route": route["lettering_route"],
        "next_experiment": "Resolve the ten decision-matrix rows, then compile only the P010–P013 four-candidate/two-repair-slot microsequence if its gates pass.",
        "limitations": ["Style-task samples are unbalanced.", "No candidate or lettering treatment is accepted or commercially cleared.", "Provider-side reproducibility metadata is unavailable.", "Non-canon armor, weapon, and monster concepts do not revise CH05."],
    }
    write(ROUTE, route)
    write(MATRIX, matrix)
    write(STYLE_R10, style_r10)
    evidence = {
        "record_type": "CH05RouteRecommendationAndReviewMatrixEvidence",
        "schema_version": "1.0",
        "record_id": "ng-ch05-route-recommendation-and-review-matrix-evidence-r1",
        "state": "PASS_OWNER_REVIEW_PENDING",
        "outputs": [binding(path) for path in (ROUTE, MATRIX, STYLE_R10)],
        "summary": {"styles": 4, "role_allocations": 4, "decisions": 10, "candidate_count": 29, "ch05_candidate_count": 26, "selected": 14, "plans": 50, "owner_decisions": 0, "accepted_candidates": 0, "prompts": 0, "executable_rows": 0, "provider_calls": 0, "uploads": 0, "cost_usd": 0, "human_review_minutes": None},
        "review_links": {"unique_artifacts": links["unique_artifact_count"], "strongest_candidates": links["category_counts"]["strongest_candidates"]},
        "source_bindings": source_bindings,
        "limitations": route["continuity_mechanism"]["known_limit"],
    }
    write(EVIDENCE, evidence)
    print("CH05 route recommendation: 4 role allocations / 10 owner decisions / 29 candidates / 50 plans")
    print("owner decisions/accepted/prompts/executable/calls/uploads/cost 0/0/0/0/0/0/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
