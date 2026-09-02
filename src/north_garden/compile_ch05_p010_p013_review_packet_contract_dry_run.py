"""Compile fail-closed review-packet semantics for the P010-P013 production dry run."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-p010-p013-production-manifest-dry-run-r1.json"
CONTINUITY = ROOT / "production/comic/continuity/ch05-character-assertion-manifest-r1.json"
LETTERING = ROOT / "docs/research/evidence/ch05-transparent-lettering-rehearsal-r1.json"
DENSITY = ROOT / "docs/research/evidence/ch05-continuity-style-density-r1.json"
OUTPUT = ROOT / "production/comic/review/ch05-p010-p013-review-packet-contract-dry-run-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-p010-p013-review-packet-contract-dry-run-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    required_checks = [
        "cast_count",
        "role_identity_and_order",
        "hair_color_and_style",
        "canonical_wardrobe",
        "mature_adult_anatomy",
        "hands_and_story_object",
        "causal_action_or_clue",
        "lettering_safe_zone",
        "phone_size_readability",
        "role_appropriate_density",
        "sequence_finish_continuity",
    ]
    candidate_reviews = []
    for row in manifest["rows"]:
        candidate_reviews.append(
            {
                "candidate_slot": row["candidate_slot"],
                "panel_id": row["panel_id"],
                "expected_output_path": row["expected_output_path"],
                "output_sha256": None,
                "source_dimensions": None,
                "phone_preview_dimensions": None,
                "checks": {check: None for check in required_checks},
                "failure_classes": [],
                "repair_slot": None,
                "reviewer": None,
                "human_review_minutes": None,
                "decision": None,
            }
        )
    artifacts = [
        {"artifact_id": "candidate_contact_sheet", "filename": "contact-sheet-p010-p013-candidates.png", "purpose": "full-resolution side-by-side candidate review", "required_inputs": 4, "path": None, "sha256": None, "dimensions": None, "state": "NOT_BUILT"},
        {"artifact_id": "phone_contact_sheet", "filename": "contact-sheet-p010-p013-phone-390px.png", "purpose": "390px phone readability and silhouette comparison", "required_inputs": 4, "phone_width_px": 390, "path": None, "sha256": None, "dimensions": None, "state": "NOT_BUILT"},
        {"artifact_id": "continuity_sequence", "filename": "sequence-p010-p013-continuity.png", "purpose": "hair, wardrobe, cast transition, finish, and causal flow", "required_inputs": 4, "path": None, "sha256": None, "dimensions": None, "state": "NOT_BUILT"},
        {"artifact_id": "lettering_safe_zones", "filename": "contact-sheet-p010-p013-lettering-safe-zones.png", "purpose": "canonical protected-content overlays without text", "required_inputs": 4, "path": None, "sha256": None, "dimensions": None, "state": "NOT_BUILT"},
        {"artifact_id": "style_density_cadence", "filename": "comparison-p010-p013-style-density-cadence.png", "purpose": "role-appropriate density and four-beat finish rhythm", "required_inputs": 4, "path": None, "sha256": None, "dimensions": None, "state": "NOT_BUILT"},
    ]
    contract = {
        "record_type": "ComicMicrosequenceReviewPacketContractDryRun",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p010-p013-review-packet-contract-dry-run-r1",
        "state": "FAIL_CLOSED_NO_PIXELS_NO_REVIEW",
        "medium": "comic",
        "inputs": [binding(path) for path in (MANIFEST, CONTINUITY, LETTERING, DENSITY)],
        "summary": {"candidate_slots": 4, "required_checks_per_candidate": len(required_checks), "planned_artifacts": 5, "built_artifacts": 0, "completed_candidate_reviews": 0, "sequence_decisions": 0, "repair_slots_allocated": 0, "accepted_candidates": 0, "provider_calls": 0, "uploads": 0, "cost_usd": 0, "human_review_minutes": None},
        "required_checks": required_checks,
        "candidate_reviews": candidate_reviews,
        "planned_artifacts": artifacts,
        "failure_vocabulary": ["CAST_COUNT", "ROLE_ORDER", "HAIR_DRIFT", "WARDROBE_DRIFT", "ADULT_ANATOMY", "HAND_OR_OBJECT", "CAUSAL_GEOMETRY", "LETTERING_COLLISION", "PHONE_READABILITY", "DENSITY_ROLE", "FINISH_CONTINUITY"],
        "promotion_rules": [
            "Candidate decisions remain null until every required check is populated by a human reviewer.",
            "Any FAIL requires preservation as diagnostic evidence and may allocate at most one exact-class repair slot.",
            "A WARN cannot be silently promoted; its limitation must appear in the owner packet.",
            "Sequence acceptance requires all four candidate decisions plus explicit continuity, cadence, and lettering-semantics decisions.",
            "Engineering review cannot establish commercial clearance or exact production-base eligibility.",
        ],
        "sequence_review": {"hair_wardrobe_continuity": None, "cast_transition": None, "causal_flow": None, "density_cadence": None, "lettering_semantics": None, "decision": None, "reviewer": None, "human_review_minutes": None},
        "repair_allocation": {"maximum_slots": 2, "allocated_slots": 0, "broad_reroll": False, "passing_rows_must_be_preserved": True},
        "comic_panel_plan_revision_created": False,
        "animation_shot_plan": None,
        "e_conte": None,
        "boundary": "Review schema only. No pixels, reviews, decisions, repairs, provider activity, acceptance, or production promotion exist.",
    }
    OUTPUT.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8", newline="\n")
    evidence = {
        "record_type": "ComicMicrosequenceReviewPacketContractDryRunEvidence",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p010-p013-review-packet-contract-dry-run-evidence-r1",
        "state": "PASS_FAIL_CLOSED",
        "contract": binding(OUTPUT),
        "inputs": contract["inputs"],
        "summary": contract["summary"],
        "failure_vocabulary_count": len(contract["failure_vocabulary"]),
        "promotion_rule_count": len(contract["promotion_rules"]),
        "animation_shot_plan": None,
        "e_conte": None,
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("CH05 P010-P013 review contract: 4 slots/11 checks each/5 planned artifacts/11 failure classes/5 promotion rules")
    print("pixels/reviews/decisions/repairs/accepted/calls/uploads/cost 0/0/0/0/0/0/0/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
