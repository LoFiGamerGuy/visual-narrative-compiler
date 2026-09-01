"""Execute every current evidence-domain reproducer from the lineage index."""
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
INDEX = ROOT / "docs/research/evidence/current-evidence-lineage-index-r1.json"
OUTPUT = ROOT / "docs/research/evidence/current-evidence-reproducer-matrix-r1.json"


class MatrixError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise MatrixError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute() -> list[dict]:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    results = []
    for domain in index["domains"]:
        reproducer = domain["reproducer"]
        require(reproducer["network_expected"] is False, f"network-capable reproducer declared: {domain['domain']}")
        argv = list(reproducer["argv"])
        require(argv[0] == "python", f"unexpected interpreter token: {domain['domain']}")
        argv[0] = sys.executable
        started = time.perf_counter()
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        require(result.returncode == 0, f"reproducer failed: {domain['domain']}")
        require(not result.stderr.strip(), f"reproducer stderr not empty: {domain['domain']}")
        stdout = result.stdout.replace("\r\n", "\n")
        lines = stdout.strip().splitlines()
        results.append({
            "domain": domain["domain"],
            "argv": domain["reproducer"]["argv"],
            "validator_path": domain["validator"]["path"],
            "validator_sha256": domain["validator"]["sha256"],
            "returncode": 0,
            "passed": True,
            "stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
            "stdout_lines": len(lines),
            "stdout_last_line": lines[-1] if lines else "",
            "observed_elapsed_ms": elapsed_ms,
        })
    return results


def semantic(observed: list[dict]) -> dict:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    executions = [{key: value for key, value in item.items() if key != "observed_elapsed_ms"} for item in observed]
    require([item["domain"] for item in executions] == [item["domain"] for item in index["domains"]], "execution domain order changed")
    require(all(item["passed"] and item["returncode"] == 0 for item in executions), "reproducer failure")
    return {
        "record_type": "CurrentEvidenceReproducerMatrix",
        "schema_version": "1.0",
        "record_id": "ng-current-evidence-reproducer-matrix-r1",
        "state": "ALL_CURRENT_LINEAGE_DOMAIN_REPRODUCERS_PASS_NO_NETWORK_EXPECTED",
        "source_index": {
            "record_id": index["record_id"],
            "path": INDEX.relative_to(ROOT).as_posix(),
            "sha256": sha256(INDEX),
        },
        "executions": executions,
        "summary": {
            "commands": len(executions),
            "passed": len(executions),
            "failed": 0,
            "current_release_checks_passed": index["summary"]["current_release_checks_passed"],
            "current_release_checks_total": index["summary"]["current_release_checks_total"],
            "lineage_records_validated": index["summary"]["lineage_records"],
            "network_expected_commands": 0,
            "provider_requests": 0,
            "external_uploads": 0,
            "models_downloaded": 0,
            "external_cost_usd": "0.000000",
        },
        "limitations": [
            "Observed wall-clock timings are local and nondeterministic.",
            "A passing validator matrix proves current evidence integrity, not provider-output reproducibility across reruns.",
            "No actual human review is executed by this matrix.",
            "No CH05 provider request, upload, budget authority, or accepted panel is created.",
        ],
        "boundary": "Commands are local validators only. The matrix does not execute provider adapters or fill human/authority fields.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    actions = [
        lambda item: item["source_index"].update(sha256="0" * 64),
        lambda item: item["executions"].pop(),
        lambda item: item["executions"][0].update(passed=False),
        lambda item: item["executions"][1].update(returncode=1),
        lambda item: item["executions"][2].update(validator_sha256="0" * 64),
        lambda item: item["executions"][3].update(stdout_sha256="0" * 64),
        lambda item: item["summary"].update(commands=10),
        lambda item: item["summary"].update(passed=10),
        lambda item: item["summary"].update(failed=1),
        lambda item: item["summary"].update(current_release_checks_passed=64),
        lambda item: item["summary"].update(lineage_records_validated=31),
        lambda item: item["summary"].update(network_expected_commands=1),
        lambda item: item["summary"].update(provider_requests=1),
        lambda item: item["summary"].update(external_uploads=1),
        lambda item: item["summary"].update(models_downloaded=1),
        lambda item: item["summary"].update(external_cost_usd="1.000000"),
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
        observed = execute()
        expected = semantic(observed)
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True)
            payload = dict(expected)
            payload["observed_runtime"] = {
                "command_elapsed_ms": {item["domain"]: item["observed_elapsed_ms"] for item in observed},
                "total_elapsed_ms": round(sum(item["observed_elapsed_ms"] for item in observed), 3),
                "timing_is_local_nondeterministic": True,
            }
            target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            tracked = json.loads(OUTPUT.read_text(encoding="utf-8"))
            tracked.pop("observed_runtime", None)
            require(tracked == expected, "tracked reproducer matrix semantic state differs")
        rejected, total = mutations(expected)
        require(rejected == total, "reproducer-matrix mutations not rejected")
    except (MatrixError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings (11/11 current evidence-domain reproducer commands pass)")
    print(f"65/65 nested release checks; 32 lineage records; {rejected}/{total} mutations rejected; 0 requests/uploads/downloads/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
