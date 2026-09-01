"""Build a deterministic, local-only CH05 P036 comic layout control.

The output is abstract geometry for compiler contract validation, not character
art, an accepted panel, an external input authorization, or animation direction.
"""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
READINESS = ROOT / "production/comic/repair-readiness/ch05-p036-openai-r1.json"
OUT_DIR = ROOT / "experiments/outputs/ch05_p036_layout_control_r1"
RESULT = ROOT / "experiments/results/ch05-p036-layout-control-r1.json"
SIZE = (1536, 1024)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rect_px(rect: list[float]) -> tuple[int, int, int, int]:
    x, y, width, height = rect
    return round(x * SIZE[0]), round(y * SIZE[1]), round((x + width) * SIZE[0]), round((y + height) * SIZE[1])


def main() -> None:
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    panel = next(item for item in plans["plans"] if item["panel_id"] == "ng-ch05-sc01-p036")
    safe = rect_px(panel["comic_direction"]["lettering"]["safe_zones"][0]["rect_norm"])
    repair = (690, 225, 970, 520)

    image = Image.new("RGB", SIZE, "#34383b")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 720, SIZE[0], SIZE[1]), fill="#23282b")
    draw.rectangle((120, 165, 1410, 220), fill="#6a5540", outline="#151515", width=6)
    draw.rectangle((145, 225, 200, 950), fill="#544638", outline="#151515", width=6)
    draw.rectangle((1320, 225, 1375, 950), fill="#544638", outline="#151515", width=6)

    # Neutral role proxies only; rectangles are not character designs.
    draw.rectangle((520, 300, 690, 700), fill="#c7761e", outline="#111111", width=7)
    draw.text((555, 470), "SOREN\nROLE", fill="white", spacing=8)
    draw.rectangle((270, 585, 470, 915), fill="#278b91", outline="#111111", width=7)
    draw.text((315, 725), "SIGRID\nROLE", fill="white", spacing=8)

    # Plank: Sigrid braces the lower end; Soren reaches near its upper end.
    draw.line((455, 790, 850, 300), fill="#9a6a3e", width=64)
    draw.line((455, 790, 850, 300), fill="#151515", width=5)
    draw.ellipse((430, 750, 495, 815), fill="#278b91", outline="#111111", width=5)
    draw.line((650, 380, 840, 300), fill="#c7761e", width=42)
    draw.ellipse((815, 270, 870, 325), fill="#c7761e", outline="#111111", width=5)
    draw.rectangle((860, 245, 935, 295), fill="#d5c6a3", outline="#111111", width=6)
    draw.text((872, 260), "TIN", fill="#111111")

    # Safe zone is deliberately empty and separate from causal action.
    draw.rectangle(safe, outline="#ef5b5b", width=6)
    draw.text((safe[0] + 12, safe[1] + 12), "LETTERING SAFE ZONE — KEEP EMPTY", fill="#ffb0b0")

    mask = Image.new("L", SIZE, 0)
    ImageDraw.Draw(mask).rectangle(repair, fill=255)
    overlay = image.copy()
    overlay_draw = ImageDraw.Draw(overlay, "RGBA")
    overlay_draw.rectangle(repair, fill=(70, 255, 110, 55), outline=(80, 255, 120, 255), width=6)
    overlay_draw.text((repair[0] + 10, repair[1] + 10), "TARGET REPAIR CONTEXT", fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 80, 20, 255))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base_path = OUT_DIR / "ch05-p036-layout-control-r1.png"
    mask_path = OUT_DIR / "ch05-p036-target-context-mask-r1.png"
    overlay_path = OUT_DIR / "ch05-p036-layout-mask-overlay-r1.png"
    image.save(base_path)
    mask.save(mask_path)
    overlay.save(overlay_path)

    safe_array = np.zeros((SIZE[1], SIZE[0]), dtype=bool)
    safe_array[safe[1]:safe[3], safe[0]:safe[2]] = True
    mask_array = np.asarray(mask) > 0
    record = {
        "record_type": "ComicPanelLayoutControl",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p036-layout-control-r1",
        "state": "LOCAL_ABSTRACT_COMIC_LAYOUT_CONTROL_NOT_ART",
        "created_at": stamp(),
        "comic_panel_plan": readiness["comic_panel_plan"],
        "plan_source": {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha256(PLANS)},
        "intent": {
            "visible_adult_role_proxies": panel["visible_adult_cast"],
            "narrative_beat": panel["narrative_beat"],
            "composition_intent": panel["composition_intent"],
            "causal_relationship": "Sigrid braces lower plank; Soren reaches at upper plank toward tin.",
            "lettering_safe_zone": {"rect_px_xyxy": list(safe), "source": "ComicPanelPlan"},
            "animation_shot_plan": plans["animation_shot_plan"],
        },
        "outputs": {
            "base": {"path": base_path.relative_to(ROOT).as_posix(), "sha256": sha256(base_path)},
            "target_context_mask": {"path": mask_path.relative_to(ROOT).as_posix(), "sha256": sha256(mask_path)},
            "overlay": {"path": overlay_path.relative_to(ROOT).as_posix(), "sha256": sha256(overlay_path)},
        },
        "measurements": {
            "canvas": list(SIZE),
            "role_proxy_count": 2,
            "target_mask_fraction": round(float(mask_array.mean()), 9),
            "target_mask_lettering_safe_zone_overlap_fraction": round(float((mask_array & safe_array).mean()), 9),
            "lettering_safe_zone_empty_by_construction": True,
        },
        "execution": {"provider_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"},
        "review": {"human_review_status": "not_yet_performed", "human_minutes": None, "accepted": False},
        "limitations": [
            "Rectangles and lines are layout/compiler proxies, not fictional character designs or final comic art.",
            "The control tests declared composition and mask/safe-zone topology only.",
            "It is not authorized as provider input and makes no continuity, commercial, or acceptance claim."
        ],
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(RESULT)


if __name__ == "__main__":
    main()
