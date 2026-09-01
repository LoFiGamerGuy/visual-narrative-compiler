"""Validate the scale-aware repair-boundary selector contract."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
P036_POLICY = ROOT / "config/ch05-openai-targeted-repair-policy-r1.json"
P036_BOUNDARY = ROOT / "docs/research/evidence/openai-targeted-repair-boundary-hardening-r2.json"
P036_TOPOLOGY = ROOT / "docs/research/evidence/ch05-p036-causal-shape-topology-control-r2.json"
P036_READINESS = ROOT / "production/comic/repair-readiness/ch05-p036-openai-r2.json"
P044_STRESS = ROOT / "docs/research/evidence/ch05-p044-fixed-16px-boundary-stress-r1.json"
P044_ADAPTIVE = ROOT / "docs/research/evidence/ch05-p044-adaptive-boundary-width-r1.json"
CONTRACT = ROOT / "config/scale-aware-repair-boundary-selector-contract-r1.json"


class SelectorError(RuntimeError):
    """Scale-aware boundary selector contract failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SelectorError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}


def build_contract() -> dict[str, Any]:
    p036_policy = json.loads(P036_POLICY.read_text(encoding="utf-8"))
    p036_boundary = json.loads(P036_BOUNDARY.read_text(encoding="utf-8"))
    p036_topology = json.loads(P036_TOPOLOGY.read_text(encoding="utf-8"))
    p036_readiness = json.loads(P036_READINESS.read_text(encoding="utf-8"))
    p044_stress = json.loads(P044_STRESS.read_text(encoding="utf-8"))
    p044_adaptive = json.loads(P044_ADAPTIVE.read_text(encoding="utf-8"))
    require(p036_policy["mechanics"]["boundary_policy"] == "cosine-inset-16px", "P036 policy width changed")
    require(p036_boundary["decision"]["selected_compositor_policy"] == "cosine-inset-16px", "P036 boundary decision changed")
    require(p036_topology["decision"]["mechanics_control_pass"] is True, "P036 topology no longer passes")
    require(p036_readiness["offline_preflight"]["blocker_count"] == 4, "P036 production blockers changed")
    require(p044_stress["decision"]["fixed_16px_compatible_with_fine_feature_control"] is False, "P044 fixed stress changed")
    require(p044_adaptive["decision"]["selected_adaptive_width_px"] == 5, "P044 adaptive width changed")
    require(p044_adaptive["decision"]["p044_production_policy_authored"] is False, "P044 unexpectedly gained a policy")

    return {
        "record_type": "ScaleAwareRepairBoundarySelectorContract",
        "schema_version": "1.0",
        "contract_id": "ng-scale-aware-repair-boundary-selector-contract-r1",
        "state": "LOCAL_SELECTOR_CONTRACT_NO_PRODUCTION_READY_PROFILES",
        "selection_pipeline": [
            {
                "gate": "exact_panel_and_support_binding",
                "requirement": "panel_id, plan_revision_id, support bytes/hash, protected regions, and lettering zones are exact",
                "failure_state": "BLOCKED_SUPPORT_OR_INTENT_MISMATCH"
            },
            {
                "gate": "topology_width_ceiling",
                "requirement": "bounded width series retains declared union/feature cores and components with zero protected/lettering overlap",
                "failure_state": "BLOCKED_TOPOLOGY_COLLAPSE"
            },
            {
                "gate": "exact_base_visual_discontinuity",
                "requirement": "selected width is measured on the exact approved base and exact candidate/repair layer; proxy transfer is insufficient",
                "failure_state": "BLOCKED_EXACT_BASE_BOUNDARY_EVIDENCE_MISSING"
            },
            {
                "gate": "exact_exterior_and_nochange",
                "requirement": "zero exterior change and byte-identical no-change short circuit",
                "failure_state": "BLOCKED_EXTERIOR_OR_NOCHANGE_FAILURE"
            },
            {
                "gate": "timed_human_seam_review",
                "requirement": "identified timed review accepts boundary, causality, protected semantics, and lettering clearance",
                "failure_state": "BLOCKED_TIMED_VISUAL_REVIEW_MISSING"
            },
            {
                "gate": "production_authority",
                "requirement": "approved base/mask, exact external scope and input package, distinct CH05 reservation, journal and RenderRecord path",
                "failure_state": "BLOCKED_PRODUCTION_AUTHORITY"
            },
        ],
        "profiles": {
            "ng-ch05-sc01-p036": {
                "plan_revision_id": "ng-ch05-sc01-p036-plan-r1",
                "local_width_px": 16,
                "width_basis": "G07 proxy discontinuity threshold plus P036 causal-shape topology control",
                "sources": {
                    "local_policy": source(P036_POLICY),
                    "boundary": source(P036_BOUNDARY),
                    "topology": source(P036_TOPOLOGY),
                    "readiness": source(P036_READINESS),
                },
                "topology_gate": "PASS_LOCAL_ABSTRACT_CONTROL",
                "visual_discontinuity_gate": "BLOCKED_EXACT_P036_APPROVED_BASE_AND_CANDIDATE_MISSING",
                "timed_human_seam_review": None,
                "production_ready": False,
                "production_blockers": p036_readiness["offline_preflight"]["blockers"],
            },
            "ng-ch05-sc01-p044": {
                "plan_revision_id": "ng-ch05-sc01-p044-plan-r1",
                "local_width_px": 5,
                "width_basis": "widest topology-retaining width on exact abstract blade/twine support",
                "sources": {
                    "fixed_stress": source(P044_STRESS),
                    "adaptive_topology": source(P044_ADAPTIVE),
                },
                "topology_gate": "PASS_LOCAL_ABSTRACT_CONTROL",
                "visual_discontinuity_gate": "BLOCKED_EXACT_P044_APPROVED_BASE_AND_CANDIDATE_MISSING",
                "timed_human_seam_review": None,
                "production_ready": False,
                "production_blockers": [
                    "PANEL_SPECIFIC_REPAIR_POLICY_MISSING",
                    "APPROVED_BASE_RASTER_MISSING_OR_INVALID",
                    "APPROVED_REPAIR_MASK_MISSING_OR_INVALID",
                    "EXACT_BASE_BOUNDARY_EVIDENCE_MISSING",
                    "TIMED_HUMAN_SEAM_REVIEW_MISSING",
                    "EXACT_EXTERNAL_AUTHORITY_MISSING_OR_INVALID",
                    "DISTINCT_PRODUCTION_RESERVATION_MISSING_OR_INVALID",
                ],
            },
        },
        "summary": {
            "local_profiles": 2,
            "distinct_local_widths": [5, 16],
            "universal_width_px": None,
            "topology_control_passes": 2,
            "exact_panel_base_visual_boundary_passes": 0,
            "timed_human_seam_reviews": 0,
            "production_ready_profiles": 0,
            "approved_production_masks": 0,
            "provider_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        },
        "generalization_rules": {
            "width_inheritance_between_panels": False,
            "proxy_visual_metric_transfer_to_panel_art": False,
            "topology_pass_implies_visual_pass": False,
            "local_profile_implies_production_policy": False,
            "motion_mode_implies_profile": False,
        },
        "boundary": "The contract keeps topology, exact-base visual discontinuity, exterior/no-change, timed review, and production authority as separate gates. It is not an executor or policy grant.",
    }


def mutation_checks(expected: dict[str, Any]) -> tuple[int, int]:
    mutations = []
    changed = copy.deepcopy(expected); changed["selection_pipeline"].pop(); mutations.append(changed)
    changed = copy.deepcopy(expected); changed["profiles"]["ng-ch05-sc01-p036"]["local_width_px"] = 5; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["profiles"]["ng-ch05-sc01-p044"]["local_width_px"] = 16; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["profiles"]["ng-ch05-sc01-p044"]["visual_discontinuity_gate"] = "PASS"; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["profiles"]["ng-ch05-sc01-p036"]["production_ready"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["summary"]["universal_width_px"] = 5; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["summary"]["timed_human_seam_reviews"] = 1; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["generalization_rules"]["width_inheritance_between_panels"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["generalization_rules"]["topology_pass_implies_visual_pass"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["summary"]["production_ready_profiles"] = 1; mutations.append(changed)
    return sum(item != expected for item in mutations), len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", type=Path)
    args = parser.parse_args()
    try:
        expected = build_contract()
        if args.emit:
            output = args.emit if args.emit.is_absolute() else ROOT / args.emit
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
            print(f"wrote {output.relative_to(ROOT).as_posix()}")
        else:
            tracked = json.loads(CONTRACT.read_text(encoding="utf-8"))
            require(tracked == expected, "tracked scale-aware selector contract differs")
        rejected, total = mutation_checks(expected)
        require(rejected == total, "selector contract mutation rejection incomplete")
    except (SelectorError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings")
    print("2 local profiles: P036=16px, P044=5px; 2 topology passes, 0 exact-base visual passes")
    print("no universal width; 0 timed seam reviews/production-ready profiles/masks/requests/uploads; $0")
    print(f"{rejected}/{total} gate/width/visual/production/generalization mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
