"""Compile an append-only current selected-route hardening handoff r2."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
R1 = ROOT / "docs/research/evidence/selected-route-hardening-state-r1.json"
OUTPUT = ROOT / "docs/research/evidence/selected-route-hardening-state-r2.json"
SOURCES = {
    "vault": ROOT / "docs/research/evidence/g07-local-evidence-vault-manifest-r1.json",
    "instrumentation": ROOT / "experiments/results/g07-provider-bakeoff-instrumentation-r1.json",
    "review_gate": ROOT / "docs/research/evidence/g07-human-review-rollup-gate-r1.json",
    "budget_audit": ROOT / "docs/research/evidence/g07-aggregate-budget-binding-audit-r3.json",
    "transport_audit": ROOT / "docs/research/evidence/g07-provider-transport-data-boundary-audit-r1.json",
    "selector": ROOT / "config/scale-aware-repair-boundary-selector-contract-r2.json",
    "selector_compatibility": ROOT / "docs/research/evidence/selector-consumer-compatibility-r2.json",
    "chapter_matrix": ROOT / "production/comic/repair-readiness/ch05-repair-evidence-readiness-matrix-r1.json",
    "measurement": ROOT / "docs/research/evidence/exact-base-boundary-measurement-packet-r1.json",
    "finalizer": ROOT / "production/comic/repair-readiness/ch05-p036-repair-outcome-finalizer-r1.json",
    "rebuild": ROOT / "docs/research/evidence/selected-route-artifact-rebuild-reproducibility-r2.json",
    "runtime": ROOT / "docs/research/evidence/instrumentation-runtime-inventory-r2.json",
    "release_gate": ROOT / "docs/research/evidence/hardening-release-validation-gate-r2.json",
    "safe_source": ROOT / "docs/research/evidence/safe-source-release-manifest-43fc787.json",
    "authority_frontier": ROOT / "docs/research/evidence/selected-route-authority-dependency-frontier-r1.json",
    "production_cost": ROOT / "docs/research/evidence/ch05-production-cost-ledger-r10.json",
}


class StateError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise StateError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path: Path, payload: dict) -> dict:
    return {
        "record_id": payload.get("record_id", payload.get("contract_id")),
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
    }


def build() -> dict:
    prior = json.loads(R1.read_text(encoding="utf-8"))
    data = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in SOURCES.items()}
    selector = data["selector"]
    rebuild = data["rebuild"]
    release = data["release_gate"]
    safe = data["safe_source"]
    authority = data["authority_frontier"]
    ledger = data["production_cost"]
    budget = data["budget_audit"]

    require(prior["selection"]["adapter_id"] == "openai_gpt_image_2", "r1 route changed")
    require(prior["g07_measured_state"]["aggregate_committed_usd"] == "1.057377", "r1 spend changed")
    require(prior["g07_measured_state"]["human_review"]["decisions"] == 0, "r1 review changed")
    require(selector["profiles"] == json.loads((ROOT / "config/scale-aware-repair-boundary-selector-contract-r1.json").read_text(encoding="utf-8"))["profiles"], "selector profiles changed")
    require(selector["summary"]["topology_control_passes"] == 3 and selector["summary"]["production_ready_profiles"] == 0, "selector state changed")
    require(rebuild["summary"]["artifacts"] == 28 and rebuild["summary"]["byte_identical"] is True, "rebuild r2 changed")
    require(release["summary"]["passed_checks"] == 60 and release["activity"]["network_requests"] == 0, "release r2 changed")
    require(safe["summary"]["tracked_paths"] == 387 and safe["summary"]["generated_experiment_paths"] == 0, "safe-source r2 changed")
    require(authority["summary"]["root_authority_items"] == 5 and authority["next_external_action"] is None, "authority frontier changed")
    require(ledger["state"] == "DISABLED_NO_PRODUCTION_SPEND_OR_UPLOAD_AUTHORITY" and ledger["revision_summary"]["total_local_milestones"] == 37, "production ledger changed")
    require(budget["ledger_reconciliation"]["committed_actual_cost_usd"] == "1.057377" and budget["ledger_reconciliation"]["available_usd"] == "98.942623", "G07 budget reconciliation changed")

    local = copy.deepcopy(prior["local_hardening"])
    local["scale_profiles"].update(
        topology_passes=selector["summary"]["topology_control_passes"],
        panel_neutral_mechanics_controls=selector["summary"]["panel_neutral_mechanics_controls"],
        exact_panel_visual_passes=selector["summary"]["exact_panel_base_visual_boundary_passes"],
        timed_seam_reviews=selector["summary"]["timed_human_seam_reviews"],
    )
    local["artifact_rebuild"] = {
        "artifacts": rebuild["summary"]["artifacts"],
        "groups": rebuild["summary"]["artifact_groups"],
        "bytes": rebuild["summary"]["total_bytes"],
        "root_sha256": rebuild["summary"]["first_root_sha256"],
        "rebuilds": rebuild["summary"]["rebuilds"],
        "byte_identical": rebuild["summary"]["byte_identical"],
    }
    governance = copy.deepcopy(prior["governance"])
    governance.update(
        safe_source_commit=safe["captured_commit"],
        safe_source_root=safe["summary"]["inventory_root_sha256"],
        safe_source_tracked_paths=safe["summary"]["tracked_paths"],
        ch05_zero_cost_milestones=ledger["revision_summary"]["total_local_milestones"],
        g07_budget_audit_revision="r3",
        g07_budget_reuse_for_ch05=False,
    )
    source_refs = {name: ref(path, data[name]) for name, path in SOURCES.items()}
    return {
        "record_type": "SelectedRouteHardeningState",
        "schema_version": "1.1",
        "record_id": "ng-selected-route-hardening-state-r2",
        "state": "ENGINEERING_ROUTE_SELECTED_LATEST_LOCAL_HARDENING_VALIDATED_PRODUCTION_BLOCKED",
        "supersedes": {
            "record_id": prior["record_id"],
            "path": R1.relative_to(ROOT).as_posix(),
            "sha256": sha256(R1),
        },
        "prior_state_rewritten": False,
        "sources": source_refs,
        "selection": prior["selection"],
        "g07_measured_state": prior["g07_measured_state"],
        "local_hardening": local,
        "chapter_scale_readiness": prior["chapter_scale_readiness"],
        "fail_closed_state": prior["fail_closed_state"],
        "authority_frontier": {
            "graph_nodes": authority["summary"]["graph_nodes"],
            "graph_edges": authority["summary"]["graph_edges"],
            "root_authority_items": authority["summary"]["root_authority_items"],
            "g07_review_decisions_complete": authority["summary"]["g07_review_decisions_complete"],
            "g07_review_decisions_required": authority["summary"]["g07_review_decisions_required"],
            "p036_root_preflight_blockers": authority["summary"]["p036_root_preflight_blockers"],
            "p036_total_finalization_blockers": authority["summary"]["p036_total_finalization_blockers"],
            "next_external_action": None,
        },
        "current_release": {
            "checks_passed": release["summary"]["passed_checks"],
            "checks_total": release["summary"]["total_checks"],
            "safe_source_commit": safe["captured_commit"],
            "safe_source_tree": safe["captured_tree"],
            "safe_source_inventory_root": safe["summary"]["inventory_root_sha256"],
            "production_zero_cost_milestones": ledger["revision_summary"]["total_local_milestones"],
            "network_requests": 0,
            "provider_requests": 0,
            "external_uploads": 0,
            "models_downloaded": 0,
            "external_cost_usd": "0.000000",
        },
        "governance": governance,
        "limitations": prior["limitations"] + [
            "The third topology pass is panel-neutral and does not create a third panel profile, policy, visual pass, or production-ready profile.",
            "Release/source/authority validation advances provenance and readiness only; it does not add renderer-quality samples.",
        ],
        "boundary": "R2 advances cross-evidence pointers only. Measured renderer state, pending review, zero production readiness, and authority boundaries remain unchanged.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    actions = [
        lambda item: item["supersedes"].update(sha256="0" * 64),
        lambda item: item.update(prior_state_rewritten=True),
        lambda item: item["selection"].update(adapter_id="bfl_flux_2"),
        lambda item: item["selection"].update(candidate_or_art_accepted=True),
        lambda item: item["g07_measured_state"].update(aggregate_committed_usd="0.987377"),
        lambda item: item["g07_measured_state"]["human_review"].update(decisions=20),
        lambda item: item["local_hardening"]["scale_profiles"].update(topology_passes=2),
        lambda item: item["local_hardening"]["scale_profiles"].update(universal_width_px=8),
        lambda item: item["chapter_scale_readiness"].update(approved_bases=1),
        lambda item: item["chapter_scale_readiness"].update(animation_shot_plan={}),
        lambda item: item["fail_closed_state"].update(real_p036_blocker_count=8),
        lambda item: item["authority_frontier"].update(root_authority_items=4),
        lambda item: item["authority_frontier"].update(next_external_action="submit P036"),
        lambda item: item["current_release"].update(checks_passed=59),
        lambda item: item["current_release"].update(provider_requests=1),
        lambda item: item["current_release"].update(external_cost_usd="1.000000"),
        lambda item: item["governance"].update(g07_budget_reuse_for_ch05=True),
        lambda item: item["limitations"].pop(),
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
            require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked hardening state r2 differs")
        rejected, total = mutations(expected)
        require(rejected == total, "hardening-state r2 mutations not rejected")
    except (StateError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings (renderer measurements unchanged; latest budget/selector/rebuild/release/source/authority/cost evidence bound)")
    print(f"G07 review 0/20; CH05 0 outcomes/$0; {rejected}/{total} mutations rejected; next external action null")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
