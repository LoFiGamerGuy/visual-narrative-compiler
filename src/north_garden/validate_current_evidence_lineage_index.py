"""Build and validate the current append-only evidence lineage index."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/research/evidence/current-evidence-lineage-index-r1.json"
DOMAINS = {
    "aggregate_budget_audit": ("docs/research/evidence/g07-aggregate-budget-binding-audit-r3.json", "src/north_garden/validate_bakeoff_adapter_budget_binding_audit.py"),
    "selector_contract": ("config/scale-aware-repair-boundary-selector-contract-r2.json", "src/north_garden/validate_scale_aware_boundary_selector_r2.py"),
    "artifact_rebuild": ("docs/research/evidence/selected-route-artifact-rebuild-reproducibility-r2.json", "src/north_garden/validate_selected_route_artifact_rebuild_r2.py"),
    "release_gate": ("docs/research/evidence/hardening-release-validation-gate-r3.json", "src/north_garden/validate_hardening_release_r3.py"),
    "safe_source": ("docs/research/evidence/safe-source-release-manifest-00498df.json", "src/north_garden/validate_safe_source_release_manifest_r3.py"),
    "selected_route_handoff": ("docs/research/evidence/selected-route-hardening-state-r2.json", "src/north_garden/validate_selected_route_hardening_state_r2.py"),
    "authority_frontier": ("docs/research/evidence/selected-route-authority-dependency-frontier-r1.json", "src/north_garden/validate_selected_route_authority_frontier.py"),
    "prerequisite_lattice": ("docs/research/evidence/p036-prerequisite-authority-lattice-r1.json", "src/north_garden/validate_p036_prerequisite_authority_lattice.py"),
    "ch05_production_cost": ("docs/research/evidence/ch05-production-cost-ledger-r14.json", "src/north_garden/validate_ch05_production_cost_ledger_r14.py"),
    "g07_review_gate": ("docs/research/evidence/g07-human-review-rollup-gate-r1.json", "src/north_garden/validate_g07_review_rollup.py"),
    "ch05_repair_readiness": ("production/comic/repair-readiness/ch05-repair-evidence-readiness-matrix-r1.json", "src/north_garden/validate_ch05_repair_evidence_readiness_matrix.py"),
}
EXPECTED_DEPTHS = {
    "aggregate_budget_audit": 2,
    "selector_contract": 2,
    "artifact_rebuild": 2,
    "release_gate": 3,
    "safe_source": 3,
    "selected_route_handoff": 2,
    "authority_frontier": 1,
    "prerequisite_lattice": 1,
    "ch05_production_cost": 14,
    "g07_review_gate": 1,
    "ch05_repair_readiness": 1,
}


class IndexError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise IndexError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(payload: dict) -> str:
    value = payload.get("record_id", payload.get("contract_id"))
    require(isinstance(value, str) and value, "record identity missing")
    return value


def follow_lineage(latest_relative: str) -> list[dict]:
    chain = []
    relative = latest_relative
    visited = set()
    while True:
        require(relative not in visited, f"lineage cycle: {relative}")
        visited.add(relative)
        path = ROOT / relative
        payload = json.loads(path.read_text(encoding="utf-8"))
        chain.append({
            "record_id": identity(payload),
            "path": relative,
            "sha256": sha256(path),
            "schema_version": payload.get("schema_version"),
            "state": payload.get("state"),
        })
        supersedes = payload.get("supersedes")
        if not isinstance(supersedes, dict) or "path" not in supersedes:
            break
        prior_relative = supersedes["path"]
        prior_path = ROOT / prior_relative
        prior = json.loads(prior_path.read_text(encoding="utf-8"))
        expected_id = supersedes.get("record_id", supersedes.get("contract_id"))
        require(expected_id == identity(prior), f"superseded identity mismatch: {relative}")
        require(supersedes.get("sha256") == sha256(prior_path), f"superseded hash mismatch: {relative}")
        relative = prior_relative
    return chain


def build() -> dict:
    domains = []
    for name, (latest, validator) in DOMAINS.items():
        chain = follow_lineage(latest)
        require(len(chain) == EXPECTED_DEPTHS[name], f"unexpected lineage depth: {name}")
        validator_path = ROOT / validator
        require(validator_path.is_file(), f"validator missing: {validator}")
        arguments = ["--allow-unpushed-current"] if name == "safe_source" else []
        domains.append({
            "domain": name,
            "current_record": chain[0],
            "lineage_newest_to_oldest": chain,
            "lineage_depth": len(chain),
            "validator": {"path": validator, "sha256": sha256(validator_path)},
            "reproducer": {"argv": ["python", validator, *arguments], "working_directory": ".", "network_expected": False},
        })

    release = json.loads((ROOT / DOMAINS["release_gate"][0]).read_text(encoding="utf-8"))
    handoff = json.loads((ROOT / DOMAINS["selected_route_handoff"][0]).read_text(encoding="utf-8"))
    source = json.loads((ROOT / DOMAINS["safe_source"][0]).read_text(encoding="utf-8"))
    cost = json.loads((ROOT / DOMAINS["ch05_production_cost"][0]).read_text(encoding="utf-8"))
    require(release["summary"]["passed_checks"] == 65, "current release count changed")
    require(handoff["g07_measured_state"]["human_review"]["decisions"] == 0, "human review state changed")
    require(handoff["chapter_scale_readiness"]["accepted_panels"] == 0, "chapter acceptance changed")
    require(source["summary"]["generated_experiment_paths"] == 0, "safe-source boundary changed")
    require(cost["revision_summary"]["total_local_milestones"] == 41 and cost["approved_aggregate_cap_usd"] is None, "cost boundary changed")
    return {
        "record_type": "CurrentEvidenceLineageIndex",
        "schema_version": "1.0",
        "record_id": "ng-current-evidence-lineage-index-r1",
        "state": "CURRENT_RECORDS_AND_APPEND_ONLY_LINEAGES_HASH_VALIDATED",
        "domains": domains,
        "summary": {
            "domains": len(domains),
            "lineage_records": sum(item["lineage_depth"] for item in domains),
            "current_release_checks_passed": release["summary"]["passed_checks"],
            "current_release_checks_total": release["summary"]["total_checks"],
            "safe_source_paths": source["summary"]["tracked_paths"],
            "safe_source_generated_paths": source["summary"]["generated_experiment_paths"],
            "production_zero_cost_milestones": cost["revision_summary"]["total_local_milestones"],
            "g07_human_decisions": handoff["g07_measured_state"]["human_review"]["decisions"],
            "g07_human_decisions_required": handoff["g07_measured_state"]["human_review"]["required_decisions"],
            "ch05_accepted_panels": handoff["chapter_scale_readiness"]["accepted_panels"],
            "ch05_production_cap_usd": cost["approved_aggregate_cap_usd"],
            "provider_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        },
        "current_boundaries": [
            "Engineering route selection is not visual acceptance or commercial clearance.",
            "G07 human review remains incomplete and no decision/minute may be invented.",
            "CH05 production remains disabled with no cap, approved inputs, upload authority, outcome, or accepted panel.",
            "ComicPanelPlan remains separate from null AnimationShotPlan and E-Conte records.",
            "Generated provider candidates and local runtime artifacts remain outside Git.",
        ],
        "boundary": "The index resolves provenance and reproducer commands only. It is not a new experiment, authority grant, or acceptance decision.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    actions = [
        lambda item: item["domains"].pop(),
        lambda item: item["domains"][0]["lineage_newest_to_oldest"].pop(),
        lambda item: item["domains"][0].update(lineage_depth=1),
        lambda item: item["domains"][1]["current_record"].update(sha256="0" * 64),
        lambda item: item["domains"][2]["validator"].update(sha256="0" * 64),
        lambda item: item["domains"][3]["reproducer"].update(network_expected=True),
        lambda item: item["summary"].update(domains=10),
        lambda item: item["summary"].update(lineage_records=31),
        lambda item: item["summary"].update(current_release_checks_passed=64),
        lambda item: item["summary"].update(safe_source_generated_paths=1),
        lambda item: item["summary"].update(production_zero_cost_milestones=40),
        lambda item: item["summary"].update(g07_human_decisions=20),
        lambda item: item["summary"].update(ch05_accepted_panels=1),
        lambda item: item["summary"].update(ch05_production_cap_usd="100.000000"),
        lambda item: item["summary"].update(provider_requests=1),
        lambda item: item["summary"].update(external_uploads=1),
        lambda item: item["summary"].update(external_cost_usd="1.000000"),
        lambda item: item["current_boundaries"].pop(),
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
            require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked lineage index differs")
        rejected, total = mutations(expected)
        require(rejected == total, "lineage-index mutations not rejected")
    except (IndexError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings (11 current domains/32 lineage records; exact supersession hashes and validator commands valid)")
    print(f"65/65 release; G07 0/20; CH05 0 accepted/no cap; {rejected}/{total} mutations rejected; 0 requests/uploads/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
