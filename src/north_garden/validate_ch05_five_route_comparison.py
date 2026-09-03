"""Validate deterministic five-route CH05 complete-chapter comparison evidence."""
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
DOC = ROOT / "docs/research/evidence/ch05-five-route-comparison-r1.json"
ROUTES = {"r6", "alt_graphic", "clear_line_watercolor", "premium_cel", "flat_graphic_gouache"}
EXPECTED_COUNTS = {
    "r6_supplemental": {"pass": 47, "warn": 1, "fail": 2},
    "alt_graphic": {"pass": 36, "warn": 7, "fail": 7},
    "clear_line_watercolor": {"pass": 45, "warn": 2, "fail": 3},
    "premium_cel": {"pass": 40, "warn": 5, "fail": 5},
    "flat_graphic_gouache": {"pass": 41, "warn": 6, "fail": 3},
}
EXPECTED_AGGREGATE = {
    "r6": {"grayscale_entropy_bits": 6.889241, "edge_density_ge_32": 0.220004, "png_bytes_per_native_pixel": 1.623124},
    "alt_graphic": {"grayscale_entropy_bits": 6.83786, "edge_density_ge_32": 0.215718, "png_bytes_per_native_pixel": 1.608028},
    "clear_line_watercolor": {"grayscale_entropy_bits": 7.02571, "edge_density_ge_32": 0.244026, "png_bytes_per_native_pixel": 1.698281},
    "premium_cel": {"grayscale_entropy_bits": 6.934245, "edge_density_ge_32": 0.227841, "png_bytes_per_native_pixel": 1.656707},
    "flat_graphic_gouache": {"grayscale_entropy_bits": 6.897733, "edge_density_ge_32": 0.21128, "png_bytes_per_native_pixel": 1.581633},
}
EXPECTED_ANCHORS = [f"ng-ch05-sc01-p{number:03d}" for number in (1, 13, 29, 32, 36, 39, 41, 43, 48, 50)]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(document: dict[str, Any], files: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(document.get("record_type") == "CH05CompleteChapterFiveRouteComparison" and document.get("state") == "ENGINEERING_SELECTION_PENDING_OWNER_REVIEW", "identity/state")
    check(document.get("planning_structure") == "ComicPanelPlan" and document.get("animation_shot_plan") is None and document.get("e_conte") is None, "planning boundary")
    check(document.get("coverage") == {"routes": 5, "comic_panel_plans_per_route": 50, "paired_panel_ids": 50, "total_panel_candidates_compared": 250}, "coverage")
    check(document.get("semantic_anchor_panel_ids") == EXPECTED_ANCHORS, "semantic anchors")
    check(document.get("semantic_counts") == EXPECTED_COUNTS, "semantic counts")
    flat = document.get("flat_graphic_gouache_constraints", {})
    check(flat.get("semantic_counts_used_for_route_comparison") == EXPECTED_COUNTS["flat_graphic_gouache"], "flat semantic counts")
    check(flat.get("combined_semantic_lettering_phone_status") == {"pass": 16, "warn": 7, "fail": 27}, "flat combined status")
    check(flat.get("lettering_clearance") == {"pass": 19, "warn": 6, "fail": 25}, "flat lettering burden")
    check(flat.get("strict_requested_style_density") == {"pass": 0, "warn": 0, "fail": 50}, "flat strict density")
    check("prevent wholesale selection" in flat.get("interpretation", ""), "flat constraint interpretation")
    metrics = document.get("visual_complexity", {})
    aggregate = metrics.get("aggregate_equal_panel_weight", {})
    check(aggregate == EXPECTED_AGGREGATE, "exact aggregate metrics")
    check(set(aggregate) == ROUTES, "aggregate metric routes")
    changes = metrics.get("flat_proxy_change_percent", {})
    check(set(changes) == {"r6", "clear_line_watercolor", "premium_cel"}, "flat proxy baselines")
    check(changes.get("r6", {}).get("edge_density_ge_32", 0) < 0 and changes.get("r6", {}).get("png_bytes_per_native_pixel", 0) < 0, "flat modest proxy reduction")
    check("0/50" in metrics.get("interpretation", "") and "modest reduction" in metrics.get("interpretation", ""), "metric interpretation")
    per_panel = metrics.get("per_panel", [])
    check(len(per_panel) == 50 and [row.get("panel_id") for row in per_panel] == [f"ng-ch05-sc01-p{number:03d}" for number in range(1, 51)], "per-panel metric coverage/order")
    check(all(set(row) == {"panel_id", *ROUTES} for row in per_panel), "per-panel metric routes")
    ranking = document.get("ranking", [])
    check([row.get("route") for row in ranking] == ["r6_plus_cross_panel_gates", "clear_line_watercolor", "premium_cel", "flat_graphic_gouache", "alt_graphic"], "ranking routes")
    check([row.get("role") for row in ranking] == ["current_base", "leading_style_direction", "selected_panel_source", "density_diagnostic", "control"], "ranking roles")
    recommendation = document.get("recommendation", {})
    check(recommendation.get("current_base") == "r6" and recommendation.get("leading_style_direction") == "clear_line_watercolor", "base/style recommendation")
    check(recommendation.get("density_diagnostic") == "flat_graphic_gouache" and recommendation.get("flat_graphic_gouache_wholesale_selection") is False, "flat recommendation")
    check(recommendation.get("wholesale_route_selection") is None and recommendation.get("appearance_only_selection") is False, "no wholesale/appearance selection")
    check(document.get("owner_disposition") == {"accepted_route": None, "accepted_panel_ids": None, "commercial_rights_clearance": None, "exact_production_base": None}, "null owner/rights disposition")
    check(document.get("spend") == {"direct_paid_api_cloud_usd": 0.0, "built_in_product_monetary_cost_usd": None}, "spend")
    limitations = document.get("limitations", [])
    check(any("R6 supplemental audit is preserved as 47/1/2" in item for item in limitations), "r6 supplemental limitation")
    check(any("No route or panel is accepted" in item for item in limitations), "acceptance limitation")

    if files:
        inputs = document.get("inputs", [])
        check(len(inputs) == 15, "input count")
        for source in inputs:
            path = ROOT / source.get("path", "")
            check(path.is_file() and sha256(path) == source.get("sha256"), f"input {source.get('path')}")
        artifacts = document.get("artifacts", {})
        check(set(artifacts) == {"all_50_five_columns", "semantic_anchors", "lettered_phone_comparison"}, "artifact names")
        expected_dimensions = {
            "all_50_five_columns": [2038, 10960],
            "semantic_anchors": [2038, 3530],
            "lettered_phone_comparison": [2062, 9078],
        }
        for name, artifact in artifacts.items():
            path = ROOT / artifact.get("path", "")
            check(path.is_file() and sha256(path) == artifact.get("sha256") and path.stat().st_size == artifact.get("bytes"), f"artifact {name}")
            if path.is_file():
                with Image.open(path) as opened:
                    check(opened.format == "PNG" and [opened.width, opened.height] == expected_dimensions[name] == [artifact.get("width"), artifact.get("height")], f"decode/dimensions {name}")
                ignored = subprocess.run(["git", "check-ignore", "--quiet", "--", artifact.get("path", "")], cwd=ROOT).returncode == 0
                check(ignored and artifact.get("repository_state") == "IGNORED_LOCAL_REVIEW_ARTIFACT", f"ignored {name}")
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations = [
        lambda value: value.__setitem__("state", "ACCEPTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value["coverage"].__setitem__("routes", 4),
        lambda value: value["semantic_anchor_panel_ids"].pop(),
        lambda value: value["semantic_counts"]["r6_supplemental"].__setitem__("pass", 50),
        lambda value: value["semantic_counts"]["flat_graphic_gouache"].__setitem__("fail", 0),
        lambda value: value["flat_graphic_gouache_constraints"]["lettering_clearance"].__setitem__("fail", 0),
        lambda value: value["flat_graphic_gouache_constraints"]["strict_requested_style_density"].__setitem__("fail", 49),
        lambda value: value["visual_complexity"]["aggregate_equal_panel_weight"].pop("flat_graphic_gouache"),
        lambda value: value["visual_complexity"]["flat_proxy_change_percent"]["r6"].__setitem__("edge_density_ge_32", 1.0),
        lambda value: value["visual_complexity"]["per_panel"].pop(),
        lambda value: value["ranking"].reverse(),
        lambda value: value["ranking"][3].__setitem__("role", "wholesale_selection"),
        lambda value: value["recommendation"].__setitem__("current_base", "flat_graphic_gouache"),
        lambda value: value["recommendation"].__setitem__("flat_graphic_gouache_wholesale_selection", True),
        lambda value: value["recommendation"].__setitem__("wholesale_route_selection", "flat_graphic_gouache"),
        lambda value: value["recommendation"].__setitem__("appearance_only_selection", True),
        lambda value: value["owner_disposition"].__setitem__("commercial_rights_clearance", True),
        lambda value: value["spend"].__setitem__("built_in_product_monetary_cost_usd", 0.0),
        lambda value: value.__setitem__("limitations", []),
    ]
    caught = 0
    for mutation in mutations:
        changed = copy.deepcopy(document)
        mutation(changed)
        caught += bool(validate(changed, files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    document = json.loads(DOC.read_text(encoding="utf-8"))
    errors = validate(document)
    caught = total = 0
    if arguments.self_test:
        caught, total = self_test(document)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(json.dumps({"errors": errors, "self_test": f"{caught}/{total}" if arguments.self_test else None, "status": "PASS" if not errors else "FAIL"}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
