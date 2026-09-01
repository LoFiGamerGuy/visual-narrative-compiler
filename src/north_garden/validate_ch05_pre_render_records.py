"""Validate CH05 approved pre-render comic records and their promotion boundary."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEVELOPMENT = ROOT / "research/development/clean-ch05-mill-signal-r1.json"
DECISION = ROOT / "production/decisions/ng-decision-ch05-mill-signal-promotion-r1.json"
STORY = ROOT / "production/canon/story-state/ch05-sc01-r1.json"
ASSETS = ROOT / "production/assets/asset-registry-ch05-r1.json"
BEAT = ROOT / "production/scene-beats/ch05-sc01-mill-signal-r1.json"
STYLE = ROOT / "production/comic/style-direction/ch05-mill-signal-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
ASSERTIONS = ROOT / "production/comic/hard-assertion-manifests/ch05-mill-signal-r1.json"


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    development, decision, story, assets, beat, style, plans, assertions = map(load, [DEVELOPMENT, DECISION, STORY, ASSETS, BEAT, STYLE, PLANS, ASSERTIONS])
    assert decision["state"] == "APPROVED_FOR_CANON_AND_COMIC_PANEL_PLAN_DEVELOPMENT"
    assert decision["source_development_script_sha256"] == hashlib.sha256(DEVELOPMENT.read_bytes()).hexdigest()
    assert story["promotion_decision"] == str(DECISION.relative_to(ROOT)).replace("\\", "/")
    assert assets["story_state_id"] == story["record_id"] == plans["story_state_id"] == beat["story_state_id"]
    assert plans["medium"] == "comic" and plans["animation_shot_plan"] is None
    assert style["animation_shot_plan"] is None and style["state"] == "PRE_RENDER_DIRECTION_NOT_EXECUTION_PROVENANCE"
    rows = plans["plans"]
    assert len(rows) == len(development["panels"]) == 50
    assert [row["display_order"] for row in rows] == list(range(1, 51))
    assert len({row["panel_id"] for row in rows}) == 50
    assert all(row["spatial_mode"] == "2d_only" for row in rows)
    assert all(row["comic_direction"]["lettering"]["safe_zones"] for row in rows)
    assert all(row["comic_direction"]["motion_mode"] in {"directional_motion", "practical_action", "held_sensory_event", "held_observation"} for row in rows)
    assert assertions["state"] == "APPROVED_CURRENT_COMIC_PRE_RENDER_NOT_BENCHMARK"
    assert len(assertions["assertions"]) == 53
    assert "RenderRecord" in decision["decision_scope"]["must_not_promote_automatically"]
    print("0 failures, 0 warnings (CH05 approved pre-render comic intent validated; no render/acceptance promotion)")


if __name__ == "__main__":
    main()
