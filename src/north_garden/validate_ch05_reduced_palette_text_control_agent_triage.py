"""Validate CH05 reduced-palette text-control non-gating agent triage."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/research/evidence/ch05-complete-chapter-reduced-palette-text-control-agent-triage-r1.json"
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
PROMPT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-prompt-manifest-r1.json"
EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-execution-manifest-r1.json"
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-assembly-r1.json"
BUILD_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/review/build-report.json"
SEMANTIC_WARN = [3, 12, 32, 44]
SEMANTIC_FAIL = [8, 36, 50]
LETTERING_WARN = [7, 11, 13, 16, 21, 22]
LETTERING_FAIL = [4, 5, 9, 12, 15, 17, 18, 19, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39, 42, 43, 48, 49, 50]
PHONE_WARN = [3, 12, 25, 26, 32, 37, 44]
STYLE_PASS = [10, 11, 14, 21, 22, 25, 35, 40, 41, 44, 46, 48]
STYLE_WARN = [2, 4, 8, 16, 18, 26, 28]
OVERALL_PASS = [10, 14, 35, 40, 41, 46]
OVERALL_WARN = [2, 11, 16, 21, 22, 44]
STRONGEST = OVERALL_PASS
CHECK_KEYS = {
    "role_binding",
    "role_order",
    "visible_adult_count",
    "shared_set_and_blocking",
    "target_change_behavior",
    "causal_action_or_clue",
    "hair_and_wardrobe",
    "mature_fictional_adult",
    "lettering_clearance",
    "phone_readability",
    "cross_panel_canon",
    "strict_3_to_5_mass_style",
}
EXPECTED_SUMMARY = {
    "chapter_panels": 50,
    "overall_pass": 6,
    "overall_warn": 6,
    "overall_fail": 38,
    "semantic_pass": 43,
    "semantic_warn": 4,
    "semantic_fail": 3,
    "lettering_pass": 17,
    "lettering_warn": 6,
    "lettering_fail": 27,
    "phone_pass": 43,
    "phone_warn": 7,
    "phone_fail": 0,
    "style_pass": 12,
    "style_warn": 7,
    "style_fail": 31,
    "strict_style_compliance_rate": 0.24,
    "visible_adult_cast_panels": 32,
    "mature_identity_hair_wardrobe_pass": 32,
    "zero_cast_panels_without_people": 18,
    "strongest_shortlist": 6,
    "human_reviewed": 0,
    "accepted": 0,
}
EXPECTED_GATES = {
    "cold_farmhouse_until_reversal": "PASS",
    "departure_vector": "PASS",
    "independent_entry_roles": "PASS",
    "near_bank_prints_stop": "PASS",
    "far_bank_prints_face_back": "WARN_ORIENTATION_AMBIGUOUS",
    "tin_high_on_beam": "PASS",
    "continuous_leverage_force_path": "FAIL_TWO_DISCONNECTED_PLANKS",
    "same_tin_open_beside_retained_map": "PASS",
    "third_upstream_mark_at_torn_edge": "PASS",
    "drum_fully_out": "PASS",
    "map_retained_during_retreat": "PASS",
    "same_map_hidden_under_wrap": "PASS",
    "first_new_farmhouse_smoke": "PASS",
    "stove_not_lit_before_departure": "PASS_VISUAL_REALIZATION",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ignored_untracked(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    ignored = subprocess.run(
        ["git", "check-ignore", "--quiet", "--", relative], cwd=ROOT, check=False
    ).returncode == 0
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", relative],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0
    return ignored and not tracked


def artifact_nodes(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
            yield value
        for child in value.values():
            yield from artifact_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from artifact_nodes(child)


def status_orders(rows: list[dict[str, Any]], field: str, status: str) -> list[int]:
    return [row.get("display_order") for row in rows if row.get(field) == status]


def validate(document: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(document.get("record_type") == "CH05CompleteChapterReducedPaletteTextControlAgentTriage", "record_type")
    check(document.get("schema_version") == "1.0", "schema_version")
    check(document.get("record_id") == "ng-ch05-complete-chapter-reduced-palette-text-control-agent-triage-r1", "record_id")
    check(document.get("state") == "NON_GATING_AGENT_TRIAGE_PENDING_OWNER_REVIEW", "state")
    check(document.get("medium") == "comic", "medium")
    check(document.get("planning_structure") == "ComicPanelPlan" and document.get("animation_shot_plan") is None and document.get("e_conte") is None, "planning boundary")

    plans = sorted(json.loads(PLAN.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    entries = sorted(json.loads(ASSEMBLY.read_text(encoding="utf-8"))["entries"], key=lambda row: row["order"])
    build_report = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    rows = document.get("rows", [])
    check(len(rows) == 50, "row denominator")
    if len(rows) == 50:
        check([row.get("panel_id") for row in rows] == [row["panel_id"] for row in plans] == [row["panel_id"] for row in entries], "canonical panel order")
        check([row.get("display_order") for row in rows] == list(range(1, 51)), "display order")
        check(status_orders(rows, "semantic_status", "WARN") == SEMANTIC_WARN, "semantic warning set")
        check(status_orders(rows, "semantic_status", "FAIL") == SEMANTIC_FAIL, "semantic failure set")
        check(status_orders(rows, "lettering_status", "WARN") == LETTERING_WARN, "lettering warning set")
        check(status_orders(rows, "lettering_status", "FAIL") == LETTERING_FAIL, "lettering failure set")
        check(status_orders(rows, "phone_status", "WARN") == PHONE_WARN, "phone warning set")
        check(status_orders(rows, "style_status", "PASS") == STYLE_PASS, "style pass set")
        check(status_orders(rows, "style_status", "WARN") == STYLE_WARN, "style warning set")
        check(status_orders(rows, "status", "PASS") == OVERALL_PASS, "overall pass set")
        check(status_orders(rows, "status", "WARN") == OVERALL_WARN, "overall warning set")
        status_fields = (
            "status",
            "semantic_status",
            "lettering_status",
            "phone_status",
            "style_status",
        )
        check(
            all(
                row.get(field) in {"PASS", "WARN", "FAIL"}
                for row in rows
                for field in status_fields
            ),
            "status vocabulary",
        )
        rank = {"PASS": 0, "WARN": 1, "FAIL": 2}
        check(
            all(
                row["status"]
                == max(
                    (
                        row["semantic_status"],
                        row["lettering_status"],
                        row["phone_status"],
                        row["style_status"],
                    ),
                    key=lambda value: rank.get(value, -1),
                )
                for row in rows
            ),
            "overall status arithmetic",
        )
        check(all(row.get("style_status") in {"PASS", "WARN", "FAIL"} and "strict 3-5" in row.get("style_note", "") and row.get("dominant_mass_assessment") for row in rows), "strict style rows")
        check(all(row.get("semantic_note") and row.get("lettering_note") and row.get("phone_note") and row.get("mature_identity_hair_wardrobe_note") for row in rows), "observation notes")
        check(
            all(
                set(row.get("checks", {})) == CHECK_KEYS
                and all(value in {"PASS", "WARN", "FAIL"} for value in row["checks"].values())
                and row["checks"]["mature_fictional_adult"] == "PASS"
                and row["checks"]["hair_and_wardrobe"] == "PASS"
                and row["checks"]["lettering_clearance"] == row["lettering_status"]
                and row["checks"]["phone_readability"] == row["phone_status"]
                and row["checks"]["strict_3_to_5_mass_style"] == row["style_status"]
                for row in rows
            ),
            "check matrix bindings",
        )
        check(all(row.get("human_review_state") == "PENDING" and row.get("human_review_minutes") is None and row.get("accepted") is False and row.get("rights_cleared") is False and row.get("commercially_cleared") is False and row.get("exact_production_base") is False for row in rows), "no review or rights promotion")
        check(all(row.get("candidate_id") == entries[index]["candidate_id"] and row.get("candidate_sha256") == entries[index]["source"]["sha256"] and row.get("native_dimensions") == {"width": entries[index]["source"]["width"], "height": entries[index]["source"]["height"]} and row.get("plan_revision_id") == plans[index]["plan_revision_id"] and row.get("narrative_beat") == plans[index]["narrative_beat"] for index, row in enumerate(rows)), "row source/plan bindings")

    summary = document.get("summary", {})
    check(summary == EXPECTED_SUMMARY, "summary")
    if len(rows) == 50:
        check(
            all(
                summary.get(f"{prefix}_{status.lower()}")
                == sum(row[field] == status for row in rows)
                for prefix, field in (
                    ("overall", "status"),
                    ("semantic", "semantic_status"),
                    ("lettering", "lettering_status"),
                    ("phone", "phone_status"),
                    ("style", "style_status"),
                )
                for status in ("PASS", "WARN", "FAIL")
            ),
            "summary derived status counts",
        )
    check([row.get("panel") for row in document.get("semantic_failures", [])] == SEMANTIC_FAIL, "failure digest")
    check([row.get("panel") for row in document.get("semantic_warnings", [])] == SEMANTIC_WARN, "warning digest")
    check(document.get("gate_transfer") == EXPECTED_GATES, "cross-panel gate transfer")
    continuity = document.get("continuity_result", {})
    check(continuity.get("result") == "PASS_32_OF_32_VISIBLE_CAST_PANELS" and "fictional-character" in continuity.get("note", ""), "continuity result")
    style = document.get("style_hypothesis_result", {})
    check(style.get("result") == "PARTIAL_STRICT_COMPLIANCE_12_OF_50" and style.get("pass_rate") == 0.24 and style.get("pass_panels") == STYLE_PASS and style.get("warn_panels") == STYLE_WARN, "style hypothesis result")
    strongest = document.get("strongest_shortlist", [])
    check([row.get("display_order") for row in strongest] == STRONGEST and all(row.get("status") == "PASS" for row in strongest), "strongest shortlist")

    input_paths = (PLAN, PROMPT, EXECUTION, ASSEMBLY, BUILD_REPORT)
    expected_inputs = [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in input_paths]
    check(document.get("inputs") == expected_inputs, "input bindings")
    check(document.get("inspection_artifacts") == build_report.get("artifacts"), "review artifact manifest binding")
    basis = document.get("inspection_basis", {})
    check(basis.get("native_pixels", "").startswith("All 50") and basis.get("phone_scale", "").startswith("All ten") and basis.get("lettering", "").startswith("All 50") and "not an automated" in basis.get("style", ""), "inspection basis")
    check("Do not promote or accept" in document.get("recommendation", ""), "recommendation boundary")
    check("no acceptance" in document.get("boundary", ""), "document boundary")

    sheet = document.get("triage_sheet", {})
    check(sheet.get("tracked") is False and isinstance(sheet.get("sha256"), str) and len(sheet.get("sha256")) == 64 and sheet.get("sha256") != "0" * 64, "triage sheet metadata")
    if verify_files:
        for item in expected_inputs:
            path = ROOT / item["path"]
            check(path.is_file() and sha256(path) == item["sha256"], f"input file:{item['path']}")
        for artifact in artifact_nodes(document.get("inspection_artifacts")):
            path = ROOT / artifact["path"]
            good = path.is_file() and sha256(path) == artifact["sha256"] and ignored_untracked(path)
            if good and "width" in artifact and "height" in artifact:
                try:
                    with Image.open(path) as image:
                        good = image.width == artifact["width"] and image.height == artifact["height"]
                except OSError:
                    good = False
            check(good, f"ignored review artifact:{artifact['path']}")
        sheet_path = ROOT / sheet.get("path", "")
        sheet_good = sheet_path.is_file() and sha256(sheet_path) == sheet.get("sha256") and ignored_untracked(sheet_path) and sheet.get("bytes") == sheet_path.stat().st_size
        if sheet_good:
            with Image.open(sheet_path) as image:
                sheet_good = image.width == sheet.get("width") == 1604 and image.height == sheet.get("height") == 2952
        check(sheet_good, "ignored triage sheet binding")
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "ACCEPTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("e_conte", {}),
        lambda value: value["rows"].pop(),
        lambda value: value["rows"][7].__setitem__("semantic_status", "PASS"),
        lambda value: value["rows"][3].__setitem__("lettering_status", "PASS"),
        lambda value: value["rows"][2].__setitem__("phone_status", "PASS"),
        lambda value: value["rows"][9].__setitem__("style_status", "FAIL"),
        lambda value: value["rows"][9].__setitem__("status", "FAIL"),
        lambda value: value["rows"][0]["checks"].__setitem__("mature_fictional_adult", "FAIL"),
        lambda value: value["rows"][0].__setitem__("accepted", True),
        lambda value: value["rows"][0].__setitem__("rights_cleared", True),
        lambda value: value["summary"].__setitem__("semantic_pass", 44),
        lambda value: value["summary"].__setitem__("overall_pass", 7),
        lambda value: value["summary"].__setitem__("style_pass", 13),
        lambda value: value["gate_transfer"].__setitem__("continuous_leverage_force_path", "PASS"),
        lambda value: value["style_hypothesis_result"].__setitem__("result", "WINNER"),
        lambda value: value["strongest_shortlist"].pop(),
        lambda value: value["inputs"][0].__setitem__("sha256", "0" * 64),
        lambda value: value["inspection_artifacts"]["phone_long_scroll"].__setitem__("sha256", "0" * 64),
        lambda value: value["triage_sheet"].__setitem__("sha256", "0" * 64),
        lambda value: value.__setitem__("recommendation", "Promote and accept"),
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
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "summary": document.get("summary"), "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
