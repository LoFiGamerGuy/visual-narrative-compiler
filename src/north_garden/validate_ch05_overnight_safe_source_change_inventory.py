"""Validate and mutation-test the CH05 overnight safe-source inventory."""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
from pathlib import Path

from north_garden.compile_ch05_overnight_safe_source_change_inventory import (
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


def validate_payload(
    record: dict[str, object], expected: dict[str, object]
) -> list[str]:
    errors: list[str] = []
    if record != expected:
        errors.append("record differs from deterministic pinned-range rebuild")
    if git_text("rev-parse", f"{FIRST_GOAL_COMMIT}^") != RANGE_BASE:
        errors.append("range base is not the first goal commit parent")
    if record.get("summary", {}).get("prohibited_or_generated_tracked_paths") != 0:
        errors.append("prohibited/generated tracked path count is nonzero")
    groups = record.get("groups", [])
    entries = [
        entry
        for group in groups
        for status_group in group.get("status_groups", [])
        for entry in status_group.get("entries", [])
    ]
    if len(entries) != record.get("summary", {}).get("changed_tracked_files"):
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
                errors.append(
                    f"deleted path retains current blob data: {entry.get('path')}"
                )
        else:
            errors.append(f"unknown current state for {entry.get('path')}")
    return errors


def mutation_cases(record: dict[str, object]) -> list[tuple[str, dict[str, object]]]:
    cases: list[tuple[str, dict[str, object]]] = []

    def mutate(name: str, operation) -> None:
        candidate = copy.deepcopy(record)
        operation(candidate)
        cases.append((name, candidate))

    mutate("record_id", lambda item: item.__setitem__("record_id", "mutated"))
    mutate(
        "base", lambda item: item["scope"].__setitem__("range_base_parent", "0" * 40)
    )
    mutate("head", lambda item: item["scope"].__setitem__("range_head", "f" * 40))
    mutate("range", lambda item: item["scope"].__setitem__("revision_range", "mutated"))
    mutate("commit_count", lambda item: item["summary"].__setitem__("commit_count", 17))
    mutate("drop_commit", lambda item: item["commits"].pop())
    mutate(
        "file_count",
        lambda item: item["summary"].__setitem__("changed_tracked_files", 273),
    )
    mutate(
        "status_counts",
        lambda item: item["summary"]["status_counts"].__setitem__("A", 266),
    )
    mutate(
        "category_counts",
        lambda item: item["summary"]["category_counts"].__setitem__("source_code", 120),
    )
    first_entry = lambda item: item["groups"][0]["status_groups"][0]["entries"][0]
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
        "entry_category",
        lambda item: first_entry(item).__setitem__("category", "other"),
    )
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
    expected_markdown = render_markdown(record)
    actual_markdown = OUTPUT_MARKDOWN.read_text(encoding="utf-8")
    if actual_markdown != expected_markdown:
        errors.append("owner-readable Markdown differs from deterministic render")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    rejected = 0
    if args.self_test:
        for name, mutation in mutation_cases(record):
            if validate_payload(mutation, expected):
                rejected += 1
            else:
                print(f"FAIL: mutation survived: {name}")
                return 1
    print(
        "CH05 overnight safe-source inventory PASS: "
        f"{record['summary']['commit_count']} commits; "
        f"{record['summary']['changed_tracked_files']} files; "
        f"{len(record['groups'])} categories; mutations {rejected}/{len(mutation_cases(record)) if args.self_test else 0} rejected"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
