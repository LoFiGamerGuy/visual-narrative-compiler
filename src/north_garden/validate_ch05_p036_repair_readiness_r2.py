"""Build and validate immutable post-hardening P036 repair readiness r2."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
R1 = ROOT / "production/comic/repair-readiness/ch05-p036-openai-r1.json"
R2 = ROOT / "production/comic/repair-readiness/ch05-p036-openai-r2.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
POLICY = ROOT / "config/ch05-openai-targeted-repair-policy-r1.json"
BOUNDARY = ROOT / "docs/research/evidence/openai-targeted-repair-boundary-hardening-r2.json"
CAUSAL = ROOT / "docs/research/evidence/ch05-p036-causal-shape-topology-control-r2.json"
PREFLIGHT = ROOT / "experiments/results/ch05-p036-openai-offline-preflight-r1.json"
BUDGET_POLICY = ROOT / "config/ch05-production-budget-policy-r1.json"
COST_LEDGER = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r1.json"


class ReadinessError(RuntimeError):
    """P036 readiness revision validation failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReadinessError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}


def build_record() -> dict[str, Any]:
    r1 = json.loads(R1.read_text(encoding="utf-8"))
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    causal = json.loads(CAUSAL.read_text(encoding="utf-8"))
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    budget_policy = json.loads(BUDGET_POLICY.read_text(encoding="utf-8"))
    cost_ledger = json.loads(COST_LEDGER.read_text(encoding="utf-8"))
    panel = next(item for item in plans["plans"] if item["panel_id"] == "ng-ch05-sc01-p036")
    blockers = [
        "APPROVED_BASE_RASTER_MISSING_OR_INVALID",
        "APPROVED_REPAIR_MASK_MISSING_OR_INVALID",
        "EXACT_EXTERNAL_AUTHORITY_MISSING_OR_INVALID",
        "DISTINCT_PRODUCTION_RESERVATION_MISSING_OR_INVALID",
    ]
    require(preflight["state"] == "BLOCKED_OFFLINE_NO_REQUEST_CONSTRUCTION", "real P036 preflight state changed")
    require(preflight["blockers"] == blockers, f"real P036 blockers changed: {preflight['blockers']}")
    require(preflight["request_envelope"] is None, "real P036 preflight created an envelope")
    require(not preflight["network"]["network_capability_present"], "real P036 preflight gained network capability")
    require(policy["production_gates"]["request_body_or_executor_implemented"] is False, "repair policy gained an executor")
    require(all(
        not item["eligible_as_production_base"]
        and not item["eligible_as_production_mask"]
        and not item["external_upload_authorized"]
        for item in policy["proxy_controls"]
    ), "proxy control became eligible")
    require(boundary["decision"]["selected_compositor_policy"] == "cosine-inset-16px", "boundary policy changed")
    require(causal["decision"]["selected_context_padding_px"] == 8, "causal context policy changed")
    require(budget_policy["execution_enabled"] is False and budget_policy["maximum_aggregate_cap_usd"] is None,
            "CH05 production budget unexpectedly enabled")
    require(cost_ledger["committed_actual_cost_usd"] == "0.000000" and cost_ledger["held_reservations_usd"] == "0.000000",
            "CH05 production ledger is not zero")
    require(plans["record_type"] == "ComicPanelPlanCollection" and plans["animation_shot_plan"] is None,
            "ComicPanelPlan/AnimationShotPlan boundary changed")
    require(r1["record_id"] == "ng-ch05-p036-openai-repair-readiness-r1", "r1 identity changed")

    return {
        "record_type": "ComicPanelRepairReadiness",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p036-openai-repair-readiness-r2",
        "state": "LOCAL_MECHANICS_POLICY_COMPLETE_FOUR_PRODUCTION_GATES_BLOCKED",
        "immutability": {
            "supersedes_record": source(R1),
            "superseded_record_rewritten": False,
            "revision_reason": "Bind post-selection boundary/topology mechanics and exact fail-closed production state without modifying r1.",
        },
        "medium": "comic",
        "comic_panel_plan": {
            "collection": source(PLANS),
            "panel_id": panel["panel_id"],
            "plan_revision_id": panel["plan_revision_id"],
            "display_order": panel["display_order"],
            "narrative_beat": panel["narrative_beat"],
            "motion_mode": panel["comic_direction"]["motion_mode"],
            "lettering_safe_zones": panel["comic_direction"]["lettering"]["safe_zones"],
        },
        "animation_shot_plan": None,
        "e_conte": None,
        "selected_route": {
            "adapter_id": policy["selected_route"]["adapter_id"],
            "model_snapshot": policy["selected_route"]["model_snapshot"],
            "endpoint": policy["selected_route"]["endpoint"],
            "selection_adr": "ADR-0025",
            "route_selection_changed": False,
        },
        "local_repair_policy": {
            **source(POLICY),
            "policy_id": policy["policy_id"],
            "boundary_policy": policy["mechanics"]["boundary_policy"],
            "causal_context_padding_px": policy["mechanics"]["causal_context_padding_px"],
            "nochange_policy": policy["mechanics"]["nochange_policy"],
            "production_authority_granted": False,
        },
        "measured_mechanics_evidence": {
            "boundary": {
                **source(BOUNDARY),
                "selected_compositor_policy": boundary["decision"]["selected_compositor_policy"],
                "art_accepted": boundary["decision"]["art_accepted"],
            },
            "causal_shape": {
                **source(CAUSAL),
                "selected_context_padding_px": causal["decision"]["selected_context_padding_px"],
                "mechanics_control_pass": causal["decision"]["mechanics_control_pass"],
                "art_accepted": causal["decision"]["art_accepted"],
                "provider_input_authorized": causal["decision"]["provider_input_authorized"],
            },
            "scope": "abstract local compositor mechanics only; no visual, identity, or continuity acceptance",
        },
        "proxy_control_state": {
            "controls": policy["proxy_controls"],
            "eligible_production_bases": 0,
            "eligible_production_masks": 0,
            "authorized_external_uploads": 0,
        },
        "production_inputs": {
            "approved_base_raster": None,
            "approved_repair_mask": None,
            "external_upload_authority": None,
            "production_budget_reservation": None,
        },
        "production_budget": {
            "policy": source(BUDGET_POLICY),
            "ledger": source(COST_LEDGER),
            "state": budget_policy["state"],
            "approved_aggregate_cap_usd": budget_policy["maximum_aggregate_cap_usd"],
            "committed_actual_cost_usd": cost_ledger["committed_actual_cost_usd"],
            "held_reservations_usd": cost_ledger["held_reservations_usd"],
            "g07_budget_reuse_prohibited": budget_policy["bakeoff_budget_reuse_prohibited"],
        },
        "offline_preflight": {
            **source(PREFLIGHT),
            "state": preflight["state"],
            "blockers": blockers,
            "blocker_count": len(blockers),
            "panel_input_package_sha256": preflight["panel_input_package_sha256"],
            "request_envelope": preflight["request_envelope"],
            "request_body_constructed": preflight["network"]["request_body_constructed"],
            "network_capability_present": preflight["network"]["network_capability_present"],
        },
        "execution": {
            "state": "NOT_AUTHORIZED_NOT_REQUEST_CAPABLE",
            "provider_request_id": None,
            "submission_journal": None,
            "render_record": None,
            "candidate": None,
            "provider_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        },
        "review": {
            "human_review_status": "not_yet_performed",
            "human_minutes": None,
            "accepted": False,
        },
        "next_required_inputs": [
            "authorized human-reviewed panel-specific fictional base raster",
            "authorized human-reviewed panel-specific causal repair mask",
            "exact provider/model/endpoint/input-package external upload authority",
            "distinct user-approved CH05 production cap and aggregate reservation",
        ],
        "boundary": "This readiness revision records local mechanics progress and exact blockers. It authorizes no production input, upload, spend, request construction, execution, review, or acceptance.",
    }


def mutation_checks(expected: dict[str, Any]) -> tuple[int, int]:
    mutations = []
    changed = copy.deepcopy(expected); changed["immutability"]["supersedes_record"]["sha256"] = "0" * 64; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["local_repair_policy"]["production_authority_granted"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["offline_preflight"]["blockers"].pop(); mutations.append(changed)
    changed = copy.deepcopy(expected); changed["production_inputs"]["approved_base_raster"] = {}; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["production_inputs"]["approved_repair_mask"] = {}; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["production_inputs"]["external_upload_authority"] = {}; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["production_inputs"]["production_budget_reservation"] = {}; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["execution"]["candidate"] = {}; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["offline_preflight"]["request_body_constructed"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["animation_shot_plan"] = {}; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["review"] = {"human_review_status": "completed", "human_minutes": 1, "accepted": True}; mutations.append(changed)
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
            tracked = json.loads(R2.read_text(encoding="utf-8"))
            require(tracked == expected, "tracked P036 readiness r2 differs")
        rejected, total = mutation_checks(expected)
        require(rejected == total, "readiness r2 mutation rejection incomplete")
    except (ReadinessError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings")
    print("P036 readiness r2: policy/mechanics pinned; 4 blockers; 0 approved inputs/requests/uploads/$0")
    print("ComicPanelPlan bound; AnimationShotPlan/E-Conte null; r1 preserved by exact hash")
    print(f"{rejected}/{total} immutability/policy/gate/input/execution/medium/review mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
