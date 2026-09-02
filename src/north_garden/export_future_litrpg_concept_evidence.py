"""Export safe pixel-free evidence for the non-canon future LitRPG concept trio."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "experiments/review-packets/future-litrpg-visual-concepts-r1"
REGISTRY = RUN / "candidate-registry.json"
PACKET = RUN / "review/review-packet.json"
PLAN = ROOT / "production/comic/concepts/future-litrpg-visual-concepts-r1.json"
REVIEW = ROOT / "production/comic/review/future-litrpg-visual-concepts-review-r1.json"
OUT = ROOT / "docs/research/evidence/future-litrpg-visual-concepts-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    reviews = {item["candidate_id"]: item for item in review["entries"]}
    candidates = []
    for item in registry["entries"]:
        candidates.append({
            **item,
            "engineering_review": reviews[item["candidate_id"]],
            "human_review_state": "PENDING",
            "human_review_minutes": None,
            "accepted": False
        })
    record = {
        "record_type": "FutureLitRPGConceptEvidence",
        "schema_version": "1.0",
        "record_id": "ng-future-litrpg-concept-evidence-r1",
        "state": "NONCANON_ENGINEERING_REVIEWED_OWNER_REVIEW_PENDING",
        "canon_status": "NONCANON_FUTURE_EXPLORATION",
        "production_planning_record": False,
        "comic_panel_plan_revision": None,
        "animation_shot_plan": None,
        "e_conte": None,
        "plan": {"path": PLAN.relative_to(ROOT).as_posix(), "sha256": sha256(PLAN)},
        "review": {"path": REVIEW.relative_to(ROOT).as_posix(), "sha256": sha256(REVIEW)},
        "local_packet": {"path": PACKET.relative_to(ROOT).as_posix(), "sha256": sha256(PACKET)},
        "summary": {"candidate_count": 3, "total_elapsed_seconds": registry["total_elapsed_seconds"], "disclosed_spend_usd": None, "paid_api_used": False, "accepted_candidates": 0},
        "candidates": candidates,
        "review_artifacts": packet["artifacts"],
        "candidate_derivatives": packet["candidate_derivatives"],
        "provisional_direction": review["provisional_direction"],
        "limitations": review["limitations"],
        "boundary": "Armor, weapons, monster, class implication, and evolved wardrobe are non-canon ideas; generated pixels remain ignored and unaccepted."
    }
    OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"exported non-canon concept evidence: {OUT.relative_to(ROOT)} {sha256(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
