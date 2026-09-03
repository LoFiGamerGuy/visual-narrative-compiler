"""Validate the deterministic CH06-CH13 progression review."""

from __future__ import annotations

import argparse
import copy
import json
from typing import Any

from build_ch06_ch13_progression_review import CHAPTERS, MANIFEST, ROOT, sha256
from PIL import Image


def load() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def validate(document: dict[str, Any], *, files: bool) -> list[str]:
    errors: list[str] = []
    if document.get("planning_structure") != "ComicPanelPlan":
        errors.append("planning structure must be ComicPanelPlan")
    if document.get("animation_shot_plan") is not None or document.get("e_conte") is not None:
        errors.append("cross-medium fields must be null")
    if document.get("chapters") != [chapter.upper() for chapter in CHAPTERS]:
        errors.append("chapter order differs")
    packets = document.get("source_packets", [])
    if len(packets) != 8:
        errors.append("eight source packets are required")
    else:
        for row in packets:
            if not isinstance(row.get("sha256"), str) or len(row["sha256"]) != 64:
                errors.append(f"packet hash is invalid: {row.get('chapter')}")
                continue
            path = ROOT / row.get("path", "")
            if files and (not path.is_file() or sha256(path) != row.get("sha256")):
                errors.append(f"packet binding failed: {row.get('chapter')}")
    expected = {
        "complete_chapters": 8,
        "panel_candidates": 320,
        "sequence_sources": 64,
        "triage": {"PASS": 296, "WARN": 5, "FAIL": 19},
        "sampled_panels": 72,
        "whole_chapter_alternate_arms": 0,
        "accepted": 0,
        "commercially_cleared": 0,
        "exact_production_base": 0,
    }
    if document.get("summary") != expected:
        errors.append("summary counts/status differ")
    artifacts = document.get("artifacts", [])
    required = {"eight_chapter_contact_sheet", "eight_chapter_sequence_progression", "eight_chapter_phone_sampler"}
    if len(artifacts) != 3 or {row.get("type") for row in artifacts} != required:
        errors.append("three exact review artifacts are required")
    else:
        for row in artifacts:
            if not isinstance(row.get("sha256"), str) or len(row["sha256"]) != 64:
                errors.append(f"artifact hash is invalid: {row.get('type')}")
                continue
            path = ROOT / row.get("path", "")
            if files and (not path.is_file() or sha256(path) != row.get("sha256")):
                errors.append(f"artifact binding failed: {row.get('type')}")
                continue
            if files:
                with Image.open(path) as opened:
                    if [opened.width, opened.height] != row.get("dimensions"):
                        errors.append(f"artifact dimensions differ: {row.get('type')}")
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations = []
    for mutate in (
        lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda d: d.__setitem__("e_conte", {}),
        lambda d: d["chapters"].reverse(),
        lambda d: d["source_packets"].pop(),
        lambda d: d["source_packets"][0].__setitem__("sha256", "bad"),
        lambda d: d["summary"].__setitem__("panel_candidates", 319),
        lambda d: d["summary"].__setitem__("accepted", 1),
        lambda d: d["summary"]["triage"].__setitem__("PASS", 297),
        lambda d: d["artifacts"].pop(),
        lambda d: d["artifacts"][0].__setitem__("sha256", "bad"),
    ):
        changed = copy.deepcopy(document)
        mutate(changed)
        mutations.append(bool(validate(changed, files=False)))
    return sum(mutations), len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = load()
    errors = validate(document, files=True)
    result: dict[str, Any] = {"status": "PASS" if not errors else "FAIL", "errors": errors}
    if args.self_test and not errors:
        rejected, total = self_test(document)
        result["self_test"] = f"{rejected}/{total}"
        if rejected != total:
            result["status"] = "FAIL"
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
