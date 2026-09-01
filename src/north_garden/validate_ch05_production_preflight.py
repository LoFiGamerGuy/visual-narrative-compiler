"""Validate the compiled CH05 chapter-scale no-render preflight."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "experiments/results/ch05-production-preflight-r1.json"


def main() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    assert record["record_type"] == "ChapterProductionPreflight"
    assert record["state"] == "CHAPTER_INTENT_COMPILED_NO_APPROVED_BASE_ART_NO_RENDER_AUTHORITY"
    assert record["medium"] == "comic" and record["animation_shot_plan"] is None
    summary = record["chapter_summary"]
    assert summary["planned_panels"] == summary["stable_panel_ids"] == summary["plan_revision_ids"] == 50
    assert summary["display_order_contiguous"] is True
    assert sum(summary["cast_count_distribution"].values()) == 50
    assert sum(summary["motion_mode_distribution"].values()) == 50
    assert summary["approved_base_rasters"] == summary["render_records"] == summary["accepted_panels"] == 0
    assert summary["authorized_human_review_minutes"] is None
    demo = record["demonstration_slice"]
    assert demo["panel_count"] == 6 and demo["display_order"] == list(range(33, 39))
    assert demo["p036_layout_control_ready"] is True and demo["execution_authorized"] is False
    assert len(record["panels"]) == 50
    assert all(panel["external_execution_authorized"] is False and panel["accepted"] is False for panel in record["panels"])
    assert all(panel["human_minutes"] is None and panel["base_raster_state"] == "MISSING_APPROVED_BASE" for panel in record["panels"])
    print("0 failures, 0 warnings (CH05 50-panel production preflight validated; six-panel slice remains no-render)")


if __name__ == "__main__":
    main()
