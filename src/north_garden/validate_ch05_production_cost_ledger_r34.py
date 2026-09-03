"""Validate append-only CH05 production cost/timing ledger r34."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r34.json"
PRIOR = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r33.json"
TARGET_EXECUTION = ROOT / "production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-execution-r1.json"
FLAT_EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-execution-manifest-r1.json"
FLAT_CROPS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-crops-r1.json"
TEXT_EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-execution-manifest-r1.json"
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


def validate(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    prior = load(PRIOR)
    target = load(TARGET_EXECUTION)
    flat = load(FLAT_EXECUTION)
    flat_crops = load(FLAT_CROPS)
    text = load(TEXT_EXECUTION)
    prior_rows = prior["local_zero_external_cost_evidence"]
    rows = document.get("local_zero_external_cost_evidence", [])

    check(
        document.get("record_type") == "ProductionCostLedger"
        and document.get("schema_version") == "1.33"
        and document.get("record_id") == "ng-ch05-production-cost-ledger-r34",
        "identity",
    )
    check(document.get("supersedes") == {"record_id": prior["record_id"], **bind(PRIOR)}, "supersedes binding")
    check(document.get("prior_record_rewritten") is False, "prior rewrite boundary")
    check(rows[: len(prior_rows)] == prior_rows, "append-only prefix")
    suffix = [
        {"milestone": name, "external_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"}
        for name in APPENDED
    ]
    check(rows[len(prior_rows) :] == suffix, "appended evidence-only suffix")
    check(
        document.get("revision_summary")
        == {
            "prior_local_milestones": 106,
            "appended_local_milestones": 3,
            "total_local_milestones": 109,
            "external_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        }
        and len(rows) == 109,
        "revision summary/denominator",
    )

    activity = document.get("built_in_product_activity", {})
    check(activity.get("product") == "OpenAI built-in ImageGen in Codex", "product")
    check(
        activity.get("prior_revision_evidence_sources") == prior["built_in_product_activity"]["evidence_sources"],
        "prior evidence-source preservation",
    )
    check(activity.get("current_revision_evidence_sources") == [bind(path) for path in CURRENT_SOURCES], "source hash bindings")
    check(
        activity.get("evidence_sources")
        == [*prior["built_in_product_activity"]["evidence_sources"], *[bind(path) for path in CURRENT_SOURCES]],
        "append-only cumulative evidence sources",
    )
    check(
        activity.get("current_revision_premium_cel") == prior["built_in_product_activity"]["current_revision_premium_cel"],
        "prior current-revision detail preservation",
    )

    activities = activity.get("current_revision_activities", [])
    check(len(activities) == 3, "activity denominator")
    by_id = {item.get("activity_id"): item for item in activities if isinstance(item, dict)}
    target_row = by_id.get("ch05_premium_cel_targeted_repair_trio_r1", {})
    flat_row = by_id.get("ch05_complete_chapter_flat_graphic_gouache_r1", {})
    text_row = by_id.get("ch05_complete_chapter_reduced_palette_text_control_r1", {})

    check(
        (
            target_row.get("activity_class"),
            target_row.get("sequence_tool_calls"),
            target_row.get("raster_outputs"),
            target_row.get("comic_panel_plans"),
            target_row.get("comic_panel_plan_crops"),
            target_row.get("authorized_reference_uses"),
            target_row.get("reference_uploads"),
            target_row.get("manual_gutter_overrides"),
        )
        == ("targeted_repair_trio", 3, 3, 3, 0, 6, None, 0),
        "targeted-repair counts",
    )
    check(
        (
            flat_row.get("activity_class"),
            flat_row.get("sequence_tool_calls"),
            flat_row.get("raster_outputs"),
            flat_row.get("comic_panel_plans"),
            flat_row.get("comic_panel_plan_crops"),
            flat_row.get("authorized_reference_uses"),
            flat_row.get("reference_uploads"),
            flat_row.get("manual_gutter_overrides"),
        )
        == ("complete_chapter_style_arm", 11, 11, 50, 50, 23, None, 1),
        "flat-gouache counts/manual override",
    )
    check(
        (
            text_row.get("activity_class"),
            text_row.get("sequence_tool_calls"),
            text_row.get("raster_outputs"),
            text_row.get("comic_panel_plans"),
            text_row.get("comic_panel_plan_crops"),
            text_row.get("authorized_reference_uses"),
            text_row.get("reference_uploads"),
            text_row.get("manual_gutter_overrides"),
        )
        == ("complete_chapter_text_only_control_arm", 11, 11, 50, 50, 0, 0, 0),
        "text-control counts/zero-reference boundary",
    )

    expected_timings = {
        "ch05_premium_cel_targeted_repair_trio_r1": (None, 0, [169.0], 169.0, 169.0, None),
        "ch05_complete_chapter_flat_graphic_gouache_r1": (1063.921, 9, [227.068], 227.068, 1290.989, None),
        "ch05_complete_chapter_reduced_palette_text_control_r1": (
            568.3,
            6,
            [300.467, 158.885],
            459.352,
            1027.652,
            None,
        ),
    }
    for activity_id, expected in expected_timings.items():
        timing = by_id.get(activity_id, {}).get("timing", {})
        actual = (
            timing.get("known_individual_wall_seconds_sum"),
            timing.get("known_individual_output_count"),
            timing.get("concurrent_batch_walls_seconds"),
            timing.get("concurrent_batch_wall_seconds_sum"),
            timing.get("non_overlap_observed_arithmetic_seconds"),
            timing.get("actual_end_to_end_wall_seconds"),
        )
        check(actual == expected, f"timing scopes: {activity_id}")
        check(isinstance(timing.get("scope_note"), str) and "stopwatch" in timing["scope_note"], f"timing scope note: {activity_id}")

    for row in activities:
        check(
            row.get("direct_paid_provider_api_calls") == 0
            and row.get("direct_paid_api_or_cloud_spend_usd") == "0.000000",
            f"direct-paid boundary: {row.get('activity_id')}",
        )
        check(all(row.get(field) is None for field in UNAVAILABLE), f"unavailable metadata/cost: {row.get('activity_id')}")

    ts = target["summary"]
    check(
        (
            ts.get("standalone_outputs"),
            ts.get("comic_panel_plans"),
            ts.get("authorized_reference_uses"),
            ts.get("unique_timing_batches"),
            ts.get("overlap_adjusted_tool_call_wall_seconds"),
            ts.get("per_output_elapsed_seconds_available"),
            ts.get("direct_paid_provider_api_calls"),
            ts.get("paid_spend_usd"),
        )
        == (3, 3, 6, 1, 169.0, 0, 0, 0.0),
        "target execution source facts",
    )
    target_batches = target.get("timing_batches", [])
    check(
        len(target_batches) == 1
        and target_batches[0].get("wall_seconds") == 169.0
        and len(target_batches[0].get("member_panel_ids", [])) == 3,
        "target timing source facts",
    )
    fs = flat["summary"]
    check(
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
        )
        == (11, 50, 50, 23, 9, 1063.921, 227.068, 1290.989, None),
        "flat execution source facts",
    )
    check(
        flat_crops.get("summary", {}).get("planned_crops") == 50
        and flat_crops.get("summary", {}).get("manual_gutter_overrides") == 1
        and flat_crops.get("summary", {}).get("complete_plan_coverage") is True,
        "flat crop source facts",
    )
    xs = text["summary"]
    check(
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
        )
        == (11, 50, 50, 0, 0, 6, 568.3, 2, 1027.652, None),
        "text execution source facts",
    )
    check([batch.get("wall_seconds") for batch in text.get("timing_batches", [])] == [300.467, 158.885], "text batch facts")

    cumulative = activity.get("cumulative_complete_chapter_style_arms", {})
    check(
        cumulative.get("included_arms")
        == [
            "ch05_complete_chapter_alt_graphic_r1",
            "ch05_complete_chapter_clear_line_watercolor_r1",
            "ch05_complete_chapter_premium_cel_r1",
            "ch05_complete_chapter_flat_graphic_gouache_r1",
            "ch05_complete_chapter_reduced_palette_text_control_r1",
        ],
        "cumulative arm identities",
    )
    check(
        (
            cumulative.get("sequence_tool_calls"),
            cumulative.get("raster_outputs"),
            cumulative.get("comic_panel_plan_crops"),
            cumulative.get("authorized_reference_uses"),
            cumulative.get("unique_authorized_reference_hashes"),
        )
        == (55, 55, 250, 92, 3),
        "cumulative non-time counts",
    )
    check(
        cumulative.get("direct_paid_provider_api_calls") == 0
        and cumulative.get("direct_paid_api_or_cloud_spend_usd") == "0.000000"
        and all(cumulative.get(field) is None for field in UNAVAILABLE),
        "cumulative cost/unavailable boundary",
    )
    check(
        cumulative.get("combined_timing_seconds") is None
        and cumulative.get("combined_actual_end_to_end_wall_seconds") is None
        and cumulative.get("timing_combination_status") == "PROHIBITED_INCOMPARABLE_SCOPES",
        "no synthetic cumulative time",
    )

    accounting = activity.get("timing_accounting", {})
    check(
        accounting.get("prior_three_complete_arms", {}).get("overlap_adjusted_tool_call_wall_seconds") == 3278.3,
        "prior timing lineage",
    )
    check(accounting.get("targeted_repair_trio") == target_row.get("timing"), "target timing mirror")
    check(accounting.get("flat_graphic_gouache_complete_arm") == flat_row.get("timing"), "flat timing mirror")
    check(accounting.get("reduced_palette_text_control_complete_arm") == text_row.get("timing"), "text timing mirror")
    check(
        accounting.get("all_activity_actual_end_to_end_wall_seconds") is None
        and "Do not add" in accounting.get("combination_rule", ""),
        "all-activity timing honesty",
    )
    check(activity.get("unavailable_fields") == UNAVAILABLE, "unavailable fields")
    notes = activity.get("accounting_notes", [])
    check(len(notes) == 3 and "manual gutter override" in notes[2], "accounting notes")

    check(
        document.get("committed_actual_cost_usd") == "0.000000"
        and document.get("held_reservations_usd") == "0.000000"
        and document.get("approved_aggregate_cap_usd") is None
        and document.get("available_usd") is None
        and document.get("entries") == [],
        "disabled direct-paid domain",
    )
    check(
        document.get("budget_domain") == prior.get("budget_domain")
        and document.get("policy_id") == prior.get("policy_id")
        and document.get("state") == prior.get("state"),
        "direct-paid lineage",
    )
    boundary = document.get("boundary", "")
    check(
        isinstance(boundary, str)
        and "0/$0" in boundary
        and "unavailable/null, not zero" in boundary
        and "not combined" in boundary
        and "G07 remains separate" in boundary
        and "No candidate acceptance" in boundary,
        "boundary semantics",
    )
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("record_id", "bad"),
        lambda value: value["supersedes"].__setitem__("sha256", "0" * 64),
        lambda value: value["local_zero_external_cost_evidence"].pop(0),
        lambda value: value["local_zero_external_cost_evidence"][-1].__setitem__("external_uploads", 1),
        lambda value: value["revision_summary"].__setitem__("total_local_milestones", 108),
        lambda value: value["built_in_product_activity"]["current_revision_evidence_sources"][0].__setitem__("sha256", "f" * 64),
        lambda value: value["built_in_product_activity"]["evidence_sources"].pop(0),
        lambda value: value["built_in_product_activity"]["current_revision_activities"].pop(),
        lambda value: value["built_in_product_activity"]["current_revision_activities"][0].__setitem__("raster_outputs", 2),
        lambda value: value["built_in_product_activity"]["current_revision_activities"][1].__setitem__("manual_gutter_overrides", 0),
        lambda value: value["built_in_product_activity"]["current_revision_activities"][2].__setitem__("reference_uploads", None),
        lambda value: value["built_in_product_activity"]["current_revision_activities"][1]["timing"].__setitem__("known_individual_wall_seconds_sum", 1290.989),
        lambda value: value["built_in_product_activity"]["current_revision_activities"][2]["timing"].__setitem__("concurrent_batch_walls_seconds", [459.352]),
        lambda value: value["built_in_product_activity"]["current_revision_activities"][0]["timing"].__setitem__("actual_end_to_end_wall_seconds", 169.0),
        lambda value: value["built_in_product_activity"]["current_revision_activities"][1].__setitem__("monetary_cost_usd", 0.0),
        lambda value: value["built_in_product_activity"]["current_revision_activities"][2].__setitem__("direct_paid_provider_api_calls", 1),
        lambda value: value["built_in_product_activity"]["cumulative_complete_chapter_style_arms"].__setitem__("raster_outputs", 58),
        lambda value: value["built_in_product_activity"]["cumulative_complete_chapter_style_arms"].__setitem__("combined_timing_seconds", 5596.941),
        lambda value: value["built_in_product_activity"]["timing_accounting"].__setitem__("all_activity_actual_end_to_end_wall_seconds", 5596.941),
        lambda value: value["built_in_product_activity"].__setitem__("unavailable_fields", []),
        lambda value: value.__setitem__("committed_actual_cost_usd", "1.000000"),
        lambda value: value.__setitem__("boundary", "all durations total 5596.941 seconds and built-in cost is zero"),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = load(LEDGER)
    errors = validate(document)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(document)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
