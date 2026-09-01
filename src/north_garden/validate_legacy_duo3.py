"""Validate reconstructed provenance and review linkage for legacy_duo3."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "experiments/reviews/legacy-duo3-ch03-ridge-signal-review-r2-reconstructed.json"
INCIDENT = ROOT / "experiments/incidents/legacy-duo3-dry-run-overwrite-correction-20260901.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    incident = json.loads(INCIDENT.read_text(encoding="utf-8"))
    assert incident["record_type"] == "ProvenanceCorrectionReport"
    assert incident["prevention"] == "legacy_duo3.py dry runs now write no records."
    assert review["adapter"] == "legacy_duo3" and review["summary"]["accepted"] == 0
    assert review["summary"]["generation_seconds"] == 117.312
    assert review["review"]["human_minutes"] is None
    assert len(review["candidates"]) == 3
    for candidate in review["candidates"]:
        record_path = ROOT / candidate["record_path"]
        record = json.loads(record_path.read_text(encoding="utf-8"))
        assert record["status"] == "completed" and record["panel_id"] == candidate["panel_id"]
        assert record["provenance_reconstruction"]["sources"] == ["local ComfyUI history", "existing r1 review", "existing output bytes"]
        assert record["safety"] == {"adult_only_prompt_check": "pass", "external_upload": False, "child_data": False}
        assert record["generated_candidates"][0]["sha256"] == candidate["sha256"]
        assert sha256(ROOT / candidate["candidate_path"]) == candidate["sha256"]
        assert record["generation_seconds"] == candidate["generation_seconds"]
        assert candidate["decision"] == "reject" and any(value == "fail" for value in candidate["hard_assertions"].values())
    print("0 failures, 0 warnings (legacy_duo3 r2 reconstruction and local production demo validated)")


if __name__ == "__main__":
    main()
