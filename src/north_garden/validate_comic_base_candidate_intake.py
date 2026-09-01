"""Validate local-only candidate intake without promoting deterministic controls."""
from __future__ import annotations

import json
from pathlib import Path

from comic_input_gate import base_raster_errors
from prepare_comic_base_candidate import CandidateIntakeError, ROOT, prepare_candidate


RESULT = ROOT / "experiments/results/ch05-p033-p038-sequence-layout-control-r1.json"


def main() -> int:
    failures = []
    sequence = json.loads(RESULT.read_text(encoding="utf-8"))
    records = []
    for panel in sequence["panels"]:
        candidate_id = f"ng-{panel['panel_id']}-layout-control-candidate-r2".replace("ng-ng-", "ng-")
        out = prepare_candidate(
            panel_id=panel["panel_id"],
            raster_path=ROOT / panel["image"]["path"],
            candidate_id=candidate_id,
        )
        record = json.loads(out.read_text(encoding="utf-8"))
        records.append(record)
        if record["raster"]["sha256"] != panel["image"]["sha256"]:
            failures.append(f"candidate hash mismatch: {panel['panel_id']}")
        if record["review"]["human_minutes"] is not None or record["review"]["accepted_as_base"]:
            failures.append(f"candidate review promoted: {panel['panel_id']}")
        if record["permissions"]["local_repair_input_authorized"] or record["permissions"]["external_upload_authorized"]:
            failures.append(f"candidate permission promoted: {panel['panel_id']}")
        if record["approval_eligibility"]["eligible"] is not False:
            failures.append(f"layout control not marked permanently ineligible: {panel['panel_id']}")
        gate_errors = base_raster_errors(record, panel["panel_id"], panel["plan_revision_id"])
        if not gate_errors or "base_raster_state_not_approved" not in gate_errors:
            failures.append(f"candidate passed or bypassed base approval gate: {panel['panel_id']}")

    first = records[0]
    try:
        prepare_candidate(
            panel_id=first["comic_panel_plan"]["panel_id"],
            raster_path=ROOT / "production/comic/ch05-sc01-panel-plans-v1.json",
            candidate_id="invalid-non-image",
        )
        failures.append("non-image candidate intake passed")
    except CandidateIntakeError:
        pass
    try:
        prepare_candidate(
            panel_id="unknown-panel",
            raster_path=ROOT / first["raster"]["path"],
            candidate_id="invalid-panel",
        )
        failures.append("unknown panel candidate intake passed")
    except CandidateIntakeError:
        pass

    for failure in failures:
        print(f"failure: {failure}")
    if failures:
        return 1
    print("0 failures, 0 warnings (6 candidates hash-matched; 0 approvals/uploads; invalid image/panel rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
