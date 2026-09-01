"""Append-only v2 boundary-evidence validation for repair RenderRecords."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from PIL import Image

from render_record import ROOT, file_errors, incident_errors, render_record_errors, sha_ref_errors
from review_session import validate_session


SELECTOR_PATH = ROOT / "config/scale-aware-repair-boundary-selector-contract-r1.json"
OUTCOME_FIELDS = {
    "boundary_evidence", "selector_contract", "boundary_profile", "selected_width_px",
    "support_mask", "inward_alpha", "topology_evidence", "exact_base_visual_boundary",
    "exterior_result", "no_change_result", "timed_seam_review",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_binding(value: dict) -> dict:
    path = ROOT / value["path"]
    with Image.open(path) as image:
        width, height = image.size
    return {"path": value["path"], "sha256": value["sha256"], "width": width, "height": height}


def load_json_ref(value: object, label: str) -> tuple[list[str], dict | None]:
    errors = sha_ref_errors(value, label)
    if errors or not isinstance(value, dict):
        return errors, None
    path = (ROOT / value["path"]).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        return errors + [f"{label}:file_missing_or_outside_root"], None
    if sha256_file(path) != value["sha256"]:
        return errors + [f"{label}:sha256_mismatch"], None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return errors + [f"{label}:invalid_json"], None
    if payload.get("record_id", payload.get("session_id")) != value["record_id"]:
        errors.append(f"{label}:record_id_mismatch")
    return errors, payload


def expected_profile(panel_id: str) -> dict:
    selector = json.loads(SELECTOR_PATH.read_text(encoding="utf-8"))
    profile = selector.get("profiles", {}).get(panel_id)
    if not profile:
        return {}
    if panel_id == "ng-ch05-sc01-p036":
        topology_ref = profile["sources"]["topology"]
        topology = json.loads((ROOT / topology_ref["path"]).read_text(encoding="utf-8"))
        support = topology["selected_outputs"]["support_mask"]
        alpha = topology["selected_outputs"]["inward_alpha"]
    elif panel_id == "ng-ch05-sc01-p044":
        topology_ref = profile["sources"]["adaptive_topology"]
        topology = json.loads((ROOT / topology_ref["path"]).read_text(encoding="utf-8"))
        support = topology["inputs"]["exact_support_mask"]
        alpha = topology["output"]["selected_inward_alpha"]
    else:
        return {}
    return {
        "selector_contract": {
            "record_id": selector["contract_id"],
            "path": SELECTOR_PATH.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(SELECTOR_PATH),
        },
        "profile": {
            "panel_id": panel_id,
            "plan_revision_id": profile["plan_revision_id"],
            "local_width_px": profile["local_width_px"],
        },
        "support_mask": image_binding(support),
        "inward_alpha": image_binding(alpha),
        "topology_evidence": {
            "record_id": topology["record_id"],
            "path": topology_ref["path"],
            "sha256": topology_ref["sha256"],
        },
    }


def boundary_render_record_errors(record: dict, journal: dict, cost_ledger: dict) -> list[str]:
    """Validate v2.1 while reusing the immutable v2.0 provenance contract."""
    errors: list[str] = []
    if record.get("schema_version") != "2.1" or record.get("render_profile") != "comic_targeted_repair_v2":
        errors.append("boundary_render_record_schema_invalid")
    legacy = copy.deepcopy(record)
    legacy["schema_version"] = "2.0"
    legacy["render_profile"] = "comic_targeted_repair_v1"
    legacy.pop("boundary_evidence", None)
    errors.extend(f"base:{item}" for item in render_record_errors(legacy, journal, cost_ledger))

    boundary = record.get("boundary_evidence")
    if not isinstance(boundary, dict):
        return sorted(set(errors + ["boundary_evidence_missing"]))
    expected = expected_profile(record.get("comic_panel_plan", {}).get("panel_id", ""))
    if not expected:
        errors.append("boundary_profile_not_registered")
        return sorted(set(errors))
    for field in ("selector_contract", "profile", "support_mask", "inward_alpha", "topology_evidence"):
        if boundary.get(field) != expected[field]:
            errors.append(f"boundary_{field}_mismatch")
    errors.extend(file_errors(boundary.get("support_mask"), "boundary:support_mask"))
    errors.extend(file_errors(boundary.get("inward_alpha"), "boundary:inward_alpha"))
    if record.get("inputs", {}).get("repair_mask", {}).get("sha256") != boundary.get("support_mask", {}).get("sha256"):
        errors.append("repair_mask_not_exact_boundary_support")

    completed = journal.get("state") == "COMPLETED"
    if completed:
        if boundary.get("outcome_state") != "EXACT_BASE_CANDIDATE_MEASURED_SEAM_ACCEPTED":
            errors.append("completed_boundary_outcome_state_invalid")
        visual = boundary.get("exact_base_visual_boundary")
        exterior = boundary.get("exterior_result")
        no_change = boundary.get("no_change_result")
        seam = boundary.get("timed_seam_review")
        visual_ref = visual.get("evidence") if isinstance(visual, dict) else None
        visual_ref_errors, visual_payload = load_json_ref(visual_ref, "visual_boundary_evidence")
        errors.extend(visual_ref_errors)
        base_hash = record.get("inputs", {}).get("base_raster", {}).get("sha256")
        candidates = record.get("outputs", {}).get("candidates", [])
        candidate_hash = candidates[0].get("sha256") if len(candidates) == 1 else None
        if not isinstance(visual, dict) or visual.get("state") != "EXACT_BASE_AND_CANDIDATE_MEASURED" or visual.get("base_sha256") != base_hash or visual.get("candidate_sha256") != candidate_hash:
            errors.append("exact_base_visual_boundary_binding_invalid")
        exact_images = visual_payload.get("exact_images", {}) if isinstance(visual_payload, dict) else {}
        if visual_payload is None or exact_images.get("base_raster", {}).get("sha256") != base_hash or exact_images.get("candidate_raster", {}).get("sha256") != candidate_hash or exact_images.get("support_mask", {}).get("sha256") != boundary.get("support_mask", {}).get("sha256") or exact_images.get("inward_alpha", {}).get("sha256") != boundary.get("inward_alpha", {}).get("sha256"):
            errors.append("exact_base_visual_boundary_payload_invalid")
        if not isinstance(exterior, dict) or exterior != {"changed_pixels": 0, "max_abs_channel_difference": 0, "exact": True}:
            errors.append("exterior_result_not_exact_zero")
        if not isinstance(no_change, dict) or not isinstance(no_change.get("requested"), bool) or not isinstance(no_change.get("candidate_byte_identical"), bool):
            errors.append("no_change_result_invalid")
        elif no_change["requested"] != (candidate_hash == base_hash) or no_change["candidate_byte_identical"] != (candidate_hash == base_hash):
            errors.append("no_change_result_hash_contradiction")
        if not isinstance(seam, dict):
            errors.append("timed_seam_review_missing")
        else:
            session_ref_errors, session = load_json_ref(seam.get("session"), "timed_seam_review_session")
            errors.extend(session_ref_errors)
            assertions = seam.get("assertions", {})
            if seam.get("status") != "COMPLETED" or seam.get("decision") != "ACCEPT_BOUNDARY" or not seam.get("reviewer_id"):
                errors.append("timed_seam_review_state_invalid")
            if not isinstance(seam.get("active_minutes"), (int, float)) or seam.get("active_minutes", 0) <= 0:
                errors.append("timed_seam_review_minutes_invalid")
            if assertions != {"boundary": True, "causality": True, "protected_semantics": True, "lettering_clearance": True}:
                errors.append("timed_seam_review_assertions_incomplete")
            if session is None:
                errors.append("timed_seam_review_session_missing")
            else:
                errors.extend(f"timed_seam_review_session:{item}" for item in validate_session(session))
                if not isinstance(visual_ref, dict) or session.get("subjects") != [visual_ref]:
                    errors.append("timed_seam_review_subject_mismatch")
                summary = session.get("summary", {})
                if seam.get("active_minutes") != summary.get("human_minutes") or seam.get("reviewer_id") != session.get("reviewer_id"):
                    errors.append("timed_seam_review_summary_mismatch")
                fixture = record.get("synthetic_validation_fixture") is True
                if session.get("validation_fixture") is not fixture or summary.get("review_evidence_eligible") is not (not fixture):
                    errors.append("timed_seam_review_eligibility_mismatch")
                decisions = session.get("events", [{}])[-1].get("data", {}).get("decisions", [])
                expected_assertions = [{"id": name, "passed": True} for name in ("boundary", "causality", "protected_semantics", "lettering_clearance")]
                visual_record_id = visual_ref.get("record_id") if isinstance(visual_ref, dict) else None
                if len(decisions) != 1 or decisions[0].get("subject_record_id") != visual_record_id or decisions[0].get("accepted") is not True or decisions[0].get("hard_assertions") != expected_assertions:
                    errors.append("timed_seam_review_decision_mismatch")
    elif journal.get("state") == "FAILED_RECONCILED":
        if boundary.get("outcome_state") != "PROVIDER_FAILED_NO_CANDIDATE":
            errors.append("failed_boundary_outcome_state_invalid")
        for field in ("exact_base_visual_boundary", "exterior_result", "no_change_result", "timed_seam_review"):
            if boundary.get(field) is not None:
                errors.append(f"failed_boundary_fabricated_{field}")
    return sorted(set(errors))


def boundary_incident_errors(record: dict, journal: dict, cost_ledger: dict) -> list[str]:
    """Unknown outcomes may carry no claimed repair-boundary outcome evidence."""
    errors: list[str] = []
    if record.get("schema_version") != "1.1":
        errors.append("boundary_incident_schema_invalid")
    legacy = copy.deepcopy(record)
    legacy["schema_version"] = "1.0"
    errors.extend(f"base:{item}" for item in incident_errors(legacy, journal, cost_ledger))
    present = sorted(OUTCOME_FIELDS.intersection(record))
    if present:
        errors.append("unknown_incident_contains_boundary_outcome_fields:" + ",".join(present))
    return sorted(set(errors))
