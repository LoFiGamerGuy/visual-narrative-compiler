"""Instrument the unaccepted CH05 P036 smoke raster for mask-readiness conflicts.

Creates a local review overlay only. It does not create a usable repair mask,
promote the smoke raster, call a provider, or revise ComicPanelPlan intent.
"""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
READINESS = ROOT / "production/comic/repair-readiness/ch05-p036-openai-r1.json"
OUT_DIR = ROOT / "experiments/review-packets/ch05-p036-repair-readiness-r1"
RESULT = ROOT / "experiments/results/ch05-p036-mask-authoring-preflight-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def px(rect: list[float], size: tuple[int, int]) -> list[int]:
    x, y, width, height = rect
    return [round(x * size[0]), round(y * size[1]), round((x + width) * size[0]), round((y + height) * size[1])]


def intersection(left: list[float], right: list[float]) -> list[float] | None:
    x1, y1 = max(left[0], right[0]), max(left[1], right[1])
    x2, y2 = min(left[0] + left[2], right[0] + right[2]), min(left[1] + left[3], right[1] + right[3])
    if x2 <= x1 or y2 <= y1:
        return None
    return [x1, y1, x2 - x1, y2 - y1]


def main() -> None:
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    smoke = ROOT / readiness["existing_smoke_evidence"]["path"]
    if sha256(smoke) != readiness["existing_smoke_evidence"]["sha256"]:
        raise SystemExit("smoke evidence hash mismatch")
    image = Image.open(smoke).convert("RGB")
    safe_norm = readiness["intent_snapshot"]["lettering_safe_zone"]["rect_norm"]
    # Non-gating agent annotation around Soren's reaching hand, tin, and their
    # immediate causal read. This is a review rectangle, not object detection.
    causal_norm = [0.60, 0.05, 0.17, 0.15]
    overlap_norm = intersection(safe_norm, causal_norm)
    if overlap_norm is None:
        raise SystemExit("expected annotated composition conflict was not present")

    safe_px, causal_px, overlap_px = px(safe_norm, image.size), px(causal_norm, image.size), px(overlap_norm, image.size)
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.rectangle(safe_px, fill=(255, 0, 0, 48), outline=(255, 50, 50, 255), width=5)
    draw.rectangle(causal_px, fill=(0, 255, 80, 42), outline=(40, 255, 100, 255), width=5)
    draw.rectangle(overlap_px, fill=(255, 220, 0, 105), outline=(255, 230, 0, 255), width=5)
    draw.text((safe_px[0] + 8, safe_px[1] + 8), "LETTERING SAFE ZONE", fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(120, 0, 0, 255))
    draw.text((causal_px[0] + 8, causal_px[3] + 8), "CAUSAL HAND / TIN REVIEW REGION", fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 80, 20, 255))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    overlay_path = OUT_DIR / "ch05-p036-lettering-target-conflict-overlay-r1.png"
    overlay.save(overlay_path)

    target_area = causal_norm[2] * causal_norm[3]
    overlap_area = overlap_norm[2] * overlap_norm[3]
    record = {
        "record_type": "ComicPanelMaskAuthoringPreflight",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p036-mask-authoring-preflight-r1",
        "state": "BLOCKED_BASE_COMPOSITION_CONFLICT_NO_MASK_EMITTED",
        "created_at": stamp(),
        "repair_readiness": {"path": READINESS.relative_to(ROOT).as_posix(), "sha256": sha256(READINESS)},
        "comic_panel_plan": readiness["comic_panel_plan"],
        "source": {
            "path": smoke.relative_to(ROOT).as_posix(),
            "sha256": sha256(smoke),
            "dimensions": list(image.size),
            "state": readiness["existing_smoke_evidence"]["state"],
        },
        "annotations": {
            "lettering_safe_zone": {"rect_norm": safe_norm, "rect_px_xyxy": safe_px, "source": "ComicPanelPlan"},
            "causal_hand_tin_review_region": {"rect_norm": causal_norm, "rect_px_xyxy": causal_px, "source": "non-gating agent visual annotation"},
            "intersection": {"rect_norm": overlap_norm, "rect_px_xyxy": overlap_px, "causal_region_overlap_fraction": round(overlap_area / target_area, 6)},
        },
        "output": {"overlay_path": overlay_path.relative_to(ROOT).as_posix(), "overlay_sha256": sha256(overlay_path), "target_mask": None},
        "decision": {
            "mask_authoring": "blocked",
            "reason": "The unaccepted smoke composition places the causal reaching hand/tin inside the approved top-right lettering safe zone.",
            "next_base_requirement": "Recompose the base so the hand/plank/tin causal read and all protected adult features sit outside the lettering safe zone, or create an explicit reviewed ComicPanelPlan revision.",
        },
        "execution": {"provider_requests": 0, "external_uploads": 0, "cost_usd": "0.000000"},
        "review": {"human_review_status": "not_yet_performed", "human_minutes": None, "accepted": False},
        "limitations": [
            "The causal rectangle is agent annotation, not calibrated segmentation.",
            "The overlay is review instrumentation, not a repair mask or accepted panel revision.",
            "No visual-quality or character-continuity conclusion follows."
        ],
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(RESULT)


if __name__ == "__main__":
    main()
