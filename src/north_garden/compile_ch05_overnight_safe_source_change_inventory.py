"""Compile the commit-pinned CH05 overnight safe-source change inventory."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIRST_GOAL_COMMIT = "f882b0e5c60d973aac55e2bb16263445662b9c7b"
RANGE_BASE = "7572c7e9a057855dfd34f3a62f6d227b955f02f9"
RANGE_HEAD = "ff1a8c4231b1579f2c41a4bcda9dd14981cdd7fc"
OUTPUT_JSON = (
    ROOT / "docs/research/evidence/ch05-overnight-safe-source-change-inventory-r1.json"
)
OUTPUT_MARKDOWN = (
    ROOT / "docs/research/ch05-overnight-safe-source-change-inventory-r1.md"
)

CATEGORY_ORDER = [
    "goal",
    "architecture_decisions",
    "research_docs",
    "research_evidence",
    "production_comic",
    "source_code",
    "scripts",
    "configuration",
    "other",
]
STATUS_ORDER = ["A", "M", "D", "R", "C", "T", "U", "X", "B"]
PROHIBITED_PREFIXES = (
    "experiments/",
    "output/",
    "models/",
    "loras/",
    "datasets/",
    "refs/",
    "tools/",
)
PROHIBITED_NAMES = {".env"}
PROHIBITED_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
    ".ckpt",
    ".safetensors",
    ".pt",
    ".pth",
    ".onnx",
    ".zip",
    ".tar",
    ".tgz",
    ".7z",
}


def git_bytes(*args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True
    ).stdout


def git_text(*args: str) -> str:
    return git_bytes(*args).decode("utf-8").strip()


def git_is_ancestor(ancestor: str, descendant: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=ROOT,
            check=False,
            capture_output=True,
        ).returncode
        == 0
    )


def category_for(path: str) -> str:
    if path == "GOAL.md":
        return "goal"
    if path.startswith("docs/adr/"):
        return "architecture_decisions"
    if path.startswith("docs/research/evidence/"):
        return "research_evidence"
    if path.startswith("docs/research/"):
        return "research_docs"
    if path.startswith("production/comic/"):
        return "production_comic"
    if path.startswith("src/"):
        return "source_code"
    if path.startswith("scripts/"):
        return "scripts"
    if path.startswith("config/"):
        return "configuration"
    return "other"


def prohibited_reason(path: str) -> str | None:
    lower = path.lower()
    if lower in PROHIBITED_NAMES:
        return "credential_or_environment_file"
    if lower.startswith(PROHIBITED_PREFIXES):
        return "excluded_runtime_generated_or_private_prefix"
    if Path(lower).suffix in PROHIBITED_SUFFIXES:
        return "generated_pixel_model_or_archive_suffix"
    return None


def parse_changes(base: str, head: str) -> list[dict[str, object]]:
    tokens = git_bytes("diff", "--name-status", "-z", "-M", base, head).split(b"\0")
    if tokens and tokens[-1] == b"":
        tokens.pop()
    changes: list[dict[str, object]] = []
    cursor = 0
    while cursor < len(tokens):
        raw_status = tokens[cursor].decode("utf-8")
        cursor += 1
        status = raw_status[0]
        previous_path: str | None = None
        if status in {"R", "C"}:
            previous_path = tokens[cursor].decode("utf-8")
            path = tokens[cursor + 1].decode("utf-8")
            cursor += 2
        else:
            path = tokens[cursor].decode("utf-8")
            cursor += 1
        entry: dict[str, object] = {
            "status": status,
            "raw_status": raw_status,
            "category": category_for(path),
            "path": path,
            "previous_path": previous_path,
        }
        if status == "D":
            entry.update(
                {
                    "current_state": "DELETED_IN_RANGE_HEAD",
                    "blob_sha256": None,
                    "git_blob_oid": None,
                    "git_mode": None,
                    "bytes": None,
                }
            )
        else:
            content = git_bytes("show", f"{head}:{path}")
            tree_line = git_text("ls-tree", head, "--", path)
            metadata, listed_path = tree_line.split("\t", 1)
            mode, object_type, oid = metadata.split(" ", 2)
            if object_type != "blob" or listed_path != path:
                raise ValueError(f"unexpected ls-tree record for {path}: {tree_line}")
            entry.update(
                {
                    "current_state": "PRESENT_AT_RANGE_HEAD",
                    "blob_sha256": hashlib.sha256(content).hexdigest(),
                    "git_blob_oid": oid,
                    "git_mode": mode,
                    "bytes": len(content),
                }
            )
        changes.append(entry)
    return sorted(
        changes,
        key=lambda item: (
            CATEGORY_ORDER.index(str(item["category"])),
            STATUS_ORDER.index(str(item["status"])),
            str(item["path"]),
        ),
    )


def commit_records(base: str, head: str) -> list[dict[str, str]]:
    raw = git_text(
        "log",
        "--reverse",
        "--format=%H%x00%P%x00%aI%x00%s%x1e",
        f"{base}..{head}",
    )
    records: list[dict[str, str]] = []
    for row in raw.split("\x1e"):
        row = row.strip()
        if not row:
            continue
        commit, parents, authored_at, subject = row.split("\x00", 3)
        records.append(
            {
                "commit": commit,
                "parents": parents,
                "authored_at": authored_at,
                "subject": subject,
            }
        )
    return records


def build_inventory() -> dict[str, object]:
    first_parent = git_text("rev-parse", f"{FIRST_GOAL_COMMIT}^")
    if first_parent != RANGE_BASE:
        raise ValueError(f"first-goal parent drift: {first_parent} != {RANGE_BASE}")
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
    grouped: list[dict[str, object]] = []
    for category in CATEGORY_ORDER:
        category_entries = [item for item in changes if item["category"] == category]
        if not category_entries:
            continue
        status_groups = []
        for status in STATUS_ORDER:
            status_entries = [
                item for item in category_entries if item["status"] == status
            ]
            if status_entries:
                status_groups.append(
                    {
                        "status": status,
                        "count": len(status_entries),
                        "entries": status_entries,
                    }
                )
        grouped.append(
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
        "schema_version": "1.0",
        "record_id": "ng-ch05-overnight-safe-source-change-inventory-r1",
        "state": "COMMIT_PINNED_SAFE_SOURCE_INVENTORY_PASS",
        "scope": {
            "first_goal_commit": FIRST_GOAL_COMMIT,
            "range_base_parent": RANGE_BASE,
            "range_head": RANGE_HEAD,
            "revision_range": f"{RANGE_BASE}..{RANGE_HEAD}",
            "base_selection": "Parent of the first overnight-goal commit; the first included commit is f882b0e.",
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
        },
        "commits": commits,
        "groups": grouped,
        "safety": {
            "prohibited_or_generated_tracked_paths": prohibited,
            "persistent_untracked_user_files_touched": 0,
            "interpretation": "The inventory is derived only from committed tracked paths in the pinned range. Working-tree and ignored/untracked files are outside the enumerated set.",
        },
        "generated_by": "src/north_garden/compile_ch05_overnight_safe_source_change_inventory.py",
        "validated_by": "src/north_garden/validate_ch05_overnight_safe_source_change_inventory.py",
        "boundary": "Source/evidence inventory only. It does not include generated pixels, untracked user material, acceptance, rights clearance, or production authority.",
    }


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|")


def render_markdown(record: dict[str, object]) -> str:
    scope = record["scope"]
    summary = record["summary"]
    lines = [
        "# CH05 overnight safe-source change inventory r1",
        "",
        "This inventory covers committed tracked source/evidence only. Generated pixels and persistent untracked user files are excluded.",
        "",
        "## Pinned range",
        "",
        f"- First goal commit: `{scope['first_goal_commit']}`.",
        f"- Base: `{scope['range_base_parent']}` (the first goal commit's parent).",
        f"- Head: `{scope['range_head']}`.",
        f"- Revision range: `{scope['revision_range']}`.",
        f"- Commits: {summary['commit_count']}; changed tracked files: {summary['changed_tracked_files']}.",
        f"- Status: `{json.dumps(summary['status_counts'], sort_keys=True)}`.",
        f"- Prohibited/generated tracked paths: {summary['prohibited_or_generated_tracked_paths']}.",
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
                    "| Path | Current blob SHA-256 | Git blob OID | Bytes/state |",
                    "| --- | --- | --- | ---: |",
                ]
            )
            for entry in status_group["entries"]:
                if entry["current_state"] == "DELETED_IN_RANGE_HEAD":
                    digest = "deleted"
                    oid = "deleted"
                    size_or_state = "DELETED_IN_RANGE_HEAD"
                else:
                    digest = f"`{entry['blob_sha256']}`"
                    oid = f"`{entry['git_blob_oid']}`"
                    size_or_state = str(entry["bytes"])
                path_label = f"`{markdown_escape(entry['path'])}`"
                if entry["previous_path"] is not None:
                    path_label += f" (from `{markdown_escape(entry['previous_path'])}`)"
                lines.append(f"| {path_label} | {digest} | {oid} | {size_or_state} |")
            lines.append("")
    lines.extend(
        [
            "## Boundary",
            "",
            str(record["boundary"]),
            "",
            "Machine-readable evidence: `docs/research/evidence/ch05-overnight-safe-source-change-inventory-r1.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    record = build_inventory()
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    OUTPUT_MARKDOWN.write_text(render_markdown(record), encoding="utf-8", newline="\n")
    print(
        "CH05 overnight safe-source inventory: "
        f"{record['summary']['commit_count']} commits; "
        f"{record['summary']['changed_tracked_files']} files; "
        f"{record['summary']['status_counts']}; "
        f"prohibited={record['summary']['prohibited_or_generated_tracked_paths']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
