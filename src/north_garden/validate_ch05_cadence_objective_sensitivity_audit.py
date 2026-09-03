"""Fail-closed validation for the CH05 cadence objective-sensitivity audit."""

from __future__ import annotations

import argparse
import copy
import json
from collections.abc import Callable
from typing import Any

from compile_ch05_cadence_objective_sensitivity_audit import (
    JSON_OUT,
    MARKDOWN_OUT,
    SECONDARY_FIELDS,
    build_documents,
    dominates,
)

BASELINE = [
    "reduced_palette_text_control",
    *("r6" for _ in range(7)),
    *("premium_cel" for _ in range(3)),
]
NO_TRANSITION_OBJECTIVE = [
    "reduced_palette_text_control",
    *("r6" for _ in range(7)),
    "premium_cel",
    "r6",
    "r6",
]


def route_path(record: dict[str, Any]) -> list[str]:
    return [row["route"] for row in record.get("assignment", [])]


def validate(document: dict[str, Any], markdown: str) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    try:
        expected_document, expected_markdown = build_documents()
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        return [f"source reconstruction failed: {exc}"]
    check(
        document == expected_document, "JSON differs from deterministic reconstruction"
    )
    check(
        markdown == expected_markdown,
        "Markdown differs from deterministic reconstruction",
    )
    check(
        document.get("record_type") == "CH05CadenceObjectiveSensitivityAudit",
        "record_type",
    )
    check(
        document.get("state") == "DETERMINISTIC_EXISTING_EVIDENCE_SENSITIVITY_RESULT",
        "state",
    )
    check(document.get("planning_structure") == "ComicPanelPlan", "planning structure")
    check(
        document.get("animation_shot_plan") is None and document.get("e_conte") is None,
        "animation boundary",
    )
    check(
        document.get("hard_constraints")
        == [
            "combined_semantic_identity_failures=0",
            "semantic_failures=0",
            "identity_failures=0",
        ],
        "hard constraints",
    )
    check(
        document.get("secondary_objectives_in_baseline_order")
        == list(SECONDARY_FIELDS),
        "secondary objective order",
    )
    check(
        document.get("coverage")
        == {
            "sequences": 11,
            "routes": 6,
            "candidate_sequence_route_cells": 66,
            "hard_feasible_assignment_count": 1728000,
            "leave_one_out_variants": 8,
        },
        "coverage",
    )
    feasible = document.get("hard_feasible_routes_by_sequence", [])
    check(
        len(feasible) == 11
        and [row.get("route_count") for row in feasible]
        == [1, 4, 5, 6, 6, 4, 5, 2, 2, 6, 5],
        "hard-feasible route counts",
    )

    baseline = document.get("recorded_baseline", {})
    check(route_path(baseline) == BASELINE, "baseline assignment")
    check(
        baseline.get("full_score")
        == {
            "adjacent_route_transitions": 2,
            "combined_semantic_identity_warnings": 3,
            "semantic_warnings": 3,
            "identity_warnings": 0,
            "overall_failures": 4,
            "lettering_failures": 2,
            "combined_overall_lettering_warnings": 3,
            "stable_route_preference_sum": 14,
        },
        "baseline score",
    )
    check(baseline.get("optimal_assignment_count") == 1, "baseline tie count")

    variants = document.get("leave_one_out_results", [])
    check(len(variants) == 8, "variant count")
    check(
        [row.get("dropped_secondary_objective") for row in variants]
        == list(SECONDARY_FIELDS),
        "leave-one-out coverage",
    )
    changed = [row for row in variants if not row.get("matches_recorded_baseline")]
    check(
        len(changed) == 1
        and changed[0].get("variant_id") == "drop_adjacent_route_transitions",
        "changed variant",
    )
    if changed:
        check(route_path(changed[0]) == NO_TRANSITION_OBJECTIVE, "changed assignment")
        check(
            [
                row.get("sequence_id")
                for row in changed[0].get("changes_from_recorded_baseline", [])
            ]
            == ["s10-silence-return", "s11-farmhouse-reversal"],
            "changed sequences",
        )
        check(
            changed[0].get("full_score_for_comparison")
            == {
                "adjacent_route_transitions": 3,
                "combined_semantic_identity_warnings": 2,
                "semantic_warnings": 2,
                "identity_warnings": 0,
                "overall_failures": 4,
                "lettering_failures": 2,
                "combined_overall_lettering_warnings": 2,
                "stable_route_preference_sum": 8,
            },
            "changed score",
        )
    check(
        all(row.get("optimal_assignment_count") == 1 for row in variants),
        "variant tie counts",
    )

    invariance = document.get("invariance", {})
    check(
        invariance.get("fully_invariant") is False
        and invariance.get("variants_matching_recorded_baseline") == 7
        and invariance.get("variants_total") == 8,
        "invariance summary",
    )
    check(
        invariance.get("changed_variant_ids") == ["drop_adjacent_route_transitions"]
        and invariance.get("distinct_assignments_across_baseline_and_variants") == 2,
        "invariance details",
    )
    ties = document.get("tie_sensitivity", {})
    check(
        ties.get("all_tested_variants_have_unique_optimum") is True
        and ties.get("maximum_optimal_assignment_count") == 1,
        "tie sensitivity",
    )

    pareto = document.get("pareto_front", {})
    pareto_rows = pareto.get("rows", [])
    check(
        pareto.get("exact_over_hard_feasible_assignments") is True
        and pareto.get("assignment_count") == 3
        and len(pareto_rows) == 3,
        "Pareto coverage",
    )
    scores = [
        tuple(row.get("full_score", {}).get(field, -1) for field in SECONDARY_FIELDS)
        for row in pareto_rows
    ]
    check(
        not any(
            dominates(left, right)
            for index, left in enumerate(scores)
            for right in scores[index + 1 :]
        ),
        "forward Pareto dominance",
    )
    check(
        not any(
            dominates(right, left)
            for index, left in enumerate(scores)
            for right in scores[index + 1 :]
        ),
        "reverse Pareto dominance",
    )
    check(
        sum(row.get("is_recorded_baseline") is True for row in pareto_rows) == 1,
        "Pareto baseline count",
    )
    check(
        [row.get("assignments_with_identical_score") for row in pareto_rows]
        == [1, 1, 1],
        "Pareto score ties",
    )

    check(
        document.get("engineering_inference", {}).get("production_promotion") is None,
        "production promotion",
    )
    check(
        document.get("disposition")
        == {
            "owner_acceptance": None,
            "rights_clearance": None,
            "commercially_cleared": None,
            "canon_change": None,
            "exact_production_base": None,
        },
        "disposition",
    )
    check(
        document.get("spend")
        == {
            "direct_paid_api_cloud_usd": 0.0,
            "provider_calls": 0,
            "uploads": 0,
            "new_pixels": 0,
        },
        "spend and execution boundary",
    )
    check("no art generation" in document.get("boundary", "").lower(), "boundary")
    check(
        "not fully invariant" in markdown
        and "Exact Pareto frontier" in markdown
        and "Every tested optimum is unique" in markdown,
        "Markdown conclusions",
    )
    return errors


