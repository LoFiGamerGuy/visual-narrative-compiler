"""Build deterministic sparse local-lettering review editions for CH06-CH13."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from build_ch06_default_route_review import (
    fit_width,
    font,
    labeled_canvas,
    rel,
    sha256,
    stack,
    target_width,
)
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
COPY = ROOT / "production/comic/ch06-ch13-lettering-copy-r1.json"
MANIFEST = ROOT / "production/comic/run-manifests/ch06-ch13-local-lettering-review-r1.json"
OUT_DIR = ROOT / "experiments/review-packets/ch06-ch13-local-lettering-review-r1"
CHAPTERS = tuple(f"ch{number:02d}" for number in range(6, 14))


def wrap(draw: ImageDraw.ImageDraw, text: str, selected_font: Any, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=selected_font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_copy(draw: ImageDraw.ImageDraw, text: str, width: int, height: int) -> tuple[Any, list[str], int]:
    for size in range(34, 11, -1):
        selected = font(size)
        lines = wrap(draw, text, selected, width)
        spacing = max(2, size // 6)
        boxes = [draw.textbbox((0, 0), line, font=selected) for line in lines]
        total = sum(box[3] - box[1] for box in boxes) + spacing * max(0, len(lines) - 1)
        if len(lines) <= 4 and total <= height:
            return selected, lines, spacing
    raise ValueError(f"copy does not fit canonical safe zone: {text!r}")


def letter_panel(image: Image.Image, plan: dict[str, Any], beat: dict[str, Any]) -> tuple[Image.Image, dict[str, Any]]:
    canvas = image.convert("RGBA")
    zones = plan["comic_direction"]["lettering"]["safe_zones"]
    if len(zones) != 1:
        raise ValueError(f"exactly one canonical safe zone required: {plan['panel_id']}")
    left, top, right, bottom = zones[0]["rect_norm"]
    box = [round(left * canvas.width), round(top * canvas.height), round(right * canvas.width), round(bottom * canvas.height)]
    inset = max(3, canvas.width // 220)
    box = [box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset]
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    kind = beat["copy_type"]
    text = beat["copy"]
    padding_x = max(8, canvas.width // 90)
    padding_y = max(5, canvas.height // 150)
    selected, lines, spacing = fit_copy(draw, text, box[2] - box[0] - 2 * padding_x, box[3] - box[1] - 2 * padding_y)
    if kind == "sfx":
        fill, outline, text_fill, radius = (25, 30, 35, 205), (246, 241, 228, 235), (250, 246, 235, 255), 6
    elif kind == "system":
        fill, outline, text_fill, radius = (24, 42, 38, 218), (90, 205, 164, 245), (223, 255, 240, 255), 7
    elif kind == "caption":
        fill, outline, text_fill, radius = (242, 236, 220, 220), (45, 42, 37, 235), (28, 28, 27, 255), 7
    else:
        fill, outline, text_fill, radius = (249, 246, 237, 220), (35, 38, 42, 240), (25, 28, 32, 255), 18
    draw.rounded_rectangle(tuple(box), radius=radius, fill=fill, outline=outline, width=max(2, canvas.width // 300))
    line_boxes = [draw.textbbox((0, 0), line, font=selected) for line in lines]
    total_height = sum(value[3] - value[1] for value in line_boxes) + spacing * max(0, len(lines) - 1)
    cursor_y = box[1] + (box[3] - box[1] - total_height) // 2
    for line, bounds in zip(lines, line_boxes, strict=True):
        line_width = bounds[2] - bounds[0]
        cursor_x = box[0] + (box[2] - box[0] - line_width) // 2
        draw.text((cursor_x, cursor_y), line, font=selected, fill=text_fill)
        cursor_y += bounds[3] - bounds[1] + spacing
    rendered = Image.alpha_composite(canvas, layer).convert("RGB")
    return rendered, {
        "panel_id": plan["panel_id"],
        "plan_revision_id": plan["plan_revision_id"],
        "copy_type": kind,
        "speaker": beat["speaker"],
        "copy": beat["copy"],
        "canonical_safe_zone_anchor": zones[0]["anchor"],
        "canonical_safe_zone_rect_norm": zones[0]["rect_norm"],
        "rendered_box_px": box,
        "font_source_px": getattr(selected, "size", None),
        "line_count": len(lines),
        "protected_subjects": plan["comic_direction"]["lettering"]["protected_subjects"],
    }


def main() -> int:
    copy_document = json.loads(COPY.read_text(encoding="utf-8"))
    copy_chapters = {row["chapter"].lower(): row["beats"] for row in copy_document["chapters"]}
    if set(copy_chapters) != set(CHAPTERS):
        raise ValueError("copy manifest must cover CH06-CH13")
    for chapter in CHAPTERS:
        plans_path = ROOT / f"production/comic/{chapter}-sc01-panel-plans-r1.json"
        packet_path = ROOT / f"production/comic/run-manifests/{chapter}-default-house-route-review-packet-r1.json"
        plans = {row["panel_id"]: row for row in json.loads(plans_path.read_text(encoding="utf-8"))["plans"]}
        candidates = {row["panel_id"]: row for row in json.loads(packet_path.read_text(encoding="utf-8"))["candidates"]}
        for beat in copy_chapters[chapter]:
            candidate = candidates[beat["panel_id"]]
            dummy = Image.new("RGB", (candidate["width"], candidate["height"]), "#777777")
            letter_panel(dummy, plans[beat["panel_id"]], beat)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    chapter_records = []
    sampler_rows = []
    total_entries = 0
    for chapter in CHAPTERS:
        plans_path = ROOT / f"production/comic/{chapter}-sc01-panel-plans-r1.json"
        packet_path = ROOT / f"production/comic/run-manifests/{chapter}-default-house-route-review-packet-r1.json"
        plans = sorted(json.loads(plans_path.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        candidates = {row["panel_id"]: row for row in packet["candidates"]}
        beats = copy_chapters[chapter]
        if len(beats) != 10 or len({row["panel_id"] for row in beats}) != 10:
            raise ValueError(f"{chapter} requires ten unique lettering beats")
        beat_map = {row["panel_id"]: row for row in beats}
        rendered_entries = []
        reading_panels = []
        phone_panels = []
        sampler_cells = []
        lettered_phone_cells = []
        for plan in plans:
            with Image.open(ROOT / candidates[plan["panel_id"]]["path"]) as opened:
                panel = opened.convert("RGB")
            if plan["panel_id"] in beat_map:
                panel, entry = letter_panel(panel, plan, beat_map[plan["panel_id"]])
                rendered_entries.append(entry)
                sampler_cells.append(labeled_canvas(panel, f"{chapter.upper()} P{plan['display_order']:03d}", 118, 24))
                lettered_phone_cells.append(fit_width(panel, 374))
            reading_panels.append(fit_width(panel, target_width(plan)))
            phone_panels.append(fit_width(panel, 374))
        chapter_dir = OUT_DIR / chapter
        chapter_dir.mkdir(parents=True, exist_ok=True)
        reading = chapter_dir / f"{chapter}-lettered-reading-draft-r1.png"
        phone = chapter_dir / f"{chapter}-lettered-phone-preview-r1.png"
        beats_phone = chapter_dir / f"{chapter}-lettered-beats-phone-review-r1.png"
        stack(reading_panels, 800, 20, "#ece8df").save(reading, format="PNG", compress_level=9)
        stack(phone_panels, 390, 10, "#ece8df").save(phone, format="PNG", compress_level=9)
        stack(lettered_phone_cells, 390, 10, "#ece8df").save(beats_phone, format="PNG", compress_level=9)
        row_height = max(cell.height for cell in sampler_cells)
        sampler = Image.new("RGB", (1200, row_height), "#11151b")
        for index, cell in enumerate(sampler_cells):
            sampler.paste(cell, (8 + index * 119, 0))
        sampler_rows.append(sampler)
        artifacts = []
        for kind, path in (
            ("lettered_reading_draft", reading),
            ("lettered_phone_preview", phone),
            ("lettered_beats_phone_review", beats_phone),
        ):
            with Image.open(path) as opened:
                dimensions = [opened.width, opened.height]
            artifacts.append({"type": kind, "path": rel(path), "sha256": sha256(path), "dimensions": dimensions})
        chapter_records.append(
            {
                "chapter": chapter.upper(),
                "plans": {"path": rel(plans_path), "sha256": sha256(plans_path)},
                "source_packet": {"path": rel(packet_path), "sha256": sha256(packet_path)},
                "source_triage": packet["summary"]["triage"],
                "summary": {"panels": 40, "lettered_panels": 10, "unlettered_panels": 30},
                "entries": rendered_entries,
                "artifacts": artifacts,
            }
        )
        total_entries += len(rendered_entries)
    sampler_path = OUT_DIR / "ch06-ch13-lettered-panel-sampler-r1.png"
    stack(sampler_rows, 1200, 12, "#11151b").save(sampler_path, format="PNG", compress_level=9)
    with Image.open(sampler_path) as opened:
        sampler_dimensions = [opened.width, opened.height]
    manifest = {
        "record_type": "ComicMultiChapterLocalLetteringReview",
        "schema_version": "1.0",
        "record_id": "ng-ch06-ch13-local-lettering-review-r1",
        "state": "REVIEW_ARTIFACT_UNACCEPTED",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "copy_manifest": {"path": rel(COPY), "sha256": sha256(COPY)},
        "treatment": {"placement": "canonical_safe_zone", "translucent_backing": True, "speaker_labels": False},
        "summary": {
            "chapters": 8,
            "panels": 320,
            "lettered_panels": total_entries,
            "artifacts": 25,
            "source_triage": {"PASS": 296, "WARN": 5, "FAIL": 19},
            "accepted": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
        "chapters": chapter_records,
        "aggregate_artifact": {"type": "eight_chapter_lettered_sampler", "path": rel(sampler_path), "sha256": sha256(sampler_path), "dimensions": sampler_dimensions},
        "limitations": [
            "Sparse review copy is provisional and does not establish final canon dialogue.",
            "Canonical safe-zone placement avoids declared protected subjects but has not been segmentation-tested against every pixel.",
            "Speaker attribution is preserved in metadata; final balloon-tail geometry remains a later typography task.",
            "All derivative pixels remain ignored, unaccepted, commercially uncleared, and not an exact production base.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"artifacts": 25, "chapters": 8, "lettered_panels": total_entries, "panels": 320}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
