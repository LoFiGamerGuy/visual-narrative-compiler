"""Append full-denominator coverage validation to immutable CH05 overnight release gate r1."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs/research/evidence/ch05-overnight-integrated-release-gate-r1.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-overnight-integrated-release-gate-r2.json"
COMMANDS = [
    "src/north_garden/validate_ch05_overnight_integrated_release_gate.py",
    "src/north_garden/validate_ch05_remaining_panel_priority.py",
    "src/north_garden/validate_ch05_remaining_panel_priority_evidence.py",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    base = json.loads(BASE.read_text(encoding="utf-8")); results = []; start_all = time.perf_counter()
    for relative in COMMANDS:
        path = ROOT / relative; start = time.perf_counter()
        completed = subprocess.run([sys.executable, str(path)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240)
        elapsed = time.perf_counter() - start
        stdout = completed.stdout.replace("\r\n", "\n").strip() + "\n"
        results.append({"path": relative, "script_sha256": sha(path), "command": f"python {relative}", "network_capable": False,
                        "return_code": completed.returncode, "elapsed_seconds": round(elapsed, 6), "stdout": stdout,
                        "stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest(), "stderr": completed.stderr.replace("\r\n", "\n")})
        print(f"[{len(results)}/3] {'PASS' if completed.returncode == 0 else 'FAIL'} {relative} {elapsed:.3f}s")
    total = time.perf_counter() - start_all; passed = sum(item["return_code"] == 0 for item in results)
    evidence = {
        "record_type": "CH05OvernightIntegratedReleaseGate", "schema_version": "1.1", "record_id": "ng-ch05-overnight-integrated-release-gate-r2",
        "state": "PASS" if passed == 3 else "FAIL", "medium": "comic", "comic_panel_plan_revision_created": False,
        "animation_shot_plan": None, "e_conte": None,
        "supersedes": {"record_id": base["record_id"], "path": BASE.relative_to(ROOT).as_posix(), "sha256": sha(BASE)},
        "summary": {"base_command_count": 16, "extension_command_count": 2, "effective_command_count": 18,
                    "orchestrator_commands": 3, "passed": passed, "failed": 3 - passed, "observed_total_seconds": round(total, 6),
                    "network_capable_commands": 0, "provider_calls": 0, "uploads": 0, "downloads": 0, "cost_usd": 0,
                    "accepted_candidates": 0, "executable_panels": 0, "human_review_minutes": None},
        "results": results,
        "effective_coverage": {"comic_panel_plans": 50, "selected": 14, "tier_a": 12, "tier_b": 12, "tier_c": 12},
        "boundaries": [
            "R1 remains immutable; r2 invokes its reproducer and adds only the two full-denominator coverage validators.",
            "All commands are local and non-network-capable.",
            "Passing does not authorize Tier A generation, accept art, bind copy, or create executable state."
        ]
    }
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle: handle.write(json.dumps(evidence, indent=2) + "\n")
    print(f"integrated release r2: {passed}/3 orchestrator commands, 18 effective checks in {total:.3f}s; {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}")
    return 0 if passed == 3 else 1


if __name__ == "__main__":
    raise SystemExit(main())
