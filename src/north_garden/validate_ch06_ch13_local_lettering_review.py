"""Validate deterministic sparse local-lettering review editions for CH06-CH13."""

from __future__ import annotations

import argparse
import copy
import json
from typing import Any

from build_ch06_ch13_local_lettering_review import (
    CHAPTERS,
    COPY,
    MANIFEST,
    ROOT,
    sha256,
)
from PIL import Image


def validate(document: dict[str, Any], copy_document: dict[str, Any], *, files: bool) -> list[str]:
    errors = []
    if copy_document.get("record_type") != "ComicPanelLetteringCopyManifest" or copy_document.get("planning_structure") != "ComicPanelPlan":
        errors.append("copy manifest planning boundary differs")
    if copy_document.get("animation_shot_plan") is not None or copy_document.get("e_conte") is not None:
        errors.append("copy manifest cross-medium fields must be null")
    if copy_document.get("totals") != {"chapters": 8, "beats": 80}:
        errors.append("copy totals differ")
    if document.get("planning_structure") != "ComicPanelPlan" or document.get("animation_shot_plan") is not None or document.get("e_conte") is not None:
        errors.append("comic planning boundary differs")
    expected_summary = {
        "chapters": 8,
        "panels": 320,
        "lettered_panels": 80,
        "artifacts": 25,
        "source_triage": {"PASS": 296, "WARN": 5, "FAIL": 19},
        "accepted": 0,
        "commercially_cleared": 0,
        "exact_production_base": 0,
    }
    if document.get("summary") != expected_summary:
        errors.append("summary differs")
    chapters = document.get("chapters", [])
    if [row.get("chapter") for row in chapters] != [chapter.upper() for chapter in CHAPTERS]:
        errors.append("chapter order differs")
    copy_beats = {row["chapter"]: row["beats"] for row in copy_document.get("chapters", [])}
    if list(copy_beats) != [chapter.upper() for chapter in CHAPTERS]:
        errors.append("copy chapter order differs")
    all_panels = []
    for chapter in chapters:
        if chapter.get("summary") != {"panels": 40, "lettered_panels": 10, "unlettered_panels": 30}:
            errors.append(f"chapter summary differs: {chapter.get('chapter')}")
        if sum(chapter.get("source_triage", {}).values()) != 40:
            errors.append(f"source triage differs: {chapter.get('chapter')}")
        entries = chapter.get("entries", [])
        source_beats = copy_beats.get(chapter.get("chapter"), [])
        plans_document = json.loads((ROOT / chapter.get("plans", {}).get("path", "")).read_text(encoding="utf-8"))
        plans = {row["panel_id"]: row for row in plans_document["plans"]}
        for beat in source_beats:
            panel = plans.get(beat.get("panel_id"))
            if panel is None or len(panel["comic_direction"]["lettering"].get("safe_zones", [])) != 1:
                errors.append(f"copy panel/safe-zone binding differs: {beat.get('panel_id')}")
                continue
            if beat.get("copy_type") not in {"dialogue", "caption", "sfx", "system"} or not beat.get("copy") or not beat.get("rationale"):
                errors.append(f"copy entry differs: {beat.get('panel_id')}")
            if beat.get("copy_type") == "dialogue" and beat.get("speaker") not in panel.get("visible_adult_cast", []):
                errors.append(f"dialogue speaker is not visible: {beat.get('panel_id')}")
            if beat.get("copy_type") == "system" and beat.get("speaker") != "SYSTEM":
                errors.append(f"system speaker differs: {beat.get('panel_id')}")
        if len(entries) != 10 or [row.get("panel_id") for row in entries] != [row.get("panel_id") for row in source_beats]:
            errors.append(f"lettering entry binding differs: {chapter.get('chapter')}")
        if any(row.get("copy_type") not in {"dialogue", "caption", "sfx", "system"} for row in entries):
            errors.append(f"copy type differs: {chapter.get('chapter')}")
        if len(chapter.get("artifacts", [])) != 3:
            errors.append(f"chapter artifacts differ: {chapter.get('chapter')}")
        all_panels.extend(row.get("panel_id") for row in entries)
    if len(all_panels) != 80 or len(set(all_panels)) != 80:
        errors.append("80 unique lettering panels are required")
    if document.get("treatment", {}).get("translucent_backing") is not True:
        errors.append("transparent backing must remain explicit")
    hash_bindings = [document.get("copy_manifest", {}), document.get("aggregate_artifact", {})]
    for chapter in chapters:
        hash_bindings.extend((chapter.get("plans", {}), chapter.get("source_packet", {}), *chapter.get("artifacts", [])))
    for binding in hash_bindings:
        if not isinstance(binding.get("sha256"), str) or len(binding["sha256"]) != 64:
            errors.append(f"invalid hash binding: {binding.get('path')}")
    if files:
        for binding in hash_bindings:
            path = ROOT / binding.get("path", "")
            if not path.is_file() or sha256(path) != binding.get("sha256"):
                errors.append(f"file binding failed: {binding.get('path')}")
                continue
            if "dimensions" in binding:
                with Image.open(path) as opened:
                    if [opened.width, opened.height] != binding["dimensions"]:
                        errors.append(f"dimensions differ: {binding.get('path')}")
    return errors


def self_test(document: dict[str, Any], copy_document: dict[str, Any]) -> tuple[int, int]:
    mutations = []
    changes = (
        lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda d: d.__setitem__("e_conte", {}),
        lambda d: d["summary"].__setitem__("lettered_panels", 79),
        lambda d: d["summary"].__setitem__("accepted", 1),
        lambda d: d["chapters"].reverse(),
        lambda d: d["chapters"][0]["entries"].pop(),
        lambda d: d["chapters"][0]["entries"][0].__setitem__("copy_type", "image_text"),
        lambda d: d["chapters"][0]["artifacts"].pop(),
        lambda d: d["treatment"].__setitem__("translucent_backing", False),
        lambda d: d["aggregate_artifact"].__setitem__("sha256", "bad"),
    )
    for change in changes:
        changed = copy.deepcopy(document)
        change(changed)
        mutations.append(bool(validate(changed, copy_document, files=False)))
    return sum(mutations), len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    copy_document = json.loads(COPY.read_text(encoding="utf-8"))
    errors = validate(document, copy_document, files=True)
    result: dict[str, Any] = {"status": "PASS" if not errors else "FAIL", "errors": errors}
    if args.self_test and not errors:
        rejected, total = self_test(document, copy_document)
        result["self_test"] = f"{rejected}/{total}"
        if rejected != total:
            result["status"] = "FAIL"
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
