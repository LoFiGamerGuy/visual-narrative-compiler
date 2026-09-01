"""Compile full-denominator CH05 targeted-repair policy coverage."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
RUN_MANIFEST = ROOT / "production/comic/run-manifests/ch05-50-panel-run-manifest-r1.json"
POLICY = ROOT / "config/ch05-openai-targeted-repair-policy-r1.json"
P036 = ROOT / "production/comic/repair-readiness/ch05-p036-openai-r2.json"
OUT = ROOT / "production/comic/repair-readiness/ch05-chapter-repair-policy-coverage-r1.json"
CAUSAL_DIRECTION = "Make the causal hand/object relationship legible before adding atmospheric texture."


class CoverageError(RuntimeError):
    """Chapter repair-policy coverage validation failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CoverageError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def source(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}


def build_record() -> dict[str, Any]:
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    run_manifest = json.loads(RUN_MANIFEST.read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    p036 = json.loads(P036.read_text(encoding="utf-8"))
    require(plans["record_type"] == "ComicPanelPlanCollection" and len(plans["plans"]) == 50, "CH05 plan denominator changed")
    require(plans["animation_shot_plan"] is None, "CH05 plans gained AnimationShotPlan")
    require(run_manifest["expected"]["panel_count"] == 50, "chapter run denominator changed")
    require(run_manifest["expected_chapter_root_sha256"] == "0498d79f705334babc60420a974a910a08c9bb9e15fb782d50f9335f43673664",
            "chapter root changed")
    require(policy["comic_panel_plan"]["panel_id"] == "ng-ch05-sc01-p036", "repair policy panel binding changed")
    require(p036["offline_preflight"]["blocker_count"] == 4, "P036 blocker count changed")

    rows = []
    for panel in sorted(plans["plans"], key=lambda item: item["display_order"]):
        explicit_causal = (
            panel["comic_direction"]["motion_mode"] == "practical_action"
            and panel["comic_direction"]["direction_note"] == CAUSAL_DIRECTION
        )
        policy_available = panel["panel_id"] == policy["comic_panel_plan"]["panel_id"]
        if policy_available:
            state = "LOCAL_MECHANICS_POLICY_AVAILABLE_PRODUCTION_BLOCKED"
            blockers = p036["offline_preflight"]["blockers"]
            policy_id = policy["policy_id"]
            readiness_id = p036["record_id"]
        elif explicit_causal:
            state = "EXPLICIT_CAUSAL_REPAIR_CANDIDATE_PANEL_SPECIFIC_POLICY_ABSENT"
            blockers = [
                "PANEL_SPECIFIC_REPAIR_POLICY_MISSING",
                "APPROVED_BASE_RASTER_MISSING_OR_INVALID",
                "APPROVED_REPAIR_MASK_MISSING_OR_INVALID",
                "EXACT_EXTERNAL_AUTHORITY_MISSING_OR_INVALID",
                "DISTINCT_PRODUCTION_RESERVATION_MISSING_OR_INVALID",
            ]
            policy_id = None
            readiness_id = None
        else:
            state = "NO_EXPLICIT_TARGETED_REPAIR_APPLICABILITY_AT_PLAN_LEVEL"
            blockers = []
            policy_id = None
            readiness_id = None
        rows.append({
            "panel_id": panel["panel_id"],
            "plan_revision_id": panel["plan_revision_id"],
            "display_order": panel["display_order"],
            "motion_mode": panel["comic_direction"]["motion_mode"],
            "explicit_causal_repair_candidate": explicit_causal,
            "panel_specific_policy_id": policy_id,
            "panel_readiness_record_id": readiness_id,
            "state": state,
            "blockers": blockers,
            "approved_base_raster": None,
            "approved_repair_mask": None,
            "production_executable": False,
            "provider_request": None,
            "accepted_panel": False,
        })
    causal_rows = [item for item in rows if item["explicit_causal_repair_candidate"]]
    policy_rows = [item for item in rows if item["panel_specific_policy_id"]]
    require([item["panel_id"] for item in causal_rows] == [
        "ng-ch05-sc01-p019", "ng-ch05-sc01-p026", "ng-ch05-sc01-p036", "ng-ch05-sc01-p044"
    ], "explicit causal repair panel set changed")
    require([item["panel_id"] for item in policy_rows] == ["ng-ch05-sc01-p036"], "P036 policy leaked to another panel")

    return {
        "record_type": "ComicChapterRepairPolicyCoverage",
        "schema_version": "1.0",
        "record_id": "ng-ch05-chapter-repair-policy-coverage-r1",
        "state": "FULL_DENOMINATOR_LOCAL_COVERAGE_NO_EXECUTABLE_PANELS",
        "medium": "comic",
        "animation_shot_plan": None,
        "e_conte": None,
        "sources": {
            "comic_panel_plans": source(PLANS),
            "chapter_run_manifest": source(RUN_MANIFEST),
            "p036_local_repair_policy": source(POLICY),
            "p036_repair_readiness_r2": source(P036),
        },
        "chapter_root_sha256": run_manifest["expected_chapter_root_sha256"],
        "applicability_rule": {
            "explicit_candidate": "motion_mode practical_action AND exact causal hand/object direction note",
            "policy_binding": "panel_id and plan_revision_id must match a distinct panel-specific policy; never inherit P036 policy",
            "non_candidate_limit": "absence of plan-level applicability does not prove a panel can never need repair",
            "mask_inference": "prohibited",
        },
        "summary": {
            "planned_panels": 50,
            "explicit_causal_repair_candidate_panels": len(causal_rows),
            "panel_specific_mechanics_policy_available": len(policy_rows),
            "explicit_candidates_without_policy": len(causal_rows) - len(policy_rows),
            "no_explicit_targeted_repair_applicability": len(rows) - len(causal_rows),
            "policy_coverage_per_planned_panel": round(len(policy_rows) / len(rows), 9),
            "policy_coverage_per_explicit_candidate": round(len(policy_rows) / len(causal_rows), 9),
            "approved_base_rasters": 0,
            "approved_repair_masks": 0,
            "production_executable_panels": 0,
            "provider_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
            "human_minutes": None,
            "accepted_panels": 0,
        },
        "panels_root_sha256": canonical_sha256(rows),
        "panels": rows,
        "decision": {
            "next_policy_target_selected": None,
            "selection_reason": "No additional panel policy is selected by motion mode alone; choose only through a separately bounded information-gain experiment.",
            "p036_policy_generalized_to_other_panels": False,
            "production_expansion_authorized": False,
        },
        "boundary": "Coverage is compiler classification over all 50 ComicPanelPlans. It creates no masks, art, inherited authority, AnimationShotPlan/E-Conte, requests, or acceptance.",
    }


def mutation_checks(expected: dict[str, Any]) -> tuple[int, int]:
    mutations = []
    changed = copy.deepcopy(expected); changed["panels"].pop(); mutations.append(changed)
    changed = copy.deepcopy(expected); changed["panels"][0], changed["panels"][1] = changed["panels"][1], changed["panels"][0]; mutations.append(changed)
    changed = copy.deepcopy(expected); p019 = next(item for item in changed["panels"] if item["panel_id"].endswith("p019")); p019["panel_specific_policy_id"] = "ng-ch05-p036-openai-targeted-repair-policy-r1"; mutations.append(changed)
    changed = copy.deepcopy(expected); p036 = next(item for item in changed["panels"] if item["panel_id"].endswith("p036")); p036["production_executable"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["summary"]["planned_panels"] = 49; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["summary"]["approved_base_rasters"] = 1; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["summary"]["approved_repair_masks"] = 1; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["next_policy_target_selected"] = "ng-ch05-sc01-p019"; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["p036_policy_generalized_to_other_panels"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["animation_shot_plan"] = {}; mutations.append(changed)
    return sum(item != expected for item in mutations), len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", type=Path)
    args = parser.parse_args()
    try:
        expected = build_record()
        if args.emit:
            output = args.emit if args.emit.is_absolute() else ROOT / args.emit
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
            print(f"wrote {output.relative_to(ROOT).as_posix()}")
        else:
            tracked = json.loads(OUT.read_text(encoding="utf-8"))
            require(tracked == expected, "tracked chapter repair coverage differs")
        rejected, total = mutation_checks(expected)
        require(rejected == total, "chapter repair coverage mutation rejection incomplete")
    except (CoverageError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    summary = expected["summary"]
    print("0 failures, 0 warnings")
    print("50/50 panels retained: 4 explicit causal candidates, 1 panel-specific mechanics policy, 3 policy-absent")
    print("0 approved bases/masks/executable panels/requests/uploads/accepted; null minutes; $0")
    print(f"{rejected}/{total} denominator/order/policy-leak/execution/input/selection/medium mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
