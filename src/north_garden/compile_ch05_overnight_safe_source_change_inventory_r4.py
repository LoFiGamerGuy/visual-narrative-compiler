"""Compile final append-only CH05 overnight safe-source inventory r4."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import compile_ch05_overnight_safe_source_change_inventory_r3 as r3

ROOT = Path(__file__).resolve().parents[2]
RANGE_BASE = "7572c7e9a057855dfd34f3a62f6d227b955f02f9"
RANGE_HEAD = "861847ef066037820b77be3f60c30a2b6fc161d0"
R3_HEAD = "ac5529a4621d4d73e9dea60a70fb515c4213caf3"
FIRST_GOAL_COMMIT = r3.FIRST_GOAL_COMMIT
OUTPUT_JSON = (
    ROOT / "docs/research/evidence/ch05-overnight-safe-source-change-inventory-r4.json"
)
OUTPUT_MARKDOWN = (
    ROOT / "docs/research/ch05-overnight-safe-source-change-inventory-r4.md"
)

TERMINAL_EVIDENCE = {
    "safe_source_frontier": "12e553e3f31a4decfa4e63a217e6d399074d7b04",
    "terminal_audit_release_gate": "75545b2050ccfc66cbb4f96b8d9c6fff3c37adde",
    "terminal_owner_handoff": "20650b204e2ef5478542bb58212f6365d7e4636a",
    "owner_response_template": "05c1a28b61f92969ed85007fbaf93761804dde7f",
    "owner_response_contract": "861847ef066037820b77be3f60c30a2b6fc161d0",
}


def _configure_engine() -> None:
    r3.RANGE_BASE = RANGE_BASE
    r3.RANGE_HEAD = RANGE_HEAD
    r3.R2_HEAD = R3_HEAD
    r3.PRIOR_JSON = (
        "docs/research/evidence/ch05-overnight-safe-source-change-inventory-r3.json"
    )
    r3.PRIOR_MARKDOWN = (
        "docs/research/ch05-overnight-safe-source-change-inventory-r3.md"
    )


def build_inventory() -> dict[str, object]:
    _configure_engine()
    record = r3.build_inventory()
    record["schema_version"] = "4.0"
    record["record_id"] = "ng-ch05-overnight-safe-source-change-inventory-r4"
    record["state"] = "TERMINAL_COMMIT_PINNED_SAFE_SOURCE_INVENTORY_PASS"
    record["supersedes"]["lineage"] = ["r1", "r2", "r3", "r4"]
    record["scope"]["head_selection"] = (
        "Clean pushed main/origin-main frontier containing the terminal audit, "
        "owner handoff, and owner-response contract."
    )
    record["summary"]["post_r3_commits"] = record["summary"].pop("post_r2_commits")
    record["terminal_evidence_commits"] = TERMINAL_EVIDENCE
    record["generated_by"] = (
        "src/north_garden/compile_ch05_overnight_safe_source_change_inventory_r4.py"
    )
    record["validated_by"] = (
        "src/north_garden/validate_ch05_overnight_safe_source_change_inventory_r4.py"
    )
    record["boundary"] = (
        "Terminal append-only source/evidence inventory. It supersedes r3 without "
        "rewriting r1, r2, or r3 and grants no authority over generated pixels, "
        "untracked user material, acceptance, rights clearance, or production state."
    )
    return record


def render_markdown(record: dict[str, object]) -> str:
    render_record = copy.deepcopy(record)
    render_record["summary"]["post_r2_commits"] = render_record["summary"][
        "post_r3_commits"
    ]
    rendered = r3.render_markdown(render_record)
    rendered = rendered.replace(
        "# CH05 overnight safe-source change inventory r3",
        "# CH05 overnight safe-source change inventory r4",
        1,
    )
    rendered = rendered.replace(
        "R3 supersedes r2 append-only and covers the complete tracked goal range "
        "through the clean pushed final owner-review start-page frontier. Generated "
        "pixels and persistent untracked user files remain excluded.",
        "R4 supersedes r3 append-only and covers the complete tracked goal range "
        "through the clean pushed terminal-audit and owner-response-contract frontier. "
        "Generated pixels and persistent untracked user files remain excluded.",
        1,
    )
    rendered = rendered.replace(" after r2's `", " after r3's `", 1)
    rendered = rendered.replace(
        "ch05-overnight-safe-source-change-inventory-r3.json`.",
        "ch05-overnight-safe-source-change-inventory-r4.json`.",
        1,
    )
    terminal_lines = [
        "## Terminal evidence commits",
        "",
        "| Evidence | Commit |",
        "| --- | --- |",
        *[
            f"| `{name}` | `{commit}` |"
            for name, commit in record["terminal_evidence_commits"].items()
        ],
        "",
    ]
    return rendered.replace(
        "## Tracked change inventory\n",
        "\n".join(terminal_lines) + "## Tracked change inventory\n",
        1,
    )


def main() -> int:
    record = build_inventory()
    OUTPUT_JSON.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    OUTPUT_MARKDOWN.write_text(render_markdown(record), encoding="utf-8", newline="\n")
    print(
        "CH05 safe-source inventory r4: "
        f"{record['summary']['commit_count']} commits; "
        f"{record['summary']['changed_tracked_files']} files; "
        f"{record['summary']['status_counts']}; "
        f"prohibited={record['summary']['prohibited_or_generated_tracked_paths']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
