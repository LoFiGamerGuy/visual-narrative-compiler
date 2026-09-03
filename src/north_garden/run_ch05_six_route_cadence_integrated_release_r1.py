"""Run the append-only CH05 six-route/cadence integrated release r1."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = (
    ROOT / "docs/research/evidence/ch05-six-route-cadence-integrated-release-r1.json"
)
VALIDATOR = (
    ROOT / "src/north_garden/validate_ch05_six_route_cadence_integrated_release_r1.py"
)
EXPECTED_HEAD = "97e0591b02209310a2ff94d3bc1ee336ce51ae06"
EXPECTED_ORIGIN = "https://github.com/LoFiGamerGuy/visual-narrative-compiler"

COMMANDS: list[tuple[str, str, list[str], str | None]] = [
    (
        "reduced_prompt",
        "src/north_garden/validate_ch05_complete_chapter_reduced_palette_text_control_prompt_manifest.py",
        ["--self-test"],
        "32/32",
    ),
    (
        "reduced_execution",
        "src/north_garden/validate_ch05_complete_chapter_route_execution.py",
        [
            "--prompt-manifest",
            "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-prompt-manifest-r1.json",
            "--execution-manifest",
            "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-execution-manifest-r1.json",
            "--self-test",
        ],
        "32/32",
    ),
    (
        "reduced_crop",
        "src/north_garden/validate_ch05_complete_chapter_reduced_palette_text_control_crops.py",
        ["--self-test"],
        "14/14",
    ),
    (
        "reduced_triage",
        "src/north_garden/validate_ch05_reduced_palette_text_control_agent_triage.py",
        ["--self-test"],
        "22/22",
    ),
    (
        "matched_prompts",
        "src/north_garden/validate_ch05_matched_reference_ablation_prompts.py",
        ["--self-test"],
        "18/18",
    ),
    (
        "s01_ablation",
        "src/north_garden/validate_ch05_s01_reference_ablation_comparison.py",
        ["--self-test"],
        "22/22",
    ),
    (
        "s11_ablation",
        "src/north_garden/validate_ch05_s11_reference_ablation_comparison.py",
        ["--self-test"],
        "22/22",
    ),
    (
        "six_route",
        "src/north_garden/validate_ch05_six_route_comparison.py",
        ["--self-test"],
        "21/21",
    ),
    (
        "cadence_review",
        "src/north_garden/validate_ch05_sequence_cadence_review.py",
        ["--self-test"],
        "23/23",
    ),
    (
        "boundary_audit",
        "src/north_garden/validate_ch05_sequence_cadence_boundary_audit.py",
        ["--self-test"],
        "21/21",
    ),
    (
        "p005_p006_attribution",
        "src/north_garden/validate_ch05_p005_p006_route_attribution_control.py",
        ["--self-test"],
        "21/21",
    ),
    (
        "six_route_owner_handoff",
        "src/north_garden/validate_ch05_six_route_owner_review_handoff.py",
        ["--self-test"],
        "20/20",
    ),
    (
        "complete_chapter_review_handoff_r7",
        "src/north_garden/validate_ch05_complete_chapter_review_handoff_r7.py",
        ["--self-test"],
        "15/15",
    ),
    (
        "frozen_integrity",
        "src/north_garden/validate_frozen_gauntlet_baseline_integrity.py",
        [],
        "15/15",
    ),
    (
        "tracked_source_scope",
        "src/north_garden/validate_tracked_source_scope.py",
        [],
        None,
    ),
]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def clean_output(value: str) -> str:
    normalized = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    return normalized + "\n" if normalized else ""


def observed_self_test(stdout: str) -> str | None:
    json_match = re.search(r'"self_test":\s*"(\d+/\d+)"', stdout)
    if json_match:
        return json_match.group(1)
    plain_match = re.search(r"(\d+/\d+) mutations rejected", stdout)
    return plain_match.group(1) if plain_match else None


def run_local(
    result_id: str, relative: str, arguments: list[str], expected: str | None
) -> dict[str, Any]:
    path = ROOT / relative
    started = time.perf_counter()
    completed = subprocess.run(
        [sys.executable, str(path), *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=1800,
        check=False,
    )
    elapsed = time.perf_counter() - started
    stdout = clean_output(completed.stdout)
    stderr = clean_output(completed.stderr)
    observed = observed_self_test(stdout)
    passed = (
        completed.returncode == 0
        and not stderr
        and (expected is None or observed == expected)
        and ('"status": "PASS"' in stdout or "0 failures" in stdout)
    )
    return {
        "id": result_id,
        "kind": "local_python_validator",
        "path": relative,
        "arguments": arguments,
        "script_sha256": sha256(path),
        "network_access": "NONE",
        "return_code": completed.returncode,
        "elapsed_seconds": round(elapsed, 6),
        "stdout": stdout,
        "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
        "stderr": stderr,
        "stderr_sha256": sha256_bytes(stderr.encode("utf-8")),
        "expected_self_test": expected,
        "observed_self_test": observed,
        "passed": passed,
    }


def git(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )


def run_remote_parity() -> tuple[dict[str, Any], dict[str, Any]]:
    started = time.perf_counter()
    calls = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tracked_status": git("status", "--porcelain=v1", "--untracked-files=no"),
        "origin_url": git("remote", "get-url", "origin"),
        "remote_head": git("ls-remote", "--heads", "origin", "refs/heads/main"),
    }
    elapsed = time.perf_counter() - started
    branch = calls["branch"].stdout.strip()
    head = calls["head"].stdout.strip()
    tracked_status = calls["tracked_status"].stdout.strip()
    origin_url = calls["origin_url"].stdout.strip()
    remote_line = calls["remote_head"].stdout.strip()
    remote_head = remote_line.split()[0] if remote_line else ""
    normalized_origin = origin_url.removesuffix(".git")
    stderr = clean_output("".join(call.stderr for call in calls.values()))
    passed = (
        all(call.returncode == 0 for call in calls.values())
        and branch == "main"
        and head == EXPECTED_HEAD
        and remote_head == EXPECTED_HEAD
        and not tracked_status
        and normalized_origin == EXPECTED_ORIGIN
        and not stderr
    )
    git_state = {
        "branch": branch,
        "local_head": head,
        "remote_head": remote_head,
        "origin_url": origin_url,
        "tracked_worktree_clean": not tracked_status,
        "local_remote_parity": head == remote_head,
    }
    stdout = clean_output(
        "\n".join(
            [
                f"branch={branch}",
                f"local_head={head}",
                f"remote_head={remote_head}",
                f"origin_url={origin_url}",
                f"tracked_worktree_clean={str(not tracked_status).lower()}",
                f"local_remote_parity={str(head == remote_head).lower()}",
            ]
        )
    )
    result = {
        "id": "git_remote_parity",
        "kind": "read_only_git_remote_state",
        "path": None,
        "arguments": [
            "git branch --show-current",
            "git rev-parse HEAD",
            "git status --porcelain=v1 --untracked-files=no",
            "git remote get-url origin",
            "git ls-remote --heads origin refs/heads/main",
        ],
        "script_sha256": None,
        "network_access": "READ_ONLY_GIT_REMOTE_STATE",
        "return_code": 0 if passed else 1,
        "elapsed_seconds": round(elapsed, 6),
        "stdout": stdout,
        "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
        "stderr": stderr,
        "stderr_sha256": sha256_bytes(stderr.encode("utf-8")),
        "expected_self_test": None,
        "observed_self_test": None,
        "passed": passed,
    }
    return result, git_state


def main() -> int:
    if OUTPUT.exists():
        print(f"FAIL: append-only target already exists: {OUTPUT.relative_to(ROOT)}")
        return 2
    if not VALIDATOR.is_file():
        print(f"FAIL: companion validator missing: {VALIDATOR.relative_to(ROOT)}")
        return 2
    started = time.perf_counter()
    results = []
    for index, command in enumerate(COMMANDS, 1):
        result = run_local(*command)
        results.append(result)
        print(
            f"[{index:02d}/{len(COMMANDS) + 1:02d}] "
            f"{'PASS' if result['passed'] else 'FAIL'} {result['id']} "
            f"{result['elapsed_seconds']:.3f}s"
        )
    remote_result, git_state = run_remote_parity()
    results.append(remote_result)
    print(
        f"[{len(results):02d}/{len(results):02d}] "
        f"{'PASS' if remote_result['passed'] else 'FAIL'} git_remote_parity "
        f"{remote_result['elapsed_seconds']:.3f}s"
    )
    total = time.perf_counter() - started
    passed = sum(result["passed"] for result in results)
    expected_tests = {
        result_id: expected
        for result_id, _path, _arguments, expected in COMMANDS
        if expected is not None
    }
    rejected = sum(int(value.split("/")[0]) for value in expected_tests.values())
    mutation_total = sum(int(value.split("/")[1]) for value in expected_tests.values())
    evidence = {
        "record_type": "CH05SixRouteCadenceIntegratedRelease",
        "schema_version": "1.0",
        "record_id": "ng-ch05-six-route-cadence-integrated-release-r1",
        "state": "PASS" if passed == len(results) else "FAIL",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "release_runner": {
            "path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "sha256": sha256(Path(__file__).resolve()),
        },
        "companion_validator": {
            "path": VALIDATOR.relative_to(ROOT).as_posix(),
            "sha256": sha256(VALIDATOR),
        },
        "summary": {
            "validation_domains": 16,
            "local_validation_commands": 15,
            "read_only_remote_queries": 1,
            "passed": passed,
            "failed": len(results) - passed,
            "self_test_suites": len(expected_tests),
            "mutations_rejected": rejected,
            "mutation_total": mutation_total,
            "observed_total_seconds": round(total, 6),
            "provider_calls": 0,
            "external_uploads": 0,
            "generation_calls": 0,
            "generated_candidates": 0,
            "accepted": 0,
            "rights_cleared": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
            "paid_spend_usd": 0.0,
        },
        "expected_self_tests": expected_tests,
        "git_remote_state": git_state,
        "results": results,
        "activity_boundary": {
            "all_commands_local_except_read_only_git_remote_state": True,
            "provider_calls": 0,
            "external_uploads": 0,
            "generation_calls": 0,
            "paid_spend_usd": 0.0,
        },
        "boundary": "Append-only integrated validation evidence. Passing grants no generation, upload, provider-call, spend, acceptance, rights, commercial-use, exact-production-base, AnimationShotPlan, or E-Conte authority.",
    }
    if passed != len(results):
        print("FAIL: integrated matrix did not pass; append-only evidence not written")
        return 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"integrated release PASS {passed}/{len(results)}; "
        f"mutations {rejected}/{mutation_total}; {total:.3f}s; "
        f"{OUTPUT.relative_to(ROOT).as_posix()} {sha256(OUTPUT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
