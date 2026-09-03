"""Validate the CH01-CH05 visual-regression packet and fail closed on scope drift."""
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
REPORT = ROOT / "docs/research/evidence/cross-chapter-comic-regression-r1.json"
DIRECTION = ROOT / "production/comic/style-direction/north-garden-cross-chapter-continuity-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(doc: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    check(doc.get("record_type") == "CrossChapterComicPanelPlanRegressionPacket", "record_type")
    check(doc.get("state") == "LOCAL_REVIEW_AID_MIXED_ACCEPTANCE_STATES", "state")
    check(doc.get("planning_structure") == "ComicPanelPlan", "planning_structure")
    check(doc.get("animation_shot_plan") is None and doc.get("e_conte") is None, "cross-medium fields")
    summary = doc.get("summary", {})
    check(summary == {"chapters": 5, "scene_fragment_chapters": 4, "full_chapter_anchor_sets": 1, "panels": 23, "ch01_ch04_panels": 13, "ch05_anchors": 10, "historical_internal_research_selected": 7, "pending_owner_review": 16}, "summary")
    panels = doc.get("panels", [])
    check(len(panels) == 23 and len({row.get("panel_id") for row in panels}) == 23, "panel rows")
    by_chapter = {chapter: sum(row.get("chapter") == chapter for row in panels) for chapter in ("CH01", "CH02", "CH03", "CH04", "CH05")}
    check(by_chapter == {"CH01": 4, "CH02": 3, "CH03": 3, "CH04": 3, "CH05": 10}, "chapter distribution")
    check(all(isinstance(row.get("visible_adult_cast"), list) and set(row["visible_adult_cast"]) <= {"SOREN", "SIGRID"} for row in panels), "adult cast fields")
    check(sum(row.get("source_acceptance_state") == "INTERNAL_RESEARCH_ACCEPTED" for row in panels) == 7, "historical selected count")
    artifacts = doc.get("artifacts", [])
    check(len(artifacts) == 2 and len({row.get("kind") for row in artifacts}) == 2, "artifacts")
    boundary = doc.get("boundary", {})
    check(all(boundary.get(key) == 0 for key in ("new_generation", "provider_calls", "uploads", "source_acceptance_states_modified", "canon_or_panel_plans_created", "commercial_clearance_decisions")), "boundary")
    if verify_files:
        check(len(doc.get("source_bindings", [])) == 10, "source binding count")
        for binding in doc.get("source_bindings", []):
            path = ROOT / binding.get("path", "")
            check(path.is_file(), f"source missing {binding.get('path')}")
            if path.is_file():
                check(sha256(path) == binding.get("sha256"), f"source hash {binding.get('path')}")
        for row in panels:
            path = ROOT / row["source"]["path"]
            check(path.is_file(), f"panel missing {row['panel_id']}")
            if path.is_file():
                check(sha256(path) == row["source"]["sha256"], f"panel hash {row['panel_id']}")
        for artifact in artifacts:
            path = ROOT / artifact.get("path", "")
            check(path.is_file(), f"artifact missing {artifact.get('path')}")
            if not path.is_file():
                continue
            check(sha256(path) == artifact.get("sha256"), f"artifact hash {artifact.get('path')}")
            with Image.open(path) as image:
                check(list(image.size) == [artifact.get("width_px"), artifact.get("height_px")], f"artifact dimensions {artifact.get('path')}")
            ignored = subprocess.run(["git", "check-ignore", "-q", "--", artifact["path"]], cwd=ROOT).returncode == 0
            tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", artifact["path"]], cwd=ROOT, capture_output=True).returncode == 0
            check(ignored and not tracked, f"artifact repository state {artifact.get('path')}")
        direction = json.loads(DIRECTION.read_text(encoding="utf-8"))
        check(direction.get("planning_structure") == "ComicPanelPlan", "direction planning structure")
        check(direction.get("animation_shot_plan") is None and direction.get("e_conte") is None, "direction cross-medium fields")
        check(direction.get("source_evidence", {}).get("sha256") == sha256(REPORT), "direction evidence hash")
        check(direction.get("acceptance_boundary") == {"historical_acceptance_modified": False, "ch05_art_accepted": False, "commercial_clearance_decided": False, "exact_production_base_decided": False}, "direction acceptance boundary")
    return errors


def self_test(doc: dict[str, Any]) -> tuple[int, int]:
    mutations = [
        lambda d: d.__setitem__("state", "ACCEPTED"),
        lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda d: d.__setitem__("animation_shot_plan", {}),
        lambda d: d["summary"].__setitem__("panels", 22),
        lambda d: d["summary"].__setitem__("scene_fragment_chapters", 0),
        lambda d: d["panels"].pop(),
        lambda d: d["panels"][0].__setitem__("panel_id", d["panels"][1]["panel_id"]),
        lambda d: d["artifacts"].pop(),
        lambda d: d["boundary"].__setitem__("new_generation", 1),
        lambda d: d["boundary"].__setitem__("canon_or_panel_plans_created", 1),
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
    doc = json.loads(REPORT.read_text(encoding="utf-8"))
    errors = validate(doc)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(doc)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "panels": len(doc.get("panels", [])), "artifacts": len(doc.get("artifacts", [])), "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
