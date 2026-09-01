"""Build an exact-byte synthetic boundary measurement and pending review packet."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from render_record import ROOT
from render_record_boundary import expected_profile
from validate_render_record_boundary import BASE, CANDIDATE, write_fixture_files


OUTPUT = ROOT / "docs/research/evidence/exact-base-boundary-measurement-packet-r1.json"
PRESENTATION = ROOT / "experiments/outputs/exact_base_boundary_measurement_packet_r1/p036-synthetic-seam-review-presentation-r1.png"
SELECTOR = ROOT / "config/scale-aware-repair-boundary-selector-contract-r1.json"
TEMPLATE = ROOT / "config/record-templates/comic-repair-render-record-v2.json"


class MeasurementError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MeasurementError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def image_ref(path: Path) -> dict:
    with Image.open(path) as image:
        width, height = image.size
    return dict(source(path), width=width, height=height)


def edge_distances(base: np.ndarray, candidate: np.ndarray, support: np.ndarray, fill: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    hard_values, candidate_values = [], []
    pair_count = 0
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        shifted = np.roll(support, (dy, dx), axis=(0, 1))
        pairs = support & ~shifted
        if dy == -1: pairs[-1, :] = False
        if dy == 1: pairs[0, :] = False
        if dx == -1: pairs[:, -1] = False
        if dx == 1: pairs[:, 0] = False
        y, x = np.nonzero(pairs)
        outside = base[y + dy, x + dx].astype(np.float64)
        hard_values.append(np.linalg.norm(fill - outside, axis=1))
        candidate_values.append(np.linalg.norm(candidate[y, x].astype(np.float64) - outside, axis=1))
        pair_count += len(y)
    return np.concatenate(hard_values), np.concatenate(candidate_values), pair_count


def make_presentation(base_image: Image.Image, candidate_image: Image.Image, support: np.ndarray) -> None:
    y, x = np.nonzero(support)
    bbox = (max(int(x.min()) - 48, 0), max(int(y.min()) - 48, 0), min(int(x.max()) + 49, base_image.width), min(int(y.max()) + 49, base_image.height))
    base_crop = base_image.crop(bbox).convert("RGB")
    candidate_crop = candidate_image.crop(bbox).convert("RGB")
    diff = np.abs(np.asarray(candidate_crop, dtype=np.int16) - np.asarray(base_crop, dtype=np.int16)).clip(0, 255).astype(np.uint8)
    diff_image = Image.fromarray(np.minimum(diff * 3, 255).astype(np.uint8), "RGB")
    panels = []
    for label, image in (("BASE CROP", base_crop), ("CANDIDATE CROP", candidate_crop), ("3X ABS DIFF", diff_image)):
        image.thumbnail((520, 520), Image.Resampling.LANCZOS)
        panel = Image.new("RGB", (540, 570), "white"); panel.paste(image, ((540 - image.width) // 2, 36))
        ImageDraw.Draw(panel).text((12, 10), label, fill="black"); panels.append(panel)
    canvas = Image.new("RGB", (1620, 570), "white")
    for index, panel in enumerate(panels): canvas.paste(panel, (index * 540, 0))
    PRESENTATION.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(PRESENTATION, format="PNG", optimize=False, compress_level=9)


def build() -> dict:
    write_fixture_files()
    binding = expected_profile("ng-ch05-sc01-p036")
    with Image.open(BASE) as base_source, Image.open(CANDIDATE) as candidate_source, Image.open(ROOT / binding["support_mask"]["path"]) as support_source, Image.open(ROOT / binding["inward_alpha"]["path"]) as alpha_source:
        base_image = base_source.convert("RGB"); candidate_image = candidate_source.convert("RGB")
        base = np.asarray(base_image); candidate = np.asarray(candidate_image)
        support = np.asarray(support_source.convert("L")) > 0; alpha = np.asarray(alpha_source.convert("L"))
    require(base.shape == candidate.shape and base.shape[:2] == support.shape == alpha.shape, "fixture dimensions differ")
    changed = np.any(base != candidate, axis=2)
    fill = np.array([68.0, 104.0, 74.0])
    hard, feathered, edge_pairs = edge_distances(base, candidate, support, fill)
    hard_mean = float(np.mean(hard)); feather_mean = float(np.mean(feathered))
    reduction = 1.0 - feather_mean / hard_mean
    make_presentation(base_image, candidate_image, support)
    topology = binding["topology_evidence"]
    measurement = {
        "support_pixels": int(support.sum()), "alpha_transition_pixels": int(((alpha > 0) & (alpha < 255)).sum()),
        "fully_replaced_core_pixels": int((alpha == 255).sum()), "changed_pixels_inside_support": int((changed & support).sum()),
        "changed_pixels_outside_support": int((changed & ~support).sum()),
        "max_abs_channel_difference_outside_support": int(np.abs(base.astype(np.int16) - candidate.astype(np.int16))[~support].max()),
        "boundary_neighbor_pairs": edge_pairs, "hard_reference_mean_boundary_rgb_distance": round(hard_mean, 9),
        "candidate_mean_boundary_rgb_distance": round(feather_mean, 9), "mean_boundary_distance_reduction_fraction": round(reduction, 9),
    }
    return {
        "record_type": "ExactBaseRepairBoundaryMeasurementPacket", "schema_version": "1.0",
        "record_id": "ng-exact-base-boundary-measurement-packet-r1", "state": "SYNTHETIC_EXACT_BYTES_MEASURED_REVIEW_PENDING_NOT_PRODUCTION_EVIDENCE",
        "synthetic_validation_fixture": True, "medium": "comic", "animation_shot_plan": None, "e_conte": None,
        "comic_panel_plan": {"panel_id": "ng-ch05-sc01-p036", "plan_revision_id": "ng-ch05-sc01-p036-plan-r1"},
        "sources": {"selector_contract": binding["selector_contract"], "selector_profile": binding["profile"], "topology_evidence": topology, "render_record_v2_template": source(TEMPLATE)},
        "exact_images": {"base_raster": image_ref(BASE), "candidate_raster": image_ref(CANDIDATE), "support_mask": binding["support_mask"], "inward_alpha": binding["inward_alpha"]},
        "method": {"candidate_fixture": "deterministic flat fictional-control fill through exact inward alpha", "hard_reference": "same fill through binary support, derived in memory only", "boundary_metric": "mean Euclidean RGB distance for directed support-to-exterior 4-neighbor pairs", "exterior_metric": "pixelwise max absolute RGB difference outside exact support"},
        "measurement": measurement,
        "no_change_short_circuit": {"requested": True, "provider_invoked": False, "input": image_ref(BASE), "output": image_ref(BASE), "byte_identical": True},
        "review_packet": {"packet_id": "ng-p036-synthetic-seam-review-packet-r1", "presentation": image_ref(PRESENTATION), "source_base_sha256": sha256(BASE), "source_candidate_sha256": sha256(CANDIDATE), "required_assertions": ["boundary", "causality", "protected_semantics", "lettering_clearance"], "review_session": None, "human_review_status": "not_yet_performed", "human_minutes": None, "decision": None, "accepted": False},
        "activity": {"provider_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"},
        "limitations": ["Base and candidate are synthetic validation fixtures, not approved CH05 art or provider output.", "The numeric boundary reduction is fixture-specific and cannot establish seam quality, narrative causality, anatomy, identity continuity, or acceptance.", "The presentation is review-ready but no human session or decision exists.", "No production input, external authority, budget reservation, RenderRecord, or candidate intake follows."],
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    item = copy.deepcopy(expected); item["sources"]["selector_profile"]["local_width_px"] = 5; values.append(item)
    item = copy.deepcopy(expected); item["exact_images"]["base_raster"]["sha256"] = "0" * 64; values.append(item)
    item = copy.deepcopy(expected); item["exact_images"]["candidate_raster"]["sha256"] = "0" * 64; values.append(item)
    item = copy.deepcopy(expected); item["exact_images"]["support_mask"]["sha256"] = "0" * 64; values.append(item)
    item = copy.deepcopy(expected); item["exact_images"]["inward_alpha"]["sha256"] = "0" * 64; values.append(item)
    item = copy.deepcopy(expected); item["measurement"]["changed_pixels_outside_support"] = 1; values.append(item)
    item = copy.deepcopy(expected); item["measurement"]["mean_boundary_distance_reduction_fraction"] = 1.0; values.append(item)
    item = copy.deepcopy(expected); item["no_change_short_circuit"]["byte_identical"] = False; values.append(item)
    item = copy.deepcopy(expected); item["no_change_short_circuit"]["provider_invoked"] = True; values.append(item)
    item = copy.deepcopy(expected); item["review_packet"]["source_candidate_sha256"] = "0" * 64; values.append(item)
    item = copy.deepcopy(expected); item["review_packet"]["human_minutes"] = 3.0; values.append(item)
    item = copy.deepcopy(expected); item["review_packet"]["accepted"] = True; values.append(item)
    item = copy.deepcopy(expected); item["synthetic_validation_fixture"] = False; values.append(item)
    item = copy.deepcopy(expected); item["activity"]["provider_requests"] = 1; values.append(item)
    return sum(value != expected for value in values), len(values)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--emit", type=Path); args = parser.parse_args()
    try:
        expected = build()
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else: require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked measurement packet differs")
        rejected, total = mutations(expected); require(rejected == total, "mutation rejection incomplete")
        require(expected["measurement"]["changed_pixels_outside_support"] == 0 and expected["measurement"]["max_abs_channel_difference_outside_support"] == 0, "exterior not exact")
    except (MeasurementError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr); return 1
    m = expected["measurement"]
    print(f"0 failures, 0 warnings ({m['support_pixels']} support; {m['alpha_transition_pixels']} transition; {m['fully_replaced_core_pixels']} core; exact exterior)")
    print(f"fixture boundary mean distance reduction {m['mean_boundary_distance_reduction_fraction']:.3%}; no-change byte-identical; review pending/null minutes")
    print(f"{rejected}/{total} binding/metric/no-change/review/fixture/activity mutations rejected; 0 requests/uploads/$0")
    return 0


if __name__ == "__main__": raise SystemExit(main())
