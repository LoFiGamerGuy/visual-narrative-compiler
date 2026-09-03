"""Build the deterministic CH06 default-route review packet and provenance records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch06-sc01-panel-plans-r1.json"
PROMPTS = ROOT / "production/comic/run-manifests/ch06-ch07-default-house-route-prompt-manifest-r1.json"
SOURCE_DIR = ROOT / "experiments/review-packets/ch06-default-house-route-r1/source"
PACKET_DIR = ROOT / "experiments/review-packets/ch06-default-house-route-r1"
EXECUTION = ROOT / "production/comic/run-manifests/ch06-default-house-route-execution-r1.json"
PACKET = ROOT / "production/comic/run-manifests/ch06-default-house-route-review-packet-r1.json"
BRIGHT_THRESHOLD = 245
COLUMN_DOMINANCE = 0.72
CLUSTER_JOIN_PX = 10

SOURCE_FILES = {
    "ng-ch06-s01-ridge-return": "ng-ch06-s01-ridge-return.png",
    "ng-ch06-s02-encirclement": "ng-ch06-s02-encirclement.png",
    "ng-ch06-s03-two-entries": "ng-ch06-s03-two-entries.png",
    "ng-ch06-s04-hearth-stranger": "ng-ch06-s04-hearth-stranger.png",
    "ng-ch06-s05-counterweight": "ng-ch06-s05-counterweight.png",
    "ng-ch06-s06-cellar-node": "ng-ch06-s06-cellar-node.png",
    "ng-ch06-s07-terms": "ng-ch06-s07-terms.png",
    "ng-ch06-s08-gate-omen": "ng-ch06-s08-gate-omen.png",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def clusters(values: list[int]) -> list[tuple[int, int]]:
    if not values:
        return []
    output: list[tuple[int, int]] = []
    start = previous = values[0]
    for value in values[1:]:
        if value - previous > CLUSTER_JOIN_PX:
            output.append((start, previous))
            start = value
        previous = value
    output.append((start, previous))
    return output


def panel_boxes(image: Image.Image) -> tuple[list[list[int]], list[list[int]]]:
    gray = image.convert("L")
    width, height = gray.size
    pixels = gray.load()
    separators = []
    for x in range(width):
        bright = sum(pixels[x, y] > BRIGHT_THRESHOLD for y in range(height))
        if bright / height > COLUMN_DOMINANCE:
            separators.append(x)
    detected = clusters(separators)
    if len(detected) != 6:
        raise ValueError(f"expected two edge and four internal gutter clusters, got {detected}")
    if detected[0][0] > 12 or detected[-1][1] < width - 13:
        raise ValueError(f"gutter clusters do not bind both image edges: {detected}")
    boxes: list[list[int]] = []
    left = detected[0][1] + 1
    for start, end in detected[1:-1]:
        boxes.append([left, 0, start, height])
        left = end + 1
    boxes.append([left, 0, detected[-1][0], height])
    if len(boxes) != 5 or any(box[2] <= box[0] for box in boxes):
        raise ValueError(f"invalid five-panel boxes: {boxes}")
    return boxes, [[start, end] for start, end in detected]


def trim_horizontal_white(image: Image.Image) -> tuple[Image.Image, list[int]]:
    gray = image.convert("L")
    width, height = gray.size
    pixels = gray.load()
    white_rows = []
    for y in range(height):
        if sum(pixels[x, y] > BRIGHT_THRESHOLD for x in range(width)) / width > 0.84:
            white_rows.append(y)
    row_clusters = clusters(white_rows)
    top, bottom = 0, height
    if row_clusters and row_clusters[0][0] <= 12:
        top = row_clusters[0][1] + 1
    if row_clusters and row_clusters[-1][1] >= height - 13:
        bottom = row_clusters[-1][0]
    if bottom - top < int(height * 0.7):
        raise ValueError(f"horizontal trim would remove too much content: {top}, {bottom}, {height}")
    return image.crop((0, top, width, bottom)), [top, bottom]


def fit_width(image: Image.Image, width: int) -> Image.Image:
    height = max(1, round(image.height * width / image.width))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def labeled_canvas(image: Image.Image, label: str, width: int, label_height: int = 34) -> Image.Image:
    thumb = ImageOps.contain(image, (width, 260), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, thumb.height + label_height), "#11151b")
    canvas.paste(thumb, ((width - thumb.width) // 2, label_height))
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 7), label, fill="#e9edf2", font=font(16))
    return canvas


def stack(images: list[Image.Image], width: int, gap: int, background: str) -> Image.Image:
    height = sum(image.height for image in images) + gap * max(0, len(images) - 1)
    output = Image.new("RGB", (width, height), background)
    y = 0
    for image in images:
        output.paste(image, ((width - image.width) // 2, y))
        y += image.height + gap
    return output


def target_width(plan: dict[str, Any]) -> int:
    role = plan["scale_role"]
    if role.startswith(("LARGE_HERO", "WIDE")):
        return 720
    if role.startswith("TALL"):
        return 480
    if role.startswith("SMALL"):
        return 420
    return 600


def main() -> int:
    plan_doc = json.loads(PLANS.read_text(encoding="utf-8"))
    prompt_doc = json.loads(PROMPTS.read_text(encoding="utf-8"))
    plans = sorted(plan_doc["plans"], key=lambda row: row["display_order"])
    requests = [row for row in prompt_doc["requests"] if row["chapter"] == "CH06"]
    if len(requests) != 8 or sum(len(row["panel_ids"]) for row in requests) != 40:
        raise ValueError("CH06 prompt manifest must cover eight five-panel sequences")

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
        boxes, gutters = panel_boxes(source)
        source_record = {
            "render_record_id": f"ng-render-{sequence_id}-r1",
            "request_id": sequence_id,
            "chapter": "CH06",
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
            "gutter_detection": {
                "bright_threshold": BRIGHT_THRESHOLD,
                "column_dominance": COLUMN_DOMINANCE,
                "cluster_join_px": CLUSTER_JOIN_PX,
                "clusters_inclusive": gutters,
            },
            "model": None,
            "endpoint": None,
            "provider_request_id": None,
            "provider_usage": None,
            "monetary_cost_usd": None,
            "deterministic_seed": None,
            "elapsed_seconds": None,
            "unavailable_fields": [
                "model",
                "endpoint",
                "provider_request_id",
                "provider_usage",
                "monetary_cost_usd",
                "deterministic_seed",
                "elapsed_seconds",
            ],
            "timing_note": "The built-in product and client wrapper exposed no per-request elapsed time; null is unavailable, not zero.",
            "human_review_state": "AGENT_TRIAGED_OWNER_REVIEW_PENDING",
            "human_review_minutes": None,
            "accepted": False,
            "commercially_cleared": False,
            "exact_production_base": False,
            "reproducible": False,
        }
        source_records.append(source_record)
        for panel_id, box in zip(request["panel_ids"], boxes, strict=True):
            cropped, horizontal_trim = trim_horizontal_white(source.crop(tuple(box)))
            panel_path = crop_dir / f"{panel_id}-default-r1.png"
            cropped.save(panel_path, format="PNG", optimize=False, compress_level=9)
            panel_images[panel_id] = cropped
            triage = "PASS"
            failure_classes: list[str] = []
            note = "Default-route crop is story-readable at packet scale; owner review remains pending."
            if panel_id == "ng-ch06-sc01-p020":
                triage = "WARN"
                failure_classes = ["TAMSIN_SIGRID_FACE_SIMILARITY"]
                note = "Tamsin and Sigrid remain garment-distinct, but their dark-haired facial rendering is similar."
            if panel_id == "ng-ch06-sc01-p030":
                triage = "FAIL"
                failure_classes = ["UNREQUESTED_RENDERED_TEXT"]
                note = "The physical Ledger is readable, but the generator rendered forbidden prose on the mechanism."
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
                    "agent_triage": triage,
                    "failure_classes": failure_classes,
                    "triage_note": note,
                    "human_review_state": "OWNER_REVIEW_PENDING",
                    "human_review_minutes": None,
                    "accepted": False,
                    "commercially_cleared": False,
                    "exact_production_base": False,
                }
            )

    observed = [row["panel_id"] for row in crop_records]
    expected = [row["panel_id"] for row in plans]
    if observed != expected:
        raise ValueError("render crop order does not match the ordered CH06 ComicPanelPlans")

    contact_cells = [
        labeled_canvas(panel_images[row["panel_id"]], f"P{row['display_order']:03d} · {row['scale_role']}", 238)
        for row in plans
    ]
    rows = []
    for offset in range(0, len(contact_cells), 5):
        group = contact_cells[offset:offset + 5]
        row_height = max(item.height for item in group)
        row_image = Image.new("RGB", (1200, row_height), "#11151b")
        x = 0
        for item in group:
            row_image.paste(item, (x, 0))
            x += 240
        rows.append(row_image)
    contact = stack(rows, 1200, 2, "#11151b")
    contact_path = PACKET_DIR / "ch06-contact-sheet-r1.png"
    contact.save(contact_path, format="PNG", compress_level=9)

    sequence_rows = []
    for request in requests:
        source_path = SOURCE_DIR / SOURCE_FILES[request["sequence_id"]]
        with Image.open(source_path) as opened:
            image = fit_width(opened.convert("RGB"), 1160)
        sequence_rows.append(labeled_canvas(image, request["sequence_id"], 1200, 38))
    sequence_contact = stack(sequence_rows, 1200, 10, "#11151b")
    sequence_path = PACKET_DIR / "ch06-sequence-contact-sheet-r1.png"
    sequence_contact.save(sequence_path, format="PNG", compress_level=9)

    reading_panels = [fit_width(panel_images[row["panel_id"]], target_width(row)) for row in plans]
    reading = stack(reading_panels, 800, 20, "#ece8df")
    reading_path = PACKET_DIR / "ch06-complete-reading-draft-r1.png"
    reading.save(reading_path, format="PNG", compress_level=9)

    phone_panels = [fit_width(panel_images[row["panel_id"]], 374) for row in plans]
    phone = stack(phone_panels, 390, 10, "#ece8df")
    phone_path = PACKET_DIR / "ch06-phone-preview-r1.png"
    phone.save(phone_path, format="PNG", compress_level=9)

    overlay_cells = []
    for row in plans:
        image = panel_images[row["panel_id"]].copy().convert("RGBA")
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        for zone in row["comic_direction"]["lettering"]["safe_zones"]:
            x, y, w, h = zone["rect_norm"]
            box = (round(x * image.width), round(y * image.height), round((x + w) * image.width), round((y + h) * image.height))
            draw.rectangle(box, fill=(35, 206, 235, 70), outline=(35, 206, 235, 230), width=max(2, image.width // 300))
        composited = Image.alpha_composite(image, layer).convert("RGB")
        overlay_cells.append(labeled_canvas(composited, f"P{row['display_order']:03d} lettering-safe zone", 238))
    overlay_rows = []
    for offset in range(0, len(overlay_cells), 5):
        group = overlay_cells[offset:offset + 5]
        row_height = max(item.height for item in group)
        row_image = Image.new("RGB", (1200, row_height), "#11151b")
        for index, item in enumerate(group):
            row_image.paste(item, (index * 240, 0))
        overlay_rows.append(row_image)
    overlay = stack(overlay_rows, 1200, 2, "#11151b")
    overlay_path = PACKET_DIR / "ch06-lettering-safe-zone-overlay-r1.png"
    overlay.save(overlay_path, format="PNG", compress_level=9)

    execution_doc = {
        "record_type": "BuiltInImageGenExecutionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch06-default-house-route-execution-r1",
        "state": "EXECUTED_AGENT_TRIAGED_OWNER_REVIEW_PENDING",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "prompt_manifest": {"path": rel(PROMPTS), "sha256": sha256(PROMPTS)},
        "comic_panel_plan_collection": {"path": rel(PLANS), "sha256": sha256(PLANS)},
        "records": source_records,
        "summary": {
            "chapter": "CH06",
            "sequence_outputs": 8,
            "panel_candidates": 40,
            "authorized_reference_uses": sum(len(row["input_references"]) for row in source_records),
            "paid_api_cloud_spend_usd": 0,
            "built_in_monetary_cost_disclosed": False,
            "individual_elapsed_times_disclosed": False,
            "accepted": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
        "boundary": "Ignored generated pixels are research evidence. No new output was re-uploaded. Null service and timing fields are unavailable, not zero.",
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
        "record_id": "ng-ch06-default-house-route-review-packet-r1",
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
            "P020 has a role-separation warning because Tamsin and Sigrid have similar dark-haired facial rendering despite distinct garments.",
            "P030 fails the no-rendered-text contract; it remains diagnostic evidence eligible for one narrow repair after full-chapter review.",
            "The S08 source added panel numerals in a white footer; deterministic horizontal cropping excludes that footer from panel candidates.",
            "Built-in model, endpoint, request ID, usage, monetary cost, deterministic seed, and per-request elapsed time were unavailable.",
            "Agent triage is non-gating. Human review, acceptance, rights, commercial clearance, reproducibility, and exact-base selection remain pending or false.",
        ],
    }
    PACKET.write_text(json.dumps(packet_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"artifacts": len(artifacts), "candidates": len(crop_records), "sequences": len(source_records), "triage": triage_counts, "packet_sha256": sha256(PACKET)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
