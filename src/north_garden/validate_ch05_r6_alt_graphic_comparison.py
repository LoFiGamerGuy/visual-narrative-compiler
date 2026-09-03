"""Validate the measured CH05 r6 versus alternate-graphic route comparison."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-r6-vs-alt-graphic-comparison-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(doc: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    check(doc.get("record_type") == "CH05CompleteChapterRouteComparison", "record_type")
    check(doc.get("state") == "MEASURED_ENGINEERING_RECOMMENDATION_PENDING_OWNER_REVIEW", "state")
    check(doc.get("planning_structure") == "ComicPanelPlan" and doc.get("animation_shot_plan") is None and doc.get("e_conte") is None, "planning boundary")
    check(doc.get("coverage") == {"r6_panels": 50, "alt_graphic_panels": 50, "paired_panel_ids": 50}, "coverage")
    metrics = doc.get("visual_complexity", {}).get("aggregate_equal_panel_weight", {})
    check(set(metrics) == {"r6", "alt_graphic", "alt_minus_r6"}, "metric arms")
    check(all(set(metrics.get(arm, {})) == {"grayscale_entropy_bits", "edge_density_ge_32", "png_bytes_per_native_pixel"} for arm in metrics), "metric fields")
    check(len(doc.get("visual_complexity", {}).get("per_panel", [])) == 50, "per-panel metrics")
    semantic = doc.get("semantic_review", {})
    check(semantic.get("r6_frozen_panel_local_triage", {}).get("pass") == 49, "frozen r6 triage")
    check(semantic.get("r6_supplemental_cross_panel_gate_audit", {}).get("fail_panel_ids") == ["ng-ch05-sc01-p001", "ng-ch05-sc01-p041"], "r6 cross-panel supplement")
    alt = semantic.get("alt_graphic_triage", {})
    check((alt.get("pass"), alt.get("warn"), alt.get("fail")) == (36, 7, 7), "alternate triage")
    selection = doc.get("selection", {})
    check(selection.get("recommended_route") == "ch05_complete_chapter_r6_plus_cross_panel_semantic_gates" and selection.get("appearance_only_selection") is False, "selection")
    spend = doc.get("spend", {})
    check(spend.get("direct_paid_api_cloud_usd") == 0.0 and spend.get("built_in_product_monetary_cost_usd") is None, "spend semantics")
    if verify_files:
        for source in doc.get("inputs", []):
            path = ROOT / source.get("path", "")
            check(path.is_file() and sha256(path) == source.get("sha256"), f"input binding {source.get('path')}")
        for name, item in doc.get("artifacts", {}).items():
            raw = item.get("path", "")
            path = ROOT / raw
            check(path.is_file() and sha256(path) == item.get("sha256") and path.stat().st_size == item.get("bytes"), f"artifact binding {name}")
            if path.is_file():
                try:
                    with Image.open(path) as image:
                        check(image.format == "PNG" and [image.width, image.height] == [item.get("width"), item.get("height")], f"artifact decode {name}")
                except OSError:
                    errors.append(f"artifact decode {name}")
                ignored = subprocess.run(["git", "check-ignore", "--quiet", "--", raw], cwd=ROOT).returncode == 0
                tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", raw], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
                check(ignored and not tracked and item.get("repository_state") == "IGNORED_LOCAL_REVIEW_ARTIFACT", f"artifact repository state {name}")
    return errors


def self_test(doc: dict[str, Any]) -> tuple[int, int]:
    mutations = [lambda d: d.__setitem__("state", "ACCEPTED"), lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"), lambda d: d["coverage"].__setitem__("paired_panel_ids", 49), lambda d: d["visual_complexity"]["per_panel"].pop(), lambda d: d["semantic_review"]["r6_frozen_panel_local_triage"].__setitem__("pass", 47), lambda d: d["semantic_review"]["r6_supplemental_cross_panel_gate_audit"].__setitem__("fail_panel_ids", []), lambda d: d["semantic_review"]["alt_graphic_triage"].__setitem__("fail", 0), lambda d: d["selection"].__setitem__("recommended_route", "alt_graphic_wholesale"), lambda d: d["selection"].__setitem__("appearance_only_selection", True), lambda d: d["spend"].__setitem__("built_in_product_monetary_cost_usd", 0.0)]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(doc); mutation(candidate); caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args()
    doc = json.loads(EVIDENCE.read_text(encoding="utf-8")); errors = validate(doc); caught = total = 0
    if args.self_test:
        caught, total = self_test(doc)
        if caught != total: errors.append(f"self-test {caught}/{total}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__": raise SystemExit(main())
