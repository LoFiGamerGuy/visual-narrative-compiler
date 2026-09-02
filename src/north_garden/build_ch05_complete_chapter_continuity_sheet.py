"""Build a deterministic cast-continuity sheet for the complete CH05 draft."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
DEFAULT_ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r1.json"
DEFAULT_OUTPUT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r1/review/ch05-complete-chapter-continuity-sheet.png"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def build(assembly_path: Path, output_path: Path) -> int:
    plans = json.loads(PLAN.read_text(encoding="utf-8"))["plans"]
    plan_by_id = {row["panel_id"]: row for row in plans}
    manifest = json.loads(assembly_path.read_text(encoding="utf-8"))
    selected = [row for row in manifest["entries"] if plan_by_id[row["panel_id"]].get("visible_adult_cast")]
    columns, tile_w, tile_h, gap, margin, header = 4, 340, 300, 16, 24, 112
    rows = math.ceil(len(selected) / columns)
    canvas = Image.new("RGB", (margin * 2 + columns * tile_w + (columns - 1) * gap, header + margin + rows * tile_h + (rows - 1) * gap), "#e8e4da")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 18), "CH05 COMPLETE DRAFT - CAST CONTINUITY", fill="#22272c", font=font(30, True))
    draw.text((margin, 58), "Soren: light-brown/dark-blond + oatmeal coat | Sigrid: dark tied hair + plaid wrap", fill="#3c454d", font=font(18))
    records = []
    for index, entry in enumerate(selected):
        source = ROOT / entry["source"]["path"]
        if sha256(source) != entry["source"]["sha256"]:
            raise ValueError(f"source hash mismatch: {source}")
        with Image.open(source) as opened:
            image = opened.convert("RGB")
        col, row = index % columns, index // columns
        x = margin + col * (tile_w + gap)
        y = header + row * (tile_h + gap)
        draw.rectangle((x, y, x + tile_w, y + tile_h), fill="#f7f5ef", outline="#65717a", width=2)
        cast = "+".join(plan_by_id[entry["panel_id"]]["visible_adult_cast"])
        label = f"{entry['order']:02d} {entry['panel_id'].split('-')[-1].upper()}  {cast}"
        draw.text((x + 10, y + 8), label, fill="#20252a", font=font(16, True))
        framed = ImageOps.contain(image, (tile_w - 20, tile_h - 54), Image.Resampling.LANCZOS)
        px = x + (tile_w - framed.width) // 2
        py = y + 42 + (tile_h - 48 - framed.height) // 2
        canvas.paste(framed, (px, py))
        records.append({"panel_id": entry["panel_id"], "cast": plan_by_id[entry["panel_id"]]["visible_adult_cast"], "source_sha256": entry["source"]["sha256"]})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", compress_level=6, optimize=False)
    report_path = output_path.parent / "continuity-sheet-report.json"
    result = {
        "record_type": "CH05CompleteChapterContinuitySheetReport",
        "schema_version": "1.0",
        "state": "AGENT_REVIEW_AID_UNACCEPTED",
        "medium": "comic",
        "animation_shot_plan": None,
        "e_conte": None,
        "summary": {"chapter_panels": len(plans), "cast_panels": len(selected), "soren_contract": "light-brown to dark-blond hair; pale oatmeal work coat", "sigrid_contract": "dark-brown to near-black tied hair; practical plaid wrap"},
        "inputs": {"assembly_manifest": {"path": assembly_path.relative_to(ROOT).as_posix(), "sha256": sha256(assembly_path)}},
        "artifact": {"path": output_path.relative_to(ROOT).as_posix(), "sha256": sha256(output_path), "width": canvas.width, "height": canvas.height, "bytes": output_path.stat().st_size},
        "panels": records,
        "boundary": "Agent continuity review aid only; image statistics and layout do not establish identity acceptance or commercial clearance."
    }
    report_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], sort_keys=True))
    print(json.dumps(result["artifact"], sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assembly", type=Path, default=DEFAULT_ASSEMBLY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    assembly_path = args.assembly if args.assembly.is_absolute() else ROOT / args.assembly
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    return build(assembly_path.resolve(), output_path.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
