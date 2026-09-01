"""Exercise completed/failure/unknown boundary-evidence states without provider calls."""
from __future__ import annotations

import copy
import hashlib
import json

from PIL import Image

from render_record import ROOT
from render_record_boundary import boundary_incident_errors, boundary_render_record_errors, expected_profile
from submission_journal import append_event, journal_digest, new_journal
from validate_render_record import failure as legacy_failure, image_ref, ref, sha256, unknown as legacy_unknown


BASE = ROOT / "experiments/outputs/ch05_p036_layout_control_r1/ch05-p036-layout-control-r1.png"
CANDIDATE = ROOT / "experiments/outputs/render_record_boundary_fixture_r1/p036-synthetic-repair-candidate-r1.png"
VISUAL = ROOT / "experiments/results/render-record-boundary-visual-fixture-r1.json"
SESSION = ROOT / "experiments/results/render-record-boundary-seam-session-fixture-r1.json"


def write_fixture_files() -> None:
    binding = expected_profile("ng-ch05-sc01-p036")
    with Image.open(BASE) as base_image, Image.open(ROOT / binding["inward_alpha"]["path"]) as alpha_image:
        base = base_image.convert("RGB")
        fill = Image.new("RGB", base.size, (68, 104, 74))
        candidate = Image.composite(fill, base, alpha_image.convert("L"))
    CANDIDATE.parent.mkdir(parents=True, exist_ok=True)
    candidate.save(CANDIDATE, format="PNG", optimize=False, compress_level=9)
    visual = {
        "record_type": "SyntheticExactBaseBoundaryMeasurementFixture", "schema_version": "1.0",
        "synthetic_validation_fixture": True, "base_sha256": sha256(BASE), "candidate_sha256": sha256(CANDIDATE),
        "support_sha256": binding["support_mask"]["sha256"], "inward_alpha_sha256": binding["inward_alpha"]["sha256"],
        "changed_pixels_outside_support": 0, "max_abs_channel_difference_outside_support": 0,
    }
    session = {
        "record_type": "SyntheticTimedSeamReviewFixture", "schema_version": "1.0", "synthetic_validation_fixture": True,
        "reviewer_id": "synthetic-validator", "active_minutes": 3.0, "decision": "ACCEPT_BOUNDARY",
        "assertions": {"boundary": True, "causality": True, "protected_semantics": True, "lettering_clearance": True},
    }
    for path, value in ((VISUAL, visual), (SESSION, session)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def local_ref(path, record_id: str) -> dict:
    return {"record_id": record_id, "path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def completed() -> tuple[dict, dict, dict]:
    package_hash = "1" * 64
    journal = new_journal(
        journal_id="boundary-success-journal", adapter_id="openai_gpt_image_2", panel_id="ng-ch05-sc01-p036",
        plan_revision_id="ng-ch05-sc01-p036-plan-r1", panel_input_package_sha256=package_hash, attempt_ordinal=1,
    )
    journal = append_event(journal, to_state="RESERVED", occurred_at="2026-09-01T19:00:00Z", data={
        "aggregate_ledger": ref("synthetic-production-ledger"), "reservation_id": "reservation-boundary-success",
        "budget_domain": "NORTH_GARDEN_CH05_PRODUCTION", "adapter_id": "openai_gpt_image_2",
        "panel_input_package_sha256": package_hash, "reserved_usd": "0.500000",
    })
    journal = append_event(journal, to_state="SUBMISSION_STARTED", occurred_at="2026-09-01T19:01:00Z", data={"started_at": "2026-09-01T19:01:00Z", "idempotency_key": journal["idempotency_key"]})
    journal = append_event(journal, to_state="PROVIDER_ACKNOWLEDGED", occurred_at="2026-09-01T19:02:00Z", data={"provider_request_id": "request-boundary-success"})
    journal = append_event(journal, to_state="RESPONSE_CAPTURED", occurred_at="2026-09-01T19:03:00Z", data={"provider_request_id": "request-boundary-success", "output_sha256": [sha256(CANDIDATE)], "timing_seconds": 12.5})
    journal = append_event(journal, to_state="COST_RECONCILED", occurred_at="2026-09-01T19:04:00Z", data={"cost_reconciliation": ref("cost-boundary-success"), "actual_cost_usd": "0.100000"})
    journal = append_event(journal, to_state="RENDER_RECORD_PERSISTED", occurred_at="2026-09-01T19:05:00Z", data={"render_record": ref("render-boundary-success")})
    journal = append_event(journal, to_state="COMPLETED", occurred_at="2026-09-01T19:06:00Z", data={})
    ledger = {"record_type": "ProductionCostLedger", "record_id": "synthetic-production-ledger", "budget_domain": "NORTH_GARDEN_CH05_PRODUCTION", "entries": [{
        "reservation_id": "reservation-boundary-success", "adapter_id": "openai_gpt_image_2", "panel_input_package_sha256": package_hash,
        "reserved_usd": "0.500000", "actual_cost_usd": "0.100000", "state": "committed", "provider_request_id": "request-boundary-success",
    }]}
    binding = expected_profile("ng-ch05-sc01-p036")
    boundary = dict(binding)
    boundary.update({
        "outcome_state": "EXACT_BASE_CANDIDATE_MEASURED_SEAM_ACCEPTED",
        "exact_base_visual_boundary": {"state": "EXACT_BASE_AND_CANDIDATE_MEASURED", "base_sha256": sha256(BASE), "candidate_sha256": sha256(CANDIDATE), "evidence": local_ref(VISUAL, "synthetic-boundary-visual")},
        "exterior_result": {"changed_pixels": 0, "max_abs_channel_difference": 0, "exact": True},
        "no_change_result": {"requested": False, "candidate_byte_identical": False},
        "timed_seam_review": {"session": local_ref(SESSION, "synthetic-seam-session"), "status": "COMPLETED", "reviewer_id": "synthetic-validator", "active_minutes": 3.0, "decision": "ACCEPT_BOUNDARY", "assertions": {"boundary": True, "causality": True, "protected_semantics": True, "lettering_clearance": True}},
    })
    record = {
        "record_type": "RenderRecord", "schema_version": "2.1", "render_profile": "comic_targeted_repair_v2",
        "record_id": "render-boundary-success", "state": "SYNTHETIC_COMPLETED_PENDING_HUMAN_REVIEW", "synthetic_validation_fixture": True,
        "medium": "comic", "animation_shot_plan": None, "comic_panel_plan": {"panel_id": "ng-ch05-sc01-p036", "plan_revision_id": "ng-ch05-sc01-p036-plan-r1"},
        "submission_journal": {"record_id": journal["journal_id"], "path": "test/boundary-success-journal.json", "sha256": journal_digest(journal), "chain_head_sha256": journal["events"][-1]["event_sha256"], "idempotency_key": journal["idempotency_key"]},
        "provider": {"adapter_id": "openai_gpt_image_2", "provider": "OpenAI API", "model_snapshot": "gpt-image-2-2026-04-21", "endpoint": "https://api.openai.com/v1/images/edits", "provider_request_id": "request-boundary-success"},
        "request": {"panel_input_package_sha256": package_hash, "request_metadata_sha256": "2" * 64, "submitted_at": "2026-09-01T19:01:00Z", "completed_at": "2026-09-01T19:03:00Z"},
        "inputs": {"base_raster": image_ref(BASE), "repair_mask": image_ref(ROOT / binding["support_mask"]["path"])},
        "outputs": {"candidates": [image_ref(CANDIDATE)], "candidate_count": 1}, "timing": {"provider_seconds": 12.5, "end_to_end_seconds": 13.0},
        "provider_usage": {"synthetic_image_count": 1}, "provider_usage_unavailable_reason": None,
        "cost": {"reservation_id": "reservation-boundary-success", "actual_cost_usd": "0.100000", "reconciliation_method": "synthetic_exact_fixture", "cost_reconciliation": ref("cost-boundary-success")},
        "failure": None, "boundary_evidence": boundary,
        "review": {"human_review_status": "not_yet_performed", "human_minutes": None, "accepted": False},
        "acceptance": {"decision": "PENDING_HUMAN_REVIEW", "accepted": False},
    }
    return record, journal, ledger


def failed() -> tuple[dict, dict, dict]:
    record, journal, ledger = legacy_failure()
    record["schema_version"] = "2.1"
    record["render_profile"] = "comic_targeted_repair_v2"
    binding = expected_profile("ng-ch05-sc01-p036")
    record["inputs"]["repair_mask"] = image_ref(ROOT / binding["support_mask"]["path"])
    record["boundary_evidence"] = dict(binding, outcome_state="PROVIDER_FAILED_NO_CANDIDATE", exact_base_visual_boundary=None, exterior_result=None, no_change_result=None, timed_seam_review=None)
    return record, journal, ledger


def unknown() -> tuple[dict, dict, dict]:
    incident, journal, ledger = legacy_unknown()
    incident["schema_version"] = "1.1"
    return incident, journal, ledger


def main() -> int:
    write_fixture_files()
    failures: list[str] = []
    success_record, success_journal, success_ledger = completed()
    failed_record, failed_journal, failed_ledger = failed()
    incident, unknown_journal, unknown_ledger = unknown()
    if boundary_render_record_errors(success_record, success_journal, success_ledger): failures.append("completed boundary fixture failed")
    if boundary_render_record_errors(failed_record, failed_journal, failed_ledger): failures.append("failed boundary fixture failed")
    if boundary_incident_errors(incident, unknown_journal, unknown_ledger): failures.append("unknown incident fixture failed")
    mutations = [
        ("selector hash", success_record, success_journal, success_ledger, lambda x: x["boundary_evidence"]["selector_contract"].update(sha256="0" * 64), boundary_render_record_errors),
        ("profile width", success_record, success_journal, success_ledger, lambda x: x["boundary_evidence"]["profile"].update(local_width_px=5), boundary_render_record_errors),
        ("cross-panel profile", success_record, success_journal, success_ledger, lambda x: x["boundary_evidence"]["profile"].update(panel_id="ng-ch05-sc01-p044"), boundary_render_record_errors),
        ("support hash", success_record, success_journal, success_ledger, lambda x: x["boundary_evidence"]["support_mask"].update(sha256="0" * 64), boundary_render_record_errors),
        ("alpha hash", success_record, success_journal, success_ledger, lambda x: x["boundary_evidence"]["inward_alpha"].update(sha256="0" * 64), boundary_render_record_errors),
        ("topology", success_record, success_journal, success_ledger, lambda x: x["boundary_evidence"]["topology_evidence"].update(sha256="0" * 64), boundary_render_record_errors),
        ("missing visual", success_record, success_journal, success_ledger, lambda x: x["boundary_evidence"].update(exact_base_visual_boundary=None), boundary_render_record_errors),
        ("visual base", success_record, success_journal, success_ledger, lambda x: x["boundary_evidence"]["exact_base_visual_boundary"].update(base_sha256="0" * 64), boundary_render_record_errors),
        ("exterior", success_record, success_journal, success_ledger, lambda x: x["boundary_evidence"]["exterior_result"].update(changed_pixels=1), boundary_render_record_errors),
        ("no-change contradiction", success_record, success_journal, success_ledger, lambda x: x["boundary_evidence"]["no_change_result"].update(requested=True), boundary_render_record_errors),
        ("missing seam review", success_record, success_journal, success_ledger, lambda x: x["boundary_evidence"].update(timed_seam_review=None), boundary_render_record_errors),
        ("untimed seam review", success_record, success_journal, success_ledger, lambda x: x["boundary_evidence"]["timed_seam_review"].update(active_minutes=0), boundary_render_record_errors),
        ("failed fabricated visual", failed_record, failed_journal, failed_ledger, lambda x: x["boundary_evidence"].update(exact_base_visual_boundary={}), boundary_render_record_errors),
        ("unknown boundary evidence", incident, unknown_journal, unknown_ledger, lambda x: x.update(boundary_evidence={}), boundary_incident_errors),
        ("unknown selected width", incident, unknown_journal, unknown_ledger, lambda x: x.update(selected_width_px=16), boundary_incident_errors),
    ]
    for label, source, journal, ledger, mutate, validator in mutations:
        changed = copy.deepcopy(source); mutate(changed)
        if not validator(changed, journal, ledger): failures.append(f"mutation passed: {label}")
    for message in failures: print(f"failure: {message}")
    if failures: return 1
    print("0 failures, 0 warnings (v2.1 completed/failure/unknown boundary states; 15/15 mutations rejected)")
    print("completed binds selector/profile/width/support/alpha/topology/exact-base/exterior/no-change/timed seam; unknown binds none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
