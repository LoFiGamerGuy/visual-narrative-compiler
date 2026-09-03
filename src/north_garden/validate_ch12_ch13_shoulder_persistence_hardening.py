"""Validate the CH12-CH13 irreversible-state hardening packet."""

from __future__ import annotations

import argparse
import copy
import json
from typing import Any

from build_ch12_ch13_shoulder_persistence_hardening import (
    EXECUTION,
    PROMPT_MANIFEST,
    REVIEW,
    ROOT,
    TARGETS,
    prompt_hash,
    sha256,
)
from PIL import Image


def validate(execution: dict[str, Any], review: dict[str, Any], *, files: bool) -> list[str]:
    errors = []
    record = execution.get("render_record", {})
    if record.get("input_references") != []:
        errors.append("hardening request must remain text-only")
    prompt_document = json.loads(PROMPT_MANIFEST.read_text(encoding="utf-8"))
    if record.get("prompt_sha256") != prompt_hash() or prompt_document.get("request", {}).get("prompt_sha256") != prompt_hash():
        errors.append("exact prompt hash differs")
    if execution.get("summary") != {"targets": 5, "candidates": 5, "triage": {"PASS": 5, "WARN": 0, "FAIL": 0}, "reference_uploads": 0, "paid_api_cloud_spend_usd": "0.000000"}:
        errors.append("execution summary differs")
    candidates = execution.get("candidates", [])
    if [row.get("target_panel_id") for row in candidates] != [row[0] for row in TARGETS]:
        errors.append("target order differs")
    if any(row.get("triage") != "PASS" or row.get("accepted") is not False for row in candidates):
        errors.append("candidate state differs")
    if review.get("summary") != execution.get("summary"):
        errors.append("review summary differs")
    artifacts = review.get("artifacts", [])
    if {row.get("type") for row in artifacts} != {"repair_strip", "baseline_repair_comparison"}:
        errors.append("two exact artifacts are required")
    if files:
        for binding in (execution.get("prompt_manifest", {}), record.get("output", {}), review.get("execution", {}), *candidates, *artifacts):
            path = ROOT / binding.get("path", "")
            if not path.is_file() or sha256(path) != binding.get("sha256"):
                errors.append(f"file binding failed: {binding.get('path')}")
        for artifact in artifacts:
            path = ROOT / artifact["path"]
            with Image.open(path) as opened:
                if [opened.width, opened.height] != artifact.get("dimensions"):
                    errors.append(f"artifact dimensions differ: {artifact.get('type')}")
    return errors


def self_test(execution: dict[str, Any], review: dict[str, Any]) -> tuple[int, int]:
    mutations = []
    changes = (
        lambda e, r: e["render_record"].__setitem__("input_references", ["forbidden"]),
        lambda e, r: e["summary"].__setitem__("targets", 4),
        lambda e, r: e["summary"].__setitem__("reference_uploads", 1),
        lambda e, r: e["summary"].__setitem__("paid_api_cloud_spend_usd", "1.000000"),
        lambda e, r: e["candidates"].reverse(),
        lambda e, r: e["candidates"][0].__setitem__("triage", "FAIL"),
        lambda e, r: e["candidates"][0].__setitem__("accepted", True),
        lambda e, r: r.__setitem__("summary", {}),
        lambda e, r: r["artifacts"].pop(),
        lambda e, r: r["artifacts"][0].__setitem__("type", "other"),
    )
    for change in changes:
        changed_execution, changed_review = copy.deepcopy(execution), copy.deepcopy(review)
        change(changed_execution, changed_review)
        mutations.append(bool(validate(changed_execution, changed_review, files=False)))
    return sum(mutations), len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    errors = validate(execution, review, files=True)
    result: dict[str, Any] = {"status": "PASS" if not errors else "FAIL", "errors": errors}
    if args.self_test and not errors:
        rejected, total = self_test(execution, review)
        result["self_test"] = f"{rejected}/{total}"
        if rejected != total:
            result["status"] = "FAIL"
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
