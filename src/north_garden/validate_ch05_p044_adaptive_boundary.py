"""Compare bounded inward widths on the exact P044 fine-feature stress geometry."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from validate_ch05_p036_mask_topology import components, inward_alpha
from validate_ch05_p044_fixed_boundary_stress import draw_mask


ROOT = Path(__file__).resolve().parents[2]
STRESS = ROOT / "docs/research/evidence/ch05-p044-fixed-16px-boundary-stress-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
OUT = ROOT / "experiments/outputs/ch05_p044_adaptive_boundary_r1/ch05-p044-selected-05px-alpha-r1.png"
REPORT = ROOT / "docs/research/evidence/ch05-p044-adaptive-boundary-width-r1.json"
WIDTHS = [1, 2, 3, 4, 5, 6, 8, 10, 12, 16]
SIZE = (1536, 1024)


class AdaptiveError(RuntimeError):
    """P044 adaptive-boundary evidence failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AdaptiveError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def source(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}


def alpha_gradient_max(alpha: np.ndarray) -> float:
    horizontal = np.abs(alpha[:, 1:] - alpha[:, :-1]).max()
    vertical = np.abs(alpha[1:, :] - alpha[:-1, :]).max()
    return float(max(horizontal, vertical))


def png_bytes(array: np.ndarray) -> bytes:
    buffer = BytesIO()
    Image.fromarray(array, "L").save(buffer, format="PNG", compress_level=6)
    return buffer.getvalue()


def build_report(*, write: bool) -> dict[str, Any]:
    stress = json.loads(STRESS.read_text(encoding="utf-8"))
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    panel = next(item for item in plans["plans"] if item["panel_id"] == "ng-ch05-sc01-p044")
    require(stress["decision"]["fixed_16px_compatible_with_fine_feature_control"] is False, "fixed-width rejection changed")
    require(stress["fixed_policy"]["tuned_within_experiment"] is False, "fixed stress was tuned")
    require(stress["measurements"]["fully_replaced_core_pixels"] == 0, "fixed stress core changed")
    require(plans["animation_shot_plan"] is None, "CH05 plans gained AnimationShotPlan")

    protected = draw_mask("protected_hands")
    blade = draw_mask("blade") & ~protected
    twine = draw_mask("twine") & ~protected
    support = blade | twine
    support_path = ROOT / stress["outputs"]["support_mask"]["path"]
    require(sha256_file(support_path) == stress["outputs"]["support_mask"]["sha256"], "stress support bytes changed")
    require(np.array_equal(np.asarray(Image.open(support_path).convert("L")) > 0, support), "stress support geometry changed")

    rect = panel["comic_direction"]["lettering"]["safe_zones"][0]["rect_norm"]
    x, y, width, height = rect
    lettering = np.zeros((SIZE[1], SIZE[0]), dtype=bool)
    lettering[round(y * SIZE[1]):round((y + height) * SIZE[1]), round(x * SIZE[0]):round((x + width) * SIZE[0])] = True
    variants = []
    alphas: dict[int, np.ndarray] = {}
    for feather_width in WIDTHS:
        alpha, core = inward_alpha(support, feather_width)
        alphas[feather_width] = alpha
        blade_core = int(np.count_nonzero(core & blade))
        twine_core = int(np.count_nonzero(core & twine))
        metrics = {
            "feather_width_px": feather_width,
            "fully_replaced_core_pixels": int(core.sum()),
            "fully_replaced_core_fraction_of_support": round(float(core.sum() / support.sum()), 9),
            "fully_replaced_core_component_count": len(components(core)),
            "nonzero_alpha_component_count": len(components(alpha > 0)),
            "blade_core_fraction": round(float(blade_core / blade.sum()), 9),
            "twine_core_fraction": round(float(twine_core / twine.sum()), 9),
            "max_neighbor_alpha_step": round(alpha_gradient_max(alpha), 9),
            "protected_hand_overlap_pixels": int(np.count_nonzero((alpha > 0) & protected)),
            "lettering_overlap_pixels": int(np.count_nonzero((alpha > 0) & lettering)),
        }
        metrics["qualifies"] = (
            metrics["fully_replaced_core_fraction_of_support"] >= 0.15
            and metrics["fully_replaced_core_component_count"] == 1
            and metrics["nonzero_alpha_component_count"] == 1
            and metrics["blade_core_fraction"] >= 0.15
            and metrics["twine_core_fraction"] >= 0.15
            and metrics["protected_hand_overlap_pixels"] == 0
            and metrics["lettering_overlap_pixels"] == 0
        )
        variants.append(metrics)
    qualifying = [item for item in variants if item["qualifies"]]
    selected_width = max(qualifying, key=lambda item: item["feather_width_px"])["feather_width_px"] if qualifying else None
    require(selected_width == 5, f"unexpected adaptive width selection: {selected_width}")
    require(next(item for item in variants if item["feather_width_px"] == 6)["qualifies"] is False,
            "width 6 no longer supplies the first failing bound")
    selected = next(item for item in variants if item["feather_width_px"] == selected_width)

    # Exact exterior check using the unchanged support.
    alpha = alphas[selected_width]
    base = np.zeros((SIZE[1], SIZE[0], 3), dtype=np.float64)
    base[:, :, :] = (48, 52, 55)
    synthetic = base.copy()
    synthetic[support] = (166, 118, 58)
    composite = np.rint(base * (1 - alpha[:, :, None]) + synthetic * alpha[:, :, None]).astype(np.uint8)
    outside = np.abs(composite.astype(np.int16) - base.astype(np.int16))[~support]
    require(int(outside.max()) == 0, "adaptive composite changed exterior")

    alpha_bytes = png_bytes(np.rint(alpha * 255).astype(np.uint8))
    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        if OUT.exists():
            require(OUT.read_bytes() == alpha_bytes, "existing adaptive alpha differs; refusing overwrite")
        else:
            OUT.write_bytes(alpha_bytes)
    return {
        "record_type": "ComicRepairAdaptiveBoundaryWidthControl",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p044-adaptive-boundary-width-r1",
        "state": "LOCAL_ADAPTIVE_WIDTH_MECHANICS_SELECTED_NOT_PRODUCTION_POLICY",
        "inputs": {
            "fixed_boundary_stress": source(STRESS),
            "comic_panel_plan": {**source(PLANS), "panel_id": panel["panel_id"], "plan_revision_id": panel["plan_revision_id"]},
            "exact_support_mask": {"path": support_path.relative_to(ROOT).as_posix(), "sha256": sha256_file(support_path)},
        },
        "method": {
            "widths_px": WIDTHS,
            "geometry_changed": False,
            "support_widened": False,
            "selection_rule": "widest width with one core/nonzero-alpha component, >=15% union/blade/twine core, zero protected-hand and lettering overlap, and exact exterior",
            "selection_direction": "widest qualifying width favors the smoothest available alpha transition subject to topology retention",
        },
        "variants": variants,
        "decision": {
            "selected_adaptive_width_px": selected_width,
            "selected_measurements": selected,
            "first_failing_larger_tested_width_px": 6,
            "p044_production_policy_authored": False,
            "production_mask_approved": False,
            "provider_route_changed": False,
            "external_action_authorized": False,
        },
        "output": {"selected_inward_alpha": {"path": OUT.relative_to(ROOT).as_posix(), "sha256": sha256_bytes(alpha_bytes)}},
        "validation": {
            "synthetic_composite_max_abs_difference_outside_support": int(outside.max()),
            "support_sha256_unchanged_from_stress": True,
        },
        "comic_boundary": {"comic_panel_plan_only": True, "animation_shot_plan": None, "e_conte": None},
        "review": {"human_review_status": "not_yet_performed", "human_minutes": None, "accepted": False},
        "activity": {"provider_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"},
        "limitations": [
            "The 5px result is selected only for this exact abstract 18px-blade/12px-twine control.",
            "It does not establish a universal width formula, visual seam quality, anatomy, identity continuity, or production acceptance.",
            "The support is hash-identical to the fixed stress; no geometry was widened or redrawn.",
            "No P044 policy, base, mask approval, provider request, or external authority follows.",
        ],
    }


