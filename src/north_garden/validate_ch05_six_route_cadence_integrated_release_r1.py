"""Replay and fail closed on the CH05 six-route/cadence integrated release r1."""

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
EVIDENCE = (
    ROOT / "docs/research/evidence/ch05-six-route-cadence-integrated-release-r1.json"
)
RUNNER = ROOT / "src/north_garden/run_ch05_six_route_cadence_integrated_release_r1.py"
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
REMOTE_ARGUMENTS = [
    "git branch --show-current",
    "git rev-parse HEAD",
    "git status --porcelain=v1 --untracked-files=no",
    "git remote get-url origin",
    "git ls-remote --heads origin refs/heads/main",
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


def current_git_state() -> tuple[dict[str, Any], int, str, str]:
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
    stderr = clean_output("".join(call.stderr for call in calls.values()))
    state = {
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
    return state, max(call.returncode for call in calls.values()), stdout, stderr


def validate(document: dict[str, Any], replay: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(
        document.get("record_type") == "CH05SixRouteCadenceIntegratedRelease",
        "record_type",
    )
    check(
        document.get("record_id") == "ng-ch05-six-route-cadence-integrated-release-r1",
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
    except ValueError:
        errors.append("created_at_utc")
    check(
        document.get("release_runner")
        == {
            "path": RUNNER.relative_to(ROOT).as_posix(),
            "sha256": sha256(RUNNER),
        },
        "runner binding",
    )
    validator_path = Path(__file__).resolve()
    check(
        document.get("companion_validator")
        == {
            "path": validator_path.relative_to(ROOT).as_posix(),
            "sha256": sha256(validator_path),
        },
        "validator binding",
    )
    expected_tests = {
        result_id: expected
        for result_id, _path, _arguments, expected in COMMANDS
        if expected is not None
    }
    check(document.get("expected_self_tests") == expected_tests, "self-test matrix")
    expected_summary = {
        "validation_domains": 16,
        "local_validation_commands": 15,
        "read_only_remote_queries": 1,
        "passed": 16,
        "failed": 0,
        "self_test_suites": 14,
        "mutations_rejected": 298,
        "mutation_total": 298,
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

    results = document.get("results", [])
    check(len(results) == 16, "result count")
    for index, (result_id, relative, arguments, expected) in enumerate(COMMANDS):
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
        check(
            result.get("script_sha256") == sha256(ROOT / relative),
            f"{prefix}:script hash",
        )
        check(result.get("network_access") == "NONE", f"{prefix}:network")
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
        check(
            '"status": "PASS"' in stdout or "0 failures" in stdout,
            f"{prefix}:PASS output",
        )
        if replay:
            return_code, replay_stdout, replay_stderr = run_local(relative, arguments)
            check(return_code == 0, f"{prefix}:replay return code")
            check(not replay_stderr, f"{prefix}:replay stderr")
            check(
                '"status": "PASS"' in replay_stdout or "0 failures" in replay_stdout,
                f"{prefix}:replay PASS output",
            )
            if expected is not None:
                check(
                    observed_self_test(replay_stdout) == expected,
                    f"{prefix}:replay self-test",
                )

    if len(results) >= 16:
        remote = results[15]
        check(remote.get("id") == "git_remote_parity", "remote:id")
        check(remote.get("kind") == "read_only_git_remote_state", "remote:kind")
        check(
            remote.get("path") is None and remote.get("script_sha256") is None,
            "remote:script",
        )
        check(remote.get("arguments") == REMOTE_ARGUMENTS, "remote:arguments")
        check(
            remote.get("network_access") == "READ_ONLY_GIT_REMOTE_STATE",
            "remote:network",
        )
        check(
            remote.get("return_code") == 0 and remote.get("passed") is True,
            "remote:pass",
        )
        check(
            remote.get("expected_self_test") is None
            and remote.get("observed_self_test") is None,
            "remote:self-test",
        )
        check(
            isinstance(remote.get("elapsed_seconds"), (int, float))
            and remote["elapsed_seconds"] > 0,
            "remote:timing",
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
        if replay:
            git_state, return_code, stdout, stderr = current_git_state()
            check(return_code == 0 and not stderr, "remote:replay command")
            recorded_head = document.get("git_remote_state", {}).get("local_head", "")
            ancestor = git("merge-base", "--is-ancestor", recorded_head, git_state["local_head"])
            check(ancestor.returncode == 0, "remote:recorded head is current ancestor")
            check(
                git_state.get("branch") == "main"
                and git_state.get("origin_url", "").removesuffix(".git")
                == EXPECTED_ORIGIN
                and git_state.get("tracked_worktree_clean") is True
                and git_state.get("local_remote_parity") is True,
                "remote:current clean parity",
            )

    expected_git = {
        "branch": "main",
        "local_head": EXPECTED_HEAD,
        "remote_head": EXPECTED_HEAD,
        "origin_url": EXPECTED_ORIGIN + ".git",
        "tracked_worktree_clean": True,
        "local_remote_parity": True,
    }
    check(document.get("git_remote_state") == expected_git, "git remote state")
    activity = document.get("activity_boundary", {})
    check(
        activity
        == {
            "all_commands_local_except_read_only_git_remote_state": True,
            "provider_calls": 0,
            "external_uploads": 0,
            "generation_calls": 0,
            "paid_spend_usd": 0.0,
        },
        "activity boundary",
    )
    boundary = document.get("boundary", "")
    for phrase in (
        "Append-only",
        "no generation",
        "upload",
        "provider-call",
        "spend",
        "acceptance",
        "rights",
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
        lambda value: value["summary"].__setitem__("validation_domains", 15),
        lambda value: value["summary"].__setitem__("passed", 15),
        lambda value: value["summary"].__setitem__("failed", 1),
        lambda value: value["summary"].__setitem__("mutations_rejected", 297),
        lambda value: value["summary"].__setitem__("provider_calls", 1),
        lambda value: value["summary"].__setitem__("external_uploads", 1),
        lambda value: value["summary"].__setitem__("generation_calls", 1),
        lambda value: value["summary"].__setitem__("paid_spend_usd", 1.0),
        lambda value: value["results"].pop(),
        lambda value: value["results"][0].__setitem__("return_code", 1),
        lambda value: value["results"][0].__setitem__("script_sha256", "0" * 64),
        lambda value: value["results"][0].__setitem__("stdout_sha256", "0" * 64),
        lambda value: value["results"][0].__setitem__("observed_self_test", "31/32"),
        lambda value: value["results"][0].__setitem__("network_access", "FULL"),
        lambda value: value["results"][15].__setitem__("network_access", "FULL"),
        lambda value: value["git_remote_state"].__setitem__("remote_head", "0" * 40),
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
