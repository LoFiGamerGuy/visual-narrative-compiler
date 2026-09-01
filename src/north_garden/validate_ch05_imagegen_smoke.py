"""Validate CH05 built-in visual-smoke provenance without promoting its non-canon script."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "research/development/clean-ch05-mill-signal-r1.json"
REVIEW = ROOT / "experiments/reviews/ch05-mill-signal-imagegen-smoke-review-r1.json"
RECORDS = ROOT / "experiments/records/built_in_imagegen_ch05"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    script = json.loads(SCRIPT.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    assert script["state"] == "NONCANON_REVIEW_DRAFT_NOT_A_COMIC_PLAN_OR_RENDER_REQUEST"
    assert review["state"] == "PENDING_AUTHORIZED_HUMAN_REVIEW"
    assert review["summary"]["candidate_generations"] == 4 and review["summary"]["research_accepted"] == 0
    expected = {"ng-dev-ch05-p001", "ng-dev-ch05-p029", "ng-dev-ch05-p036", "ng-dev-ch05-p050"}
    observed = set()
    for path in sorted(RECORDS.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        observed.add(record["development_panel_id"])
        output = ROOT / record["output"]["path"]
        assert output.exists() and sha256(output) == record["output"]["sha256"]
        assert record["accepted"] is False and record["human_minutes"] is None
        assert record["prompt_safety"] == {"fictional_adults_only": True, "child_data": False, "adult_likeness_input": False, "external_personal_data_upload": False, "age_wording_hygiene": "pass"}
    assert observed == expected
    print("0 failures, 0 warnings (CH05 built-in visual-smoke provenance validated; no canon or acceptance promotion)")


if __name__ == "__main__":
    main()
