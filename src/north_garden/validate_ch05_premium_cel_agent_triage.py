"""Validate the full CH05 premium-cel non-gating agent triage."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/research/evidence/ch05-complete-chapter-premium-cel-agent-triage-r1.json"
MARKDOWN = ROOT / "docs/research/ch05-complete-chapter-premium-cel-agent-triage-r1.md"
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-assembly-r1.json"
WARN_ORDERS = [3, 8, 12, 32, 45]
FAIL_ORDERS = [1, 13, 29, 36, 39]
STRONGEST_ORDERS = [4, 6, 17, 19, 20, 22, 26, 30, 33, 41, 43, 44, 46, 48, 49, 50]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(document: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(document.get("record_type") == "CH05CompleteChapterAgentTriage", "record_type")
    check(document.get("record_id") == "ng-ch05-complete-chapter-premium-cel-agent-triage-r1", "record_id")
    check(document.get("state") == "NON_GATING_AGENT_TRIAGE_PENDING_OWNER_REVIEW", "state")
    check(
        document.get("planning_structure") == "ComicPanelPlan"
        and document.get("animation_shot_plan") is None
        and document.get("e_conte") is None,
        "planning boundary",
    )
    plans = sorted(json.loads(PLAN.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    entries = sorted(assembly["entries"], key=lambda row: row["order"])
    rows = document.get("rows", [])
    check(
        len(rows) == 50
        and [row.get("panel_id") for row in rows] == [row["panel_id"] for row in plans] == [row["panel_id"] for row in entries],
        "canonical coverage",
    )
    counts = {status: sum(row.get("status") == status for row in rows) for status in ("PASS", "WARN", "FAIL")}
    check(counts == {"PASS": 40, "WARN": 5, "FAIL": 5}, "40/5/5 counts")
    check([row["display_order"] for row in rows if row.get("status") == "WARN"] == WARN_ORDERS, "warning set")
    check([row["display_order"] for row in rows if row.get("status") == "FAIL"] == FAIL_ORDERS, "failure set")
    expected_issues = {
        3: "track_overlap",
        8: "map_fold_state",
        12: "twine_direction",
        32: "far_bank_footprint_orientation",
        45: "farmhouse_geography",
        1: "departure_vector",
        13: "role_order",
        29: "independent_exterior_watch",
        36: "continuous_leverage_force_path",
        39: "simultaneous_three_mark_count",
    }
    check(
        all(rows[order - 1].get("primary_issue_class") == issue for order, issue in expected_issues.items()),
        "exact issue classes",
    )
    summary = document.get("summary", {})
    check(
        summary
        == {
            "chapter_panels": 50,
            "pass": 40,
            "warn": 5,
            "fail": 5,
            "hair_and_wardrobe_pass": 50,
            "role_correct_hair_and_wardrobe_pass": 50,
            "cross_panel_gates_pass": 3,
            "cross_panel_gates_warn": 1,
            "cross_panel_gates_fail": 4,
            "strongest_shortlist": 16,
            "human_reviewed": 0,
            "accepted": 0,
        },
        "summary",
    )
    role = document.get("role_continuity", {})
    check(
        role.get("result") == "PASS_50_OF_50"
        and "light-brown/dark-blond" in role.get("SOREN", "")
        and "oatmeal" in role.get("SOREN", "")
        and "dark-brown/near-black" in role.get("SIGRID", "")
        and "plaid" in role.get("SIGRID", ""),
        "role-correct hair/wardrobe",
    )
    check(all(row.get("checks", {}).get("hair_and_wardrobe") == "PASS" for row in rows), "row hair/wardrobe")
    check(
        document.get("gate_transfer")
        == {
            "cold_farmhouse_until_reversal": "PASS",
            "departure_vector": "FAIL",
            "independent_entry_roles": "FAIL",
            "impossible_far_bank_prints": "WARN",
            "continuous_leverage_force_path": "FAIL",
            "third_upstream_mark": "FAIL_STRICT_SIMULTANEOUS_COUNT",
            "drum_fully_out": "PASS",
            "map_possession": "PASS",
        },
        "gate transfer",
    )
    style = document.get("style_hypothesis_result", {})
    check(
        style.get("result") == "WEAKLY_SEPARATING"
        and "high" in style.get("note", "")
        and "s08" in style.get("largest_discontinuity", "")
        and "P035-P039" in style.get("largest_discontinuity", ""),
        "style result/discontinuity",
    )
    strongest = document.get("strongest_shortlist", [])
    check([row.get("display_order") for row in strongest] == STRONGEST_ORDERS, "strongest shortlist")
    check(all(row.get("status") == "PASS" for row in strongest), "strongest status")
    if len(rows) == 50:
        check(
            all(
                row.get("human_review_state") == "PENDING"
                and row.get("human_review_minutes") is None
                and row.get("accepted") is False
                and row.get("commercially_cleared") is False
                and row.get("exact_production_base") is False
                for row in rows
            ),
            "owner/promotion boundary",
        )
        check(
            all(
                row.get("candidate_id") == entries[index]["candidate_id"]
                and row.get("candidate_sha256") == entries[index]["source"]["sha256"]
                and row.get("plan_revision_id") == plans[index]["plan_revision_id"]
                for index, row in enumerate(rows)
            ),
            "row bindings",
        )
    expected_inputs = [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in (PLAN, ASSEMBLY)
    ]
    check(document.get("inputs") == expected_inputs, "input list")
    check("Do not promote" in document.get("recommendation", ""), "recommendation boundary")
    sheet = document.get("triage_sheet", {})
    check(
        isinstance(sheet.get("sha256"), str)
        and len(sheet.get("sha256")) == 64
        and sheet.get("sha256") != "0" * 64
        and sheet.get("tracked") is False,
        "triage sheet metadata",
    )
    if verify_files:
        for source in document.get("inputs", []):
            path = ROOT / source.get("path", "")
            check(path.is_file() and sha256(path) == source.get("sha256"), f"input:{source.get('path')}")
        sheet_path = ROOT / sheet.get("path", "")
        check(
            sheet_path.is_file()
            and sha256(sheet_path) == sheet.get("sha256")
            and sheet.get("width") == 1604
            and sheet.get("height") == 2802
            and sheet.get("bytes") == sheet_path.stat().st_size,
            "triage sheet binding",
        )
        check(
            subprocess.run(["git", "check-ignore", "-q", str(sheet_path)], cwd=ROOT, check=False).returncode == 0
            and sheet.get("tracked") is False,
            "triage sheet ignored",
        )
        check(MARKDOWN.is_file() and "40 PASS / 5 WARN / 5 FAIL" in MARKDOWN.read_text(encoding="utf-8"), "markdown")
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "ACCEPTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("e_conte", {}),
        lambda value: value["rows"].pop(),
        lambda value: value["rows"][2].__setitem__("status", "PASS"),
        lambda value: value["rows"][0].__setitem__("status", "WARN"),
        lambda value: value["rows"][12].__setitem__("primary_issue_class", "wrong"),
        lambda value: value["rows"][0]["checks"].__setitem__("hair_and_wardrobe", "FAIL"),
        lambda value: value["rows"][0].__setitem__("accepted", True),
        lambda value: value["summary"].__setitem__("hair_and_wardrobe_pass", 49),
        lambda value: value["summary"].__setitem__("cross_panel_gates_pass", 4),
        lambda value: value["role_continuity"].__setitem__("SOREN", "black hair"),
        lambda value: value["gate_transfer"].__setitem__("departure_vector", "PASS"),
        lambda value: value["style_hypothesis_result"].__setitem__("result", "WINNER"),
        lambda value: value["style_hypothesis_result"].__setitem__("largest_discontinuity", "none"),
        lambda value: value["strongest_shortlist"].pop(),
        lambda value: value["triage_sheet"].__setitem__("sha256", "0" * 64),
        lambda value: value.__setitem__("recommendation", "Promote wholesale"),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = json.loads(DOC.read_text(encoding="utf-8"))
    errors = validate(document)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(document)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
                "counts": {key: document.get("summary", {}).get(key) for key in ("pass", "warn", "fail")},
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
