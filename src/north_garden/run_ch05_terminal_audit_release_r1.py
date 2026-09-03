"""Run the append-only CH05 terminal audit release r1."""

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
OUTPUT = ROOT / "docs/research/evidence/ch05-terminal-audit-release-r1.json"
VALIDATOR = ROOT / "src/north_garden/validate_ch05_terminal_audit_release_r1.py"
APPROVED_BASE_HEAD = "12e553e3f31a4decfa4e63a217e6d399074d7b04"
EXPECTED_ORIGIN = "https://github.com/LoFiGamerGuy/visual-narrative-compiler"

INPUTS = [
    "docs/research/evidence/ch05-final-owner-start-here-r1.json",
    "docs/research/evidence/ch05-overnight-closeout-release-r1.json",
    "docs/research/evidence/ch05-active-goal-art-output-reconciliation-r1.json",
    "docs/research/evidence/ch05-production-cost-ledger-r37.json",
    "docs/research/evidence/ch05-overnight-safe-source-change-inventory-r3.json",
    "docs/research/evidence/frozen-gauntlet-baseline-integrity-r1.json",
]

COMMANDS: list[tuple[str, str, list[str], str | None, str]] = [
    (
        "final_owner_start_here",
        "src/north_garden/validate_ch05_final_owner_start_here_r1.py",
        ["--self-test"],
        "25/25",
        "NONE",
    ),
    (
        "overnight_closeout_release",
        "src/north_garden/validate_ch05_overnight_closeout_release_r1.py",
        ["--self-test"],
        "30/30",
        "READ_ONLY_GIT_REMOTE_STATE",
    ),
    (
        "active_goal_output_reconciliation",
        "src/north_garden/validate_ch05_active_goal_art_output_reconciliation.py",
        ["--self-test"],
        "18/18",
        "NONE",
    ),
    (
        "production_cost_ledger_r37",
        "src/north_garden/validate_ch05_production_cost_ledger_r37.py",
        ["--self-test"],
        "15/15",
        "NONE",
    ),
    (
        "overnight_safe_source_inventory_r3",
        "src/north_garden/validate_ch05_overnight_safe_source_change_inventory_r3.py",
        ["--self-test"],
        "21/21",
        "NONE",
    ),
    (
        "frozen_baseline_integrity",
        "src/north_garden/validate_frozen_gauntlet_baseline_integrity.py",
        [],
        "15/15",
        "NONE",
    ),
    (
        "tracked_source_scope",
        "src/north_garden/validate_tracked_source_scope.py",
        [],
        None,
        "NONE",
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
    for pattern in (
        r'"self_test":\s*"(\d+/\d+)"',
        r'"mutations_caught":\s*(\d+)',
        r"mutations (\d+/\d+) rejected",
        r"(\d+/\d+) mutations rejected",
    ):
        match = re.search(pattern, stdout)
        if not match:
            continue
        value = match.group(1)
        if "/" in value:
            return value
        return f"{value}/{value}"
    return None


def has_pass_marker(stdout: str) -> bool:
    return '"status": "PASS"' in stdout or " PASS:" in stdout or "0 failures" in stdout


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


def collect_git_state() -> tuple[dict[str, Any], int, str, float]:
    started = time.perf_counter()
    calls = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tracked_status": git("status", "--porcelain=v1", "--untracked-files=no"),
        "origin_url": git("remote", "get-url", "origin"),
        "remote_head": git("ls-remote", "--heads", "origin", "refs/heads/main"),
    }
    branch = calls["branch"].stdout.strip()
    head = calls["head"].stdout.strip()
    tracked_status = calls["tracked_status"].stdout.strip()
    origin_url = calls["origin_url"].stdout.strip()
    remote_line = calls["remote_head"].stdout.strip()
    remote_head = remote_line.split()[0] if remote_line else ""
    ancestor = git("merge-base", "--is-ancestor", APPROVED_BASE_HEAD, head)
    stderr = clean_output(
        "".join(call.stderr for call in calls.values()) + ancestor.stderr
    )
    passed = (
        all(call.returncode == 0 for call in calls.values())
        and ancestor.returncode == 0
        and branch == "main"
        and head == remote_head
        and not tracked_status
        and origin_url.removesuffix(".git") == EXPECTED_ORIGIN
        and not stderr
    )
    return (
        {
            "approved_base_head": APPROVED_BASE_HEAD,
            "approved_base_is_ancestor": ancestor.returncode == 0,
            "branch": branch,
            "local_head": head,
            "remote_head": remote_head,
            "origin_url": origin_url,
            "tracked_worktree_clean": not tracked_status,
            "local_remote_parity": head == remote_head,
        },
        0 if passed else 1,
        stderr,
        time.perf_counter() - started,
    )


def tracked_at_head(relative: str, head: str) -> bool:
    return git("cat-file", "-e", f"{head}:{relative}").returncode == 0


def binding(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)}


