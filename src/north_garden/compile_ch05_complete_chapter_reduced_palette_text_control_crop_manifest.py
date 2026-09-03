"""Compile deterministic crops for CH05 reduced-palette text-only control strips."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from compile_ch05_complete_chapter_alt_graphic_crop_manifest import (
    EDGE_CLUSTER_PX,
    SEPARATOR_DOMINANCE,
    SEPARATOR_JOIN_DISTANCE_PX,
    panel_boxes,
)
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
PROMPTS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-prompt-manifest-r1.json"
EXECUTIONS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-execution-manifest-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-crops-r1.json"

# Automatic row-dominance detection is authoritative except for the three exact
# source hashes below. Native visual inspection and row-luminance inspection
# found narrow painted separator rows that the generic dominance threshold did
# not classify consistently. Each override removes only those separator rows.
MANUAL_GUTTER_OVERRIDES: dict[str, dict[str, Any]] = {
    "reduced-palette-text-control-s03-listening-twine-ridge": {
        "source_sha256": "8c389293452e1e7e139ae3629209531768556fe4dfd0f3f1b528b6e887c929e0",
        "gutters": [[366, 371], [731, 736], [1095, 1100], [1461, 1466]],
        "justification": "Native visual and row-luminance inspection identified four exact white separator bands; automatic detection returned only three incomplete extents.",
    },
    "reduced-palette-text-control-s09-deduction-retreat-cut": {
        "source_sha256": "81d61fc893bf3c8e8aef4518f2674858f5534dd9827a47fbbda359f1a4aa549b",
        "gutters": [[358, 360], [713, 715], [1068, 1070], [1456, 1458]],
        "justification": "Native visual and row-luminance inspection identified four three-row painted separators; automatic detection returned only one.",
    },
    "reduced-palette-text-control-s11-farmhouse-reversal": {
        "source_sha256": "9aa41e0e57b3d22fc46ef228252b3533c129d2be280f6fa3743f19e3b31862aa",
        "gutters": [[588, 593], [1181, 1186]],
        "justification": "Native visual and row-luminance inspection identified two six-row white separator bands; automatic detection returned only the first.",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def boxes_from_override(image: Image.Image, gutters: list[list[int]]) -> list[list[int]]:
    boxes: list[list[int]] = []
    top = 0
    for start, end in gutters:
        if not (0 <= top < start <= end < image.height):
            raise ValueError(f"invalid manual gutter override: {gutters}")
        boxes.append([0, top, image.width, start])
        top = end + 1
    if top >= image.height:
        raise ValueError(f"manual gutter override consumes final panel: {gutters}")
    boxes.append([0, top, image.width, image.height])
    return boxes


def main() -> int:
    prompt_document = json.loads(PROMPTS.read_text(encoding="utf-8"))
    execution_document = json.loads(EXECUTIONS.read_text(encoding="utf-8"))
    prompts_by_id = {row["sequence_id"]: row for row in prompt_document["sequences"]}
    plan_rows = sorted(json.loads(PLANS.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    expected_ids = [row["panel_id"] for row in plan_rows]
    plan_by_id = {row["panel_id"]: row for row in plan_rows}
    sequences: list[dict[str, Any]] = []
    observed_ids: list[str] = []

    for execution in execution_document["records"]:
        prompt = prompts_by_id[execution["sequence_id"]]
        for key in ("source_sequence_id", "panel_range", "panel_count", "prompt_sha256", "input_references", "cross_panel_gate_phrases"):
            if execution[key] != prompt[key]:
                raise ValueError(f"execution/prompt mismatch {execution['sequence_id']}:{key}")
        start, end = execution["panel_range"]
        panel_ids = expected_ids[start - 1:end]
        source = execution["output"]
        source_path = ROOT / source["path"]
        if not source_path.is_file():
            raise ValueError(f"reduced-palette source is missing: {source['path']}")
        source_hash = sha256(source_path)
        if source_hash != source["sha256"] or source_path.stat().st_size != source["bytes"]:
            raise ValueError(f"execution output binding failed: {execution['sequence_id']}")
        with Image.open(source_path) as opened:
            image = opened.convert("RGB")
        if [image.width, image.height] != [source["width"], source["height"]]:
            raise ValueError(f"execution dimensions failed: {execution['sequence_id']}")

        override = MANUAL_GUTTER_OVERRIDES.get(execution["sequence_id"])
        if override is None:
            boxes, gutters = panel_boxes(image, execution["panel_count"])
            mode = "row_dominance"
            override_hash = None
            justification = None
        else:
            if source_hash != override["source_sha256"]:
                raise ValueError(f"manual gutter override source hash mismatch: {execution['sequence_id']}")
            gutters = override["gutters"]
            boxes = boxes_from_override(image, gutters)
            mode = "hash_pinned_manual_override"
            override_hash = override["source_sha256"]
            justification = override["justification"]
        if len(boxes) != execution["panel_count"]:
            raise ValueError(f"panel count mismatch: {execution['sequence_id']}")

        crops = []
        for panel_id, box in zip(panel_ids, boxes, strict=True):
            plan = plan_by_id[panel_id]
            crops.append({"panel_id": panel_id, "plan_revision_id": plan["plan_revision_id"], "display_order": plan["display_order"], "box": box})
        observed_ids.extend(panel_ids)
        sequences.append({
            "sequence_id": execution["source_sequence_id"],
            "execution_sequence_id": execution["sequence_id"],
            "prompt_sequence_id": prompt["sequence_id"],
            "prompt_sha256": execution["prompt_sha256"],
            "panel_range": execution["panel_range"],
            "panel_count": execution["panel_count"],
            "source": source,
            "gutter_detection": {
                "mode": mode,
                "dominance_threshold": SEPARATOR_DOMINANCE,
                "join_distance_px": SEPARATOR_JOIN_DISTANCE_PX,
                "edge_cluster_px": EDGE_CLUSTER_PX,
                "detected_internal_gutter_extents_inclusive": gutters,
                "override_source_sha256": override_hash,
                "override_justification": justification,
            },
            "crops": crops,
        })

    if observed_ids != expected_ids:
        raise ValueError("reduced-palette crop coverage differs from ordered ComicPanelPlans")
    document = {
        "record_type": "CH05SequenceStripCropManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-reduced-palette-text-control-crops-r1",
        "state": "HASH_PINNED_LOCAL_DERIVATIVE_PLAN_UNACCEPTED",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "comic_panel_plan_source": {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha256(PLANS)},
        "prompt_manifest": {"path": PROMPTS.relative_to(ROOT).as_posix(), "sha256": sha256(PROMPTS)},
        "execution_manifest": {"path": EXECUTIONS.relative_to(ROOT).as_posix(), "sha256": sha256(EXECUTIONS)},
        "output_filename_template": "p{panel_number:03d}-reduced-palette-text-control-r1.png",
        "summary": {
            "sequence_sources": len(sequences),
            "planned_crops": len(observed_ids),
            "complete_plan_coverage": True,
            "deterministic_gutter_detection": True,
            "automatic_gutter_sequences": len(sequences) - len(MANUAL_GUTTER_OVERRIDES),
            "manual_gutter_overrides": len(MANUAL_GUTTER_OVERRIDES),
        },
        "sequences": sequences,
        "boundary": "Exact source strips and crops remain ignored local research pixels; no acceptance, commercial clearance, rights decision, or exact production-base selection.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), **document["summary"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