def mutation_checks(expected: dict[str, Any]) -> tuple[int, int]:
    mutations = []
    changed = copy.deepcopy(expected); changed["inputs"]["exact_support_mask"]["sha256"] = "0" * 64; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["method"]["widths_px"].remove(6); mutations.append(changed)
    changed = copy.deepcopy(expected); changed["method"]["geometry_changed"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["selected_adaptive_width_px"] = 6; mutations.append(changed)
    changed = copy.deepcopy(expected); selected = changed["decision"]["selected_measurements"]; selected["twine_core_fraction"] = 0; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["validation"]["synthetic_composite_max_abs_difference_outside_support"] = 1; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["p044_production_policy_authored"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["external_action_authorized"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["review"] = {"human_review_status": "completed", "human_minutes": 1, "accepted": True}; mutations.append(changed)
    return sum(item != expected for item in mutations), len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--emit", type=Path)
    args = parser.parse_args()
    try:
        expected = build_report(write=args.build)
        if args.emit:
            output = args.emit if args.emit.is_absolute() else ROOT / args.emit
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
            print(f"wrote {output.relative_to(ROOT).as_posix()}")
        else:
            tracked = json.loads(REPORT.read_text(encoding="utf-8"))
            require(tracked == expected, "tracked P044 adaptive-boundary evidence differs")
            require(OUT.is_file() and sha256_file(OUT) == tracked["output"]["selected_inward_alpha"]["sha256"], "adaptive alpha missing or changed")
        rejected, total = mutation_checks(expected)
        require(rejected == total, "adaptive-boundary mutation rejection incomplete")
    except (AdaptiveError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    m = expected["decision"]["selected_measurements"]
    print("0 failures, 0 warnings")
    print(f"selected 5px as widest pass: union {m['fully_replaced_core_fraction_of_support']:.3%}, blade {m['blade_core_fraction']:.3%}, twine {m['twine_core_fraction']:.3%}")
    print("width 6 is first larger failure; unchanged support; 0 protected/lettering/exterior change")
    print(f"{rejected}/{total} support/series/geometry/selection/core/exterior/authority/review mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
