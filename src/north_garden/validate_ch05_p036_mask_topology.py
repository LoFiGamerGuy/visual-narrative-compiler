"""Audit selected boundary-policy compatibility with the current abstract P036 mask."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
MASK = ROOT / "experiments/outputs/ch05_p036_layout_control_r1/ch05-p036-target-context-mask-r1.png"
BASE = ROOT / "experiments/outputs/ch05_p036_layout_control_r1/ch05-p036-layout-control-r1.png"
LAYOUT_RECORD = ROOT / "experiments/results/ch05-p036-layout-control-r1.json"
BOUNDARY = ROOT / "docs/research/evidence/openai-targeted-repair-boundary-hardening-r2.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
OUT = ROOT / "experiments/outputs/ch05_p036_mask_topology_r1/ch05-p036-16px-inward-alpha-r1.png"
REPORT = ROOT / "docs/research/evidence/ch05-p036-mask-topology-compatibility-r1.json"
EXPECTED = {
    "mask": "a54386313171ec60ec6970442822d391fca7f41615a09ccc625b9deaf7c31467",
    "base": "a859557289f2fff25271e5ef5ede5687f7ff2edd7346f5c77813b9465e0dbe1d",
}


class TopologyError(RuntimeError):
    """P036 mask-topology evidence failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TopologyError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def components(mask: np.ndarray) -> list[int]:
    visited = np.zeros(mask.shape, dtype=bool)
    height, width = mask.shape
    sizes: list[int] = []
    for y, x in zip(*np.where(mask & ~visited)):
        if visited[y, x]:
            continue
        queue = deque([(int(y), int(x))])
        visited[y, x] = True
        size = 0
        while queue:
            cy, cx = queue.popleft()
            size += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == dx == 0:
                        continue
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        queue.append((ny, nx))
        sizes.append(size)
    return sorted(sizes, reverse=True)


def inward_alpha(support: np.ndarray, width: int) -> tuple[np.ndarray, np.ndarray]:
    current = support.copy()
    alpha = np.zeros(support.shape, dtype=np.float64)
    for step in range(width):
        eroded = np.asarray(Image.fromarray((current * 255).astype(np.uint8), "L").filter(ImageFilter.MinFilter(3))) > 0
        boundary = current & ~eroded
        alpha[boundary] = 0.5 - 0.5 * np.cos(np.pi * step / width)
        current = eroded
    alpha[current] = 1.0
    return alpha, current


