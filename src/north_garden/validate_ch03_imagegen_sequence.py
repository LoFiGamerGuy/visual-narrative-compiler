"""Validate CH03 built-in frontier-art provenance without judging art quality."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch03-sc01-panel-plans-v1.json"
REVISIONS = ROOT / "production/comic/panel-revisions/ch03-sc01-imagegen-r1.json"
REVIEW = ROOT / "experiments/reviews/ch03-ridge-signal-imagegen-review-r1.json"
EDITION = ROOT / "production/editions/north-garden-ch03-imagegen-draft-edition-001.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    revisions = json.loads(REVISIONS.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    edition = json.loads(EDITION.read_text(encoding="utf-8"))
    assert plans["medium"] == "comic" and plans["animation_shot_plan"] is None
    assert [item["panel_id"] for item in plans["plans"]] == ["ng-ch03-sc01-p001", "ng-ch03-sc01-p002", "ng-ch03-sc01-p003"]
    assert all(item["spatial_mode"] == "2d_only" for item in plans["plans"])
    assert len(revisions["revisions"]) == 3
    for revision in revisions["revisions"]:
        raster = ROOT / revision["asset_path"]
        record = ROOT / revision["render_record"]
        assert raster.exists() and sha256(raster) == revision["sha256"]
        payload = json.loads(record.read_text(encoding="utf-8"))
        assert payload["accepted"] is False and payload["human_minutes"] is None
        assert payload["prompt_safety"]["fictional_adults_only"] and not payload["prompt_safety"]["child_data"]
        assert payload["output"]["sha256"] == revision["sha256"]
    assert review["state"] == "PENDING_AUTHORIZED_HUMAN_REVIEW"
    assert review["summary"]["research_accepted"] == 0
    assert edition["publication_state"] == "DRAFT_REVIEW_PENDING_NOT_PUBLISHED"
    assert edition["selected_panel_revision_ids"] == [item["panel_revision_id"] for item in revisions["revisions"]]
    repair = ROOT / review["repair_candidate"]["record"]
    assert json.loads(repair.read_text(encoding="utf-8"))["failure_tags"] == ["required_prop_missing_or_unproven"]
    print("0 failures, 0 warnings (CH03 built-in frontier-art sequence provenance validated)")


if __name__ == "__main__":
    main()
