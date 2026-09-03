"""Validate the flat-graphic-gouache crop manifest and deterministic split report."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-crops-r1.json"
REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-flat-graphic-gouache-r1/panels/flat-graphic-gouache-panel-split-report-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
PROMPTS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-prompt-manifest-r1.json"
EXECUTIONS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-execution-manifest-r1.json"
COUNTS = [5, 4, 5, 5, 5, 5, 5, 5, 5, 3, 3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(document: dict[str, Any], report: dict[str, Any] | None, verify_files: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    plans = sorted(
        json.loads(PLANS.read_text(encoding="utf-8"))["plans"],
        key=lambda row: row["display_order"],
    )
    prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))["sequences"]
    executions = json.loads(EXECUTIONS.read_text(encoding="utf-8"))["records"]
    panel_ids = [row["panel_id"] for row in plans]
    plan_by_id = {row["panel_id"]: row for row in plans}
    sequences = document.get("sequences", [])
    crops = [crop for sequence in sequences for crop in sequence.get("crops", [])]

    check(document.get("record_type") == "CH05SequenceStripCropManifest", "record_type")
    check(document.get("record_id") == "ng-ch05-complete-chapter-flat-graphic-gouache-crops-r1", "record_id")
    check(document.get("state") == "HASH_PINNED_LOCAL_DERIVATIVE_PLAN_UNACCEPTED", "state")
    check(document.get("medium") == "comic", "medium")
    check(
        document.get("planning_structure") == "ComicPanelPlan"
        and document.get("animation_shot_plan") is None
        and document.get("e_conte") is None,
        "planning boundary",
    )
    check(
        document.get("comic_panel_plan_source")
        == {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha256(PLANS)},
        "ComicPanelPlan source",
    )
    check(
        document.get("prompt_manifest")
        == {"path": PROMPTS.relative_to(ROOT).as_posix(), "sha256": sha256(PROMPTS)},
        "prompt manifest source",
    )
    check(
        document.get("execution_manifest")
        == {"path": EXECUTIONS.relative_to(ROOT).as_posix(), "sha256": sha256(EXECUTIONS)},
        "execution manifest source",
    )
    check(document.get("output_filename_template") == "p{panel_number:03d}-flat-graphic-gouache-r1.png", "template")
    check(
        document.get("summary")
        == {
            "sequence_sources": 11,
            "planned_crops": 50,
            "complete_plan_coverage": True,
            "deterministic_gutter_detection": True,
            "manual_gutter_overrides": 1,
        },
        "summary",
    )
    check(len(sequences) == 11 and [len(sequence.get("crops", [])) for sequence in sequences] == COUNTS, "sequence counts")
    check([crop.get("panel_id") for crop in crops] == panel_ids, "canonical panel coverage")
    check([crop.get("display_order") for crop in crops] == list(range(1, 51)), "canonical display order")
    check(
        all(
            crop.get("plan_revision_id") == plan_by_id[crop.get("panel_id")]["plan_revision_id"]
            for crop in crops
            if crop.get("panel_id") in plan_by_id
        ),
        "plan revision bindings",
    )

    for index, (sequence, prompt, execution) in enumerate(zip(sequences, prompts, executions, strict=False)):
        label = f"sequence[{index}]"
        check(sequence.get("sequence_id") == prompt.get("source_sequence_id"), f"{label} source sequence")
        check(sequence.get("prompt_sequence_id") == prompt.get("sequence_id"), f"{label} prompt sequence")
        check(sequence.get("execution_sequence_id") == execution.get("sequence_id"), f"{label} execution sequence")
        check(sequence.get("prompt_sha256") == prompt.get("prompt_sha256"), f"{label} prompt hash")
        check(sequence.get("panel_range") == prompt.get("panel_range"), f"{label} panel range")
        check(sequence.get("panel_count") == prompt.get("panel_count"), f"{label} panel count")
        source = sequence.get("source", {})
        check(source == execution.get("output"), f"{label} execution source binding")
        check(source.get("path") == prompt.get("planned_output"), f"{label} planned source path")
        gutter = sequence.get("gutter_detection", {})
        boxes = [crop.get("box") for crop in sequence.get("crops", [])]
        expected_mode = (
            "hash_pinned_manual_override"
            if sequence.get("execution_sequence_id") == "flat-graphic-gouache-s11-farmhouse-reversal"
            else "row_dominance"
        )
        check(gutter.get("mode") == expected_mode, f"{label} gutter detection mode")
        if expected_mode == "hash_pinned_manual_override":
            check(
                gutter.get("detected_internal_gutter_extents_inclusive") == [[625, 628], [1252, 1255]],
                f"{label} exact hash-pinned S11 separator extents",
            )
        check(
            isinstance(gutter.get("detected_internal_gutter_extents_inclusive"), list)
            and len(gutter["detected_internal_gutter_extents_inclusive"]) == len(boxes) - 1,
            f"{label} gutter count",
        )
        check(
            all(
                isinstance(box, list)
                and len(box) == 4
                and all(isinstance(value, int) and not isinstance(value, bool) for value in box)
                and 0 <= box[0] < box[2] <= source.get("width", -1)
                and 0 <= box[1] < box[3] <= source.get("height", -1)
                for box in boxes
            ),
            f"{label} crop bounds",
        )
        check(all(boxes[position][3] <= boxes[position + 1][1] for position in range(len(boxes) - 1)), f"{label} monotonic crops")
        if verify_files:
            path = ROOT / source.get("path", "")
            check(
                path.is_file()
                and sha256(path) == source.get("sha256")
                and path.stat().st_size == source.get("bytes"),
                f"{label} source file binding",
            )
            if path.is_file():
                with Image.open(path) as image:
                    check([image.width, image.height] == [source.get("width"), source.get("height")], f"{label} source dimensions")

    if report is not None:
        check(report.get("record_type") == "CH05SequenceStripSplitReport", "split report type")
        check(
            report.get("manifest")
            == {"path": MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha256(MANIFEST)},
            "split report manifest binding",
        )
        check(
            report.get("summary")
            == {
                "sequence_sources": 11,
                "panels_produced": 50,
                "complete_plan_coverage": True,
                "source_hashes_verified": 11,
                "crop_bounds_verified": 50,
            },
            "split report summary",
        )
        check(
            report.get("planning_structure") == "ComicPanelPlan"
            and report.get("animation_shot_plan") is None
            and report.get("e_conte") is None,
            "split report planning boundary",
        )
        report_panels = report.get("panels", [])
        outputs = [row.get("output", {}) for row in report_panels]
        check(len(outputs) == 50, "split output count")
        check([row.get("panel_id") for row in report_panels] == panel_ids, "split canonical order")
        for number, (crop, row, output) in enumerate(zip(crops, report_panels, outputs, strict=False), start=1):
            path = ROOT / output.get("path", "")
            box = crop["box"]
            check(row.get("crop_box") == box, f"split crop binding {number}")
            check(Path(output.get("path", "")).name == f"p{number:03d}-flat-graphic-gouache-r1.png", f"split filename {number}")
            check([output.get("width"), output.get("height")] == [box[2] - box[0], box[3] - box[1]], f"split dimensions {number}")
            if verify_files:
                check(path.is_file() and sha256(path) == output.get("sha256"), f"split hash {number}")
                if path.is_file():
                    with Image.open(path) as image:
                        check(
                            image.format == "PNG"
                            and [image.width, image.height] == [output.get("width"), output.get("height")],
                            f"split decode {number}",
                        )
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("e_conte", {}),
        lambda value: value["sequences"].pop(),
        lambda value: value["sequences"][0]["crops"].pop(),
        lambda value: value["sequences"][0]["crops"][0].__setitem__("panel_id", "bad"),
        lambda value: value["sequences"][0]["crops"][0].__setitem__("plan_revision_id", "bad"),
        lambda value: value["sequences"][0]["crops"][0].__setitem__("display_order", 2),
        lambda value: value["sequences"][0]["crops"][0].__setitem__("box", [0, 2, 1, 1]),
        lambda value: value["sequences"][0]["gutter_detection"].__setitem__("mode", "manual"),
        lambda value: value["sequences"][0]["gutter_detection"]["detected_internal_gutter_extents_inclusive"].pop(),
        lambda value: value["sequences"][0].__setitem__("prompt_sha256", "0" * 64),
        lambda value: value.__setitem__("output_filename_template", "bad.png"),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate, None, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.is_file() else None
    errors = validate(document, report)
    caught = total = 0
    if arguments.self_test:
        caught, total = self_test(document)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(
        json.dumps(
            {
                "errors": errors,
                "report_present": report is not None,
                "self_test": f"{caught}/{total}" if arguments.self_test else None,
                "status": "PASS" if not errors else "FAIL",
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
