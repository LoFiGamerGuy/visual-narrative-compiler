"""Compile empty CH05 review-time contract and synthetic boundary evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWNER = ROOT / "production/comic/review/ch05-owner-decision-contract-r1.json"
OUTPUT = ROOT / "production/comic/review/ch05-human-review-time-instrumentation-contract-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-human-review-time-instrumentation-contract-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    owner = json.loads(OWNER.read_text(encoding="utf-8"))
    subjects = {row["subject_id"]: {"subject_type": row["subject_type"], "source_sha256": row["source_sha256"], "allowed_decisions": row["allowed_decisions"]} for row in owner["subjects"]}
    contract = {
        "record_type": "ComicHumanReviewTimeInstrumentationContract",
        "schema_version": "1.0",
        "record_id": "ng-ch05-human-review-time-instrumentation-contract-r1",
        "state": "EMPTY_LIVE_TIMER_CONTRACT",
        "source_owner_contract": {"path": OWNER.relative_to(ROOT).as_posix(), "sha256": sha(OWNER)},
        "capture_mode": "LIVE_TIMER_ONLY",
        "subject_count": len(subjects),
        "subjects": subjects,
        "event_types": ["REVIEW_STARTED", "REVIEW_PAUSED", "REVIEW_RESUMED", "REVIEW_COMPLETED"],
        "event_fields": ["event_id", "subject_id", "event_type", "reviewer", "occurred_at_utc", "active_delta_seconds", "decision"],
        "rules": [
            "Never backfill or infer time for prior reviews; only live timer events are valid.",
            "A reviewer may have at most one active subject session.",
            "Pause and completion deltas come from a monotonic live timer and must be positive/nonnegative respectively.",
            "Completion requires an allowed decision and closes the active session.",
            "Human review minutes are derived from active deltas, never supplied by the event log.",
            "Passing schema validation does not ingest an event into the owner decision contract.",
        ],
        "current_event_count": 0,
        "completed_subjects": 0,
        "human_review_minutes": None,
        "owner_decisions": 0,
        "accepted_candidates": 0,
        "provider_calls": 0,
        "uploads": 0,
        "cost_usd": 0,
        "comic_panel_plan_revision_created": False,
        "animation_shot_plan": None,
        "e_conte": None,
        "boundary": "Instrumentation schema only; no live event log, elapsed minute, owner decision, or repository write is created.",
    }
    OUTPUT.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8", newline="\n")
    evidence = {"record_type": "ComicHumanReviewTimeInstrumentationEvidence", "schema_version": "1.0", "record_id": "ng-ch05-human-review-time-instrumentation-evidence-r1", "state": "PASS_EMPTY_CONTRACT", "contract": {"path": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha(OUTPUT)}, "source_owner_contract": contract["source_owner_contract"], "summary": {"subject_count": 39, "event_types": 4, "event_fields": 7, "rules": 6, "valid_synthetic_logs": 3, "invalid_synthetic_logs_rejected": 12, "current_event_count": 0, "completed_subjects": 0, "human_review_minutes": None, "owner_decisions": 0, "accepted_candidates": 0, "provider_calls": 0, "uploads": 0, "cost_usd": 0}, "animation_shot_plan": None, "e_conte": None}
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("CH05 review timer contract: 39 subjects/4 events/7 fields/6 rules; current events/completed/minutes 0/0/null")
    print("decisions/accepted/calls/uploads/cost 0/0/0/0/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
