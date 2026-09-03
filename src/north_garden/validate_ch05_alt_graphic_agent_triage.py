"""Validate alternate graphic CH05 non-gating triage."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TRIAGE = ROOT / "docs/research/evidence/ch05-complete-chapter-alt-graphic-agent-triage-r1.json"
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(doc: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    check(doc.get("record_type") == "CH05CompleteChapterAgentTriage", "record_type")
    check(doc.get("state") == "NON_GATING_AGENT_TRIAGE_PENDING_OWNER_REVIEW", "state")
    check(doc.get("planning_structure") == "ComicPanelPlan" and doc.get("animation_shot_plan") is None and doc.get("e_conte") is None, "planning boundary")
    rows = doc.get("rows", [])
    expected = [row["panel_id"] for row in json.loads(PLAN.read_text(encoding="utf-8"))["plans"]]
    check(len(rows) == 50 and [row.get("panel_id") for row in rows] == expected, "ordered coverage")
    counts = {status: sum(row.get("status") == status for row in rows) for status in ("PASS", "WARN", "FAIL")}
    check(counts == {"PASS": 36, "WARN": 7, "FAIL": 7}, "status counts")
    check(doc.get("summary", {}).get("pass") == 36 and doc.get("summary", {}).get("warn") == 7 and doc.get("summary", {}).get("fail") == 7, "summary counts")
    check(doc.get("summary", {}).get("hair_and_wardrobe_pass") == 50, "continuity count")
    check([row["display_order"] for row in rows if row.get("status") == "FAIL"] == [1, 29, 32, 36, 39, 41, 43], "failure set")
    check(doc.get("style_hypothesis_result", {}).get("result") == "NON_SEPARATING", "style result")
    check(all(row.get("human_review_state") == "PENDING" and row.get("human_review_minutes") is None and row.get("accepted") is False and row.get("commercially_cleared") is False and row.get("exact_production_base") is False for row in rows), "decision boundary")
    if verify_files:
        for source in doc.get("inputs", []):
            path = ROOT / source.get("path", "")
            check(path.is_file() and sha256(path) == source.get("sha256"), f"input binding {source.get('path')}")
    return errors


def self_test(doc: dict[str, Any]) -> tuple[int, int]:
    mutations = [lambda d: d.__setitem__("state", "ACCEPTED"), lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"), lambda d: d["rows"].pop(), lambda d: d["rows"][0].__setitem__("panel_id", "wrong"), lambda d: d["rows"][0].__setitem__("status", "PASS"), lambda d: d["summary"].__setitem__("fail", 0), lambda d: d["summary"].__setitem__("hair_and_wardrobe_pass", 49), lambda d: d["rows"][0].__setitem__("accepted", True), lambda d: d["style_hypothesis_result"].__setitem__("result", "WIN")]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(doc); mutation(candidate); caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args()
    doc = json.loads(TRIAGE.read_text(encoding="utf-8")); errors = validate(doc); caught = total = 0
    if args.self_test:
        caught, total = self_test(doc)
        if caught != total: errors.append(f"self-test {caught}/{total}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__": raise SystemExit(main())
