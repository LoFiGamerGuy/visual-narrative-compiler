"""Validate append-only CH05 production cost/timing ledger r33."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r33.json"
PRIOR = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r32.json"
EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-execution-manifest-r1.json"
CROPS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-crops-r1.json"
ASSEMBLY = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-assembly-r1.json"
SPLIT_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-premium-cel-r1/panels/premium-cel-panel-split-report-r1.json"
REVIEW_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-premium-cel-r1/review/build-report.json"
LETTERING_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-premium-cel-r1/lettered/lettering-build-report.json"
SOURCES = [EXECUTION, CROPS, ASSEMBLY, SPLIT_REPORT, REVIEW_REPORT, LETTERING_REPORT]
APPENDED = [
    "ch05_premium_cel_execution_renderrecords_r1",
    "ch05_premium_cel_deterministic_crop_and_assembly_r1",
    "ch05_premium_cel_lettering_and_review_packets_r1",
]
UNAVAILABLE = ["model", "endpoint", "provider_request_ids", "usage", "monetary_cost_usd", "deterministic_seed"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    crops = json.loads(CROPS.read_text(encoding="utf-8"))
    assembly = json.loads(ASSEMBLY.read_text(encoding="utf-8"))
    split_report = json.loads(SPLIT_REPORT.read_text(encoding="utf-8"))
    review_report = json.loads(REVIEW_REPORT.read_text(encoding="utf-8"))
    lettering_report = json.loads(LETTERING_REPORT.read_text(encoding="utf-8"))
    prior_rows = prior["local_zero_external_cost_evidence"]
    rows = document.get("local_zero_external_cost_evidence", [])

    check(
        document.get("record_type") == "ProductionCostLedger"
        and document.get("schema_version") == "1.32"
        and document.get("record_id") == "ng-ch05-production-cost-ledger-r33",
        "identity",
    )
    check(
        document.get("supersedes")
        == {"record_id": prior["record_id"], "path": PRIOR.relative_to(ROOT).as_posix(), "sha256": sha256(PRIOR)},
        "supersedes",
    )
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
            "prior_local_milestones": 103,
            "appended_local_milestones": 3,
            "total_local_milestones": 106,
            "external_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
        }
        and len(rows) == 106,
        "revision summary/denominator",
    )

    activity = document.get("built_in_product_activity", {})
    check(activity.get("product") == "OpenAI built-in ImageGen in Codex", "product")
    check(
        activity.get("evidence_sources")
        == [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in SOURCES],
        "evidence source bindings",
    )
    current = activity.get("current_revision_premium_cel", {})
    check(
        (
            current.get("sequence_tool_calls"),
            current.get("raster_outputs"),
            current.get("comic_panel_plan_crops"),
            current.get("authorized_reference_uses"),
            current.get("unique_timing_batches"),
            current.get("overlap_adjusted_tool_call_wall_seconds"),
        )
        == (11, 11, 50, 23, 6, 1234.0),
        "premium-cel counts/timing",
    )
    check(current.get("unique_authorized_reference_hashes") == 3, "premium-cel unique references")
    check(current.get("timing_scope") == execution["summary"]["timing_scope"], "timing scope")
    check(all(current.get(field) is None for field in UNAVAILABLE), "premium-cel unavailable metadata/cost")
    check(
        execution["summary"].get("sequence_outputs") == 11
        and execution["summary"].get("authorized_reference_uses") == 23
        and execution["summary"].get("overlap_adjusted_tool_call_wall_seconds") == 1234.0,
        "execution source facts",
    )
    check(
        crops.get("summary", {}).get("planned_crops") == 50
        and len(assembly.get("entries", [])) == 50
        and split_report.get("summary", {}).get("panels_produced") == 50,
        "crop/assembly source facts",
    )
    check(
        review_report.get("chapter_complete") is True
        and lettering_report.get("summary", {}).get("chapter_panels") == 50,
        "review packet source facts",
    )

    cumulative = activity.get("cumulative_complete_chapter_style_arms", {})
    check(
        cumulative.get("included_arms")
        == [
            "ch05_complete_chapter_alt_graphic_r1",
            "ch05_complete_chapter_clear_line_watercolor_r1",
            "ch05_complete_chapter_premium_cel_r1",
        ],
        "cumulative arms",
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
        == (33, 33, 150, 69, 18, 3278.3),
        "cumulative counts/timing",
    )
    check(cumulative.get("unique_authorized_reference_hashes") == 3, "cumulative unique references")
    check(
        cumulative.get("direct_paid_provider_api_calls") == 0
        and cumulative.get("direct_paid_api_or_cloud_spend_usd") == "0.000000",
        "cumulative direct-paid boundary",
    )
    check(all(cumulative.get(field) is None for field in UNAVAILABLE), "cumulative unavailable metadata/cost")
    check(activity.get("unavailable_fields") == UNAVAILABLE, "unavailable field names")
    check(
        activity.get("accounting_note")
        == "Fifty deterministic panel crops are local derivatives and are not counted as tool calls or raster generation outputs.",
        "crop/tool-call distinction",
    )

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
        and "11 built-in sequence outputs" in boundary
        and "50 deterministic local crops" in boundary
        and "0/0/$0" in boundary
        and "unavailable/null, not zero" in boundary,
        "boundary semantics",
    )
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("record_id", "bad"),
        lambda value: value["supersedes"].__setitem__("sha256", "0" * 64),
        lambda value: value["local_zero_external_cost_evidence"].pop(0),
        lambda value: value["local_zero_external_cost_evidence"][-1].__setitem__("external_requests", 50),
        lambda value: value["revision_summary"].__setitem__("total_local_milestones", 105),
        lambda value: value["built_in_product_activity"]["current_revision_premium_cel"].__setitem__("sequence_tool_calls", 50),
        lambda value: value["built_in_product_activity"]["current_revision_premium_cel"].__setitem__("comic_panel_plan_crops", 11),
        lambda value: value["built_in_product_activity"]["current_revision_premium_cel"].__setitem__("monetary_cost_usd", 0.0),
        lambda value: value["built_in_product_activity"]["cumulative_complete_chapter_style_arms"].__setitem__("raster_outputs", 150),
        lambda value: value["built_in_product_activity"]["cumulative_complete_chapter_style_arms"].__setitem__("authorized_reference_uses", 92),
        lambda value: value["built_in_product_activity"]["cumulative_complete_chapter_style_arms"].__setitem__("overlap_adjusted_tool_call_wall_seconds", 4512.3),
        lambda value: value["built_in_product_activity"].__setitem__("unavailable_fields", []),
        lambda value: value.__setitem__("committed_actual_cost_usd", "1.000000"),
        lambda value: value.__setitem__("boundary", "crops are provider calls and built-in cost is zero"),
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
    document = json.loads(LEDGER.read_text(encoding="utf-8"))
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
