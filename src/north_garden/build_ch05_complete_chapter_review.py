"""Deterministically assemble a complete CH05 comic review from an explicit manifest.

The builder is deliberately provider-agnostic.  It reads already-rendered, hash-pinned
candidate pixels, verifies that every ordered entry resolves to a ComicPanelPlan, and
writes review derivatives only beneath ``experiments/review-packets``.  Source images
are opened read-only and are never modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_OUTPUT_ROOT = Path("experiments/review-packets")
DEFAULT_PHONE_WIDTH = 390
DEFAULT_PHONE_VIEWPORT_HEIGHT = 844


class ManifestError(ValueError):
    """Raised when a production manifest violates the chapter assembly contract."""


@dataclass(frozen=True)
class PreparedPanel:
    order: int
    panel_id: str
    candidate_id: str
    sequence_id: str | None
    source_path: Path
    source_rel: str
    source_sha256: str
    source_width: int
    source_height: int
    target_width: int
    target_height: int
    alignment: str
    gutter_after: int
    safe_zones: tuple[dict[str, Any], ...]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ManifestError(f"top-level JSON must be an object: {path}")
    return value


def project_path(root: Path, raw: Any, label: str, *, must_exist: bool = True) -> tuple[Path, str]:
    if not isinstance(raw, str) or not raw.strip():
        raise ManifestError(f"{label} must be a non-empty project-relative path")
    rel = Path(raw.replace("\\", "/"))
    if rel.is_absolute() or ".." in rel.parts:
        raise ManifestError(f"{label} must not be absolute or traverse parents: {raw}")
    resolved = (root / rel).resolve()
    try:
        normalized = resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ManifestError(f"{label} escapes the project root: {raw}") from exc
    if must_exist and not resolved.is_file():
        raise ManifestError(f"{label} does not exist: {normalized}")
    return resolved, normalized


def output_path(root: Path, raw: str) -> Path:
    resolved, normalized = project_path(root, raw, "output directory", must_exist=False)
    allowed = (root / ALLOWED_OUTPUT_ROOT).resolve()
    try:
        resolved.relative_to(allowed)
    except ValueError as exc:
        raise ManifestError(
            f"output directory must remain under {ALLOWED_OUTPUT_ROOT.as_posix()}: {normalized}"
        ) from exc
    if resolved == allowed:
        raise ManifestError("output directory must be a named child of experiments/review-packets")
    return resolved


def require_null_planning_boundaries(record: dict[str, Any], label: str) -> None:
    prohibited = {
        "animation_shot_plan": "AnimationShotPlan",
        "animationShotPlan": "AnimationShotPlan",
        "e_conte": "E-Conte",
        "eConte": "E-Conte",
    }
    for key, display in prohibited.items():
        if key in record and record[key] is not None:
            raise ManifestError(f"{label}.{key} must be absent or null; {display} is not allowed")


def positive_int(value: Any, label: str, *, allow_zero: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ManifestError(f"{label} must be an integer")
    minimum = 0 if allow_zero else 1
    if value < minimum:
        raise ManifestError(f"{label} must be >= {minimum}")
    return value


def color(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) not in (4, 7) or not value.startswith("#"):
        raise ManifestError(f"{label} must be a #RGB or #RRGGBB color")
    try:
        int(value[1:], 16)
    except ValueError as exc:
        raise ManifestError(f"{label} is not a hexadecimal color") from exc
    return value


def normalized_rect(value: Any, label: str) -> tuple[float, float, float, float]:
    if not isinstance(value, list) or len(value) != 4 or any(
        isinstance(item, bool) or not isinstance(item, (int, float)) for item in value
    ):
        raise ManifestError(f"{label} must contain four numbers")
    x, y, width, height = (float(item) for item in value)
    if x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > 1 or y + height > 1:
        raise ManifestError(f"{label} must be a positive normalized rectangle inside [0,1]")
    return x, y, width, height


def source_fields(entry: dict[str, Any], index: int) -> tuple[str, str, int, int]:
    source = entry.get("source")
    if not isinstance(source, dict):
        raise ManifestError(f"entries[{index}].source must be an object")
    digest = source.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ManifestError(f"entries[{index}].source.sha256 must be a 64-character digest")
    try:
        int(digest, 16)
    except ValueError as exc:
        raise ManifestError(f"entries[{index}].source.sha256 is not hexadecimal") from exc
    return (
        source.get("path"),
        digest.lower(),
        positive_int(source.get("width"), f"entries[{index}].source.width"),
        positive_int(source.get("height"), f"entries[{index}].source.height"),
    )


def validate_and_prepare(
    root: Path, manifest_path: Path, *, load_pixels: bool = True
) -> tuple[dict[str, Any], dict[str, Any], list[PreparedPanel], dict[str, Any]]:
    manifest = load_json(manifest_path)
    require_null_planning_boundaries(manifest, "manifest")
    if manifest.get("medium") != "comic":
        raise ManifestError("manifest.medium must be 'comic'")
    if manifest.get("record_type") != "ComicChapterProductionManifest":
        raise ManifestError("manifest.record_type must be ComicChapterProductionManifest")
    if not isinstance(manifest.get("record_id"), str) or not manifest["record_id"].strip():
        raise ManifestError("manifest.record_id must be a non-empty string")

    plan_ref = manifest.get("comic_panel_plan_collection")
    if not isinstance(plan_ref, dict):
        raise ManifestError("comic_panel_plan_collection must be a path/hash object")
    plan_path, plan_rel = project_path(root, plan_ref.get("path"), "comic_panel_plan_collection.path")
    expected_plan_hash = plan_ref.get("sha256")
    if not isinstance(expected_plan_hash, str) or len(expected_plan_hash) != 64:
        raise ManifestError("comic_panel_plan_collection.sha256 must be a 64-character digest")
    actual_plan_hash = sha256(plan_path)
    if actual_plan_hash != expected_plan_hash.lower():
        raise ManifestError(
            f"ComicPanelPlan collection hash mismatch: expected {expected_plan_hash}, got {actual_plan_hash}"
        )
    collection = load_json(plan_path)
    require_null_planning_boundaries(collection, "comic_panel_plan_collection")
    if collection.get("medium") != "comic" or not isinstance(collection.get("plans"), list):
        raise ManifestError("ComicPanelPlan collection must have medium 'comic' and a plans array")
    plans: dict[str, dict[str, Any]] = {}
    display_orders: dict[str, int] = {}
    for index, plan in enumerate(collection["plans"]):
        if not isinstance(plan, dict) or not isinstance(plan.get("panel_id"), str):
            raise ManifestError(f"plans[{index}] is not a valid ComicPanelPlan")
        require_null_planning_boundaries(plan, f"plans[{index}]")
        panel_id = plan["panel_id"]
        if panel_id in plans:
            raise ManifestError(f"duplicate panel_id in collection: {panel_id}")
        plans[panel_id] = plan
        display_orders[panel_id] = positive_int(plan.get("display_order"), f"{panel_id}.display_order")

    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ManifestError("manifest.entries must be a non-empty array")
    chapter_complete = manifest.get("chapter_complete")
    if chapter_complete is not True:
        raise ManifestError("manifest.chapter_complete must be true for complete-chapter assembly")
    if len(entries) != len(plans):
        raise ManifestError(
            f"complete chapter requires one entry per ComicPanelPlan: {len(entries)} entries != {len(plans)} plans"
        )

    canvas = manifest.get("canvas", {})
    if not isinstance(canvas, dict):
        raise ManifestError("manifest.canvas must be an object")
    canvas_spec = {
        "width": positive_int(canvas.get("width", 1200), "canvas.width"),
        "side_margin": positive_int(canvas.get("side_margin", 80), "canvas.side_margin", allow_zero=True),
        "background": color(canvas.get("background", "#12151a"), "canvas.background"),
        "top_gutter": positive_int(canvas.get("top_gutter", 80), "canvas.top_gutter", allow_zero=True),
        "phone_width": positive_int(canvas.get("phone_width", DEFAULT_PHONE_WIDTH), "canvas.phone_width"),
        "phone_viewport_height": positive_int(
            canvas.get("phone_viewport_height", DEFAULT_PHONE_VIEWPORT_HEIGHT),
            "canvas.phone_viewport_height",
        ),
    }
    if canvas_spec["side_margin"] * 2 >= canvas_spec["width"]:
        raise ManifestError("canvas.side_margin leaves no usable panel width")

    seen_panels: set[str] = set()
    seen_candidates: set[str] = set()
    prepared: list[PreparedPanel] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ManifestError(f"entries[{index}] must be an object")
        require_null_planning_boundaries(entry, f"entries[{index}]")
        order = positive_int(entry.get("order"), f"entries[{index}].order")
        if order != index + 1:
            raise ManifestError(f"entries must be consecutively ordered; index {index} has order {order}")
        panel_id = entry.get("panel_id")
        candidate_id = entry.get("candidate_id")
        if not isinstance(panel_id, str) or panel_id not in plans:
            raise ManifestError(f"entries[{index}].panel_id is not in the pinned ComicPanelPlan collection")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            raise ManifestError(f"entries[{index}].candidate_id must be a non-empty string")
        if panel_id in seen_panels:
            raise ManifestError(f"duplicate chapter panel entry: {panel_id}")
        if candidate_id in seen_candidates:
            raise ManifestError(f"duplicate candidate_id: {candidate_id}")
        if display_orders[panel_id] != order:
            raise ManifestError(
                f"entry order {order} does not match {panel_id} display_order {display_orders[panel_id]}"
            )
        seen_panels.add(panel_id)
        seen_candidates.add(candidate_id)

        source_raw, expected_hash, expected_width, expected_height = source_fields(entry, index)
        source_path, source_rel = project_path(root, source_raw, f"entries[{index}].source.path")
        if not source_rel.startswith("experiments/"):
            raise ManifestError(
                f"{candidate_id} source must remain under the ignored local experiments/ tree: {source_rel}"
            )
        if load_pixels:
            actual_hash = sha256(source_path)
            if actual_hash != expected_hash:
                raise ManifestError(
                    f"source hash mismatch for {candidate_id}: expected {expected_hash}, got {actual_hash}"
                )
            try:
                with Image.open(source_path) as image:
                    actual_size = image.size
                    image.verify()
            except Exception as exc:
                raise ManifestError(f"cannot decode source image for {candidate_id}: {exc}") from exc
            if actual_size != (expected_width, expected_height):
                raise ManifestError(
                    f"source dimensions mismatch for {candidate_id}: expected "
                    f"{expected_width}x{expected_height}, got {actual_size[0]}x{actual_size[1]}"
                )

        layout = entry.get("layout", {})
        if not isinstance(layout, dict):
            raise ManifestError(f"entries[{index}].layout must be an object")
        max_width = canvas_spec["width"] - canvas_spec["side_margin"] * 2
        target_width = positive_int(layout.get("target_width", max_width), f"entries[{index}].layout.target_width")
        if target_width > max_width:
            raise ManifestError(f"{candidate_id} target_width exceeds the usable canvas width")
        alignment = layout.get("alignment", "center")
        if alignment not in {"left", "center", "right"}:
            raise ManifestError(f"{candidate_id} alignment must be left, center, or right")
        gutter_after = positive_int(
            layout.get("gutter_after", 80), f"entries[{index}].layout.gutter_after", allow_zero=True
        )
        target_height = max(1, round(expected_height * target_width / expected_width))

        lettering = plans[panel_id].get("comic_direction", {}).get("lettering", {})
        safe_zones_raw = lettering.get("safe_zones")
        if not isinstance(safe_zones_raw, list) or not safe_zones_raw:
            raise ManifestError(f"{panel_id} has no ComicPanelPlan lettering safe zone")
        safe_zones: list[dict[str, Any]] = []
        for zone_index, zone in enumerate(safe_zones_raw):
            if not isinstance(zone, dict):
                raise ManifestError(f"{panel_id} safe_zones[{zone_index}] must be an object")
            rect = normalized_rect(zone.get("rect_norm"), f"{panel_id} safe_zones[{zone_index}].rect_norm")
            safe_zones.append({"anchor": zone.get("anchor"), "rect_norm": list(rect)})

        sequence_id = entry.get("sequence_id")
        if sequence_id is not None and not isinstance(sequence_id, str):
            raise ManifestError(f"entries[{index}].sequence_id must be a string or null")
        prepared.append(
            PreparedPanel(
                order=order,
                panel_id=panel_id,
                candidate_id=candidate_id,
                sequence_id=sequence_id,
                source_path=source_path,
                source_rel=source_rel,
                source_sha256=expected_hash,
                source_width=expected_width,
                source_height=expected_height,
                target_width=target_width,
                target_height=target_height,
                alignment=alignment,
                gutter_after=gutter_after,
                safe_zones=tuple(safe_zones),
            )
        )

    missing = sorted(set(plans) - seen_panels)
    if missing:
        raise ManifestError(f"chapter manifest is missing ComicPanelPlans: {', '.join(missing)}")
    return manifest, collection, prepared, {"plan_path": plan_path, "plan_rel": plan_rel, "plan_hash": actual_plan_hash, "canvas": canvas_spec}


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def save_png(path: Path, image: Image.Image, root: Path) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=False, compress_level=6)
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": sha256(path),
        "width": image.width,
        "height": image.height,
    }


def panel_x(panel: PreparedPanel, canvas: dict[str, Any]) -> int:
    if panel.alignment == "left":
        return canvas["side_margin"]
    if panel.alignment == "right":
        return canvas["width"] - canvas["side_margin"] - panel.target_width
    return (canvas["width"] - panel.target_width) // 2


def safe_zone_rect(x: int, y: int, width: int, height: int, rect: list[float]) -> tuple[int, int, int, int]:
    rx, ry, rw, rh = rect
    return (
        x + round(rx * width),
        y + round(ry * height),
        x + round((rx + rw) * width),
        y + round((ry + rh) * height),
    )


def overlay_zones(image: Image.Image, zones: tuple[dict[str, Any], ...]) -> Image.Image:
    result = image.convert("RGBA")
    layer = Image.new("RGBA", result.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    line = max(3, min(image.size) // 220)
    for index, zone in enumerate(zones, start=1):
        rect = safe_zone_rect(0, 0, image.width, image.height, zone["rect_norm"])
        draw.rectangle(rect, fill=(18, 196, 235, 66), outline=(0, 150, 190, 255), width=line)
        draw.text((rect[0] + line * 2, rect[1] + line * 2), f"SAFE {index}", fill=(0, 64, 86, 255), font=font(max(14, min(image.size) // 55)))
    return Image.alpha_composite(result, layer).convert("RGB")


def build_contact_sheet(panels: list[PreparedPanel], *, overlay: bool) -> Image.Image:
    columns, cell_w, cell_h, gap, margin, header = 5, 300, 390, 16, 24, 90
    rows = (len(panels) + columns - 1) // columns
    canvas = Image.new("RGB", (margin * 2 + columns * cell_w + (columns - 1) * gap, header + margin + rows * cell_h + (rows - 1) * gap), "#e9e6df")
    draw = ImageDraw.Draw(canvas)
    title = "CH05 COMPLETE CHAPTER - LETTERING AUDIT" if overlay else "CH05 COMPLETE CHAPTER - STORY ORDER"
    draw.text((margin, 18), title, fill="#16191d", font=font(27))
    draw.text((margin, 55), f"{len(panels)} ordered ComicPanelPlans; generated candidates remain unaccepted", fill="#4c535b", font=font(16))
    for index, panel in enumerate(panels):
        col, row = index % columns, index // columns
        x = margin + col * (cell_w + gap)
        y = header + row * (cell_h + gap)
        draw.rectangle((x, y, x + cell_w, y + cell_h), fill="#faf8f2", outline="#697079", width=2)
        with Image.open(panel.source_path) as opened:
            source = opened.convert("RGB")
        if overlay:
            source = overlay_zones(source, panel.safe_zones)
        framed = ImageOps.contain(source, (cell_w - 16, cell_h - 64), Image.Resampling.LANCZOS)
        canvas.paste(framed, (x + (cell_w - framed.width) // 2, y + 44 + (cell_h - 54 - framed.height) // 2))
        label = f"{panel.order:02d} {panel.panel_id.split('-')[-1].upper()}  {panel.candidate_id}"
        draw.text((x + 9, y + 10), label, fill="#16191d", font=font(15))
    return canvas


def build(root: Path, manifest_path: Path, output_dir: Path) -> dict[str, Any]:
    manifest, _collection, panels, context = validate_and_prepare(root, manifest_path)
    canvas = context["canvas"]
    total_height = canvas["top_gutter"] + sum(panel.target_height + panel.gutter_after for panel in panels)
    clean = Image.new("RGB", (canvas["width"], total_height), canvas["background"])
    overlay = clean.copy()
    overlay_draw = ImageDraw.Draw(overlay, "RGBA")
    placements: list[dict[str, Any]] = []
    individual_overlays: list[dict[str, Any]] = []
    y = canvas["top_gutter"]
    for panel in panels:
        with Image.open(panel.source_path) as opened:
            source = opened.convert("RGB")
        resized = source.resize((panel.target_width, panel.target_height), Image.Resampling.LANCZOS)
        x = panel_x(panel, canvas)
        clean.paste(resized, (x, y))
        overlay.paste(resized, (x, y))
        assembly_zones = []
        for zone_index, zone in enumerate(panel.safe_zones, start=1):
            rect = safe_zone_rect(x, y, panel.target_width, panel.target_height, zone["rect_norm"])
            overlay_draw.rectangle(rect, fill=(18, 196, 235, 66), outline=(0, 150, 190, 255), width=4)
            overlay_draw.text((rect[0] + 8, rect[1] + 8), f"SAFE {zone_index}", fill=(0, 64, 86, 255), font=font(16))
            assembly_zones.append({**zone, "assembly_rect_px": list(rect)})
        overlay_name = f"{panel.order:03d}-{panel.panel_id.split('-')[-1]}-{panel.candidate_id}-lettering-overlay.png"
        overlay_artifact = save_png(output_dir / "lettering-overlays" / overlay_name, overlay_zones(source, panel.safe_zones), root)
        individual_overlays.append({"panel_id": panel.panel_id, "candidate_id": panel.candidate_id, **overlay_artifact})
        placements.append(
            {
                "order": panel.order,
                "panel_id": panel.panel_id,
                "candidate_id": panel.candidate_id,
                "sequence_id": panel.sequence_id,
                "source": {
                    "path": panel.source_rel,
                    "sha256": panel.source_sha256,
                    "width": panel.source_width,
                    "height": panel.source_height,
                },
                "assembly_rect_px": [x, y, panel.target_width, panel.target_height],
                "lettering_safe_zones": assembly_zones,
            }
        )
        y += panel.target_height + panel.gutter_after

    artifacts: dict[str, Any] = {}
    artifacts["long_scroll"] = save_png(output_dir / "ch05-complete-chapter-long-scroll.png", clean, root)
    artifacts["long_scroll_lettering_overlay"] = save_png(
        output_dir / "ch05-complete-chapter-long-scroll-lettering-overlay.png", overlay, root
    )
    artifacts["contact_sheet"] = save_png(
        output_dir / "ch05-complete-chapter-contact-sheet.png", build_contact_sheet(panels, overlay=False), root
    )
    artifacts["contact_sheet_lettering_overlay"] = save_png(
        output_dir / "ch05-complete-chapter-contact-sheet-lettering-overlay.png",
        build_contact_sheet(panels, overlay=True),
        root,
    )
    phone_height = max(1, round(clean.height * canvas["phone_width"] / clean.width))
    phone = clean.resize((canvas["phone_width"], phone_height), Image.Resampling.LANCZOS)
    artifacts["phone_long_scroll"] = save_png(output_dir / "ch05-complete-chapter-phone-390px.png", phone, root)
    viewport_records = []
    step = canvas["phone_viewport_height"]
    for index, top in enumerate(range(0, phone.height, step), start=1):
        viewport = Image.new("RGB", (canvas["phone_width"], step), canvas["background"])
        crop = phone.crop((0, top, phone.width, min(phone.height, top + step)))
        viewport.paste(crop, (0, 0))
        viewport_records.append({"index": index, "source_top_px": top, **save_png(output_dir / "phone-viewports" / f"viewport-{index:03d}.png", viewport, root)})
    artifacts["phone_viewports"] = viewport_records
    artifacts["individual_lettering_overlays"] = individual_overlays

    report = {
        "record_type": "ComicChapterReviewBuildReport",
        "schema_version": "1.0",
        "record_id": f"{manifest['record_id']}-review-build-report",
        "state": "READY_FOR_CHAPTER_REVIEW_UNACCEPTED",
        "medium": "comic",
        "chapter_complete": True,
        "animation_shot_plan": None,
        "e_conte": None,
        "production_manifest": {
            "path": manifest_path.resolve().relative_to(root.resolve()).as_posix(),
            "sha256": sha256(manifest_path),
        },
        "comic_panel_plan_collection": {"path": context["plan_rel"], "sha256": context["plan_hash"]},
        "validation": {
            "status": "PASS",
            "ordered_entry_count": len(panels),
            "comic_panel_plan_count": len(panels),
            "unique_panel_count": len({panel.panel_id for panel in panels}),
            "unique_candidate_count": len({panel.candidate_id for panel in panels}),
            "source_hashes_verified": len(panels),
            "source_dimensions_verified": len(panels),
            "planning_boundary": "ComicPanelPlan only",
        },
        "canvas": canvas,
        "placements": placements,
        "artifacts": artifacts,
        "limitations": [
            "This deterministic packet measures layout and review readiness; it does not accept candidate art.",
            "Lettering rectangles reproduce the pinned ComicPanelPlan safe zones and are not final balloons.",
            "Generated and derivative pixels remain local under ignored experiment directories.",
        ],
    }
    report_path = output_dir / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"built {len(panels)}-panel complete-chapter review")
    print(f"long scroll: {clean.width}x{clean.height}; phone: {phone.width}x{phone.height}")
    print(f"build report: {report_path.relative_to(root).as_posix()} {sha256(report_path)}")
    return report


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="ng-chapter-review-") as temporary:
        root = Path(temporary)
        (root / "production/comic").mkdir(parents=True)
        (root / "experiments/sources").mkdir(parents=True)
        plans = []
        entries = []
        for index, size in enumerate(((320, 180), (180, 320), (260, 220)), start=1):
            panel_id = f"ng-ch05-self-test-p{index:03d}"
            image_path = root / "experiments/sources" / f"candidate-{index}.png"
            Image.new("RGB", size, (35 * index, 65 * index, 85)).save(image_path, format="PNG", compress_level=6)
            plans.append(
                {
                    "panel_id": panel_id,
                    "display_order": index,
                    "comic_direction": {
                        "lettering": {"safe_zones": [{"anchor": "top_left", "rect_norm": [0.04, 0.04, 0.3, 0.18]}]}
                    },
                }
            )
            entries.append(
                {
                    "order": index,
                    "panel_id": panel_id,
                    "candidate_id": f"self-test-{index}",
                    "source": {
                        "path": image_path.relative_to(root).as_posix(),
                        "sha256": sha256(image_path),
                        "width": size[0],
                        "height": size[1],
                    },
                    "layout": {"target_width": 280, "alignment": ("left", "center", "right")[index - 1], "gutter_after": 12},
                }
            )
        collection = {"record_type": "ComicPanelPlanCollection", "medium": "comic", "animation_shot_plan": None, "plans": plans}
        collection_path = root / "production/comic/panel-plans.json"
        collection_path.write_text(json.dumps(collection, indent=2) + "\n", encoding="utf-8")
        manifest = {
            "record_type": "ComicChapterProductionManifest",
            "schema_version": "1.0",
            "record_id": "ng-ch05-self-test-manifest",
            "medium": "comic",
            "chapter_complete": True,
            "animation_shot_plan": None,
            "e_conte": None,
            "comic_panel_plan_collection": {
                "path": collection_path.relative_to(root).as_posix(),
                "sha256": sha256(collection_path),
            },
            "canvas": {"width": 400, "side_margin": 40, "top_gutter": 12, "phone_width": 195, "phone_viewport_height": 220},
            "entries": entries,
        }
        manifest_path = root / "production/comic/manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        out = output_path(root, "experiments/review-packets/self-test")
        report = build(root, manifest_path, out)
        if report["validation"]["status"] != "PASS" or report["validation"]["ordered_entry_count"] != 3:
            raise AssertionError("self-test valid build did not report three passing entries")
        for key in ("long_scroll", "long_scroll_lettering_overlay", "contact_sheet", "phone_long_scroll"):
            if not (root / report["artifacts"][key]["path"]).is_file():
                raise AssertionError(f"self-test artifact missing: {key}")
        invalid = json.loads(json.dumps(manifest))
        invalid["entries"][1]["order"] = 3
        manifest_path.write_text(json.dumps(invalid, indent=2) + "\n", encoding="utf-8")
        try:
            validate_and_prepare(root, manifest_path)
        except ManifestError as exc:
            if "consecutively ordered" not in str(exc):
                raise AssertionError(f"self-test got unexpected order error: {exc}") from exc
        else:
            raise AssertionError("self-test failed to reject out-of-order entries")
        invalid = json.loads(json.dumps(manifest))
        invalid["e_conte"] = {"not": "allowed"}
        manifest_path.write_text(json.dumps(invalid, indent=2) + "\n", encoding="utf-8")
        try:
            validate_and_prepare(root, manifest_path)
        except ManifestError as exc:
            if "E-Conte" not in str(exc):
                raise AssertionError(f"self-test got unexpected E-Conte error: {exc}") from exc
        else:
            raise AssertionError("self-test failed to reject E-Conte")
    print("self-test PASS: deterministic build, order rejection, and planning-boundary rejection")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, help="Project-relative complete-chapter production manifest")
    parser.add_argument("--output-dir", help="Project-relative output directory beneath experiments/review-packets")
    parser.add_argument("--validate-only", action="store_true", help="Verify manifest, plan, hashes, and dimensions without writing output")
    parser.add_argument("--self-test", action="store_true", help="Run an isolated generated-fixture test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.manifest is None:
        raise SystemExit("--manifest is required unless --self-test is used")
    manifest_path, _ = project_path(ROOT, args.manifest.as_posix(), "manifest")
    if args.validate_only:
        manifest, _collection, panels, _context = validate_and_prepare(ROOT, manifest_path)
        print(f"validation PASS: {manifest['record_id']} / {len(panels)} ordered ComicPanelPlans / all sources verified")
        return 0
    default_name = f"ch05-complete-chapter-review-{load_json(manifest_path).get('record_id', 'unknown')}"
    destination = output_path(ROOT, args.output_dir or f"experiments/review-packets/{default_name}")
    destination.mkdir(parents=True, exist_ok=True)
    build(ROOT, manifest_path, destination)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ManifestError as exc:
        raise SystemExit(f"manifest error: {exc}") from exc
