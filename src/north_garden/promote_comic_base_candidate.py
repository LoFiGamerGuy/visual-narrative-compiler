"""Validate human review and build a distinct local base approval record."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "experiments/intake/comic-base-approvals"


class CandidatePromotionError(ValueError):
    """Raised when candidate review cannot grant local base approval."""


def review_errors(candidate: dict, review: dict) -> list[str]:
    errors = []
    if candidate.get("record_type") != "ComicPanelBaseRasterCandidate":
        errors.append("candidate_record_type_invalid")
    if candidate.get("approval_eligibility", {}).get("eligible") is False:
        errors.append("candidate_policy_ineligible")
    if review.get("record_type") != "ComicPanelBaseRasterCandidateReview" or review.get("state") != "COMPLETED":
        errors.append("review_state_not_completed")
    if review.get("candidate_record_id") != candidate.get("record_id"):
        errors.append("candidate_record_id_mismatch")
    if review.get("candidate_raster_sha256") != candidate.get("raster", {}).get("sha256"):
        errors.append("candidate_raster_hash_mismatch")
    if review.get("comic_panel_plan") != {
        key: candidate.get("comic_panel_plan", {}).get(key)
        for key in ("panel_id", "plan_revision_id")
    }:
        errors.append("comic_panel_plan_mismatch")
    reviewer = review.get("reviewer", {})
    if not reviewer.get("reviewer_id") or reviewer.get("human_review_status") != "completed":
        errors.append("authorized_human_reviewer_missing")
    if not isinstance(reviewer.get("human_minutes"), (int, float)) or reviewer.get("human_minutes", 0) <= 0:
        errors.append("positive_human_minutes_missing")
    classification = review.get("data_classification", {})
    if classification.get("fictional_adults_only") is not True:
        errors.append("fictional_adults_only_not_confirmed")
    for field in ("real_person_likeness", "child_material", "personal_or_biometric_data", "lora_output"):
        if classification.get(field) is not False:
            errors.append(f"prohibited_or_unresolved_classification:{field}")
    art = review.get("art_and_provenance_review", {})
    if art.get("approval_eligible") is not True:
        errors.append("art_approval_eligibility_missing")
    if art.get("provenance_sufficient_for_local_repair") is not True:
        errors.append("local_provenance_review_missing")
    assertions = art.get("applicable_hard_assertions")
    if not isinstance(assertions, list) or not assertions:
        errors.append("applicable_hard_assertions_missing")
    elif any(item.get("passed") is not True for item in assertions):
        errors.append("hard_assertion_failed")
    if art.get("accepted_as_local_base") is not True:
        errors.append("local_base_acceptance_missing")
    permissions = review.get("permissions", {})
    if permissions.get("local_repair_input_authorized") is not True:
        errors.append("local_repair_permission_missing")
    if permissions.get("external_upload_authorized") is not False:
        errors.append("candidate_review_cannot_authorize_external_upload")
    return sorted(set(errors))


def build_approval(candidate: dict, review: dict) -> dict:
    errors = review_errors(candidate, review)
    if errors:
        raise CandidatePromotionError("; ".join(errors))
    fixture = review.get("validation_fixture") is True
    approval = {
        "record_type": "ComicPanelBaseRasterApproval",
        "schema_version": "1.0",
        "record_id": f"{candidate['record_id']}-base-approval-r1",
        "state": "SYNTHETIC_VALIDATION_ONLY_NOT_APPROVAL" if fixture else "APPROVED_FOR_LOCAL_REPAIR_INPUT",
        "synthetic_validation_fixture": fixture,
        "medium": "comic",
        "animation_shot_plan": None,
        "comic_panel_plan": candidate["comic_panel_plan"],
        "raster": {
            key: candidate["raster"][key]
            for key in ("path", "sha256", "width", "height")
        },
        "provenance": {
            **candidate["provenance"],
            "candidate_record_id": candidate["record_id"],
            "candidate_review_record_id": review["record_id"],
            "commercial_state": review["art_and_provenance_review"]["commercial_state"],
        },
        "data_classification": review["data_classification"],
        "review": {
            "reviewer_id": review["reviewer"]["reviewer_id"],
            "human_review_status": "completed",
            "human_minutes": review["reviewer"]["human_minutes"],
            "applicable_hard_assertions": review["art_and_provenance_review"]["applicable_hard_assertions"],
            "accepted": not fixture,
        },
        "permissions": {
            "local_repair_input_authorized": not fixture,
            "external_upload_authorized": False,
            "external_provider": None,
            "external_model_snapshot": None,
            "external_endpoint": None,
        },
        "boundary": "Local base approval never implies external upload. Validation fixtures remain non-approval records.",
    }
    return approval


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    args = parser.parse_args()
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    review = json.loads(args.review.read_text(encoding="utf-8"))
    approval = build_approval(candidate, review)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{approval['record_id']}.json"
    if out.exists() and json.loads(out.read_text(encoding="utf-8")) != approval:
        raise CandidatePromotionError("approval record already exists with different immutable content")
    out.write_text(json.dumps(approval, indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
