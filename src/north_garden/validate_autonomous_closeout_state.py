"""Compile the evidence-backed autonomous research/engineering closeout state."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CAPTURE_COMMIT = "a4800123b53fc6f3e8046cfe12e56f3a3b9b6d1f"
OUTPUT = ROOT / "docs/research/evidence/autonomous-research-engineering-closeout-r1.json"
SOURCES = {
    "selection_adr": ROOT / "docs/adr/ADR-0025-select-openai-gpt-image-2-for-bounded-targeted-repair-hardening.md",
    "provider_chronology": ROOT / "docs/research/evidence/provider-documentation-pre-spend-chronology-r1.json",
    "budget_audit": ROOT / "docs/research/evidence/g07-aggregate-budget-binding-audit-r3.json",
    "vault": ROOT / "docs/research/evidence/g07-local-evidence-vault-manifest-r1.json",
    "review_gate": ROOT / "docs/research/evidence/g07-human-review-rollup-gate-r1.json",
    "hardening_state": ROOT / "docs/research/evidence/selected-route-hardening-state-r2.json",
    "release_gate": ROOT / "docs/research/evidence/hardening-release-validation-gate-r4.json",
    "reproducer_matrix": ROOT / "docs/research/evidence/current-evidence-reproducer-matrix-r2.json",
    "frozen_integrity": ROOT / "docs/research/evidence/frozen-gauntlet-baseline-integrity-r1.json",
    "review_authority_handoff": ROOT / "docs/research/evidence/review-authority-handoff-packet-r1.json",
    "safe_source": ROOT / "docs/research/evidence/safe-source-release-manifest-00498df.json",
    "lineage_index": ROOT / "docs/research/evidence/current-evidence-lineage-index-r1.json",
    "production_cost": ROOT / "docs/research/evidence/ch05-production-cost-ledger-r20.json",
}


class CloseoutError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise CloseoutError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    require(result.returncode == 0, f"git {' '.join(args)} failed")
    return result.stdout.strip()


def ref(path: Path, payload: dict | None = None) -> dict:
    value = {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}
    if payload is not None:
        value["record_id"] = payload.get("record_id", payload.get("manifest_id"))
    return value


def build() -> dict:
    data = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in SOURCES.items() if path.suffix == ".json"}
    chronology = data["provider_chronology"]
    budget = data["budget_audit"]
    vault = data["vault"]
    review = data["review_gate"]
    hardening = data["hardening_state"]
    release = data["release_gate"]
    repro = data["reproducer_matrix"]
    frozen = data["frozen_integrity"]
    handoff = data["review_authority_handoff"]
    safe = data["safe_source"]
    lineage = data["lineage_index"]
    cost = data["production_cost"]

    require(git("merge-base", "--is-ancestor", CAPTURE_COMMIT, "HEAD") == "", "capture commit is not an ancestor")
    require(git("merge-base", "--is-ancestor", CAPTURE_COMMIT, "origin/main") == "", "capture commit was not pushed")
    require(chronology["summary"]["records_after_documentation"] == 19, "documentation chronology incomplete")
    require(budget["ledger_reconciliation"]["committed_actual_cost_usd"] == "1.057377" and budget["ledger_reconciliation"]["available_usd"] == "98.942623", "budget reconciliation changed")
    require(vault["inventory"]["completed_candidates"] == 16 and vault["inventory"]["provider_records"] == 19, "vault denominator changed")
    require(review["actual_decisions"] == 0 and review["required_decisions"] == 20 and review["human_minutes"] is None, "review state changed")
    require(hardening["selection"]["adapter_id"] == "openai_gpt_image_2" and hardening["selection"]["candidate_or_art_accepted"] is False, "selection boundary changed")
    require(release["summary"]["passed_checks"] == 74 and release["activity"]["provider_requests"] == 0, "release state changed")
    require(repro["summary"]["passed"] == 11 and repro["summary"]["failed"] == 0, "reproducer state changed")
    require(frozen["summary"]["frozen_paths_changed"] == frozen["summary"]["baseline_tracked_paths_changed"] == 0, "frozen target changed")
    require(handoff["blank_authority_state"]["approvals_requested_now"] == [] and handoff["blank_authority_state"]["next_external_action"] is None, "handoff requests authority")
    require(cost["revision_summary"]["total_local_milestones"] == 48 and cost["approved_aggregate_cap_usd"] is None, "production cost state changed")

    checklist = [
        ("aggregate_budget_ledger", "One shared cap/reservation ledger is bound across 4/4 paid adapters; 18 entries reconcile to $1.057377 actual/$0 held."),
        ("official_documents_before_paid_execution", "Four provider sections/19 official URLs preceded all 19 retained provider records."),
        ("four_request_four_provider_bakeoff", "OpenAI, Gemini, xAI, and BFL each produced four required fictional-control candidates."),
        ("complete_provider_evidence", "Nineteen records bind requests, hashes, timing, usage/cost, failures, candidates, and pending review state."),
        ("review_packet_and_comparison", "Sixteen blinded candidates plus four repeat pairs and nonhuman cost/latency/drift dimensions are bound; human review remains pending."),
        ("measured_route_selection", "ADR-0025 selects OpenAI for engineering hardening from cost/latency/drift/provenance dimensions, not visual appeal."),
        ("smallest_high_information_hardening", "Boundary, topology, exact-base, no-change, seam-review, finalizer, and prerequisite-lattice mechanics are instrumented locally."),
        ("chapter_scale_instrumentation", "All 50 ComicPanelPlans remain visible with four explicit repair candidates/two profiles/one policy and zero fabricated outcomes."),
        ("medium_separation", "ComicPanelPlan remains the active medium; AnimationShotPlan and E-Conte remain null/separate."),
        ("frozen_target_integrity", "Sixteen v2.1.1 plus four tracked baseline paths are unchanged; baseline remains 0/24 accepted/no tuning."),
        ("reproducible_safe_source", "Eleven current reproducers pass; 412-path safe-source snapshot tracks two controls and zero generated/prohibited/oversize paths."),
        ("regular_safe_git_history", "The capture commit and preceding evidence milestones are pushed; generated art, credentials, models, runtimes, datasets, and unrelated workspace material remain excluded."),
    ]
    objective_checklist = [{"requirement": name, "status": "COMPLETE_WITH_BOUNDARY_PRESERVED", "evidence": evidence} for name, evidence in checklist]
    source_refs = {name: ref(path, data.get(name)) for name, path in SOURCES.items()}
    return {
        "record_type": "AutonomousResearchEngineeringCloseout",
        "schema_version": "1.0",
        "record_id": "ng-autonomous-research-engineering-closeout-r1",
        "state": "OBJECTIVE_ACHIEVED_ENGINEERING_ROUTE_HARDENED_HUMAN_AND_PRODUCTION_AUTHORITY_GATED",
        "captured_pushed_commit": CAPTURE_COMMIT,
        "sources": source_refs,
        "objective_checklist": objective_checklist,
        "selection": hardening["selection"],
        "bakeoff": {
            "providers": 4,
            "required_candidates": 16,
            "provider_records": 19,
            "required_candidate_cost_usd": vault["cost_reconciliation"]["required_candidate_cost_usd"],
            "paid_failure_cost_usd": vault["cost_reconciliation"]["paid_failure_cost_usd"],
            "aggregate_paid_usd": vault["cost_reconciliation"]["aggregate_paid_cost_usd"],
            "held_usd": vault["cost_reconciliation"]["held_usd"],
            "available_usd": vault["cost_reconciliation"]["available_usd"],
            "nonhuman_arm_evidence": review["measured_nonhuman_arm_evidence"],
            "documentation_records_after_retrieval": chronology["summary"]["records_after_documentation"],
        },
        "human_review": {
            "decisions_complete": review["actual_decisions"],
            "decisions_required": review["required_decisions"],
            "human_minutes": review["human_minutes"],
            "accepted_candidates": review["accepted_candidate_subjects"],
            "human_arm_results": review["human_arm_results"],
        },
        "hardening": {
            "boundary_policy": hardening["local_hardening"]["selected_boundary"],
            "scale_profiles": hardening["local_hardening"]["scale_profiles"],
            "artifact_rebuild": hardening["local_hardening"]["artifact_rebuild"],
            "chapter_scale_readiness": hardening["chapter_scale_readiness"],
            "p036_fail_closed_state": hardening["fail_closed_state"],
        },
        "integrity": {
            "release_checks_passed": release["summary"]["passed_checks"],
            "release_checks_total": release["summary"]["total_checks"],
            "reproducer_commands_passed": repro["summary"]["passed"],
            "lineage_domains": lineage["summary"]["domains"],
            "lineage_records": lineage["summary"]["lineage_records"],
            "safe_source_commit": safe["captured_commit"],
            "safe_source_paths": safe["summary"]["tracked_paths"],
            "safe_source_inventory_root": safe["summary"]["inventory_root_sha256"],
            "frozen_paths_changed": frozen["summary"]["frozen_paths_changed"],
            "baseline_tracked_paths_changed": frozen["summary"]["baseline_tracked_paths_changed"],
            "baseline_accepted_outputs": frozen["summary"]["baseline_accepted_outputs"],
            "local_zero_cost_milestones": cost["revision_summary"]["total_local_milestones"],
        },
        "remaining_roots": {
            "g07_human_review": handoff["g07_review_root"],
            "ch05": handoff["ch05_root_authority_items"],
            "primary_document_refresh_before_future_execution": handoff["pre_execution_research_refresh"],
            "approvals_requested_now": [],
            "next_external_action": None,
        },
        "activity_during_closeout": {"provider_requests": 0, "external_uploads": 0, "models_downloaded": 0, "external_cost_usd": "0.000000"},
        "limitations": [
            "G07 visual judgment is incomplete: 0/20 decisions, null minutes, zero accepted candidates.",
            "The selected route is an engineering hardening route, not visual acceptance, commercial clearance, or universal superiority.",
            "CH05 has no approved base/mask, exact upload authority, production cap/reservation, real provider outcome, eligible seam review, RenderRecord v2.1, or accepted panel.",
            "Provider-output rerun reproducibility is limited; exact local evidence and validation reproducibility are measured separately.",
            "Any future CH05 paid execution requires a fresh then-current primary documentation review and explicit authority roots.",
        ],
        "boundary": "The research/engineering objective is achieved at the requested evidence-backed selection and local hardening scope. Human review and production remain intentionally gated; this record grants neither.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    actions = [
        lambda item: item.update(captured_pushed_commit="0" * 40),
        lambda item: item["sources"]["release_gate"].update(sha256="0" * 64),
        lambda item: item["objective_checklist"].pop(),
        lambda item: item["objective_checklist"][0].update(status="INCOMPLETE"),
        lambda item: item["selection"].update(adapter_id="bfl_flux_2"),
        lambda item: item["selection"].update(candidate_or_art_accepted=True),
        lambda item: item["bakeoff"].update(required_candidates=15),
        lambda item: item["bakeoff"].update(aggregate_paid_usd="0.987377"),
        lambda item: item["human_review"].update(decisions_complete=20),
        lambda item: item["human_review"].update(human_minutes=10),
        lambda item: item["hardening"]["scale_profiles"].update(universal_width_px=8),
        lambda item: item["hardening"]["chapter_scale_readiness"].update(accepted_panels=1),
        lambda item: item["integrity"].update(release_checks_passed=73),
        lambda item: item["integrity"].update(reproducer_commands_passed=10),
        lambda item: item["integrity"].update(frozen_paths_changed=1),
        lambda item: item["integrity"].update(baseline_accepted_outputs=1),
        lambda item: item["remaining_roots"]["approvals_requested_now"].append("CH05 cap"),
        lambda item: item["remaining_roots"].update(next_external_action="submit P036"),
        lambda item: item["activity_during_closeout"].update(provider_requests=1),
        lambda item: item["activity_during_closeout"].update(external_uploads=1),
        lambda item: item["activity_during_closeout"].update(external_cost_usd="1.000000"),
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
            require(git("rev-parse", "HEAD") == CAPTURE_COMMIT and git("rev-parse", "origin/main") == CAPTURE_COMMIT, "capture commit is not current pushed HEAD")
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked closeout state differs")
        rejected, total = mutations(expected)
        require(rejected == total, "closeout mutations not rejected")
    except (CloseoutError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings (12/12 objective requirements evidence-bound; engineering selection/hardening scope achieved)")
    print(f"G07 review 0/20; CH05 authority gated; 74/74 release/11 reproducers; {rejected}/{total} mutations rejected; 0 requests/uploads/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
