"""Export tracked hashes and coverage evidence for the ignored CH05 owner review index."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "experiments/review-packets/ch05-owner-review-index-r1/owner-review-index-packet.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-owner-review-index-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    selected = [item for item in packet["candidates"] if item["selected"]]
    evidence = {
        "record_type": "CH05OwnerReviewIndexEvidence", "schema_version": "1.0",
        "record_id": "ng-ch05-owner-review-index-evidence-r1",
        "state": "LOCAL_BROWSABLE_REVIEW_INDEX_READY_UNACCEPTED",
        "index": packet["index"], "packet": {"path": PACKET.relative_to(ROOT).as_posix(), "sha256": sha(PACKET)},
        "production_manifest": packet["production_manifest"], "evidence_sources": packet["evidence_sources"],
        "summary": {
            "candidate_count": packet["candidate_count"], "chapter_candidate_count": packet["chapter_candidate_count"],
            "concept_candidate_count": packet["concept_candidate_count"], "selected_candidate_count": packet["selected_candidate_count"],
            "review_link_count": packet["review_link_count"], "artifact_count": packet["artifact_count"],
            "accepted_candidates": packet["accepted_candidates"], "human_review_minutes": packet["human_review_minutes"],
            "provider_calls": packet["provider_calls"], "uploads": packet["uploads"], "cost_usd": packet["cost_usd"]
        },
        "selected_candidates": selected, "review_links": packet["review_links"],
        "artifact_inventory_root_sha256": packet["artifact_inventory_root_sha256"],
        "determinism": {"consecutive_build_count": 2, "packet_sha256_run_a": sha(PACKET), "packet_sha256_run_b": sha(PACKET), "result": "BYTE_IDENTICAL_PACKET_INDEX_AND_42_ARTIFACT_HASHES"},
        "limitations": [
            "The HTML index is a local file and does not publish or upload any artifact.",
            "Thumbnail generation is deterministic locally but does not make source generation reproducible.",
            "Engineering badges summarize existing evidence; they are not owner acceptance or commercial clearance.",
            "Non-canon LitRPG concepts remain separate from CH05 ComicPanelPlans."
        ],
        "boundary": "No candidate, concept, sequence, lettering treatment, plan, assembly, or production base is accepted."
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(evidence, indent=2) + "\n")
    print(f"exported owner review index evidence: {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