def run_local(
    result_id: str,
    relative: str,
    arguments: list[str],
    expected: str | None,
    network_access: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    completed = subprocess.run(
        [sys.executable, str(ROOT / relative), *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=1800,
        check=False,
    )
    stdout = clean_output(completed.stdout)
    stderr = clean_output(completed.stderr)
    observed = observed_self_test(stdout)
    passed = (
        completed.returncode == 0
        and not stderr
        and has_pass_marker(stdout)
        and (expected is None or observed == expected)
    )
    return {
        "id": result_id,
        "kind": "local_python_validator",
        "path": relative,
        "arguments": arguments,
        "script_sha256": sha256(ROOT / relative),
        "network_access": network_access,
        "return_code": completed.returncode,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "stdout": stdout,
        "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
        "stderr": stderr,
        "stderr_sha256": sha256_bytes(stderr.encode("utf-8")),
        "expected_self_test": expected,
        "observed_self_test": observed,
        "passed": passed,
    }


def git_result(
    state: dict[str, Any], return_code: int, stderr: str, elapsed: float
) -> dict[str, Any]:
    stdout = clean_output("\n".join(f"{key}={value}" for key, value in state.items()))
    return {
        "id": "git_remote_parity",
        "kind": "read_only_git_remote_state",
        "path": None,
        "arguments": [
            "git branch --show-current",
            "git rev-parse HEAD",
            "git status --porcelain=v1 --untracked-files=no",
            "git remote get-url origin",
            "git ls-remote --heads origin refs/heads/main",
            f"git merge-base --is-ancestor {APPROVED_BASE_HEAD} HEAD",
        ],
        "script_sha256": None,
        "network_access": "READ_ONLY_GIT_REMOTE_STATE",
        "return_code": return_code,
        "elapsed_seconds": round(elapsed, 6),
        "stdout": stdout,
        "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
        "stderr": stderr,
        "stderr_sha256": sha256_bytes(stderr.encode("utf-8")),
        "expected_self_test": None,
        "observed_self_test": None,
        "passed": return_code == 0 and not stderr,
    }


def main() -> int:
    if OUTPUT.exists():
        print(f"FAIL: append-only target already exists: {OUTPUT.relative_to(ROOT)}")
        return 2

    initial_state, initial_code, initial_stderr, _elapsed = collect_git_state()
    execution_head = initial_state["local_head"]
    required = [
        *INPUTS,
        *(relative for _id, relative, _args, _expected, _network in COMMANDS),
        Path(__file__).resolve().relative_to(ROOT).as_posix(),
        VALIDATOR.relative_to(ROOT).as_posix(),
    ]
    missing = [
        relative
        for relative in required
        if not (ROOT / relative).is_file()
        or not tracked_at_head(relative, execution_head)
    ]
    if initial_code or initial_stderr or missing:
        print(
            "FAIL: terminal preflight requires a clean pushed main descendant of "
            f"the approved base and all inputs/scripts tracked; missing_or_untracked={missing}; "
            f"git_stderr={initial_stderr!r}"
        )
        return 2

    started = time.perf_counter()
    results: list[dict[str, Any]] = []
    for index, command in enumerate(COMMANDS, 1):
        result = run_local(*command)
        results.append(result)
        print(
            f"[{index:02d}/{len(COMMANDS) + 1:02d}] "
            f"{'PASS' if result['passed'] else 'FAIL'} {result['id']} "
            f"{result['elapsed_seconds']:.3f}s"
        )

    final_state, final_code, final_stderr, final_elapsed = collect_git_state()
    if final_state["local_head"] != execution_head:
        final_code = 1
    remote = git_result(final_state, final_code, final_stderr, final_elapsed)
    results.append(remote)
    print(f"[08/08] {'PASS' if remote['passed'] else 'FAIL'} git_remote_parity")

    expected_tests = {
        result_id: expected
        for result_id, _relative, _arguments, expected, _network in COMMANDS
        if expected is not None
    }
    rejected = sum(int(value.split("/")[0]) for value in expected_tests.values())
    mutation_total = sum(int(value.split("/")[1]) for value in expected_tests.values())
    passed = sum(result["passed"] for result in results)
    total = time.perf_counter() - started
    tracked_match = re.search(r"(\d+) tracked safe-source paths", results[6]["stdout"])
    tracked_paths = int(tracked_match.group(1)) if tracked_match else None
    inventory_match = re.search(
        r"PASS: (\d+) commits; (\d+) files; (\d+) categories", results[4]["stdout"]
    )
    inventory_counts = (
        {
            "commits": int(inventory_match.group(1)),
            "changed_tracked_files": int(inventory_match.group(2)),
            "categories": int(inventory_match.group(3)),
        }
        if inventory_match
        else None
    )
    evidence = {
        "record_type": "CH05TerminalAuditRelease",
        "schema_version": "1.0",
        "record_id": "ng-ch05-terminal-audit-release-r1",
        "state": "PASS" if passed == len(results) else "FAIL",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "release_runner": binding(
            Path(__file__).resolve().relative_to(ROOT).as_posix()
        ),
        "companion_validator": binding(VALIDATOR.relative_to(ROOT).as_posix()),
        "input_bindings": [binding(relative) for relative in INPUTS],
        "expected_self_tests": expected_tests,
        "summary": {
            "validation_domains": 8,
            "local_validation_commands": 7,
            "explicit_read_only_remote_queries": 1,
            "read_only_remote_capable_results": 2,
            "passed": passed,
            "failed": len(results) - passed,
            "self_test_suites": 6,
            "mutations_rejected": rejected,
            "mutation_total": mutation_total,
            "observed_total_seconds": round(total, 6),
            "tracked_safe_source_paths": tracked_paths,
            "owner_start_supporting_documents": 7,
            "owner_start_visuals": 10,
            "closeout_bound_mutations": 135,
            "closeout_domains": 9,
            "reconciled_rasters": 76,
            "reconciled_panel_candidates_and_crops": 312,
            "reconciled_reference_bearing_records": 132,
            "reconciled_zero_reference_records": 13,
            "reconciled_unsplit_records": 2,
            "cost_ledger_milestones": 124,
            "inventory": inventory_counts,
            "frozen_paths_compared": 16,
            "baseline_tracked_paths_compared": 4,
            "provider_calls": 0,
            "external_uploads": 0,
            "generation_calls": 0,
            "new_pixels": 0,
            "accepted": 0,
            "rights_cleared": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
            "paid_spend_usd": 0.0,
        },
        "historical_execution_policy": {
            "approved_clean_base_head": APPROVED_BASE_HEAD,
            "execution_head": execution_head,
            "execution_head_is_clean_pushed_descendant": True,
            "record_is_immutable_historical_execution_evidence": True,
            "publication_may_create_a_clean_pushed_descendant": True,
            "replay_requires_recorded_head_ancestor_current_main": True,
            "replay_requires_current_clean_remote_parity": True,
        },
        "git_remote_state": final_state,
        "results": results,
        "activity_boundary": {
            "local_only_except_read_only_git_remote_state": True,
            "provider_calls": 0,
            "external_uploads": 0,
            "generation_calls": 0,
            "new_pixels": 0,
            "paid_spend_usd": 0.0,
        },
        "boundary": "Append-only terminal audit evidence under ADR-0192 historical-record/current-clean-descendant semantics. Passing grants no generation, pixel review or edit, upload, provider-call, spend, acceptance, rights, commercial-use, exact-production-base, AnimationShotPlan, or E-Conte authority.",
    }
    if passed != len(results) or tracked_paths is None or inventory_counts is None:
        print("FAIL: terminal matrix did not pass; append-only evidence not written")
        return 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"terminal audit PASS {passed}/{len(results)}; mutations "
        f"{rejected}/{mutation_total}; {total:.3f}s; "
        f"{OUTPUT.relative_to(ROOT).as_posix()} {sha256(OUTPUT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
