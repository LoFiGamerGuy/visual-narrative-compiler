"""Fail-closed validation for the CH05 P005→P006 attribution control."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections.abc import Callable
from typing import Any

from build_ch05_p005_p006_route_attribution_control import (
    EVIDENCE,
    ROOT,
    build_document,
)
from PIL import Image


def sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(document: dict[str, Any], verify_artifact: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    try:
        expected = build_document()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return [f"source reconstruction failed: {exc}"]
    check(document == expected, "document differs from deterministic source reconstruction")
    check(document.get("record_type") == "CH05P005P006RouteAttributionControl", "record_type")
    check(document.get("state") == "EXISTING_PIXEL_ATTRIBUTION_CONTROL_PENDING_OWNER_REVIEW", "state")
    check(document.get("planning_structure") == "ComicPanelPlan", "planning_structure")
    check(document.get("animation_shot_plan") is None and document.get("e_conte") is None, "animation boundary")
    check(document.get("coverage") == {"canonical_panel_ids": ["ng-ch05-sc01-p005", "ng-ch05-sc01-p006"], "unique_existing_candidates": 4, "matched_transition_arms": 3, "new_art_candidates": 0, "provider_calls": 0, "uploads": 0}, "coverage")

    candidates = document.get("candidates", [])
    check(len(candidates) == 4, "candidate count")
    check([row.get("candidate_key") for row in candidates] == ["text_p005", "text_p006", "r6_p005", "r6_p006"], "candidate order")
    check(len({row.get("source", {}).get("sha256") for row in candidates}) == 4, "unique source hashes")
    for index, row in enumerate(candidates):
        check(row.get("planning_structure") == "ComicPanelPlan", f"candidate planning structure:{index}")
        check(row.get("animation_shot_plan") is None and row.get("e_conte") is None, f"candidate animation boundary:{index}")
        check(row.get("owner_acceptance") is None and row.get("rights_clearance") is None and row.get("commercially_cleared") is None and row.get("exact_production_base") is None, f"candidate disposition:{index}")
        check(set(row.get("complexity_proxies", {})) == {"grayscale_entropy_bits", "edge_density_ge_32", "png_bytes_per_native_pixel"}, f"complexity metrics:{index}")

    arms = document.get("arms", [])
    check(len(arms) == 3, "arm count")
    check([row.get("arm_id") for row in arms] == ["selected_cross_route", "all_text_control", "all_r6_control"], "arm order")
    check([(row.get("left_candidate_key"), row.get("right_candidate_key")) for row in arms] == [("text_p005", "r6_p006"), ("text_p005", "text_p006"), ("r6_p005", "r6_p006")], "arm bindings")
    for index, row in enumerate(arms):
        check(row.get("review_state") == "PENDING_OWNER_REVIEW_NOT_GRADED", f"review state:{index}")
        check(set(row.get("metrics", {})) == {"luminance_histogram_total_variation", "rgb_64_bin_histogram_mean_channel_total_variation"}, f"pair metrics:{index}")
        check(row.get("owner_acceptance") is None and row.get("rights_clearance") is None and row.get("commercially_cleared") is None and row.get("exact_production_base") is None, f"arm disposition:{index}")

    attribution = document.get("attribution", {})
    check(attribution.get("proxies_evaluated") == 2, "proxy count")
    check(attribution.get("proxies_supporting_rule") == 0, "attribution support count")
    check(attribution.get("result") == "ROUTE_SWITCH_CONTRIBUTION_NOT_ISOLATED_ON_BOTH_HISTOGRAM_PROXIES", "attribution result")
    check(len(attribution.get("confounds", [])) == 3, "confound coverage")
    for metric, row in attribution.get("comparison", {}).items():
        check(metric in {"luminance_histogram_total_variation", "rgb_64_bin_histogram_mean_channel_total_variation"}, f"attribution metric:{metric}")
        check(row.get("selected_exceeds_both_same_route_controls") is False, f"predeclared rule outcome:{metric}")

    artifact = document.get("artifact", {})
    artifact_path = ROOT / artifact.get("path", "")
    check(artifact.get("repository_state") == "IGNORED_LOCAL_REVIEW_LAYOUT_DERIVATIVE", "artifact state")
    check(artifact.get("contains_new_art") is False, "artifact content boundary")
    if verify_artifact:
        check(artifact_path.is_file(), "artifact exists")
        if artifact_path.is_file():
            check(sha256(artifact_path) == artifact.get("sha256"), "artifact hash")
            check(artifact_path.stat().st_size == artifact.get("bytes"), "artifact bytes")
            with Image.open(artifact_path) as opened:
                check([opened.width, opened.height] == [artifact.get("width"), artifact.get("height")], "artifact dimensions")
        check(subprocess.run(["git", "check-ignore", "-q", str(artifact_path)], cwd=ROOT, check=False).returncode == 0, "artifact ignored")

    check(document.get("disposition") == {"selected_or_ranked_candidate": None, "owner_acceptance": None, "rights_clearance": None, "commercially_cleared": None, "exact_production_base": None, "pixel_edits": None}, "disposition")
    check(document.get("spend") == {"direct_paid_api_cloud_usd": 0.0, "built_in_product_monetary_cost_usd": None, "provider_calls": 0, "uploads": 0}, "spend")
    check("do not measure or grade artistic quality" in document.get("method", {}).get("interpretation_boundary", ""), "non-quality boundary")
    check("no provider execution" in document.get("boundary", "").lower(), "execution boundary")
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "ACCEPTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("animation_shot_plan", {}),
        lambda value: value["coverage"].__setitem__("unique_existing_candidates", 3),
        lambda value: value["coverage"].__setitem__("provider_calls", 1),
        lambda value: value["inputs"][0].__setitem__("sha256", "0" * 64),
        lambda value: value["candidates"].pop(),
        lambda value: value["candidates"][0]["source"].__setitem__("sha256", "0" * 64),
        lambda value: value["candidates"][0]["complexity_proxies"].__setitem__("edge_density_ge_32", 0.0),
        lambda value: value["candidates"][0].__setitem__("owner_acceptance", True),
        lambda value: value["arms"].pop(),
        lambda value: value["arms"][0].__setitem__("right_candidate_key", "text_p006"),
        lambda value: value["arms"][0]["metrics"].__setitem__("luminance_histogram_total_variation", 0.0),
        lambda value: value["arms"][0].__setitem__("review_state", "GRADED"),
        lambda value: value["attribution"].__setitem__("proxies_supporting_rule", 2),
        lambda value: value["attribution"].__setitem__("result", "ROUTE_SWITCH_CAUSAL"),
        lambda value: value["artifact"].__setitem__("sha256", "0" * 64),
        lambda value: value["artifact"].__setitem__("contains_new_art", True),
        lambda value: value["disposition"].__setitem__("selected_or_ranked_candidate", "r6"),
        lambda value: value["spend"].__setitem__("uploads", 1),
        lambda value: value["spend"].__setitem__("direct_paid_api_cloud_usd", 1.0),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate, verify_artifact=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    errors = validate(document)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(document)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
