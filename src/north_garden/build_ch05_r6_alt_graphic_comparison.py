"""Build deterministic, evidence-backed r6 versus alternate-graphic CH05 review packets."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r6.json"
ALT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-alt-graphic-assembly-r1.json"
ALT_TRIAGE = ROOT / "docs/research/evidence/ch05-complete-chapter-alt-graphic-agent-triage-r1.json"
R6_TRIAGE = ROOT / "docs/research/evidence/ch05-complete-chapter-agent-triage-r6.json"
BASE_PHONE = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r6/lettered/ch05-complete-chapter-lettered-phone-390px-r1.png"
ALT_PHONE = ROOT / "experiments/review-packets/ch05-complete-chapter-alt-graphic-r1/lettered/ch05-complete-chapter-alt-graphic-lettered-r1-phone-390px.png"
OUTDIR = ROOT / "experiments/review-packets/ch05-r6-vs-alt-graphic-comparison-r1"
EVIDENCE = ROOT / "docs/research/evidence/ch05-r6-vs-alt-graphic-comparison-r1.json"
ANCHORS = [1, 3, 17, 19, 29, 32, 36, 39, 41, 43, 44, 48, 50]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def artifact(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        width, height = image.size
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "width": width, "height": height, "bytes": path.stat().st_size, "repository_state": "IGNORED_LOCAL_REVIEW_ARTIFACT"}


def load_panel(entry: dict[str, Any]) -> Image.Image:
    path = ROOT / entry["source"]["path"]
    if sha256(path) != entry["source"]["sha256"]:
        raise ValueError(f"source hash mismatch: {entry['panel_id']}")
    with Image.open(path) as opened:
        return opened.convert("RGB")


def metric(image: Image.Image, source_bytes: int) -> dict[str, float]:
    width = 390
    height = max(1, round(image.height * width / image.width))
    normalized = image.resize((width, height), Image.Resampling.LANCZOS).convert("L")
    histogram = normalized.histogram()
    total = sum(histogram)
    entropy = -sum((count / total) * math.log2(count / total) for count in histogram if count)
    edges = normalized.filter(ImageFilter.FIND_EDGES)
    cropped = edges.crop((1, 1, max(2, edges.width - 1), max(2, edges.height - 1)))
    edge_density = sum(value >= 32 for value in cropped.tobytes()) / (cropped.width * cropped.height)
    return {"grayscale_entropy_bits": round(entropy, 6), "edge_density_ge_32": round(edge_density, 6), "png_bytes_per_native_pixel": round(source_bytes / (image.width * image.height), 6)}


def mean(rows: list[dict[str, float]], key: str) -> float:
    return round(sum(row[key] for row in rows) / len(rows), 6)


def build_full_pairs(base_entries: list[dict[str, Any]], alt_entries: list[dict[str, Any]], status: dict[str, str], path: Path) -> None:
    columns, tile_w, tile_h, gap, margin, header = 5, 330, 235, 12, 20, 88
    rows = math.ceil(len(base_entries) / columns)
    canvas = Image.new("RGB", (margin * 2 + columns * tile_w + (columns - 1) * gap, header + margin + rows * tile_h + (rows - 1) * gap), "#e8e4da")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 14), "CH05 R6 vs ALT GRAPHIC R1 - ALL 50 PANELS", fill="#20252a", font=font(28, True))
    draw.text((margin, 50), "Left: r6 baseline | Right: alternate | status labels apply to alternate non-gating triage", fill="#3d464e", font=font(16))
    for index, (base, alt) in enumerate(zip(base_entries, alt_entries, strict=True)):
        x = margin + (index % columns) * (tile_w + gap)
        y = header + (index // columns) * (tile_h + gap)
        label_status = status[alt["panel_id"]]
        color = "#2d8a57" if label_status == "PASS" else "#c47a16" if label_status == "WARN" else "#b83b3b"
        draw.rectangle((x, y, x + tile_w, y + tile_h), fill="#faf8f2", outline=color, width=3)
        draw.text((x + 8, y + 6), f"P{index + 1:03d}  ALT {label_status}", fill=color, font=font(14, True))
        for side, entry in enumerate((base, alt)):
            image = ImageOps.contain(load_panel(entry), (150, 165), Image.Resampling.LANCZOS)
            px = x + 8 + side * 164 + (150 - image.width) // 2
            py = y + 34 + (165 - image.height) // 2
            canvas.paste(image, (px, py))
            draw.text((x + 55 + side * 164, y + 207), "R6" if side == 0 else "ALT", fill="#303940", font=font(13, True))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", compress_level=6, optimize=False)


def build_anchors(base_entries: list[dict[str, Any]], alt_entries: list[dict[str, Any]], status_rows: dict[str, dict[str, Any]], path: Path) -> None:
    columns, tile_w, tile_h, gap, margin, header = 2, 800, 410, 18, 24, 96
    rows = math.ceil(len(ANCHORS) / columns)
    canvas = Image.new("RGB", (margin * 2 + columns * tile_w + gap, header + margin + rows * tile_h + (rows - 1) * gap), "#e8e4da")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 14), "CH05 CAUSAL / CONTINUITY ANCHORS", fill="#20252a", font=font(30, True))
    draw.text((margin, 54), "R6 left, alternate right; selection considers story causality before appearance", fill="#3d464e", font=font(17))
    for index, order in enumerate(ANCHORS):
        base, alt = base_entries[order - 1], alt_entries[order - 1]
        review = status_rows[alt["panel_id"]]
        x = margin + (index % columns) * (tile_w + gap)
        y = header + (index // columns) * (tile_h + gap)
        color = "#2d8a57" if review["status"] == "PASS" else "#c47a16" if review["status"] == "WARN" else "#b83b3b"
        draw.rectangle((x, y, x + tile_w, y + tile_h), fill="#faf8f2", outline=color, width=4)
        draw.text((x + 10, y + 8), f"P{order:03d}  ALT {review['status']}  {review['primary_issue_class'] or 'no blocking issue'}", fill=color, font=font(16, True))
        for side, entry in enumerate((base, alt)):
            image = ImageOps.contain(load_panel(entry), (370, 300), Image.Resampling.LANCZOS)
            px = x + 15 + side * 400 + (370 - image.width) // 2
            py = y + 44 + (300 - image.height) // 2
            canvas.paste(image, (px, py))
            draw.text((x + 170 + side * 400, y + 352), "R6" if side == 0 else "ALT", fill="#303940", font=font(15, True))
        note = review["note"]
        if len(note) > 100:
            note = note[:97] + "..."
        draw.text((x + 10, y + 380), note, fill="#303940", font=font(12))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", compress_level=6, optimize=False)


def build_phone(path: Path) -> None:
    with Image.open(BASE_PHONE) as image:
        base = image.convert("RGB")
    with Image.open(ALT_PHONE) as image:
        alt = image.convert("RGB")
    margin, gap, header = 20, 20, 72
    canvas = Image.new("RGB", (margin * 2 + base.width + alt.width + gap, header + max(base.height, alt.height) + margin), "#11151a")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 14), "R6 LETTERED PHONE", fill="#f4f1e8", font=font(20, True))
    draw.text((margin + base.width + gap, 14), "ALT GRAPHIC LETTERED PHONE", fill="#f4f1e8", font=font(20, True))
    canvas.paste(base, (margin, header))
    canvas.paste(alt, (margin + base.width + gap, header))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", compress_level=6, optimize=False)


def main() -> int:
    base_doc = json.loads(BASE.read_text(encoding="utf-8"))
    alt_doc = json.loads(ALT.read_text(encoding="utf-8"))
    triage = json.loads(ALT_TRIAGE.read_text(encoding="utf-8"))
    base_entries, alt_entries = base_doc["entries"], alt_doc["entries"]
    if [row["panel_id"] for row in base_entries] != [row["panel_id"] for row in alt_entries] or len(base_entries) != 50:
        raise ValueError("comparison assemblies must share all 50 canonical panels")
    status_rows = {row["panel_id"]: row for row in triage["rows"]}
    base_metrics, alt_metrics, per_panel = [], [], []
    for base, alt in zip(base_entries, alt_entries, strict=True):
        base_path, alt_path = ROOT / base["source"]["path"], ROOT / alt["source"]["path"]
        base_image, alt_image = load_panel(base), load_panel(alt)
        b_metric, a_metric = metric(base_image, base_path.stat().st_size), metric(alt_image, alt_path.stat().st_size)
        base_metrics.append(b_metric); alt_metrics.append(a_metric)
        per_panel.append({"panel_id": base["panel_id"], "r6": b_metric, "alt_graphic": a_metric})
    all_pairs = OUTDIR / "ch05-r6-vs-alt-graphic-all-50-contact-sheet.png"
    anchors = OUTDIR / "ch05-r6-vs-alt-graphic-causal-continuity-anchors.png"
    phone = OUTDIR / "ch05-r6-vs-alt-graphic-lettered-phone-comparison.png"
    build_full_pairs(base_entries, alt_entries, {key: row["status"] for key, row in status_rows.items()}, all_pairs)
    build_anchors(base_entries, alt_entries, status_rows, anchors)
    build_phone(phone)
    metric_names = ("grayscale_entropy_bits", "edge_density_ge_32", "png_bytes_per_native_pixel")
    aggregate = {"r6": {key: mean(base_metrics, key) for key in metric_names}, "alt_graphic": {key: mean(alt_metrics, key) for key in metric_names}}
    aggregate["alt_minus_r6"] = {key: round(aggregate["alt_graphic"][key] - aggregate["r6"][key], 6) for key in metric_names}
    document = {
        "record_type": "CH05CompleteChapterRouteComparison",
        "schema_version": "1.0",
        "record_id": "ng-ch05-r6-vs-alt-graphic-comparison-r1",
        "state": "MEASURED_ENGINEERING_RECOMMENDATION_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in (BASE, ALT, R6_TRIAGE, ALT_TRIAGE, BASE_PHONE, ALT_PHONE)],
        "coverage": {"r6_panels": 50, "alt_graphic_panels": 50, "paired_panel_ids": 50},
        "visual_complexity_method": {"normalization": "Each crop resized to 390 px wide with aspect preserved; every panel weighted equally.", "grayscale_entropy_bits": "Shannon entropy of the normalized 8-bit grayscale histogram.", "edge_density_ge_32": "Fraction of non-border pixels whose Pillow FIND_EDGES grayscale value is >=32.", "png_bytes_per_native_pixel": "Source PNG byte size divided by native width*height; compression-sensitive supporting cue only."},
        "visual_complexity": {"aggregate_equal_panel_weight": aggregate, "per_panel": per_panel, "interpretation": "Only small aggregate differences are evidence that the alternate arm did not materially separate density. These proxies do not measure artistic quality."},
        "semantic_review": {
            "r6_frozen_panel_local_triage": {"pass": 49, "warn": 1, "fail": 0, "note": "Preserved unchanged; it predates the new cross-panel gates."},
            "r6_supplemental_cross_panel_gate_audit": {"pass": 47, "warn": 1, "fail": 2, "fail_panel_ids": ["ng-ch05-sc01-p001", "ng-ch05-sc01-p041"], "warn_panel_ids": ["ng-ch05-sc01-p032"], "note": "P001 prematurely shows chimney smoke/lit window; P041 retains visible hot material/plume; this supplements rather than rewrites frozen r6 evidence."},
            "alt_graphic_triage": triage["summary"],
        },
        "selection": {"recommended_route": "ch05_complete_chapter_r6_plus_cross_panel_semantic_gates", "not_selected": "alt_graphic_wholesale", "reason": "r6 remains materially stronger on causal action, role separation, footprint logic, leverage, mark continuity, and map possession. The alternate route preserves hair/wardrobe and offers strong individual panels, but does not achieve a meaningful density reduction and introduces seven failures.", "appearance_only_selection": False},
        "strong_alt_evidence_panel_ids": [f"ng-ch05-sc01-p{number:03d}" for number in (2, 4, 6, 10, 17, 19, 20, 23, 28, 33, 37, 38, 40, 42, 44, 47, 48, 49, 50)],
        "artifacts": {"all_50_pairs": artifact(all_pairs), "causal_continuity_anchors": artifact(anchors), "lettered_phone_comparison": artifact(phone)},
        "spend": {"direct_paid_api_cloud_usd": 0.0, "built_in_product_monetary_cost_usd": None},
        "limitations": ["Agent visual review is non-gating.", "Complexity proxies do not measure style quality, identity, narrative value, or commercial suitability.", "Built-in model, endpoint, request ID, usage, cost, and seed are unavailable.", "No route is accepted, commercially cleared, or selected as an exact production base."],
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": EVIDENCE.relative_to(ROOT).as_posix(), "sha256": sha256(EVIDENCE), "visual_complexity": aggregate, "artifacts": document["artifacts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
