"""Detect clean strip gutters and compile hash-pinned CH05 alternate graphic crops."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
EXECUTIONS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-alt-graphic-execution-manifest-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-alt-graphic-crops-r1.json"
SEPARATOR_DOMINANCE = 0.72
SEPARATOR_JOIN_DISTANCE_PX = 14
EDGE_CLUSTER_PX = 15


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def separator_clusters(image: Image.Image) -> list[tuple[int, int]]:
    gray = image.convert("L")
    width, height = gray.size
    pixels = memoryview(gray.tobytes())
    threshold = int(width * SEPARATOR_DOMINANCE)
    rows: list[int] = []
    for y in range(height):
        row = pixels[y * width:(y + 1) * width]
        bright = sum(value > 245 for value in row)
        dark = sum(value < 15 for value in row)
        if max(bright, dark) > threshold:
            rows.append(y)
    clusters: list[tuple[int, int]] = []
    if rows:
        start = previous = rows[0]
        for y in rows[1:]:
            if y - previous > SEPARATOR_JOIN_DISTANCE_PX:
                clusters.append((start, previous))
                start = y
            previous = y
        clusters.append((start, previous))
    return clusters


def panel_boxes(image: Image.Image, panel_count: int) -> tuple[list[list[int]], list[list[int]]]:
    width, height = image.size
    clusters = separator_clusters(image)
    content_top, content_bottom = 0, height
    if clusters and clusters[0][0] <= EDGE_CLUSTER_PX:
        content_top = clusters.pop(0)[1] + 1
    if clusters and clusters[-1][1] >= height - 1 - EDGE_CLUSTER_PX:
        content_bottom = clusters.pop()[0]
    if len(clusters) != panel_count - 1:
        raise ValueError(f"expected {panel_count - 1} internal gutters, detected {len(clusters)}: {clusters}")
    boxes: list[list[int]] = []
    top = content_top
    for start, end in clusters:
        if start <= top:
            raise ValueError("non-positive crop caused by separator detection")
        boxes.append([0, top, width, start])
        top = end + 1
    if content_bottom <= top:
        raise ValueError("non-positive final crop caused by separator detection")
    boxes.append([0, top, width, content_bottom])
    return boxes, [[start, end] for start, end in clusters]


def main() -> int:
    execution_doc = json.loads(EXECUTIONS.read_text(encoding="utf-8"))
    plans = json.loads(PLANS.read_text(encoding="utf-8"))["plans"]
    expected_ids = [row["panel_id"] for row in sorted(plans, key=lambda row: row["display_order"])]
    sequences = []
    observed_ids: list[str] = []
    for record in execution_doc["records"]:
        start, end = record["panel_range"]
        panel_ids = expected_ids[start - 1:end]
        source = record["output"]
        source_path = ROOT / source["path"]
        if not source_path.is_file() or sha256(source_path) != source["sha256"]:
            raise ValueError(f"source binding failed: {source['path']}")
        with Image.open(source_path) as opened:
            image = opened.convert("RGB")
        boxes, gutters = panel_boxes(image, record["panel_count"])
        crops = [{"panel_id": panel_id, "box": box} for panel_id, box in zip(panel_ids, boxes, strict=True)]
        observed_ids.extend(panel_ids)
        sequences.append({
            "sequence_id": record["source_sequence_id"],
            "execution_sequence_id": record["sequence_id"],
            "source": source,
            "gutter_detection": {"dominance_threshold": SEPARATOR_DOMINANCE, "join_distance_px": SEPARATOR_JOIN_DISTANCE_PX, "edge_cluster_px": EDGE_CLUSTER_PX, "detected_internal_gutter_extents_inclusive": gutters},
            "crops": crops,
        })
    if observed_ids != expected_ids:
        raise ValueError("crop coverage differs from ordered ComicPanelPlans")
    document = {
        "record_type": "CH05SequenceStripCropManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-alt-graphic-crops-r1",
        "state": "HASH_PINNED_LOCAL_DERIVATIVE_PLAN_UNACCEPTED",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "comic_panel_plan_source": {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha256(PLANS)},
        "execution_manifest": {"path": EXECUTIONS.relative_to(ROOT).as_posix(), "sha256": sha256(EXECUTIONS)},
        "output_filename_template": "p{panel_number:03d}-alt-graphic-r1.png",
        "summary": {"sequence_sources": len(sequences), "planned_crops": len(observed_ids), "complete_plan_coverage": True, "deterministic_gutter_detection": True},
        "sequences": sequences,
        "boundary": "Exact source strips and crops remain ignored local research pixels; this manifest creates no acceptance, commercial clearance, or exact production-base selection.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), **document["summary"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
