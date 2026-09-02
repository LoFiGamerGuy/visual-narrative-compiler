"""Build local 88%-backing width/copy sensitivity previews for selected CH05 panels."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

from build_ch05_transparent_lettering_rehearsal import digest, render_subject, safe_rect


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/lettering/ch05-lettering-width-copy-sensitivity-r1.json"
ASSEMBLY = ROOT / "production/comic/assembly/ch05-variable-cadence-assembly-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
OUT = ROOT / "experiments/review-packets/ch05-lettering-width-copy-sensitivity-r1"


def phone_preview(image: Image.Image, target_width: int, alignment: str) -> Image.Image:
    panel_h = round(image.height * target_width / image.width)
    canvas = Image.new("RGB", (1200, panel_h + 100), (18, 21, 26))
    panel = image.resize((target_width, panel_h), Image.Resampling.LANCZOS)
    x = {"left": 0 if target_width == 1200 else 80,
         "center": (1200 - target_width) // 2,
         "right": 0 if target_width == 1200 else 1120 - target_width}[alignment]
    x = max(0, min(1200 - target_width, x))
    canvas.paste(panel, (x, 50))
    return canvas.resize((390, round(canvas.height * 390 / 1200)), Image.Resampling.LANCZOS)


def card(preview: Image.Image, title: str, subtitle: str, width: int = 390) -> Image.Image:
    image = preview if preview.width == width else preview.resize((width, round(preview.height * width / preview.width)), Image.Resampling.LANCZOS)
    result = Image.new("RGB", (width + 20, image.height + 76), "white")
    draw = ImageDraw.Draw(result)
    draw.text((10, 10), title, fill=(18, 21, 26))
    draw.text((10, 35), subtitle, fill=(70, 75, 82))
    result.paste(image, (10, 66))
    return result


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    entries = {item["candidate_id"]: item for item in assembly["entries"]}
    plan_map = {item["panel_id"]: item for item in plans["plans"]}
    font_path = Path(manifest["font"]["local_path"])
    if not font_path.is_file() or digest(font_path) != manifest["font"]["sha256"]:
        raise SystemExit("hash-pinned lettering font is unavailable or changed")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "phone-previews").mkdir(exist_ok=True)
    records, cards, artifacts = [], [], []
    treatment = manifest["backing_treatment"]
    for subject in manifest["subjects"]:
        entry = entries[subject["candidate_id"]]
        source_path = ROOT / entry["source_path"]
        if entry["panel_id"] != subject["panel_id"] or digest(source_path) != entry["source_sha256"]:
            raise SystemExit(f"source binding mismatch: {subject['candidate_id']}")
        with Image.open(source_path) as opened:
            source = opened.convert("RGB")
        zone = plan_map[subject["panel_id"]]["comic_direction"]["lettering"]["safe_zones"][0]
        rect = safe_rect(source, zone)
        for copy_load in manifest["copy_loads"]:
            for width in subject["sweep_widths"]:
                scale = width / source.width * manifest["phone_canvas_width"] / manifest["chapter_canvas_width"]
                rendered, metrics = render_subject(source, rect, treatment, font_path, 512, copy_load["lines"], scale)
                preview = phone_preview(rendered, width, entry["alignment"])
                stem = f"{subject['candidate_id']}-{copy_load['copy_id']}-w{width}"
                path = OUT / "phone-previews" / f"{stem}.png"
                preview.save(path)
                artifacts.append(path)
                passes = metrics["font_size_phone_px"] >= manifest["target_phone_font_px"]
                record = {
                    "candidate_id": subject["candidate_id"], "panel_id": subject["panel_id"], "copy_id": copy_load["copy_id"],
                    "copy_lines": copy_load["lines"], "copy_is_canon": False, "target_width": width, "is_current_width": width == subject["current_width"],
                    "phone_scale": round(scale, 6), "font_size_source_px": metrics["font_size_source_px"],
                    "font_size_phone_px": metrics["font_size_phone_px"], "meets_13px_target": passes,
                    "black_type_contrast_ratio_p05": metrics["black_type_contrast_ratio_p05"],
                    "preview": {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "dimensions": list(preview.size)}
                }
                records.append(record)
                cards.append(card(preview, f"{stem} {'PASS' if passes else 'FAIL'}", f"phone type {metrics['font_size_phone_px']}px · p05 contrast {metrics['black_type_contrast_ratio_p05']}:1"))
    cols = 3
    rows = math.ceil(len(cards) / cols)
    cell_w, cell_h = max(x.width for x in cards), max(x.height for x in cards)
    sheet = Image.new("RGB", (cols * cell_w + 40, rows * cell_h + 105), (232, 234, 238))
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 18), "CH05 lettering width × copy sensitivity · 88% backing · non-canon review copy", fill=(18, 21, 26))
    draw.text((20, 45), "PASS means rendered type ≥13px at actual 390px chapter footprint; semantic clearance remains separate", fill=(70, 75, 82))
    for index, item in enumerate(cards):
        sheet.paste(item, (20 + (index % cols) * cell_w, 92 + (index // cols) * cell_h))
    sheet_path = OUT / "ch05-lettering-width-copy-sensitivity-r1.png"
    sheet.save(sheet_path)
    artifacts.append(sheet_path)
    inventory = [{"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "bytes": path.stat().st_size} for path in sorted(artifacts)]
    inventory_root = hashlib.sha256("".join(x["path"] + ":" + x["sha256"] + "\n" for x in inventory).encode()).hexdigest()
    thresholds = {}
    for subject in manifest["subjects"]:
        thresholds[subject["candidate_id"]] = {}
        for copy_load in manifest["copy_loads"]:
            matching = [r for r in records if r["candidate_id"] == subject["candidate_id"] and r["copy_id"] == copy_load["copy_id"] and r["meets_13px_target"]]
            thresholds[subject["candidate_id"]][copy_load["copy_id"]] = min((r["target_width"] for r in matching), default=None)
    packet = {
        "record_type": "ComicLetteringWidthCopySensitivityPacket", "schema_version": "1.0",
        "record_id": "ng-ch05-lettering-width-copy-sensitivity-packet-r1", "state": "LOCAL_MEASURED_OWNER_REVIEW_PENDING",
        "manifest": {"path": MANIFEST.relative_to(ROOT).as_posix(), "sha256": digest(MANIFEST)},
        "records": records, "minimum_passing_widths": thresholds,
        "comparison_sheet": {"path": sheet_path.relative_to(ROOT).as_posix(), "sha256": digest(sheet_path), "dimensions": list(sheet.size)},
        "artifact_count": len(inventory), "artifact_inventory_root_sha256": inventory_root, "artifacts": inventory,
        "provider_calls": 0, "uploads": 0, "cost_usd": 0, "human_review_minutes": None, "accepted_layouts": [],
        "boundary": "A measured type-size pass is not a ComicPanelPlan revision, semantic-clearance pass, final-copy pass, or acceptance."
    }
    packet_path = OUT / "width-copy-sensitivity-packet.json"
    with packet_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(packet, indent=2) + "\n")
    print(f"built {len(records)} width/copy cases / {len(inventory)} artifacts; thresholds {json.dumps(thresholds, sort_keys=True)}; packet {digest(packet_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
