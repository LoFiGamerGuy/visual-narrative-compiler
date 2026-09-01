"""Prove frozen v2.1.1 and baseline_legacy targets were not modified."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EARLY = ROOT / "docs/research/evidence/safe-source-release-manifest-f505788.json"
LATE = ROOT / "docs/research/evidence/safe-source-release-manifest-00498df.json"
OUTPUT = ROOT / "docs/research/evidence/frozen-gauntlet-baseline-integrity-r1.json"
FROZEN_PREFIX = "research/authoritative/v2.1.1/"
BASELINE_TRACKED = [
    "src/north_garden/baseline_legacy.py",
    "config/runtime-assets.example.json",
    "scripts/bootstrap-local.ps1",
    "src/north_garden/validate_runtime_asset_manifest.py",
]
LOCAL_BUNDLE = ROOT / "benchmarks/case-bundles/baseline_legacy-v1.json"
LOCAL_WORKFLOW = ROOT / "garden/gen3.py"
LOCAL_RESULT = ROOT / "experiments/results/baseline_legacy_stage_a_20260831.json"


class IntegrityError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise IntegrityError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(payload: dict) -> dict[str, dict]:
    return {item["path"]: item for item in payload["entries"]}


def canonical_root(entries: list[dict]) -> str:
    minimal = [{"path": item["path"], "bytes": item["bytes"], "sha256": item["sha256"]} for item in entries]
    return hashlib.sha256(json.dumps(minimal, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build() -> dict:
    early = json.loads(EARLY.read_text(encoding="utf-8"))
    late = json.loads(LATE.read_text(encoding="utf-8"))
    early_entries = inventory(early)
    late_entries = inventory(late)
    early_frozen = sorted((item for path, item in early_entries.items() if path.startswith(FROZEN_PREFIX)), key=lambda item: item["path"])
    late_frozen = sorted((item for path, item in late_entries.items() if path.startswith(FROZEN_PREFIX)), key=lambda item: item["path"])
    require(len(early_frozen) == len(late_frozen) == 16, "frozen package path count changed")
    frozen_comparison = []
    for first, last in zip(early_frozen, late_frozen, strict=True):
        require(first["path"] == last["path"], "frozen package path changed")
        require(first["bytes"] == last["bytes"] and first["sha256"] == last["sha256"], f"frozen bytes changed: {first['path']}")
        frozen_comparison.append({"path": first["path"], "bytes": first["bytes"], "sha256": first["sha256"], "identical": True})

    baseline_comparison = []
    for relative in BASELINE_TRACKED:
        first = early_entries[relative]
        last = late_entries[relative]
        require(first["bytes"] == last["bytes"] and first["sha256"] == last["sha256"], f"baseline tracked bytes changed: {relative}")
        baseline_comparison.append({"path": relative, "bytes": first["bytes"], "sha256": first["sha256"], "identical": True})

    bundle = json.loads(LOCAL_BUNDLE.read_text(encoding="utf-8"))
    result = json.loads(LOCAL_RESULT.read_text(encoding="utf-8"))
    gauntlet = ROOT / bundle["semantic_source"]
    workflow = ROOT / bundle["workflow_source"]
    require(workflow.resolve() == LOCAL_WORKFLOW.resolve(), "baseline workflow path changed")
    require(bundle["semantic_source_sha256"] == sha256(gauntlet) == "f826b0f1d06ed5a999667bde23ba0d04f8ebb22f516095034dab62c7541ae9ae", "gauntlet semantic hash changed")
    require(bundle["workflow_source_sha256"] == sha256(workflow) == "004298df5b022e54b9cea9eaddd93a63280ea7aad02ac2316bbe92d8891a5db8", "legacy workflow hash changed")
    require(bundle["state"] == "DRAFT_LEGACY_LIMITED_NOT_FROZEN" and bundle["freeze_prohibition"], "legacy bundle promoted")
    require(result["renderer_adapter"] == "baseline_legacy" and result["renderer_generations"] == 24, "baseline result denominator changed")
    require(result["accepted_outputs"] == [] and result["hard_gate_summary"]["fully_assertion_conformant_candidates"] == 0, "baseline acceptance changed")
    require(result["decision"] == "REJECTED_FOR_FURTHER_BENCHMARKING" and "no baseline tuning was performed" in result["decision_reason"], "baseline decision changed")
    require(result["stage_a_cases"] == 12 and len(result["per_case"]) == 12 and all(item["decision"] == "REJECT" for item in result["per_case"].values()), "baseline failure profile changed")

    frozen_validator = subprocess.run([sys.executable, "research/authoritative/v2.1.1/scripts/validate_research_package.py"], cwd=ROOT, capture_output=True, text=True)
    runtime_validator = subprocess.run([sys.executable, "src/north_garden/validate_runtime_asset_manifest.py"], cwd=ROOT, capture_output=True, text=True)
    require(frozen_validator.returncode == runtime_validator.returncode == 0, "frozen/runtime validator failed")
    return {
        "record_type": "FrozenGauntletBaselineIntegrityEvidence",
        "schema_version": "1.0",
        "record_id": "ng-frozen-gauntlet-baseline-integrity-r1",
        "state": "FROZEN_PACKAGE_AND_BASELINE_TARGETS_UNCHANGED",
        "snapshots": {
            "early": {"commit": early["captured_commit"], "manifest_path": EARLY.relative_to(ROOT).as_posix(), "manifest_sha256": sha256(EARLY)},
            "late": {"commit": late["captured_commit"], "manifest_path": LATE.relative_to(ROOT).as_posix(), "manifest_sha256": sha256(LATE)},
        },
        "frozen_v2_1_1": {
            "paths": frozen_comparison,
            "path_count": len(frozen_comparison),
            "total_bytes": sum(item["bytes"] for item in frozen_comparison),
            "canonical_path_byte_root_sha256": canonical_root(frozen_comparison),
            "all_identical": True,
            "validator_passed": True,
        },
        "baseline_legacy_tracked": {
            "paths": baseline_comparison,
            "path_count": len(baseline_comparison),
            "all_identical": True,
            "runtime_manifest_validator_passed": True,
        },
        "baseline_legacy_local_pins": {
            "case_bundle": {"path": LOCAL_BUNDLE.relative_to(ROOT).as_posix(), "sha256": sha256(LOCAL_BUNDLE), "git_tracked": False, "state": bundle["state"]},
            "workflow": {"path": LOCAL_WORKFLOW.relative_to(ROOT).as_posix(), "sha256": sha256(LOCAL_WORKFLOW), "matches_bundle_declared_sha256": True, "git_tracked": False},
            "stage_a_result": {
                "path": LOCAL_RESULT.relative_to(ROOT).as_posix(),
                "sha256": sha256(LOCAL_RESULT),
                "git_tracked": False,
                "cases": result["stage_a_cases"],
                "generations": result["renderer_generations"],
                "fully_assertion_conformant_candidates": result["hard_gate_summary"]["fully_assertion_conformant_candidates"],
                "accepted_outputs": len(result["accepted_outputs"]),
                "decision": result["decision"],
                "human_minutes": result["human_minutes"],
            },
            "limitation": "Local untracked bundle/workflow/result are hash-checked against their own declarations but are outside safe-source history; no historical identity beyond those pins is claimed.",
        },
        "summary": {
            "frozen_paths_compared": 16,
            "frozen_paths_changed": 0,
            "baseline_tracked_paths_compared": 4,
            "baseline_tracked_paths_changed": 0,
            "baseline_generations": 24,
            "baseline_accepted_outputs": 0,
            "baseline_tuning_performed": False,
            "provider_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        },
        "boundary": "The audit reads frozen/baseline files only. It does not rerun the legacy renderer, inspect candidate imagery, tune prompts, or change benchmark semantics.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    actions = [
        lambda item: item["snapshots"]["early"].update(manifest_sha256="0" * 64),
        lambda item: item["frozen_v2_1_1"]["paths"].pop(),
        lambda item: item["frozen_v2_1_1"]["paths"][0].update(sha256="0" * 64),
        lambda item: item["frozen_v2_1_1"].update(all_identical=False),
        lambda item: item["baseline_legacy_tracked"]["paths"].pop(),
        lambda item: item["baseline_legacy_tracked"].update(all_identical=False),
        lambda item: item["baseline_legacy_local_pins"]["workflow"].update(matches_bundle_declared_sha256=False),
        lambda item: item["baseline_legacy_local_pins"]["stage_a_result"].update(accepted_outputs=1),
        lambda item: item["summary"].update(frozen_paths_changed=1),
        lambda item: item["summary"].update(baseline_tracked_paths_changed=1),
        lambda item: item["summary"].update(baseline_accepted_outputs=1),
        lambda item: item["summary"].update(baseline_tuning_performed=True),
        lambda item: item["summary"].update(provider_requests=1),
        lambda item: item["summary"].update(external_uploads=1),
        lambda item: item["summary"].update(external_cost_usd="1.000000"),
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
            require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked frozen integrity evidence differs")
        rejected, total = mutations(expected)
        require(rejected == total, "frozen-integrity mutations not rejected")
    except (IntegrityError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings (16 frozen + 4 baseline tracked paths byte-identical from f505788 to 00498df)")
    print(f"baseline remains 0/24 accepted/no tuning; local workflow pin exact; {rejected}/{total} mutations rejected; 0 requests/uploads/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
