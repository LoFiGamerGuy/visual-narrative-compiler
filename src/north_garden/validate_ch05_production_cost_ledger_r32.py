"""Validate append-only CH05 cost/timing ledger r32."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r32.json"
PRIOR = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r31.json"
CLEAR_EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-execution-manifest-r1.json"
CLEAR_CROPS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-crops-r1.json"
APPENDED = [
    "ch05_clear_line_watercolor_execution_renderrecords_r1",
    "ch05_clear_line_watercolor_deterministic_crop_and_assembly_r1",
    "ch05_clear_line_watercolor_agent_triage_r1",
    "ch05_three_route_measured_comparison_r1",
    "ch05_three_route_owner_review_start_r1",
]
UNAVAILABLE = [
    "model",
    "endpoint",
    "provider_request_ids",
    "usage",
    "monetary_cost_usd",
    "deterministic_seed",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    execution = json.loads(CLEAR_EXECUTION.read_text(encoding="utf-8"))
    crops = json.loads(CLEAR_CROPS.read_text(encoding="utf-8"))
    prior_rows = prior["local_zero_external_cost_evidence"]
    rows = doc.get("local_zero_external_cost_evidence", [])

    check(
        doc.get("record_type") == "ProductionCostLedger"
        and doc.get("schema_version") == "1.31"
        and doc.get("record_id") == "ng-ch05-production-cost-ledger-r32",
        "identity",
    )
    check(
        doc.get("supersedes")
        == {
            "record_id": prior["record_id"],
            "path": PRIOR.relative_to(ROOT).as_posix(),
            "sha256": sha256(PRIOR),
        },
        "supersedes",
    )
    check(doc.get("prior_record_rewritten") is False, "prior rewrite boundary")
    check(rows[: len(prior_rows)] == prior_rows, "append-only prefix")
    expected_suffix = [
        {"milestone": name, "external_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"}
        for name in APPENDED
    ]
    check(rows[len(prior_rows) :] == expected_suffix, "appended suffix")
    check(
        doc.get("revision_summary")
        == {
            "prior_local_milestones": 98,
            "appended_local_milestones": 5,
            "total_local_milestones": 103,
            "external_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        },
        "revision summary",
    )
    check(len(rows) == 103, "milestone denominator")

    activity = doc.get("built_in_product_activity", {})
    check(activity.get("product") == "OpenAI built-in ImageGen in Codex", "built-in product")
    check(
        activity.get("evidence_sources")
        == [
            {"path": CLEAR_EXECUTION.relative_to(ROOT).as_posix(), "sha256": sha256(CLEAR_EXECUTION)},
            {"path": CLEAR_CROPS.relative_to(ROOT).as_posix(), "sha256": sha256(CLEAR_CROPS)},
        ],
        "activity evidence sources",
    )
    clear = activity.get("current_revision_clear_line_watercolor", {})
    expected_clear_counts = (
        execution["summary"]["sequence_outputs"],
        execution["summary"]["sequence_outputs"],
        crops["summary"]["planned_crops"],
        execution["summary"]["authorized_reference_uses"],
        execution["summary"]["unique_timing_batches"],
        execution["summary"]["overlap_adjusted_tool_call_wall_seconds"],
    )
    observed_clear_counts = (
        clear.get("sequence_tool_calls"),
        clear.get("raster_outputs"),
        clear.get("comic_panel_plan_crops"),
        clear.get("authorized_reference_uses"),
        clear.get("unique_timing_batches"),
        clear.get("overlap_adjusted_tool_call_wall_seconds"),
    )
    check(observed_clear_counts == expected_clear_counts == (11, 11, 50, 23, 6, 1090.0), "clear-line activity counts")
    check(clear.get("unique_authorized_reference_hashes") == 3, "clear-line unique references")
    check(clear.get("timing_scope") == execution["summary"]["timing_scope"], "clear-line timing scope")
    check(all(clear.get(field) is None for field in UNAVAILABLE), "clear-line unavailable fields")

    cumulative = activity.get("cumulative_complete_chapter_style_arms", {})
    check(
        cumulative.get("included_arms")
        == ["ch05_complete_chapter_alt_graphic_r1", "ch05_complete_chapter_clear_line_watercolor_r1"],
        "cumulative arm set/order",
    )
    check(
        (
            cumulative.get("sequence_tool_calls"),
            cumulative.get("raster_outputs"),
            cumulative.get("comic_panel_plan_crops"),
            cumulative.get("authorized_reference_uses"),
            cumulative.get("unique_timing_batches"),
            cumulative.get("overlap_adjusted_tool_call_wall_seconds"),
        )
        == (22, 22, 100, 46, 12, 2044.3),
        "cumulative activity counts",
    )
    check(cumulative.get("unique_authorized_reference_hashes") == 3, "cumulative unique references")
    check(
        cumulative.get("direct_paid_provider_api_calls") == 0
        and cumulative.get("direct_paid_api_or_cloud_spend_usd") == "0.000000",
        "cumulative paid boundary",
    )
    check(all(cumulative.get(field) is None for field in UNAVAILABLE), "cumulative unavailable fields")
    check(activity.get("unavailable_fields") == UNAVAILABLE, "unavailable field names")

    check(
        doc.get("committed_actual_cost_usd") == "0.000000"
        and doc.get("held_reservations_usd") == "0.000000"
        and doc.get("approved_aggregate_cap_usd") is None
        and doc.get("available_usd") is None
        and doc.get("entries") == [],
        "disabled paid domain",
    )
    check(
        doc.get("budget_domain") == prior.get("budget_domain")
        and doc.get("policy_id") == prior.get("policy_id")
        and doc.get("state") == prior.get("state"),
        "paid domain lineage",
    )
    boundary = doc.get("boundary", "")
    check(
        isinstance(boundary, str)
        and "unavailable/null, not zero" in boundary
        and "Direct paid requests/uploads/spend remain 0/0/$0" in boundary,
        "boundary semantics",
    )
    return errors


def self_test(doc: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda d: d.__setitem__("record_id", "bad"),
        lambda d: d["supersedes"].__setitem__("sha256", "0" * 64),
        lambda d: d["local_zero_external_cost_evidence"].pop(0),
        lambda d: d["local_zero_external_cost_evidence"][-1].__setitem__("external_uploads", 1),
        lambda d: d["revision_summary"].__setitem__("total_local_milestones", 102),
        lambda d: d["built_in_product_activity"]["current_revision_clear_line_watercolor"].__setitem__("comic_panel_plan_crops", 49),
        lambda d: d["built_in_product_activity"]["current_revision_clear_line_watercolor"].__setitem__("monetary_cost_usd", 0),
        lambda d: d["built_in_product_activity"]["cumulative_complete_chapter_style_arms"].__setitem__("authorized_reference_uses", 69),
        lambda d: d["built_in_product_activity"]["cumulative_complete_chapter_style_arms"].__setitem__("overlap_adjusted_tool_call_wall_seconds", 3134.3),
        lambda d: d["built_in_product_activity"].__setitem__("unavailable_fields", []),
        lambda d: d.__setitem__("committed_actual_cost_usd", "1.000000"),
        lambda d: d.__setitem__("boundary", "built-in cost is zero"),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(doc)
        mutation(candidate)
        caught += bool(validate(candidate))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    doc = json.loads(LEDGER.read_text(encoding="utf-8"))
    errors = validate(doc)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(doc)
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
