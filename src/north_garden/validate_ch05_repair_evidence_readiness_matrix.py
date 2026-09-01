"""Compile the full CH05 repair-evidence gate matrix without inferring artifacts."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
COVERAGE = ROOT / "production/comic/repair-readiness/ch05-chapter-repair-policy-coverage-r1.json"
SELECTOR = ROOT / "config/scale-aware-repair-boundary-selector-contract-r1.json"
RECORD_TEMPLATE = ROOT / "config/record-templates/comic-repair-render-record-v2.json"
BUDGET_POLICY = ROOT / "config/ch05-production-budget-policy-r1.json"
COST_LEDGER = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r2.json"
OUTPUT = ROOT / "production/comic/repair-readiness/ch05-repair-evidence-readiness-matrix-r1.json"


class MatrixError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MatrixError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def root_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build() -> dict:
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    selector = json.loads(SELECTOR.read_text(encoding="utf-8"))
    budget = json.loads(BUDGET_POLICY.read_text(encoding="utf-8"))
    ledger = json.loads(COST_LEDGER.read_text(encoding="utf-8"))
    require(len(plans["plans"]) == len(coverage["panels"]) == 50, "full denominator missing")
    require(budget["execution_enabled"] is False and ledger["entries"] == [], "production budget unexpectedly enabled")
    coverage_by_id = {item["panel_id"]: item for item in coverage["panels"]}
    rows = []
    for plan in plans["plans"]:
        panel_id = plan["panel_id"]
        prior = coverage_by_id[panel_id]
        profile = selector["profiles"].get(panel_id)
        explicit = prior["explicit_causal_repair_candidate"]
        policy_present = prior["panel_specific_policy_id"] is not None
        topology_present = profile is not None and profile["topology_gate"] == "PASS_LOCAL_ABSTRACT_CONTROL"
        if panel_id == "ng-ch05-sc01-p036": state = "LOCAL_POLICY_AND_TOPOLOGY_ONLY_PRODUCTION_GATES_MISSING"
        elif panel_id == "ng-ch05-sc01-p044": state = "LOCAL_SELECTOR_TOPOLOGY_PRESENT_POLICY_AND_PRODUCTION_GATES_MISSING"
        elif explicit: state = "EXPLICIT_CANDIDATE_SELECTOR_POLICY_AND_PRODUCTION_GATES_MISSING"
        else: state = "NO_EXPLICIT_PLAN_LEVEL_REPAIR_APPLICABILITY_NO_ARTIFACTS_INFERRED"
        gates = {
            "comic_panel_plan_bound": True,
            "explicit_plan_level_repair_candidate": explicit,
            "selector_profile_present": profile is not None,
            "local_topology_evidence_present": topology_present,
            "panel_specific_policy_present": policy_present,
            "approved_base_raster_present": False,
            "approved_repair_mask_present": False,
            "exact_external_authority_present": False,
            "distinct_production_reservation_present": False,
            "exact_base_candidate_visual_boundary_present": False,
            "exact_exterior_result_present": False,
            "no_change_result_present": False,
            "timed_seam_review_present": False,
            "render_record_v2_1_present": False,
        }
        rows.append({
            "panel_id": panel_id, "plan_revision_id": plan["plan_revision_id"], "display_order": plan["display_order"],
            "motion_mode": plan["comic_direction"]["motion_mode"], "state": state,
            "selector_profile": None if profile is None else {"contract_id": selector["contract_id"], "local_width_px": profile["local_width_px"], "topology_gate": profile["topology_gate"], "visual_discontinuity_gate": profile["visual_discontinuity_gate"], "production_ready": profile["production_ready"]},
            "panel_specific_policy_id": prior["panel_specific_policy_id"], "gates": gates,
            "approved_base_raster": None, "approved_repair_mask": None, "external_authority": None,
            "production_reservation": None, "exact_visual_boundary_evidence": None, "timed_seam_review": None,
            "render_record": None, "candidate": None, "human_minutes": None, "accepted": False,
        })
    summary = {
        "planned_panels": 50, "explicit_repair_candidates": sum(row["gates"]["explicit_plan_level_repair_candidate"] for row in rows),
        "selector_profiles": sum(row["gates"]["selector_profile_present"] for row in rows),
        "local_topology_evidence": sum(row["gates"]["local_topology_evidence_present"] for row in rows),
        "panel_specific_policies": sum(row["gates"]["panel_specific_policy_present"] for row in rows),
        "approved_base_rasters": 0, "approved_repair_masks": 0, "external_authorities": 0, "production_reservations": 0,
        "exact_base_visual_boundary_results": 0, "exact_exterior_results": 0, "no_change_results": 0,
        "timed_seam_reviews": 0, "render_records_v2_1": 0, "candidates": 0, "accepted_panels": 0,
        "human_minutes": None, "provider_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000",
    }
    return {
        "record_type": "ComicChapterRepairEvidenceReadinessMatrix", "schema_version": "1.0",
        "record_id": "ng-ch05-repair-evidence-readiness-matrix-r1", "state": "FULL_DENOMINATOR_NO_PRODUCTION_READY_REPAIR_OUTCOMES",
        "medium": "comic", "animation_shot_plan": None, "e_conte": None,
        "sources": {"comic_panel_plans": source(PLANS), "prior_policy_coverage": source(COVERAGE), "boundary_selector": source(SELECTOR), "render_record_v2_template": source(RECORD_TEMPLATE), "production_budget_policy": source(BUDGET_POLICY), "production_cost_ledger": source(COST_LEDGER)},
        "gate_rule": "A gate is present only from an exact panel/revision-bound artifact. Motion, nearby panels, proxy controls, G07 budget, and synthetic fixtures cannot satisfy or infer a gate.",
        "summary": summary, "panels_root_sha256": root_hash(rows), "panels": rows,
        "decision": {"production_ready_panel_selected": None, "next_external_action": None, "profile_or_policy_inferred": False, "mask_inferred": False, "synthetic_fixture_counted_as_real": False},
        "boundary": "Full-denominator compiler evidence only. No art, mask, authority, budget, outcome, review, AnimationShotPlan, or E-Conte record is created.",
    }


def mutation_checks(expected: dict) -> tuple[int, int]:
    values = []
    item = copy.deepcopy(expected); item["panels"].pop(); values.append(item)
    item = copy.deepcopy(expected); item["panels"][0]["display_order"] = 2; values.append(item)
    item = copy.deepcopy(expected); item["panels"][18]["selector_profile"] = expected["panels"][35]["selector_profile"]; values.append(item)
    item = copy.deepcopy(expected); item["panels"][25]["gates"]["panel_specific_policy_present"] = True; values.append(item)
    item = copy.deepcopy(expected); item["panels"][43]["selector_profile"]["local_width_px"] = 16; values.append(item)
    item = copy.deepcopy(expected); item["panels"][35]["approved_base_raster"] = {"sha256": "0" * 64}; values.append(item)
    item = copy.deepcopy(expected); item["panels"][35]["gates"]["exact_base_candidate_visual_boundary_present"] = True; values.append(item)
    item = copy.deepcopy(expected); item["panels"][43]["timed_seam_review"] = {}; values.append(item)
    item = copy.deepcopy(expected); item["panels"][35]["render_record"] = {}; values.append(item)
    item = copy.deepcopy(expected); item["summary"]["render_records_v2_1"] = 1; values.append(item)
    item = copy.deepcopy(expected); item["summary"]["human_minutes"] = 3.0; values.append(item)
    item = copy.deepcopy(expected); item["decision"]["production_ready_panel_selected"] = "ng-ch05-sc01-p036"; values.append(item)
    item = copy.deepcopy(expected); item["animation_shot_plan"] = {}; values.append(item)
    return sum(value != expected for value in values), len(values)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--emit", type=Path); args = parser.parse_args()
    try:
        expected = build()
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else: require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked readiness matrix differs")
        rejected, total = mutation_checks(expected); require(rejected == total, "mutation rejection incomplete")
        require(expected["panels_root_sha256"] == root_hash(expected["panels"]), "panel root mismatch")
    except (MatrixError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr); return 1
    s = expected["summary"]
    print(f"0 failures, 0 warnings (50 panels; {s['explicit_repair_candidates']} explicit, {s['selector_profiles']} profiles, {s['panel_specific_policies']} policy)")
    print("0 approved bases/masks/authorities/reservations/visual results/seam reviews/RenderRecords/candidates/accepted; minutes null; $0")
    print(f"{rejected}/{total} denominator/inference/width/input/result/review/medium mutations rejected")
    return 0


if __name__ == "__main__": raise SystemExit(main())
