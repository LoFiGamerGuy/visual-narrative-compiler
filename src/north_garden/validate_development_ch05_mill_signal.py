"""Validate the clean non-canon chapter-scale planning option without promoting it."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/development/clean-ch05-mill-signal-r1.json"


def main() -> None:
    record = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert record["record_type"] == "NarrativeDevelopmentScript"
    assert record["state"] == "NONCANON_REVIEW_DRAFT_NOT_A_COMIC_PLAN_OR_RENDER_REQUEST"
    assert record["continuity_proposal"]["animation_shot_plan"] is None
    assert record["source_boundary"]["does_not_import"]
    panels = record["panels"]
    assert len(panels) == 50
    assert [item["display_order"] for item in panels] == list(range(1, 51))
    assert len({item["panel_id"] for item in panels}) == 50
    allowed = {"SOREN", "SIGRID"}
    assert all(set(item["visible_adult_cast"]) <= allowed for item in panels)
    assert all("DIO" not in json.dumps(item) and "THAL" not in json.dumps(item) for item in panels)
    print("0 failures, 0 warnings (clean CH05 development script is a 50-panel non-canon, adult-only planning option)")


if __name__ == "__main__":
    main()
