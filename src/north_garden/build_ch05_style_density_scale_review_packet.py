"""Build deterministic local review sheets for the CH05 style/density/scale probes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-style-density-scale-exploration-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
OUT = ROOT / "experiments/review-packets/ch05-style-density-scale-exploration-r1"
SHEET = OUT / "contact-sheet-r1.png"
OVERLAY = OUT / "lettering-clearance-overlay-r1.png"
PACKET = OUT / "review-packet.json"
CANVAS = (2400, 1900)
CELL = (1160, 850)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def candidate_image(candidate: dict, safe_zone: list[float] | None) -> Image.Image:
    source = Image.open(ROOT / candidate["path"]).convert("RGB")
    if safe_zone:
        overlay = Image.new("RGBA", source.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        x, y, w, h = safe_zone
        rect = (round(x * source.width), round(y * source.height), round((x + w) * source.width), round((y + h) * source.height))
        draw.rectangle(rect, fill=(20, 190, 235, 72), outline=(0, 105, 145, 255), width=max(4, source.width // 250))
        source = Image.alpha_composite(source.convert("RGBA"), overlay).convert("RGB")
    return source


def build_sheet(evidence: dict, plans: dict, *, overlay: bool) -> Image.Image:
    canvas = Image.new("RGB", CANVAS, "#e8e5de")
    draw = ImageDraw.Draw(canvas)
    title = "CH05 STYLE / DENSITY / PANEL-SCALE - LETTERING OVERLAY" if overlay else "CH05 STYLE / DENSITY / PANEL-SCALE - BLIND-FREE DEVELOPMENT REVIEW"
    draw.text((50, 28), title, fill="#17191c", font=font(34))
    draw.text((50, 73), "Unaccepted research candidates. Cyan = ComicPanelPlan top-right safe zone." if overlay else "Compare causal read, density, action, format, face/hand integrity, and quiet lettering space.", fill="#3b4148", font=font(22))
    plan_by_id = {item["panel_id"]: item for item in plans["plans"]}
    origins = [(35, 130), (1205, 130), (35, 1010), (1205, 1010)]
    for candidate, origin in zip(evidence["candidates"], origins, strict=True):
        plan = plan_by_id[candidate["panel_id"]]
        safe_zone = plan["comic_direction"]["lettering"]["safe_zones"][0]["rect_norm"] if overlay else None
        image = candidate_image(candidate, safe_zone)
        framed = ImageOps.contain(image, (CELL[0] - 30, CELL[1] - 100), Image.Resampling.LANCZOS)
        x = origin[0] + (CELL[0] - framed.width) // 2
        y = origin[1] + 68 + (CELL[1] - 100 - framed.height) // 2
        draw.rectangle((origin[0], origin[1], origin[0] + CELL[0], origin[1] + CELL[1]), fill="#f8f6f0", outline="#636a70", width=3)
        canvas.paste(framed, (x, y))
        label = f"{candidate['candidate_id']}  |  {candidate['width']}x{candidate['height']}  |  {candidate['format_role']}"
        draw.text((origin[0] + 18, origin[1] + 15), label, fill="#15171a", font=font(20))
        draw.text((origin[0] + 18, origin[1] + 42), candidate["style"], fill="#3b4148", font=font(17))
    return canvas


def main() -> int:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    build_sheet(evidence, plans, overlay=False).save(SHEET, optimize=False)
    build_sheet(evidence, plans, overlay=True).save(OVERLAY, optimize=False)
    packet = {
        "record_type": "CH05StyleDensityScaleReviewPacket",
        "schema_version": "1.0",
        "record_id": "ng-ch05-style-density-scale-review-packet-r1",
        "state": "READY_FOR_HUMAN_COMPARISON_UNACCEPTED",
        "source_evidence": EVIDENCE.relative_to(ROOT).as_posix(),
        "source_evidence_sha256": sha256(EVIDENCE),
        "contact_sheet": {"path": SHEET.relative_to(ROOT).as_posix(), "sha256": sha256(SHEET)},
        "lettering_overlay": {"path": OVERLAY.relative_to(ROOT).as_posix(), "sha256": sha256(OVERLAY)},
        "candidate_ids": [item["candidate_id"] for item in evidence["candidates"]],
        "review_dimensions": evidence["comparison_dimensions"],
        "boundary": "Review aid only. No exact base, upload authority, RenderRecord, commercial clearance, or production acceptance is created.",
    }
    PACKET.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"built 4-candidate packet: {SHEET.relative_to(ROOT)} {sha256(SHEET)}")
    print(f"lettering overlay: {OVERLAY.relative_to(ROOT)} {sha256(OVERLAY)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
