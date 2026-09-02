"""Run append-only integrated release r6 over post-r5 CH05 evidence."""
from __future__ import annotations

import hashlib, json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs/research/evidence/ch05-overnight-integrated-release-gate-r5.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-overnight-integrated-release-gate-r6.json"
COMMANDS = [
    "src/north_garden/validate_ch05_overnight_integrated_release_gate_r5.py",
    "src/north_garden/validate_ch05_chapter_production_readiness_matrix.py",
    "src/north_garden/validate_ch05_reference_use_and_continuity_risk_plan.py",
    "src/north_garden/validate_ch05_human_review_time_instrumentation_contract.py",
    "src/north_garden/validate_ch05_owner_handoff_dependency_checklist.py",
]


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    base = json.loads(BASE.read_text(encoding="utf-8")); results = []; started_all = time.perf_counter()
    for index, relative in enumerate(COMMANDS, 1):
        path = ROOT / relative; started = time.perf_counter()
        done = subprocess.run([sys.executable, str(path)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        elapsed = time.perf_counter() - started; stdout = done.stdout.replace("\r\n", "\n").strip() + "\n"
        results.append({"path": relative, "script_sha256": sha(path), "command": f"python {relative}", "network_capable": False, "return_code": done.returncode, "elapsed_seconds": round(elapsed, 6), "stdout": stdout, "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(), "stderr": done.stderr.replace("\r\n", "\n")})
        print(f"[{index}/{len(COMMANDS)}] {'PASS' if done.returncode == 0 else 'FAIL'} {relative} {elapsed:.3f}s")
    total = time.perf_counter() - started_all; passed = sum(item["return_code"] == 0 for item in results)
    evidence = {"record_type": "CH05OvernightIntegratedReleaseGate", "schema_version": "1.5", "record_id": "ng-ch05-overnight-integrated-release-gate-r6", "state": "PASS" if passed == len(COMMANDS) else "FAIL", "medium": "comic", "comic_panel_plan_revision_created": False, "animation_shot_plan": None, "e_conte": None, "supersedes": {"record_id": base["record_id"], "path": BASE.relative_to(ROOT).as_posix(), "sha256": sha(BASE)}, "summary": {"base_effective_command_count": 38, "extension_command_count": 4, "effective_command_count": 42, "orchestrator_commands": len(COMMANDS), "passed": passed, "failed": len(COMMANDS) - passed, "observed_total_seconds": round(total, 6), "network_capable_commands": 0, "provider_calls": 0, "uploads": 0, "downloads": 0, "cost_usd": 0, "accepted_candidates": 0, "executable_panels": 0, "owner_decisions": 0, "live_review_events": 0, "human_review_minutes": None}, "results": results, "effective_state": {"candidates": 29, "review_artifacts": 99, "comic_panel_plans": 50, "readiness_selected": 14, "readiness_dry_run": 4, "readiness_tier_a": 8, "readiness_backlog": 24, "reference_hypotheses": 42, "text_only_plans": 18, "critical_reference_guards": 1, "owner_tasks": 24, "owner_task_stages": [19, 4, 1], "timer_subjects": 39, "next_prompts": 0, "frozen_paths": 16, "baseline_paths": 4}, "boundaries": ["R5 remains immutable; r6 preserves its 38 effective checks and adds readiness, reference-risk, live-timer, and dependency-handoff validators.", "All commands are local and non-network-capable.", "Passing does not ingest review, compile prompts, upload references, infer identity, accept art, revise plans, or grant commercial clearance."]}
    OUTPUT.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"integrated release r6: {passed}/{len(COMMANDS)} orchestrator commands, 42 effective checks in {total:.3f}s; {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}")
    return 0 if passed == len(COMMANDS) else 1


if __name__ == "__main__": raise SystemExit(main())
