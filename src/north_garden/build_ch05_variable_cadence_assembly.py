"""Build a deterministic variable-width CH05 vertical-scroll assembly from selected candidates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageStat

import build_ch05_overnight_review_packet as packet_tools


ROOT = Path(__file__).resolve().parents[2]
ASSEMBLY = ROOT / "production/comic/assembly/ch05-variable-cadence-assembly-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
OUT = ROOT / "experiments/review-packets/ch05-variable-cadence-assembly-r1"
PACKET = OUT / "assembly-packet.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def load_source(entry: dict) -> Image.Image:
    path = ROOT / entry["source_path"]
    if sha256(path) != entry["source_sha256"]:
        raise ValueError(f"source hash mismatch: {entry['candidate_id']}")
    image = Image.open(path).convert("RGB")
    if list(image.size) != entry["source_dimensions"]:
        raise ValueError(f"source dimensions mismatch: {entry['candidate_id']}")
    return image


def safe_metrics(image: Image.Image, rect_norm: list[float]) -> dict:
    x, y, w, h = rect_norm
    rect = (round(x * image.width), round(y * image.height), round((x + w) * image.width), round((y + h) * image.height))
    crop = image.crop(rect).convert("L")
    edge = crop.filter(ImageFilter.FIND_EDGES)
    return {
        "source_rect_px": list(rect),
        "luma_mean": round(ImageStat.Stat(crop).mean[0], 3),
        "luma_stddev": round(ImageStat.Stat(crop).stddev[0], 3),
        "edge_mean": round(ImageStat.Stat(edge).mean[0], 3)
    }


def place_x(entry: dict, canvas: dict) -> int:
    if entry["alignment"] == "left":
        return canvas["side_margin"]
    if entry["alignment"] == "right":
        return canvas["width"] - canvas["side_margin"] - entry["target_width"]
    return (canvas["width"] - entry["target_width"]) // 2


def artifact(path: Path, image: Image.Image) -> dict:
    image.save(path, optimize=False)
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "width": image.width, "height": image.height}


def main() -> int:
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    plan_by_id = {item["panel_id"]: item for item in plans["plans"]}
    canvas_spec = assembly["canvas"]
    prepared = []
    total_height = canvas_spec["default_gutter"]
    for entry in assembly["entries"]:
        source = load_source(entry)
        target_h = round(source.height * entry["target_width"] / source.width)
        resized = source.resize((entry["target_width"], target_h), Image.Resampling.LANCZOS)
        safe = plan_by_id[entry["panel_id"]]["comic_direction"]["lettering"]["safe_zones"][0]
        prepared.append((entry, source, resized, safe))
        total_height += target_h + entry["gutter_after"]
    clean = Image.new("RGB", (canvas_spec["width"], total_height), canvas_spec["background"])
    overlay = clean.copy()
    overlay_draw = ImageDraw.Draw(overlay, "RGBA")
    placements = []
    y = canvas_spec["default_gutter"]
    for entry, source, resized, safe in prepared:
        x = place_x(entry, canvas_spec)
        clean.paste(resized, (x, y))
        overlay.paste(resized, (x, y))
        sx, sy, sw, sh = safe["rect_norm"]
        rect = (x + round(sx * resized.width), y + round(sy * resized.height), x + round((sx + sw) * resized.width), y + round((sy + sh) * resized.height))
        overlay_draw.rectangle(rect, fill=(18, 196, 235, 66), outline=(0, 150, 190, 255), width=4)
        overlay_draw.text((x, max(5, y - 30)), f"{entry['order']:02d} {entry['panel_id'].split('-')[-1].upper()} {entry['candidate_id']} {entry['cadence_role']}", fill=(235, 239, 242, 255), font=font(18))
        metrics = safe_metrics(source, safe["rect_norm"])
        placements.append({
            "order": entry["order"], "panel_id": entry["panel_id"], "candidate_id": entry["candidate_id"],
            "rect_px": [x, y, resized.width, resized.height], "safe_zone": {"anchor": safe["anchor"], "rect_norm": safe["rect_norm"], "assembly_rect_px": list(rect), **metrics}
        })
        y += resized.height + entry["gutter_after"]
    OUT.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "vertical_scroll_clean": artifact(OUT / "ch05-variable-cadence-scroll-clean-r1.png", clean),
        "vertical_scroll_safe_zones": artifact(OUT / "ch05-variable-cadence-scroll-safe-zones-r1.png", overlay)
    }
    phone_h = round(clean.height * canvas_spec["phone_width"] / clean.width)
    phone = clean.resize((canvas_spec["phone_width"], phone_h), Image.Resampling.LANCZOS)
    artifacts["phone_scroll"] = artifact(OUT / "ch05-variable-cadence-phone-scroll-390px-r1.png", phone)
    slices_dir = OUT / "phone-viewport-slices"
    slices_dir.mkdir(parents=True, exist_ok=True)
    slices = []
    top = 0
    index = 1
    while top < phone.height:
        frame = Image.new("RGB", (canvas_spec["phone_width"], canvas_spec["phone_viewport_height"]), canvas_spec["background"])
        crop = phone.crop((0, top, phone.width, min(phone.height, top + canvas_spec["phone_viewport_height"])))
        frame.paste(crop, (0, 0))
        path = slices_dir / f"viewport-{index:02d}.png"
        slices.append({"index": index, "source_top_px": top, **artifact(path, frame)})
        top += canvas_spec["phone_slice_step"]
        index += 1
    artifacts["phone_viewport_slices"] = slices
    all_registry_entries = []
    for path in [ROOT / "experiments/review-packets/ch05-overnight-production-r1/candidate-registry.json", ROOT / "experiments/review-packets/ch05-cadence-hardening-r1/candidate-registry.json"]:
        all_registry_entries.extend(json.loads(path.read_text(encoding="utf-8"))["entries"])
    by_id = {item["candidate_id"]: item for item in all_registry_entries}
    packet_tools.OUT = OUT
    sequence_artifacts = []
    for sequence in assembly["sequences"]:
        ids = [entry["candidate_id"] for entry in assembly["entries"] if entry["sequence_id"] == sequence["sequence_id"]]
        image = packet_tools.build_grid(f"CH05 SELECTED SEQUENCE - {sequence['sequence_id'].replace('_', ' ').upper()}", "Selected engineering candidates in ComicPanelPlan order; owner acceptance pending", [by_id[cid] for cid in ids], columns=3, cell=(620, 700), render_mode="clean", plans=plan_by_id)
        sequence_artifacts.append({"sequence_id": sequence["sequence_id"], **artifact(OUT / f"sequence-selected-{sequence['sequence_id']}.png", image)})
    artifacts["selected_sequences"] = sequence_artifacts
    packet = {
        "record_type": "CH05VariableCadenceAssemblyPacket", "schema_version": "1.0", "record_id": "ng-ch05-variable-cadence-assembly-packet-r1",
        "state": "READY_FOR_OWNER_CADENCE_REVIEW_UNACCEPTED", "assembly": {"path": ASSEMBLY.relative_to(ROOT).as_posix(), "sha256": sha256(ASSEMBLY)},
        "panel_plan_collection": {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha256(PLANS)}, "panel_count": len(placements),
        "sequence_count": len(assembly["sequences"]), "canvas": canvas_spec, "placements": placements, "artifacts": artifacts,
        "boundary": "Local deterministic assembly of unaccepted ignored candidates; no exact-base promotion, provider activity, or new production-planning record."
    }
    PACKET.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"built 14-panel cadence assembly: {clean.width}x{clean.height}; phone {phone.width}x{phone.height}; {len(slices)} viewport slices")
    print(f"packet: {PACKET.relative_to(ROOT)} {sha256(PACKET)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
