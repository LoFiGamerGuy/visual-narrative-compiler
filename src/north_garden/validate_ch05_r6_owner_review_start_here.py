"""Validate the current CH05 r6 owner-review start-here pointer."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-r6-owner-review-start-here-r1.json"
MARKDOWN = ROOT / "docs/research/ch05-r6-owner-review-start-here-r1.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(doc: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    check(doc.get("record_type") == "CH05R6OwnerReviewStartHere", "record_type")
    check(doc.get("state") == "NAVIGATION_READY_OWNER_REVIEW_PENDING", "state")
    check(doc.get("planning_structure") == "ComicPanelPlan", "planning_structure")
    check(doc.get("animation_shot_plan") is None and doc.get("e_conte") is None, "cross-medium fields")
    summary = doc.get("measured_summary", {})
    expected = {"chapter_panels": 50, "panel_candidates": 59, "raster_outputs": 16, "review_artifacts": 10, "strongest_candidates": 13, "warning_candidates": 2, "chapter_inventory_plans": 63, "cross_chapter_panels": 23, "integrated_release_commands": 10, "integrated_release_effective_checks": 93, "accepted": 0, "commercially_cleared": 0, "exact_production_base": 0}
    for key, value in expected.items():
        check(summary.get(key) == value, f"summary.{key}")
    check(summary.get("agent_triage") == {"pass": 49, "warn": 1, "fail": 0, "gating": False}, "agent triage")
    check(summary.get("human_review_minutes") is None, "human minutes")
    artifacts = doc.get("review_artifacts", [])
    strongest = doc.get("strongest_candidates", [])
    warnings = doc.get("warning_candidates", [])
    check(len(artifacts) == 10 and len({row.get("path") for row in artifacts}) == 10, "artifacts")
    check(len(strongest) == 13 and len({row.get("panel_id") for row in strongest}) == 13, "strongest")
    check(len(warnings) == 2 and all(row.get("panel_id") == "ng-ch05-sc01-p032" for row in warnings), "warnings")
    check([row.get("status") for row in warnings] == ["SELECTED_WARN", "DIAGNOSTIC_WARN_NOT_SELECTED"], "warning status")
    groups = doc.get("decision_groups", {})
    check({key: len(value) for key, value in groups.items()} == {"visual": 4, "canon": 3, "rights_and_production": 3}, "decision groups")
    check(all(row.get("state") == "PENDING" for row in groups.get("visual", []) + groups.get("canon", [])), "visual/canon decision state")
    check(doc.get("pipeline_next_state", {}).get("next_full_chapter_render_ready") is False, "next chapter state")
    check(doc.get("pipeline_next_state", {}).get("semantic_validation") == {"positive": "1/1", "adversarial": "23/23"}, "semantic validation")
    boundary = doc.get("boundary", {})
    check(len(boundary) == 7 and all(value == 0 for value in boundary.values()), "boundary")
    if verify_files:
        markdown = MARKDOWN.read_text(encoding="utf-8")
        for binding in doc.get("source_bindings", []):
            path = ROOT / binding.get("path", "")
            check(path.is_file(), f"source missing {binding.get('path')}")
            if path.is_file():
                check(sha256(path) == binding.get("sha256"), f"source hash {binding.get('path')}")
        for row in artifacts + strongest + warnings:
            path = ROOT / row.get("path", "")
            check(path.is_file(), f"asset missing {row.get('path')}")
            if not path.is_file():
                continue
            check(sha256(path) == row.get("sha256"), f"asset hash {row.get('path')}")
            with Image.open(path) as image:
                check(list(image.size) == [row.get("width_px"), row.get("height_px")], f"asset dimensions {row.get('path')}")
            ignored = subprocess.run(["git", "check-ignore", "-q", "--", row["path"]], cwd=ROOT).returncode == 0
            tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", row["path"]], cwd=ROOT, capture_output=True).returncode == 0
            check(ignored and not tracked, f"asset repository state {row.get('path')}")
            check((ROOT / row["path"]).as_posix() in markdown, f"markdown link {row.get('path')}")
    return errors


def self_test(doc: dict[str, Any]) -> tuple[int, int]:
    mutations = [
        lambda d: d.__setitem__("state", "PUBLISHED"),
        lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda d: d.__setitem__("animation_shot_plan", {}),
        lambda d: d["measured_summary"].__setitem__("chapter_panels", 49),
        lambda d: d["measured_summary"].__setitem__("accepted", 1),
        lambda d: d["review_artifacts"].pop(),
        lambda d: d["strongest_candidates"].pop(),
        lambda d: d["warning_candidates"].pop(),
        lambda d: d["warning_candidates"][0].__setitem__("status", "PASS"),
        lambda d: d["decision_groups"]["canon"][0].__setitem__("state", "APPROVED"),
        lambda d: d["pipeline_next_state"].__setitem__("next_full_chapter_render_ready", True),
        lambda d: d["boundary"].__setitem__("publication", 1),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(doc)
        mutation(candidate)
        caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    doc = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    errors = validate(doc)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(doc)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "artifacts": len(doc.get("review_artifacts", [])), "strongest": len(doc.get("strongest_candidates", [])), "warnings": len(doc.get("warning_candidates", [])), "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
