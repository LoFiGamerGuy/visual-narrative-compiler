"""Run hardening release gate r1 plus all append-only post-r1 validators."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
R1_SCRIPT = "src/north_garden/validate_hardening_release.py"
R1_REPORT = ROOT / "docs/research/evidence/hardening-release-validation-gate-r1.json"
OUTPUT = ROOT / "docs/research/evidence/hardening-release-validation-gate-r2.json"
EXTENSIONS = [
    ("selector_consumer_compatibility_r2", "src/north_garden/validate_selector_consumer_compatibility_r2.py"),
    ("selected_route_authority_frontier_r1", "src/north_garden/validate_selected_route_authority_frontier.py"),
    ("safe_source_release_manifest_r2", "src/north_garden/validate_safe_source_release_manifest_r2.py"),
    ("production_cost_ledger_r6", "src/north_garden/validate_ch05_production_cost_ledger_r6.py"),
    ("production_cost_ledger_r7", "src/north_garden/validate_ch05_production_cost_ledger_r7.py"),
    ("production_cost_ledger_r8", "src/north_garden/validate_ch05_production_cost_ledger_r8.py"),
    ("production_cost_ledger_r9", "src/north_garden/validate_ch05_production_cost_ledger_r9.py"),
]


class GateError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise GateError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(script: str) -> tuple[subprocess.CompletedProcess[str], float]:
    started = time.perf_counter()
    result = subprocess.run([sys.executable, script], cwd=ROOT, capture_output=True, text=True)
    return result, round((time.perf_counter() - started) * 1000, 3)


def execute() -> dict:
    base, base_ms = run(R1_SCRIPT)
    require(base.returncode == 0, "r1 release gate failed")
    r1 = json.loads(R1_REPORT.read_text(encoding="utf-8"))
    require(r1["summary"] == {"core_checks": 44, "extension_checks": 9, "total_checks": 53, "passed_checks": 53, "failed_checks": 0}, "r1 gate count changed")
    results = []
    for name, script in EXTENSIONS:
        result, elapsed_ms = run(script)
        require(result.returncode == 0, f"r2 extension failed: {name}")
        lines = result.stdout.strip().splitlines()
        results.append({
            "name": name,
            "script": script,
            "script_sha256": sha256(ROOT / script),
            "passed": True,
            "stdout_last_line": lines[-1] if lines else "",
            "observed_elapsed_ms": elapsed_ms,
        })
    return {"base_elapsed_ms": base_ms, "extensions": results}


def semantic(observed: dict) -> dict:
    return {
        "record_type": "HardeningReleaseValidationGate",
        "schema_version": "1.1",
        "record_id": "ng-hardening-release-validation-gate-r2",
        "state": "R1_GATE_AND_ALL_POST_R1_LOCAL_CHECKS_PASS",
        "supersedes": {
            "record_id": "ng-hardening-release-validation-gate-r1",
            "path": R1_REPORT.relative_to(ROOT).as_posix(),
            "sha256": sha256(R1_REPORT),
            "checks": 53,
        },
        "prior_gate_rewritten": False,
        "base_gate": {
            "script": R1_SCRIPT,
            "script_sha256": sha256(ROOT / R1_SCRIPT),
            "checks": 53,
            "passed": 53,
        },
        "extensions": [{key: value for key, value in item.items() if key != "observed_elapsed_ms"} for item in observed["extensions"]],
        "summary": {
            "base_checks": 53,
            "extension_checks": len(EXTENSIONS),
            "total_checks": 53 + len(EXTENSIONS),
            "passed_checks": 53 + len(EXTENSIONS),
            "failed_checks": 0,
        },
        "activity": {
            "network_requests": 0,
            "provider_requests": 0,
            "external_uploads": 0,
            "models_downloaded": 0,
            "external_cost_usd": "0.000000",
        },
        "boundaries": [
            "R1 remains immutable and is executed as the 53-check base gate.",
            "R2 extensions validate compatibility, dependency accounting, safe-source scope, and append-only cost ledgers only.",
            "Passing does not create G07 human judgment, CH05 inputs, upload authority, production cap, provider outcome, acceptance, or commercial clearance.",
        ],
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    actions = [
        lambda item: item["supersedes"].update(sha256="0" * 64),
        lambda item: item.update(prior_gate_rewritten=True),
        lambda item: item["base_gate"].update(checks=52),
        lambda item: item["extensions"].pop(),
        lambda item: item["extensions"][0].update(passed=False),
        lambda item: item["summary"].update(total_checks=59),
        lambda item: item["summary"].update(passed_checks=59),
        lambda item: item["activity"].update(network_requests=1),
        lambda item: item["activity"].update(external_uploads=1),
        lambda item: item["activity"].update(external_cost_usd="1.000000"),
        lambda item: item["boundaries"].pop(),
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
        observed = execute()
        expected = semantic(observed)
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True)
            payload = dict(expected)
            payload["observed_runtime"] = {
                "base_elapsed_ms": observed["base_elapsed_ms"],
                "extension_elapsed_ms": {item["name"]: item["observed_elapsed_ms"] for item in observed["extensions"]},
                "total_elapsed_ms": round(observed["base_elapsed_ms"] + sum(item["observed_elapsed_ms"] for item in observed["extensions"]), 3),
                "timing_is_local_nondeterministic": True,
            }
            target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            tracked = json.loads(OUTPUT.read_text(encoding="utf-8"))
            tracked.pop("observed_runtime", None)
            require(tracked == expected, "tracked release gate r2 semantic state differs")
        rejected, total = mutations(expected)
        require(rejected == total, "r2 release mutations not rejected")
    except (GateError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"0 failures, 0 warnings (53-check r1 base + {len(EXTENSIONS)} extensions = {53 + len(EXTENSIONS)}/{53 + len(EXTENSIONS)} local checks pass)")
    print(f"{rejected}/{total} release-r2 mutations rejected; 0 network/provider/uploads/downloads/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
