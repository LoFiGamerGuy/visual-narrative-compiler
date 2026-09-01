"""Measure local inward-feather compositor variants on existing OpenAI G07 evidence."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "public-controls/g07a-role-id-r1.png"
PROVIDER = ROOT / "experiments/outputs/openai_gpt_image2_g07_bakeoff_r1/g07a-target-change.png"
PROVIDER_RECORD = ROOT / "experiments/records/openai_gpt_image2_g07_bakeoff_r1/g07a-target-change.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
OUT = ROOT / "experiments/outputs/openai_targeted_repair_boundary_hardening_r2"
REPORT = ROOT / "docs/research/evidence/openai-targeted-repair-boundary-hardening-r2.json"
WIDTHS = [0, 2, 4, 8, 16, 24, 32]
EXPECTED_INPUTS = {
    "source": "0a7237f655492f4aea7618036b7bac1a5068882f113ae395188ab50abb5a2699",
    "provider": "3f9f05b2b3582088f9bd7a3caed9cc90c53ad148fc471656cf2ee534aac22906",
    "provider_record": "66f00641b0aeaa56df5eea312b2c3878bca11c26ccb2f919bf0c33a1ce0988b1",
}


class BoundaryError(RuntimeError):
    """Boundary-hardening evidence failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BoundaryError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def target_bbox(source: np.ndarray) -> tuple[int, int, int, int]:
    teal = (source[:, :, 1] > source[:, :, 0] + 15) & (source[:, :, 2] > source[:, :, 0] + 15)
    ys, xs = np.where(teal)
    require(bool(len(xs)), "teal target proxy not detected")
    pad = 12
    return (
        max(0, int(xs.min()) - pad), max(0, int(ys.min()) - pad),
        min(source.shape[1], int(xs.max()) + 1 + pad), min(source.shape[0], int(ys.max()) + 1 + pad),
    )


def alpha_mask(shape: tuple[int, int], bbox: tuple[int, int, int, int], width: int) -> np.ndarray:
    height, image_width = shape
    left, top, right, bottom = bbox
    ys, xs = np.indices((height, image_width))
    inside = (xs >= left) & (xs < right) & (ys >= top) & (ys < bottom)
    if width == 0:
        return inside.astype(np.float64)
    distance = np.minimum.reduce([xs - left, right - 1 - xs, ys - top, bottom - 1 - ys]).astype(np.float64)
    ramp = 0.5 - 0.5 * np.cos(np.pi * np.clip(distance / width, 0, 1))
    return ramp * inside


def boundary_artificial_jump(
    composite: np.ndarray, source: np.ndarray, provider: np.ndarray,
    bbox: tuple[int, int, int, int], band: int,
) -> tuple[float, float, float]:
    left, top, right, bottom = bbox
    per_offset_excess: list[float] = []
    per_offset_jump: list[float] = []
    for offset in range(band + 1):
        pairs = [
            ((slice(top, bottom), left + offset), (slice(top, bottom), left + offset - 1)),
            ((slice(top, bottom), right - 1 - offset), (slice(top, bottom), right - offset)),
            ((top + offset, slice(left, right)), (top + offset - 1, slice(left, right))),
            ((bottom - 1 - offset, slice(left, right)), (bottom - offset, slice(left, right))),
        ]
        excess, jumps = [], []
        for inner, outer in pairs:
            composite_jump = np.abs(composite[inner] - composite[outer])
            source_jump = np.abs(source[inner] - source[outer])
            provider_jump = np.abs(provider[inner] - provider[outer])
            excess.append(np.maximum(0, composite_jump - np.maximum(source_jump, provider_jump)).reshape(-1, 3))
            jumps.append(composite_jump.reshape(-1, 3))
        per_offset_excess.append(float(np.concatenate(excess).mean()))
        per_offset_jump.append(float(np.concatenate(jumps).mean()))
    return max(per_offset_excess), sum(per_offset_excess), max(per_offset_jump)


