"""Build a deterministic visual PASS/WARN sheet for the complete CH05 draft."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r2.json"
TRIAGE = ROOT / "docs/research/evidence/ch05-complete-chapter-agent-triage-r2.json"
OUTPUT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r2/review/ch05-complete-chapter-triage-sheet.png"
REPORT = OUTPUT.parent / "triage-sheet-report.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    for name in (["DejaVuSans-Bold.ttf", "Arial Bold.ttf"] if bold else ["DejaVuSans.ttf", "Arial.ttf"]):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def wrap(draw: ImageDraw.ImageDraw, text: str, selected: ImageFont.ImageFont, width: int, max_lines: int = 2) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=selected)[2] <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
            if len(lines) == max_lines:
                break
    if current and len(lines) < max_lines:
        lines.append(current)
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", choices=("r2", "r3", "r4"), default="r2")
    args = parser.parse_args()
    revision = args.revision
    assembly_path = ROOT / f"production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-{revision}.json"
    triage_path = ROOT / f"docs/research/evidence/ch05-complete-chapter-agent-triage-{revision}.json"
    output_path = ROOT / f"experiments/review-packets/ch05-complete-chapter-draft-{revision}/review/ch05-complete-chapter-triage-sheet.png"
    report_path = output_path.parent / "triage-sheet-report.json"
    assembly = json.loads(assembly_path.read_text(encoding="utf-8"))
    triage = json.loads(triage_path.read_text(encoding="utf-8"))
    status = {row["panel_id"]: row for row in triage["rows"]}
    entries = assembly["entries"]
    if len(entries) != 50 or set(status) != {row["panel_id"] for row in entries}:
        raise ValueError("triage and assembly must bind the same 50 panels")
    columns, rows = 5, math.ceil(len(entries) / 5)
    tile_w, tile_h, gap, margin, header = 300, 254, 14, 24, 100
    canvas = Image.new("RGB", (margin * 2 + columns * tile_w + 4 * gap, header + margin + rows * tile_h + (rows - 1) * gap), "#e7e3da")
    draw = ImageDraw.Draw(canvas)
    summary = triage["summary"]
    draw.text((margin, 16), f"CH05 COMPLETE DRAFT {revision} - AGENT TRIAGE", fill="#20252a", font=font(28, True))
    draw.text((margin, 54), f"{summary['pass']} PASS | {summary['warn']} WARN | {summary['fail']} FAIL | human review pending", fill="#3b454d", font=font(18))
    records = []
    for index, entry in enumerate(entries):
        row = status[entry["panel_id"]]
        source = ROOT / entry["source"]["path"]
        if sha256(source) != entry["source"]["sha256"]:
            raise ValueError(f"source hash mismatch: {entry['panel_id']}")
        with Image.open(source) as opened:
            image = opened.convert("RGB")
        col, grid_row = index % columns, index // columns
        x = margin + col * (tile_w + gap)
        y = header + grid_row * (tile_h + gap)
        color = "#2d8a57" if row["status"] == "PASS" else "#c47a16"
        draw.rectangle((x, y, x + tile_w, y + tile_h), fill="#faf8f2", outline=color, width=4)
        label = f"{entry['order']:02d}  {entry['panel_id'].split('-')[-1].upper()}  {row['status']}"
        draw.text((x + 10, y + 8), label, fill=color, font=font(16, True))
        framed = ImageOps.contain(image, (tile_w - 18, 165), Image.Resampling.LANCZOS)
        px = x + (tile_w - framed.width) // 2
        py = y + 38 + (165 - framed.height) // 2
        canvas.paste(framed, (px, py))
        note = row["primary_issue_class"] or "no blocking issue"
        for line_no, line in enumerate(wrap(draw, note.replace("_", " "), font(13), tile_w - 20)):
            draw.text((x + 10, y + 212 + line_no * 16), line, fill="#343b41", font=font(13))
        records.append({"panel_id": entry["panel_id"], "status": row["status"], "source_sha256": entry["source"]["sha256"]})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", compress_level=6, optimize=False)
    report = {
        "record_type": "CH05CompleteChapterTriageSheetReport",
        "schema_version": "1.0",
        "state": "NON_GATING_AGENT_REVIEW_AID",
        "inputs": [
            {"path": assembly_path.relative_to(ROOT).as_posix(), "sha256": sha256(assembly_path)},
            {"path": triage_path.relative_to(ROOT).as_posix(), "sha256": sha256(triage_path)},
        ],
        "artifact": {"path": output_path.relative_to(ROOT).as_posix(), "sha256": sha256(output_path), "width": canvas.width, "height": canvas.height, "bytes": output_path.stat().st_size},
        "summary": triage["summary"],
        "panels": records,
        "boundary": "Visual index only; PASS/WARN is agent triage and grants no acceptance or commercial status.",
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report["artifact"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
