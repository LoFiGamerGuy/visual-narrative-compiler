"""Build deterministic, local-only CH05 transparent-lettering review artifacts."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/lettering/ch05-transparent-lettering-rehearsal-r1.json"
ASSEMBLY = ROOT / "production/comic/assembly/ch05-variable-cadence-assembly-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
OUT = ROOT / "experiments/review-packets/ch05-transparent-lettering-rehearsal-r1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def srgb_luminance(rgb: tuple[int, int, int]) -> float:
    channels = []
    for value in rgb:
        value = value / 255.0
        channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, round((len(ordered) - 1) * fraction)))]


def safe_rect(image: Image.Image, zone: dict) -> tuple[int, int, int, int]:
    x, y, w, h = zone["rect_norm"]
    return (round(x * image.width), round(y * image.height), round((x + w) * image.width), round((y + h) * image.height))


def inset_rect(rect: tuple[int, int, int, int], fraction: float = 0.05) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = rect
    dx, dy = round((x1 - x0) * fraction), round((y1 - y0) * fraction)
    return x0 + dx, y0 + dy, x1 - dx, y1 - dy


def load_font(font_path: Path, max_size: int, rect: tuple[int, int, int, int], lines: list[str]) -> tuple[ImageFont.FreeTypeFont, int]:
    x0, y0, x1, y1 = rect
    for size in range(max_size, 9, -1):
        font = ImageFont.truetype(str(font_path), size)
        boxes = [font.getbbox(line) for line in lines]
        width = max(box[2] - box[0] for box in boxes)
        height = sum(box[3] - box[1] for box in boxes) + round(size * 0.22) * (len(lines) - 1)
        if width <= (x1 - x0) * 0.76 and height <= (y1 - y0) * 0.66:
            return font, size
    raise ValueError("review copy cannot fit safe zone")


def render_subject(source: Image.Image, rect: tuple[int, int, int, int], treatment: dict, font_path: Path,
                   requested_font: int, lines: list[str], phone_scale: float) -> tuple[Image.Image, dict]:
    balloon = inset_rect(rect)
    font, font_size = load_font(font_path, requested_font, balloon, lines)
    outline = max(2, round(treatment["outline_px_at_phone"] / phone_scale))
    radius = max(12, round(min(balloon[2] - balloon[0], balloon[3] - balloon[1]) * 0.18))
    overlay = Image.new("RGBA", source.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    alpha = round(treatment["fill_opacity"] * 255)
    draw.rounded_rectangle(balloon, radius=radius, fill=tuple(treatment["fill_rgb"]) + (alpha,),
                           outline=tuple(treatment["outline_rgb"]) + (255,), width=outline)
    boxes = [font.getbbox(line) for line in lines]
    line_gap = round(font_size * 0.22)
    heights = [box[3] - box[1] for box in boxes]
    total_height = sum(heights) + line_gap * (len(lines) - 1)
    cursor_y = balloon[1] + ((balloon[3] - balloon[1]) - total_height) // 2
    text_rgb = (20, 23, 26, 255)
    for line, box, height in zip(lines, boxes, heights):
        width = box[2] - box[0]
        x = balloon[0] + ((balloon[2] - balloon[0]) - width) // 2 - box[0]
        draw.text((x, cursor_y - box[1]), line, font=font, fill=text_rgb)
        cursor_y += height + line_gap
    composited = Image.alpha_composite(source.convert("RGBA"), overlay).convert("RGB")

    crop = source.convert("RGB").crop(balloon)
    pixels = list(crop.get_flattened_data())
    fill = tuple(treatment["fill_rgb"])
    opacity = treatment["fill_opacity"]
    backing_luma = []
    for pixel in pixels:
        mixed = tuple(round(opacity * fill[i] + (1.0 - opacity) * pixel[i]) for i in range(3))
        backing_luma.append(srgb_luminance(mixed))
    contrast = [(value + 0.05) / 0.05 for value in backing_luma]
    metrics = {
        "safe_rect_px": list(rect),
        "balloon_rect_px": list(balloon),
        "safe_zone_coverage_fraction": round(((balloon[2] - balloon[0]) * (balloon[3] - balloon[1])) / ((rect[2] - rect[0]) * (rect[3] - rect[1])), 6),
        "font_size_source_px": font_size,
        "font_size_phone_px": round(font_size * phone_scale, 3),
        "outline_source_px": outline,
        "outline_phone_px": round(outline * phone_scale, 3),
        "black_type_contrast_ratio_min": round(min(contrast), 3),
        "black_type_contrast_ratio_p05": round(percentile(contrast, 0.05), 3),
        "black_type_contrast_ratio_median": round(percentile(contrast, 0.50), 3),
        "background_luma_stddev": round(ImageStat.Stat(crop.convert("L")).stddev[0], 3),
        "measurement_boundary": "Computed backing contrast only; excludes the black outline and glyph raster and cannot detect semantic occlusion."
    }
    return composited, metrics


def canvas_phone_preview(image: Image.Image, entry: dict) -> Image.Image:
    canvas = Image.new("RGB", (1200, round(image.height * entry["target_width"] / image.width) + 100), (18, 21, 26))
    panel_h = round(image.height * entry["target_width"] / image.width)
    panel = image.resize((entry["target_width"], panel_h), Image.Resampling.LANCZOS)
    x = {"left": 80, "center": (1200 - entry["target_width"]) // 2, "right": 1120 - entry["target_width"]}[entry["alignment"]]
    canvas.paste(panel, (x, 50))
    return canvas.resize((390, round(canvas.height * 390 / 1200)), Image.Resampling.LANCZOS)


def label_card(image: Image.Image, title: str, subtitle: str, width: int = 520) -> Image.Image:
    height = round(image.height * width / image.width)
    thumb = image.resize((width, height), Image.Resampling.LANCZOS)
    card = Image.new("RGB", (width + 24, height + 92), "white")
    card.paste(thumb, (12, 72))
    draw = ImageDraw.Draw(card)
    draw.text((14, 12), title, fill=(18, 21, 26))
    draw.text((14, 38), subtitle, fill=(70, 75, 82))
    return card


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    font_path = Path(manifest["font"]["local_path"])
    if not font_path.is_file() or digest(font_path) != manifest["font"]["sha256"]:
        raise SystemExit("hash-pinned lettering font is unavailable or changed")
    entries = {item["candidate_id"]: item for item in assembly["entries"]}
    plan_map = {item["panel_id"]: item for item in plans["plans"]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "composites").mkdir(exist_ok=True)
    (OUT / "phone-previews").mkdir(exist_ok=True)
    records, cards, artifacts = [], [], []
    for subject in manifest["subjects"]:
        entry = entries[subject["candidate_id"]]
        if entry["panel_id"] != subject["panel_id"]:
            raise SystemExit(f"subject binding mismatch: {subject['candidate_id']}")
        source_path = ROOT / entry["source_path"]
        if digest(source_path) != entry["source_sha256"]:
            raise SystemExit(f"source hash mismatch: {subject['candidate_id']}")
        with Image.open(source_path) as opened:
            source = opened.convert("RGB")
        zone = plan_map[subject["panel_id"]]["comic_direction"]["lettering"]["safe_zones"][0]
        rect = safe_rect(source, zone)
        phone_scale = entry["target_width"] / source.width * 390 / 1200
        requested_font = max(10, round(manifest["font"]["target_phone_font_px"] / phone_scale))
        for treatment in manifest["treatments"]:
            rendered, metrics = render_subject(source, rect, treatment, font_path, requested_font, manifest["review_copy"], phone_scale)
            stem = f"{subject['candidate_id']}-{treatment['treatment_id']}"
            composite_path = OUT / "composites" / f"{stem}.png"
            phone_path = OUT / "phone-previews" / f"{stem}-phone.png"
            rendered.save(composite_path)
            phone = canvas_phone_preview(rendered, entry)
            phone.save(phone_path)
            artifacts.extend([composite_path, phone_path])
            record = {
                "candidate_id": subject["candidate_id"], "panel_id": subject["panel_id"], "subject_class": subject["class"],
                "treatment_id": treatment["treatment_id"], "source_path": entry["source_path"], "source_sha256": entry["source_sha256"],
                "safe_zone": zone, "phone_scale": round(phone_scale, 6), "metrics": metrics,
                "composite": {"path": composite_path.relative_to(ROOT).as_posix(), "sha256": digest(composite_path), "dimensions": list(rendered.size)},
                "phone_preview": {"path": phone_path.relative_to(ROOT).as_posix(), "sha256": digest(phone_path), "dimensions": list(phone.size)}
            }
            records.append(record)
            cards.append(label_card(phone, f"{subject['candidate_id']} · {treatment['treatment_id']}",
                                    f"phone type {metrics['font_size_phone_px']}px · p05 contrast {metrics['black_type_contrast_ratio_p05']}:1"))
    cols = 3
    rows = math.ceil(len(cards) / cols)
    cell_w = max(card.width for card in cards)
    cell_h = max(card.height for card in cards)
    sheet = Image.new("RGB", (cols * cell_w + 40, rows * cell_h + 100), (232, 234, 238))
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 18), "CH05 transparent lettering rehearsal · non-canon review copy", fill=(18, 21, 26))
    draw.text((20, 46), "Rows: c005/c014 dense outliers, c013/h001 clean controls · columns: 96% / 88% / 76% backing", fill=(70, 75, 82))
    for index, card in enumerate(cards):
        x = 20 + (index % cols) * cell_w
        y = 88 + (index // cols) * cell_h
        sheet.paste(card, (x, y))
    sheet_path = OUT / "ch05-transparent-lettering-phone-comparison-r1.png"
    sheet.save(sheet_path)
    artifacts.append(sheet_path)
    inventory = [{"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "bytes": path.stat().st_size} for path in sorted(artifacts)]
    root = hashlib.sha256("".join(item["path"] + ":" + item["sha256"] + "\n" for item in inventory).encode()).hexdigest()
    packet = {
        "record_type": "ComicLetteringRehearsalPacket", "schema_version": "1.0",
        "record_id": "ng-ch05-transparent-lettering-rehearsal-packet-r1", "state": "OWNER_REVIEW_PENDING_UNACCEPTED",
        "manifest": {"path": MANIFEST.relative_to(ROOT).as_posix(), "sha256": digest(MANIFEST)},
        "font": manifest["font"], "review_copy": manifest["review_copy"], "review_copy_is_canon": False,
        "records": records, "comparison_sheet": {"path": sheet_path.relative_to(ROOT).as_posix(), "sha256": digest(sheet_path), "dimensions": list(sheet.size)},
        "artifact_count": len(inventory), "artifact_inventory_root_sha256": root, "artifacts": inventory,
        "provider_calls": 0, "uploads": 0, "cost_usd": 0, "human_review_minutes": None, "accepted_treatments": [],
        "boundary": "Measured local review artifacts only; no lettering, dialogue, art, or production base is accepted."
    }
    packet_path = OUT / "lettering-rehearsal-packet.json"
    packet_path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(records)} lettering treatments / {len(inventory)} artifacts; root {root}; packet {digest(packet_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