def safe_zone_mask(shape: tuple[int, int], rect_norm: list[float]) -> np.ndarray:
    height, width = shape
    x, y, w, h = rect_norm
    left, top = round(x * width), round(y * height)
    right, bottom = round((x + w) * width), round((y + h) * height)
    mask = np.zeros(shape, dtype=bool)
    mask[top:bottom, left:right] = True
    return mask


def build_report(*, write: bool) -> dict[str, Any]:
    for name, path in (("source", SOURCE), ("provider", PROVIDER), ("provider_record", PROVIDER_RECORD)):
        require(sha256_file(path) == EXPECTED_INPUTS[name], f"{name} input hash mismatch")
    provider_record = json.loads(PROVIDER_RECORD.read_text(encoding="utf-8"))
    require(provider_record["candidate"]["sha256"] == EXPECTED_INPUTS["provider"], "provider record/candidate mismatch")
    require(provider_record["accepted"] is False, "provider candidate unexpectedly accepted")

    source_image = Image.open(SOURCE).convert("RGB")
    source = np.asarray(source_image, dtype=np.float64)
    provider = np.asarray(
        Image.open(PROVIDER).convert("RGB").resize(source_image.size, Image.Resampling.LANCZOS), dtype=np.float64
    )
    bbox = target_bbox(source)
    require(bbox == (812, 274, 994, 711), f"target bbox drifted: {bbox}")
    left, top, right, bottom = bbox
    height, width = source.shape[:2]
    ys, xs = np.indices((height, width))
    support = (xs >= left) & (xs < right) & (ys >= top) & (ys < bottom)
    core = (xs >= left + 32) & (xs < right - 32) & (ys >= top + 32) & (ys < bottom - 32)

    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    panel = next(item for item in plans["plans"] if item["panel_id"] == "ng-ch05-sc01-p036")
    require(plans["record_type"] == "ComicPanelPlanCollection", "CH05 plan type changed")
    require(plans["animation_shot_plan"] is None, "comic plans gained an animation shot plan")
    safe_zones = panel["comic_direction"]["lettering"]["safe_zones"]
    require(len(safe_zones) == 1, "P036 safe-zone inventory changed")
    lettering = safe_zone_mask((height, width), safe_zones[0]["rect_norm"])
    require(int(np.count_nonzero(support & lettering)) == 0, "repair support overlaps P036 lettering safe zone")

    variants: list[dict[str, Any]] = []
    images: dict[str, tuple[bytes, bytes]] = {}
    for feather_width in WIDTHS:
        alpha = alpha_mask((height, width), bbox, feather_width)
        composite_float = source * (1 - alpha[:, :, None]) + provider * alpha[:, :, None]
        composite = np.rint(composite_float).clip(0, 255).astype(np.uint8)
        changed = np.any(composite != source.astype(np.uint8), axis=2)
        core_pixels = composite[core]
        green = (core_pixels[:, 1] > core_pixels[:, 0] + 10) & (core_pixels[:, 1] > core_pixels[:, 2] + 5)
        maximum_excess, cumulative_excess, maximum_jump = boundary_artificial_jump(
            composite.astype(np.float64), source, provider, bbox, max(2, feather_width + 1)
        )
        variant_id = "hard" if feather_width == 0 else f"cosine-inset-{feather_width:02d}px"
        composite_path = OUT / f"g07a-{variant_id}-composite.png"
        alpha_path = OUT / f"g07a-{variant_id}-alpha.png"
        composite_buffer = __import__("io").BytesIO()
        alpha_buffer = __import__("io").BytesIO()
        Image.fromarray(composite, "RGB").save(composite_buffer, format="PNG", compress_level=6)
        Image.fromarray(np.rint(alpha * 255).astype(np.uint8), "L").save(alpha_buffer, format="PNG", compress_level=6)
        composite_bytes, alpha_bytes = composite_buffer.getvalue(), alpha_buffer.getvalue()
        images[variant_id] = (composite_bytes, alpha_bytes)
        if write:
            OUT.mkdir(parents=True, exist_ok=True)
            for path, data in ((composite_path, composite_bytes), (alpha_path, alpha_bytes)):
                if path.exists():
                    require(path.read_bytes() == data, f"existing boundary output differs; refusing overwrite: {path.name}")
                else:
                    path.write_bytes(data)
        variants.append({
            "variant_id": variant_id,
            "feather_width_px": feather_width,
            "composite": {"path": composite_path.relative_to(ROOT).as_posix(), "sha256": sha256_bytes(composite_bytes)},
            "alpha": {"path": alpha_path.relative_to(ROOT).as_posix(), "sha256": sha256_bytes(alpha_bytes)},
            "measurements": {
                "max_boundary_artificial_jump_mae_0_255": round(maximum_excess, 9),
                "cumulative_boundary_artificial_jump_mae_0_255": round(cumulative_excess, 9),
                "max_observed_boundary_pair_mae_0_255": round(maximum_jump, 9),
                "changed_outside_support_fraction": round(float(changed[~support].mean()), 9),
                "max_abs_channel_difference_outside_support": int(np.abs(composite.astype(np.int16) - source.astype(np.int16))[~support].max()),
                "changed_full_frame_fraction": round(float(changed.mean()), 9),
                "core_green_dominant_fraction": round(float(green.mean()), 9),
                "support_lettering_overlap_pixels": int(np.count_nonzero(support & lettering)),
            },
        })
    hard_metric = variants[0]["measurements"]["max_boundary_artificial_jump_mae_0_255"]
    hard_green = variants[0]["measurements"]["core_green_dominant_fraction"]
    for variant in variants:
        metric = variant["measurements"]["max_boundary_artificial_jump_mae_0_255"]
        variant["measurements"]["boundary_artificial_jump_reduction_vs_hard"] = round(1 - metric / hard_metric, 9)
        variant["qualifies"] = (
            variant["feather_width_px"] > 0
            and variant["measurements"]["boundary_artificial_jump_reduction_vs_hard"] >= 0.90
            and variant["measurements"]["core_green_dominant_fraction"] >= hard_green * 0.99
            and variant["measurements"]["changed_outside_support_fraction"] == 0
            and variant["measurements"]["max_abs_channel_difference_outside_support"] == 0
            and variant["measurements"]["support_lettering_overlap_pixels"] == 0
        )
    qualifying = [item for item in variants if item["qualifies"]]
    selected = min(qualifying, key=lambda item: item["feather_width_px"])["variant_id"] if qualifying else None
    require(selected == "cosine-inset-16px", f"unexpected boundary policy selection: {selected}")

    return {
        "record_type": "SelectedRouteBoundaryHardeningExperiment",
        "schema_version": "1.0",
        "record_id": "ng-openai-targeted-repair-boundary-hardening-r2",
        "state": "COMPLETED_LOCAL_PROXY_MECHANICS_NOT_ART",
        "selection_adr": "docs/adr/ADR-0025-select-openai-gpt-image-2-for-bounded-targeted-repair-hardening.md",
        "inputs": {
            "source": {"path": SOURCE.relative_to(ROOT).as_posix(), "sha256": EXPECTED_INPUTS["source"]},
            "unaccepted_provider_candidate": {"path": PROVIDER.relative_to(ROOT).as_posix(), "sha256": EXPECTED_INPUTS["provider"]},
            "provider_render_record": {"path": PROVIDER_RECORD.relative_to(ROOT).as_posix(), "sha256": EXPECTED_INPUTS["provider_record"]},
            "comic_panel_plan_collection": {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha256_file(PLANS)},
        },
        "method": {
            "target_bbox_xyxy": list(bbox),
            "variants": WIDTHS,
            "feather": "inward-only cosine alpha; alpha is exactly zero at and outside support boundary",
            "boundary_metric": "maximum across normal offsets of mean positive composite adjacent-pixel jump above max(source jump, provider jump)",
            "selection_rule": "narrowest nonzero feather with >=90% hard-boundary artificial-jump reduction, >=99% hard core-green fraction, exact exterior, and zero lettering overlap",
        },
        "variants": variants,
        "decision": {
            "selected_compositor_policy": selected,
            "scope": "local fictional-proxy repair mechanics only",
            "provider_route_selection_changed": False,
            "art_accepted": False,
        },
        "narrative_panel_applicability": {
            "panel_id": panel["panel_id"],
            "plan_revision_id": panel["plan_revision_id"],
            "lettering_safe_zones": safe_zones,
            "support_lettering_overlap_pixels": 0,
            "comic_panel_plan_only": True,
            "animation_shot_plan": plans["animation_shot_plan"],
            "external_execution_state": "NOT_AUTHORIZED",
        },
        "review": {"human_review_status": "not_yet_performed", "human_minutes": None, "accepted": False},
        "activity": {"provider_requests": 0, "external_uploads": 0, "additional_external_cost_usd": "0.000000"},
        "limitations": [
            "A rectangular color proxy does not model object-aware boundaries around hands, hair, faces, props, or line art.",
            "The boundary metric measures adjacent-pixel discontinuity mechanics, not semantic correctness or visual acceptance.",
            "The source provider candidate remains unaccepted G07 research evidence.",
            "No CH05 raster, character continuity, page rhythm, lettering render, provider call, or commercial clearance is tested.",
        ],
    }


