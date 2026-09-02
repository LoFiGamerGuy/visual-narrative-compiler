"""Run append-only integrated release r4 over post-r3 CH05 evidence."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs/research/evidence/ch05-overnight-integrated-release-gate-r3.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-overnight-integrated-release-gate-r4.json"
COMMANDS = [
    "src/north_garden/validate_ch05_overnight_integrated_release_gate_r3.py",
    "src/north_garden/validate_ch05_chapter_scale_production_envelope.py",
    "src/north_garden/validate_future_litrpg_concept_timing_reconciliation.py",
    "src/north_garden/validate_ch05_renderrecord_completeness_audit.py",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    base = json.loads(BASE.read_text(encoding="utf-8"))
    results = []
    started_all = time.perf_counter()
    for index, relative in enumerate(COMMANDS, 1):
        path = ROOT / relative
        started = time.perf_counter()
        done = subprocess.run(
            [sys.executable, str(path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
        elapsed = time.perf_counter() - started
        stdout = done.stdout.replace("\r\n", "\n").strip() + "\n"
        results.append(
            {
                "path": relative,
                "script_sha256": sha(path),
                "command": f"python {relative}",
                "network_capable": False,
                "return_code": done.returncode,
                "elapsed_seconds": round(elapsed, 6),
                "stdout": stdout,
                "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
                "stderr": done.stderr.replace("\r\n", "\n"),
            }
        )
        print(f"[{index}/{len(COMMANDS)}] {'PASS' if done.returncode == 0 else 'FAIL'} {relative} {elapsed:.3f}s")
    total = time.perf_counter() - started_all
    passed = sum(item["return_code"] == 0 for item in results)
    evidence = {
        "record_type": "CH05OvernightIntegratedReleaseGate",
        "schema_version": "1.3",
        "record_id": "ng-ch05-overnight-integrated-release-gate-r4",
        "state": "PASS" if passed == len(COMMANDS) else "FAIL",
        "medium": "comic",
        "comic_panel_plan_revision_created": False,
        "animation_shot_plan": None,
        "e_conte": None,
        "supersedes": {
            "record_id": base["record_id"],
            "path": BASE.relative_to(ROOT).as_posix(),
            "sha256": sha(BASE),
        },
        "summary": {
            "base_effective_command_count": 30,
            "extension_command_count": 3,
            "effective_command_count": 33,
            "orchestrator_commands": len(COMMANDS),
            "passed": passed,
            "failed": len(COMMANDS) - passed,
            "observed_total_seconds": round(total, 6),
            "network_capable_commands": 0,
            "provider_calls": 0,
            "uploads": 0,
            "downloads": 0,
            "cost_usd": 0,
            "accepted_candidates": 0,
            "executable_panels": 0,
            "owner_decisions": 0,
            "human_review_minutes": None,
        },
        "results": results,
        "effective_state": {
            "candidates": 29,
            "renderrecords": 29,
            "reference_uses": 39,
            "observed_generation_seconds": 1385.036,
            "ch05_candidates": 26,
            "noncanon_concepts": 3,
            "selected": 14,
            "comic_panel_plans": 50,
            "remaining_plans": 36,
            "chapter_scenarios": [36, 49, 72],
            "pending_decision_subjects": 39,
            "completed_decisions": 0,
            "frozen_paths": 16,
            "baseline_paths": 4,
        },
        "boundaries": [
            "R3 remains immutable; r4 preserves its 30 effective checks and adds the chapter envelope, timing reconciliation, and all-29 RenderRecord audit.",
            "All commands are local and non-network-capable.",
            "Passing does not accept art, infer unavailable service metadata, authorize prompts/uploads, revise ComicPanelPlans, or grant commercial clearance.",
        ],
    }
    OUTPUT.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(
        f"integrated release r4: {passed}/{len(COMMANDS)} orchestrator commands, "
        f"33 effective checks in {total:.3f}s; {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}"
    )
    return 0 if passed == len(COMMANDS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
