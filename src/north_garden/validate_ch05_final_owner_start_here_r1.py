"""Validate the final CH05 owner start-here packet and its ignored visuals."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from compile_ch05_final_owner_start_here_r1 import (
    DOCUMENTS,
    GIT_COMMIT,
    GIT_URL,
    JSON_OUT,
    MARKDOWN_OUT,
    ROOT,
    VISUALS,
    build_documents,
)
from PIL import Image


class ValidationError(ValueError):
    """Raised when an owner-start-here invariant is violated."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_document(document: dict[str, Any]) -> None:
    require(
        document.get("record_type") == "CH05FinalOwnerStartHere", "record type drift"
    )
    require(
        document.get("state") == "LOCAL_OWNER_REVIEW_START_READY_DECISIONS_PENDING",
        "state drift",
    )
    require(document.get("medium") == "comic", "medium drift")
    require(
        document.get("planning_structure") == "ComicPanelPlan",
        "planning structure drift",
    )
    require(
        document.get("animation_shot_plan") is None,
        "AnimationShotPlan must remain null",
    )
    require(document.get("e_conte") is None, "E-Conte must remain null")

    expected_visuals = {row[0]: row for row in VISUALS}
    visuals = document.get("visual_review_set", [])
    require(len(visuals) == 10, "visual review set must contain exactly ten artifacts")
    require(
        [row.get("id") for row in visuals] == [row[0] for row in VISUALS],
        "visual order or ids drift",
    )
    require(
        len({row.get("path") for row in visuals}) == 10, "visual paths must be unique"
    )
    for row in visuals:
        expected = expected_visuals[row["id"]]
        path = ROOT / expected[2]
        require(row.get("path") == expected[2], f"visual path drift: {row['id']}")
        require(
            row.get("absolute_path") == path.resolve().as_posix(),
            f"absolute visual path drift: {row['id']}",
        )
        require(path.is_file(), f"missing visual: {row['id']}")
        observed_hash = sha256(path)
        with Image.open(path) as image:
            observed_dimensions = list(image.size)
        require(
            row.get("sha256") == expected[3] == observed_hash,
            f"visual hash drift: {row['id']}",
        )
        require(
            [row.get("width"), row.get("height")]
            == [expected[4], expected[5]]
            == observed_dimensions,
            f"visual dimensions drift: {row['id']}",
        )
        require(
            row.get("bytes") == path.stat().st_size,
            f"visual byte count drift: {row['id']}",
        )
        require(
            row.get("repository_state") == "IGNORED_LOCAL_REVIEW_ARTIFACT",
            f"visual repository state drift: {row['id']}",
        )
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", "--", expected[2]], cwd=ROOT, check=False
        )
        require(ignored.returncode == 0, f"visual is not ignored: {row['id']}")

    expected_documents = {row[0]: row for row in DOCUMENTS}
    supporting = document.get("supporting_documents", [])
    require(
        len(supporting) == 7,
        "supporting document set must contain exactly seven records",
    )
    require(
        [row.get("id") for row in supporting] == [row[0] for row in DOCUMENTS],
        "supporting document order or ids drift",
    )
    for row in supporting:
        expected = expected_documents[row["id"]]
        path = ROOT / expected[2]
        require(row.get("path") == expected[2], f"supporting path drift: {row['id']}")
        require(
            row.get("absolute_path") == path.resolve().as_posix(),
            f"absolute supporting path drift: {row['id']}",
        )
        require(path.is_file(), f"missing supporting document: {row['id']}")
        require(
            row.get("sha256") == expected[3] == sha256(path),
            f"supporting hash drift: {row['id']}",
        )
        require(
            row.get("bytes") == path.stat().st_size,
            f"supporting byte count drift: {row['id']}",
        )

    checkpoint = document.get("git_checkpoint", {})
    require(checkpoint.get("commit") == GIT_COMMIT, "Git commit drift")
    require(checkpoint.get("short_commit") == "fa8d1ed", "short Git commit drift")
    require(checkpoint.get("url") == GIT_URL, "Git URL drift")
    commit = subprocess.run(
        ["git", "rev-parse", f"{GIT_COMMIT}^{{commit}}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    require(commit == GIT_COMMIT, "bound Git commit does not resolve exactly")

    require(
        document.get("measured_counts")
        == {
            "service_raster_outputs": 76,
            "panel_level_candidates_or_crops": 312,
            "authorized_reference_uses": 132,
            "zero_reference_outputs": 13,
            "unsplit_ablation_diagnostics": 2,
        },
        "measured counts drift",
    )

    cadence = document.get("selected_cadence", {})
    require(
        cadence.get("assignment")
        == {
            "S01": "reduced_palette_text_control",
            "S02-S08": "r6",
            "S09-S11": "premium_cel",
        },
        "cadence assignment drift",
    )
    require(
        [
            cadence.get("semantic_pass"),
            cadence.get("semantic_warn"),
            cadence.get("semantic_fail"),
            cadence.get("route_transitions"),
        ]
        == [47, 3, 0, 2],
        "cadence measurements drift",
    )
    require(
        cadence.get("warning_panel_ids") == ["P003", "P032", "P045"],
        "warning panels drift",
    )
    require(
        cadence.get("finish_review_question") == "P005-to-P006",
        "finish boundary question drift",
    )

    ranking = document.get("ranked_recommendation", [])
    require(
        [row.get("rank") for row in ranking] == [1, 2, 3, 4, 5, 6], "route ranks drift"
    )
    require(
        [row.get("route") for row in ranking]
        == [
            "r6",
            "premium_cel",
            "clear_line_watercolor",
            "reduced_palette_text_control",
            "alt_graphic",
            "flat_graphic_gouache",
        ],
        "route order drift",
    )

    decisions = document.get("decision_separation", {})
    require(
        len(decisions.get("visual_decisions_now", [])) == 3,
        "visual decisions must remain explicit",
    )
    require(
        len(decisions.get("rights_and_exact_base_decisions_later", [])) == 3,
        "rights/exact-base decisions must remain separate",
    )
    disposition = document.get("disposition", {})
    require(
        disposition
        == {
            "owner_visual_decisions_recorded": 0,
            "accepted": 0,
            "rights_cleared": 0,
            "commercially_cleared": 0,
            "canon_promoted": 0,
            "exact_production_base": 0,
        },
        "disposition must remain null/zero",
    )

    timing = document.get("timing_and_spend", {})
    require(
        timing.get("aggregate_end_to_end_art_production_seconds") is None,
        "aggregate art-production time must remain unavailable",
    )
    require(
        timing.get("closeout_validation_observed_seconds") == 42.965392,
        "closeout validation timing drift",
    )
    require(
        timing.get("closeout_validation_is_not_art_production_time") is True,
        "validation time must not be recast as production time",
    )
    require(timing.get("direct_paid_api_cloud_usd") == 0.0, "direct paid spend drift")
    require(
        timing.get("built_in_product_monetary_cost_usd") is None,
        "built-in monetary cost must remain unavailable",
    )
    require(
        timing.get("service_metadata_unavailable")
        == ["model", "endpoint", "provider_request_id", "usage", "deterministic_seed"],
        "unavailable service metadata drift",
    )
    require(
        document.get("activity_boundary")
        == {"new_pixels": 0, "provider_calls": 0, "uploads": 0, "paid_spend_usd": 0.0},
        "activity boundary drift",
    )


def validate_markdown(markdown: str, document: dict[str, Any]) -> None:
    require(
        markdown.count("experiments/review-packets/") == 10,
        "Markdown must link exactly ten review artifacts",
    )
    for row in document["visual_review_set"]:
        require(
            f"]({row['absolute_path']})" in markdown,
            f"missing visual link: {row['id']}",
        )
        require(row["sha256"] in markdown, f"missing visual hash: {row['id']}")
    for row in document["supporting_documents"]:
        require(
            f"]({row['absolute_path']})" in markdown,
            f"missing supporting link: {row['id']}",
        )
    for token in (
        "| 76 | 312 | 132 | 13 | 2 |",
        "42.965392 seconds",
        "Direct paid API/cloud spend is $0",
        "### Visual review now",
        "### Rights and exact-base authority later",
        GIT_URL,
    ):
        require(token in markdown, f"required owner-facing token missing: {token}")


def mutation_tests(document: dict[str, Any], markdown: str) -> int:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("state", lambda d: d.__setitem__("state", "ACCEPTED")),
        (
            "planning",
            lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"),
        ),
        ("animation", lambda d: d.__setitem__("animation_shot_plan", {})),
        (
            "visual_hash",
            lambda d: d["visual_review_set"][0].__setitem__("sha256", "0" * 64),
        ),
        ("visual_width", lambda d: d["visual_review_set"][1].__setitem__("width", 391)),
        (
            "visual_path",
            lambda d: d["visual_review_set"][2].__setitem__("path", "wrong.png"),
        ),
        ("visual_missing", lambda d: d["visual_review_set"].pop()),
        (
            "document_hash",
            lambda d: d["supporting_documents"][0].__setitem__("sha256", "0" * 64),
        ),
        ("document_missing", lambda d: d["supporting_documents"].pop()),
        ("commit", lambda d: d["git_checkpoint"].__setitem__("commit", "0" * 40)),
        (
            "service_count",
            lambda d: d["measured_counts"].__setitem__("service_raster_outputs", 77),
        ),
        (
            "candidate_count",
            lambda d: d["measured_counts"].__setitem__(
                "panel_level_candidates_or_crops", 311
            ),
        ),
        (
            "reference_count",
            lambda d: d["measured_counts"].__setitem__(
                "authorized_reference_uses", 131
            ),
        ),
        (
            "zero_reference_count",
            lambda d: d["measured_counts"].__setitem__("zero_reference_outputs", 12),
        ),
        (
            "diagnostic_count",
            lambda d: d["measured_counts"].__setitem__(
                "unsplit_ablation_diagnostics", 1
            ),
        ),
        (
            "cadence_fail",
            lambda d: d["selected_cadence"].__setitem__("semantic_fail", 1),
        ),
        (
            "cadence_route",
            lambda d: d["selected_cadence"]["assignment"].__setitem__(
                "S02-S08", "premium_cel"
            ),
        ),
        (
            "ranking",
            lambda d: d["ranked_recommendation"][0].__setitem__("route", "premium_cel"),
        ),
        (
            "decision_split",
            lambda d: d["decision_separation"].__setitem__(
                "rights_and_exact_base_decisions_later", []
            ),
        ),
        (
            "production_time",
            lambda d: d["timing_and_spend"].__setitem__(
                "aggregate_end_to_end_art_production_seconds", 42.965392
            ),
        ),
        (
            "spend",
            lambda d: d["timing_and_spend"].__setitem__(
                "direct_paid_api_cloud_usd", 1.0
            ),
        ),
        ("rights", lambda d: d["disposition"].__setitem__("rights_cleared", 1)),
        (
            "exact_base",
            lambda d: d["disposition"].__setitem__("exact_production_base", 1),
        ),
        ("upload", lambda d: d["activity_boundary"].__setitem__("uploads", 1)),
    ]
    caught = 0
    for name, mutate in mutations:
        candidate = copy.deepcopy(document)
        mutate(candidate)
        try:
            validate_document(candidate)
        except (ValidationError, KeyError):
            caught += 1
        else:
            raise ValidationError(f"mutation was not caught: {name}")
    try:
        validate_markdown(
            markdown.replace(
                "| 76 | 312 | 132 | 13 | 2 |", "| 76 | 311 | 132 | 13 | 2 |"
            ),
            document,
        )
    except ValidationError:
        caught += 1
    else:
        raise ValidationError("Markdown count mutation was not caught")
    return caught


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    expected_document, expected_markdown = build_documents()
    require(
        JSON_OUT.is_file() and MARKDOWN_OUT.is_file(),
        "compiled owner packet is missing",
    )
    observed_document = json.loads(JSON_OUT.read_text(encoding="utf-8"))
    observed_markdown = MARKDOWN_OUT.read_text(encoding="utf-8")
    require(
        observed_document == expected_document,
        "compiled JSON is stale or nondeterministic",
    )
    require(
        observed_markdown == expected_markdown,
        "compiled Markdown is stale or nondeterministic",
    )
    validate_document(observed_document)
    validate_markdown(observed_markdown, observed_document)
    caught = (
        mutation_tests(observed_document, observed_markdown) if args.self_test else 0
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "visuals": 10,
                "supporting_documents": 7,
                "mutations_caught": caught,
                "json_sha256": sha256(JSON_OUT),
                "markdown_sha256": sha256(MARKDOWN_OUT),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
