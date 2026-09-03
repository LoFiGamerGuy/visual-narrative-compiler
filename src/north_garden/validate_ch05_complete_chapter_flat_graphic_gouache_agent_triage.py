"""Validate the full CH05 flat-gouache non-gating agent triage."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/research/evidence/ch05-complete-chapter-flat-graphic-gouache-agent-triage-r1.json"
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-assembly-r1.json"
SEMANTIC_WARN = [3, 8, 12, 32, 33, 39]
SEMANTIC_FAIL = [1, 9, 43]
LETTERING_WARN = [3, 11, 16, 21, 26, 42]
LETTERING_FAIL = [2, 4, 5, 7, 8, 12, 13, 15, 17, 18, 19, 24, 25, 27, 29, 31, 33, 34, 37, 38, 39, 43, 44, 49, 50]
PHONE_WARN = [3, 12, 18, 24, 27, 32, 33]
OVERALL_WARN = [3, 11, 16, 21, 26, 32, 42]
OVERALL_FAIL = [1, 2, 4, 5, 7, 8, 9, 12, 13, 15, 17, 18, 19, 24, 25, 27, 29, 31, 33, 34, 37, 38, 39, 43, 44, 49, 50]
STRONGEST = [6, 10, 14, 20, 22, 23, 28, 30, 35, 36, 40, 41, 45, 46, 47, 48]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(document: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(document.get("record_type") == "CH05CompleteChapterAgentTriage", "record_type")
    check(document.get("record_id") == "ng-ch05-complete-chapter-flat-graphic-gouache-agent-triage-r1", "record_id")
    check(document.get("state") == "NON_GATING_AGENT_TRIAGE_PENDING_OWNER_REVIEW", "state")
    check(document.get("planning_structure") == "ComicPanelPlan" and document.get("animation_shot_plan") is None and document.get("e_conte") is None, "planning boundary")
    plans = sorted(json.loads(PLAN.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    entries = sorted(assembly["entries"], key=lambda row: row["order"])
    rows = document.get("rows", [])
    check(len(rows) == 50 and [row.get("panel_id") for row in rows] == [row["panel_id"] for row in plans] == [row["panel_id"] for row in entries], "canonical coverage")
    if len(rows) == 50:
        check([row["display_order"] for row in rows if row.get("semantic_status") == "WARN"] == SEMANTIC_WARN, "semantic warning set")
        check([row["display_order"] for row in rows if row.get("semantic_status") == "FAIL"] == SEMANTIC_FAIL, "semantic failure set")
        check([row["display_order"] for row in rows if row.get("checks", {}).get("lettering_clearance") == "WARN"] == LETTERING_WARN, "lettering warning set")
        check([row["display_order"] for row in rows if row.get("checks", {}).get("lettering_clearance") == "FAIL"] == LETTERING_FAIL, "lettering failure set")
        check([row["display_order"] for row in rows if row.get("checks", {}).get("phone_readability") == "WARN"] == PHONE_WARN, "phone warning set")
        check([row["display_order"] for row in rows if row.get("status") == "WARN"] == OVERALL_WARN, "overall warning set")
        check([row["display_order"] for row in rows if row.get("status") == "FAIL"] == OVERALL_FAIL, "overall failure set")
        check(all(row.get("style_density_compliance") == "FAIL_STRICT" and "4-6 broad-mass" in row.get("style_density_note", "") for row in rows), "strict density rows")
        check(all(row.get("checks", {}).get("hair_and_wardrobe") == "PASS" and row.get("hair_and_wardrobe_observation") for row in rows), "hair/wardrobe rows")
        check(all(row.get("human_review_state") == "PENDING" and row.get("human_review_minutes") is None and row.get("accepted") is False and row.get("commercially_cleared") is False and row.get("exact_production_base") is False for row in rows), "owner/promotion boundary")
        check(all(row.get("candidate_id") == entries[index]["candidate_id"] and row.get("candidate_sha256") == entries[index]["source"]["sha256"] and row.get("plan_revision_id") == plans[index]["plan_revision_id"] for index, row in enumerate(rows)), "row bindings")
    summary = document.get("summary", {})
    check(summary == {
        "chapter_panels": 50, "pass": 16, "warn": 7, "fail": 27,
        "semantic_pass": 41, "semantic_warn": 6, "semantic_fail": 3,
        "lettering_pass": 19, "lettering_warn": 6, "lettering_fail": 25,
        "phone_pass": 43, "phone_warn": 7, "phone_fail": 0,
        "style_density_pass": 0, "style_density_warn": 0, "style_density_fail_strict": 50,
        "hair_and_wardrobe_pass": 50, "role_correct_hair_and_wardrobe_pass": 50,
        "cross_panel_gates_pass": 3, "cross_panel_gates_warn": 2, "cross_panel_gates_fail": 3,
        "strongest_shortlist": 16, "human_reviewed": 0, "accepted": 0,
    }, "summary")
    check(document.get("role_continuity", {}).get("result") == "PASS_50_OF_50_WITH_PLANNED_PARTIAL_INSERTS", "role continuity result")
    check(document.get("gate_transfer") == {
        "cold_farmhouse_until_reversal": "FAIL_P001_PREMATURE_SMOKE",
        "departure_vector": "FAIL_P001_UPHILL_TOWARD_HOUSE",
        "independent_entry_roles": "PASS",
        "impossible_far_bank_prints": "WARN_ORIENTATION_AMBIGUOUS",
        "continuous_leverage_force_path": "PASS",
        "third_upstream_mark": "WARN_DISTINCT_IDENTITY_AND_TORN_EDGE_AMBIGUOUS",
        "drum_fully_out": "PASS",
        "map_possession": "FAIL_P043_MAP_LEFT_WITH_TIN",
    }, "gate transfer")
    check(document.get("style_hypothesis_result", {}).get("result") == "FAIL_STRICT_DENSITY_0_OF_50", "style result")
    strongest = document.get("strongest_shortlist", [])
    check([row.get("display_order") for row in strongest] == STRONGEST and all(row.get("status") == "PASS" for row in strongest), "strongest shortlist")
    check(document.get("inspection_basis", {}).get("phone_scale", "").startswith("All 50"), "phone inspection basis")
    expected_inputs = [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in (PLAN, ASSEMBLY)]
    check(document.get("inputs") == expected_inputs, "input list")
    check("Do not promote" in document.get("recommendation", ""), "recommendation boundary")
    sheet = document.get("triage_sheet", {})
    check(isinstance(sheet.get("sha256"), str) and len(sheet.get("sha256")) == 64 and sheet.get("sha256") != "0" * 64 and sheet.get("tracked") is False, "triage sheet metadata")
    if verify_files:
        for source in expected_inputs:
            path = ROOT / source["path"]
            check(path.is_file() and sha256(path) == source["sha256"], f"input:{source['path']}")
        sheet_path = ROOT / sheet.get("path", "")
        check(sheet_path.is_file() and sha256(sheet_path) == sheet.get("sha256") and sheet.get("width") == 1604 and sheet.get("height") == 2802 and sheet.get("bytes") == sheet_path.stat().st_size, "triage sheet binding")
        check(subprocess.run(["git", "check-ignore", "-q", str(sheet_path)], cwd=ROOT, check=False).returncode == 0 and sheet.get("tracked") is False, "triage sheet ignored")
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "ACCEPTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("e_conte", {}),
        lambda value: value["rows"].pop(),
        lambda value: value["rows"][0].__setitem__("semantic_status", "PASS"),
        lambda value: value["rows"][1]["checks"].__setitem__("lettering_clearance", "PASS"),
        lambda value: value["rows"][2]["checks"].__setitem__("phone_readability", "PASS"),
        lambda value: value["rows"][5].__setitem__("status", "FAIL"),
        lambda value: value["rows"][0].__setitem__("style_density_compliance", "PASS"),
        lambda value: value["rows"][0]["checks"].__setitem__("hair_and_wardrobe", "FAIL"),
        lambda value: value["rows"][0].__setitem__("accepted", True),
        lambda value: value["summary"].__setitem__("lettering_fail", 24),
        lambda value: value["summary"].__setitem__("style_density_fail_strict", 49),
        lambda value: value["gate_transfer"].__setitem__("map_possession", "PASS"),
        lambda value: value["style_hypothesis_result"].__setitem__("result", "WINNER"),
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
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "counts": {key: document.get("summary", {}).get(key) for key in ("pass", "warn", "fail")}, "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
