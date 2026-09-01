"""Validate that comic input templates fail closed."""
from __future__ import annotations

import json
from pathlib import Path

from comic_input_gate import ROOT, base_raster_errors, repair_mask_errors


BASE = ROOT / "config/record-templates/comic-panel-base-raster-approval-v1.json"
MASK = ROOT / "config/record-templates/comic-panel-repair-mask-review-v1.json"


def main() -> None:
    base = json.loads(BASE.read_text(encoding="utf-8"))
    mask = json.loads(MASK.read_text(encoding="utf-8"))
    base_errors = base_raster_errors(base, "ng-ch05-sc01-p036", "ng-ch05-sc01-p036-plan-r1", require_external=True)
    mask_errors = repair_mask_errors(mask, "ng-ch05-sc01-p036", "ng-ch05-sc01-p036-plan-r1", "base-r1", require_external=True)
    assert "base_raster_state_not_approved" in base_errors
    assert "authorized_timed_human_review_missing" in base_errors
    assert "external_upload_not_authorized" in base_errors
    assert "repair_mask_state_not_approved" in mask_errors
    assert "mask_context_or_seam_review_missing" in mask_errors
    assert "lettering_safe_zone_overlap" in mask_errors
    assert "external_upload_not_authorized" in mask_errors
    assert not any(value for value in (base["raster"]["path"], mask["mask"]["path"]))
    print(f"0 failures, 0 warnings (comic input gate fails closed: base={len(base_errors)} mask={len(mask_errors)} reasons)")


if __name__ == "__main__":
    main()
