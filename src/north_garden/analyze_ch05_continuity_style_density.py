"""Measure CH05 phone-scale visual density and style engineering results without identity inference."""
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-instrumented-production-manifest-r1.json"
INITIAL = ROOT / "docs/research/evidence/ch05-overnight-production-r1.json"
HARDENING = ROOT / "docs/research/evidence/ch05-cadence-hardening-r1.json"
ASSEMBLY_REVIEW = ROOT / "production/comic/review/ch05-variable-cadence-assembly-review-r1.json"
FONT_PATH = Path("C:/Windows/Fonts/arialbd.ttf")
FONT_SHA = "e8f4e3baf6cc35fed6fcce3a540e8b39e8f6cda1d22a28f2ec8f526fef7a43f5"
OUT = ROOT / "experiments/review-packets/ch05-continuity-style-density-r1"

STYLES = ["cel_painted", "clear_line_watercolor", "limited_ink_flat", "clean_graphic"]
STYLE_COLORS = {
    "cel_painted": (70, 155, 235), "clear_line_watercolor": (63, 181, 139),
    "limited_ink_flat": (224, 170, 70), "clean_graphic": (194, 102, 196)
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def engineering_state(candidate: dict) -> str:
    values = list(candidate["engineering_review"]["results"].values())
    if any(str(value).startswith("FAIL") for value in values): return "fail"
    if any(str(value).startswith("WARN") for value in values): return "warn"
    return "pass"


def colorfulness(array: np.ndarray) -> float:
    rgb = array.astype(np.float64)
    rg = rgb[:, :, 0] - rgb[:, :, 1]
    yb = 0.5 * (rgb[:, :, 0] + rgb[:, :, 1]) - rgb[:, :, 2]
    return float(math.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * math.sqrt(rg.mean() ** 2 + yb.mean() ** 2))


def color_entropy(array: np.ndarray) -> float:
    q = (array.astype(np.uint16) >> 4)
    keys = q[:, :, 0] * 256 + q[:, :, 1] * 16 + q[:, :, 2]
    _, counts = np.unique(keys, return_counts=True)
    probabilities = counts / counts.sum()
    return float(-(probabilities * np.log2(probabilities)).sum())


def metrics(path: Path, target_width: int) -> tuple[dict, Image.Image]:
    with Image.open(path) as opened:
        source = opened.convert("RGB")
    phone_width = round(target_width * 390 / 1200)
    phone_height = round(source.height * phone_width / source.width)
    phone = source.resize((phone_width, phone_height), Image.Resampling.LANCZOS)
    luma = phone.convert("L")
    edge = luma.filter(ImageFilter.FIND_EDGES)
    if edge.width > 2 and edge.height > 2:
        edge = ImageOps.crop(edge, 1)
    edge_array = np.asarray(edge, dtype=np.uint8)
    rgb = np.asarray(phone, dtype=np.uint8)
    luma_stat = ImageStat.Stat(luma)
    return ({
        "phone_dimensions": [phone.width, phone.height],
        "luma_mean": round(luma_stat.mean[0], 3), "luma_stddev": round(luma_stat.stddev[0], 3),
        "luma_entropy_bits": round(luma.entropy(), 4),
        "edge_mean": round(float(edge_array.mean()), 4), "edge_occupancy_ge_32": round(float((edge_array >= 32).mean()), 6),
        "colorfulness": round(colorfulness(rgb), 4), "quantized_color_entropy_bits": round(color_entropy(rgb), 4),
        "black_clip_fraction": round(float((np.asarray(luma) <= 15).mean()), 6),
        "white_clip_fraction": round(float((np.asarray(luma) >= 240).mean()), 6),
        "measurement_boundary": "Global phone-footprint image statistics; cannot identify people, hair, wardrobe, hands, story objects, causality, or aesthetic acceptance."
    }, phone)


def draw_montage(records: list[dict], phones: dict[str, Image.Image]) -> Image.Image:
    cols, cell_w, cell_h = 4, 340, 470
    rows = math.ceil(len(records) / cols)
    image = Image.new("RGB", (cols * cell_w + 40, rows * cell_h + 100), (230, 233, 238))
    draw = ImageDraw.Draw(image)
    draw.text((20, 16), "CH05 selected 14 · actual phone-footprint density montage", font=font(24), fill=(18, 21, 26))
    draw.text((20, 50), "Dimensions reflect each panel's current 390/1200 cadence scale; identity/wardrobe review is manual", font=font(16), fill=(70, 75, 82))
    for index, record in enumerate(records):
        x = 20 + (index % cols) * cell_w; y = 88 + (index // cols) * cell_h
        draw.rectangle((x, y, x + cell_w - 12, y + cell_h - 12), fill="white")
        phone = phones[record["candidate_id"]].copy()
        phone.thumbnail((cell_w - 36, 340), Image.Resampling.LANCZOS)
        px = x + (cell_w - 12 - phone.width) // 2; py = y + 14
        image.paste(phone, (px, py))
        m = record["metrics"]
        ty = y + 360
        draw.text((x + 12, ty), f"{record['order']:02d} {record['candidate_id']} · {record['style_id']}", font=font(16), fill=(18, 21, 26))
        draw.text((x + 12, ty + 26), f"{m['phone_dimensions'][0]}×{m['phone_dimensions'][1]}px · edge {m['edge_occupancy_ge_32']:.3f}", font=font(14), fill=(70, 75, 82))
        draw.text((x + 12, ty + 49), f"entropy {m['luma_entropy_bits']:.2f} · color {m['colorfulness']:.1f}", font=font(14), fill=(70, 75, 82))
    return image


def draw_style_results(style_results: dict) -> Image.Image:
    image = Image.new("RGB", (1200, 620), (235, 237, 241)); draw = ImageDraw.Draw(image)
    draw.text((36, 25), "CH05 all-26 engineering triage by style", font=font(28), fill=(18, 21, 26))
    draw.text((36, 65), "Unbalanced panel tasks; counts describe this run and are not a universal model/style score", font=font(17), fill=(75, 80, 87))
    colors = {"pass": (48, 145, 105), "warn": (207, 157, 55), "fail": (181, 68, 78)}
    for index, style in enumerate(STYLES):
        y = 130 + index * 110
        counts = style_results[style]
        total = sum(counts.values())
        draw.text((40, y), style, font=font(21), fill=(18, 21, 26))
        cursor = 330
        for state in ("pass", "warn", "fail"):
            width = round(760 * counts.get(state, 0) / total)
            draw.rectangle((cursor, y, cursor + width, y + 42), fill=colors[state])
            if counts.get(state, 0): draw.text((cursor + 10, y + 9), f"{state} {counts[state]}", font=font(16), fill="white")
            cursor += width
        draw.text((1110, y + 10), f"n={total}", font=font(16), fill=(70, 75, 82))
    draw.text((40, 575), "Pass = all six declared engineering dimensions pass; warn/fail preserve exact recorded candidate reviews.", font=font(16), fill=(75, 80, 87))
    return image


def draw_jump_profile(records: list[dict], jumps: list[dict]) -> Image.Image:
    image = Image.new("RGB", (1500, 650), (235, 237, 241)); draw = ImageDraw.Draw(image)
    draw.text((35, 24), "Selected-sequence adjacent appearance-feature jumps", font=font(28), fill=(18, 21, 26))
    draw.text((35, 63), "Euclidean distance over z-scored edge occupancy, luma entropy/stddev, colorfulness, and color entropy", font=font(16), fill=(75, 80, 87))
    x0, y0, plot_w, plot_h = 70, 520, 1360, 390
    max_jump = max(item["distance"] for item in jumps)
    step = plot_w / len(jumps)
    for index, item in enumerate(jumps):
        bar_h = round(plot_h * item["distance"] / max_jump)
        x = round(x0 + index * step)
        color = (181, 68, 78) if item["sequence_break"] else (70, 135, 195)
        draw.rectangle((x + 4, y0 - bar_h, x + round(step) - 5, y0), fill=color)
        draw.text((x + 4, y0 + 10), f"{item['from_candidate']}→", font=font(12), fill=(55, 60, 68))
        draw.text((x + 4, y0 + 28), item["to_candidate"], font=font(12), fill=(55, 60, 68))
        draw.text((x + 4, y0 - bar_h - 23), f"{item['distance']:.2f}", font=font(12), fill=(55, 60, 68))
    draw.line((x0, y0, x0 + plot_w, y0), fill=(80, 85, 92), width=2)
    draw.text((35, 600), "Red bars cross declared sequence breaks. High jumps are review cues, not failures or continuity identity measurements.", font=font(16), fill=(75, 80, 87))
    return image


def draw_scatter(records: list[dict]) -> Image.Image:
    image = Image.new("RGB", (1200, 820), (235, 237, 241)); draw = ImageDraw.Draw(image)
    draw.text((35, 24), "Phone-scale density × colorfulness", font=font(28), fill=(18, 21, 26))
    draw.text((35, 63), "Marker size follows current target width; labels are selected candidate IDs", font=font(16), fill=(75, 80, 87))
    x0, y0, w, h = 100, 720, 980, 590
    xs = [r["metrics"]["edge_occupancy_ge_32"] for r in records]; ys = [r["metrics"]["colorfulness"] for r in records]
    xmin, xmax = min(xs) * .9, max(xs) * 1.1; ymin, ymax = min(ys) * .85, max(ys) * 1.1
    for tick in range(6):
        x = x0 + round(w * tick / 5); y = y0 - round(h * tick / 5)
        draw.line((x, y0 - h, x, y0), fill=(210, 214, 220)); draw.line((x0, y, x0 + w, y), fill=(210, 214, 220))
    for r in records:
        xv, yv = r["metrics"]["edge_occupancy_ge_32"], r["metrics"]["colorfulness"]
        x = x0 + round((xv - xmin) / (xmax - xmin) * w); y = y0 - round((yv - ymin) / (ymax - ymin) * h)
        radius = 7 + round(r["target_width"] / 180)
        color = STYLE_COLORS[r["style_id"]]
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color, outline=(30, 34, 40), width=2)
        draw.text((x + radius + 3, y - 9), r["candidate_id"], font=font(13), fill=(35, 40, 47))
    draw.text((430, 775), "edge occupancy ≥32", font=font(18), fill=(45, 50, 57))
    draw.text((15, 350), "colorfulness", font=font(18), fill=(45, 50, 57))
    lx = 840
    for index, style in enumerate(STYLES):
        draw.rectangle((lx, 92 + index * 28, lx + 18, 110 + index * 28), fill=STYLE_COLORS[style]); draw.text((lx + 26, 91 + index * 28), style, font=font(14), fill=(45, 50, 57))
    return image


def artifact(path: Path, image: Image.Image) -> dict:
    image.save(path, optimize=False)
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "width": image.width, "height": image.height, "bytes": path.stat().st_size}


