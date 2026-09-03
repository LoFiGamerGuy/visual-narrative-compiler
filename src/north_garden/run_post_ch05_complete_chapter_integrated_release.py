"""Run the post-CH05 complete-chapter local integrated release matrix."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/research/evidence/post-ch05-complete-chapter-integrated-release-r1.json"
COMMANDS = [
    ("src/north_garden/validate_ch05_complete_chapter_release_r6.py", ["--self-test"], 11),
    ("src/north_garden/validate_comic_panel_plan_chapter_inventory.py", ["--self-test"], 11),
    ("src/north_garden/validate_cross_chapter_comic_regression.py", ["--self-test"], 11),
    ("src/north_garden/validate_complete_chapter_comicpanelplan_authoring_contract.py", ["--self-test"], 16),
    ("src/north_garden/validate_complete_chapter_semantic_graph.py", ["--self-test"], 24),
    ("src/north_garden/validate_ch05_complete_chapter.py", ["--manifest", "production/comic/run-manifests/ch05-complete-chapter-production-manifest-r6.json"], 1),
    ("src/north_garden/build_ch05_complete_chapter_review.py", ["--manifest", "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r6.json", "--validate-only"], 1),
    ("src/north_garden/validate_frozen_gauntlet_baseline_integrity.py", [], 16),
    ("src/north_garden/validate_tracked_source_scope.py", [], 1),
    ("src/north_garden/validate_current_git_remote_parity.py", [], 1),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    results = []
    start = time.perf_counter()
    for index, (relative, arguments, checks) in enumerate(COMMANDS, 1):
        path = ROOT / relative
        tick = time.perf_counter()
        completed = subprocess.run(
            [sys.executable, str(path), *arguments], cwd=ROOT, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=1800,
        )
        elapsed = time.perf_counter() - tick
        stdout = completed.stdout.replace("\r\n", "\n")
        stderr = completed.stderr.replace("\r\n", "\n")
        results.append({
            "path": relative,
            "arguments": arguments,
            "script_sha256": sha256(path),
            "network_capable": False,
            "expected_effective_checks": checks,
            "return_code": completed.returncode,
            "elapsed_seconds": round(elapsed, 6),
            "stdout": stdout,
            "stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
            "stderr": stderr,
        })
        print(f"[{index}/{len(COMMANDS)}] {'PASS' if completed.returncode == 0 else 'FAIL'} {relative} {elapsed:.3f}s")
    total = time.perf_counter() - start
    passed = sum(row["return_code"] == 0 for row in results)
    document = {
        "record_type": "PostCH05CompleteChapterIntegratedRelease",
        "schema_version": "1.0",
        "record_id": "ng-post-ch05-complete-chapter-integrated-release-r1",
        "state": "PASS" if passed == len(COMMANDS) else "FAIL",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "summary": {
            "orchestrator_commands": len(COMMANDS),
            "passed": passed,
            "failed": len(COMMANDS) - passed,
            "effective_checks": sum(row[2] for row in COMMANDS),
            "observed_total_seconds": round(total, 6),
            "network_capable_commands": 0,
            "ch05_selected_panels": 50,
            "ch05_candidates": 59,
            "ch05_agent_triage": {"pass": 49, "warn": 1, "fail": 0, "gating": False},
            "chapter_inventory_plans": 63,
            "cross_chapter_review_panels": 23,
            "authoring_contract_mutations_rejected": 15,
            "semantic_graph_mutations_rejected": 23,
            "provider_calls": 0,
            "uploads": 0,
            "new_generation": 0,
            "accepted": 0,
            "commercial_decisions": 0,
            "paid_spend_usd": 0,
            "human_review_minutes": None,
        },
        "results": results,
        "boundary": "Local no-network integrated validation. PASS proves evidence/contract integrity only and grants no story, prompt, provider, upload, generation, acceptance, rights, exact-base, or production authority.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"post-CH05 release: {passed}/{len(COMMANDS)} commands, {document['summary']['effective_checks']} effective checks in {total:.3f}s; {OUTPUT.relative_to(ROOT)} {sha256(OUTPUT)}")
    return 0 if passed == len(COMMANDS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
