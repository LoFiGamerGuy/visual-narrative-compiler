"""Validate and mutation-test active-goal CH05 output reconciliation."""

from __future__ import annotations

import argparse
import copy
import json

from compile_ch05_active_goal_art_output_reconciliation import (
    OUTPUT_JSON,
    OUTPUT_MARKDOWN,
    build_record,
    render_markdown,
)


def validate_payload(record: dict, expected: dict) -> list[str]:
    errors: list[str] = []
    if record != expected:
        errors.append("record differs from deterministic manifest rebuild")
    if record.get("planning_structure") != "ComicPanelPlan":
        errors.append("planning structure mismatch")
    if (
        record.get("animation_shot_plan") is not None
        or record.get("e_conte") is not None
    ):
        errors.append("cross-medium planning leakage")
    totals = record.get("totals", {})
    required = {
        "service_raster_outputs": 76,
        "panel_level_candidates_or_crops": 312,
        "authorized_reference_uses": 132,
        "zero_reference_outputs": 13,
        "unsplit_ablation_diagnostics": 2,
    }
    if totals != required:
        errors.append("reconciled total mismatch")
    subset = record.get("six_route_subset", {})
    if subset.get("aligned_review_candidates") != 300:
        errors.append("six-route aligned subset mismatch")
    if (
        300
        + subset.get("excluded_base_additional_candidates", -1)
        + subset.get("excluded_premium_targeted_repair_candidates", -1)
        != 312
    ):
        errors.append("six-route/full-pool relationship mismatch")
    timing = record.get("timing_boundary", {})
    if timing.get("aggregate_end_to_end_seconds") is not None:
        errors.append("aggregate E2E must remain null")
    if timing.get("aggregation_permitted") is not False:
        errors.append("timing aggregation must remain prohibited")
    activity = record.get("package_activity", {})
    if any(value != 0 for value in activity.values()):
        errors.append("package activity is not zero")
    source_paths = [
        source["path"]
        for component in record.get("components", [])
        for source in component.get("source_manifests", [])
    ]
    if len(source_paths) != len(set(source_paths)):
        errors.append("duplicate source manifest binding")
    for component in record.get("components", []):
        if (
            component.get("unsplit_ablation_diagnostics", 0) > 0
            and component.get("panel_level_candidates_or_crops") != 0
        ):
            errors.append("unsplit ablation counted as panel crops")
    return errors


def mutations(record: dict) -> list[tuple[str, dict]]:
    cases = []

    def add(name, operation):
        candidate = copy.deepcopy(record)
        operation(candidate)
        cases.append((name, candidate))

    add("record_id", lambda item: item.__setitem__("record_id", "mutated"))
    add(
        "planning",
        lambda item: item.__setitem__("planning_structure", "AnimationShotPlan"),
    )
    add("animation", lambda item: item.__setitem__("animation_shot_plan", {}))
    add(
        "rasters", lambda item: item["totals"].__setitem__("service_raster_outputs", 77)
    )
    add(
        "panels",
        lambda item: item["totals"].__setitem__("panel_level_candidates_or_crops", 313),
    )
    add(
        "references",
        lambda item: item["totals"].__setitem__("authorized_reference_uses", 133),
    )
    add(
        "zero_reference",
        lambda item: item["totals"].__setitem__("zero_reference_outputs", 12),
    )
    add(
        "unsplit",
        lambda item: item["totals"].__setitem__("unsplit_ablation_diagnostics", 0),
    )
    add(
        "six_route",
        lambda item: item["six_route_subset"].__setitem__(
            "aligned_review_candidates", 312
        ),
    )
    add(
        "r6_extra",
        lambda item: item["six_route_subset"].__setitem__(
            "excluded_base_additional_candidates", 8
        ),
    )
    add(
        "timing_value",
        lambda item: item["timing_boundary"].__setitem__(
            "aggregate_end_to_end_seconds", 7125.241
        ),
    )
    add(
        "timing_permission",
        lambda item: item["timing_boundary"].__setitem__("aggregation_permitted", True),
    )
    add(
        "provider",
        lambda item: item["package_activity"].__setitem__("provider_calls", 1),
    )
    add("upload", lambda item: item["package_activity"].__setitem__("uploads", 1))
    add(
        "source_hash",
        lambda item: item["components"][0]["source_manifests"][0].__setitem__(
            "sha256", "0" * 64
        ),
    )
    add(
        "component_output",
        lambda item: item["components"][0].__setitem__("service_raster_outputs", 15),
    )
    add(
        "ablation_crop",
        lambda item: item["components"][-1].__setitem__(
            "panel_level_candidates_or_crops", 3
        ),
    )
    add("drop_component", lambda item: item["components"].pop())
    return cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    record = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    expected = build_record()
    errors = validate_payload(record, expected)
    if OUTPUT_MARKDOWN.read_text(encoding="utf-8") != render_markdown(record):
        errors.append("Markdown differs from deterministic render")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    cases = mutations(record) if args.self_test else []
    rejected = 0
    for name, mutation in cases:
        if validate_payload(mutation, expected):
            rejected += 1
        else:
            print(f"FAIL: mutation survived: {name}")
            return 1
    print(
        "CH05 active-goal output reconciliation PASS: "
        f"76 rasters; 312 panel candidates/crops; 132 refs; "
        f"13 zero-ref; 2 unsplit; mutations {rejected}/{len(cases)} rejected"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
