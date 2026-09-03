"""Fail-closed validation for the deterministic CH05 cadence-boundary audit."""
from __future__ import annotations

import argparse
import copy
import json
from collections.abc import Callable
from typing import Any

from compile_ch05_sequence_cadence_boundary_audit import (
    EVIDENCE,
    PAIR_SPECS,
    build_document,
)


def validate(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    try:
        expected = build_document()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return [f"source reconstruction failed: {exc}"]

    check(document == expected, "document differs from deterministic source reconstruction")
    check(document.get("record_type") == "CH05SequenceCadenceBoundaryAudit", "record_type")
    check(document.get("state") == "MEASURED_NON_GATING_CONTINUITY_RISK_AUDIT_PENDING_OWNER_REVIEW", "state")
    check(document.get("planning_structure") == "ComicPanelPlan", "planning_structure")
    check(document.get("animation_shot_plan") is None and document.get("e_conte") is None, "animation boundary")
    check(document.get("coverage") == {"source_panels": 8, "pair_comparisons": 6, "cross_route_boundaries": 2, "adjacent_within_route_controls": 4, "new_generated_images": 0, "external_uploads": 0}, "coverage")
    check(len(document.get("panels", [])) == 8, "panel count")
    check([row.get("order") for row in document.get("panels", [])] == [4, 5, 6, 7, 38, 39, 40, 41], "panel order")
    check([row.get("pair_id") for row in document.get("pairs", [])] == [spec[0] for spec in PAIR_SPECS], "pair order")
    check([row.get("pair_kind") for row in document.get("pairs", [])].count("cross_route") == 2, "cross-route count")
    check([row.get("pair_kind") for row in document.get("pairs", [])].count("within_route") == 4, "within-route count")
    boundaries = document.get("boundaries", [])
    check(len(boundaries) == 2, "boundary count")
    check(len(boundaries) >= 1 and boundaries[0].get("assessment") == "CONTINUITY_RISK_VISUALLY_ABRUPT", "first-boundary risk")
    check(len(boundaries) >= 2 and boundaries[1].get("assessment") == "LOWER_OBSERVED_CONTINUITY_RISK_REVIEW_STILL_REQUIRED", "second-boundary assessment")
    check("do not measure artistic quality" in document.get("method", {}).get("interpretation_boundary", ""), "proxy non-quality boundary")
    check(document.get("recommendation", {}).get("route_selection_changed") is False, "route selection boundary")
    check(document.get("recommendation", {}).get("pixel_edits_authorized_or_performed") is False, "pixel edit boundary")
    check(document.get("spend") == {"direct_paid_api_cloud_usd": 0.0, "built_in_product_monetary_cost_usd": None}, "spend")
    check(document.get("owner_disposition") == {"accepted": None, "rights_cleared": None, "commercially_cleared": None, "exact_production_base": None}, "owner disposition")
    for index, row in enumerate(document.get("panels", [])):
        check(row.get("planning_structure") == "ComicPanelPlan", f"panel planning structure:{index}")
        check(row.get("animation_shot_plan") is None and row.get("e_conte") is None, f"panel animation boundary:{index}")
        check(row.get("owner_acceptance") is None and row.get("rights_clearance") is None and row.get("commercially_cleared") is None and row.get("exact_production_base") is None, f"panel disposition:{index}")
        check(set(row.get("metrics", {})) == {"grayscale_entropy_bits", "edge_density_ge_32", "png_bytes_per_native_pixel"}, f"panel metrics:{index}")
    for index, row in enumerate(document.get("pairs", [])):
        check(set(row.get("metrics", {})) == {"luminance_histogram_total_variation", "rgb_64_bin_histogram_mean_channel_total_variation"}, f"pair metrics:{index}")
    for index, row in enumerate(document.get("boundaries", [])):
        manual = row.get("manual_observation", {})
        check(manual.get("reviewer") == "Codex agent visual review", f"manual attribution:{index}")
        check("cannot" in manual.get("confound", "") or "neither" in manual.get("confound", ""), f"manual confound:{index}")
        check(row.get("owner_acceptance") is None and row.get("rights_clearance") is None and row.get("commercially_cleared") is None and row.get("exact_production_base") is None, f"boundary disposition:{index}")
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "ACCEPTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("animation_shot_plan", {}),
        lambda value: value["coverage"].__setitem__("source_panels", 7),
        lambda value: value["coverage"].__setitem__("new_generated_images", 1),
        lambda value: value["inputs"][0].__setitem__("sha256", "0" * 64),
        lambda value: value["panels"].pop(),
        lambda value: value["panels"][0]["source"].__setitem__("sha256", "0" * 64),
        lambda value: value["panels"][0]["metrics"].__setitem__("grayscale_entropy_bits", 0.0),
        lambda value: value["panels"][0].__setitem__("owner_acceptance", True),
        lambda value: value["pairs"].pop(),
        lambda value: value["pairs"][1].__setitem__("pair_kind", "within_route"),
        lambda value: value["pairs"][1]["metrics"].__setitem__("luminance_histogram_total_variation", 0.0),
        lambda value: value["boundaries"].pop(),
        lambda value: value["boundaries"][0].__setitem__("assessment", "NO_RISK"),
        lambda value: value["boundaries"][0]["manual_observation"].__setitem__("reviewer", "owner"),
        lambda value: value["boundaries"][0]["proxy_rule_result"].__setitem__("distances_evaluated", 99),
        lambda value: value["recommendation"].__setitem__("route_selection_changed", True),
        lambda value: value["recommendation"].__setitem__("pixel_edits_authorized_or_performed", True),
        lambda value: value["spend"].__setitem__("direct_paid_api_cloud_usd", 1.0),
        lambda value: value["owner_disposition"].__setitem__("accepted", True),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate))
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
