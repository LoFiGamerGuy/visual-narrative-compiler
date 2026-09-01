"""Adversarially validate candidate review/promotion without real approval."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from PIL import Image

from comic_input_gate import base_raster_errors
from prepare_comic_base_candidate import ROOT, prepare_candidate
from promote_comic_base_candidate import CandidatePromotionError, build_approval, review_errors


def valid_review(candidate: dict) -> dict:
    link = candidate["comic_panel_plan"]
    return {
        "record_type": "ComicPanelBaseRasterCandidateReview",
        "schema_version": "1.0",
        "record_id": f"{candidate['record_id']}-synthetic-review-r1",
        "state": "COMPLETED",
        "candidate_record_id": candidate["record_id"],
        "candidate_raster_sha256": candidate["raster"]["sha256"],
        "comic_panel_plan": {"panel_id": link["panel_id"], "plan_revision_id": link["plan_revision_id"]},
        "reviewer": {"reviewer_id": "synthetic-validator-not-human", "human_review_status": "completed", "human_minutes": 1.0},
        "data_classification": {
            "fictional_adults_only": True, "real_person_likeness": False, "child_material": False,
            "personal_or_biometric_data": False, "lora_output": False,
        },
        "art_and_provenance_review": {
            "approval_eligible": True, "provenance_sufficient_for_local_repair": True,
            "commercial_state": "SYNTHETIC_VALIDATION_ONLY",
            "applicable_hard_assertions": [{"id": "synthetic_fixture", "passed": True}],
            "accepted_as_local_base": True, "failure_tags": [],
        },
        "permissions": {"local_repair_input_authorized": True, "external_upload_authorized": False},
        "validation_fixture": True,
    }


def main() -> int:
    failures = []
    candidates = sorted((ROOT / "experiments/intake/comic-base-candidates").glob("*layout-control-candidate-r2.json"))
    if len(candidates) != 6:
        failures.append(f"expected six layout candidates, found {len(candidates)}")
    for path in candidates:
        candidate = json.loads(path.read_text(encoding="utf-8"))
        try:
            build_approval(candidate, valid_review(candidate))
            failures.append(f"policy-ineligible control promoted: {candidate['record_id']}")
        except CandidatePromotionError:
            pass

    synthetic_path = ROOT / "experiments/outputs/candidate_promotion_validation/synthetic-eligible-raster.png"
    synthetic_path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (64, 64), "#456789").save(synthetic_path)
    candidate_path = prepare_candidate(
        panel_id="ng-ch05-sc01-p033",
        raster_path=synthetic_path,
        candidate_id="ng-ch05-p033-synthetic-eligible-fixture-r1",
    )
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    review = valid_review(candidate)
    if review_errors(candidate, review):
        failures.append("synthetic eligible review fixture did not pass review mechanics")
    approval = build_approval(candidate, review)
    if approval["state"] != "SYNTHETIC_VALIDATION_ONLY_NOT_APPROVAL":
        failures.append("validation fixture became a real approval")
    gate = base_raster_errors(approval, "ng-ch05-sc01-p033", "ng-ch05-sc01-p033-plan-r1")
    if not gate or "base_raster_state_not_approved" not in gate:
        failures.append("validation fixture passed real base gate")

    mutations = [
        ("minutes", lambda x: x["reviewer"].update(human_minutes=None)),
        ("child", lambda x: x["data_classification"].update(child_material=True)),
        ("likeness", lambda x: x["data_classification"].update(real_person_likeness=True)),
        ("hash", lambda x: x.update(candidate_raster_sha256="0" * 64)),
        ("assertion", lambda x: x["art_and_provenance_review"]["applicable_hard_assertions"][0].update(passed=False)),
        ("provenance", lambda x: x["art_and_provenance_review"].update(provenance_sufficient_for_local_repair=False)),
        ("external", lambda x: x["permissions"].update(external_upload_authorized=True)),
        ("local_permission", lambda x: x["permissions"].update(local_repair_input_authorized=False)),
    ]
    for label, mutate in mutations:
        changed = copy.deepcopy(review)
        mutate(changed)
        if not review_errors(candidate, changed):
            failures.append(f"promotion mutation passed: {label}")

    for failure in failures:
        print(f"failure: {failure}")
    if failures:
        return 1
    print("0 failures, 0 warnings (6/6 layout controls blocked; synthetic fixture non-approval; 8/8 review mutations rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
