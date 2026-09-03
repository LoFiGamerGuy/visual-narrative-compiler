"""Validate and mutation-test append-only CH05 safe-source inventory r2."""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
from pathlib import Path

from compile_ch05_overnight_safe_source_change_inventory_r2 import (
    FIRST_GOAL_COMMIT,
    OUTPUT_JSON,
    OUTPUT_MARKDOWN,
    RANGE_BASE,
    build_inventory,
    render_markdown,
)

ROOT = Path(__file__).resolve().parents[2]


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def flattened_entries(record: dict[str, object]) -> list[dict[str, object]]:
    return [
        entry
        for group in record.get("groups", [])
        for status_group in group.get("status_groups", [])
        for entry in status_group.get("entries", [])
    ]


def validate_payload(
    record: dict[str, object], expected: dict[str, object]
) -> list[str]:
    errors: list[str] = []
    if record != expected:
        errors.append("record differs from deterministic pinned-range rebuild")
    if git_text("rev-parse", f"{FIRST_GOAL_COMMIT}^") != RANGE_BASE:
        errors.append("range base is not the first goal commit parent")
    if record.get("supersedes", {}).get("prior_record_rewritten") is not False:
        errors.append("r1 rewrite boundary is not false")
    summary = record.get("summary", {})
    if summary.get("prohibited_or_generated_tracked_paths") != 0:
        errors.append("prohibited/generated tracked path count is nonzero")
    entries = flattened_entries(record)
    if len(entries) != summary.get("changed_tracked_files"):
        errors.append("flattened entry count mismatch")
    if len({entry.get("path") for entry in entries}) != len(entries):
        errors.append("duplicate current path")
    for entry in entries:
        if entry.get("current_state") == "PRESENT_AT_RANGE_HEAD":
            digest = entry.get("blob_sha256")
            if not isinstance(digest, str) or len(digest) != 64:
                errors.append(f"invalid SHA-256 for {entry.get('path')}")
        elif entry.get("current_state") == "DELETED_IN_RANGE_HEAD":
            if any(
                entry.get(field) is not None
                for field in ("blob_sha256", "git_blob_oid", "git_mode", "bytes")
            ):
                errors.append(f"deleted path retains blob data: {entry.get('path')}")
        else:
            errors.append(f"unknown current state for {entry.get('path')}")
    return errors


def mutation_cases(record: dict[str, object]) -> list[tuple[str, dict[str, object]]]:
    cases: list[tuple[str, dict[str, object]]] = []

    def mutate(name: str, operation) -> None:
        candidate = copy.deepcopy(record)
        operation(candidate)
        cases.append((name, candidate))

    def first_entry(item: dict[str, object]) -> dict[str, object]:
        return item["groups"][0]["status_groups"][0]["entries"][0]

    mutate("record_id", lambda item: item.__setitem__("record_id", "mutated"))
    mutate(
        "prior_hash",
        lambda item: item["supersedes"]["record"].__setitem__("blob_sha256", "0" * 64),
    )
    mutate(
        "prior_rewrite",
        lambda item: item["supersedes"].__setitem__("prior_record_rewritten", True),
    )
    mutate(
        "base", lambda item: item["scope"].__setitem__("range_base_parent", "0" * 40)
    )
    mutate("head", lambda item: item["scope"].__setitem__("range_head", "f" * 40))
    mutate("range", lambda item: item["scope"].__setitem__("revision_range", "mutated"))
    mutate("commit_count", lambda item: item["summary"].__setitem__("commit_count", 21))
    mutate(
        "post_r1_count", lambda item: item["summary"].__setitem__("post_r1_commits", 3)
    )
    mutate("drop_commit", lambda item: item["commits"].pop())
    mutate(
        "file_count",
        lambda item: item["summary"].__setitem__("changed_tracked_files", 292),
    )
    mutate(
        "status_counts",
        lambda item: item["summary"]["status_counts"].__setitem__("A", 285),
    )
    mutate(
        "category_counts",
        lambda item: item["summary"]["category_counts"].__setitem__("source_code", 130),
    )
    mutate("entry_path", lambda item: first_entry(item).__setitem__("path", "mutated"))
    mutate("entry_status", lambda item: first_entry(item).__setitem__("status", "D"))
    mutate(
        "entry_sha256",
        lambda item: first_entry(item).__setitem__("blob_sha256", "0" * 64),
    )
    mutate(
        "entry_oid",
        lambda item: first_entry(item).__setitem__("git_blob_oid", "0" * 40),
    )
    mutate("entry_size", lambda item: first_entry(item).__setitem__("bytes", 0))
    mutate(
        "safety_count",
        lambda item: item["summary"].__setitem__(
            "prohibited_or_generated_tracked_paths", 1
        ),
    )
    return cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    record = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    expected = build_inventory()
    errors = validate_payload(record, expected)
    if OUTPUT_MARKDOWN.read_text(encoding="utf-8") != render_markdown(record):
        errors.append("Markdown differs from deterministic render")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    rejected = 0
    cases = mutation_cases(record) if args.self_test else []
    for name, mutation in cases:
        if validate_payload(mutation, expected):
            rejected += 1
        else:
            print(f"FAIL: mutation survived: {name}")
            return 1
    print(
        "CH05 safe-source inventory r2 PASS: "
        f"{record['summary']['commit_count']} commits; "
        f"{record['summary']['changed_tracked_files']} files; "
        f"{len(record['groups'])} categories; mutations {rejected}/{len(cases)} rejected"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
