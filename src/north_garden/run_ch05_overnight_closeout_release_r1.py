"""Run the append-only CH05 overnight closeout release r1."""

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
OUTPUT = ROOT / "docs/research/evidence/ch05-overnight-closeout-release-r1.json"
VALIDATOR = ROOT / "src/north_garden/validate_ch05_overnight_closeout_release_r1.py"
APPROVED_BASE_HEAD = "fabe843304bbae9ccf8e8426b0ae86144972e99f"
EXPECTED_ORIGIN = "https://github.com/LoFiGamerGuy/visual-narrative-compiler"

INPUTS = [
    "docs/research/evidence/ch05-six-route-cadence-integrated-release-r1.json",
    "docs/research/evidence/ch05-production-cost-ledger-r36.json",
    "docs/research/evidence/ch05-chapter-scale-production-decision-matrix-r1.json",
    "docs/research/evidence/ch05-complete-chapter-review-handoff-r7-link-integrity-r1.json",
    "docs/research/evidence/ch05-cadence-objective-sensitivity-audit-r1.json",
    "docs/research/evidence/ch05-overnight-safe-source-change-inventory-r2.json",
    "docs/research/evidence/frozen-gauntlet-baseline-integrity-r1.json",
]

COMMANDS: list[tuple[str, str, list[str], str | None, str]] = [
    (
        "six_route_integrated_release",
        "src/north_garden/validate_ch05_six_route_cadence_integrated_release_r1.py",
        ["--self-test"],
        "26/26",
        "READ_ONLY_GIT_REMOTE_STATE",
    ),
    (
        "production_cost_ledger_r36",
        "src/north_garden/validate_ch05_production_cost_ledger_r36.py",
        ["--self-test"],
        "17/17",
        "NONE",
    ),
    (
        "chapter_scale_decision_matrix",
        "src/north_garden/validate_ch05_chapter_scale_production_decision_matrix.py",
        ["--self-test"],
        "16/16",
        "NONE",
    ),
    (
        "review_handoff_link_integrity",
        "src/north_garden/validate_ch05_review_handoff_r7_link_integrity.py",
        ["--self-test"],
        "24/24",
        "NONE",
    ),
    (
        "cadence_objective_sensitivity",
        "src/north_garden/validate_ch05_cadence_objective_sensitivity_audit.py",
        ["--self-test"],
        "19/19",
        "NONE",
    ),
    (
        "overnight_safe_source_inventory_r2",
        "src/north_garden/validate_ch05_overnight_safe_source_change_inventory_r2.py",
        ["--self-test"],
        "18/18",
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
    json_match = re.search(r'"self_test":\s*"(\d+/\d+)"', stdout)
    if json_match:
        return json_match.group(1)
    plain_match = re.search(r"(\d+/\d+) mutations rejected", stdout)
    return plain_match.group(1) if plain_match else None


def has_pass_marker(stdout: str) -> bool:
    return (
        '"status": "PASS"' in stdout
        or " PASS:" in stdout
        or " PASS " in stdout
        or stdout.startswith("CH05 safe-source inventory r2 PASS:")
        or "0 failures" in stdout
    )


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


def git_state() -> tuple[dict[str, Any], int, str]:
    calls = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tracked_status": git("status", "--porcelain=v1", "--untracked-files=no"),
        "origin_url": git("remote", "get-url", "origin"),
        "remote_head": git("ls-remote", "--heads", "origin", "refs/heads/main"),
    }
    branch = calls["branch"].stdout.strip()
    head = calls["head"].stdout.strip()
    status = calls["tracked_status"].stdout.strip()
    origin_url = calls["origin_url"].stdout.strip()
    remote_line = calls["remote_head"].stdout.strip()
    remote_head = remote_line.split()[0] if remote_line else ""
    base_ancestor = git("merge-base", "--is-ancestor", APPROVED_BASE_HEAD, head)
    stderr = clean_output(
        "".join(call.stderr for call in calls.values()) + base_ancestor.stderr
    )
    passed = (
        all(call.returncode == 0 for call in calls.values())
        and base_ancestor.returncode == 0
        and branch == "main"
        and head == remote_head
        and not status
        and origin_url.removesuffix(".git") == EXPECTED_ORIGIN
        and not stderr
    )
    state = {
        "approved_base_head": APPROVED_BASE_HEAD,
        "approved_base_is_ancestor": base_ancestor.returncode == 0,
        "branch": branch,
        "local_head": head,
        "remote_head": remote_head,
        "origin_url": origin_url,
        "tracked_worktree_clean": not status,
        "local_remote_parity": head == remote_head,
    }
    return state, 0 if passed else 1, stderr


def tracked_at_head(relative: str, head: str) -> bool:
    result = git("cat-file", "-e", f"{head}:{relative}")
    return result.returncode == 0


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
        and has_pass_marker(stdout)
        and (expected is None or observed == expected)
    )
    return {
        "id": result_id,
        "kind": "local_python_validator",
        "path": relative,
        "arguments": arguments,
        "script_sha256": sha256(path),
        "network_access": network_access,
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


def remote_result(
    state: dict[str, Any], return_code: int, stderr: str
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
        "elapsed_seconds": None,
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

    first_state, first_code, first_stderr = git_state()
    execution_head = first_state["local_head"]
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
    if first_code or first_stderr or missing:
        print(
            "FAIL: preflight requires a clean pushed main descendant of the approved "
            f"base and all inputs/scripts tracked; missing_or_untracked={missing}; "
            f"git_stderr={first_stderr!r}"
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

    final_state, final_code, final_stderr = git_state()
    if final_state["local_head"] != execution_head:
        final_code = 1
    git_result = remote_result(final_state, final_code, final_stderr)
    results.append(git_result)
    print(
        f"[{len(results):02d}/{len(results):02d}] "
        f"{'PASS' if git_result['passed'] else 'FAIL'} git_remote_parity"
    )

    expected_tests = {
        result_id: expected
        for result_id, _relative, _arguments, expected, _network in COMMANDS
        if expected is not None
    }
    mutations = sum(int(value.split("/")[0]) for value in expected_tests.values())
    total_mutations = sum(int(value.split("/")[1]) for value in expected_tests.values())
    passed = sum(result["passed"] for result in results)
    total = time.perf_counter() - started
    scope_match = re.search(
        r"(\d+) tracked safe-source paths", results[7].get("stdout", "")
    )
    tracked_paths = int(scope_match.group(1)) if scope_match else None
    evidence = {
        "record_type": "CH05OvernightCloseoutRelease",
        "schema_version": "1.0",
        "record_id": "ng-ch05-overnight-closeout-release-r1",
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
            "validation_domains": 9,
            "local_validation_commands": 8,
            "explicit_read_only_remote_queries": 1,
            "read_only_remote_capable_results": 2,
            "passed": passed,
            "failed": len(results) - passed,
            "self_test_suites": 7,
            "mutations_rejected": mutations,
            "mutation_total": total_mutations,
            "observed_total_seconds": round(total, 6),
            "tracked_safe_source_paths": tracked_paths,
            "cost_ledger_milestones": 122,
            "cost_ledger_source_bindings": 5,
            "inventory_commits": 22,
            "inventory_changed_tracked_files": 293,
            "inventory_categories": 7,
            "review_links_bound": 41,
            "cadence_sensitivity_variants": 8,
            "cadence_variants_matching_baseline": 7,
            "frozen_paths_compared": 16,
            "baseline_tracked_paths_compared": 4,
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
        "boundary": "Append-only closeout evidence under ADR-0192 historical-record/current-clean-descendant semantics. Passing grants no generation, pixel review or edit, upload, provider-call, spend, acceptance, rights, commercial-use, exact-production-base, AnimationShotPlan, or E-Conte authority.",
    }
    if passed != len(results) or tracked_paths is None:
        print("FAIL: closeout matrix did not pass; append-only evidence not written")
        return 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"overnight closeout PASS {passed}/{len(results)}; mutations "
        f"{mutations}/{total_mutations}; {total:.3f}s; "
        f"{OUTPUT.relative_to(ROOT).as_posix()} {sha256(OUTPUT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
