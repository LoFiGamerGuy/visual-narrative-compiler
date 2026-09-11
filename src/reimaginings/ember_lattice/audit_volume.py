from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageFilter, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[3]
PROD = ROOT / "production" / "reimaginings" / "ember-lattice"
VOLUME = PROD / "volume"
REVIEW = ROOT / "docs" / "reimaginings" / "ember-lattice" / "volume"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def wrap_count(text: str, max_chars: int) -> int:
    lines, current = 0, ""
    for word in text.split():
        trial = word if not current else f"{current} {word}"
        if len(trial) <= max_chars:
            current = trial
        else:
            lines += 1
            current = word
    return lines + bool(current)


def wrapped_lines(text: str, max_chars: int) -> list[str]:
    words, lines, current = text.split(), [], ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if len(trial) <= max_chars:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def iou(a: list[float], b: list[float]) -> float:
    left, top, right, bottom = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    if right <= left or bottom <= top:
        return 0.0
    intersection = (right - left) * (bottom - top)
    area_a, area_b = (a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1])
    return intersection / (area_a + area_b - intersection)


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []
    requests = read_json(VOLUME / "generation-requests.json")["requests"]
    registry = read_json(PROD / "reference-registry.json")["references"]
    master = read_json(VOLUME / "volume-master.json")
    density = read_json(VOLUME / "dialogue-and-density-metrics.json")
    state_validation = read_json(VOLUME / "system-state-validation.json")
    art_rows: list[dict[str, Any]] = []
    density_by_panel: dict[str, str] = {}
    for chapter in range(1, 11):
        plan = read_json(VOLUME / "chapters" / f"ch{chapter:02d}" / "comic-panel-plans.json")
        density_by_panel.update({panel["panel_id"]: panel["density"] for panel in plan["panels"]})

    if len(requests) != 225:
        errors.append(f"expected 224 base panel requests plus one localized retry, got {len(requests)}")
    for ref in registry:
        path = ROOT / ref["path"]
        if not path.exists():
            errors.append(f'missing reference {ref["reference_id"]}')
        elif sha_file(path) != ref["sha256"]:
            errors.append(f'reference hash mismatch {ref["reference_id"]}')

    seen_hashes: dict[str, str] = {}
    for request in requests:
        source = ROOT / request["output_path"]
        row = {"request_id": request["request_id"], "panel_id": request["panel_id"], "planned_density": density_by_panel[request["panel_id"]], "status": request["review_status"], "failure_classes": request["failure_classes"]}
        if not source.exists():
            errors.append(f'missing source {request["panel_id"]}')
            art_rows.append(row)
            continue
        digest = sha_file(source)
        if digest != request.get("sha256"):
            errors.append(f'source hash mismatch {request["panel_id"]}')
        if request["prompt_hash"] != sha_bytes(request["exact_prompt"].encode("utf-8")):
            errors.append(f'prompt hash mismatch {request["panel_id"]}')
        is_diagnostic = request["review_status"] == "HARD_FAIL_PRESERVED_DIAGNOSTIC"
        if request["review_status"] not in {"REVIEWED_PASS", "HARD_FAIL_PRESERVED_DIAGNOSTIC"}:
            errors.append(f'art not visually reviewed {request["panel_id"]}: {request["review_status"]}')
        if digest in seen_hashes:
            errors.append(f'duplicate source hash {request["panel_id"]} and {seen_hashes[digest]}')
        seen_hashes[digest] = request["panel_id"]
        with Image.open(source) as image:
            rgb = image.convert("RGB")
            width, height = rgb.size
            sample = ImageOps.grayscale(rgb.resize((128, max(128, round(128 * height / width))), Image.Resampling.LANCZOS))
            entropy = sample.entropy()
            luma_std = ImageStat.Stat(sample).stddev[0]
            phone_h = max(1, round(height * 390 / width))
            phone_gray = ImageOps.grayscale(rgb.resize((390, phone_h), Image.Resampling.LANCZOS))
            edge_hist = phone_gray.filter(ImageFilter.FIND_EDGES).histogram()
            edge_density = sum(edge_hist[42:]) / (390 * phone_h)
            high_hist = ImageChops.difference(phone_gray, phone_gray.filter(ImageFilter.GaussianBlur(1.2))).histogram()
            high_frequency = sum(high_hist[12:]) / (390 * phone_h)
        if not is_diagnostic and (width < 768 or height < 1200 or height <= width):
            errors.append(f'invalid tall source dimensions {request["panel_id"]}: {width}x{height}')
        if entropy < 3.5 or luma_std < 12:
            errors.append(f'low-information source {request["panel_id"]}: entropy={entropy:.2f}, std={luma_std:.2f}')
        row.update({"sha256": digest, "width": width, "height": height, "phone_width": 390, "phone_height": phone_h, "edge_density": round(edge_density, 6), "high_frequency_occupancy": round(high_frequency, 6), "entropy": round(entropy, 3), "luma_std": round(luma_std, 3)})
        art_rows.append(row)

    selected_art_rows = [row for row in art_rows if row.get("status") == "REVIEWED_PASS"]
    diagnostic_art_rows = [row for row in art_rows if row.get("status") == "HARD_FAIL_PRESERVED_DIAGNOSTIC"]
    if len(selected_art_rows) != 224 or len(diagnostic_art_rows) != 1:
        errors.append(f"selection/retry reconciliation mismatch: selected={len(selected_art_rows)}, diagnostics={len(diagnostic_art_rows)}")
    low_rows = [row for row in selected_art_rows if row.get("planned_density") == "low"]
    low_warnings = [row for row in low_rows if "planned_low_rendered_above_accepted_calibration" in row.get("failure_classes", [])]
    if len(low_warnings) / max(1, len(low_rows)) > .25:
        errors.append(f"planned-low fail-closed threshold exceeded: {len(low_warnings)}/{len(low_rows)}")
    elif low_warnings:
        warnings.append(f"planned-low visual warnings remain within threshold: {len(low_warnings)}/{len(low_rows)}")

    panel_count = action_count = 0
    density_counts = {"low": 0, "moderate": 0, "high": 0}
    fit_checks = overlap_checks = 0
    for chapter in range(1, 11):
        chapter_id = f"ch{chapter:02d}"
        chapter_dir = VOLUME / "chapters" / chapter_id
        plans = read_json(chapter_dir / "comic-panel-plans.json")
        units_by_panel = read_json(chapter_dir / "lettering-copy.json")["panel_units"]
        if len(plans["panels"]) != 24:
            errors.append(f"{chapter_id} does not have 24 panels")
        for panel in plans["panels"]:
            panel_count += 1
            action_count += int(panel["action"])
            density_counts[panel["density"]] += 1
            source = ROOT / panel["source_path"]
            if not source.exists():
                continue
            with Image.open(source) as image:
                width, height = image.size
            boxes: list[tuple[str, list[float]]] = []
            for unit in units_by_panel.get(panel["panel_id"], []):
                if "box" not in unit:
                    continue
                box = unit["box"]
                effective_box = list(box)
                fit_checks += 1
                bw, bh = (box[2] - box[0]) * width, (box[3] - box[1]) * height
                if unit.get("lines"):
                    font = width * 13 / 390
                    max_chars = max(11, int((bw - 44) / (font * .54)))
                    line_count = sum(len(wrapped_lines(line, max_chars)) for line in unit["lines"])
                    needed = line_count * font * 1.12 + 38
                elif unit["kind"] == "caption":
                    font = width * 14 / 390
                    needed = wrap_count(unit.get("text", ""), max(12, int((bw - 40) / (font * .57)))) * font * 1.08 + 24
                else:
                    font = width * 14 / 390
                    needed = wrap_count(unit.get("text", ""), max(12, int((bw - 48) / (font * .57)))) * font * 1.08 + 34
                if needed > bh:
                    if box[1] < .5:
                        effective_box[3] = min(.49 if unit.get("lines") else .48, box[1] + needed / height)
                    else:
                        effective_box[1] = max(.51 if unit.get("lines") else .52, box[3] - needed / height)
                available = (effective_box[3] - effective_box[1]) * height
                if needed > available * 1.02:
                    errors.append(f'lettering fit failure {unit["unit_id"]}: need {needed:.1f}px in {available:.1f}px')
                phone_type = font * 390 / width
                minimum = 13 if unit.get("lines") else 14
                if phone_type + .01 < minimum:
                    errors.append(f'phone type too small {unit["unit_id"]}: {phone_type:.2f}px')
                boxes.append((unit["unit_id"], effective_box))
            for index, (id_a, box_a) in enumerate(boxes):
                for id_b, box_b in boxes[index + 1:]:
                    overlap_checks += 1
                    value = iou(box_a, box_b)
                    if value > .08:
                        errors.append(f'lettering overlap {id_a} / {id_b}: IoU {value:.3f}')

    if panel_count != 240:
        errors.append(f"expected 240 planned panels, got {panel_count}")
    if action_count != 108:
        errors.append(f"expected 108 action panels, got {action_count}")
    if density_counts != {"low": 159, "moderate": 60, "high": 21}:
        errors.append(f"density mismatch: {density_counts}")
    system_moments = sum(row["meaningful_system_moments"] for row in density["chapters"])
    dialogue_words = sum(row["spoken_internal_words"] for row in density["chapters"])
    if system_moments < 40:
        errors.append("insufficient system moment count")
    if state_validation["status"] != "PASS":
        errors.append("system state validation did not pass")

    href_checks = 0
    if not (REVIEW / "index.html").exists():
        errors.append("missing volume review hub")
    for html_path in REVIEW.rglob("*.html") if REVIEW.exists() else []:
        source = html_path.read_text(encoding="utf-8")
        for href in re.findall(r'(?:href|src)="([^"#]+)"', source):
            if href.startswith(("http:", "https:", "mailto:")):
                continue
            href_checks += 1
            target = (html_path.parent / href).resolve()
            if not target.exists():
                warnings.append(f'local review link unresolved from {html_path.relative_to(ROOT)}: {href}')
    build = VOLUME / "volume-build-report.json"
    if not build.exists() or read_json(build).get("panels") != 240:
        errors.append("volume build report missing or incomplete")

    report = {
        "schema": "VolumeValidation/1.0",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "review_totals": {
            "PASS": len(selected_art_rows),
            "WARN": len(warnings),
            "FAIL": len(errors),
            "RESOLVED_DIAGNOSTICS": len(diagnostic_art_rows),
            "failure_classes": sorted({failure for row in art_rows for failure in row.get("failure_classes", [])}),
        },
        "counts": {
            "chapters": len(master["chapters"]), "panels": panel_count, "new_generated_sources": len(art_rows),
            "approved_pilot_sources_reused": 16, "action_panels": action_count, "density": density_counts,
            "dialogue_words": dialogue_words, "system_moments": system_moments,
            "lettering_fit_checks": fit_checks, "lettering_overlap_pair_checks": overlap_checks, "local_review_link_checks": href_checks,
        },
        "direct_paid_cloud_spend_usd": 0,
        "system_state_validation": state_validation["status"],
    }
    write = lambda path, value: path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    write(VOLUME / "art-source-review.json", {"schema": "ArtSourceReview/1.0", "status": "PASS" if not any("source" in e or "art" in e for e in errors) else "FAIL", "panels": art_rows})
    write(VOLUME / "volume-validation.json", report)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
