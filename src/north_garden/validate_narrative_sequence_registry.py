"""Validate the immutable-link boundary of the narrative sequence registry."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "production/comic/narrative-sequence-registry-r1.json"


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    target = registry["chapter_scale_target_panels"]
    assert registry["record_type"] == "NarrativeSequenceRegistry"
    assert int(target["minimum"]) == 50 and int(target["maximum"]) == 90
    seen: set[str] = set()
    for item in registry["entries"]:
        assert item["sequence_id"] not in seen
        seen.add(item["sequence_id"])
        edition_path = ROOT / item["edition"]
        review_path = ROOT / item["review"]
        lint_path = ROOT / item["lint"]
        assert edition_path.exists() and review_path.exists() and lint_path.exists()
        edition = json.loads(edition_path.read_text(encoding="utf-8"))
        review = json.loads(review_path.read_text(encoding="utf-8"))
        assert edition["publication_state"] == "DRAFT_REVIEW_PENDING_NOT_PUBLISHED"
        assert review["state"] == "PENDING_AUTHORIZED_HUMAN_REVIEW"
        assert review["summary"]["research_accepted"] == 0
        assert int(item["panel_count"]) < int(target["minimum"])
        assert item["state"] == "DRAFT_REVIEW_PENDING_NOT_CHAPTER_SCALE"
    print("0 failures, 0 warnings (narrative sequence registry boundary validated)")


if __name__ == "__main__":
    main()
