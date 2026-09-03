"""Compile the CH05 cadence objective-sensitivity audit from six-route evidence only."""

from __future__ import annotations

import hashlib
import json
import math
from itertools import pairwise
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/research/evidence/ch05-six-route-comparison-r1.json"
JSON_OUT = (
    ROOT / "docs/research/evidence/ch05-cadence-objective-sensitivity-audit-r1.json"
)
MARKDOWN_OUT = ROOT / "docs/research/ch05-cadence-objective-sensitivity-audit-r1.md"
ROUTES = (
    "r6",
    "alt_graphic",
    "clear_line_watercolor",
    "premium_cel",
    "flat_graphic_gouache",
    "reduced_palette_text_control",
)
SECONDARY_FIELDS = (
    "adjacent_route_transitions",
    "combined_semantic_identity_warnings",
    "semantic_warnings",
    "identity_warnings",
    "overall_failures",
    "lettering_failures",
    "combined_overall_lettering_warnings",
    "stable_route_preference_sum",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_cost(
    route: str,
    start: int,
    end: int,
    semantic: dict[str, list[str]],
    identity: dict[str, list[str]],
    overall: dict[str, list[str]],
    lettering: dict[str, list[str]],
) -> tuple[int, ...]:
    region = slice(start - 1, end)
    sem = semantic[route][region]
    ident = identity[route][region]
    all_status = overall[route][region]
    letter = lettering[route][region]
    return (
        sem.count("FAIL") + ident.count("FAIL"),
        sem.count("FAIL"),
        ident.count("FAIL"),
        sem.count("WARN") + ident.count("WARN"),
        sem.count("WARN"),
        ident.count("WARN"),
        all_status.count("FAIL"),
        letter.count("FAIL"),
        all_status.count("WARN") + letter.count("WARN"),
        ROUTES.index(route),
    )


def add_vector(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a + b for a, b in zip(left, right, strict=True))


def score_dict(score: tuple[int, ...]) -> dict[str, int]:
    return dict(zip(SECONDARY_FIELDS, score, strict=True))


def assignment_rows(
    path: tuple[str, ...], sequences: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    return [
        {
            "sequence_id": sequence["sequence_id"],
            "panel_range": sequence["panel_range"],
            "route": route,
        }
        for sequence, route in zip(sequences, path, strict=True)
    ]


def full_score(
    path: tuple[str, ...],
    sequences: list[dict[str, Any]],
    costs: dict[tuple[str, str], tuple[int, ...]],
) -> tuple[int, ...]:
    score = [sum(left != right for left, right in pairwise(path))] + [0] * 7
    for route, sequence in zip(path, sequences, strict=True):
        local = costs[(sequence["sequence_id"], route)]
        for index, value in enumerate(local[3:], start=1):
            score[index] += value
    return tuple(score)


def solve_variant(
    sequences: list[dict[str, Any]],
    costs: dict[tuple[str, str], tuple[int, ...]],
    dropped_index: int | None,
) -> tuple[tuple[int, ...], tuple[str, ...], int]:
    active = tuple(
        index for index in range(len(SECONDARY_FIELDS)) if index != dropped_index
    )
    first = sequences[0]
    states: dict[str, tuple[tuple[int, ...], tuple[str, ...], int]] = {}
    for route in ROUTES:
        local = costs[(first["sequence_id"], route)]
        if any(local[index] for index in range(3)):
            continue
        vector = (0, *local[3:])
        states[route] = (tuple(vector[index] for index in active), (route,), 1)
    for sequence in sequences[1:]:
        next_states: dict[str, tuple[tuple[int, ...], tuple[str, ...], int]] = {}
        for route in ROUTES:
            local = costs[(sequence["sequence_id"], route)]
            if any(local[index] for index in range(3)):
                continue
            options: list[tuple[tuple[int, ...], tuple[str, ...], int]] = []
            for previous, (prior_score, prior_path, prior_count) in states.items():
                vector = (int(previous != route), *local[3:])
                increment = tuple(vector[index] for index in active)
                options.append(
                    (
                        add_vector(prior_score, increment),
                        prior_path + (route,),
                        prior_count,
                    )
                )
            best_score = min(option[0] for option in options)
            tied = [option for option in options if option[0] == best_score]
            representative = min(
                (option[1] for option in tied),
                key=lambda value: tuple(
                    ROUTES.index(route_name) for route_name in value
                ),
            )
            next_states[route] = (
                best_score,
                representative,
                sum(option[2] for option in tied),
            )
        states = next_states
    best_score = min(value[0] for value in states.values())
    tied = [value for value in states.values() if value[0] == best_score]
    representative = min(
        (value[1] for value in tied),
        key=lambda value: tuple(ROUTES.index(route_name) for route_name in value),
    )
    return best_score, representative, sum(value[2] for value in tied)


def dominates(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
    return all(a <= b for a, b in zip(left, right, strict=True)) and any(
        a < b for a, b in zip(left, right, strict=True)
    )


def prune_frontier(
    candidates: list[tuple[tuple[int, ...], tuple[str, ...], int]],
) -> list[tuple[tuple[int, ...], tuple[str, ...], int]]:
    merged: dict[tuple[int, ...], tuple[tuple[str, ...], int]] = {}
    for score, path, count in candidates:
        if score in merged:
            existing_path, existing_count = merged[score]
            representative = min(
                (existing_path, path),
                key=lambda value: tuple(ROUTES.index(route) for route in value),
            )
            merged[score] = (representative, existing_count + count)
        else:
            merged[score] = (path, count)
    scores = list(merged)
    kept = [
        score
        for score in scores
        if not any(dominates(other, score) for other in scores if other != score)
    ]
    return [(score, *merged[score]) for score in sorted(kept)]


def pareto_front(
    sequences: list[dict[str, Any]],
    costs: dict[tuple[str, str], tuple[int, ...]],
) -> list[tuple[tuple[int, ...], tuple[str, ...], int]]:
    first = sequences[0]
    states: dict[str, list[tuple[tuple[int, ...], tuple[str, ...], int]]] = {}
    for route in ROUTES:
        local = costs[(first["sequence_id"], route)]
        if not any(local[index] for index in range(3)):
            states[route] = [((0, *local[3:]), (route,), 1)]
    for sequence in sequences[1:]:
        next_states: dict[str, list[tuple[tuple[int, ...], tuple[str, ...], int]]] = {}
        for route in ROUTES:
            local = costs[(sequence["sequence_id"], route)]
            if any(local[index] for index in range(3)):
                continue
            candidates = []
            for previous, rows in states.items():
                increment = (int(previous != route), *local[3:])
                for score, path, count in rows:
                    candidates.append(
                        (add_vector(score, increment), path + (route,), count)
                    )
            next_states[route] = prune_frontier(candidates)
        states = next_states
    return prune_frontier([row for rows in states.values() for row in rows])


def changes_from_baseline(
    path: tuple[str, ...], baseline: tuple[str, ...], sequences: list[dict[str, Any]]
) -> list[dict[str, str]]:
    return [
        {
            "sequence_id": sequence["sequence_id"],
            "baseline_route": original,
            "alternate_route": current,
        }
        for sequence, original, current in zip(sequences, baseline, path, strict=True)
        if original != current
    ]


def compact(path: tuple[str, ...]) -> str:
    abbreviations = {
        "r6": "R6",
        "alt_graphic": "ALT",
        "clear_line_watercolor": "CLW",
        "premium_cel": "CEL",
        "flat_graphic_gouache": "FGG",
        "reduced_palette_text_control": "RPT",
    }
    return " / ".join(abbreviations[route] for route in path)


def build_documents() -> tuple[dict[str, Any], str]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    panels = source["visual_complexity"]["per_panel"]
    sequences = [
        {"sequence_id": row["sequence_id"], "panel_range": row["panel_range"]}
        for row in source["sequence_cadence_recommendation"]["sequences"]
    ]
    semantic = {
        route: [row[route]["semantic_status"] for row in panels] for route in ROUTES
    }
    identity = {
        route: [row[route]["identity_status"] for row in panels] for route in ROUTES
    }
    overall = {
        route: [row[route]["overall_status"] for row in panels] for route in ROUTES
    }
    lettering = {
        route: [row[route]["lettering_status"] for row in panels] for route in ROUTES
    }
    costs = {
        (sequence["sequence_id"], route): local_cost(
            route, *sequence["panel_range"], semantic, identity, overall, lettering
        )
        for sequence in sequences
        for route in ROUTES
    }
    feasible_routes: list[dict[str, Any]] = []
    for sequence in sequences:
        allowed = [
            route
            for route in ROUTES
            if not any(
                costs[(sequence["sequence_id"], route)][index] for index in range(3)
            )
        ]
        feasible_routes.append(
            {
                "sequence_id": sequence["sequence_id"],
                "panel_range": sequence["panel_range"],
                "zero_hard_failure_routes": allowed,
                "route_count": len(allowed),
            }
        )
    feasible_assignment_count = math.prod(row["route_count"] for row in feasible_routes)

    _baseline_score, baseline, baseline_ties = solve_variant(sequences, costs, None)
    recorded = tuple(
        row["selected_route"]
        for row in source["sequence_cadence_recommendation"]["sequences"]
    )
    if baseline != recorded:
        raise ValueError("reconstructed baseline differs from recorded cadence")
    variants: list[dict[str, Any]] = []
    for dropped_index, field in enumerate(SECONDARY_FIELDS):
        optimized_score, path, tie_count = solve_variant(
            sequences, costs, dropped_index
        )
        variants.append(
            {
                "variant_id": f"drop_{field}",
                "dropped_secondary_objective": field,
                "active_objectives_in_order": [
                    name
                    for index, name in enumerate(SECONDARY_FIELDS)
                    if index != dropped_index
                ],
                "optimized_score_without_dropped_field": dict(
                    zip(
                        [
                            name
                            for index, name in enumerate(SECONDARY_FIELDS)
                            if index != dropped_index
                        ],
                        optimized_score,
                        strict=True,
                    )
                ),
                "full_score_for_comparison": score_dict(
                    full_score(path, sequences, costs)
                ),
                "assignment": assignment_rows(path, sequences),
                "compact_assignment_S01_to_S11": compact(path),
                "matches_recorded_baseline": path == baseline,
                "changes_from_recorded_baseline": changes_from_baseline(
                    path, baseline, sequences
                ),
                "optimal_assignment_count": tie_count,
            }
        )
    changed = [row for row in variants if not row["matches_recorded_baseline"]]
    frontier = pareto_front(sequences, costs)
    pareto_rows = [
        {
            "pareto_id": f"pareto_{index:02d}",
            "full_score": score_dict(score),
            "assignment": assignment_rows(path, sequences),
            "compact_assignment_S01_to_S11": compact(path),
            "changes_from_recorded_baseline": changes_from_baseline(
                path, baseline, sequences
            ),
            "assignments_with_identical_score": count,
            "is_recorded_baseline": path == baseline,
        }
        for index, (score, path, count) in enumerate(frontier, start=1)
    ]
    document: dict[str, Any] = {
        "record_type": "CH05CadenceObjectiveSensitivityAudit",
        "schema_version": "1.0",
        "record_id": "ng-ch05-cadence-objective-sensitivity-audit-r1",
        "state": "DETERMINISTIC_EXISTING_EVIDENCE_SENSITIVITY_RESULT",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [
            {"path": SOURCE.relative_to(ROOT).as_posix(), "sha256": sha256(SOURCE)}
        ],
        "hard_constraints": [
            "combined_semantic_identity_failures=0",
            "semantic_failures=0",
            "identity_failures=0",
        ],
        "secondary_objectives_in_baseline_order": list(SECONDARY_FIELDS),
        "method": {
            "leave_one_out": "Run eight variants, each deleting exactly one secondary objective while retaining the order of the other seven and enforcing all three zero-failure hard constraints.",
            "tie_handling": "Count all assignments sharing the optimal retained-objective tuple. Use ROUTES order only to choose a deterministic representative; the tie count is reported independently.",
            "pareto": "Exact dynamic-programming Pareto frontier over all eight secondary fields, pruning dominated partial scores only within the same last-route state before the final global prune.",
            "evidence_boundary": "Uses only status fields and sequence ranges already recorded in the six-route evidence; no pixels, prompts, providers, uploads, or cost data are introduced.",
        },
        "coverage": {
            "sequences": len(sequences),
            "routes": len(ROUTES),
            "candidate_sequence_route_cells": len(sequences) * len(ROUTES),
            "hard_feasible_assignment_count": feasible_assignment_count,
            "leave_one_out_variants": len(variants),
        },
        "hard_feasible_routes_by_sequence": feasible_routes,
        "recorded_baseline": {
            "full_score": score_dict(full_score(baseline, sequences, costs)),
            "assignment": assignment_rows(baseline, sequences),
            "compact_assignment_S01_to_S11": compact(baseline),
            "optimal_assignment_count": baseline_ties,
        },
        "leave_one_out_results": variants,
        "invariance": {
            "fully_invariant": not changed,
            "variants_matching_recorded_baseline": len(variants) - len(changed),
            "variants_total": len(variants),
            "changed_variant_ids": [row["variant_id"] for row in changed],
            "distinct_assignments_across_baseline_and_variants": len(
                {tuple(item["route"] for item in row["assignment"]) for row in variants}
                | {baseline}
            ),
            "interpretation": "The three-block cadence is invariant to seven of eight single-objective omissions. Removing adjacent-route transitions changes S10 and S11 from premium cel to R6; transition minimization is therefore outcome-determinative for the late block.",
        },
        "tie_sensitivity": {
            "all_tested_variants_have_unique_optimum": all(
                row["optimal_assignment_count"] == 1 for row in variants
            )
            and baseline_ties == 1,
            "maximum_optimal_assignment_count": max(
                [baseline_ties, *[row["optimal_assignment_count"] for row in variants]]
            ),
            "interpretation": "No equal-score assignment tie appears in the baseline or tested variants. The observed change is objective-inclusion sensitivity, not unresolved deterministic tie-breaking.",
        },
        "pareto_front": {
            "exact_over_hard_feasible_assignments": True,
            "assignment_count": len(pareto_rows),
            "rows": pareto_rows,
            "interpretation": "Three nondominated assignments exist. The baseline trades one extra semantic warning for one fewer transition; the two alternatives reduce warning fields but add transitions and, for the third frontier point, substantial overall/lettering failures.",
        },
        "engineering_inference": {
            "recommendation": "Retain the recorded three-block cadence for owner review because it is stable to seven of eight leave-one-out variants and uniquely optimizes the declared transition-first policy. Treat the S10-S11 premium-cel choice as policy-sensitive, not inevitable.",
            "production_promotion": None,
        },
        "disposition": {
            "owner_acceptance": None,
            "rights_clearance": None,
            "commercially_cleared": None,
            "canon_change": None,
            "exact_production_base": None,
        },
        "spend": {
            "direct_paid_api_cloud_usd": 0.0,
            "provider_calls": 0,
            "uploads": 0,
            "new_pixels": 0,
        },
        "limitations": [
            "Leave-one-out analysis tests objective inclusion, not every permutation or weighting of the secondary objectives.",
            "The exact Pareto frontier is over recorded categorical review counts, not visual quality, human preference, commercial suitability, or stochastic reproducibility.",
            "All underlying reviews remain non-gating agent evidence; owner review and acceptance remain unrecorded.",
            "Stable route preference is a deterministic tie preference, not a quality measure.",
        ],
        "boundary": "Sensitivity evidence only; no art generation, pixel review or edit, provider call, upload, spend, owner acceptance, rights clearance, canon change, or exact production-base selection.",
    }

    variant_lines = []
    for row in variants:
        score = row["full_score_for_comparison"]
        variant_lines.append(
            f"| `{row['dropped_secondary_objective']}` | {'yes' if row['matches_recorded_baseline'] else 'no'} | {row['optimal_assignment_count']} | {score['adjacent_route_transitions']} | {score['semantic_warnings']} | {score['overall_failures']} | {score['lettering_failures']} | `{row['compact_assignment_S01_to_S11']}` |"
        )
    pareto_lines = []
    for row in pareto_rows:
        score = row["full_score"]
        pareto_lines.append(
            f"| {row['pareto_id']} | {'yes' if row['is_recorded_baseline'] else 'no'} | {score['adjacent_route_transitions']} | {score['semantic_warnings']} | {score['overall_failures']} | {score['lettering_failures']} | {score['combined_overall_lettering_warnings']} | `{row['compact_assignment_S01_to_S11']}` |"
        )
    markdown = "\n".join(
        [
            "# CH05 cadence objective-sensitivity audit r1",
            "",
            "The recorded three-block cadence is not fully invariant, but it is stable under seven of eight leave-one-secondary-objective-out variants. This audit uses only the existing six-route status table; it creates no pixels and makes no acceptance or production-base decision.",
            "",
            "Route abbreviations: `RPT` reduced-palette text control, `R6` R6, `CEL` premium cel, `CLW` clear-line watercolor, `ALT` alternate graphic, `FGG` flat graphic-gouache. Assignments run S01 through S11.",
            "",
            "## Method",
            "",
            "Hard constraints remain zero combined semantic/identity failures, zero semantic failures, and zero identity failures. Each variant removes exactly one of eight secondary objectives while retaining the original order of the other seven. There are 1,728,000 hard-feasible assignments across the 11 sequences.",
            "",
            "## Leave-one-out results",
            "",
            "| Dropped objective | Matches baseline | Optimal ties | Transitions | Semantic WARN | Overall FAIL | Lettering FAIL | Assignment |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
            *variant_lines,
            "",
            "Seven variants reproduce `RPT / R6 / R6 / R6 / R6 / R6 / R6 / R6 / CEL / CEL / CEL`. Removing `adjacent_route_transitions` alone changes S10-S11 to R6: `RPT / R6 / R6 / R6 / R6 / R6 / R6 / R6 / CEL / R6 / R6`. This adds one transition (2→3) while reducing semantic warnings (3→2). Every tested optimum is unique, so the change is objective-inclusion sensitivity, not a score tie.",
            "",
            "## Exact Pareto frontier",
            "",
            "| Point | Baseline | Transitions | Semantic WARN | Overall FAIL | Lettering FAIL | Secondary WARN | Assignment |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
            *pareto_lines,
            "",
            "The baseline and both alternatives are nondominated over the eight recorded secondary fields. The third point changes S07 to reduced-palette and S10-S11 to R6; its one secondary warning is purchased with five transitions, nine overall failures, and six lettering failures. Pareto status is not a quality or production recommendation.",
            "",
            "## Conclusion",
            "",
            "Retain the three-block cadence for owner review: it is stable to seven of eight objective omissions and uniquely implements the declared transition-first policy. Record S10-S11 premium cel as policy-sensitive rather than inevitable. No promotion, rerender, or provider action follows.",
            "",
            "## Limitations",
            "",
            "- Leave-one-out does not test every ordering or weighting of secondary objectives.",
            "- The exact Pareto frontier covers recorded categorical counts, not visual quality or human preference.",
            "- Reviews remain non-gating; owner acceptance, rights clearance, canon change, and exact-production-base selection remain null.",
            "- Provider calls, uploads, new pixels, and direct paid spend are zero.",
            "",
            f"Input: `{SOURCE.relative_to(ROOT).as_posix()}` — SHA-256 `{sha256(SOURCE)}`.",
            "",
            "Machine-readable evidence: `docs/research/evidence/ch05-cadence-objective-sensitivity-audit-r1.json`.",
            "",
        ]
    )
    return document, markdown


def main() -> int:
    document, markdown = build_documents()
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN_OUT.write_text(markdown, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "json": JSON_OUT.relative_to(ROOT).as_posix(),
                "json_sha256": sha256(JSON_OUT),
                "markdown": MARKDOWN_OUT.relative_to(ROOT).as_posix(),
                "markdown_sha256": sha256(MARKDOWN_OUT),
                "invariance": document["invariance"],
                "pareto_assignments": document["pareto_front"]["assignment_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
