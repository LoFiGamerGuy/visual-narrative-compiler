"""Compile measured Tier-A effort scenarios and a fail-closed owner decision intake contract."""
from __future__ import annotations

import hashlib
import json
import math
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
PRIORITY = ROOT / "production/comic/coverage/ch05-remaining-panel-priority-r1.json"
INITIAL = ROOT / "docs/research/evidence/ch05-overnight-production-r1.json"
HARDENING = ROOT / "docs/research/evidence/ch05-cadence-hardening-r1.json"
CONCEPTS = ROOT / "docs/research/evidence/future-litrpg-visual-concepts-r1.json"
HYPOTHESES = ROOT / "production/comic/coverage/ch05-tier-a-production-hypotheses-r1.json"
DECISIONS = ROOT / "production/comic/review/ch05-owner-decision-contract-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-tier-a-effort-scenarios-r1.json"

TIER_A = {
    10: ("cel_painted", "medium_sensory_portrait", 760, "SILENT_OR_FINAL_COPY_PENDING"),
    11: ("clear_line_watercolor", "small_causal_clue", 600, "SILENT_OBJECT_BEAT"),
    12: ("clear_line_watercolor", "small_directional_object_insert", 560, "SILENT_OBJECT_BEAT"),
    13: ("clear_line_watercolor", "medium_directional_transition", 880, "SILENT_MOVEMENT_BEAT"),
    14: ("clean_graphic", "wide_smoke_visibility_transition", 1040, "SILENT_ATMOSPHERIC_BEAT"),
    15: ("cel_painted", "medium_map_continuity", 740, "SILENT_OR_CAPTION_PENDING"),
    17: ("clear_line_watercolor", "wide_mill_reveal", 1040, "SILENT_REVEAL_BEAT"),
    18: ("clean_graphic", "wide_smoke_origin_reveal", 1040, "SILENT_REVEAL_BEAT"),
    20: ("clear_line_watercolor", "wide_creek_crossing_action", 1040, "SILENT_ACTION_BEAT"),
    21: ("clear_line_watercolor", "small_red_cloth_insert", 560, "SILENT_OBJECT_BEAT"),
    22: ("cel_painted", "medium_protected_object_interaction", 780, "SILENT_OR_FINAL_COPY_PENDING"),
    23: ("clear_line_watercolor", "wide_loading_door_approach", 1040, "SILENT_MOVEMENT_BEAT"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def percentile(values: list[float], fraction: float) -> float:
    values = sorted(values); index = (len(values) - 1) * fraction; low, high = math.floor(index), math.ceil(index)
    return values[low] if low == high else values[low] + (values[high] - values[low]) * (index - low)


def main() -> int:
    plans = json.loads(PLANS.read_text(encoding="utf-8")); priority = json.loads(PRIORITY.read_text(encoding="utf-8"))
    initial = json.loads(INITIAL.read_text(encoding="utf-8")); hardening = json.loads(HARDENING.read_text(encoding="utf-8")); concepts = json.loads(CONCEPTS.read_text(encoding="utf-8"))
    plan_by_order = {plan["display_order"]: plan for plan in plans["plans"]}
    tier_a_orders = [order for tier in priority["priority_tiers"] if tier["tier"] == "A" for group in tier["groups"] for order in group["orders"]]
    if set(tier_a_orders) != set(TIER_A): raise SystemExit("Tier A style hypothesis denominator mismatch")
    rows = []
    for order in sorted(tier_a_orders):
        plan = plan_by_order[order]; style, role, width, lettering = TIER_A[order]
        rows.append({
            "order": order, "panel_id": plan["panel_id"], "plan_revision_id": plan["plan_revision_id"], "plan_canonical_sha256": canonical_sha(plan),
            "narrative_beat": plan["narrative_beat"], "motion_mode": plan["comic_direction"]["motion_mode"], "visible_adult_cast": plan["visible_adult_cast"],
            "provisional_style_id": style, "provisional_format_role": role, "provisional_target_width": width,
            "provisional_lettering_mode": lettering, "prompt": None, "final_copy": None,
            "owner_style_approval": False, "owner_generation_authority": False, "production_executable": False
        })
    all_ch05 = initial["candidates"] + hardening["candidates"]
    times = [candidate["execution"]["elapsed_seconds"] for candidate in all_ch05]
    p10, p50, p90 = percentile(times, .10), percentile(times, .50), percentile(times, .90)
    average = sum(times) / len(times)
    nonpass = sum(any(str(value).startswith(("WARN", "FAIL")) for value in candidate["engineering_review"]["results"].values()) for candidate in all_ch05)
    scenarios = []
    for scenario_id, candidate_count, note in [
        ("one_initial_per_plan", 12, "Minimum coverage arm: one candidate for each Tier A plan; no repair capacity."),
        ("one_initial_plus_four_targeted_repairs", 16, "Planning arm: 12 initials plus four repair slots, rounded from 12 × the observed 9/26 non-pass fraction; not a forecast."),
        ("two_arms_per_plan", 24, "Comparison arm: two style/reference conditions per plan; highest evidence but unnecessary before current owner review.")
    ]:
        scenarios.append({
            "scenario_id": scenario_id, "candidate_count": candidate_count, "note": note,
            "observed_time_basis_seconds_per_candidate": {"p10": round(p10, 3), "median": round(p50, 3), "p90": round(p90, 3), "mean": round(average, 3)},
            "derived_generation_seconds": {"p10": round(candidate_count * p10, 3), "median": round(candidate_count * p50, 3), "p90": round(candidate_count * p90, 3), "mean": round(candidate_count * average, 3)},
            "monetary_cost_usd": None, "human_review_minutes": None, "executed": False
        })
    hypotheses = {
        "record_type": "ComicTierAProductionHypotheses", "schema_version": "1.0", "record_id": "ng-ch05-tier-a-production-hypotheses-r1",
        "state": "PROVISIONAL_LOCAL_HYPOTHESES_OWNER_REVIEW_BEFORE_PROMPTS_OR_GENERATION", "medium": "comic",
        "comic_panel_plan_collection": {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha(PLANS)},
        "priority_manifest": {"path": PRIORITY.relative_to(ROOT).as_posix(), "sha256": sha(PRIORITY)},
        "comic_panel_plan_revision_created": False, "animation_shot_plan": None, "e_conte": None,
        "summary": {"tier_a_plans": 12, "provisional_style_assignments": 12, "prompts": 0, "final_copy_bound": 0, "owner_style_approvals": 0,
                    "owner_generation_authorities": 0, "production_executable": 0, "provider_calls": 0, "uploads": 0, "cost_usd": 0},
        "rows": rows, "row_root_sha256": canonical_sha(rows),
        "decision": "Use these role-aware style/size assignments only to focus owner review and future prompt planning. Do not compile prompts or generate Tier A until current candidate/style/cadence decisions are recorded.",
        "boundary": "Hypotheses are not ComicPanelPlan revisions, prompts, execution authority, or production state."
    }
    HYPOTHESES.parent.mkdir(parents=True, exist_ok=True)
    with HYPOTHESES.open("w", encoding="utf-8", newline="\n") as handle: handle.write(json.dumps(hypotheses, indent=2) + "\n")

    candidate_subjects = []
    for candidate in all_ch05:
        candidate_subjects.append({"subject_id": candidate["candidate_id"], "subject_type": "CH05_CANDIDATE", "source_sha256": candidate["output"]["sha256"],
                                   "allowed_decisions": ["ACCEPT_FOR_FURTHER_PRODUCTION_EVALUATION", "REJECT", "REQUEST_SMALLEST_TARGETED_REPAIR"],
                                   "decision": None, "decision_tags": [], "reviewer": None, "human_review_minutes": None, "notes": None})
    for candidate in concepts["candidates"]:
        candidate_subjects.append({"subject_id": candidate["candidate_id"], "subject_type": "NONCANON_CONCEPT", "source_sha256": candidate["output"]["sha256"],
                                   "allowed_decisions": ["KEEP_NONCANON_DIRECTION", "REJECT", "REQUEST_FUTURE_NONCANON_VARIANT"],
                                   "decision": None, "decision_tags": [], "reviewer": None, "human_review_minutes": None, "notes": None})
    higher_subjects = [
        ("sequence_departure_and_clue", "SEQUENCE", ["ACCEPT_RHYTHM", "REVISE_SELECTION", "REJECT_SEQUENCE"]),
        ("sequence_bridge_to_mill", "SEQUENCE", ["ACCEPT_RHYTHM", "REVISE_SELECTION", "REJECT_SEQUENCE"]),
        ("sequence_signal_and_return", "SEQUENCE", ["ACCEPT_RHYTHM", "REVISE_SELECTION", "REJECT_SEQUENCE"]),
        ("variable_panel_cadence", "CADENCE", ["ACCEPT_DIRECTION", "REVISE_WIDTHS_GUTTERS", "REJECT_DIRECTION"]),
        ("role_aware_cel_clear_line_route", "STYLE_ROUTE", ["ACCEPT_DIRECTION", "REVISE_ROLE_ASSIGNMENTS", "REJECT_DIRECTION"]),
        ("c005_dense_transition", "DENSITY", ["KEEP_INTENTIONAL_DENSITY", "REQUEST_TARGETED_DENSITY_REDUCTION"]),
        ("c014_to_c015_action_punctuation", "DENSITY_RHYTHM", ["KEEP_INTENTIONAL_PULSE", "REQUEST_FINISH_UNIFICATION"]),
        ("translucent_88_balloon_arm", "LETTERING", ["KEEP_AS_DEVELOPMENT_ARM", "REJECT_ARM"]),
        ("light_outside_art_caption_band", "LETTERING", ["KEEP_AS_PLAN_REVISION_OPTION", "REJECT_ARM"]),
        ("dark_direct_gutter_text", "LETTERING", ["KEEP_AS_COMPARISON_ARM", "REJECT_ARM"]),
    ]
    for subject_id, subject_type, allowed in higher_subjects:
        candidate_subjects.append({"subject_id": subject_id, "subject_type": subject_type, "source_sha256": None, "allowed_decisions": allowed,
                                   "decision": None, "decision_tags": [], "reviewer": None, "human_review_minutes": None, "notes": None})
    decisions = {
        "record_type": "ComicOwnerDecisionContract", "schema_version": "1.0", "record_id": "ng-ch05-owner-decision-contract-r1",
        "state": "EMPTY_APPEND_ONLY_DECISION_INTAKE", "medium": "comic", "comic_panel_plan_revision_created": False,
        "animation_shot_plan": None, "e_conte": None,
        "summary": {"subject_count": len(candidate_subjects), "ch05_candidate_subjects": 26, "noncanon_concept_subjects": 3, "higher_order_subjects": 10,
                    "completed_decisions": 0, "human_review_minutes": None, "accepted_production_candidates": 0, "events": 0},
        "subjects": candidate_subjects,
        "event_contract": {"required_fields": ["event_id", "subject_id", "decision", "reviewer", "started_at", "ended_at", "active_minutes", "notes", "prior_event_sha256", "event_sha256"],
                           "append_only": True, "events": []},
        "promotion_rule": "A subject summary may change only by deriving the latest valid hash-chained event. Candidate evaluation acceptance is not commercial clearance or exact production-base acceptance.",
        "boundary": "This empty contract records no owner decision, review minute, acceptance, plan revision, or generation authority."
    }
    DECISIONS.parent.mkdir(parents=True, exist_ok=True)
    with DECISIONS.open("w", encoding="utf-8", newline="\n") as handle: handle.write(json.dumps(decisions, indent=2) + "\n")

    evidence = {
        "record_type": "CH05TierAEffortScenarioEvidence", "schema_version": "1.0", "record_id": "ng-ch05-tier-a-effort-scenarios-r1",
        "state": "MEASURED_SCENARIOS_NOT_FORECAST_OR_AUTHORITY", "medium": "comic",
        "hypotheses": {"path": HYPOTHESES.relative_to(ROOT).as_posix(), "sha256": sha(HYPOTHESES)},
        "decision_contract": {"path": DECISIONS.relative_to(ROOT).as_posix(), "sha256": sha(DECISIONS)},
        "observed_basis": {"candidate_count": 26, "generation_seconds": round(sum(times), 3), "p10_seconds": round(p10, 3), "median_seconds": round(p50, 3),
                           "p90_seconds": round(p90, 3), "min_seconds": round(min(times), 3), "max_seconds": round(max(times), 3),
                           "engineering_all_pass": 26 - nonpass, "engineering_warn_or_fail": nonpass},
        "scenarios": scenarios,
        "monetary_cost_boundary": "Built-in product cost/usage remains unavailable; scenario cost is null, never $0 or estimated.",
        "human_time_boundary": "No timed owner review exists; scenario human minutes remain null.",
        "recommendation": "Use the 12-initial-plus-up-to-four-targeted-repairs scenario only after current owner decisions. Repair slots are a bounded planning allowance derived from the observed non-pass fraction, not a predicted requirement.",
        "activity": {"prompts_created": 0, "provider_calls": 0, "uploads": 0, "cost_usd": 0, "owner_decisions_recorded": 0, "human_review_minutes": None},
        "boundary": "No scenario is executed or authorized; no plan, prompt, copy, decision, acceptance, or commercial conclusion is created."
    }
    with EVIDENCE.open("w", encoding="utf-8", newline="\n") as handle: handle.write(json.dumps(evidence, indent=2) + "\n")
    print(f"compiled Tier A hypotheses/effort/decision contract: 12 plans, 26-candidate {sum(times):.3f}s basis, {len(candidate_subjects)} pending decisions")
    print(f"hypotheses {sha(HYPOTHESES)} decisions {sha(DECISIONS)} evidence {sha(EVIDENCE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
