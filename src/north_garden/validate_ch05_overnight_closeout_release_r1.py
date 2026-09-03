"""Replay and fail closed on the CH05 overnight closeout release r1."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-overnight-closeout-release-r1.json"
RUNNER = ROOT / "src/north_garden/run_ch05_overnight_closeout_release_r1.py"
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


def git_blob(head: str, relative: str) -> bytes | None:
    completed = subprocess.run(
        ["git", "show", f"{head}:{relative}"],
        cwd=ROOT,
        capture_output=True,
        timeout=120,
        check=False,
    )
    return completed.stdout if completed.returncode == 0 else None


def current_git_state() -> tuple[dict[str, Any], int, str]:
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
    stderr = clean_output("".join(call.stderr for call in calls.values()))
    state = {
        "branch": branch,
        "local_head": head,
        "remote_head": remote_head,
        "origin_url": origin_url,
        "tracked_worktree_clean": not status,
        "local_remote_parity": head == remote_head,
    }
    return state, max(call.returncode for call in calls.values()), stderr


def run_local(relative: str, arguments: list[str]) -> tuple[int, str, str]:
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
    return (
        completed.returncode,
        clean_output(completed.stdout),
        clean_output(completed.stderr),
    )


def check_historical_binding(
    binding: Any, expected_path: str, head: str, errors: list[str], label: str
) -> None:
    if not isinstance(binding, dict):
        errors.append(f"{label}:object")
        return
    blob = git_blob(head, expected_path)
    if blob is None:
        errors.append(f"{label}:historical blob")
        return
    if binding.get("path") != expected_path:
        errors.append(f"{label}:path")
    if binding.get("bytes") != len(blob):
        errors.append(f"{label}:bytes")
    if binding.get("sha256") != sha256_bytes(blob):
        errors.append(f"{label}:sha256")


def validate(document: dict[str, Any], replay: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(document.get("record_type") == "CH05OvernightCloseoutRelease", "record_type")
    check(
        document.get("record_id") == "ng-ch05-overnight-closeout-release-r1",
        "record_id",
    )
    check(document.get("state") == "PASS", "state")
    check(document.get("medium") == "comic", "medium")
    check(
        document.get("planning_structure") == "ComicPanelPlan"
        and document.get("animation_shot_plan") is None
        and document.get("e_conte") is None,
        "planning boundary",
    )
    try:
        datetime.fromisoformat(document.get("created_at_utc", ""))
    except (TypeError, ValueError):
        errors.append("created_at_utc")

    policy = document.get("historical_execution_policy", {})
    execution_head = policy.get("execution_head", "")
    check(re.fullmatch(r"[0-9a-f]{40}", execution_head) is not None, "execution head")
    check(
        policy
        == {
            "approved_clean_base_head": APPROVED_BASE_HEAD,
            "execution_head": execution_head,
            "execution_head_is_clean_pushed_descendant": True,
            "record_is_immutable_historical_execution_evidence": True,
            "publication_may_create_a_clean_pushed_descendant": True,
            "replay_requires_recorded_head_ancestor_current_main": True,
            "replay_requires_current_clean_remote_parity": True,
        },
        "historical execution policy",
    )
    if execution_head:
        base_ancestor = git(
            "merge-base", "--is-ancestor", APPROVED_BASE_HEAD, execution_head
        )
        check(base_ancestor.returncode == 0, "approved base ancestor of execution head")
        check_historical_binding(
            document.get("release_runner"),
            RUNNER.relative_to(ROOT).as_posix(),
            execution_head,
            errors,
            "runner binding",
        )
        check_historical_binding(
            document.get("companion_validator"),
            Path(__file__).resolve().relative_to(ROOT).as_posix(),
            execution_head,
            errors,
            "validator binding",
        )
        bindings = document.get("input_bindings", [])
        check(len(bindings) == len(INPUTS), "input binding count")
        for index, relative in enumerate(INPUTS):
            if index < len(bindings):
                check_historical_binding(
                    bindings[index],
                    relative,
                    execution_head,
                    errors,
                    f"input:{relative}",
                )

    expected_tests = {
        result_id: expected
        for result_id, _path, _args, expected, _network in COMMANDS
        if expected is not None
    }
    check(document.get("expected_self_tests") == expected_tests, "self-test matrix")
    expected_summary = {
        "validation_domains": 9,
        "local_validation_commands": 8,
        "explicit_read_only_remote_queries": 1,
        "read_only_remote_capable_results": 2,
        "passed": 9,
        "failed": 0,
        "self_test_suites": 7,
        "mutations_rejected": 135,
        "mutation_total": 135,
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
    }
    summary = document.get("summary", {})
    for key, expected in expected_summary.items():
        check(summary.get(key) == expected, f"summary:{key}")
    check(
        isinstance(summary.get("observed_total_seconds"), (int, float))
        and summary["observed_total_seconds"] > 0,
        "summary:observed_total_seconds",
    )
    check(
        isinstance(summary.get("tracked_safe_source_paths"), int)
        and summary["tracked_safe_source_paths"] > 0,
        "summary:tracked_safe_source_paths",
    )

    results = document.get("results", [])
    check(len(results) == 9, "result count")
    for index, (result_id, relative, arguments, expected, network) in enumerate(
        COMMANDS
    ):
        if index >= len(results):
            break
        result = results[index]
        prefix = f"result:{result_id}"
        stdout = result.get("stdout", "")
        stderr = result.get("stderr", "")
        check(result.get("id") == result_id, f"{prefix}:id")
        check(result.get("kind") == "local_python_validator", f"{prefix}:kind")
        check(result.get("path") == relative, f"{prefix}:path")
        check(result.get("arguments") == arguments, f"{prefix}:arguments")
        historical_script = (
            git_blob(execution_head, relative) if execution_head else None
        )
        check(
            historical_script is not None
            and result.get("script_sha256") == sha256_bytes(historical_script),
            f"{prefix}:historical script hash",
        )
        check(result.get("network_access") == network, f"{prefix}:network")
        check(result.get("return_code") == 0, f"{prefix}:return code")
        check(
            isinstance(result.get("elapsed_seconds"), (int, float))
            and result["elapsed_seconds"] > 0,
            f"{prefix}:timing",
        )
        check(
            result.get("stdout_sha256") == sha256_bytes(stdout.encode("utf-8")),
            f"{prefix}:stdout hash",
        )
        check(
            not stderr and result.get("stderr_sha256") == sha256_bytes(b""),
            f"{prefix}:stderr",
        )
        check(
            result.get("expected_self_test") == expected, f"{prefix}:expected self-test"
        )
        check(
            result.get("observed_self_test") == expected, f"{prefix}:observed self-test"
        )
        check(result.get("passed") is True, f"{prefix}:passed")
        check(has_pass_marker(stdout), f"{prefix}:PASS output")
        if replay:
            code, replay_stdout, replay_stderr = run_local(relative, arguments)
            check(code == 0 and not replay_stderr, f"{prefix}:replay command")
            check(has_pass_marker(replay_stdout), f"{prefix}:replay PASS output")
            if expected is not None:
                check(
                    observed_self_test(replay_stdout) == expected,
                    f"{prefix}:replay self-test",
                )

    if len(results) >= 9:
        remote = results[8]
        check(remote.get("id") == "git_remote_parity", "remote:id")
        check(remote.get("kind") == "read_only_git_remote_state", "remote:kind")
        check(
            remote.get("path") is None and remote.get("script_sha256") is None,
            "remote:script",
        )
        check(
            remote.get("network_access") == "READ_ONLY_GIT_REMOTE_STATE",
            "remote:network",
        )
        check(
            remote.get("return_code") == 0 and remote.get("passed") is True,
            "remote:pass",
        )
        check(remote.get("elapsed_seconds") is None, "remote:timing")
        check(
            remote.get("expected_self_test") is None
            and remote.get("observed_self_test") is None,
            "remote:self-test",
        )
        check(
            remote.get("stdout_sha256")
            == sha256_bytes(remote.get("stdout", "").encode("utf-8")),
            "remote:stdout hash",
        )
        check(
            not remote.get("stderr")
            and remote.get("stderr_sha256") == sha256_bytes(b""),
            "remote:stderr",
        )

    recorded_git = document.get("git_remote_state", {})
    check(
        recorded_git
        == {
            "approved_base_head": APPROVED_BASE_HEAD,
            "approved_base_is_ancestor": True,
            "branch": "main",
            "local_head": execution_head,
            "remote_head": execution_head,
            "origin_url": EXPECTED_ORIGIN + ".git",
            "tracked_worktree_clean": True,
            "local_remote_parity": True,
        },
        "recorded git remote state",
    )
    if replay:
        current, return_code, stderr = current_git_state()
        check(return_code == 0 and not stderr, "current git commands")
        ancestor = git(
            "merge-base", "--is-ancestor", execution_head, current["local_head"]
        )
        check(ancestor.returncode == 0, "recorded head is current ancestor")
        check(
            current.get("branch") == "main"
            and current.get("origin_url", "").removesuffix(".git") == EXPECTED_ORIGIN
            and current.get("tracked_worktree_clean") is True
            and current.get("local_remote_parity") is True,
            "current clean remote parity",
        )

    check(
        document.get("activity_boundary")
        == {
            "local_only_except_read_only_git_remote_state": True,
            "provider_calls": 0,
            "external_uploads": 0,
            "generation_calls": 0,
            "new_pixels": 0,
            "paid_spend_usd": 0.0,
        },
        "activity boundary",
    )
    boundary = document.get("boundary", "")
    for phrase in (
        "Append-only",
        "ADR-0192",
        "no generation",
        "pixel review or edit",
        "upload",
        "provider-call",
        "spend",
        "acceptance",
        "rights",
        "commercial-use",
        "exact-production-base",
        "AnimationShotPlan",
        "E-Conte",
    ):
        check(phrase in boundary, f"boundary:{phrase}")
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    Mutation = Callable[[dict[str, Any]], None]
    mutations: list[Mutation] = [
        lambda value: value.__setitem__("state", "FAIL"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("animation_shot_plan", {}),
        lambda value: value.__setitem__("e_conte", {}),
        lambda value: value["release_runner"].__setitem__("sha256", "0" * 64),
        lambda value: value["companion_validator"].__setitem__("sha256", "0" * 64),
        lambda value: value["input_bindings"][0].__setitem__("sha256", "0" * 64),
        lambda value: value["input_bindings"].pop(),
        lambda value: value["summary"].__setitem__("validation_domains", 8),
        lambda value: value["summary"].__setitem__("passed", 8),
        lambda value: value["summary"].__setitem__("failed", 1),
        lambda value: value["summary"].__setitem__("mutations_rejected", 134),
        lambda value: value["summary"].__setitem__("tracked_safe_source_paths", 0),
        lambda value: value["summary"].__setitem__("review_links_bound", 40),
        lambda value: value["summary"].__setitem__("provider_calls", 1),
        lambda value: value["summary"].__setitem__("external_uploads", 1),
        lambda value: value["summary"].__setitem__("generation_calls", 1),
        lambda value: value["summary"].__setitem__("paid_spend_usd", 1.0),
        lambda value: value["results"].pop(),
        lambda value: value["results"][0].__setitem__("return_code", 1),
        lambda value: value["results"][0].__setitem__("script_sha256", "0" * 64),
        lambda value: value["results"][0].__setitem__("stdout_sha256", "0" * 64),
        lambda value: value["results"][0].__setitem__("observed_self_test", "25/26"),
        lambda value: value["results"][0].__setitem__("network_access", "FULL"),
        lambda value: value["results"][8].__setitem__("network_access", "FULL"),
        lambda value: value["historical_execution_policy"].__setitem__(
            "approved_clean_base_head", "0" * 40
        ),
        lambda value: value["git_remote_state"].__setitem__(
            "tracked_worktree_clean", False
        ),
        lambda value: value["activity_boundary"].__setitem__("provider_calls", 1),
        lambda value: value.__setitem__("expected_self_tests", {}),
        lambda value: value.__setitem__("boundary", "accepted"),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate, replay=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not EVIDENCE.is_file():
        print(f"FAIL: evidence does not exist: {EVIDENCE.relative_to(ROOT)}")
        return 2
    document = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    errors = validate(document)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(document)
        if caught != total:
            errors.append(f"self-test:{caught}/{total}")
    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
                "domains_replayed": len(document.get("results", [])),
                "bound_mutations": document.get("summary", {}).get(
                    "mutations_rejected"
                ),
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
