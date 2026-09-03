"""Compile the null CH05 owner-review response template."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MARKDOWN_OUT = ROOT / "docs/research/ch05-final-owner-review-response-template-r1.md"
JSON_OUT = (
    ROOT / "docs/research/evidence/ch05-final-owner-review-response-template-r1.json"
)
START_HERE = ROOT / "docs/research/ch05-final-owner-start-here-r1.md"
START_HERE_SHA256 = "93979b19b7c84f510fd676cbe2c835b6ddb8f7c133016a92c541bb36fe6a674f"

QUESTIONS = (
    (
        "overall_three_block_cadence",
        "Overall three-block cadence",
        "Retain, revise, or reject reduced-palette S01 / R6 S02-S08 / premium-cel S09-S11? State the smallest useful revision.",
    ),
    (
        "p003",
        "P003 warning",
        "Pass, revise, or replace P003? Note the visible issue and desired change.",
    ),
    (
        "p032",
        "P032 warning",
        "Pass, revise, or replace P032? Note the visible issue and desired change.",
    ),
    (
        "p045",
        "P045 warning",
        "Pass, revise, or replace P045? Note the visible issue and desired change.",
    ),
    (
        "p005_p006",
        "P005-P006 boundary",
        "Does the route/finish transition read as intentional? If not, identify which side should change.",
    ),
    (
        "lettering_clearance_readability",
        "Lettering clearance and readability",
        "Are faces, people, important hands, story objects, and phone-size reading preserved? List exact panels needing changes.",
    ),
    (
        "strongest_candidate_disposition",
        "Strongest-candidate disposition",
        "Which candidates should remain shortlisted, be revised, or be removed from consideration? Visual disposition only.",
    ),
    (
        "s10_s11_premium_vs_r6",
        "S10-S11 premium versus R6",
        "Prefer premium cel, R6, or a targeted mix for S10-S11? Identify the narrative or continuity reason.",
    ),
    (
        "noncanon_litrpg_direction",
        "Noncanon LitRPG direction",
        "Which armor, weapon, monster, clothing, action, or style ideas merit a future canon proposal? This answer does not change canon.",
    ),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_documents() -> tuple[dict[str, Any], str]:
    if not START_HERE.is_file() or sha256(START_HERE) != START_HERE_SHA256:
        raise ValueError("final owner start-here binding mismatch")
    reviews = [
        {"id": question_id, "label": label, "prompt": prompt, "response": None}
        for question_id, label, prompt in QUESTIONS
    ]
    document: dict[str, Any] = {
        "record_type": "CH05FinalOwnerReviewResponseTemplate",
        "schema_version": "1.0",
        "record_id": "ng-ch05-final-owner-review-response-template-r1",
        "state": "OWNER_INPUT_NOT_RECORDED",
        "source_start_here": {
            "path": START_HERE.relative_to(ROOT).as_posix(),
            "absolute_path": START_HERE.resolve().as_posix(),
            "sha256": START_HERE_SHA256,
            "visual_artifact_count": 10,
        },
        "visual_review_responses": reviews,
        "rights_decision": {
            "commercial_rights_clearance": None,
            "scope": None,
            "rationale": None,
        },
        "exact_production_base_decision": {
            "approved": None,
            "candidate_ids": None,
            "scope": None,
            "rationale": None,
        },
        "authority_boundary": {
            "review_feedback_only": True,
            "grants_ingestion_authority": False,
            "grants_execution_authority": False,
            "grants_provider_authority": False,
            "grants_upload_authority": False,
            "grants_spend_authority": False,
            "grants_canon_promotion": False,
        },
        "activity_boundary": {
            "new_pixels": 0,
            "provider_calls": 0,
            "uploads": 0,
            "paid_spend_usd": 0.0,
        },
        "instructions": "Replace only response/decision nulls after explicit owner input. A completed form remains review feedback and must be separately ingested through an authorized workflow before any execution.",
    }

    question_lines: list[str] = []
    for index, row in enumerate(reviews, start=1):
        question_lines.extend(
            [
                f"{index}. **{row['label']}** — {row['prompt']}",
                "   Response: `null`",
                "",
            ]
        )
    markdown = "\n".join(
        [
            "# CH05 final owner-review response template",
            "",
            f"Review source: [ten-visual CH05 start page]({START_HERE.resolve().as_posix()}) (SHA-256 `{START_HERE_SHA256}`).",
            "",
            "Copy this page into a new response record only when recording explicit owner feedback. Every response below is intentionally `null`.",
            "",
            "## Visual review",
            "",
            *question_lines,
            "## Separate rights decision",
            "",
            "- Commercial-rights clearance: `null`",
            "- Scope: `null`",
            "- Rationale: `null`",
            "",
            "## Separate exact-production-base decision",
            "",
            "- Approved: `null`",
            "- Candidate IDs: `null`",
            "- Scope: `null`",
            "- Rationale: `null`",
            "",
            "## Authority boundary",
            "",
            "This template records review feedback only. It grants no ingestion, execution, provider, upload, spend, rights-clearance, exact-base, or canon-promotion authority. Any later non-null response must be explicitly ingested through a separately authorized workflow before it can affect production.",
            "",
            "Machine-readable template: `docs/research/evidence/ch05-final-owner-review-response-template-r1.json`.",
            "",
        ]
    )
    return document, markdown


def main() -> int:
    document, markdown = build_documents()
    MARKDOWN_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_OUT.write_text(markdown, encoding="utf-8", newline="\n")
    JSON_OUT.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "json": JSON_OUT.relative_to(ROOT).as_posix(),
                "json_sha256": sha256(JSON_OUT),
                "markdown": MARKDOWN_OUT.relative_to(ROOT).as_posix(),
                "markdown_sha256": sha256(MARKDOWN_OUT),
                "null_visual_responses": len(
                    reviews := document["visual_review_responses"]
                ),
                "all_visual_responses_null": all(
                    row["response"] is None for row in reviews
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
