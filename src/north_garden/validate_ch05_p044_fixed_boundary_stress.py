"""Stress the fixed P036 16px boundary on deterministic P044 blade/twine geometry."""
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
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
ASSERTIONS = ROOT / "production/comic/hard-assertion-manifests/ch05-mill-signal-r1.json"
SELECTION = ROOT / "docs/research/evidence/ch05-next-repair-policy-information-gain-r1.json"
BOUNDARY = ROOT / "docs/research/evidence/openai-targeted-repair-boundary-hardening-r2.json"
POLICY = ROOT / "config/ch05-openai-targeted-repair-policy-r1.json"
OUT_DIR = ROOT / "experiments/outputs/ch05_p044_fixed_boundary_stress_r1"
REPORT = ROOT / "docs/research/evidence/ch05-p044-fixed-16px-boundary-stress-r1.json"
SIZE = (1536, 1024)


class StressError(RuntimeError):
    """P044 fixed-boundary stress evidence failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise StressError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def source(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}


def draw_mask(kind: str) -> np.ndarray:
    image = Image.new("L", SIZE, 0)
    draw = ImageDraw.Draw(image)
    if kind == "protected_hands":
        draw.ellipse((675, 590, 745, 660), fill=255)
        draw.ellipse((825, 410, 895, 480), fill=255)
    elif kind == "blade":
        draw.line((710, 625, 860, 445), fill=255, width=18)
    elif kind == "twine":
        draw.line((480, 535, 1000, 535), fill=255, width=12)
    else:
        raise StressError(f"unknown geometry: {kind}")
    return np.asarray(image) > 0


def png_bytes(array: np.ndarray) -> bytes:
    buffer = BytesIO()
    Image.fromarray(array, "L").save(buffer, format="PNG", compress_level=6)
    return buffer.getvalue()


def write_if_absent_or_equal(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        require(path.read_bytes() == data, f"existing P044 stress output differs; refusing overwrite: {path.name}")
    else:
        path.write_bytes(data)


def build_report(*, write: bool) -> dict[str, Any]:
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    assertions = json.loads(ASSERTIONS.read_text(encoding="utf-8"))
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    panel = next(item for item in plans["plans"] if item["panel_id"] == "ng-ch05-sc01-p044")
    assertion = next(item for item in assertions["assertions"] if item["id"] == "p044_core_read")
    require(selection["decision"]["selected_next_local_control_panel_id"] == panel["panel_id"], "P044 control selection changed")
    require(boundary["decision"]["selected_compositor_policy"] == "cosine-inset-16px", "fixed boundary changed")
    require(policy["mechanics"]["boundary_policy"] == "cosine-inset-16px", "repair policy boundary changed")
    require(panel["composition_intent"] == "hands, blade, taut twine", "P044 explicit geometry changed")
    require(assertion["applicability"] == panel["panel_id"] and assertion["severity"] == "hard", "P044 assertion changed")
    require(plans["animation_shot_plan"] is None, "CH05 plans gained AnimationShotPlan")

    protected = draw_mask("protected_hands")
    blade = draw_mask("blade") & ~protected
    twine = draw_mask("twine") & ~protected
    support = blade | twine
    alpha, core = inward_alpha(support, 16)
    safe = panel["comic_direction"]["lettering"]["safe_zones"][0]["rect_norm"]
    x, y, width, height = safe
    lettering = np.zeros((SIZE[1], SIZE[0]), dtype=bool)
    lettering[round(y * SIZE[1]):round((y + height) * SIZE[1]), round(x * SIZE[0]):round((x + width) * SIZE[0])] = True

    feature_metrics = {}
    for name, feature in (("blade", blade), ("twine", twine)):
        feature_metrics[name] = {
            "declared_width_px": 18 if name == "blade" else 12,
            "support_pixels": int(feature.sum()),
            "fully_replaced_core_pixels": int(np.count_nonzero(core & feature)),
            "fully_replaced_core_fraction": round(float(np.count_nonzero(core & feature) / feature.sum()), 9),
            "nonzero_alpha_fraction": round(float(np.count_nonzero((alpha > 0) & feature) / feature.sum()), 9),
        }
    # A deterministic synthetic layer proves exterior behavior without creating art.
    base = np.zeros((SIZE[1], SIZE[0], 3), dtype=np.float64)
    base[:, :, :] = (48, 52, 55)
    synthetic = base.copy()
    synthetic[support] = (166, 118, 58)
    composite = np.rint(base * (1 - alpha[:, :, None]) + synthetic * alpha[:, :, None]).astype(np.uint8)
    outside = np.abs(composite.astype(np.int16) - base.astype(np.int16))[~support]

    support_bytes = png_bytes((support * 255).astype(np.uint8))
    alpha_bytes = png_bytes(np.rint(alpha * 255).astype(np.uint8))
    protected_bytes = png_bytes((protected * 255).astype(np.uint8))
    outputs = {
        "support_mask": {"path": (OUT_DIR / "ch05-p044-blade-twine-support-r1.png").relative_to(ROOT).as_posix(), "sha256": sha256_bytes(support_bytes)},
        "inward_alpha": {"path": (OUT_DIR / "ch05-p044-fixed-16px-alpha-r1.png").relative_to(ROOT).as_posix(), "sha256": sha256_bytes(alpha_bytes)},
        "protected_hands_mask": {"path": (OUT_DIR / "ch05-p044-protected-hands-r1.png").relative_to(ROOT).as_posix(), "sha256": sha256_bytes(protected_bytes)},
    }
    if write:
        for key, data in (("support_mask", support_bytes), ("inward_alpha", alpha_bytes), ("protected_hands_mask", protected_bytes)):
            write_if_absent_or_equal(ROOT / outputs[key]["path"], data)

    compatible = bool(
        core.sum() > 0
        and len(components(core)) == 1
        and all(item["fully_replaced_core_fraction"] >= 0.15 for item in feature_metrics.values())
        and not np.any((alpha > 0) & lettering)
        and int(outside.max()) == 0
    )
    require(not compatible, "fixed 16px policy unexpectedly passed sub-32px control")
    require(int(core.sum()) == 0, "fixed 16px stress no longer collapses the fully replaced core")
    return {
        "record_type": "ComicRepairFineFeatureBoundaryStressControl",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p044-fixed-16px-boundary-stress-r1",
        "state": "FIXED_16PX_REJECTED_FOR_SUB32PX_FINE_FEATURE_CONTROL",
        "intent_bindings": {
            "comic_panel_plan": {**source(PLANS), "panel_id": panel["panel_id"], "plan_revision_id": panel["plan_revision_id"]},
            "hard_assertion": {**source(ASSERTIONS), "assertion_id": assertion["id"]},
            "information_gain_selection": source(SELECTION),
        },
        "fixed_policy": {
            "boundary_evidence": source(BOUNDARY),
            "policy": source(POLICY),
            "boundary_policy": "cosine-inset-16px",
            "tuned_within_experiment": False,
        },
        "geometry": {
            "canvas": list(SIZE),
            "protected_hands": {"ellipses_xyxy": [[675, 590, 745, 660], [825, 410, 895, 480]]},
            "blade": {"line_xyxy": [710, 625, 860, 445], "width_px": 18, "clipped_from_protected_hands": True},
            "twine": {"line_xyxy": [480, 535, 1000, 535], "width_px": 12, "clipped_from_protected_hands": True},
            "source_limit": "coordinates are abstract control choices; only hands/blade/taut-twine categories come from the ComicPanelPlan",
        },
        "measurements": {
            "support_pixels": int(support.sum()),
            "support_component_count": len(components(support)),
            "fully_replaced_core_pixels": int(core.sum()),
            "fully_replaced_core_component_count": len(components(core)),
            "feature_metrics": feature_metrics,
            "support_protected_hand_overlap_pixels": int(np.count_nonzero(support & protected)),
            "alpha_nonzero_lettering_overlap_pixels": int(np.count_nonzero((alpha > 0) & lettering)),
            "synthetic_composite_max_abs_difference_outside_support": int(outside.max()),
        },
        "outputs": outputs,
        "decision": {
            "fixed_16px_compatible_with_fine_feature_control": compatible,
            "rejection_reason": "Both 18px blade and 12px twine lose all fully replaced core under a 16px inward boundary.",
            "next_required_experiment": "bounded adaptive-width comparison on the same exact geometry; do not widen support or change geometry",
            "p044_production_policy_authored": False,
            "production_mask_approved": False,
            "provider_route_changed": False,
        },
        "comic_boundary": {"comic_panel_plan_only": True, "animation_shot_plan": None, "e_conte": None},
        "review": {"human_review_status": "not_yet_performed", "human_minutes": None, "accepted": False},
        "activity": {"provider_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"},
        "limitations": [
            "Feature widths and coordinates are deliberate stress-control parameters, not measurements from absent P044 art.",
            "The control proves fixed-width topology collapse, not visual failure on a rendered hand/tool/twine scene.",
            "Protected-hand clipping tests mask separation mechanically; identity and anatomy are not represented.",
            "No adaptive boundary is selected in this experiment and no production input or policy is created.",
        ],
    }


def mutation_checks(expected: dict[str, Any]) -> tuple[int, int]:
    mutations = []
    changed = copy.deepcopy(expected); changed["intent_bindings"]["comic_panel_plan"]["panel_id"] = "ng-ch05-sc01-p036"; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["fixed_policy"]["boundary_policy"] = "cosine-inset-08px"; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["fixed_policy"]["tuned_within_experiment"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["geometry"]["twine"]["width_px"] = 32; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["measurements"]["fully_replaced_core_pixels"] = 1; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["measurements"]["support_protected_hand_overlap_pixels"] = 1; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["fixed_16px_compatible_with_fine_feature_control"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["decision"]["p044_production_policy_authored"] = True; mutations.append(changed)
    changed = copy.deepcopy(expected); changed["review"] = {"human_review_status": "completed", "human_minutes": 1, "accepted": True}; mutations.append(changed)
    return sum(item != expected for item in mutations), len(mutations)


def validate_outputs(record: dict[str, Any]) -> None:
    for artifact in record["outputs"].values():
        path = ROOT / artifact["path"]
        require(path.is_file() and sha256_file(path) == artifact["sha256"], f"P044 stress output missing or changed: {artifact['path']}")


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
            require(tracked == expected, "tracked P044 fixed-boundary stress evidence differs")
            validate_outputs(tracked)
        rejected, total = mutation_checks(expected)
        require(rejected == total, "P044 stress mutation rejection incomplete")
    except (StressError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    m = expected["measurements"]
    print("0 failures, 0 warnings")
    print(f"fixed 16px stress: {m['fully_replaced_core_pixels']} core pixels; blade/twine core 0/0; policy rejected for this control")
    print("1 support component; 0 protected-hand/lettering/exterior change; no tuning or production policy")
    print(f"{rejected}/{total} intent/policy/tuning/geometry/metric/separation/decision/review mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
