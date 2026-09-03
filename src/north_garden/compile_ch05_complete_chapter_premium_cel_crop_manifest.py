"""Compile deterministic crops for CH05 premium-cel sequence strips."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image

from compile_ch05_complete_chapter_alt_graphic_crop_manifest import (
    EDGE_CLUSTER_PX,
    SEPARATOR_DOMINANCE,
    SEPARATOR_JOIN_DISTANCE_PX,
    panel_boxes,
)


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
PROMPTS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-prompt-manifest-r1.json"
EXECUTIONS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-execution-manifest-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-crops-r1.json"

# Overrides must be keyed by the exact prompt sequence id and are valid only while
# that sequence's source SHA-256 remains the value pinned in the output manifest.
# All r1 premium-cel strips expose the exact expected gutters, so no override is
# justified. Keep this explicit rather than silently carrying another arm's boxes.
MANUAL_GUTTER_OVERRIDES: dict[str, list[list[int]]] = {}


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
    prompt_doc = json.loads(PROMPTS.read_text(encoding="utf-8"))
    execution_doc = json.loads(EXECUTIONS.read_text(encoding="utf-8"))
    prompts_by_id = {row["sequence_id"]: row for row in prompt_doc["sequences"]}
    plan_rows = sorted(
        json.loads(PLANS.read_text(encoding="utf-8"))["plans"],
        key=lambda row: row["display_order"],
    )
    expected_ids = [row["panel_id"] for row in plan_rows]
    plan_by_id = {row["panel_id"]: row for row in plan_rows}
    sequences: list[dict[str, Any]] = []
    observed_ids: list[str] = []

    for execution in execution_doc["records"]:
        prompt = prompts_by_id[execution["sequence_id"]]
        for key in (
            "source_sequence_id",
            "panel_range",
            "panel_count",
            "prompt_sha256",
            "input_references",
            "cross_panel_gate_phrases",
        ):
            if execution[key] != prompt[key]:
                raise ValueError(f"execution/prompt mismatch {execution['sequence_id']}:{key}")
        start, end = execution["panel_range"]
        panel_ids = expected_ids[start - 1:end]
        source = execution["output"]
        source_path = ROOT / source["path"]
        if not source_path.is_file():
            raise ValueError(f"premium-cel source is missing: {source['path']}")
        if sha256(source_path) != source["sha256"] or source_path.stat().st_size != source["bytes"]:
            raise ValueError(f"premium-cel execution output binding failed: {execution['sequence_id']}")
        with Image.open(source_path) as opened:
            image = opened.convert("RGB")
        if [image.width, image.height] != [source["width"], source["height"]]:
            raise ValueError(f"premium-cel execution dimensions failed: {execution['sequence_id']}")
        override = MANUAL_GUTTER_OVERRIDES.get(execution["sequence_id"])
        if override is None:
            boxes, gutters = panel_boxes(image, execution["panel_count"])
            mode = "row_dominance"
        else:
            gutters = override
            boxes = boxes_from_override(image, gutters)
            mode = "hash_pinned_manual_override"
        if len(boxes) != execution["panel_count"]:
            raise ValueError(f"panel count mismatch: {execution['sequence_id']}")

        crops = []
        for panel_id, box in zip(panel_ids, boxes, strict=True):
            plan = plan_by_id[panel_id]
            crops.append(
                {
                    "panel_id": panel_id,
                    "plan_revision_id": plan["plan_revision_id"],
                    "display_order": plan["display_order"],
                    "box": box,
                }
            )
        observed_ids.extend(panel_ids)
        sequences.append(
            {
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
                },
                "crops": crops,
            }
        )

    if observed_ids != expected_ids:
        raise ValueError("premium-cel crop coverage differs from ordered ComicPanelPlans")
    document = {
        "record_type": "CH05SequenceStripCropManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-premium-cel-crops-r1",
        "state": "HASH_PINNED_LOCAL_DERIVATIVE_PLAN_UNACCEPTED",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "comic_panel_plan_source": {
            "path": PLANS.relative_to(ROOT).as_posix(),
            "sha256": sha256(PLANS),
        },
        "prompt_manifest": {
            "path": PROMPTS.relative_to(ROOT).as_posix(),
            "sha256": sha256(PROMPTS),
        },
        "execution_manifest": {
            "path": EXECUTIONS.relative_to(ROOT).as_posix(),
            "sha256": sha256(EXECUTIONS),
        },
        "output_filename_template": "p{panel_number:03d}-premium-cel-r1.png",
        "summary": {
            "sequence_sources": len(sequences),
            "planned_crops": len(observed_ids),
            "complete_plan_coverage": True,
            "deterministic_gutter_detection": True,
            "manual_gutter_overrides": len(MANUAL_GUTTER_OVERRIDES),
        },
        "sequences": sequences,
        "boundary": (
            "Exact source strips and crops remain ignored local research pixels; no acceptance, commercial clearance, "
            "or exact production-base selection."
        ),
    }
    OUTPUT.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {"output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), **document["summary"]},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
