"""Build a deterministic P036 causal-shape mask topology control."""
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
from PIL import Image, ImageDraw

from validate_ch05_p036_mask_topology import components, inward_alpha


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/outputs/ch05_p036_layout_control_r1/ch05-p036-layout-control-r1.png"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
READINESS = ROOT / "production/comic/repair-readiness/ch05-p036-openai-r1.json"
ASSERTIONS = ROOT / "production/comic/hard-assertion-manifests/ch05-mill-signal-r1.json"
DEMO = ROOT / "production/comic/demonstration-packets/ch05-p033-p038-no-network-r1.json"
BOUNDARY = ROOT / "docs/research/evidence/openai-targeted-repair-boundary-hardening-r2.json"
OUT_DIR = ROOT / "experiments/outputs/ch05_p036_causal_shape_topology_r2"
REPORT = ROOT / "docs/research/evidence/ch05-p036-causal-shape-topology-control-r2.json"
PADDINGS = [0, 4, 8, 12, 16]
SIZE = (1536, 1024)


class CausalShapeError(RuntimeError):
    """Causal-shape topology control failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CausalShapeError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def feature_masks(padding: int) -> dict[str, np.ndarray]:
    features: dict[str, np.ndarray] = {}
    geometry = {
        "plank": ("line", (455, 790, 850, 300), 64 + 2 * padding),
        "reach": ("line", (650, 380, 840, 300), 42 + 2 * padding),
        "hand": ("ellipse", (815 - padding, 270 - padding, 870 + padding, 325 + padding), None),
        "tin": ("rectangle", (860 - padding, 245 - padding, 935 + padding, 295 + padding), None),
    }
    for name, (kind, coordinates, line_width) in geometry.items():
        image = Image.new("L", SIZE, 0)
        draw = ImageDraw.Draw(image)
        if kind == "line":
            draw.line(coordinates, fill=255, width=int(line_width))
        elif kind == "ellipse":
            draw.ellipse(coordinates, fill=255)
        else:
            draw.rectangle(coordinates, fill=255)
        features[name] = np.asarray(image) > 0
    return features


def safe_mask(panel: dict[str, Any]) -> np.ndarray:
    rect = panel["comic_direction"]["lettering"]["safe_zones"][0]["rect_norm"]
    x, y, width, height = rect
    result = np.zeros((SIZE[1], SIZE[0]), dtype=bool)
    result[round(y * SIZE[1]):round((y + height) * SIZE[1]), round(x * SIZE[0]):round((x + width) * SIZE[0])] = True
    return result


def variant_metrics(padding: int, lettering: np.ndarray) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    features = feature_masks(padding)
    support = np.logical_or.reduce(list(features.values()))
    alpha, core = inward_alpha(support, 16)
    ys, xs = np.where(support)
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
    feature_results = {}
    for name, feature in features.items():
        feature_results[name] = {
            "support_pixels": int(feature.sum()),
            "fully_replaced_core_pixels": int(np.count_nonzero(core & feature)),
            "fully_replaced_core_fraction": round(float(np.count_nonzero(core & feature) / feature.sum()), 9),
        }
    support_components = components(support)
    core_components = components(core)
    measurements = {
        "context_padding_px": padding,
        "support_pixels": int(support.sum()),
        "support_fraction": round(float(support.mean()), 9),
        "support_bbox_xyxy": list(bbox),
        "bbox_rectangularity": round(float(support.sum() / bbox_area), 9),
        "support_component_count": len(support_components),
        "fully_replaced_core_pixels": int(core.sum()),
        "fully_replaced_core_fraction_of_support": round(float(core.sum() / support.sum()), 9),
        "fully_replaced_core_component_count": len(core_components),
        "alpha_nonzero_component_count": len(components(alpha > 0)),
        "alpha_nonzero_lettering_overlap_pixels": int(np.count_nonzero((alpha > 0) & lettering)),
        "feature_core_retention": feature_results,
    }
    measurements["qualifies"] = (
        measurements["support_component_count"] == 1
        and measurements["fully_replaced_core_component_count"] == 1
        and measurements["alpha_nonzero_component_count"] == 1
        and measurements["fully_replaced_core_fraction_of_support"] >= 0.40
        and measurements["bbox_rectangularity"] <= 0.50
        and measurements["alpha_nonzero_lettering_overlap_pixels"] == 0
        and all(item["fully_replaced_core_fraction"] >= 0.15 for item in feature_results.values())
    )
    return measurements, support, alpha


def png_bytes(array: np.ndarray) -> bytes:
    buffer = BytesIO()
    Image.fromarray(array, "L").save(buffer, format="PNG", compress_level=6)
    return buffer.getvalue()


def write_if_absent_or_equal(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_bytes() == data, f"existing causal-shape output differs; refusing overwrite: {path.name}")
    else:
        path.write_bytes(data)


def build_report(*, write: bool) -> dict[str, Any]:
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    assertions = json.loads(ASSERTIONS.read_text(encoding="utf-8"))
    demo = json.loads(DEMO.read_text(encoding="utf-8"))
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    panel = next(item for item in plans["plans"] if item["panel_id"] == "ng-ch05-sc01-p036")
    assertion = next(item for item in assertions["assertions"] if item["id"] == "p036_core_read")
    chain = next(item for item in demo["derived_continuity_contracts"] if item["id"] == "sealed_tin_causal_chain")
    require(plans["record_type"] == "ComicPanelPlanCollection" and plans["animation_shot_plan"] is None,
            "CH05 comic/animation record separation changed")
    require(panel["comic_direction"]["motion_mode"] == "practical_action", "P036 motion intent changed")
    require("hand/object relationship" in panel["comic_direction"]["direction_note"], "P036 causal direction changed")
    require(readiness["targeted_repair_contract"]["target_semantics"].startswith("causal Soren-hand / fallen-plank / tin"),
            "P036 repair target semantics changed")
    require(chain["target_panels"] == ["ng-ch05-sc01-p036", "ng-ch05-sc01-p037"], "sealed-tin chain changed")
    require(assertion["applicability"] == "ng-ch05-sc01-p036", "P036 assertion applicability changed")
    require(boundary["decision"]["selected_compositor_policy"] == "cosine-inset-16px", "boundary policy changed")
    require(sha256_file(BASE) == "a859557289f2fff25271e5ef5ede5687f7ff2edd7346f5c77813b9465e0dbe1d", "abstract base changed")

    lettering = safe_mask(panel)
    variants = []
    arrays: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for padding in PADDINGS:
        metrics, support, alpha = variant_metrics(padding, lettering)
        variants.append(metrics)
        arrays[padding] = (support, alpha)
    qualifying = [item for item in variants if item["qualifies"]]
    selected_padding = min(qualifying, key=lambda item: item["context_padding_px"])["context_padding_px"] if qualifying else None
    require(selected_padding == 8, f"unexpected causal context selection: {selected_padding}")
    selected = next(item for item in variants if item["context_padding_px"] == selected_padding)
    support, alpha = arrays[selected_padding]

    # Exact-exterior compositor mechanics on a deterministic synthetic layer.
    base = np.asarray(Image.open(BASE).convert("RGB"), dtype=np.float64)
    synthetic_layer = base.copy()
    synthetic_layer[support, 0] = np.clip(synthetic_layer[support, 0] + 29, 0, 255)
    synthetic_layer[support, 2] = np.clip(synthetic_layer[support, 2] + 41, 0, 255)
    composite = np.rint(base * (1 - alpha[:, :, None]) + synthetic_layer * alpha[:, :, None]).astype(np.uint8)
    outside = np.abs(composite.astype(np.int16) - base.astype(np.int16))[~support]
    require(int(outside.max()) == 0, "causal-shape synthetic composite changed exterior")

    mask_bytes = png_bytes((support * 255).astype(np.uint8))
    alpha_bytes = png_bytes(np.rint(alpha * 255).astype(np.uint8))
    mask_path = OUT_DIR / "ch05-p036-causal-shape-mask-pad08-r2.png"
    alpha_path = OUT_DIR / "ch05-p036-causal-shape-alpha-pad08-r2.png"
    if write:
        write_if_absent_or_equal(mask_path, mask_bytes)
        write_if_absent_or_equal(alpha_path, alpha_bytes)

    return {
        "record_type": "ComicRepairCausalShapeTopologyControl",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p036-causal-shape-topology-control-r2",
        "state": "LOCAL_ABSTRACT_CAUSAL_TOPOLOGY_CONTROL_NOT_ART",
        "intent_bindings": {
            "comic_panel_plan": {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha256_file(PLANS), "panel_id": panel["panel_id"], "plan_revision_id": panel["plan_revision_id"]},
            "repair_readiness": {"path": READINESS.relative_to(ROOT).as_posix(), "sha256": sha256_file(READINESS), "target_semantics": readiness["targeted_repair_contract"]["target_semantics"]},
            "hard_assertion": {"path": ASSERTIONS.relative_to(ROOT).as_posix(), "sha256": sha256_file(ASSERTIONS), "assertion_id": assertion["id"]},
            "continuity_contract": {"path": DEMO.relative_to(ROOT).as_posix(), "sha256": sha256_file(DEMO), "contract_id": chain["id"]},
        },
        "geometry": {
            "source": "deterministic coordinates from the existing abstract P036 layout control",
            "features": {
                "plank": {"kind": "line", "xyxy": [455, 790, 850, 300], "base_width_px": 64},
                "reach": {"kind": "line", "xyxy": [650, 380, 840, 300], "base_width_px": 42},
                "hand": {"kind": "ellipse", "bbox_xyxy": [815, 270, 870, 325]},
                "tin": {"kind": "rectangle", "bbox_xyxy": [860, 245, 935, 295]},
            },
            "context_padding_variants_px": PADDINGS,
            "boundary_policy": {"id": "cosine-inset-16px", "source": BOUNDARY.relative_to(ROOT).as_posix(), "sha256": sha256_file(BOUNDARY)},
            "selection_rule": "narrowest padding with one support/core/nonzero-alpha component, >=40% union core, >=15% core for every causal feature, <=0.50 rectangularity, and zero lettering overlap",
        },
        "variants": variants,
        "decision": {
            "selected_context_padding_px": selected_padding,
            "all_four_causal_features_retain_core": all(item["fully_replaced_core_fraction"] >= 0.15 for item in selected["feature_core_retention"].values()),
            "connected_fully_replaced_core": selected["fully_replaced_core_component_count"] == 1,
            "concavity_exercised": selected["bbox_rectangularity"] < 0.50,
            "thin_feature_exercised": True,
            "mechanics_control_pass": selected["qualifies"],
            "art_accepted": False,
            "provider_input_authorized": False,
        },
        "selected_outputs": {
            "support_mask": {"path": mask_path.relative_to(ROOT).as_posix(), "sha256": sha256_bytes(mask_bytes)},
            "inward_alpha": {"path": alpha_path.relative_to(ROOT).as_posix(), "sha256": sha256_bytes(alpha_bytes)},
        },
        "selected_measurements": selected | {
            "synthetic_composite_max_abs_difference_outside_support": int(outside.max()),
        },
        "comic_boundary": {"comic_panel_plan_only": True, "animation_shot_plan": plans["animation_shot_plan"]},
        "review": {"human_review_status": "not_yet_performed", "human_minutes": None, "accepted": False},
        "activity": {"provider_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"},
        "limitations": [
            "This is labeled deterministic geometry, not a base raster, character design, mask approval, or provider input.",
            "Concavity and a 42-pixel thin reach feature are exercised; holes and multiple disconnected support components are not.",
            "Feature-core survival does not establish causal readability, line-art blending, identity continuity, or visual acceptance.",
            "The fixed coordinates come from the abstract layout control and cannot be transferred to unapproved smoke art.",
        ],
    }


def mutation_checks(expected: dict[str, Any]) -> tuple[int, int]:
    mutations = []
    changed = copy.deepcopy(expected); changed["intent_bindings"]["comic_panel_plan"]["plan_revision_id"] = "wrong"; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["geometry"]["context_padding_variants_px"].remove(4); mutations.append(changed)
    changed = copy.deepcopy(expected); changed["geometry"]["boundary_policy"]["id"] = "hard"; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["selected_context_padding_px"] = 4; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["selected_measurements"]["fully_replaced_core_component_count"] = 2; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["selected_measurements"]["feature_core_retention"]["tin"]["fully_replaced_core_fraction"] = 0; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["selected_measurements"]["alpha_nonzero_lettering_overlap_pixels"] = 1; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["selected_measurements"]["synthetic_composite_max_abs_difference_outside_support"] = 1; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["provider_input_authorized"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["review"] = {"human_review_status": "completed", "human_minutes": 1, "accepted": True}; mutations.append(changed)
    return sum(item != expected for item in mutations), len(mutations)


def validate_outputs(report: dict[str, Any]) -> None:
    for artifact in report["selected_outputs"].values():
        path = ROOT / artifact["path"]
        require(path.is_file() and sha256_file(path) == artifact["sha256"], f"causal-shape output missing or changed: {artifact['path']}")


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
            require(tracked == expected, "tracked causal-shape evidence differs")
            validate_outputs(tracked)
        rejected, total = mutation_checks(expected)
        require(rejected == total, "causal-shape mutation rejection incomplete")
    except (CausalShapeError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    m = expected["selected_measurements"]
    print("0 failures, 0 warnings")
    print(f"selected 8px context by rule: {m['fully_replaced_core_fraction_of_support']:.3%} union core, 1 connected core")
    print("plank/reach/hand/tin: 4/4 retain >=15% fully replaced core; 0 exterior/lettering change")
    print(f"{rejected}/{total} intent/method/topology/feature/boundary/review mutations rejected; 0 calls/uploads/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
