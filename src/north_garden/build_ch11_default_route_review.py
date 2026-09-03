"""Build deterministic CH11 RenderRecords, crops, and chapter review artifacts."""

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
PLANS = ROOT / "production/comic/ch11-sc01-panel-plans-r1.json"
PROMPTS = ROOT / "production/comic/run-manifests/ch10-ch11-default-house-route-prompt-manifest-r1.json"
PACKET_DIR = ROOT / "experiments/review-packets/ch11-default-house-route-r1"
SOURCE_DIR = PACKET_DIR / "source"
EXECUTION = ROOT / "production/comic/run-manifests/ch11-default-house-route-execution-r1.json"
PACKET = ROOT / "production/comic/run-manifests/ch11-default-house-route-review-packet-r1.json"
SOURCE_FILES = {
    "ng-ch11-s01-siege-alarm": "ng-ch11-s01-siege-alarm.png",
    "ng-ch11-s02-adult-defense": "ng-ch11-s02-adult-defense.png",
    "ng-ch11-s03-terrace-contact": "ng-ch11-s03-terrace-contact.png",
    "ng-ch11-s04-water-firebreak": "ng-ch11-s04-water-firebreak.png",
    "ng-ch11-s05-sequential-gates": "ng-ch11-s05-sequential-gates.png",
    "ng-ch11-s06-opposite-heights": "ng-ch11-s06-opposite-heights.png",
    "ng-ch11-s07-two-hands": "ng-ch11-s07-two-hands.png",
    "ng-ch11-s08-cost-and-map": "ng-ch11-s08-cost-and-map.png",
}
ELAPSED_SECONDS = {
    "ng-ch11-s01-siege-alarm": 109.933,
    "ng-ch11-s02-adult-defense": 227.383,
    "ng-ch11-s03-terrace-contact": 330.874,
    "ng-ch11-s04-water-firebreak": 442.406,
    "ng-ch11-s05-sequential-gates": 113.317,
    "ng-ch11-s06-opposite-heights": 230.532,
    "ng-ch11-s07-two-hands": 331.057,
    "ng-ch11-s08-cost-and-map": 429.358,
}


def source_boxes(sequence_id: str, image: Image.Image) -> tuple[list[list[int]], dict[str, Any]]:
    boxes, gutters = panel_boxes(image)
    return boxes, {
        "method": "DETERMINISTIC_VERTICAL_GUTTER_DETECTION",
        "bright_threshold": 245,
        "column_dominance": 0.72,
        "cluster_join_px": 10,
        "clusters_inclusive": gutters,
    }


def triage(panel_id: str) -> tuple[str, list[str], str]:
    if panel_id in {
        "ng-ch11-sc01-p003",
        "ng-ch11-sc01-p008",
        "ng-ch11-sc01-p013",
        "ng-ch11-sc01-p025",
    }:
        return (
            "FAIL",
            ["HALVOR_ROLE_IDENTITY_SUBSTITUTION"],
            "Halvor's authored action is assigned to a Soren-like pale-coated blond adult, weakening role continuity in the siege.",
        )
    if panel_id == "ng-ch11-sc01-p040":
        return (
            "WARN",
            ["TAMSIN_BRAID_NOT_LEGIBLE"],
            "Tamsin is distinct and chestnut-haired, but her practical braid is not clearly visible in the final map reveal.",
        )
    return (
        "PASS",
        [],
        "Default-route crop is story-readable at packet scale; owner review remains pending.",
    )


def create_grid(images: list[Image.Image]) -> Image.Image:
    rows = []
    for offset in range(0, len(images), 5):
        group = images[offset:offset + 5]
        height = max(image.height for image in group)
        row = Image.new("RGB", (1200, height), "#11151b")
        for index, image in enumerate(group):
            row.paste(image, (index * 240, 0))
        rows.append(row)
    return stack(rows, 1200, 2, "#11151b")


