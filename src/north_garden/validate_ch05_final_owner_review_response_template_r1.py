"""Validate the null CH05 final owner-review response template."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from compile_ch05_final_owner_review_response_template_r1 import (
    JSON_OUT,
    MARKDOWN_OUT,
    QUESTIONS,
    START_HERE,
    START_HERE_SHA256,
    build_documents,
)


class ValidationError(ValueError):
    """Raised when the response template violates a required invariant."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def response_values(document: dict[str, Any]) -> list[Any]:
    return (
        [row.get("response") for row in document.get("visual_review_responses", [])]
        + list(document.get("rights_decision", {}).values())
        + list(document.get("exact_production_base_decision", {}).values())
    )


def validate_document(document: dict[str, Any]) -> None:
    require(
        document.get("record_type") == "CH05FinalOwnerReviewResponseTemplate",
        "record type drift",
    )
    require(document.get("state") == "OWNER_INPUT_NOT_RECORDED", "template state drift")
    source = document.get("source_start_here", {})
    require(
        source.get("path") == "docs/research/ch05-final-owner-start-here-r1.md",
        "start-page path drift",
    )
    require(
        source.get("absolute_path") == START_HERE.resolve().as_posix(),
        "absolute start-page path drift",
    )
    require(
        source.get("sha256") == START_HERE_SHA256, "start-page hash declaration drift"
    )
    require(source.get("visual_artifact_count") == 10, "start-page visual count drift")
    require(
        START_HERE.is_file() and sha256(START_HERE) == START_HERE_SHA256,
        "bound start page changed",
    )

    reviews = document.get("visual_review_responses", [])
    require(len(reviews) == 9, "exactly nine visual review responses are required")
    require(
        [row.get("id") for row in reviews] == [row[0] for row in QUESTIONS],
        "review ids or order drift",
    )
    for row, expected in zip(reviews, QUESTIONS):
        require(row.get("label") == expected[1], f"review label drift: {expected[0]}")
        require(row.get("prompt") == expected[2], f"review prompt drift: {expected[0]}")
        require(
            row.get("response") is None,
            f"visual response must remain null: {expected[0]}",
        )

    require(
        set(document.get("rights_decision", {}))
        == {"commercial_rights_clearance", "scope", "rationale"},
        "rights fields drift",
    )
    require(
        set(document.get("exact_production_base_decision", {}))
        == {"approved", "candidate_ids", "scope", "rationale"},
        "exact-base fields drift",
    )
    values = response_values(document)
    require(
        len(values) == 16 and all(value is None for value in values),
        "all response and decision values must remain null",
    )

    require(
        document.get("authority_boundary")
        == {
            "review_feedback_only": True,
            "grants_ingestion_authority": False,
            "grants_execution_authority": False,
            "grants_provider_authority": False,
            "grants_upload_authority": False,
            "grants_spend_authority": False,
            "grants_canon_promotion": False,
        },
        "authority boundary drift",
    )
    require(
        document.get("activity_boundary")
        == {"new_pixels": 0, "provider_calls": 0, "uploads": 0, "paid_spend_usd": 0.0},
        "activity boundary drift",
    )
    require(
        "separately ingested through an authorized workflow"
        in document.get("instructions", ""),
        "separate-ingestion instruction missing",
    )


def validate_markdown(markdown: str) -> None:
    required = (
        "## Visual review",
        "Overall three-block cadence",
        "P003 warning",
        "P032 warning",
        "P045 warning",
        "P005-P006 boundary",
        "Lettering clearance and readability",
        "Strongest-candidate disposition",
        "S10-S11 premium versus R6",
        "Noncanon LitRPG direction",
        "## Separate rights decision",
        "## Separate exact-production-base decision",
        "## Authority boundary",
        "no ingestion, execution, provider, upload, spend, rights-clearance, exact-base, or canon-promotion authority",
        START_HERE.resolve().as_posix(),
        START_HERE_SHA256,
    )
    for token in required:
        require(token in markdown, f"required Markdown token missing: {token}")
    require(
        markdown.count("Response: `null`") == 9,
        "Markdown must expose nine null visual responses",
    )
    require(
        markdown.count("- Commercial-rights clearance: `null`") == 1,
        "commercial-rights null missing",
    )
    require(markdown.count("- Approved: `null`") == 1, "exact-base null missing")


