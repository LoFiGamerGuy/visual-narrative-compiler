"""Build local outside-art lettering-band alternatives over the CH05 cadence assembly."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/lettering/ch05-outside-art-lettering-band-r1.json"
ASSEMBLY = ROOT / "production/comic/assembly/ch05-variable-cadence-assembly-r1.json"
OUT = ROOT / "experiments/review-packets/ch05-outside-art-lettering-band-r1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def place_x(entry: dict, canvas: dict) -> int:
    if entry["target_width"] == canvas["width"]:
        return 0
    if entry["alignment"] == "left":
        return canvas["side_margin"]
    if entry["alignment"] == "right":
        return canvas["width"] - canvas["side_margin"] - entry["target_width"]
    return (canvas["width"] - entry["target_width"]) // 2


def load_source(entry: dict) -> Image.Image:
    path = ROOT / entry["source_path"]
    if not path.is_file() or sha(path) != entry["source_sha256"]:
        raise ValueError(f"source hash mismatch: {entry['candidate_id']}")
    with Image.open(path) as opened:
        image = opened.convert("RGB")
    if list(image.size) != entry["source_dimensions"]:
        raise ValueError(f"source dimensions mismatch: {entry['candidate_id']}")
    return image


def draw_centered(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], lines: list[str], font: ImageFont.FreeTypeFont, fill: tuple[int, int, int]) -> None:
    boxes = [font.getbbox(line) for line in lines]
    gap = 6
    heights = [box[3] - box[1] for box in boxes]
    total = sum(heights) + gap * (len(lines) - 1)
    cursor = rect[1] + ((rect[3] - rect[1]) - total) // 2
    for line, box, height in zip(lines, boxes, heights):
        width = box[2] - box[0]
        x = rect[0] + ((rect[2] - rect[0]) - width) // 2 - box[0]
        draw.text((x, cursor - box[1]), line, font=font, fill=fill)
        cursor += height + gap


def save_artifact(path: Path, image: Image.Image) -> dict:
    image.save(path, optimize=False)
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "width": image.width, "height": image.height, "bytes": path.stat().st_size}


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    font_path = Path(manifest["font"]["local_path"])
    if not font_path.is_file() or sha(font_path) != manifest["font"]["sha256"]:
        raise SystemExit("hash-pinned lettering font unavailable or changed")
    font = ImageFont.truetype(str(font_path), manifest["font"]["assembly_size_px"])
    subject_ids = {item["candidate_id"] for item in manifest["subjects"]}
    OUT.mkdir(parents=True, exist_ok=True)
    artifacts, treatment_records = [], []
    canvas_spec = assembly["canvas"]
    prepared = []
    for entry in assembly["entries"]:
        source = load_source(entry)
        height = round(source.height * entry["target_width"] / source.width)
        prepared.append((entry, source.resize((entry["target_width"], height), Image.Resampling.LANCZOS)))
    for treatment in manifest["treatments"]:
        band_count = sum(entry["candidate_id"] in subject_ids for entry, _ in prepared)
        total_height = canvas_spec["default_gutter"] + sum(image.height + entry["gutter_after"] for entry, image in prepared) + band_count * manifest["band_height_px"]
        scroll = Image.new("RGB", (canvas_spec["width"], total_height), canvas_spec["background"])
        draw = ImageDraw.Draw(scroll)
        y = canvas_spec["default_gutter"]
        placements = []
        for entry, image in prepared:
            x = place_x(entry, canvas_spec)
            band_rect = None
            if entry["candidate_id"] in subject_ids:
                band_rect = [x, y, x + entry["target_width"], y + manifest["band_height_px"]]
                draw.rectangle(tuple(band_rect), fill=tuple(treatment["band_rgb"]))
                if treatment["outline_rgb"] is not None:
                    draw.rectangle(tuple(band_rect), outline=tuple(treatment["outline_rgb"]), width=3)
                draw_centered(draw, tuple(band_rect), manifest["review_copy"], font, tuple(treatment["text_rgb"]))
                y += manifest["band_height_px"]
            image_rect = [x, y, x + image.width, y + image.height]
            scroll.paste(image, (x, y))
            placements.append({"candidate_id": entry["candidate_id"], "panel_id": entry["panel_id"], "band_rect_px": band_rect, "image_rect_px": image_rect, "source_pixel_overlap": 0})
            y += image.height + entry["gutter_after"]
        scroll_path = OUT / f"ch05-scroll-{treatment['treatment_id']}-r1.png"
        scroll_artifact = save_artifact(scroll_path, scroll)
        phone = scroll.resize((390, round(scroll.height * 390 / 1200)), Image.Resampling.LANCZOS)
        phone_path = OUT / f"ch05-scroll-{treatment['treatment_id']}-phone-390px-r1.png"
        phone_artifact = save_artifact(phone_path, phone)
        artifacts.extend([scroll_artifact, phone_artifact])
        treatment_records.append({
            "treatment_id": treatment["treatment_id"], "scroll": scroll_artifact, "phone_scroll": phone_artifact,
            "band_count": band_count, "band_height_assembly_px": manifest["band_height_px"],
            "band_height_phone_px": round(manifest["band_height_px"] * 390 / 1200, 3),
            "font_size_assembly_px": manifest["font"]["assembly_size_px"], "font_size_phone_px": round(manifest["font"]["assembly_size_px"] * 390 / 1200, 3),
            "source_pixels_changed": 0, "placements": placements
        })
    # Compact side-by-side phone-scroll strips for direct owner comparison.
    phones = []
    for record in treatment_records:
        with Image.open(ROOT / record["phone_scroll"]["path"]) as opened:
            phones.append(opened.convert("RGB"))
    sheet = Image.new("RGB", (820, max(x.height for x in phones) + 100), (232, 234, 238))
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 15), "CH05 outside-art lettering band comparison · non-canon review copy", fill=(18, 21, 26))
    draw.text((20, 43), "Left: light caption band · right: direct gutter text · both preserve all source pixels", fill=(70, 75, 82))
    sheet.paste(phones[0], (15, 88)); sheet.paste(phones[1], (415, 88))
    sheet_path = OUT / "ch05-outside-art-lettering-band-comparison-r1.png"
    sheet_artifact = save_artifact(sheet_path, sheet)
    artifacts.append(sheet_artifact)
    inventory_root = hashlib.sha256("".join(x["path"] + ":" + x["sha256"] + "\n" for x in sorted(artifacts, key=lambda x: x["path"])).encode()).hexdigest()
    packet = {
        "record_type": "ComicOutsideArtLetteringBandPacket", "schema_version": "1.0",
        "record_id": "ng-ch05-outside-art-lettering-band-packet-r1", "state": "LOCAL_NONPLAN_REVIEW_READY_UNACCEPTED",
        "manifest": {"path": MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha(MANIFEST)},
        "assembly": {"path": ASSEMBLY.relative_to(ROOT).as_posix(), "sha256": sha(ASSEMBLY)},
        "treatments": treatment_records, "comparison_sheet": sheet_artifact,
        "artifact_count": len(artifacts), "artifact_inventory_root_sha256": inventory_root,
        "provider_calls": 0, "uploads": 0, "cost_usd": 0, "human_review_minutes": None, "accepted_treatments": [],
        "comic_panel_plan_revision_created": False, "assembly_revision_created": False,
        "boundary": "Outside-art geometry demonstration only; caption/direct-text semantics do not authorize dialogue, plan, assembly, or production changes."
    }
    packet_path = OUT / "outside-art-lettering-band-packet.json"
    with packet_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(packet, indent=2) + "\n")
    print(f"built 2 outside-art scrolls / {len(artifacts)} artifacts; full {treatment_records[0]['scroll']['width']}x{treatment_records[0]['scroll']['height']}; phone {treatment_records[0]['phone_scroll']['width']}x{treatment_records[0]['phone_scroll']['height']}; packet {sha(packet_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
