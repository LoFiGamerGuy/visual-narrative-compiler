"""Build the deterministic CH07 default-route review packet and provenance records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from build_ch06_default_route_review import (
    fit_width,
    labeled_canvas,
    panel_boxes,
    rel,
    sha256,
    stack,
    target_width,
    trim_horizontal_white,
)
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch07-sc01-panel-plans-r1.json"
PROMPTS = ROOT / "production/comic/run-manifests/ch06-ch07-default-house-route-prompt-manifest-r1.json"
SOURCE_DIR = ROOT / "experiments/review-packets/ch07-default-house-route-r1/source"
PACKET_DIR = ROOT / "experiments/review-packets/ch07-default-house-route-r1"
EXECUTION = ROOT / "production/comic/run-manifests/ch07-default-house-route-execution-r1.json"
PACKET = ROOT / "production/comic/run-manifests/ch07-default-house-route-review-packet-r1.json"

SOURCE_FILES = {
    "ng-ch07-s01-storm-prep": "ng-ch07-s01-storm-prep.png",
    "ng-ch07-s02-field-weapons": "ng-ch07-s02-field-weapons.png",
    "ng-ch07-s03-first-contact": "ng-ch07-s03-first-contact.png",
    "ng-ch07-s04-mud-trap": "ng-ch07-s04-mud-trap.png",
    "ng-ch07-s05-counterattack": "ng-ch07-s05-counterattack.png",
    "ng-ch07-s06-shelter-held": "ng-ch07-s06-shelter-held.png",
    "ng-ch07-s07-cost": "ng-ch07-s07-cost.png",
    "ng-ch07-s08-road-north": "ng-ch07-s08-road-north.png",
}

ELAPSED_SECONDS = {
    "ng-ch07-s01-storm-prep": 117.070,
    "ng-ch07-s02-field-weapons": 234.027,
    "ng-ch07-s03-first-contact": 370.189,
    "ng-ch07-s04-mud-trap": 497.196,
    "ng-ch07-s05-counterattack": 115.380,
    "ng-ch07-s06-shelter-held": 233.090,
    "ng-ch07-s07-cost": 342.941,
    "ng-ch07-s08-road-north": 460.672,
}

MANUAL_BOXES = {
    "ng-ch07-s01-storm-prep": [
        [0, 0, 1130, 440],
        [1135, 0, 1774, 440],
        [0, 446, 599, 882],
        [600, 446, 1134, 882],
        [1135, 446, 1768, 882],
    ],
    "ng-ch07-s03-first-contact": [
        [4, 3, 1686, 417],
        [4, 422, 340, 925],
        [344, 422, 843, 925],
        [845, 422, 1253, 925],
        [1256, 422, 1686, 925],
    ],
    "ng-ch07-s08-road-north": [
        [3, 54, 438, 389],
        [443, 54, 881, 389],
        [887, 54, 1385, 389],
        [1390, 54, 1770, 389],
        [3, 447, 1770, 882],
    ],
}


def crop_boxes(sequence_id: str, image: Image.Image) -> tuple[list[list[int]], dict[str, Any]]:
    if sequence_id in MANUAL_BOXES:
        return MANUAL_BOXES[sequence_id], {
            "method": "HASH_BOUND_MANUAL_GRID_BOXES",
            "boxes": MANUAL_BOXES[sequence_id],
        }
    boxes, gutters = panel_boxes(image)
    return boxes, {
        "method": "DETERMINISTIC_VERTICAL_GUTTER_DETECTION",
        "bright_threshold": 245,
        "column_dominance": 0.72,
        "cluster_join_px": 10,
        "clusters_inclusive": gutters,
    }


def triage(panel_id: str) -> tuple[str, list[str], str]:
    if panel_id == "ng-ch07-sc01-p009":
        return (
            "WARN",
            ["TAMSIN_HAIR_CONTINUITY_DRIFT"],
            "Tamsin's hair lightens substantially from CH06; role order and clothing remain clear.",
        )
    if panel_id == "ng-ch07-sc01-p030":
        return (
            "FAIL",
            ["UNREQUESTED_RENDERED_TEXT"],
            "The held shelter reads, but forbidden status prose is rendered on the gate.",
        )
    if panel_id == "ng-ch07-sc01-p040":
        return (
            "FAIL",
            ["WARDENS_REACH_FORM_DRIFT"],
            "The final departure is readable, but Warden's Reach drifts into an unexplained mechanical gun-like form.",
        )
    return (
        "PASS",
        [],
        "Default-route crop is story-readable at packet scale; owner review remains pending.",
    )


def main() -> int:
    plan_doc = json.loads(PLANS.read_text(encoding="utf-8"))
    prompt_doc = json.loads(PROMPTS.read_text(encoding="utf-8"))
    plans = sorted(plan_doc["plans"], key=lambda row: row["display_order"])
    requests = [row for row in prompt_doc["requests"] if row["chapter"] == "CH07"]
    if len(requests) != 8 or sum(len(row["panel_ids"]) for row in requests) != 40:
        raise ValueError("CH07 prompt manifest must cover eight five-panel sequences")

    crop_dir = PACKET_DIR / "crops"
    crop_dir.mkdir(parents=True, exist_ok=True)
    source_records = []
    crop_records = []
    panel_images: dict[str, Image.Image] = {}
    for request in requests:
        sequence_id = request["sequence_id"]
        source_path = SOURCE_DIR / SOURCE_FILES[sequence_id]
        if not source_path.is_file():
            raise ValueError(f"missing source output: {rel(source_path)}")
        with Image.open(source_path) as opened:
            source = opened.convert("RGB")
        boxes, crop_method = crop_boxes(sequence_id, source)
        source_record = {
            "render_record_id": f"ng-render-{sequence_id}-r1",
            "request_id": sequence_id,
            "chapter": "CH07",
            "panel_ids": request["panel_ids"],
            "exact_prompt": request["prompt"],
            "prompt_sha256": request["prompt_sha256"],
            "input_references": request["reference_images"],
            "output": {
                "path": rel(source_path),
                "sha256": sha256(source_path),
                "width": source.width,
                "height": source.height,
                "mime_type": "image/png",
            },
            "crop_method": crop_method,
            "model": None,
            "endpoint": None,
            "provider_request_id": None,
            "provider_usage": None,
            "monetary_cost_usd": None,
            "deterministic_seed": None,
            "elapsed_seconds": ELAPSED_SECONDS[sequence_id],
            "elapsed_source": "CLIENT_WRAPPER_DATE_NOW_AROUND_IMAGEGEN_CALL",
            "unavailable_fields": [
                "model",
                "endpoint",
                "provider_request_id",
                "provider_usage",
                "monetary_cost_usd",
                "deterministic_seed",
            ],
            "human_review_state": "AGENT_TRIAGED_OWNER_REVIEW_PENDING",
            "human_review_minutes": None,
            "accepted": False,
            "commercially_cleared": False,
            "exact_production_base": False,
            "reproducible": False,
        }
        source_records.append(source_record)
        for panel_id, box in zip(request["panel_ids"], boxes, strict=True):
            cropped = source.crop(tuple(box))
            if sequence_id == "ng-ch07-s07-cost":
                cropped = cropped.crop((0, 52, cropped.width, cropped.height))
                horizontal_trim = [52, cropped.height + 52]
            elif sequence_id in MANUAL_BOXES:
                horizontal_trim = [box[1], box[3]]
            else:
                cropped, horizontal_trim = trim_horizontal_white(cropped)
            panel_path = crop_dir / f"{panel_id}-default-r1.png"
            cropped.save(panel_path, format="PNG", optimize=False, compress_level=9)
            panel_images[panel_id] = cropped
            state, failure_classes, note = triage(panel_id)
            crop_records.append(
                {
                    "candidate_id": f"ng-candidate-{panel_id}-default-r1",
                    "panel_id": panel_id,
                    "sequence_id": sequence_id,
                    "source_render_record_id": source_record["render_record_id"],
                    "source_box": box,
                    "horizontal_trim": horizontal_trim,
                    "path": rel(panel_path),
                    "sha256": sha256(panel_path),
                    "width": cropped.width,
                    "height": cropped.height,
                    "agent_triage": state,
                    "failure_classes": failure_classes,
                    "triage_note": note,
                    "human_review_state": "OWNER_REVIEW_PENDING",
                    "human_review_minutes": None,
                    "accepted": False,
                    "commercially_cleared": False,
                    "exact_production_base": False,
                }
            )
    if [row["panel_id"] for row in crop_records] != [row["panel_id"] for row in plans]:
        raise ValueError("render crop order does not match the ordered CH07 ComicPanelPlans")

    contact_cells = [
        labeled_canvas(panel_images[row["panel_id"]], f"P{row['display_order']:03d} · {row['scale_role']}", 238)
        for row in plans
    ]
    rows = []
    for offset in range(0, len(contact_cells), 5):
        group = contact_cells[offset:offset + 5]
        row_height = max(item.height for item in group)
        row_image = Image.new("RGB", (1200, row_height), "#11151b")
        for index, item in enumerate(group):
            row_image.paste(item, (index * 240, 0))
        rows.append(row_image)
    contact = stack(rows, 1200, 2, "#11151b")
    contact_path = PACKET_DIR / "ch07-contact-sheet-r1.png"
    contact.save(contact_path, format="PNG", compress_level=9)

    sequence_rows = []
    for request in requests:
        with Image.open(SOURCE_DIR / SOURCE_FILES[request["sequence_id"]]) as opened:
            image = fit_width(opened.convert("RGB"), 1160)
        sequence_rows.append(labeled_canvas(image, request["sequence_id"], 1200, 38))
    sequence_contact = stack(sequence_rows, 1200, 10, "#11151b")
    sequence_path = PACKET_DIR / "ch07-sequence-contact-sheet-r1.png"
    sequence_contact.save(sequence_path, format="PNG", compress_level=9)

    reading = stack([fit_width(panel_images[row["panel_id"]], target_width(row)) for row in plans], 800, 20, "#ece8df")
    reading_path = PACKET_DIR / "ch07-complete-reading-draft-r1.png"
    reading.save(reading_path, format="PNG", compress_level=9)
    phone = stack([fit_width(panel_images[row["panel_id"]], 374) for row in plans], 390, 10, "#ece8df")
    phone_path = PACKET_DIR / "ch07-phone-preview-r1.png"
    phone.save(phone_path, format="PNG", compress_level=9)

    overlay_cells = []
    for row in plans:
        image = panel_images[row["panel_id"]].copy().convert("RGBA")
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        for zone in row["comic_direction"]["lettering"]["safe_zones"]:
            x, y, width, height = zone["rect_norm"]
            box = (
                round(x * image.width),
                round(y * image.height),
                round((x + width) * image.width),
                round((y + height) * image.height),
            )
            draw.rectangle(box, fill=(35, 206, 235, 70), outline=(35, 206, 235, 230), width=max(2, image.width // 300))
        overlay_cells.append(labeled_canvas(Image.alpha_composite(image, layer).convert("RGB"), f"P{row['display_order']:03d} lettering-safe zone", 238))
    overlay_rows = []
    for offset in range(0, len(overlay_cells), 5):
        group = overlay_cells[offset:offset + 5]
        row_height = max(item.height for item in group)
        row_image = Image.new("RGB", (1200, row_height), "#11151b")
        for index, item in enumerate(group):
            row_image.paste(item, (index * 240, 0))
        overlay_rows.append(row_image)
    overlay = stack(overlay_rows, 1200, 2, "#11151b")
    overlay_path = PACKET_DIR / "ch07-lettering-safe-zone-overlay-r1.png"
    overlay.save(overlay_path, format="PNG", compress_level=9)

    execution_doc = {
        "record_type": "BuiltInImageGenExecutionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch07-default-house-route-execution-r1",
        "state": "EXECUTED_AGENT_TRIAGED_OWNER_REVIEW_PENDING",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "prompt_manifest": {"path": rel(PROMPTS), "sha256": sha256(PROMPTS)},
        "comic_panel_plan_collection": {"path": rel(PLANS), "sha256": sha256(PLANS)},
        "records": source_records,
        "summary": {
            "chapter": "CH07",
            "sequence_outputs": 8,
            "panel_candidates": 40,
            "authorized_reference_uses": sum(len(row["input_references"]) for row in source_records),
            "client_observed_elapsed_seconds_sum": round(sum(ELAPSED_SECONDS.values()), 3),
            "parallel_group_wall_seconds": [497.196, 460.672],
            "paid_api_cloud_spend_usd": 0,
            "built_in_monetary_cost_disclosed": False,
            "accepted": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
        "timing_note": "Per-request values are client-observed wall intervals. Their sum is not total wall time because requests ran in two parallel groups.",
        "boundary": "Ignored generated pixels are research evidence. No new output was re-uploaded. Null service fields are unavailable, not zero.",
    }
    EXECUTION.parent.mkdir(parents=True, exist_ok=True)
    EXECUTION.write_text(json.dumps(execution_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    artifacts = []
    for artifact_type, path in (
        ("contact_sheet", contact_path),
        ("sequence_contact_sheet", sequence_path),
        ("complete_reading_draft", reading_path),
        ("phone_preview", phone_path),
        ("lettering_safe_zone_overlay", overlay_path),
    ):
        with Image.open(path) as opened:
            width, height = opened.size
        artifacts.append({"type": artifact_type, "path": rel(path), "sha256": sha256(path), "width": width, "height": height})
    triage_counts = {state: sum(row["agent_triage"] == state for row in crop_records) for state in ("PASS", "WARN", "FAIL")}
    packet_doc = {
        "record_type": "ComicChapterReviewPacketManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch07-default-house-route-review-packet-r1",
        "state": "OWNER_REVIEW_PENDING",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "execution_manifest": {"path": rel(EXECUTION), "sha256": sha256(EXECUTION)},
        "candidates": crop_records,
        "artifacts": artifacts,
        "summary": {
            "complete_chapter": True,
            "panel_plans": 40,
            "selected_default_candidates": 40,
            "sequence_sources": 8,
            "triage": triage_counts,
            "targeted_repairs_executed": 0,
            "whole_chapter_alternate_arms": 0,
        },
        "limitations": [
            "P009 warns because Tamsin's hair lightens substantially relative to CH06; role and clothing remain distinct.",
            "P030 fails the no-rendered-text contract because the gate carries unrequested status prose.",
            "P040 fails equipment continuity because Warden's Reach becomes an unexplained mechanical gun-like form.",
            "S07/S08 source numbering is excluded through recorded deterministic crop bounds; source evidence remains unchanged.",
            "Built-in model, endpoint, request ID, usage, monetary cost, and deterministic seed were unavailable.",
            "Agent triage is non-gating; acceptance, rights, commercial clearance, reproducibility, and exact-base selection remain pending or false.",
        ],
    }
    PACKET.write_text(json.dumps(packet_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"artifacts": len(artifacts), "candidates": len(crop_records), "sequences": len(source_records), "triage": triage_counts, "elapsed_sum": execution_doc["summary"]["client_observed_elapsed_seconds_sum"], "packet_sha256": sha256(PACKET)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