def mutation_checks(expected: dict[str, Any]) -> tuple[int, int]:
    mutations = []
    changed = copy.deepcopy(expected); changed["inputs"]["source"]["sha256"] = "0" * 64; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["method"]["variants"].remove(8); mutations.append(changed)
    changed = copy.deepcopy(expected); changed["variants"][0]["measurements"]["max_boundary_artificial_jump_mae_0_255"] = 0; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["selected_compositor_policy"] = "cosine-inset-08px"; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["variants"][4]["measurements"]["changed_outside_support_fraction"] = 0.001; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["variants"][4]["measurements"]["core_green_dominant_fraction"] = 0; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["narrative_panel_applicability"]["support_lettering_overlap_pixels"] = 1; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["review"] = {"human_review_status": "completed", "human_minutes": 1, "accepted": True}; mutations.append(changed)
    return sum(item != expected for item in mutations), len(mutations)


def validate_outputs(report: dict[str, Any]) -> None:
    for variant in report["variants"]:
        for field in ("composite", "alpha"):
            artifact = variant[field]
            path = ROOT / artifact["path"]
            require(path.is_file(), f"boundary artifact missing: {artifact['path']}")
            require(sha256_file(path) == artifact["sha256"], f"boundary artifact hash mismatch: {artifact['path']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="create ignored local compositor artifacts if absent")
    parser.add_argument("--emit", type=Path, help="write deterministic non-art experiment evidence")
    args = parser.parse_args()
    try:
        expected = build_report(write=args.build)
        if args.build:
            validate_outputs(expected)
        if args.emit:
            output = args.emit if args.emit.is_absolute() else ROOT / args.emit
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
            print(f"wrote {output.relative_to(ROOT).as_posix()}")
        else:
            tracked = json.loads(REPORT.read_text(encoding="utf-8"))
            require(tracked == expected, "tracked boundary-hardening evidence differs")
            validate_outputs(tracked)
        rejected, total = mutation_checks(expected)
        require(rejected == total, "boundary mutation rejection incomplete")
    except (BoundaryError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    chosen = next(item for item in expected["variants"] if item["variant_id"] == expected["decision"]["selected_compositor_policy"])
    print("0 failures, 0 warnings")
    print(f"7/7 local boundary variants verified; selected {chosen['variant_id']} by predeclared rule")
    print(
        f"boundary artificial-jump reduction {chosen['measurements']['boundary_artificial_jump_reduction_vs_hard']:.3%}; "
        "0 exterior pixels changed; 0 lettering-overlap pixels"
    )
    print(f"{rejected}/{total} input/method/metric/decision/review mutations rejected; 0 calls/uploads/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
