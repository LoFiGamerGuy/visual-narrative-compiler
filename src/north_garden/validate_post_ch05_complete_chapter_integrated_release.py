"""Validate the post-CH05 integrated release record and its command bindings."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "docs/research/evidence/post-ch05-complete-chapter-integrated-release-r1.json"
EXPECTED_PATHS = [
    "src/north_garden/validate_ch05_complete_chapter_release_r6.py",
    "src/north_garden/validate_comic_panel_plan_chapter_inventory.py",
    "src/north_garden/validate_cross_chapter_comic_regression.py",
    "src/north_garden/validate_complete_chapter_comicpanelplan_authoring_contract.py",
    "src/north_garden/validate_complete_chapter_semantic_graph.py",
    "src/north_garden/validate_ch05_complete_chapter.py",
    "src/north_garden/build_ch05_complete_chapter_review.py",
    "src/north_garden/validate_frozen_gauntlet_baseline_integrity.py",
    "src/north_garden/validate_tracked_source_scope.py",
    "src/north_garden/validate_current_git_remote_parity.py",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(doc: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    check(doc.get("record_type") == "PostCH05CompleteChapterIntegratedRelease", "record_type")
    check(doc.get("state") == "PASS", "state")
    check(doc.get("planning_structure") == "ComicPanelPlan", "planning_structure")
    check(doc.get("animation_shot_plan") is None and doc.get("e_conte") is None, "cross-medium fields")
    summary = doc.get("summary", {})
    expected = {
        "orchestrator_commands": 10, "passed": 10, "failed": 0, "effective_checks": 93,
        "network_capable_commands": 0, "ch05_selected_panels": 50, "ch05_candidates": 59,
        "chapter_inventory_plans": 63, "cross_chapter_review_panels": 23,
        "authoring_contract_mutations_rejected": 15, "semantic_graph_mutations_rejected": 23,
        "provider_calls": 0, "uploads": 0, "new_generation": 0, "accepted": 0,
        "commercial_decisions": 0, "paid_spend_usd": 0,
    }
    for key, value in expected.items():
        check(summary.get(key) == value, f"summary.{key}")
    check(summary.get("ch05_agent_triage") == {"pass": 49, "warn": 1, "fail": 0, "gating": False}, "summary.ch05_agent_triage")
    check(summary.get("human_review_minutes") is None, "summary.human_review_minutes")
    check(isinstance(summary.get("observed_total_seconds"), (int, float)) and summary.get("observed_total_seconds", 0) > 0, "summary.observed_total_seconds")
    results = doc.get("results", [])
    check(len(results) == 10, "result count")
    check([row.get("path") for row in results] == EXPECTED_PATHS, "result path order")
    check(all(row.get("return_code") == 0 for row in results), "result return codes")
    check(all(row.get("network_capable") is False for row in results), "network capability")
    check(sum(row.get("expected_effective_checks", 0) for row in results) == 93, "effective check sum")
    check(all(row.get("stderr") == "" for row in results), "stderr")
    for row in results:
        stdout = row.get("stdout", "")
        check(hashlib.sha256(stdout.encode("utf-8")).hexdigest() == row.get("stdout_sha256"), f"stdout hash {row.get('path')}")
        check(isinstance(row.get("elapsed_seconds"), (int, float)) and row.get("elapsed_seconds", -1) >= 0, f"elapsed {row.get('path')}")
        if verify_files:
            path = ROOT / row.get("path", "")
            check(path.is_file(), f"script missing {row.get('path')}")
            if path.is_file():
                check(sha256(path) == row.get("script_sha256"), f"script hash {row.get('path')}")
    parity = results[-1].get("stdout", "") if results else ""
    check('"head_equals_origin_main": true' in parity and '"status": "PASS"' in parity, "remote parity stdout")
    check("0 failures, 0 warnings (16 frozen + 4 baseline" in (results[7].get("stdout", "") if len(results) > 7 else ""), "frozen stdout")
    return errors


def self_test(doc: dict[str, Any]) -> tuple[int, int]:
    mutations = [
        lambda d: d.__setitem__("state", "FAIL"),
        lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda d: d.__setitem__("animation_shot_plan", {}),
        lambda d: d["summary"].__setitem__("passed", 9),
        lambda d: d["summary"].__setitem__("effective_checks", 92),
        lambda d: d["summary"].__setitem__("accepted", 1),
        lambda d: d["summary"].__setitem__("provider_calls", 1),
        lambda d: d["results"].pop(),
        lambda d: d["results"][0].__setitem__("return_code", 1),
        lambda d: d["results"][0].__setitem__("network_capable", True),
        lambda d: d["results"][0].__setitem__("stdout", "tampered"),
        lambda d: d["results"][-1].__setitem__("stdout", d["results"][-1]["stdout"].replace('"head_equals_origin_main": true', '"head_equals_origin_main": false')),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(doc)
        mutation(candidate)
        caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    doc = json.loads(RELEASE.read_text(encoding="utf-8"))
    errors = validate(doc)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(doc)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "commands": len(doc.get("results", [])), "effective_checks": doc.get("summary", {}).get("effective_checks"), "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
