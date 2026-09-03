"""Validate the alternate graphic crop manifest and ignored split report."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-complete-chapter-alt-graphic-crops-r1.json"
REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-alt-graphic-r1/panels/panel-split-report-r2.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(doc: dict[str, Any], report: dict[str, Any] | None, verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    check(doc.get("record_type") == "CH05SequenceStripCropManifest", "record_type")
    check(doc.get("planning_structure") == "ComicPanelPlan", "planning_structure")
    check(doc.get("animation_shot_plan") is None and doc.get("e_conte") is None, "cross-medium fields")
    check(doc.get("output_filename_template") == "p{panel_number:03d}-alt-graphic-r1.png", "filename template")
    sequences = doc.get("sequences", [])
    crops = [crop for sequence in sequences for crop in sequence.get("crops", [])]
    expected_ids = [row["panel_id"] for row in json.loads(PLANS.read_text(encoding="utf-8"))["plans"]]
    check(len(sequences) == 11 and len(crops) == 50, "coverage counts")
    check([row.get("panel_id") for row in crops] == expected_ids, "ordered panel ids")
    check(all(len(sequence.get("gutter_detection", {}).get("detected_internal_gutter_extents_inclusive", [])) == len(sequence.get("crops", [])) - 1 for sequence in sequences), "gutter counts")
    check(all(len(crop.get("box", [])) == 4 and crop["box"][0] == 0 and crop["box"][1] < crop["box"][3] for crop in crops), "crop boxes")
    if verify_files:
        for sequence in sequences:
            source = sequence.get("source", {})
            path = ROOT / source.get("path", "")
            check(path.is_file() and sha256(path) == source.get("sha256"), f"source binding {source.get('path')}")
    if report is not None:
        check(report.get("record_type") == "CH05SequenceStripSplitReport", "report record_type")
        check(report.get("summary", {}).get("panels_produced") == 50 and report.get("summary", {}).get("complete_plan_coverage") is True, "report summary")
        outputs = [row.get("output", {}) for row in report.get("panels", [])]
        check(len(outputs) == 50 and all(Path(row.get("path", "")).name == f"p{index:03d}-alt-graphic-r1.png" for index, row in enumerate(outputs, 1)), "report output names")
        if verify_files:
            for output in outputs:
                path = ROOT / output.get("path", "")
                check(path.is_file() and sha256(path) == output.get("sha256"), f"crop binding {output.get('path')}")
    return errors


def self_test(doc: dict[str, Any]) -> tuple[int, int]:
    mutations = [
        lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda d: d["sequences"].pop(),
        lambda d: d["sequences"][0]["crops"].pop(),
        lambda d: d["sequences"][0]["crops"][0].__setitem__("panel_id", "wrong"),
        lambda d: d["sequences"][0]["crops"][0].__setitem__("box", [0, 2, 1, 1]),
        lambda d: d["sequences"][0]["gutter_detection"]["detected_internal_gutter_extents_inclusive"].pop(),
        lambda d: d.__setitem__("output_filename_template", "unsafe.png"),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(doc)
        mutation(candidate)
        caught += bool(validate(candidate, None, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.is_file() else None
    errors = validate(doc, report)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(doc)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "report_present": report is not None, "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
