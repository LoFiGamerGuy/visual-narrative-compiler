"""Build a sparse, translucent, lettering-safe CH05 review edition."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUILD_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r1/review/build-report.json"
DEFAULT_PROPOSAL = ROOT / "production/comic/lettering/ch05-complete-chapter-lettering-proposal-r1.json"
DEFAULT_OUTPUT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r1/lettered"
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"


class LetteringError(ValueError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, *, italic: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ["DejaVuSansCondensed-Oblique.ttf", "DejaVuSansCondensed.ttf"] if italic else ["DejaVuSansCondensed-Bold.ttf", "DejaVuSans-Bold.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def wrap(draw: ImageDraw.ImageDraw, text: str, selected_font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
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


def fit_text(draw: ImageDraw.ImageDraw, text: str, width: int, height: int, kind: str) -> tuple[ImageFont.ImageFont, list[str], int]:
    preferred = 48 if kind == "sfx" else 42
    for size in range(preferred, 23, -1):
        selected = font(size, italic=kind == "caption")
        lines = wrap(draw, text, selected, width)
        spacing = max(3, size // 6)
        boxes = [draw.textbbox((0, 0), line, font=selected) for line in lines]
        total_height = sum(box[3] - box[1] for box in boxes) + spacing * max(0, len(lines) - 1)
        if len(lines) <= 3 and total_height <= height:
            return selected, lines, spacing
    raise LetteringError(f"copy does not fit safe zone at phone-readable source size: {text!r}")


def validate_inputs(report: dict[str, Any], proposal: dict[str, Any]) -> tuple[Path, dict[str, dict[str, Any]]]:
    if report.get("record_type") != "ComicChapterReviewBuildReport" or report.get("chapter_complete") is not True:
        raise LetteringError("build report is not a complete comic chapter")
    if report.get("animation_shot_plan") is not None or report.get("e_conte") is not None:
        raise LetteringError("build report crosses the comic-only planning boundary")
    if proposal.get("record_type") != "ComicPanelPlanLetteringProposal" or proposal.get("planning_structure") != "ComicPanelPlan":
        raise LetteringError("lettering proposal must remain ComicPanelPlan-bound")
    if proposal.get("animation_shot_plan") is not None or proposal.get("e_conte") is not None:
        raise LetteringError("lettering proposal crosses the comic-only planning boundary")
    plan_ref = proposal.get("comic_panel_plan_source", {})
    if plan_ref.get("path") != PLAN.relative_to(ROOT).as_posix() or plan_ref.get("sha256") != sha256(PLAN):
        raise LetteringError("lettering proposal plan source mismatch")
    long_scroll = report["artifacts"]["long_scroll"]
    scroll_path = ROOT / long_scroll["path"]
    if sha256(scroll_path) != long_scroll["sha256"]:
        raise LetteringError("clean long-scroll hash mismatch")
    placements = {row["panel_id"]: row for row in report["placements"]}
    plans = {row["panel_id"]: row for row in json.loads(PLAN.read_text(encoding="utf-8"))["plans"]}
    seen: set[str] = set()
    for entry in proposal.get("entries", []):
        panel_id = entry.get("panel_id")
        if panel_id in seen or panel_id not in placements or panel_id not in plans:
            raise LetteringError(f"unknown or duplicate lettering panel: {panel_id}")
        seen.add(panel_id)
        if entry.get("plan_revision_id") != plans[panel_id]["plan_revision_id"]:
            raise LetteringError(f"plan revision mismatch: {panel_id}")
        if entry.get("kind") not in {"dialogue", "caption", "sfx"} or not isinstance(entry.get("text"), str) or not entry["text"]:
            raise LetteringError(f"invalid lettering entry: {panel_id}")
        if entry.get("placement_mode", "safe_zone") not in {"safe_zone", "gutter_after"}:
            raise LetteringError(f"invalid lettering placement mode: {panel_id}")
        if len(placements[panel_id].get("lettering_safe_zones", [])) != 1:
            raise LetteringError(f"exactly one canonical safe zone required: {panel_id}")
    return scroll_path, placements


def save(image: Image.Image, path: Path) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", compress_level=6, optimize=False)
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "width": image.width, "height": image.height, "bytes": path.stat().st_size}


def build(build_report_path: Path, proposal_path: Path, output_dir: Path, *, record_id: str = "ng-ch05-complete-chapter-lettering-build-r1", artifact_stem: str = "ch05-complete-chapter-lettered-r1") -> dict[str, Any]:
    report = json.loads(build_report_path.read_text(encoding="utf-8"))
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    scroll_path, placements = validate_inputs(report, proposal)
    with Image.open(scroll_path) as source:
        canvas = source.convert("RGBA")
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    rendered = []
    opacity = round(float(proposal["treatment"]["opacity"]) * 255)
    placement_order = sorted(placements.values(), key=lambda row: row["order"])
    next_top = {
        row["panel_id"]: (placement_order[index + 1]["assembly_rect_px"][1] if index + 1 < len(placement_order) else canvas.height)
        for index, row in enumerate(placement_order)
    }
    for entry in proposal["entries"]:
        panel_id = entry["panel_id"]
        zone = placements[panel_id]["lettering_safe_zones"][0]["assembly_rect_px"]
        placement_mode = entry.get("placement_mode", "safe_zone")
        if placement_mode == "gutter_after":
            assembly = placements[panel_id]["assembly_rect_px"]
            panel_bottom = assembly[1] + assembly[3]
            gutter_top, gutter_bottom = panel_bottom + 6, next_top[panel_id] - 6
            if gutter_bottom - gutter_top < 36:
                raise LetteringError(f"gutter is too short for outside-art lettering: {panel_id}")
            anchor = placements[panel_id]["lettering_safe_zones"][0].get("anchor", "top_left")
            box_width = 420
            left = canvas.width - 80 - box_width if "right" in anchor else 80
            box = (left, gutter_top, left + box_width, gutter_bottom)
        else:
            left, top, right, bottom = zone
            inset = 5
            box = (left + inset, top + inset, right - inset, bottom - inset)
        box_width = box[2] - box[0]
        box_height = box[3] - box[1]
        padding_x, padding_y = 12, 4
        selected_font, lines, spacing = fit_text(draw, entry["text"], box_width - 2 * padding_x, box_height - 2 * padding_y, entry["kind"])
        fill = (247, 244, 235, opacity) if entry["kind"] != "sfx" else (30, 35, 42, 210)
        outline = (32, 37, 43, 235) if entry["kind"] != "sfx" else (247, 244, 235, 220)
        text_fill = (24, 28, 33, 255) if entry["kind"] != "sfx" else (247, 244, 235, 255)
        radius = 18 if entry["kind"] == "dialogue" else 7
        draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)
        line_boxes = [draw.textbbox((0, 0), line, font=selected_font) for line in lines]
        text_height = sum(value[3] - value[1] for value in line_boxes) + spacing * max(0, len(lines) - 1)
        y = box[1] + (box_height - text_height) // 2
        for line, bounds in zip(lines, line_boxes):
            line_width = bounds[2] - bounds[0]
            x = box[0] + (box_width - line_width) // 2
            draw.text((x, y), line, font=selected_font, fill=text_fill, stroke_width=0)
            y += bounds[3] - bounds[1] + spacing
        rendered.append({
            "panel_id": panel_id,
            "plan_revision_id": entry["plan_revision_id"],
            "kind": entry["kind"],
            "speaker": entry.get("speaker"),
            "text": entry["text"],
            "placement_mode": placement_mode,
            "canonical_safe_zone_rect_px": zone,
            "rendered_backing_rect_px": list(box),
            "opacity": proposal["treatment"]["opacity"],
            "font_source_px": getattr(selected_font, "size", None),
            "line_count": len(lines),
        })
    lettered = Image.alpha_composite(canvas, layer).convert("RGB")
    if not record_id.strip() or not artifact_stem.strip() or Path(artifact_stem).name != artifact_stem:
        raise LetteringError("record-id and artifact-stem must be safe non-empty leaf values")
    main_artifact = save(lettered, output_dir / f"{artifact_stem}.png")
    phone_width = report["canvas"]["phone_width"]
    phone_height = round(lettered.height * phone_width / lettered.width)
    phone = lettered.resize((phone_width, phone_height), Image.Resampling.LANCZOS)
    phone_name = "ch05-complete-chapter-lettered-phone-390px-r1.png" if artifact_stem == "ch05-complete-chapter-lettered-r1" else f"{artifact_stem}-phone-390px.png"
    phone_artifact = save(phone, output_dir / phone_name)
    result = {
        "record_type": "ComicChapterLetteringBuildReport",
        "schema_version": "1.0",
        "record_id": record_id,
        "state": "REVIEW_ARTIFACT_UNACCEPTED",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": {
            "chapter_build_report": {"path": build_report_path.relative_to(ROOT).as_posix(), "sha256": sha256(build_report_path)},
            "lettering_proposal": {"path": proposal_path.relative_to(ROOT).as_posix(), "sha256": sha256(proposal_path)},
            "clean_long_scroll": {"path": scroll_path.relative_to(ROOT).as_posix(), "sha256": sha256(scroll_path)},
        },
        "summary": {"chapter_panels": len(report["placements"]), "lettered_panels": len(rendered), "opacity": proposal["treatment"]["opacity"], "phone_width_px": phone_width},
        "entries": rendered,
        "artifacts": {"lettered_long_scroll": main_artifact, "lettered_phone_scroll": phone_artifact},
        "boundary": "Review-only copy and pixels; no canon dialogue, acceptance, commercial clearance, or exact production-base selection.",
    }
    report_path = output_dir / "lettering-build-report.json"
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"lettered_panels": len(rendered), "long_scroll": main_artifact, "phone_scroll": phone_artifact}, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-report", default=str(DEFAULT_BUILD_REPORT))
    parser.add_argument("--proposal", default=str(DEFAULT_PROPOSAL))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--record-id", default="ng-ch05-complete-chapter-lettering-build-r1")
    parser.add_argument("--artifact-stem", default="ch05-complete-chapter-lettered-r1")
    args = parser.parse_args()
    build(Path(args.build_report).resolve(), Path(args.proposal).resolve(), Path(args.output_dir).resolve(), record_id=args.record_id, artifact_stem=args.artifact_stem)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
