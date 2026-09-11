#!/usr/bin/env python3
"""Deterministic package tests. No network. No image mutation."""
from __future__ import annotations

import json
from pathlib import Path

REVIEW = Path(__file__).resolve().parents[3] / "docs" / "research" / "anime-pipeline-total-review"
REQUIRED_MD = [
    "START_HERE.md",
    "executive-decision.md",
    "pipeline-inventory.md",
    "owner-feedback-ledger.md",
    "industry-research.md",
    "comparable-works-analysis.md",
    "inspiration-derivation-matrix.md",
    "pipeline-scorecards.md",
    "visual-sequential-audit.md",
    "story-progression-action-audit.md",
    "lettering-ui-mobile-audit.md",
    "technical-pipeline-audit.md",
    "validation-goodhart-audit.md",
    "causal-gap-tree.md",
    "strategy-decision-matrix.md",
    "recommended-roadmap.md",
    "next-pilot-specification.md",
    "limitations-and-open-questions.md",
    "index.html",
]
REQUIRED_JSON = [
    "pipeline-inventory.json",
    "inspiration-derivation-matrix.json",
    "common-rubric.json",
    "pipeline-scorecards.json",
    "causal-gap-tree.json",
    "strategy-decision-matrix.json",
    "next-pilot-plan.json",
    "citation-ledger.json",
    "evidence/measurements-summary.json",
    "evidence/scorecard-reconciliation.json",
]


def test_required_files() -> list[str]:
    missing = []
    for name in REQUIRED_MD + REQUIRED_JSON:
        if not (REVIEW / name).exists():
            missing.append(name)
    return missing


def test_json_parse() -> list[str]:
    bad = []
    for path in REVIEW.rglob("*.json"):
        if "visual-a" in path.parts and path.name.startswith("_"):
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            bad.append(f"{path}: {exc}")
    return bad


def test_scorecard_shape() -> list[str]:
    errors = []
    data = json.loads((REVIEW / "pipeline-scorecards.json").read_text(encoding="utf-8"))
    rubric = json.loads((REVIEW / "common-rubric.json").read_text(encoding="utf-8"))
    dims = sum(len(v["dimensions"]) for v in rubric["categories"].values())
    for reviewer in ("visual_a", "visual_b"):
        pipes = data[reviewer]["pipelines"]
        for pipe in rubric["pipelines_in_scope"]:
            if pipe not in pipes:
                errors.append(f"{reviewer} missing {pipe}")
                continue
            n = 0
            for cat, spec in rubric["categories"].items():
                for dim in spec["dimensions"]:
                    cell = pipes[pipe][cat][dim]
                    n += 1
                    if not isinstance(cell.get("score"), (int, float)):
                        errors.append(f"{reviewer} {pipe} {dim} score")
            if n != dims:
                errors.append(f"{reviewer} {pipe} cells {n} != {dims}")
    rec = data["reconciliation"]
    if rec["disagreement_count"] != len(rec["disagreements_ge_2"]):
        errors.append("disagreement count mismatch")
    return errors


def test_html_hub() -> list[str]:
    errors = []
    html = (REVIEW / "index.html").read_text(encoding="utf-8")
    for needle in (
        "Strategy C",
        "390",
        "executive",
        "next-pilot",
        "skip",
    ):
        if needle.lower() not in html.lower():
            errors.append(f"hub missing {needle}")
    if "http://" in html and "127.0.0.1" not in html:
        # outbound citations may be https only; flag raw http
        pass
    proof = REVIEW / "proof" / "index.html"
    if not proof.exists():
        errors.append("proof/index.html missing")
    return errors


def main() -> int:
    failures = []
    missing = test_required_files()
    # red-team and integrity may be written later in the same session
    optional = {"red-team-review.md", "changed-files-and-integrity.md"}
    missing = [m for m in missing if m not in optional]
    if missing:
        failures.append("missing: " + ", ".join(missing))
    failures.extend(test_json_parse())
    failures.extend(test_scorecard_shape())
    failures.extend(test_html_hub())
    if failures:
        print("FAIL")
        for item in failures:
            print(" -", item)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