def mutation_tests(document: dict[str, Any], markdown: str) -> int:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("state", lambda d: d.__setitem__("state", "OWNER_INPUT_RECORDED")),
        (
            "source_hash",
            lambda d: d["source_start_here"].__setitem__("sha256", "0" * 64),
        ),
        (
            "visual_count",
            lambda d: d["source_start_here"].__setitem__("visual_artifact_count", 9),
        ),
        ("review_missing", lambda d: d["visual_review_responses"].pop()),
        ("review_reordered", lambda d: d["visual_review_responses"].reverse()),
        (
            "review_prompt",
            lambda d: d["visual_review_responses"][0].__setitem__("prompt", "changed"),
        ),
        (
            "cadence_response",
            lambda d: d["visual_review_responses"][0].__setitem__("response", "retain"),
        ),
        (
            "panel_response",
            lambda d: d["visual_review_responses"][1].__setitem__("response", "pass"),
        ),
        (
            "litrpg_response",
            lambda d: d["visual_review_responses"][8].__setitem__(
                "response", "promote"
            ),
        ),
        (
            "rights_response",
            lambda d: d["rights_decision"].__setitem__(
                "commercial_rights_clearance", True
            ),
        ),
        ("rights_field", lambda d: d["rights_decision"].__setitem__("new_field", None)),
        (
            "exact_base_response",
            lambda d: d["exact_production_base_decision"].__setitem__("approved", True),
        ),
        (
            "exact_base_ids",
            lambda d: d["exact_production_base_decision"].__setitem__(
                "candidate_ids", []
            ),
        ),
        (
            "ingestion_authority",
            lambda d: d["authority_boundary"].__setitem__(
                "grants_ingestion_authority", True
            ),
        ),
        (
            "execution_authority",
            lambda d: d["authority_boundary"].__setitem__(
                "grants_execution_authority", True
            ),
        ),
        (
            "provider_authority",
            lambda d: d["authority_boundary"].__setitem__(
                "grants_provider_authority", True
            ),
        ),
        (
            "upload_authority",
            lambda d: d["authority_boundary"].__setitem__(
                "grants_upload_authority", True
            ),
        ),
        (
            "spend_authority",
            lambda d: d["authority_boundary"].__setitem__(
                "grants_spend_authority", True
            ),
        ),
        (
            "canon_authority",
            lambda d: d["authority_boundary"].__setitem__(
                "grants_canon_promotion", True
            ),
        ),
        (
            "provider_call",
            lambda d: d["activity_boundary"].__setitem__("provider_calls", 1),
        ),
        ("upload", lambda d: d["activity_boundary"].__setitem__("uploads", 1)),
        ("spend", lambda d: d["activity_boundary"].__setitem__("paid_spend_usd", 1.0)),
    ]
    caught = 0
    for name, mutate in mutations:
        candidate = copy.deepcopy(document)
        mutate(candidate)
        try:
            validate_document(candidate)
        except ValidationError:
            caught += 1
        else:
            raise ValidationError(f"mutation was not caught: {name}")
    try:
        validate_markdown(markdown.replace("Response: `null`", "Response: retain", 1))
    except ValidationError:
        caught += 1
    else:
        raise ValidationError("Markdown response mutation was not caught")
    return caught


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    expected_document, expected_markdown = build_documents()
    require(
        JSON_OUT.is_file() and MARKDOWN_OUT.is_file(),
        "compiled response template is missing",
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
    validate_markdown(observed_markdown)
    caught = (
        mutation_tests(observed_document, observed_markdown) if args.self_test else 0
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "visual_response_fields": 9,
                "response_and_decision_nulls": len(response_values(observed_document)),
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