def self_test(document: dict[str, Any], markdown: str) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "ACCEPTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("animation_shot_plan", {}),
        lambda value: value["inputs"][0].__setitem__("sha256", "0" * 64),
        lambda value: value["coverage"].__setitem__(
            "hard_feasible_assignment_count", 1
        ),
        lambda value: value["hard_feasible_routes_by_sequence"][0].__setitem__(
            "route_count", 2
        ),
        lambda value: value["recorded_baseline"]["full_score"].__setitem__(
            "adjacent_route_transitions", 3
        ),
        lambda value: value["recorded_baseline"]["assignment"][0].__setitem__(
            "route", "r6"
        ),
        lambda value: value["leave_one_out_results"].pop(),
        lambda value: value["leave_one_out_results"][0].__setitem__(
            "matches_recorded_baseline", True
        ),
        lambda value: value["leave_one_out_results"][0].__setitem__(
            "optimal_assignment_count", 2
        ),
        lambda value: value["invariance"].__setitem__("fully_invariant", True),
        lambda value: value["tie_sensitivity"].__setitem__(
            "all_tested_variants_have_unique_optimum", False
        ),
        lambda value: value["pareto_front"].__setitem__("assignment_count", 2),
        lambda value: value["pareto_front"]["rows"][0]["full_score"].__setitem__(
            "adjacent_route_transitions", 99
        ),
        lambda value: value["engineering_inference"].__setitem__(
            "production_promotion", "approved"
        ),
        lambda value: value["disposition"].__setitem__("owner_acceptance", True),
        lambda value: value["spend"].__setitem__("provider_calls", 1),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate, markdown))
    caught += bool(validate(document, markdown + "\nmutated"))
    return caught, len(mutations) + 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = json.loads(JSON_OUT.read_text(encoding="utf-8"))
    markdown = MARKDOWN_OUT.read_text(encoding="utf-8")
    errors = validate(document, markdown)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(document, markdown)
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
