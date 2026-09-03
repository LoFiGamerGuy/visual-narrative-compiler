"""Advance the append-only CH05 cost/time ledger through the newest built-in runs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r33.json"
TARGET_EXECUTION = ROOT / "production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-execution-r1.json"
FLAT_EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-execution-manifest-r1.json"
FLAT_CROPS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-crops-r1.json"
TEXT_EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-execution-manifest-r1.json"
OUTPUT = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r34.json"
CURRENT_SOURCES = [TARGET_EXECUTION, FLAT_EXECUTION, FLAT_CROPS, TEXT_EXECUTION]
APPENDED = [
    "ch05_premium_cel_targeted_repair_trio_execution_r1",
    "ch05_flat_graphic_gouache_complete_chapter_execution_r1",
    "ch05_reduced_palette_text_control_complete_chapter_execution_r1",
]
UNAVAILABLE = ["model", "endpoint", "provider_request_ids", "usage", "monetary_cost_usd", "deterministic_seed"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def bind(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def require(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise ValueError(f"{label}: expected {expected!r}, got {actual!r}")


def unavailable_metadata() -> dict[str, None]:
    return {field: None for field in UNAVAILABLE}


def main() -> int:
    prior = load(PRIOR)
    target = load(TARGET_EXECUTION)
    flat = load(FLAT_EXECUTION)
    flat_crops = load(FLAT_CROPS)
    text = load(TEXT_EXECUTION)

    ts = target["summary"]
    require(
        (
            ts.get("standalone_outputs"),
            ts.get("comic_panel_plans"),
            ts.get("authorized_reference_uses"),
            ts.get("unique_timing_batches"),
            ts.get("overlap_adjusted_tool_call_wall_seconds"),
            ts.get("per_output_elapsed_seconds_available"),
        ),
        (3, 3, 6, 1, 169.0, 0),
        "targeted-repair accounting facts",
    )
    target_batch = target["timing_batches"][0]
    require((target_batch.get("wall_seconds"), len(target_batch.get("member_panel_ids", []))), (169.0, 3), "repair batch")

    fs = flat["summary"]
    require(
        (
            fs.get("sequence_outputs"),
            fs.get("comic_panel_plans_requested"),
            fs.get("planned_comic_panel_crops"),
            fs.get("authorized_reference_uses"),
            fs.get("per_output_wall_seconds_available"),
            fs.get("known_per_output_tool_wall_seconds_sum"),
            fs.get("concurrent_pair_batch_wall_seconds"),
            fs.get("non_overlap_adjusted_observed_total_seconds"),
            fs.get("actual_end_to_end_wall_seconds"),
        ),
        (11, 50, 50, 23, 9, 1063.921, 227.068, 1290.989, None),
        "flat-gouache accounting facts",
    )
    require(
        (
            flat_crops.get("summary", {}).get("planned_crops"),
            flat_crops.get("summary", {}).get("manual_gutter_overrides"),
            flat_crops.get("summary", {}).get("complete_plan_coverage"),
        ),
        (50, 1, True),
        "flat-gouache crop facts",
    )

    xs = text["summary"]
    require(
        (
            xs.get("sequence_outputs"),
            xs.get("comic_panel_plans_requested"),
            xs.get("planned_comic_panel_crops"),
            xs.get("authorized_reference_uses"),
            xs.get("reference_uploads"),
            xs.get("per_output_wall_seconds_available"),
            xs.get("known_individual_tool_wall_seconds_sum"),
            xs.get("concurrent_batch_count"),
            xs.get("non_overlap_observed_arithmetic_seconds"),
            xs.get("actual_end_to_end_wall_seconds"),
        ),
        (11, 50, 50, 0, 0, 6, 568.3, 2, 1027.652, None),
        "text-control accounting facts",
    )
    require([batch.get("wall_seconds") for batch in text["timing_batches"]], [300.467, 158.885], "text batch walls")

    for name, summary in (("target", ts), ("flat", fs), ("text", xs)):
        require(summary.get("direct_paid_provider_api_calls"), 0, f"{name} direct-paid calls")
        if "cost_total_usd" in summary:
            require(summary["cost_total_usd"], None, f"{name} built-in monetary cost")
    require(ts.get("paid_spend_usd"), 0.0, "target direct-paid spend")

    rows = list(prior["local_zero_external_cost_evidence"])
    rows.extend(
        {"milestone": name, "external_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"}
        for name in APPENDED
    )
    metadata = unavailable_metadata()
    activities = [
        {
            "activity_id": "ch05_premium_cel_targeted_repair_trio_r1",
            "activity_class": "targeted_repair_trio",
            "sequence_tool_calls": 3,
            "raster_outputs": 3,
            "comic_panel_plans": 3,
            "comic_panel_plan_crops": 0,
            "authorized_reference_uses": 6,
            "reference_uploads": None,
            "manual_gutter_overrides": 0,
            "timing": {
                "known_individual_wall_seconds_sum": None,
                "known_individual_output_count": 0,
                "concurrent_batch_walls_seconds": [169.0],
                "concurrent_batch_wall_seconds_sum": 169.0,
                "non_overlap_observed_arithmetic_seconds": 169.0,
                "actual_end_to_end_wall_seconds": None,
                "scope_note": "One caller-observed concurrent batch wall; no trustworthy individual-output or full-workflow stopwatch.",
            },
            "direct_paid_provider_api_calls": 0,
            "direct_paid_api_or_cloud_spend_usd": "0.000000",
            **metadata,
        },
        {
            "activity_id": "ch05_complete_chapter_flat_graphic_gouache_r1",
            "activity_class": "complete_chapter_style_arm",
            "sequence_tool_calls": 11,
            "raster_outputs": 11,
            "comic_panel_plans": 50,
            "comic_panel_plan_crops": 50,
            "authorized_reference_uses": 23,
            "reference_uploads": None,
            "manual_gutter_overrides": 1,
            "timing": {
                "known_individual_wall_seconds_sum": 1063.921,
                "known_individual_output_count": 9,
                "concurrent_batch_walls_seconds": [227.068],
                "concurrent_batch_wall_seconds_sum": 227.068,
                "non_overlap_observed_arithmetic_seconds": 1290.989,
                "actual_end_to_end_wall_seconds": None,
                "scope_note": "Nine individual walls plus one S10/S11 concurrent-pair wall; parallel caller lanes lacked a shared stopwatch.",
            },
            "direct_paid_provider_api_calls": 0,
            "direct_paid_api_or_cloud_spend_usd": "0.000000",
            **metadata,
        },
        {
            "activity_id": "ch05_complete_chapter_reduced_palette_text_control_r1",
            "activity_class": "complete_chapter_text_only_control_arm",
            "sequence_tool_calls": 11,
            "raster_outputs": 11,
            "comic_panel_plans": 50,
            "comic_panel_plan_crops": 50,
            "authorized_reference_uses": 0,
            "reference_uploads": 0,
            "manual_gutter_overrides": 0,
            "timing": {
                "known_individual_wall_seconds_sum": 568.3,
                "known_individual_output_count": 6,
                "concurrent_batch_walls_seconds": [300.467, 158.885],
                "concurrent_batch_wall_seconds_sum": 459.352,
                "non_overlap_observed_arithmetic_seconds": 1027.652,
                "actual_end_to_end_wall_seconds": None,
                "scope_note": "Six individual walls plus two concurrent-batch walls; parallel caller lanes lacked a shared stopwatch.",
            },
            "direct_paid_provider_api_calls": 0,
            "direct_paid_api_or_cloud_spend_usd": "0.000000",
            **metadata,
        },
    ]

    prior_cumulative = prior["built_in_product_activity"]["cumulative_complete_chapter_style_arms"]
    cumulative = {
        "included_arms": [
            *prior_cumulative["included_arms"],
            "ch05_complete_chapter_flat_graphic_gouache_r1",
            "ch05_complete_chapter_reduced_palette_text_control_r1",
        ],
        "sequence_tool_calls": prior_cumulative["sequence_tool_calls"] + 22,
        "raster_outputs": prior_cumulative["raster_outputs"] + 22,
        "comic_panel_plan_crops": prior_cumulative["comic_panel_plan_crops"] + 100,
        "authorized_reference_uses": prior_cumulative["authorized_reference_uses"] + 23,
        "unique_authorized_reference_hashes": 3,
        "direct_paid_provider_api_calls": 0,
        "direct_paid_api_or_cloud_spend_usd": "0.000000",
        **metadata,
        "combined_timing_seconds": None,
        "combined_actual_end_to_end_wall_seconds": None,
        "timing_combination_status": "PROHIBITED_INCOMPARABLE_SCOPES",
    }
    timing_accounting = {
        "prior_three_complete_arms": {
            "overlap_adjusted_tool_call_wall_seconds": prior_cumulative["overlap_adjusted_tool_call_wall_seconds"],
            "scope": "Historical r33 aggregate for alt-graphic, clear-line-watercolor, and premium-cel only.",
        },
        "targeted_repair_trio": activities[0]["timing"],
        "flat_graphic_gouache_complete_arm": activities[1]["timing"],
        "reduced_palette_text_control_complete_arm": activities[2]["timing"],
        "all_activity_actual_end_to_end_wall_seconds": None,
        "combination_rule": "Do not add historical overlap-adjusted walls, individual sums, concurrent-batch walls, or non-overlap arithmetic into a synthetic total.",
    }

    document = {
        **prior,
        "schema_version": "1.33",
        "record_id": "ng-ch05-production-cost-ledger-r34",
        "supersedes": {"record_id": prior["record_id"], **bind(PRIOR)},
        "local_zero_external_cost_evidence": rows,
        "revision_summary": {
            "prior_local_milestones": len(prior["local_zero_external_cost_evidence"]),
            "appended_local_milestones": len(APPENDED),
            "total_local_milestones": len(rows),
            "external_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        },
        "built_in_product_activity": {
            **prior["built_in_product_activity"],
            "evidence_sources": [
                *prior["built_in_product_activity"]["evidence_sources"],
                *[bind(path) for path in CURRENT_SOURCES],
            ],
            "prior_revision_evidence_sources": prior["built_in_product_activity"]["evidence_sources"],
            "current_revision_evidence_sources": [bind(path) for path in CURRENT_SOURCES],
            "current_revision_activities": activities,
            "cumulative_complete_chapter_style_arms": cumulative,
            "timing_accounting": timing_accounting,
            "unavailable_fields": UNAVAILABLE,
            "accounting_notes": [
                "Panel crops are deterministic local derivatives, not generation outputs or provider calls.",
                "Authorized reference-use counts are not monetary costs; the built-in product did not disclose monetary cost.",
                "Flat-gouache has one hash-pinned manual gutter override; it changes local crop accounting only.",
            ],
        },
        "boundary": (
            "Append-only accounting from r33. Direct paid API/cloud calls and spend remain 0/$0; built-in monetary cost remains "
            "unavailable/null, not zero. Targeted-repair, flat-gouache, and text-control timing scopes remain separate: known "
            "individual sums, concurrent-batch walls, non-overlap arithmetic, and unavailable actual end-to-end time are not "
            "combined. G07 remains separate. No candidate acceptance, rights clearance, or exact-production-base decision is implied."
        ),
    }
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "output": OUTPUT.relative_to(ROOT).as_posix(),
                "sha256": sha256(OUTPUT),
                "milestones": len(rows),
                "current_outputs": sum(item["raster_outputs"] for item in activities),
                "complete_arm_outputs": cumulative["raster_outputs"],
                "complete_arm_crops": cumulative["comic_panel_plan_crops"],
                "combined_timing_seconds": None,
                "direct_paid_spend_usd": "0.000000",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
