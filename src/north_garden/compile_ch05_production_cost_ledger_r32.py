"""Advance CH05 cost/timing evidence append-only for the clear-line chapter arm."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r31.json"
CLEAR_EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-execution-manifest-r1.json"
CLEAR_CROPS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-crops-r1.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r32.json"
APPENDED = [
    "ch05_clear_line_watercolor_execution_renderrecords_r1",
    "ch05_clear_line_watercolor_deterministic_crop_and_assembly_r1",
    "ch05_clear_line_watercolor_agent_triage_r1",
    "ch05_three_route_measured_comparison_r1",
    "ch05_three_route_owner_review_start_r1",
]
UNAVAILABLE = (
    "model",
    "endpoint",
    "provider_request_ids",
    "usage",
    "monetary_cost_usd",
    "deterministic_seed",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    execution = json.loads(CLEAR_EXECUTION.read_text(encoding="utf-8"))
    crops = json.loads(CLEAR_CROPS.read_text(encoding="utf-8"))
    prior_activity = prior["built_in_product_activity"]
    clear_summary = execution["summary"]
    crop_summary = crops["summary"]

    milestones = list(prior["local_zero_external_cost_evidence"])
    milestones.extend(
        {
            "milestone": name,
            "external_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        }
        for name in APPENDED
    )

    clear_activity = {
        "arm_id": "ch05_complete_chapter_clear_line_watercolor_r1",
        "sequence_tool_calls": clear_summary["sequence_outputs"],
        "raster_outputs": clear_summary["sequence_outputs"],
        "comic_panel_plan_crops": crop_summary["planned_crops"],
        "authorized_reference_uses": clear_summary["authorized_reference_uses"],
        "unique_authorized_reference_hashes": 3,
        "unique_timing_batches": clear_summary["unique_timing_batches"],
        "overlap_adjusted_tool_call_wall_seconds": clear_summary["overlap_adjusted_tool_call_wall_seconds"],
        "timing_scope": clear_summary["timing_scope"],
        "model": None,
        "endpoint": None,
        "provider_request_ids": None,
        "usage": None,
        "monetary_cost_usd": None,
        "deterministic_seed": None,
    }
    cumulative_activity = {
        "included_arms": ["ch05_complete_chapter_alt_graphic_r1", clear_activity["arm_id"]],
        "sequence_tool_calls": prior_activity["sequence_tool_calls"] + clear_activity["sequence_tool_calls"],
        "raster_outputs": prior_activity["raster_outputs"] + clear_activity["raster_outputs"],
        "comic_panel_plan_crops": prior_activity["comic_panel_plan_crops"] + clear_activity["comic_panel_plan_crops"],
        "authorized_reference_uses": prior_activity["authorized_reference_uses"] + clear_activity["authorized_reference_uses"],
        "unique_authorized_reference_hashes": 3,
        "unique_timing_batches": 6 + clear_activity["unique_timing_batches"],
        "overlap_adjusted_tool_call_wall_seconds": round(
            prior_activity["overlap_adjusted_tool_call_wall_seconds"]
            + clear_activity["overlap_adjusted_tool_call_wall_seconds"],
            1,
        ),
        "direct_paid_provider_api_calls": 0,
        "direct_paid_api_or_cloud_spend_usd": "0.000000",
        "model": None,
        "endpoint": None,
        "provider_request_ids": None,
        "usage": None,
        "monetary_cost_usd": None,
        "deterministic_seed": None,
    }
    doc = {
        **prior,
        "schema_version": "1.31",
        "record_id": "ng-ch05-production-cost-ledger-r32",
        "supersedes": {
            "record_id": prior["record_id"],
            "path": PRIOR.relative_to(ROOT).as_posix(),
            "sha256": sha256(PRIOR),
        },
        "local_zero_external_cost_evidence": milestones,
        "revision_summary": {
            "prior_local_milestones": len(prior["local_zero_external_cost_evidence"]),
            "appended_local_milestones": len(APPENDED),
            "total_local_milestones": len(milestones),
            "external_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        },
        "built_in_product_activity": {
            "product": "OpenAI built-in ImageGen in Codex",
            "evidence_sources": [
                {"path": CLEAR_EXECUTION.relative_to(ROOT).as_posix(), "sha256": sha256(CLEAR_EXECUTION)},
                {"path": CLEAR_CROPS.relative_to(ROOT).as_posix(), "sha256": sha256(CLEAR_CROPS)},
            ],
            "current_revision_clear_line_watercolor": clear_activity,
            "cumulative_complete_chapter_style_arms": cumulative_activity,
            "unavailable_fields": list(UNAVAILABLE),
        },
        "boundary": (
            "Append-only accounting. The clear-line watercolor continuation and the cumulative alternate+clear "
            "totals count authorized built-in ImageGen activity separately from the disabled direct paid API/cloud "
            "domain. Direct paid requests/uploads/spend remain 0/0/$0; built-in model, endpoint, provider request "
            "IDs, usage, seed, and monetary cost are unavailable/null, not zero. G07 remains separate."
        ),
    }
    OUTPUT.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output": OUTPUT.relative_to(ROOT).as_posix(),
                "sha256": sha256(OUTPUT),
                "total_local_milestones": len(milestones),
                "clear_line_wall_seconds": clear_activity["overlap_adjusted_tool_call_wall_seconds"],
                "cumulative_wall_seconds": cumulative_activity["overlap_adjusted_tool_call_wall_seconds"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
