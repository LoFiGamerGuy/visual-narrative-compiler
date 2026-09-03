"""Validate six-route CH05 comparison and sequence-level cadence evidence."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections.abc import Callable
from itertools import pairwise
from pathlib import Path
from typing import Any

from build_ch05_six_route_comparison import (
    ASSEMBLIES,
    EVIDENCE,
    FIVE_ROUTE,
    HYBRID,
    PHONES,
    R6_SUPPLEMENTAL,
    REDUCED_EXECUTIONS,
    REDUCED_PROMPTS,
    ROOT,
    ROUTES,
    TRIAGES,
    choose_cadence,
    counts,
    normalize_density,
)
from PIL import Image


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_tables() -> tuple[
    list[str],
    dict[str, list[str]],
    dict[str, list[str]],
    dict[str, list[str]],
    dict[str, list[str]],
    dict[str, list[str]],
    dict[str, Any],
    dict[str, Any],
]:
    assemblies = {route: json.loads(path.read_text(encoding="utf-8")) for route, path in ASSEMBLIES.items()}
    canonical = [entry["panel_id"] for entry in sorted(assemblies["r6"]["entries"], key=lambda row: row["order"])]
    triages = {route: json.loads(path.read_text(encoding="utf-8")) for route, path in TRIAGES.items()}
    semantic: dict[str, list[str]] = {}
    overall: dict[str, list[str]] = {}
    lettering: dict[str, list[str]] = {}
    density: dict[str, list[str]] = {}
    identity: dict[str, list[str]] = {}
    evaluation: dict[str, Any] = {}
    for route in ROUTES:
        rows = sorted(triages[route]["rows"], key=lambda row: row["display_order"])
        if [row["panel_id"] for row in rows] != canonical:
            raise ValueError(f"triage canonical coverage mismatch: {route}")
        semantic_values = [row.get("semantic_status", row["status"]) for row in rows]
        if route == "r6":
            semantic_values = [R6_SUPPLEMENTAL.get(index + 1, value) for index, value in enumerate(semantic_values)]
        overall_values = [row["status"] for row in rows]
        lettering_values = [row.get("checks", {}).get("lettering_clearance", "NOT_ASSESSED") for row in rows]
        density_values = [normalize_density(row.get("style_density_compliance", row.get("style_status"))) for row in rows]
        identity_values = [row.get("checks", {}).get("hair_and_wardrobe", "NOT_ASSESSED") for row in rows]
        semantic[route], overall[route] = semantic_values, overall_values
        lettering[route], density[route], identity[route] = lettering_values, density_values, identity_values
        evaluation[route] = {
            "semantic": counts(semantic_values),
            "overall": counts(overall_values),
            "lettering": counts(lettering_values, True),
            "style_density": counts(density_values, True),
            "identity_hair_wardrobe": counts(identity_values, True),
        }
    return canonical, semantic, overall, lettering, density, identity, evaluation, triages


def validate(document: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    required = [*ASSEMBLIES.values(), *TRIAGES.values(), *PHONES.values(), REDUCED_PROMPTS, REDUCED_EXECUTIONS, FIVE_ROUTE, HYBRID]
    canonical, semantic, overall, lettering, density, identity, evaluation, triages = expected_tables()
    prompt_document = json.loads(REDUCED_PROMPTS.read_text(encoding="utf-8"))
    execution_document = json.loads(REDUCED_EXECUTIONS.read_text(encoding="utf-8"))
    sequences = prompt_document["sequences"]
    expected_routes, expected_score = choose_cadence(sequences, semantic, identity, overall, lettering)

    check(document.get("record_type") == "CH05CompleteChapterSixRouteComparison", "record_type")
    check(document.get("record_id") == "ng-ch05-six-route-comparison-r1", "record_id")
    check(document.get("state") == "ENGINEERING_COMPARISON_AND_SEQUENCE_CADENCE_PENDING_OWNER_REVIEW", "state")
    check(document.get("medium") == "comic", "medium")
    check(document.get("planning_structure") == "ComicPanelPlan" and document.get("animation_shot_plan") is None and document.get("e_conte") is None, "planning boundary")
    expected_inputs = [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in required]
    check(document.get("inputs") == expected_inputs, "input bindings")
    check(document.get("coverage") == {"routes": 6, "comic_panel_plans_per_route": 50, "paired_panel_ids": 50, "total_panel_candidates_compared": 300}, "coverage")
    check(document.get("evaluation_counts") == evaluation, "evaluation counts")
    check(document.get("semantic_anchor_panel_ids") == [f"ng-ch05-sc01-p{number:03d}" for number in (1, 13, 29, 32, 36, 39, 41, 43, 48, 50)], "semantic anchors")

    per_panel = document.get("visual_complexity", {}).get("per_panel", [])
    check(len(per_panel) == 50 and [row.get("panel_id") for row in per_panel] == canonical, "per-panel metric coverage")
    metric_keys = {"grayscale_entropy_bits", "edge_density_ge_32", "png_bytes_per_native_pixel"}
    if len(per_panel) == 50:
        for index, panel in enumerate(per_panel):
            for route in ROUTES:
                result = panel.get(route, {})
                check(metric_keys <= set(result), f"metric keys:{index}:{route}")
                check(result.get("semantic_status") == semantic[route][index], f"semantic status:{index}:{route}")
                check(result.get("overall_status") == overall[route][index], f"overall status:{index}:{route}")
                check(result.get("lettering_status") == lettering[route][index], f"lettering status:{index}:{route}")
                check(result.get("style_density_status") == density[route][index], f"density status:{index}:{route}")
                check(result.get("identity_status") == identity[route][index], f"identity status:{index}:{route}")
    aggregate = document.get("visual_complexity", {}).get("aggregate_equal_panel_weight", {})
    for route in ROUTES:
        if len(per_panel) == 50:
            expected_aggregate = {key: round(sum(panel[route][key] for panel in per_panel) / 50, 6) for key in metric_keys}
            check(aggregate.get(route) == expected_aggregate, f"aggregate:{route}")
    check("do not score quality" in document.get("visual_complexity", {}).get("method", ""), "metric limitation")

    reduced = document.get("reduced_palette_text_control", {})
    zero = reduced.get("zero_upload_result", {})
    execution_summary = execution_document["summary"]
    expected_zero = {
        "result": "PASS_ZERO_UPLOAD_TEXT_ONLY_CONTROL",
        "prompt_sequences": 11,
        "prompt_input_reference_bindings": sum(len(row.get("input_references", [])) for row in sequences),
        "execution_records": 11,
        "execution_input_reference_bindings": sum(len(row.get("input_references", [])) for row in execution_document["records"]),
        "authorized_reference_uses": execution_summary["authorized_reference_uses"],
        "reference_uploads": execution_summary["reference_uploads"],
        "direct_paid_provider_api_calls": execution_summary["direct_paid_provider_api_calls"],
    }
    check(zero == expected_zero and all(expected_zero[key] == 0 for key in ("prompt_input_reference_bindings", "execution_input_reference_bindings", "authorized_reference_uses", "reference_uploads", "direct_paid_provider_api_calls")), "zero-upload result")
    check(reduced.get("summary_as_recorded") == triages["reduced_palette_text_control"]["summary"], "reduced triage summary")
    drift = reduced.get("identity_drift", {})
    reduced_summary = triages["reduced_palette_text_control"]["summary"]
    check(drift.get("result") == "NO_OBSERVED_ROLE_HAIR_WARDROBE_DRIFT_IN_VISIBLE_CAST_PANELS", "identity drift result")
    check(drift.get("visible_adult_cast_panels") == reduced_summary.get("visible_adult_cast_panels"), "identity visible-cast count")
    check(drift.get("visible_cast_identity_pass") == reduced_summary.get("mature_identity_hair_wardrobe_pass"), "identity pass count")
    check(drift.get("planned_zero_cast_panels") == reduced_summary.get("zero_cast_panels_without_people"), "identity zero-cast count")
    check(drift.get("counts") == evaluation["reduced_palette_text_control"]["identity_hair_wardrobe"], "identity drift counts")
    check(drift.get("continuity_result") == triages["reduced_palette_text_control"].get("continuity_result"), "identity drift narrative")
    check("not biometric" in drift.get("basis", ""), "identity boundary")
    check("does not establish exact facial identity" in drift.get("scope_limitation", ""), "identity drift scope limitation")

    recommendation = document.get("sequence_cadence_recommendation", {})
    cadence = recommendation.get("sequences", [])
    check(len(cadence) == 11, "cadence sequence count")
    check([row.get("selected_route") for row in cadence] == expected_routes, "measured cadence selection")
    check(recommendation.get("objective_score_fields") == ["combined_semantic_identity_failures", "semantic_failures", "identity_failures", "adjacent_route_transitions", "combined_semantic_identity_warnings", "semantic_warnings", "identity_warnings", "overall_failures", "lettering_failures", "combined_overall_lettering_warnings", "stable_route_preference_sum"], "cadence objective fields")
    check(recommendation.get("objective_score") == list(expected_score), "cadence objective score")
    selected_panel_routes: list[str] = []
    expected_repairs: list[dict[str, Any]] = []
    for sequence, selected in zip(sequences, cadence, strict=False):
        start, end = sequence["panel_range"]
        route = selected.get("selected_route")
        check(selected.get("sequence_id") == sequence["source_sequence_id"] and selected.get("panel_range") == [start, end] and selected.get("panel_count") == end - start + 1, f"cadence binding:{sequence['source_sequence_id']}")
        check(route in ROUTES and selected.get("within_sequence_style_transitions") == 0, f"single route:{sequence['source_sequence_id']}")
        if route in ROUTES:
            sem_values = semantic[route][start - 1:end]
            id_values = identity[route][start - 1:end]
            overall_values = overall[route][start - 1:end]
            lettering_values = lettering[route][start - 1:end]
            density_values = density[route][start - 1:end]
            failures = [canonical[index] for index in range(start - 1, end) if semantic[route][index] == "FAIL"]
            check(selected.get("semantic_counts") == counts(sem_values), f"cadence semantic counts:{sequence['source_sequence_id']}")
            check(selected.get("identity_counts") == counts(id_values, True), f"cadence identity counts:{sequence['source_sequence_id']}")
            check(selected.get("overall_counts") == counts(overall_values), f"cadence overall counts:{sequence['source_sequence_id']}")
            check(selected.get("lettering_counts") == counts(lettering_values, True), f"cadence lettering counts:{sequence['source_sequence_id']}")
            check(selected.get("style_density_counts") == counts(density_values, True), f"cadence density counts:{sequence['source_sequence_id']}")
            check(selected.get("explicit_semantic_failure_panel_ids") == failures, f"cadence failures:{sequence['source_sequence_id']}")
            selected_panel_routes.extend([route] * (end - start + 1))
            expected_repairs.extend({"panel_id": panel_id, "sequence_id": sequence["source_sequence_id"], "style_to_preserve": route, "reason": "explicit semantic FAIL in selected sequence route", "action": "smallest targeted same-style repair; do not substitute a differently styled panel"} for panel_id in failures)
    transitions = sum(left != right for left, right in pairwise(selected_panel_routes))
    check(recommendation.get("sequence_route_transitions") == transitions and recommendation.get("adjacent_panel_route_transitions") == transitions, "transition counts")
    check(transitions <= 10 and recommendation.get("review_only_panel_hybrid_transitions") == 33 and recommendation.get("transition_reduction_from_hybrid") == 33 - transitions, "hybrid transition reduction")
    check(recommendation.get("targeted_same_style_repairs") == expected_repairs, "targeted repairs")
    check(recommendation.get("production_manifest_created") is False and "one style per narrative sequence" in recommendation.get("policy", "").lower(), "cadence boundary")

    owner = document.get("owner_disposition", {})
    check(owner == {"accepted_route": None, "accepted_sequence_assignments": None, "accepted_panel_ids": None, "commercial_rights_clearance": None, "exact_production_base": None}, "owner disposition")
    check(document.get("recommendation", {}).get("wholesale_route_selection") is None and document.get("recommendation", {}).get("appearance_only_selection") is False, "selection boundary")
    check(document.get("spend") == {"direct_paid_api_cloud_usd": 0.0, "built_in_product_monetary_cost_usd": None}, "spend")
    check("owner acceptance" in document.get("boundary", "").lower(), "document boundary")

    artifacts = document.get("artifacts", {})
    check(set(artifacts) == {"all_50_six_columns", "semantic_anchors", "lettered_phone_comparison", "style_density_comparison", "sequence_cadence"}, "artifact set")
    for label, value in artifacts.items():
        path = ROOT / value.get("path", "")
        check(value.get("repository_state") == "IGNORED_LOCAL_REVIEW_ARTIFACT", f"artifact state:{label}")
        check(isinstance(value.get("sha256"), str) and len(value["sha256"]) == 64 and value["sha256"] != "0" * 64, f"artifact hash:{label}")
        check(all(isinstance(value.get(key), int) and value[key] > 0 for key in ("width", "height", "bytes")), f"artifact shape:{label}")
        if verify_files:
            check(path.is_file() and sha256(path) == value.get("sha256") and path.stat().st_size == value.get("bytes"), f"artifact binding:{label}")
            if path.is_file():
                with Image.open(path) as image:
                    check([image.width, image.height] == [value.get("width"), value.get("height")], f"artifact dimensions:{label}")
            check(subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT, check=False).returncode == 0, f"artifact ignored:{label}")
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "ACCEPTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("e_conte", {}),
        lambda value: value["coverage"].__setitem__("routes", 5),
        lambda value: value["inputs"].pop(),
        lambda value: value["evaluation_counts"]["reduced_palette_text_control"]["semantic"].__setitem__("fail", 99),
        lambda value: value["visual_complexity"]["per_panel"].pop(),
        lambda value: value["visual_complexity"]["per_panel"][0]["r6"].__setitem__("semantic_status", "PASS"),
        lambda value: value["visual_complexity"]["aggregate_equal_panel_weight"]["r6"].__setitem__("edge_density_ge_32", 0.0),
        lambda value: value["reduced_palette_text_control"]["zero_upload_result"].__setitem__("reference_uploads", 1),
        lambda value: value["reduced_palette_text_control"]["identity_drift"]["counts"].__setitem__("fail", 99),
        lambda value: value["sequence_cadence_recommendation"]["sequences"].pop(),
        lambda value: value["sequence_cadence_recommendation"]["sequences"][0].__setitem__("selected_route", "bad"),
        lambda value: value["sequence_cadence_recommendation"]["sequences"][0].__setitem__("within_sequence_style_transitions", 1),
        lambda value: value["sequence_cadence_recommendation"].__setitem__("adjacent_panel_route_transitions", 33),
        lambda value: value["sequence_cadence_recommendation"].__setitem__("transition_reduction_from_hybrid", 0),
        lambda value: value["sequence_cadence_recommendation"].__setitem__("production_manifest_created", True),
        lambda value: value["owner_disposition"].__setitem__("accepted_route", "r6"),
        lambda value: value["recommendation"].__setitem__("wholesale_route_selection", "r6"),
        lambda value: value["artifacts"]["sequence_cadence"].__setitem__("sha256", "0" * 64),
        lambda value: value["spend"].__setitem__("direct_paid_api_cloud_usd", 1.0),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate, verify_files=False))
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
