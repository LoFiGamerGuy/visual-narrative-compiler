"""Compile a deterministic, read-only audit of the two CH05 cadence boundaries."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
CADENCE_EVIDENCE = ROOT / "docs/research/evidence/ch05-six-route-comparison-r1.json"
CADENCE_MANIFEST = ROOT / "production/comic/run-manifests/ch05-sequence-cadence-review-assembly-r1.json"
BOUNDARY_SHEET = ROOT / "experiments/review-packets/ch05-sequence-cadence-review-r1/review/ch05-sequence-cadence-boundary-continuity-sheet-r1.png"
EVIDENCE = ROOT / "docs/research/evidence/ch05-sequence-cadence-boundary-audit-r1.json"

PAIR_SPECS = (
    ("b1_left_within", 4, 5, "within_route", "reduced_palette_text_control"),
    ("b1_cross_route", 5, 6, "cross_route", "reduced_palette_text_control_to_r6"),
    ("b1_right_within", 6, 7, "within_route", "r6"),
    ("b2_left_within", 38, 39, "within_route", "r6"),
    ("b2_cross_route", 39, 40, "cross_route", "r6_to_premium_cel"),
    ("b2_right_within", 40, 41, "within_route", "premium_cel"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_image(entry: dict[str, Any]) -> tuple[Path, Image.Image]:
    path = ROOT / entry["source"]["path"]
    if not path.is_file() or sha256(path) != entry["source"]["sha256"]:
        raise ValueError(f"source binding failed: {entry['panel_id']}")
    with Image.open(path) as opened:
        image = opened.convert("RGB")
    if [image.width, image.height] != [entry["source"]["width"], entry["source"]["height"]]:
        raise ValueError(f"source dimensions failed: {entry['panel_id']}")
    return path, image


def panel_metrics(image: Image.Image, source_bytes: int) -> dict[str, float]:
    width = 390
    height = max(1, round(image.height * width / image.width))
    luminance = image.resize((width, height), Image.Resampling.LANCZOS).convert("L")
    histogram = luminance.histogram()
    total = sum(histogram)
    entropy = -sum((count / total) * math.log2(count / total) for count in histogram if count)
    edges = luminance.filter(ImageFilter.FIND_EDGES)
    cropped = edges.crop((1, 1, max(2, edges.width - 1), max(2, edges.height - 1)))
    edge_density = sum(value >= 32 for value in cropped.tobytes()) / (cropped.width * cropped.height)
    return {
        "grayscale_entropy_bits": round(entropy, 6),
        "edge_density_ge_32": round(edge_density, 6),
        "png_bytes_per_native_pixel": round(source_bytes / (image.width * image.height), 6),
    }


def normalized_histograms(image: Image.Image) -> tuple[list[float], list[list[float]]]:
    normalized = image.resize((256, 256), Image.Resampling.LANCZOS)
    pixel_count = normalized.width * normalized.height
    luminance = [count / pixel_count for count in normalized.convert("L").histogram()]
    channels: list[list[float]] = []
    for channel in normalized.split():
        full = channel.histogram()
        bins = [sum(full[index : index + 4]) / pixel_count for index in range(0, 256, 4)]
        channels.append(bins)
    return luminance, channels


def total_variation(left: list[float], right: list[float]) -> float:
    return 0.5 * sum(abs(a - b) for a, b in zip(left, right, strict=True))


def pair_metrics(left: Image.Image, right: Image.Image) -> dict[str, float]:
    left_luma, left_color = normalized_histograms(left)
    right_luma, right_color = normalized_histograms(right)
    color_distance = sum(total_variation(a, b) for a, b in zip(left_color, right_color, strict=True)) / 3
    return {
        "luminance_histogram_total_variation": round(total_variation(left_luma, right_luma), 6),
        "rgb_64_bin_histogram_mean_channel_total_variation": round(color_distance, 6),
    }


def build_document() -> dict[str, Any]:
    manifest = json.loads(CADENCE_MANIFEST.read_text(encoding="utf-8"))
    entries = {row["order"]: row for row in manifest["entries"]}
    required_orders = sorted({order for _, left, right, _, _ in PAIR_SPECS for order in (left, right)})
    if required_orders != [4, 5, 6, 7, 38, 39, 40, 41]:
        raise ValueError("unexpected audit panel coverage")

    images: dict[int, Image.Image] = {}
    panels: list[dict[str, Any]] = []
    for order in required_orders:
        entry = entries[order]
        path, image = load_image(entry)
        images[order] = image
        panels.append(
            {
                "order": order,
                "panel_id": entry["panel_id"],
                "candidate_id": entry["candidate_id"],
                "sequence_id": entry["sequence_id"],
                "route": entry["selection"]["route"],
                "source": {
                    "path": path.relative_to(ROOT).as_posix(),
                    "sha256": sha256(path),
                    "width": image.width,
                    "height": image.height,
                    "png_bytes": path.stat().st_size,
                },
                "metrics": panel_metrics(image, path.stat().st_size),
                "planning_structure": "ComicPanelPlan",
                "animation_shot_plan": None,
                "e_conte": None,
                "owner_acceptance": None,
                "rights_clearance": None,
                "commercially_cleared": None,
                "exact_production_base": None,
            }
        )

    pairs: list[dict[str, Any]] = []
    for pair_id, left, right, kind, route_context in PAIR_SPECS:
        metrics = pair_metrics(images[left], images[right])
        pairs.append(
            {
                "pair_id": pair_id,
                "left_panel_id": entries[left]["panel_id"],
                "right_panel_id": entries[right]["panel_id"],
                "pair_kind": kind,
                "route_context": route_context,
                "metrics": metrics,
            }
        )

    by_id = {row["pair_id"]: row for row in pairs}
    boundaries: list[dict[str, Any]] = []
    boundary_specs = (
        (
            "reduced_palette_text_control_to_r6",
            "b1_cross_route",
            "b1_left_within",
            "b1_right_within",
            "CONTINUITY_RISK_VISUALLY_ABRUPT",
            "The existing boundary sheet shows an abrupt cut from P005's high-key cream negative space and low, people-free runnel insert to P006's cool blue-gray sky, denser line/texture, taller frame, and two-adult action staging.",
            "Keep the selected sequence routes provisional; use existing P005/P006 pixels to compare selected reduced→R6 against all-reduced and all-R6 transition controls before any pixel repair or production acceptance.",
        ),
        (
            "r6_to_premium_cel",
            "b2_cross_route",
            "b2_left_within",
            "b2_right_within",
            "LOWER_OBSERVED_CONTINUITY_RISK_REVIEW_STILL_REQUIRED",
            "The existing boundary sheet shows P039 and P040 sharing dark mill timbers, a cool exterior opening, grounded earth tones, and close character-led staging; the focal character and aspect ratio change, but the value/palette bridge is comparatively cohesive.",
            "Retain the provisional boundary and include P039→P041 in owner review; no pixel intervention is justified by this audit alone.",
        ),
    )
    for boundary_id, cross_id, left_id, right_id, assessment, observation, next_action in boundary_specs:
        cross = by_id[cross_id]["metrics"]
        left = by_id[left_id]["metrics"]
        right = by_id[right_id]["metrics"]
        comparison: dict[str, Any] = {}
        exceeds_both_count = 0
        exceeds_mean_count = 0
        for key in cross:
            maximum = max(left[key], right[key])
            neighbor_mean = (left[key] + right[key]) / 2
            exceeds_both = cross[key] > maximum
            exceeds_mean = cross[key] > neighbor_mean
            exceeds_both_count += int(exceeds_both)
            exceeds_mean_count += int(exceeds_mean)
            comparison[key] = {
                "cross_route": cross[key],
                "left_within_route": left[key],
                "right_within_route": right[key],
                "adjacent_within_route_mean": round((left[key] + right[key]) / 2, 6),
                "cross_minus_adjacent_mean": round(cross[key] - (left[key] + right[key]) / 2, 6),
                "cross_to_adjacent_mean_ratio": round(cross[key] / ((left[key] + right[key]) / 2), 6) if left[key] + right[key] else None,
                "cross_exceeds_adjacent_within_route_mean": exceeds_mean,
                "cross_exceeds_both_adjacent_within_route_pairs": exceeds_both,
            }
        boundaries.append(
            {
                "boundary_id": boundary_id,
                "cross_pair_id": cross_id,
                "neighbor_pair_ids": [left_id, right_id],
                "proxy_comparison": comparison,
                "proxy_rule_result": {
                    "rule": "COUNT_PAIRED_HISTOGRAM_DISTANCES_WHERE_CROSS_ROUTE_EXCEEDS_THE_MEAN_OF_ITS_TWO_ADJACENT_WITHIN_ROUTE_PAIRS",
                    "distances_exceeding_adjacent_mean": exceeds_mean_count,
                    "distances_exceeding_both": exceeds_both_count,
                    "distances_evaluated": len(cross),
                    "supports_above_local_mean_on_both_histogram_proxies": exceeds_mean_count == len(cross),
                },
                "manual_observation": {
                    "reviewer": "Codex agent visual review",
                    "basis_path": BOUNDARY_SHEET.relative_to(ROOT).as_posix(),
                    "basis_sha256": sha256(BOUNDARY_SHEET),
                    "observation": observation,
                    "confound": "The route cut also changes narrative sequence, subject matter, shot scale, and/or aspect ratio; neither histogram distance nor this observation isolates style as the cause.",
                },
                "assessment": assessment,
                "smallest_no_upload_next_action": next_action,
                "owner_acceptance": None,
                "rights_clearance": None,
                "commercially_cleared": None,
                "exact_production_base": None,
            }
        )

    source_inputs = [
        CADENCE_EVIDENCE,
        CADENCE_MANIFEST,
        BOUNDARY_SHEET,
        *[ROOT / row["source"]["path"] for row in panels],
    ]
    return {
        "record_type": "CH05SequenceCadenceBoundaryAudit",
        "schema_version": "1.0",
        "record_id": "ng-ch05-sequence-cadence-boundary-audit-r1",
        "state": "MEASURED_NON_GATING_CONTINUITY_RISK_AUDIT_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in source_inputs],
        "coverage": {"source_panels": 8, "pair_comparisons": 6, "cross_route_boundaries": 2, "adjacent_within_route_controls": 4, "new_generated_images": 0, "external_uploads": 0},
        "method": {
            "panel_normalization": "Entropy and edge density resize each panel to 390 px wide with aspect preserved. Histogram distances resize both images to 256x256 RGB with Lanczos solely for deterministic equal-sample comparison.",
            "grayscale_entropy_bits": "Shannon entropy of the normalized 8-bit luminance histogram.",
            "edge_density_ge_32": "Fraction of non-border pixels whose Pillow FIND_EDGES luminance value is >=32.",
            "png_bytes_per_native_pixel": "Source PNG bytes divided by native pixel count; compression-sensitive supporting cue only.",
            "luminance_histogram_total_variation": "Total-variation distance over normalized 256-bin luminance histograms; 0 means identical histograms and 1 means disjoint histograms.",
            "rgb_64_bin_histogram_mean_channel_total_variation": "Mean of R/G/B channel total-variation distances after deterministic aggregation into 64 bins per channel.",
            "interpretation_boundary": "These are content-, crop-, aspect-, codec-, and resize-sensitive proxies. They do not measure artistic quality, narrative quality, identity, or production fitness and cannot attribute a difference to route/style alone.",
        },
        "panels": panels,
        "pairs": pairs,
        "boundaries": boundaries,
        "recommendation": {
            "route_selection_changed": False,
            "pixel_edits_authorized_or_performed": False,
            "next_action": "Run a zero-upload, no-new-pixel three-arm P005→P006 control using already-existing candidates: selected reduced→R6, all-reduced, and all-R6. Holding the two panel IDs/story beats fixed will better separate route-switch contribution from content change. Keep P039→P040 unchanged unless owner review finds a semantic or identity issue.",
            "reason": "The first boundary warrants one controlled existing-pixel attribution check, while the second does not justify an intervention from proxy/manual evidence alone.",
        },
        "spend": {"direct_paid_api_cloud_usd": 0.0, "built_in_product_monetary_cost_usd": None},
        "owner_disposition": {"accepted": None, "rights_cleared": None, "commercially_cleared": None, "exact_production_base": None},
        "limitations": [
            "Manual observations are transparent non-gating agent review of the existing boundary sheet.",
            "The compared pairs depict different content and use different panel shapes, so proxy distances are not controlled style-only effects.",
            "No new image was generated, edited, uploaded, or accepted.",
            "No commercial-use, license, rights, or exact-production-base conclusion is made.",
        ],
        "boundary": "Evidence and smallest-next-action recommendation only; no owner acceptance, rights clearance, commercial clearance, pixel repair, canon replacement, or exact production-base decision.",
    }


def main() -> int:
    document = build_document()
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": EVIDENCE.relative_to(ROOT).as_posix(), "sha256": sha256(EVIDENCE), "boundaries": [{"boundary_id": row["boundary_id"], "assessment": row["assessment"], "proxy_rule_result": row["proxy_rule_result"]} for row in document["boundaries"]]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
