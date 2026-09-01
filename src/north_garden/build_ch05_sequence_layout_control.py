"""Build deterministic non-art layout controls for CH05 P033-P038."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
SLICE = ROOT / "production/comic/demonstration-slices/ch05-p033-p038-r1.json"
PACKET = ROOT / "production/comic/demonstration-packets/ch05-p033-p038-no-network-r1.json"
OUT_DIR = ROOT / "experiments/outputs/ch05_p033_p038_sequence_layout_control_r1"
RESULT = ROOT / "experiments/results/ch05-p033-p038-sequence-layout-control-r1.json"
SIZE = (1536, 1024)

COLORS = {
    "background": "#34383b",
    "floor": "#23282b",
    "structure": "#66513d",
    "soren": "#c7761e",
    "sigrid": "#278b91",
    "bell": "#c9a33a",
    "tin": "#d5c6a3",
    "map": "#d8c893",
    "matches": "#bb5b35",
    "note": "#e5e1d3",
    "ink": "#111111",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rect_px(rect: list[float]) -> tuple[int, int, int, int]:
    x, y, width, height = rect
    return (
        round(x * SIZE[0]), round(y * SIZE[1]),
        round((x + width) * SIZE[0]), round((y + height) * SIZE[1]),
    )


def draw_rect(draw: ImageDraw.ImageDraw, mask: ImageDraw.ImageDraw, xy, **kwargs) -> None:
    draw.rectangle(xy, **kwargs)
    mask.rectangle(xy, fill=255)


def draw_ellipse(draw: ImageDraw.ImageDraw, mask: ImageDraw.ImageDraw, xy, **kwargs) -> None:
    draw.ellipse(xy, **kwargs)
    mask.ellipse(xy, fill=255)


def draw_line(draw: ImageDraw.ImageDraw, mask: ImageDraw.ImageDraw, xy, **kwargs) -> None:
    draw.line(xy, **kwargs)
    mask.line(xy, fill=255, width=kwargs.get("width", 1))


def role(draw, mask, name: str, xy: tuple[int, int, int, int]) -> None:
    color = COLORS["soren" if name == "SOREN" else "sigrid"]
    draw_rect(draw, mask, xy, fill=color, outline=COLORS["ink"], width=7)
    draw.text((xy[0] + 18, (xy[1] + xy[3]) // 2), f"{name}\nROLE", fill="white", spacing=8)


def shared_stage(draw, mask) -> None:
    draw_rect(draw, mask, (0, 730, SIZE[0], SIZE[1]), fill=COLORS["floor"])
    draw_rect(draw, mask, (100, 245, 1435, 295), fill=COLORS["structure"], outline=COLORS["ink"], width=5)
    draw_rect(draw, mask, (110, 295, 165, 930), fill=COLORS["structure"], outline=COLORS["ink"], width=5)
    draw_rect(draw, mask, (1370, 295, 1425, 930), fill=COLORS["structure"], outline=COLORS["ink"], width=5)


def panel_geometry(order: int, draw, mask) -> list[str]:
    objects = []
    if order == 33:
        shared_stage(draw, mask)
        role(draw, mask, "SIGRID", (300, 520, 500, 900))
        role(draw, mask, "SOREN", (830, 365, 985, 710))
        draw_ellipse(draw, mask, (1230, 300, 1325, 395), fill=COLORS["bell"], outline=COLORS["ink"], width=6)
        draw_line(draw, mask, (1278, 395, 1278, 610), fill=COLORS["bell"], width=12)
        objects = ["bell"]
    elif order == 34:
        shared_stage(draw, mask)
        draw_rect(draw, mask, (600, 315, 930, 730), fill="#171b1d", outline="#8e765b", width=12)
        role(draw, mask, "SIGRID", (260, 520, 450, 900))
        role(draw, mask, "SOREN", (1010, 455, 1190, 840))
        draw_ellipse(draw, mask, (510, 360, 575, 425), fill=COLORS["bell"], outline=COLORS["ink"], width=5)
        objects = ["doorway", "bell"]
    elif order == 35:
        shared_stage(draw, mask)
        draw_rect(draw, mask, (1185, 305, 1295, 375), fill=COLORS["tin"], outline=COLORS["ink"], width=7)
        draw.text((1215, 327), "TIN", fill=COLORS["ink"])
        draw_line(draw, mask, (1080, 820, 1210, 400), fill="#ead9a8", width=16)
        objects = ["sealed_tin", "daylight"]
    elif order == 36:
        shared_stage(draw, mask)
        role(draw, mask, "SIGRID", (270, 585, 470, 915))
        role(draw, mask, "SOREN", (520, 320, 690, 710))
        draw_line(draw, mask, (455, 790, 850, 330), fill="#9a6a3e", width=64)
        draw_ellipse(draw, mask, (430, 750, 495, 815), fill=COLORS["sigrid"], outline=COLORS["ink"], width=5)
        draw_line(draw, mask, (650, 400, 840, 330), fill=COLORS["soren"], width=42)
        draw_rect(draw, mask, (860, 285, 935, 335), fill=COLORS["tin"], outline=COLORS["ink"], width=6)
        objects = ["sealed_tin", "fallen_plank"]
    elif order == 37:
        draw_rect(draw, mask, (110, 680, 1430, 1000), fill="#575958", outline=COLORS["ink"], width=7)
        draw_rect(draw, mask, (210, 455, 455, 650), fill=COLORS["tin"], outline=COLORS["ink"], width=7)
        draw_rect(draw, mask, (525, 520, 790, 730), fill=COLORS["map"], outline=COLORS["ink"], width=7)
        for x in range(850, 1070, 42):
            draw_line(draw, mask, (x, 600, x + 24, 690), fill=COLORS["matches"], width=12)
        draw_rect(draw, mask, (1130, 500, 1350, 690), fill=COLORS["note"], outline=COLORS["ink"], width=7)
        objects = ["opened_tin", "creek_map", "dry_matches", "blank_note_card"]
    elif order == 38:
        draw_rect(draw, mask, (170, 260, 1360, 955), fill=COLORS["map"], outline=COLORS["ink"], width=9)
        draw_line(draw, mask, (250, 810, 450, 620, 690, 700, 920, 470, 1260, 580), fill="#4c8194", width=28)
        draw_rect(draw, mask, (430, 520, 520, 610), fill="#75523b", outline=COLORS["ink"], width=7)
        draw_ellipse(draw, mask, (1000, 455, 1100, 555), outline="#75523b", width=14)
        draw.text((390, 625), "FARMHOUSE\nSQUARE", fill=COLORS["ink"], spacing=5)
        draw.text((985, 575), "MILL\nCIRCLE", fill=COLORS["ink"], spacing=5)
        objects = ["creek_map", "farmhouse_square", "mill_circle"]
    else:
        raise ValueError(order)
    return objects


def main() -> None:
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    selected = json.loads(SLICE.read_text(encoding="utf-8"))
    by_id = {item["panel_id"]: item for item in plans["plans"]}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows, images = [], []
    for panel_id in selected["panel_ids"]:
        plan = by_id[panel_id]
        safe = rect_px(plan["comic_direction"]["lettering"]["safe_zones"][0]["rect_norm"])
        image = Image.new("RGB", SIZE, COLORS["background"])
        occupancy = Image.new("L", SIZE, 0)
        draw, mask_draw = ImageDraw.Draw(image), ImageDraw.Draw(occupancy)
        objects = panel_geometry(plan["display_order"], draw, mask_draw)
        draw.rectangle(safe, outline="#ef5b5b", width=6)
        draw.text((safe[0] + 12, safe[1] + 12), "LETTERING SAFE ZONE", fill="#ffb0b0")
        image_path = OUT_DIR / f"ch05-p{plan['display_order']:03d}-layout-control-r1.png"
        occupancy_path = OUT_DIR / f"ch05-p{plan['display_order']:03d}-story-occupancy-r1.png"
        image.save(image_path)
        occupancy.save(occupancy_path)
        safe_array = np.zeros((SIZE[1], SIZE[0]), dtype=bool)
        safe_array[safe[1]:safe[3], safe[0]:safe[2]] = True
        occupied = np.asarray(occupancy) > 0
        overlap = int((occupied & safe_array).sum())
        rows.append({
            "panel_id": panel_id,
            "plan_revision_id": plan["plan_revision_id"],
            "display_order": plan["display_order"],
            "visible_adult_cast": plan["visible_adult_cast"],
            "role_proxy_count": len(plan["visible_adult_cast"]),
            "object_tokens": objects,
            "lettering_safe_zone_rect_px": list(safe),
            "story_occupancy_safe_zone_overlap_pixels": overlap,
            "story_occupancy_safe_zone_overlap_fraction": round(overlap / max(1, int(safe_array.sum())), 9),
            "image": {"path": image_path.relative_to(ROOT).as_posix(), "sha256": sha256(image_path)},
            "story_occupancy_mask": {"path": occupancy_path.relative_to(ROOT).as_posix(), "sha256": sha256(occupancy_path)},
            "human_review_status": "not_yet_performed",
            "human_minutes": None,
            "accepted": False,
        })
        images.append(image)

    thumbs = [ImageOps.contain(image, (512, 341)) for image in images]
    sheet = Image.new("RGB", (1536, 682), "#17191b")
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % 3) * 512, (index // 3) * 341))
    sheet_path = OUT_DIR / "ch05-p033-p038-sequence-contact-sheet-r1.png"
    sheet.save(sheet_path)

    record = {
        "record_type": "ComicPanelSequenceLayoutControl",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p033-p038-sequence-layout-control-r1",
        "state": "LOCAL_DETERMINISTIC_ABSTRACT_CONTROL_NOT_ART",
        "medium": "comic",
        "animation_shot_plan": None,
        "sources": {
            "comic_panel_plans": {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha256(PLANS)},
            "demonstration_slice": {"path": SLICE.relative_to(ROOT).as_posix(), "sha256": sha256(SLICE)},
            "demonstration_packet": {"path": PACKET.relative_to(ROOT).as_posix(), "sha256": sha256(PACKET)},
        },
        "continuity_color_tokens": {key: value for key, value in COLORS.items() if key in {"soren", "sigrid", "bell", "tin", "map"}},
        "panels": rows,
        "contact_sheet": {"path": sheet_path.relative_to(ROOT).as_posix(), "sha256": sha256(sheet_path)},
        "summary": {
            "panel_count": len(rows),
            "role_proxy_count": sum(item["role_proxy_count"] for item in rows),
            "safe_zone_overlap_pixels": sum(item["story_occupancy_safe_zone_overlap_pixels"] for item in rows),
            "provider_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
            "accepted_panels": 0,
            "human_minutes": None,
        },
        "limitations": [
            "Geometry and color tokens are compiler diagnostics, not fictional character designs or panel art.",
            "Control-local role position and color conventions do not add canon or directing intent.",
            "Object-token recurrence tests dependency plumbing, not achieved visual continuity.",
            "These files are not approved base rasters or authorized provider inputs.",
        ],
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(RESULT)


if __name__ == "__main__":
    main()
