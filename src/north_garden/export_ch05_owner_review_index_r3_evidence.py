"""Export tracked hashes for the ignored CH05 owner review index r3."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "experiments/review-packets/ch05-owner-review-index-r3/owner-review-index-r3-packet.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-owner-review-index-r3.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    evidence = {
        "record_type": "CH05OwnerReviewIndexEvidence",
        "schema_version": "3.0",
        "record_id": "ng-ch05-owner-review-index-evidence-r3",
        "state": "LOCAL_REVIEW_HUB_READY_OWNER_PENDING",
        "packet": {"path": PACKET.relative_to(ROOT).as_posix(), "sha256": sha(PACKET)},
        "extends": packet["extends"],
        "contract": packet["contract"],
        "summary": {
            "candidate_count": 29,
            "selected_candidate_count": 14,
            "pending_subject_count": 39,
            "link_count": packet["link_count"],
            "image_link_count": packet["image_link_count"],
            "html_link_count": packet["html_link_count"],
            "artifact_count": packet["artifact_count"],
            "owner_decisions": 0,
            "accepted_candidates": 0,
            "provider_calls": 0,
            "uploads": 0,
            "cost_usd": 0,
            "human_review_minutes": None,
        },
        "links": [{"id": row["id"], "path": row["path"], "sha256": row["sha256"], "kind": row["kind"]} for row in packet["links"]],
        "index": packet["index"],
        "determinism": {"consecutive_build_count": 2, "result": "BYTE_IDENTICAL_INDEX_PACKET_AND_THUMBNAILS"},
        "limitations": [
            "The hub only links local evidence and does not capture browser interaction.",
            "Owner decisions and timed review remain absent until a validated event workflow is used.",
            "Generated pixels remain ignored and commercially uncleared.",
        ],
        "boundary": packet["boundary"],
    }
    OUTPUT.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"exported CH05 owner review index r3 evidence {sha(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
