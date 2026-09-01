"""Build a local review packet for candidate eligibility without art approval."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANDIDATES = ROOT / "experiments/intake/comic-base-candidates"
SEQUENCE = ROOT / "experiments/results/ch05-p033-p038-sequence-layout-control-r1.json"
OUT = ROOT / "experiments/reviews/ch05-p033-p038-base-candidate-intake-r1/review-packet.json"


def main() -> None:
    sequence = json.loads(SEQUENCE.read_text(encoding="utf-8"))
    rows = []
    for panel in sequence["panels"]:
        matches = sorted(CANDIDATES.glob(f"*{panel['panel_id']}*candidate-r2.json"))
        if len(matches) != 1:
            raise ValueError(f"expected one r2 candidate for {panel['panel_id']}, found {len(matches)}")
        candidate = json.loads(matches[0].read_text(encoding="utf-8"))
        rows.append({
            "panel_id": panel["panel_id"],
            "plan_revision_id": panel["plan_revision_id"],
            "candidate_record_id": candidate["record_id"],
            "raster_sha256": candidate["raster"]["sha256"],
            "candidate_kind": candidate["provenance"]["candidate_kind"],
            "policy_approval_eligible": candidate["approval_eligibility"]["eligible"],
            "policy_reason": candidate["approval_eligibility"]["reason"],
            "human_review_status": "not_yet_performed",
            "human_minutes": None,
            "accepted_as_base": False,
        })
    packet = {
        "record_type": "ComicPanelBaseCandidateReviewPacket",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p033-p038-base-candidate-review-packet-r1",
        "state": "POLICY_INELIGIBLE_LAYOUT_CONTROLS_NO_HUMAN_REVIEW_REQUIRED_FOR_PROMOTION",
        "medium": "comic",
        "animation_shot_plan": None,
        "contact_sheet": sequence["contact_sheet"],
        "candidates": rows,
        "summary": {
            "candidate_count": len(rows),
            "policy_ineligible": sum(item["policy_approval_eligible"] is False for item in rows),
            "approved_bases": 0,
            "external_uploads": 0,
            "human_minutes": None,
        },
        "boundary": "Packet exposes intake state; layout controls cannot be promoted as art under ADR-0027. No human decision or minute is fabricated.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
