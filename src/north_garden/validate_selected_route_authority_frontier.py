"""Compile the measured local-versus-authority frontier for G07 and CH05."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/research/evidence/selected-route-authority-dependency-frontier-r1.json"
SOURCES = {
    "review_protocol": ROOT / "config/g07-blinded-human-review-protocol-r1.json",
    "review_gate": ROOT / "docs/research/evidence/g07-human-review-rollup-gate-r1.json",
    "hardening_state": ROOT / "docs/research/evidence/selected-route-hardening-state-r1.json",
    "chapter_matrix": ROOT / "production/comic/repair-readiness/ch05-repair-evidence-readiness-matrix-r1.json",
    "p036_readiness": ROOT / "production/comic/repair-readiness/ch05-p036-openai-r2.json",
    "p036_finalizer": ROOT / "production/comic/repair-readiness/ch05-p036-repair-outcome-finalizer-r1.json",
    "production_policy": ROOT / "config/ch05-production-budget-policy-r1.json",
    "production_ledger": ROOT / "docs/research/evidence/ch05-production-cost-ledger-r7.json",
    "budget_audit": ROOT / "docs/research/evidence/g07-aggregate-budget-binding-audit-r3.json",
}


class FrontierError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise FrontierError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_ref(path: Path, payload: dict) -> dict:
    return {
        "record_id": payload.get("record_id", payload.get("protocol_id")),
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
    }


def topological_order(nodes: list[dict], edges: list[dict]) -> list[str]:
    ids = {item["id"] for item in nodes}
    require(len(ids) == len(nodes), "duplicate graph node")
    require(all(edge["prerequisite"] in ids and edge["dependent"] in ids for edge in edges), "edge references missing node")
    incoming = {node_id: 0 for node_id in ids}
    outgoing = {node_id: [] for node_id in ids}
    for edge in edges:
        require(edge["prerequisite"] != edge["dependent"], "self edge")
        incoming[edge["dependent"]] += 1
        outgoing[edge["prerequisite"]].append(edge["dependent"])
    ready = sorted(node_id for node_id, count in incoming.items() if count == 0)
    order = []
    while ready:
        node_id = ready.pop(0)
        order.append(node_id)
        for dependent in sorted(outgoing[node_id]):
            incoming[dependent] -= 1
            if incoming[dependent] == 0:
                ready.append(dependent)
                ready.sort()
    require(len(order) == len(nodes), "dependency graph contains a cycle")
    return order


def build() -> dict:
    payload = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in SOURCES.items()}
    review_protocol = payload["review_protocol"]
    review_gate = payload["review_gate"]
    hardening = payload["hardening_state"]
    matrix = payload["chapter_matrix"]
    readiness = payload["p036_readiness"]
    finalizer = payload["p036_finalizer"]
    policy = payload["production_policy"]
    ledger = payload["production_ledger"]
    budget = payload["budget_audit"]

    require(review_protocol["total_decisions_required"] == 20, "review decision denominator changed")
    require(review_gate["required_decisions"] == 20 and review_gate["actual_decisions"] == 0, "review gate state changed")
    require(review_gate["human_minutes"] is None and review_gate["human_arm_results"] is None, "human review fabricated")
    require(hardening["selection"]["adapter_id"] == "openai_gpt_image_2", "engineering route changed")
    require(hardening["selection"]["engineering_hardening_route_only"] is True, "engineering-only boundary removed")
    require(matrix["medium"] == "comic" and matrix["animation_shot_plan"] is None and matrix["e_conte"] is None, "medium separation changed")
    require(matrix["summary"]["planned_panels"] == 50, "chapter denominator changed")
    require(matrix["summary"]["approved_base_rasters"] == matrix["summary"]["approved_repair_masks"] == 0, "production inputs unexpectedly present")
    require(readiness["production_inputs"] == {
        "approved_base_raster": None,
        "approved_repair_mask": None,
        "external_upload_authority": None,
        "production_budget_reservation": None,
    }, "P036 production inputs changed")
    four_blockers = [
        "APPROVED_BASE_RASTER_MISSING_OR_INVALID",
        "APPROVED_REPAIR_MASK_MISSING_OR_INVALID",
        "EXACT_EXTERNAL_AUTHORITY_MISSING_OR_INVALID",
        "DISTINCT_PRODUCTION_RESERVATION_MISSING_OR_INVALID",
    ]
    require(readiness["offline_preflight"]["blockers"] == four_blockers, "offline prerequisite blockers changed")
    require(finalizer["real_p036"]["blocker_count"] == 9 and finalizer["real_p036"]["blockers"][:4] == four_blockers, "finalizer blockers changed")
    require(finalizer["real_p036"]["render_record"] is None and finalizer["real_p036"]["candidate"] is None, "real outcome unexpectedly present")
    require(policy["state"] == "DISABLED_NO_PRODUCTION_SPEND_OR_UPLOAD_AUTHORITY" and policy["execution_enabled"] is False, "production policy enabled")
    require(policy["maximum_aggregate_cap_usd"] is None and policy["bakeoff_budget_reuse_prohibited"] is True, "budget domain boundary changed")
    require(ledger["approved_aggregate_cap_usd"] is None and ledger["entries"] == [], "production ledger gained authority")
    require(budget["ledger_reconciliation"]["available_usd"] == "98.942623", "G07 remaining capacity changed")

    nodes = [
        {"id": "g07_paid_bakeoff_evidence", "state": "COMPLETE_MEASURED", "authority_class": "LOCAL_EVIDENCE", "facts": {"providers": 4, "required_candidates": 16, "aggregate_paid_usd": "1.057377"}},
        {"id": "g07_blinded_review_packet", "state": "COMPLETE_INSTRUMENTED", "authority_class": "LOCAL_EVIDENCE", "facts": {"required_decisions": 20, "packet_sha256": review_gate["review_packet_sha256"]}},
        {"id": "g07_eligible_human_session", "state": "BLOCKED_HUMAN_JUDGMENT", "authority_class": "IDENTIFIED_HUMAN_REVIEW", "facts": {"completed_decisions": 0, "remaining_decisions": 20, "human_minutes": None}},
        {"id": "g07_human_dimension_rollup", "state": "WAITING_DEPENDENCY", "authority_class": "DERIVED_AFTER_HUMAN_REVIEW", "facts": {"human_arm_results": None, "automatic_ranking": False}},
        {"id": "openai_engineering_hardening_route", "state": "COMPLETE_MEASURED_NOT_ART_ACCEPTED", "authority_class": "ENGINEERING_DECISION", "facts": {"adapter_id": "openai_gpt_image_2", "decision": "ADR-0025", "automatic_reselection": False}},
        {"id": "ch05_comic_panel_plan_denominator", "state": "COMPLETE_LOCAL", "authority_class": "COMIC_PANEL_PLAN_ONLY", "facts": {"planned_panels": 50, "explicit_repair_candidates": 4, "animation_shot_plan": None, "e_conte": None}},
        {"id": "p036_local_mechanics_policy", "state": "COMPLETE_LOCAL_NOT_PRODUCTION_READY", "authority_class": "LOCAL_ENGINEERING", "facts": {"selector_profiles": 2, "panel_policies": 1}},
        {"id": "p036_approved_base_raster", "state": "BLOCKED_INPUT_APPROVAL", "authority_class": "IDENTIFIED_HUMAN_INPUT_REVIEW", "facts": {"approved_count": 0}},
        {"id": "p036_approved_repair_mask", "state": "BLOCKED_INPUT_APPROVAL", "authority_class": "IDENTIFIED_HUMAN_INPUT_REVIEW", "facts": {"approved_count": 0}},
        {"id": "p036_exact_external_authority", "state": "BLOCKED_USER_AUTHORITY", "authority_class": "EXACT_PROVIDER_MODEL_ENDPOINT_INPUT_PACKAGE_AUTHORITY", "facts": {"authority": None, "expanded_upload_authority": False}},
        {"id": "ch05_distinct_production_cap", "state": "BLOCKED_USER_AUTHORITY", "authority_class": "DISTINCT_CH05_AGGREGATE_BUDGET_AUTHORITY", "facts": {"approved_cap_usd": None, "g07_available_usd_not_reusable": "98.942623"}},
        {"id": "current_primary_terms_pricing_data_use_refresh", "state": "REQUIRED_BEFORE_EXTERNAL_EXECUTION", "authority_class": "LOCAL_RESEARCH_THEN_POLICY_REVIEW", "facts": {"refresh_trigger": "before any CH05 paid provider execution"}},
        {"id": "ch05_aggregate_production_reservation", "state": "WAITING_AUTHORITY", "authority_class": "AGGREGATE_LEDGER", "facts": {"entries": 0, "held_usd": "0.000000"}},
        {"id": "p036_offline_request_preflight", "state": "BLOCKED_FOUR_PREREQUISITES", "authority_class": "FAIL_CLOSED_LOCAL_COMPILER", "facts": {"blockers": four_blockers, "request_body_constructed": False, "network_capability_present": False}},
        {"id": "p036_paid_submission_journal", "state": "WAITING_AUTHORIZED_EXECUTION", "authority_class": "EXTERNAL_EXECUTION", "facts": {"journal": None, "provider_request": None}},
        {"id": "p036_candidate_and_cost_reconciliation", "state": "WAITING_PROVIDER_OUTCOME", "authority_class": "PROVIDER_RETURNED_EVIDENCE", "facts": {"candidate": None, "cost_reconciliation": None}},
        {"id": "p036_real_exact_base_boundary_measurement", "state": "WAITING_EXACT_CANDIDATE", "authority_class": "LOCAL_MEASUREMENT_AFTER_OUTPUT", "facts": {"real_results": 0}},
        {"id": "p036_eligible_timed_seam_review", "state": "WAITING_MEASUREMENT_AND_HUMAN", "authority_class": "IDENTIFIED_HUMAN_REVIEW", "facts": {"sessions": 0, "human_minutes": None}},
        {"id": "p036_render_record_v2_1_finalization", "state": "BLOCKED_NINE_EVIDENCE_GATES", "authority_class": "FAIL_CLOSED_LOCAL_FINALIZER", "facts": {"blocker_count": 9, "render_record": None}},
        {"id": "p036_panel_acceptance", "state": "WAITING_ELIGIBLE_HUMAN_DECISION", "authority_class": "IDENTIFIED_HUMAN_ACCEPTANCE", "facts": {"accepted": False}},
    ]
    edges = [
        {"prerequisite": "g07_paid_bakeoff_evidence", "dependent": "g07_blinded_review_packet"},
        {"prerequisite": "g07_blinded_review_packet", "dependent": "g07_eligible_human_session"},
        {"prerequisite": "g07_eligible_human_session", "dependent": "g07_human_dimension_rollup"},
        {"prerequisite": "g07_paid_bakeoff_evidence", "dependent": "openai_engineering_hardening_route"},
        {"prerequisite": "ch05_comic_panel_plan_denominator", "dependent": "p036_local_mechanics_policy"},
        {"prerequisite": "p036_local_mechanics_policy", "dependent": "p036_offline_request_preflight"},
        {"prerequisite": "p036_approved_base_raster", "dependent": "p036_offline_request_preflight"},
        {"prerequisite": "p036_approved_repair_mask", "dependent": "p036_offline_request_preflight"},
        {"prerequisite": "p036_exact_external_authority", "dependent": "p036_offline_request_preflight"},
        {"prerequisite": "ch05_distinct_production_cap", "dependent": "ch05_aggregate_production_reservation"},
        {"prerequisite": "ch05_aggregate_production_reservation", "dependent": "p036_offline_request_preflight"},
        {"prerequisite": "current_primary_terms_pricing_data_use_refresh", "dependent": "p036_paid_submission_journal"},
        {"prerequisite": "p036_offline_request_preflight", "dependent": "p036_paid_submission_journal"},
        {"prerequisite": "p036_paid_submission_journal", "dependent": "p036_candidate_and_cost_reconciliation"},
        {"prerequisite": "p036_candidate_and_cost_reconciliation", "dependent": "p036_real_exact_base_boundary_measurement"},
        {"prerequisite": "p036_real_exact_base_boundary_measurement", "dependent": "p036_eligible_timed_seam_review"},
        {"prerequisite": "p036_candidate_and_cost_reconciliation", "dependent": "p036_render_record_v2_1_finalization"},
        {"prerequisite": "p036_real_exact_base_boundary_measurement", "dependent": "p036_render_record_v2_1_finalization"},
        {"prerequisite": "p036_eligible_timed_seam_review", "dependent": "p036_render_record_v2_1_finalization"},
        {"prerequisite": "p036_render_record_v2_1_finalization", "dependent": "p036_panel_acceptance"},
    ]
    order = topological_order(nodes, edges)
    source_refs = {name: source_ref(SOURCES[name], payload[name]) for name in SOURCES}
    return {
        "record_type": "SelectedRouteAuthorityDependencyFrontier",
        "schema_version": "1.0",
        "record_id": "ng-selected-route-authority-dependency-frontier-r1",
        "state": "LOCAL_HARDENING_VALIDATED_REAL_REVIEW_AND_PRODUCTION_AUTHORITY_FRONTIER_EXPLICIT",
        "sources": source_refs,
        "graph": {"nodes": nodes, "edges": edges, "topological_order": order, "acyclic": True},
        "root_authority_frontier": [
            {"node_id": "g07_eligible_human_session", "needed_from": "identified human reviewer", "scope": "20 immutable blinded decisions; no invented minutes"},
            {"node_id": "p036_approved_base_raster", "needed_from": "authorized human input review", "scope": "exact fictional panel base bytes/hash"},
            {"node_id": "p036_approved_repair_mask", "needed_from": "authorized human input review", "scope": "exact panel-specific causal mask bytes/hash"},
            {"node_id": "p036_exact_external_authority", "needed_from": "user", "scope": "exact OpenAI model snapshot, endpoint, and complete input-package hash"},
            {"node_id": "ch05_distinct_production_cap", "needed_from": "user", "scope": "distinct CH05 aggregate cap; G07 remainder cannot be reused"},
        ],
        "autonomous_local_frontier": [
            "validate and release safe tracked source/evidence snapshots",
            "extend no-network release gates append-only as validators advance",
            "maintain deterministic rebuild/runtime/source manifests",
            "prepare hash-bound review and production handoff packets without filling human decisions or authority fields",
        ],
        "prohibited_inferences": [
            "G07 remaining capacity grants CH05 production budget",
            "engineering route selection equals visual acceptance or commercial clearance",
            "synthetic base/mask/review fixtures are eligible production evidence",
            "a topology profile grants panel-specific policy or upload authority",
            "ComicPanelPlan can be replaced by AnimationShotPlan or E-Conte",
        ],
        "summary": {
            "graph_nodes": len(nodes),
            "graph_edges": len(edges),
            "root_authority_items": 5,
            "g07_review_decisions_complete": 0,
            "g07_review_decisions_required": 20,
            "ch05_planned_panels": 50,
            "p036_root_preflight_blockers": 4,
            "p036_total_finalization_blockers": 9,
            "approved_ch05_inputs": 0,
            "ch05_production_cap_usd": None,
            "real_render_records_v2_1": 0,
            "accepted_ch05_panels": 0,
            "provider_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        },
        "next_external_action": None,
        "boundary": "This graph records dependencies; it grants no judgment, input approval, upload scope, production budget, request capability, or acceptance.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    actions = [
        lambda item: item["graph"].update(acyclic=False),
        lambda item: item["graph"]["nodes"].pop(),
        lambda item: item["graph"]["edges"].pop(),
        lambda item: item["root_authority_frontier"].pop(),
        lambda item: item["summary"].update(root_authority_items=4),
        lambda item: item["summary"].update(g07_review_decisions_complete=20),
        lambda item: item["summary"].update(p036_root_preflight_blockers=3),
        lambda item: item["summary"].update(p036_total_finalization_blockers=8),
        lambda item: item["summary"].update(approved_ch05_inputs=2),
        lambda item: item["summary"].update(ch05_production_cap_usd="100.000000"),
        lambda item: item["summary"].update(real_render_records_v2_1=1),
        lambda item: item["summary"].update(accepted_ch05_panels=1),
        lambda item: item["summary"].update(provider_requests=1),
        lambda item: item["summary"].update(external_uploads=1),
        lambda item: item["summary"].update(external_cost_usd="1.000000"),
        lambda item: item.update(next_external_action="submit P036"),
        lambda item: item["prohibited_inferences"].pop(0),
        lambda item: item["sources"]["production_policy"].update(sha256="0" * 64),
    ]
    for action in actions:
        item = copy.deepcopy(expected)
        action(item)
        values.append(item)
    return sum(item != expected for item in values), len(values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", type=Path)
    args = parser.parse_args()
    try:
        expected = build()
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked authority frontier differs")
        rejected, total = mutations(expected)
        require(rejected == total, "authority-frontier mutations not rejected")
    except (FrontierError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings (20-node/20-edge acyclic dependency graph; 5 root authority items)")
    print(f"G07 review 0/20; P036 blockers 4 root/9 total; {rejected}/{total} mutations rejected; 0 requests/uploads/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
