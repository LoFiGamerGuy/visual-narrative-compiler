"""Compile append-only CH05 overnight safe-source change inventory r3."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from compile_ch05_overnight_safe_source_change_inventory import (
    CATEGORY_ORDER,
    FIRST_GOAL_COMMIT,
    STATUS_ORDER,
    commit_records,
    git_bytes,
    git_is_ancestor,
    git_text,
    markdown_escape,
    parse_changes,
    prohibited_reason,
)

ROOT = Path(__file__).resolve().parents[2]
RANGE_BASE = "7572c7e9a057855dfd34f3a62f6d227b955f02f9"
RANGE_HEAD = "ac5529a4621d4d73e9dea60a70fb515c4213caf3"
R2_HEAD = "52fbcea15202690f42bcd971fbee5ae100bc5845"
PRIOR_JSON = (
    "docs/research/evidence/ch05-overnight-safe-source-change-inventory-r2.json"
)
PRIOR_MARKDOWN = "docs/research/ch05-overnight-safe-source-change-inventory-r2.md"
OUTPUT_JSON = (
    ROOT / "docs/research/evidence/ch05-overnight-safe-source-change-inventory-r3.json"
)
OUTPUT_MARKDOWN = (
    ROOT / "docs/research/ch05-overnight-safe-source-change-inventory-r3.md"
)


def commit_blob_binding(relative: str) -> dict[str, object]:
    content = git_bytes("show", f"{RANGE_HEAD}:{relative}")
    tree_line = git_text("ls-tree", RANGE_HEAD, "--", relative)
    metadata, listed_path = tree_line.split("\t", 1)
    mode, object_type, oid = metadata.split(" ", 2)
    if object_type != "blob" or listed_path != relative:
        raise ValueError(f"unexpected prior-record ls-tree result: {tree_line}")
    return {
        "path": relative,
        "blob_sha256": hashlib.sha256(content).hexdigest(),
        "git_blob_oid": oid,
        "git_mode": mode,
        "bytes": len(content),
    }


def build_inventory() -> dict[str, object]:
    if git_text("rev-parse", f"{FIRST_GOAL_COMMIT}^") != RANGE_BASE:
        raise ValueError("range base is not the parent of the first goal commit")
    current_head = git_text("rev-parse", "HEAD")
    if not git_is_ancestor(RANGE_HEAD, current_head):
        raise ValueError(
            f"pinned range head {RANGE_HEAD} is not an ancestor of {current_head}"
        )

    changes = parse_changes(RANGE_BASE, RANGE_HEAD)
    commits = commit_records(RANGE_BASE, RANGE_HEAD)
    status_counts = Counter(str(item["status"]) for item in changes)
    category_counts = Counter(str(item["category"]) for item in changes)
    prohibited = [
        {"path": str(item["path"]), "reason": prohibited_reason(str(item["path"]))}
        for item in changes
        if prohibited_reason(str(item["path"])) is not None
    ]
    groups: list[dict[str, object]] = []
    for category in CATEGORY_ORDER:
        category_entries = [item for item in changes if item["category"] == category]
        if not category_entries:
            continue
        status_groups = []
        for status in STATUS_ORDER:
            entries = [item for item in category_entries if item["status"] == status]
            if entries:
                status_groups.append(
                    {"status": status, "count": len(entries), "entries": entries}
                )
        groups.append(
            {
                "category": category,
                "count": len(category_entries),
                "status_counts": {
                    group["status"]: group["count"] for group in status_groups
                },
                "status_groups": status_groups,
            }
        )

    return {
        "record_type": "CH05OvernightSafeSourceChangeInventory",
        "schema_version": "3.0",
        "record_id": "ng-ch05-overnight-safe-source-change-inventory-r3",
        "state": "FINAL_COMMIT_PINNED_SAFE_SOURCE_INVENTORY_PASS",
        "supersedes": {
            "record": commit_blob_binding(PRIOR_JSON),
            "owner_readable_inventory": commit_blob_binding(PRIOR_MARKDOWN),
            "prior_records_rewritten": False,
            "lineage": ["r1", "r2", "r3"],
        },
        "scope": {
            "first_goal_commit": FIRST_GOAL_COMMIT,
            "range_base_parent": RANGE_BASE,
            "range_head": RANGE_HEAD,
            "revision_range": f"{RANGE_BASE}..{RANGE_HEAD}",
            "base_selection": "Parent of the first overnight-goal commit; the first included commit is f882b0e.",
            "head_selection": "Clean pushed main/origin-main frontier containing the final CH05 owner-review start page.",
            "working_tree_included": False,
            "untracked_files_included": False,
            "generated_pixels_included": False,
        },
        "summary": {
            "commit_count": len(commits),
            "changed_tracked_files": len(changes),
            "status_counts": {
                status: status_counts[status]
                for status in STATUS_ORDER
                if status_counts[status]
            },
            "category_counts": {
                category: category_counts[category]
                for category in CATEGORY_ORDER
                if category_counts[category]
            },
            "present_blob_sha256_count": sum(
                1 for item in changes if item["blob_sha256"] is not None
            ),
            "deleted_count": sum(1 for item in changes if item["status"] == "D"),
            "prohibited_or_generated_tracked_paths": len(prohibited),
            "post_r2_commits": len(commit_records(R2_HEAD, RANGE_HEAD)),
        },
        "commits": commits,
        "groups": groups,
        "safety": {
            "prohibited_or_generated_tracked_paths": prohibited,
            "persistent_untracked_user_files_touched": 0,
            "interpretation": "The inventory derives only from committed tracked paths in the pinned range. Working-tree, ignored, and untracked files are outside the enumerated set.",
        },
        "generated_by": "src/north_garden/compile_ch05_overnight_safe_source_change_inventory_r3.py",
        "validated_by": "src/north_garden/validate_ch05_overnight_safe_source_change_inventory_r3.py",
        "boundary": "Final append-only source/evidence inventory. It supersedes r2 without rewriting r1 or r2 and grants no authority over generated pixels, untracked user material, acceptance, rights clearance, or production state.",
    }


def render_markdown(record: dict[str, object]) -> str:
    scope = record["scope"]
    summary = record["summary"]
    prior = record["supersedes"]
    lines = [
        "# CH05 overnight safe-source change inventory r3",
        "",
        "R3 supersedes r2 append-only and covers the complete tracked goal range through the clean pushed final owner-review start-page frontier. Generated pixels and persistent untracked user files remain excluded.",
        "",
        "## Pinned range and lineage",
        "",
        f"- First goal commit: `{scope['first_goal_commit']}`.",
        f"- Base: `{scope['range_base_parent']}` (the first goal commit's parent).",
        f"- Head: `{scope['range_head']}`.",
        f"- Revision range: `{scope['revision_range']}`.",
        f"- Commits: {summary['commit_count']} total; {summary['post_r2_commits']} after r2's `{R2_HEAD}` capture.",
        f"- Changed tracked files: {summary['changed_tracked_files']}; status `{json.dumps(summary['status_counts'], sort_keys=True)}`.",
        f"- Prohibited/generated tracked paths: {summary['prohibited_or_generated_tracked_paths']}.",
        f"- Prior JSON: `{prior['record']['path']}` SHA-256 `{prior['record']['blob_sha256']}`.",
        f"- Prior Markdown: `{prior['owner_readable_inventory']['path']}` SHA-256 `{prior['owner_readable_inventory']['blob_sha256']}`.",
        "",
        "## Counts by category",
        "",
        "| Category | Files | Status counts |",
        "| --- | ---: | --- |",
    ]
    for group in record["groups"]:
        lines.append(
            f"| `{group['category']}` | {group['count']} | `{json.dumps(group['status_counts'], sort_keys=True)}` |"
        )
    lines.extend(
        [
            "",
            "## Included commits",
            "",
            "| # | Commit | Authored | Subject |",
            "| ---: | --- | --- | --- |",
        ]
    )
    for index, commit in enumerate(record["commits"], start=1):
        lines.append(
            f"| {index} | `{commit['commit']}` | `{commit['authored_at']}` | {markdown_escape(commit['subject'])} |"
        )
    lines.extend(["", "## Tracked change inventory", ""])
    for group in record["groups"]:
        lines.extend([f"### {group['category']} ({group['count']})", ""])
        for status_group in group["status_groups"]:
            lines.extend(
                [
                    f"#### Status {status_group['status']} ({status_group['count']})",
                    "",
                    "| Path | Current blob SHA-256 | Git blob OID | Mode | Bytes/state |",
                    "| --- | --- | --- | --- | ---: |",
                ]
            )
            for entry in status_group["entries"]:
                if entry["current_state"] == "DELETED_IN_RANGE_HEAD":
                    digest = oid = mode = "deleted"
                    size_or_state = "DELETED_IN_RANGE_HEAD"
                else:
                    digest = f"`{entry['blob_sha256']}`"
                    oid = f"`{entry['git_blob_oid']}`"
                    mode = f"`{entry['git_mode']}`"
                    size_or_state = str(entry["bytes"])
                label = f"`{markdown_escape(entry['path'])}`"
                if entry["previous_path"] is not None:
                    label += f" (from `{markdown_escape(entry['previous_path'])}`)"
                lines.append(
                    f"| {label} | {digest} | {oid} | {mode} | {size_or_state} |"
                )
            lines.append("")
    lines.extend(
        [
            "## Boundary",
            "",
            str(record["boundary"]),
            "",
            "Machine-readable evidence: `docs/research/evidence/ch05-overnight-safe-source-change-inventory-r3.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    record = build_inventory()
    OUTPUT_JSON.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    OUTPUT_MARKDOWN.write_text(render_markdown(record), encoding="utf-8", newline="\n")
    print(
        "CH05 safe-source inventory r3: "
        f"{record['summary']['commit_count']} commits; "
        f"{record['summary']['changed_tracked_files']} files; "
        f"{record['summary']['status_counts']}; "
        f"prohibited={record['summary']['prohibited_or_generated_tracked_paths']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
