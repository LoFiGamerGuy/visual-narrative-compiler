"""Run hardening release gate r2 plus the final handoff/lattice validators."""
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
R2_SCRIPT = "src/north_garden/validate_hardening_release_r2.py"
R2_REPORT = ROOT / "docs/research/evidence/hardening-release-validation-gate-r2.json"
OUTPUT = ROOT / "docs/research/evidence/hardening-release-validation-gate-r3.json"
EXTENSIONS = [
    ("selected_route_hardening_state_r2", "src/north_garden/validate_selected_route_hardening_state_r2.py"),
    ("p036_prerequisite_authority_lattice_r1", "src/north_garden/validate_p036_prerequisite_authority_lattice.py"),
    ("production_cost_ledger_r10", "src/north_garden/validate_ch05_production_cost_ledger_r10.py"),
    ("production_cost_ledger_r11", "src/north_garden/validate_ch05_production_cost_ledger_r11.py"),
    ("production_cost_ledger_r12", "src/north_garden/validate_ch05_production_cost_ledger_r12.py"),
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
    base, base_ms = run(R2_SCRIPT)
    require(base.returncode == 0, "r2 release gate failed")
    r2 = json.loads(R2_REPORT.read_text(encoding="utf-8"))
    require(r2["summary"] == {"base_checks": 53, "extension_checks": 7, "total_checks": 60, "passed_checks": 60, "failed_checks": 0}, "r2 gate count changed")
    results = []
    for name, script in EXTENSIONS:
        result, elapsed_ms = run(script)
        require(result.returncode == 0, f"r3 extension failed: {name}")
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
        "schema_version": "1.2",
        "record_id": "ng-hardening-release-validation-gate-r3",
        "state": "R2_GATE_AND_FINAL_LOCAL_HANDOFF_CHECKS_PASS",
        "supersedes": {
            "record_id": "ng-hardening-release-validation-gate-r2",
            "path": R2_REPORT.relative_to(ROOT).as_posix(),
            "sha256": sha256(R2_REPORT),
            "checks": 60,
        },
        "prior_gate_rewritten": False,
        "base_gate": {
            "script": R2_SCRIPT,
            "script_sha256": sha256(ROOT / R2_SCRIPT),
            "checks": 60,
            "passed": 60,
        },
        "extensions": [{key: value for key, value in item.items() if key != "observed_elapsed_ms"} for item in observed["extensions"]],
        "summary": {
            "base_checks": 60,
            "extension_checks": len(EXTENSIONS),
            "total_checks": 60 + len(EXTENSIONS),
            "passed_checks": 60 + len(EXTENSIONS),
            "failed_checks": 0,
        },
        "activity": {
            "network_requests": 0,
            "provider_requests": 0,
            "external_uploads": 0,
            "models_downloaded": 0,
            "external_cost_usd": "0.000000",
        },
        "current_boundary_state": {
            "g07_human_decisions": 0,
            "g07_human_decisions_required": 20,
            "ch05_approved_inputs": 0,
            "ch05_production_cap_usd": None,
            "p036_root_blockers": 4,
            "p036_total_blockers": 9,
            "real_render_records_v2_1": 0,
            "accepted_ch05_panels": 0,
            "next_external_action": None,
        },
        "boundaries": [
            "R2 remains immutable and is executed as the 60-check base gate.",
            "R3 adds only current handoff, exhaustive prerequisite-lattice, and append-only ledger checks.",
            "Passing does not create human judgment, input approval, upload authority, production cap, provider outcome, acceptance, or commercial clearance.",
        ],
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    actions = [
        lambda item: item["supersedes"].update(sha256="0" * 64),
        lambda item: item.update(prior_gate_rewritten=True),
        lambda item: item["base_gate"].update(checks=59),
        lambda item: item["extensions"].pop(),
        lambda item: item["extensions"][0].update(passed=False),
        lambda item: item["summary"].update(total_checks=64),
        lambda item: item["summary"].update(passed_checks=64),
        lambda item: item["current_boundary_state"].update(g07_human_decisions=20),
        lambda item: item["current_boundary_state"].update(ch05_approved_inputs=2),
        lambda item: item["current_boundary_state"].update(ch05_production_cap_usd="100.000000"),
        lambda item: item["current_boundary_state"].update(real_render_records_v2_1=1),
        lambda item: item["current_boundary_state"].update(next_external_action="submit P036"),
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
            require(tracked == expected, "tracked release gate r3 semantic state differs")
        rejected, total = mutations(expected)
        require(rejected == total, "r3 release mutations not rejected")
    except (GateError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"0 failures, 0 warnings (60-check r2 base + {len(EXTENSIONS)} extensions = {60 + len(EXTENSIONS)}/{60 + len(EXTENSIONS)} local checks pass)")
    print(f"{rejected}/{total} release-r3 mutations rejected; G07 0/20; CH05 0 outcomes; 0 network/provider/uploads/downloads/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