def main() -> int:
    if not FONT_PATH.is_file() or sha(FONT_PATH) != FONT_SHA:
        raise SystemExit("hash-pinned analysis font unavailable or changed")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    initial = json.loads(INITIAL.read_text(encoding="utf-8")); hardening = json.loads(HARDENING.read_text(encoding="utf-8"))
    assembly_review = json.loads(ASSEMBLY_REVIEW.read_text(encoding="utf-8"))
    all_candidates = initial["candidates"] + hardening["candidates"]
    candidate_map = {item["candidate_id"]: item for item in all_candidates}
    records, phones = [], {}
    for row in manifest["rows"]:
        path = ROOT / row["source_path"]
        if sha(path) != row["source_sha256"]: raise SystemExit(f"source mismatch: {row['candidate_id']}")
        measured, phone = metrics(path, row["layout"]["target_width"])
        phones[row["candidate_id"]] = phone
        records.append({"order": row["order"], "sequence_id": row["sequence_id"], "candidate_id": row["candidate_id"],
                        "panel_id": row["panel_id"], "style_id": row["style_id"], "cadence_role": row["cadence_role"],
                        "target_width": row["layout"]["target_width"], "metrics": measured})
    feature_names = ["edge_occupancy_ge_32", "luma_entropy_bits", "luma_stddev", "colorfulness", "quantized_color_entropy_bits"]
    matrix = np.array([[record["metrics"][name] for name in feature_names] for record in records], dtype=np.float64)
    z = (matrix - matrix.mean(axis=0)) / np.where(matrix.std(axis=0) == 0, 1, matrix.std(axis=0))
    jumps = []
    for index in range(len(records) - 1):
        jumps.append({"from_candidate": records[index]["candidate_id"], "to_candidate": records[index + 1]["candidate_id"],
                      "from_sequence": records[index]["sequence_id"], "to_sequence": records[index + 1]["sequence_id"],
                      "sequence_break": records[index]["sequence_id"] != records[index + 1]["sequence_id"],
                      "distance": round(float(np.linalg.norm(z[index + 1] - z[index])), 4)})
    style_results = {style: Counter() for style in STYLES}
    for candidate in all_candidates: style_results[candidate["style_id"]][engineering_state(candidate)] += 1
    style_results_json = {style: {state: style_results[style].get(state, 0) for state in ("pass", "warn", "fail")} for style in STYLES}
    selected_styles = Counter(record["style_id"] for record in records)
    OUT.mkdir(parents=True, exist_ok=True)
    artifacts = [
        artifact(OUT / "selected-phone-density-montage-r1.png", draw_montage(records, phones)),
        artifact(OUT / "style-engineering-results-r1.png", draw_style_results(style_results_json)),
        artifact(OUT / "sequence-appearance-jumps-r1.png", draw_jump_profile(records, jumps)),
        artifact(OUT / "density-colorfulness-scatter-r1.png", draw_scatter(records)),
    ]
    packet = {
        "record_type": "CH05ContinuityStyleDensityPacket", "schema_version": "1.0",
        "record_id": "ng-ch05-continuity-style-density-packet-r1", "state": "LOCAL_DIAGNOSTIC_OWNER_REVIEW_PENDING",
        "manifest": {"path": MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha(MANIFEST)},
        "assembly_review": {"path": ASSEMBLY_REVIEW.relative_to(ROOT).as_posix(), "sha256": sha(ASSEMBLY_REVIEW)},
        "font": {"path": str(FONT_PATH), "sha256": FONT_SHA}, "feature_names": feature_names,
        "selected_records": records, "adjacent_appearance_jumps": jumps,
        "max_adjacent_jump": max(jumps, key=lambda item: item["distance"]),
        "style_engineering_results_all_26": style_results_json, "selected_style_counts": dict(sorted(selected_styles.items())),
        "manual_continuity_review": assembly_review["continuity_review"],
        "artifacts": artifacts, "artifact_count": len(artifacts),
        "artifact_inventory_root_sha256": hashlib.sha256("".join(x["path"] + ":" + x["sha256"] + "\n" for x in artifacts).encode()).hexdigest(),
        "provider_calls": 0, "uploads": 0, "cost_usd": 0, "human_review_minutes": None, "accepted_candidates": 0,
        "boundary": "Global features are density/rhythm diagnostics only; manual review remains authoritative for identity, hair, wardrobe, anatomy, causality, lettering, and acceptance."
    }
    packet_path = OUT / "continuity-style-density-packet.json"
    with packet_path.open("w", encoding="utf-8", newline="\n") as handle: handle.write(json.dumps(packet, indent=2) + "\n")
    print(f"analyzed 14 selected / 26 style-triage candidates; max jump {packet['max_adjacent_jump']['from_candidate']}->{packet['max_adjacent_jump']['to_candidate']} {packet['max_adjacent_jump']['distance']}; 4 artifacts; packet {sha(packet_path)}")
    print("style results", json.dumps(style_results_json, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
