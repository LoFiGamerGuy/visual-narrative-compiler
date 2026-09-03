"""Compile the hash-verified reduced-palette text-control CH05 assembly."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from compile_ch05_complete_chapter_assembly import gutter_after, target_width
from validate_ch05_complete_chapter_reduced_palette_text_control_crops import (
    validate as validate_crops,
)

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
CROP_MANIFEST = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-crops-r1.json"
SPLIT_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/panels/reduced-palette-text-control-panel-split-report-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-assembly-r1.json"
CANDIDATE_PREFIX = "reduced-palette-text-control-r1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    plans = sorted(json.loads(PLAN.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    crop_manifest = json.loads(CROP_MANIFEST.read_text(encoding="utf-8"))
    split_report = json.loads(SPLIT_REPORT.read_text(encoding="utf-8"))
    errors = validate_crops(crop_manifest, split_report, verify_files=True)
    if errors:
        raise ValueError("reduced-palette crop/split validation failed: " + "; ".join(errors))
    report_panels = split_report["panels"]
    expected_ids = [plan["panel_id"] for plan in plans]
    if [row["panel_id"] for row in report_panels] != expected_ids:
        raise ValueError("split report is not the exact canonical 50-panel CH05 order")

    entries: list[dict[str, Any]] = []
    for plan, split in zip(plans, report_panels, strict=True):
        output = split["output"]
        source_path = ROOT / output["path"]
        if not source_path.is_file() or sha256(source_path) != output["sha256"]:
            raise ValueError(f"split output missing or hash mismatch: {output['path']}")
        entries.append({
            "order": plan["display_order"],
            "panel_id": plan["panel_id"],
            "candidate_id": f"{CANDIDATE_PREFIX}-p{plan['display_order']:03d}",
            "sequence_id": split["sequence_id"],
            "source": {"path": output["path"], "sha256": output["sha256"], "width": output["width"], "height": output["height"]},
            "layout": {"target_width": target_width(plan), "alignment": "center", "gutter_after": gutter_after(plan)},
            "animation_shot_plan": None,
            "e_conte": None,
        })

    manifest = {
        "record_type": "ComicChapterProductionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-reduced-palette-text-control-assembly-r1",
        "state": "COMPLETE_READING_DRAFT_READY_FOR_ASSEMBLY_UNACCEPTED",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "chapter_complete": True,
        "animation_shot_plan": None,
        "e_conte": None,
        "comic_panel_plan_collection": {"path": PLAN.relative_to(ROOT).as_posix(), "sha256": sha256(PLAN)},
        "crop_manifest": {"path": CROP_MANIFEST.relative_to(ROOT).as_posix(), "sha256": sha256(CROP_MANIFEST)},
        "split_report": {"path": SPLIT_REPORT.relative_to(ROOT).as_posix(), "sha256": sha256(SPLIT_REPORT), "repository_state": "IGNORED_LOCAL_REVIEW_ARTIFACT"},
        "canvas": {"width": 1200, "side_margin": 80, "background": "#11151a", "top_gutter": 72, "phone_width": 390, "phone_viewport_height": 844},
        "entries": entries,
        "owner_disposition": {"accepted": None, "commercial_rights_clearance": None, "exact_production_base": None},
        "boundary": "Complete local review assembly only; source pixels remain ignored local artifacts and acceptance, commercial-rights clearance, and exact production-base selection remain null.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"entries": len(entries), "output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), "split_report_sha256": sha256(SPLIT_REPORT)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
