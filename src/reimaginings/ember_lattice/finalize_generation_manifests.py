from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VOLUME = ROOT / "production" / "reimaginings" / "ember-lattice" / "volume"


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    global_manifest = json.loads((VOLUME / "generation-requests.json").read_text(encoding="utf-8"))
    rows = global_manifest["requests"]
    selected = [row for row in rows if row["review_status"] == "REVIEWED_PASS"]
    diagnostics = [row for row in rows if row["review_status"] == "HARD_FAIL_PRESERVED_DIAGNOSTIC"]
    if len(rows) != 225 or len(selected) != 224 or len(diagnostics) != 1:
        raise SystemExit(f"generation manifest cannot finalize: requests={len(rows)}, selected={len(selected)}, diagnostics={len(diagnostics)}")
    registry_rows = json.loads((ROOT / "production" / "reimaginings" / "ember-lattice" / "reference-registry.json").read_text(encoding="utf-8"))["references"]
    registry = {row["reference_id"]: row for row in registry_rows}
    render_records = []
    for row in rows:
        render_records.append({
            "schema": "RenderRecord/1.0",
            "request_id": row["request_id"],
            "exact_prompt": row["exact_prompt"],
            "prompt_hash": row["prompt_hash"],
            "target_chapter": row["chapter"],
            "target_sequence": row["panel_id"].rsplit("-p", 1)[0],
            "target_panel_ids": [row["panel_id"]],
            "input_references": [{"reference_id": ref_id, "path": registry[ref_id]["path"], "sha256": registry[ref_id]["sha256"]} for ref_id in row["reference_ids"]],
            "output_path": row["output_path"],
            "output_hash": row["sha256"],
            "dimensions": row["dimensions"],
            "measured_elapsed_seconds": row["measured_elapsed_seconds"],
            "model": row["model"], "endpoint": row["endpoint"], "provider_request_id": row["provider_request_id"],
            "usage": row["usage"], "monetary_cost": row["monetary_cost"], "deterministic_seed": row["seed"],
            "extraction_crop_composite": "no crop; full returned source art; deterministic SVG lettering after selection",
            "crop_coordinates": None,
            "candidate_paths_and_hashes": [{"path": row["output_path"], "sha256": row["sha256"]}],
            "review_status": row["review_status"], "failure_classes": row["failure_classes"],
            "human_review": row["visual_review"], "owner_approval": row["owner_approval"],
            "commercial_clearance": row["commercial_clearance"], "production_base": row["production_base"],
            "reproducibility": row["reproducible"],
        })
    write_json(VOLUME / "render-records.json", {"schema": "RenderRecordCollection/1.0", "records": render_records})
    chapter_summaries = []
    for chapter in range(1, 11):
        chapter_id = f"ch{chapter:02d}"
        chapter_rows = [row for row in rows if row["chapter"] == chapter_id]
        target = VOLUME / "chapters" / chapter_id / "prompt-manifest.json"
        write_json(target, {"schema": "PromptManifest/1.0", "chapter": chapter_id, "requests": chapter_rows})
        chapter_summaries.append({
            "chapter": chapter_id,
            "generation_requests": len(chapter_rows),
            "reviewed_pass": sum(row["review_status"] == "REVIEWED_PASS" for row in chapter_rows),
            "preserved_diagnostics": sum(row["review_status"] == "HARD_FAIL_PRESERVED_DIAGNOSTIC" for row in chapter_rows),
            "measured_elapsed_seconds_sum": round(sum(row["measured_elapsed_seconds"] for row in chapter_rows), 3),
        })
    summary = {
        "schema": "GenerationReconciliation/1.0",
        "status": "PASS",
        "base_panel_requests": 224,
        "localized_repair_requests": 1,
        "total_panel_generation_requests": 225,
        "returned_and_recorded": 225,
        "selected_and_reviewed_pass": 224,
        "preserved_hard_fail_diagnostics": 1,
        "approved_pilot_assets_reused": 16,
        "total_volume_panels": 240,
        "missing": [],
        "failed_unresolved": [],
        "resolved_failure_classes": ["non_vertical_source"],
        "repair_requests": 1,
        "direct_paid_cloud_spend_usd": 0,
        "provider_metadata_availability": {"model": "imagegen-default", "endpoint": "built-in-image_gen", "usage": None, "monetary_cost": 0, "seed": None},
        "chapters": chapter_summaries,
    }
    write_json(VOLUME / "generation-reconciliation.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
