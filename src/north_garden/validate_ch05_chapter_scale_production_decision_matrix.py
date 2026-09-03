"""Validate the CH05 chapter-scale production decision matrix and its claim boundaries."""

from __future__ import annotations

import argparse
import copy
import json
from collections.abc import Callable
from typing import Any

from compile_ch05_chapter_scale_production_decision_matrix import (
    JSON_OUT,
    MARKDOWN_OUT,
    build_documents,
)


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
        document.get("record_type") == "CH05ChapterScaleProductionDecisionMatrix",
        "record_type",
    )
    check(document.get("state") == "EVIDENCE_SYNTHESIS_PENDING_OWNER_REVIEW", "state")
    check(document.get("planning_structure") == "ComicPanelPlan", "planning structure")
    check(
        document.get("animation_shot_plan") is None and document.get("e_conte") is None,
        "animation boundary",
    )
    check(
        set(document)
        >= {
            "measured_fact",
            "engineering_inference",
            "owner_review_question",
            "future_noncanon_litrpg_exploration",
            "next_high_information_experiment",
        },
        "claim-class separation",
    )
    rows = document.get("measured_fact", {}).get("route_matrix", [])
    check(len(rows) == 6, "route count")
    check(
        {row.get("route") for row in rows}
        == {
            "r6",
            "premium_cel",
            "clear_line_watercolor",
            "reduced_palette_text_control",
            "alt_graphic",
            "flat_graphic_gouache",
        },
        "route set",
    )
    rankings = document.get("engineering_inference", {}).get("ranked_routes", [])
    check([row.get("rank") for row in rankings] == [1, 2, 3, 4, 5, 6], "rank sequence")
    check(
        [row.get("route") for row in rankings]
        == [
            "r6",
            "premium_cel",
            "clear_line_watercolor",
            "reduced_palette_text_control",
            "alt_graphic",
            "flat_graphic_gouache",
        ],
        "route ranking",
    )
    check(
        all(row.get("not_a_quality_score") is True for row in rankings),
        "non-quality ranking boundary",
    )
    check(len(document.get("owner_review_question", [])) == 4, "owner question count")
    future = document.get("future_noncanon_litrpg_exploration", {})
    check(
        future.get("status")
        == "IDEATION_ONLY_NONCANON_NOT_AUTHORIZED_FOR_GENERATION_OR_PRODUCTION",
        "noncanon status",
    )
    check(len(future.get("ideas", [])) == 3, "noncanon idea count")
    experiment = document.get("next_high_information_experiment", {})
    check(experiment.get("count") == 1, "exactly one experiment")
    check(
        experiment.get("experiment_id")
        == "ch05-cadence-objective-sensitivity-audit-r1",
        "experiment id",
    )
    check(
        experiment.get("new_provider_needed") is False
        and experiment.get("new_upload_needed") is False
        and experiment.get("new_pixels_needed") is False
        and experiment.get("paid_spend_usd") == 0.0,
        "experiment authority boundary",
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
        "not a measured scalar score" in " ".join(document.get("limitations", [])),
        "inference limitation",
    )
    check(
        "no art acceptance" in document.get("boundary", "").lower(),
        "acceptance boundary",
    )
    check(
        "## Measured facts" in markdown
        and "## Engineering inference" in markdown
        and "## Owner-review questions" in markdown
        and "## Future noncanon LitRPG exploration" in markdown
        and "## Exactly one next experiment" in markdown,
        "Markdown claim-class sections",
    )
    return errors


def self_test(document: dict[str, Any], markdown: str) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "ACCEPTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("animation_shot_plan", {}),
        lambda value: value["inputs"][0].__setitem__("sha256", "0" * 64),
        lambda value: value["measured_fact"]["route_matrix"].pop(),
        lambda value: value["measured_fact"]["route_matrix"][0][
            "semantic_pass_warn_fail"
        ].__setitem__("fail", 0),
        lambda value: value["measured_fact"]["selected_review_cadence"].__setitem__(
            "accepted", 1
        ),
        lambda value: value["engineering_inference"]["ranked_routes"][0].__setitem__(
            "route", "premium_cel"
        ),
        lambda value: value["engineering_inference"]["ranked_routes"][0].__setitem__(
            "not_a_quality_score", False
        ),
        lambda value: value["owner_review_question"].pop(),
        lambda value: value["future_noncanon_litrpg_exploration"].__setitem__(
            "status", "CANON"
        ),
        lambda value: value["next_high_information_experiment"].__setitem__("count", 2),
        lambda value: value["next_high_information_experiment"].__setitem__(
            "new_provider_needed", True
        ),
        lambda value: value["next_high_information_experiment"].__setitem__(
            "paid_spend_usd", 1.0
        ),
        lambda value: value["disposition"].__setitem__("owner_acceptance", True),
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