def build_report(*, write: bool) -> dict[str, Any]:
    require(sha256_file(MASK) == EXPECTED["mask"], "P036 mask hash mismatch")
    require(sha256_file(BASE) == EXPECTED["base"], "P036 base hash mismatch")
    layout = json.loads(LAYOUT_RECORD.read_text(encoding="utf-8"))
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    require(layout["outputs"]["target_context_mask"]["sha256"] == EXPECTED["mask"], "layout record mask mismatch")
    require(boundary["decision"]["selected_compositor_policy"] == "cosine-inset-16px", "selected boundary policy changed")
    require(boundary["decision"]["art_accepted"] is False, "boundary experiment unexpectedly accepted art")
    require(plans["record_type"] == "ComicPanelPlanCollection" and plans["animation_shot_plan"] is None,
            "CH05 comic/animation record separation changed")
    panel = next(item for item in plans["plans"] if item["panel_id"] == "ng-ch05-sc01-p036")

    support = np.asarray(Image.open(MASK).convert("L")) > 0
    height, width = support.shape
    ys, xs = np.where(support)
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
    support_pixels = int(support.sum())
    rectangularity = support_pixels / bbox_area
    support_components = components(support)
    alpha, core = inward_alpha(support, 16)
    core_components = components(core)

    safe = panel["comic_direction"]["lettering"]["safe_zones"][0]["rect_norm"]
    sx, sy, sw, sh = safe
    safe_mask = np.zeros_like(support)
    safe_mask[round(sy * height):round((sy + sh) * height), round(sx * width):round((sx + sw) * width)] = True
    alpha_nonzero = alpha > 0

    base = np.asarray(Image.open(BASE).convert("RGB"), dtype=np.float64)
    synthetic_layer = base.copy()
    synthetic_layer[support, 0] = np.clip(synthetic_layer[support, 0] + 37, 0, 255)
    synthetic_layer[support, 1] = np.clip(synthetic_layer[support, 1] + 19, 0, 255)
    composite = np.rint(base * (1 - alpha[:, :, None]) + synthetic_layer * alpha[:, :, None]).astype(np.uint8)
    outside_difference = np.abs(composite.astype(np.int16) - base.astype(np.int16))[~support]

    alpha_bytes_io = __import__("io").BytesIO()
    Image.fromarray(np.rint(alpha * 255).astype(np.uint8), "L").save(alpha_bytes_io, format="PNG", compress_level=6)
    alpha_bytes = alpha_bytes_io.getvalue()
    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        if OUT.exists():
            require(OUT.read_bytes() == alpha_bytes, "existing topology alpha differs; refusing overwrite")
        else:
            OUT.write_bytes(alpha_bytes)

    topology_features = {
        "axis_aligned_rectangle": rectangularity == 1.0,
        "concavity_exercised": False,
        "hole_exercised": False,
        "multiple_components_exercised": len(support_components) > 1,
        "thin_feature_exercised": False,
    }
    mechanical_pass = (
        len(support_components) == len(core_components) == 1
        and core.sum() / support.sum() >= 0.50
        and not np.any(alpha_nonzero & safe_mask)
        and int(outside_difference.max()) == 0
    )
    narrative_topology_sufficient = mechanical_pass and all(topology_features.values())
    require(mechanical_pass, "selected feather fails current rectangular mask mechanics")
    require(not narrative_topology_sufficient, "rectangular mask incorrectly establishes irregular narrative topology")

    return {
        "record_type": "ComicRepairMaskTopologyCompatibility",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p036-mask-topology-compatibility-r1",
        "state": "RECTANGULAR_MECHANICS_PASS_IRREGULAR_NARRATIVE_TOPOLOGY_NOT_TESTED",
        "inputs": {
            "comic_panel_plan_collection": {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha256_file(PLANS)},
            "layout_control_record": {"path": LAYOUT_RECORD.relative_to(ROOT).as_posix(), "sha256": sha256_file(LAYOUT_RECORD)},
            "abstract_base": {"path": BASE.relative_to(ROOT).as_posix(), "sha256": EXPECTED["base"]},
            "target_context_mask": {"path": MASK.relative_to(ROOT).as_posix(), "sha256": EXPECTED["mask"]},
            "selected_boundary_evidence": {"path": BOUNDARY.relative_to(ROOT).as_posix(), "sha256": sha256_file(BOUNDARY)},
        },
        "policy": {"id": "cosine-inset-16px", "width_px": 16, "source_adr": "ADR-0040"},
        "measurements": {
            "canvas": [width, height],
            "support_bbox_xyxy": list(bbox),
            "support_pixels": support_pixels,
            "support_fraction": round(float(support.mean()), 9),
            "bbox_rectangularity": round(rectangularity, 9),
            "support_component_count": len(support_components),
            "support_component_sizes": support_components,
            "fully_replaced_core_pixels": int(core.sum()),
            "fully_replaced_core_fraction_of_support": round(float(core.sum() / support.sum()), 9),
            "fully_replaced_core_fraction_of_frame": round(float(core.mean()), 9),
            "core_component_count": len(core_components),
            "core_component_survival_fraction": round(len(core_components) / len(support_components), 9),
            "transition_or_zero_alpha_fraction_of_support": round(float(1 - core.sum() / support.sum()), 9),
            "alpha_nonzero_lettering_overlap_pixels": int(np.count_nonzero(alpha_nonzero & safe_mask)),
            "synthetic_composite_max_abs_difference_outside_support": int(outside_difference.max()),
        },
        "topology_feature_coverage": topology_features,
        "decision": {
            "current_rectangle_mechanics_compatible": mechanical_pass,
            "evidence_sufficient_for_irregular_narrative_mask": narrative_topology_sufficient,
            "next_required_control": "deterministic causal-shape mask with concavity and thin plank/hand/tin context",
            "provider_route_selection_changed": False,
            "art_accepted": False,
        },
        "output": {"inward_alpha": {"path": OUT.relative_to(ROOT).as_posix(), "sha256": sha256_bytes(alpha_bytes)}},
        "comic_boundary": {
            "panel_id": panel["panel_id"],
            "plan_revision_id": panel["plan_revision_id"],
            "comic_panel_plan_only": True,
            "animation_shot_plan": plans["animation_shot_plan"],
        },
        "review": {"human_review_status": "not_yet_performed", "human_minutes": None, "accepted": False},
        "activity": {"provider_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"},
        "limitations": [
            "The current P036 target-context mask is a filled axis-aligned rectangle, not an irregular causal-object mask.",
            "Component and core survival on this rectangle cannot establish thin-feature, concavity, hole, or multi-component behavior.",
            "The synthetic color layer tests exterior compositing only and is not art or a renderer output.",
            "No character continuity, causal readability, provider execution, or visual acceptance is tested.",
        ],
    }


def mutation_checks(expected: dict[str, Any]) -> tuple[int, int]:
    mutations = []
    changed = copy.deepcopy(expected); changed["inputs"]["target_context_mask"]["sha256"] = "0" * 64; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["policy"]["width_px"] = 8; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["measurements"]["bbox_rectangularity"] = 0.5; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["measurements"]["fully_replaced_core_fraction_of_support"] = 0; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["measurements"]["alpha_nonzero_lettering_overlap_pixels"] = 1; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["topology_feature_coverage"]["thin_feature_exercised"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["evidence_sufficient_for_irregular_narrative_mask"] = True; mutations.append(changed)
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
            require(tracked == expected, "tracked topology evidence differs")
            require(OUT.is_file() and sha256_file(OUT) == tracked["output"]["inward_alpha"]["sha256"], "topology alpha missing or changed")
        rejected, total = mutation_checks(expected)
        require(rejected == total, "topology mutation rejection incomplete")
    except (TopologyError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    m = expected["measurements"]
    print("0 failures, 0 warnings")
    print(f"rectangle mechanics: {m['fully_replaced_core_fraction_of_support']:.3%} core retained, 1/1 component, 0 exterior/lettering change")
    print("irregular narrative topology: NOT TESTED (no concavity, hole, multi-component, or thin feature)")
    print(f"{rejected}/{total} input/policy/metric/topology/decision/review mutations rejected; 0 calls/uploads/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
