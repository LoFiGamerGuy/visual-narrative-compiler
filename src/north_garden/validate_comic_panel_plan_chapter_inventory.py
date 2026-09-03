"""Validate the current CH01-CH05 ComicPanelPlan chapter inventory."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "docs/research/evidence/comic-panel-plan-chapter-inventory-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(doc: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    check(doc.get("record_type") == "ComicPanelPlanChapterInventory", "record_type")
    check(doc.get("state") == "CURRENT_SOURCE_INVENTORY", "state")
    check(doc.get("planning_structure") == "ComicPanelPlan", "planning_structure")
    check(doc.get("animation_shot_plan") is None and doc.get("e_conte") is None, "cross-medium fields")
    summary = doc.get("summary", {})
    check(summary == {"chapters_inventoried": 5, "full_chapter_review_ready": ["CH05"], "scene_fragment_only": ["CH01", "CH02", "CH03", "CH04"], "total_current_panel_plans": 63, "next_full_chapter_render_ready": False}, "summary")
    chapters = doc.get("chapters", [])
    check([row.get("chapter") for row in chapters] == ["CH01", "CH02", "CH03", "CH04", "CH05"], "chapter order")
    check([row.get("panel_count") for row in chapters] == [4, 3, 3, 3, 50], "panel counts")
    check([row.get("candidate_count") for row in chapters] == [4, 3, 3, 3, 59], "candidate counts")
    check(all(row.get("planning_structure") == "ComicPanelPlan" and row.get("animation_shot_plan") is None and row.get("e_conte") is None for row in chapters), "chapter planning boundaries")
    check(all(len(row.get("panel_ids", [])) == row.get("panel_count") and len(set(row.get("panel_ids", []))) == row.get("panel_count") for row in chapters), "panel identities")
    boundary = doc.get("boundary", {})
    check(len(boundary) == 6 and all(value == 0 for value in boundary.values()), "boundary")
    check(doc.get("decision", {}).get("current_production_baseline") == "CH05 r6", "baseline decision")
    if verify_files:
        for row in chapters:
            for key in ("plan_source", "art_or_revision_binding", "edition_or_release_binding"):
                binding = row.get(key, {})
                path = ROOT / binding.get("path", "")
                check(path.is_file(), f"missing {key} {binding.get('path')}")
                if path.is_file():
                    check(sha256(path) == binding.get("sha256"), f"hash {key} {binding.get('path')}")
    return errors


def self_test(doc: dict[str, Any]) -> tuple[int, int]:
    mutations = [
        lambda d: d.__setitem__("state", "READY"),
        lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda d: d.__setitem__("animation_shot_plan", {}),
        lambda d: d["summary"].__setitem__("total_current_panel_plans", 64),
        lambda d: d["summary"].__setitem__("next_full_chapter_render_ready", True),
        lambda d: d["summary"]["full_chapter_review_ready"].append("CH04"),
        lambda d: d["chapters"][0].__setitem__("panel_count", 50),
        lambda d: d["chapters"][1]["panel_ids"].pop(),
        lambda d: d["chapters"][4].__setitem__("candidate_count", 50),
        lambda d: d["boundary"].__setitem__("canon_changes", 1),
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
    doc = json.loads(INVENTORY.read_text(encoding="utf-8"))
    errors = validate(doc)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(doc)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "chapters": len(doc.get("chapters", [])), "plans": doc.get("summary", {}).get("total_current_panel_plans"), "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