def main() -> int:
    plans = sorted(json.loads(PLANS.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    prompt_doc = json.loads(PROMPTS.read_text(encoding="utf-8"))
    requests = [row for row in prompt_doc["requests"] if row["chapter"] == "CH11"]
    if len(requests) != 8 or sum(len(row["panel_ids"]) for row in requests) != 40:
        raise ValueError("CH11 must have eight preflighted five-panel sequences")
    crop_dir = PACKET_DIR / "crops"
    crop_dir.mkdir(parents=True, exist_ok=True)
    source_records = []
    candidates = []
    panel_images: dict[str, Image.Image] = {}
    for request in requests:
        sequence_id = request["sequence_id"]
        source_path = SOURCE_DIR / SOURCE_FILES[sequence_id]
        with Image.open(source_path) as opened:
            source = opened.convert("RGB")
        boxes, method = source_boxes(sequence_id, source)
        render_id = f"ng-render-{sequence_id}-r1"
        source_records.append(
            {
                "render_record_id": render_id,
                "request_id": sequence_id,
                "chapter": "CH11",
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
                "crop_method": method,
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
        )
        for panel_id, box in zip(request["panel_ids"], boxes, strict=True):
            image = source.crop(tuple(box))
            image, trim = trim_horizontal_white(image)
            path = crop_dir / f"{panel_id}-default-r1.png"
            image.save(path, format="PNG", compress_level=9)
            panel_images[panel_id] = image
            state, failures, note = triage(panel_id)
            candidates.append(
                {
                    "candidate_id": f"ng-candidate-{panel_id}-default-r1",
                    "panel_id": panel_id,
                    "sequence_id": sequence_id,
                    "source_render_record_id": render_id,
                    "source_box": box,
                    "horizontal_trim": trim,
                    "path": rel(path),
                    "sha256": sha256(path),
                    "width": image.width,
                    "height": image.height,
                    "agent_triage": state,
                    "failure_classes": failures,
                    "triage_note": note,
                    "human_review_state": "OWNER_REVIEW_PENDING",
                    "human_review_minutes": None,
                    "accepted": False,
                    "commercially_cleared": False,
                    "exact_production_base": False,
                }
            )
    if [row["panel_id"] for row in candidates] != [row["panel_id"] for row in plans]:
        raise ValueError("candidate order differs from the 40 ordered CH11 plans")

    contact_cells = [
        labeled_canvas(panel_images[row["panel_id"]], f"P{row['display_order']:03d} · {row['scale_role']}", 238)
        for row in plans
    ]
    contact_path = PACKET_DIR / "ch11-contact-sheet-r1.png"
    create_grid(contact_cells).save(contact_path, format="PNG", compress_level=9)
    sequence_rows = []
    for request in requests:
        with Image.open(SOURCE_DIR / SOURCE_FILES[request["sequence_id"]]) as opened:
            sequence_rows.append(labeled_canvas(fit_width(opened.convert("RGB"), 1160), request["sequence_id"], 1200, 38))
    sequence_path = PACKET_DIR / "ch11-sequence-contact-sheet-r1.png"
    stack(sequence_rows, 1200, 10, "#11151b").save(sequence_path, format="PNG", compress_level=9)
    reading_path = PACKET_DIR / "ch11-complete-reading-draft-r1.png"
    stack([fit_width(panel_images[row["panel_id"]], target_width(row)) for row in plans], 800, 20, "#ece8df").save(reading_path, format="PNG", compress_level=9)
    phone_path = PACKET_DIR / "ch11-phone-preview-r1.png"
    stack([fit_width(panel_images[row["panel_id"]], 374) for row in plans], 390, 10, "#ece8df").save(phone_path, format="PNG", compress_level=9)
    overlays = []
    for row in plans:
        image = panel_images[row["panel_id"]].copy().convert("RGBA")
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        for zone in row["comic_direction"]["lettering"]["safe_zones"]:
            x, y, width, height = zone["rect_norm"]
            box = (round(x * image.width), round(y * image.height), round((x + width) * image.width), round((y + height) * image.height))
            draw.rectangle(box, fill=(35, 206, 235, 70), outline=(35, 206, 235, 230), width=max(2, image.width // 300))
        overlays.append(labeled_canvas(Image.alpha_composite(image, layer).convert("RGB"), f"P{row['display_order']:03d} lettering-safe zone", 238))
    overlay_path = PACKET_DIR / "ch11-lettering-safe-zone-overlay-r1.png"
    create_grid(overlays).save(overlay_path, format="PNG", compress_level=9)

    elapsed_sum = round(sum(ELAPSED_SECONDS.values()), 3)
    execution_doc = {
        "record_type": "BuiltInImageGenExecutionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch11-default-house-route-execution-r1",
        "state": "EXECUTED_AGENT_TRIAGED_OWNER_REVIEW_PENDING",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "prompt_manifest": {"path": rel(PROMPTS), "sha256": sha256(PROMPTS)},
        "comic_panel_plan_collection": {"path": rel(PLANS), "sha256": sha256(PLANS)},
        "records": source_records,
        "summary": {
            "chapter": "CH11",
            "sequence_outputs": 8,
            "panel_candidates": 40,
            "authorized_reference_uses": sum(len(row["input_references"]) for row in source_records),
            "client_observed_elapsed_seconds_sum": elapsed_sum,
            "parallel_group_wall_seconds": [442.406, 429.358],
            "paid_api_cloud_spend_usd": 0,
            "built_in_monetary_cost_disclosed": False,
            "accepted": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
        "timing_note": "Per-request wall intervals overlap within two parallel groups; their sum is not total wall time.",
        "boundary": "Ignored generated pixels are research evidence. No output was re-uploaded; null service fields are unavailable, not zero.",
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
    counts = {state: sum(row["agent_triage"] == state for row in candidates) for state in ("PASS", "WARN", "FAIL")}
    packet_doc = {
        "record_type": "ComicChapterReviewPacketManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch11-default-house-route-review-packet-r1",
        "state": "OWNER_REVIEW_PENDING",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "execution_manifest": {"path": rel(EXECUTION), "sha256": sha256(EXECUTION)},
        "candidates": candidates,
        "artifacts": artifacts,
        "summary": {
            "complete_chapter": True,
            "panel_plans": 40,
            "selected_default_candidates": 40,
            "sequence_sources": 8,
            "triage": counts,
            "targeted_repairs_executed": 0,
            "whole_chapter_alternate_arms": 0,
        },
        "limitations": [
            "P003, P008, P013, and P025 fail because Halvor's authored action is assigned to a Soren-like pale-coated blond adult.",
            "P040 warns because Tamsin's chestnut hair is distinct but the practical braid is not clearly visible.",
            "Rigid brace, forged gear, quarry armor, adult faction identities, and Mireback continuity are text-defined because new outputs cannot be re-uploaded as references.",
            "The one-row/no-number, nonverbal-Ledger, anti-firearm polehook, lead-character hair, monster anatomy, and causal-action controls remain effective; secondary-character identity is the repeated weakness.",
            "Built-in model, endpoint, request IDs, usage, monetary cost, and seeds remain unavailable.",
            "Agent triage is non-gating; acceptance, rights, clearance, reproducibility, and exact-base status remain pending or false.",
        ],
    }
    PACKET.write_text(json.dumps(packet_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"artifacts": 5, "candidates": 40, "elapsed_sum": elapsed_sum, "packet_sha256": sha256(PACKET), "sequences": 8, "triage": counts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


