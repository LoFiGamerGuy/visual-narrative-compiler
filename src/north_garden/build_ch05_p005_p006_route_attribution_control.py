"""Build the existing-pixel P005→P006 three-arm route-attribution control."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from compile_ch05_sequence_cadence_boundary_audit import pair_metrics, panel_metrics
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
BOUNDARY_AUDIT = ROOT / "docs/research/evidence/ch05-sequence-cadence-boundary-audit-r1.json"
SELECTED = ROOT / "production/comic/run-manifests/ch05-sequence-cadence-review-assembly-r1.json"
TEXT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-assembly-r1.json"
R6 = ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r6.json"
OUTDIR = ROOT / "experiments/review-packets/ch05-p005-p006-route-attribution-control-r1"
SHEET = OUTDIR / "ch05-p005-p006-three-arm-matched-review-sheet-r1.png"
EVIDENCE = ROOT / "docs/research/evidence/ch05-p005-p006-route-attribution-control-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def manifest_entries(path: Path) -> dict[int, dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    entries = {row["order"]: row for row in document["entries"]}
    if {5, 6} - set(entries):
        raise ValueError(f"manifest lacks P005/P006: {path}")
    return entries


def load_entry(entry: dict[str, Any], expected_route: str | None = None) -> tuple[Path, Image.Image]:
    if entry["panel_id"] != f"ng-ch05-sc01-p{entry['order']:03d}":
        raise ValueError(f"canonical panel mismatch: {entry['panel_id']}")
    if expected_route is not None and entry.get("selection", {}).get("route") != expected_route:
        raise ValueError(f"selected route mismatch: {entry['panel_id']}")
    path = ROOT / entry["source"]["path"]
    if not path.is_file() or sha256(path) != entry["source"]["sha256"]:
        raise ValueError(f"source hash mismatch: {entry['candidate_id']}")
    with Image.open(path) as opened:
        image = opened.convert("RGB")
    if [image.width, image.height] != [entry["source"]["width"], entry["source"]["height"]]:
        raise ValueError(f"source dimensions mismatch: {entry['candidate_id']}")
    return path, image


def build_sheet(arms: list[dict[str, Any]], images: dict[str, Image.Image], path: Path) -> None:
    width, header, row_height, margin, gap = 1440, 130, 390, 34, 28
    canvas = Image.new("RGB", (width, header + len(arms) * row_height + margin), "#e9e5dc")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 22), "CH05 P005 TO P006 ROUTE-ATTRIBUTION CONTROL", fill="#17212a", font=font(30, True))
    draw.text((margin, 65), "Existing pixels only · identical review cells · derivative layout · no candidate grading", fill="#45515b", font=font(18))
    draw.text((margin, 94), "Each row crosses the same two story beats; only route assignment changes.", fill="#45515b", font=font(16))
    cell_width, cell_height = 590, 270
    x_positions = (margin, margin + cell_width + gap)
    for index, arm in enumerate(arms):
        top = header + index * row_height
        draw.rounded_rectangle((margin, top, width - margin, top + row_height - 14), radius=10, fill="#f9f7f1", outline="#9ba4aa", width=2)
        draw.text((margin + 16, top + 12), f"{index + 1}. {arm['label']}", fill="#17212a", font=font(20, True))
        for side, key in enumerate((arm["left_candidate_key"], arm["right_candidate_key"])):
            x = x_positions[side]
            y = top + 54
            draw.rectangle((x, y, x + cell_width, y + cell_height), fill="#d8d5ce", outline="#7d878e", width=1)
            image = ImageOps.contain(images[key], (cell_width - 16, cell_height - 16), Image.Resampling.LANCZOS)
            canvas.paste(image, (x + (cell_width - image.width) // 2, y + (cell_height - image.height) // 2))
            draw.text((x + 8, y + cell_height + 8), arm["display_labels"][side], fill="#26313a", font=font(15, True))
        metrics = arm["metrics"]
        metric_text = f"Luma TV {metrics['luminance_histogram_total_variation']:.6f}   RGB-64 mean TV {metrics['rgb_64_bin_histogram_mean_channel_total_variation']:.6f}"
        draw.text((margin + 16, top + 350), metric_text, fill="#45515b", font=font(14))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", compress_level=6, optimize=False)


def build_document() -> dict[str, Any]:
    selected_entries = manifest_entries(SELECTED)
    text_entries = manifest_entries(TEXT)
    r6_entries = manifest_entries(R6)
    selected_bindings = {
        5: load_entry(selected_entries[5], "reduced_palette_text_control"),
        6: load_entry(selected_entries[6], "r6"),
    }
    source_entries = {
        "text_p005": text_entries[5],
        "text_p006": text_entries[6],
        "r6_p005": r6_entries[5],
        "r6_p006": r6_entries[6],
    }
    source_manifests = {"text_p005": TEXT, "text_p006": TEXT, "r6_p005": R6, "r6_p006": R6}
    routes = {"text_p005": "reduced_palette_text_control", "text_p006": "reduced_palette_text_control", "r6_p005": "r6", "r6_p006": "r6"}
    images: dict[str, Image.Image] = {}
    candidates: list[dict[str, Any]] = []
    for key, entry in source_entries.items():
        path, image = load_entry(entry)
        images[key] = image
        candidates.append(
            {
                "candidate_key": key,
                "order": entry["order"],
                "panel_id": entry["panel_id"],
                "candidate_id": entry["candidate_id"],
                "sequence_id": entry["sequence_id"],
                "route": routes[key],
                "source_manifest": {"path": source_manifests[key].relative_to(ROOT).as_posix(), "sha256": sha256(source_manifests[key])},
                "source": {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "width": image.width, "height": image.height, "png_bytes": path.stat().st_size},
                "complexity_proxies": panel_metrics(image, path.stat().st_size),
                "planning_structure": "ComicPanelPlan",
                "animation_shot_plan": None,
                "e_conte": None,
                "owner_acceptance": None,
                "rights_clearance": None,
                "commercially_cleared": None,
                "exact_production_base": None,
            }
        )
    if sha256(selected_bindings[5][0]) != sha256(ROOT / source_entries["text_p005"]["source"]["path"]):
        raise ValueError("selected P005 does not bind the exact text-control P005 candidate")
    if sha256(selected_bindings[6][0]) != sha256(ROOT / source_entries["r6_p006"]["source"]["path"]):
        raise ValueError("selected P006 does not bind the exact R6 P006 candidate")

    arm_specs = (
        ("selected_cross_route", "Selected cadence: text P005 TO R6 P006", "text_p005", "r6_p006"),
        ("all_text_control", "Same-route control: text P005 TO text P006", "text_p005", "text_p006"),
        ("all_r6_control", "Same-route control: R6 P005 TO R6 P006", "r6_p005", "r6_p006"),
    )
    arms: list[dict[str, Any]] = []
    by_candidate = {row["candidate_key"]: row for row in candidates}
    for arm_id, label, left, right in arm_specs:
        arms.append(
            {
                "arm_id": arm_id,
                "label": label,
                "left_candidate_key": left,
                "right_candidate_key": right,
                "display_labels": [f"P005 · {by_candidate[left]['route']}", f"P006 · {by_candidate[right]['route']}"],
                "metrics": pair_metrics(images[left], images[right]),
                "review_state": "PENDING_OWNER_REVIEW_NOT_GRADED",
                "owner_acceptance": None,
                "rights_clearance": None,
                "commercially_cleared": None,
                "exact_production_base": None,
            }
        )
    by_arm = {row["arm_id"]: row for row in arms}
    selected_metrics = by_arm["selected_cross_route"]["metrics"]
    text_metrics = by_arm["all_text_control"]["metrics"]
    r6_metrics = by_arm["all_r6_control"]["metrics"]
    comparisons: dict[str, Any] = {}
    exceeds_both = 0
    for metric in selected_metrics:
        selected_value = selected_metrics[metric]
        control_mean = (text_metrics[metric] + r6_metrics[metric]) / 2
        is_above_both = selected_value > max(text_metrics[metric], r6_metrics[metric])
        exceeds_both += int(is_above_both)
        comparisons[metric] = {
            "selected_cross_route": selected_value,
            "all_text_control": text_metrics[metric],
            "all_r6_control": r6_metrics[metric],
            "same_route_control_mean": round(control_mean, 6),
            "selected_minus_control_mean": round(selected_value - control_mean, 6),
            "selected_to_control_mean_ratio": round(selected_value / control_mean, 6) if control_mean else None,
            "selected_exceeds_both_same_route_controls": is_above_both,
        }
    attribution_result = "ROUTE_SWITCH_CONTRIBUTION_SUPPORTED_ON_BOTH_HISTOGRAM_PROXIES" if exceeds_both == len(selected_metrics) else "ROUTE_SWITCH_CONTRIBUTION_NOT_ISOLATED_ON_BOTH_HISTOGRAM_PROXIES"

    build_sheet(arms, images, SHEET)
    with Image.open(SHEET) as opened:
        sheet_dimensions = [opened.width, opened.height]
    unique_pixels = [ROOT / row["source"]["path"] for row in candidates]
    inputs = [BOUNDARY_AUDIT, SELECTED, TEXT, R6, *unique_pixels]
    return {
        "record_type": "CH05P005P006RouteAttributionControl",
        "schema_version": "1.0",
        "record_id": "ng-ch05-p005-p006-route-attribution-control-r1",
        "state": "EXISTING_PIXEL_ATTRIBUTION_CONTROL_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in inputs],
        "coverage": {"canonical_panel_ids": ["ng-ch05-sc01-p005", "ng-ch05-sc01-p006"], "unique_existing_candidates": 4, "matched_transition_arms": 3, "new_art_candidates": 0, "provider_calls": 0, "uploads": 0},
        "method": {
            "control_design": "Compare the selected text→R6 transition with all-text and all-R6 transitions across the identical P005→P006 story-beat boundary.",
            "matched_presentation": "Every sheet image is aspect-preserving Lanczos-downsampled into the same 590x270 neutral review cell; source pixels remain unchanged.",
            "histogram_method": "Same deterministic 256x256 luminance-TV and mean RGB 64-bin channel-TV implementation as the parent boundary audit.",
            "complexity_method": "Same 390px-wide grayscale entropy, FIND_EDGES>=32 density, and native PNG-bytes-per-pixel implementation as the parent boundary audit.",
            "interpretation_boundary": "All measurements are content-, crop-, aspect-, codec-, and resize-sensitive proxies. They do not measure or grade artistic quality, narrative quality, identity, acceptance, or production fitness.",
        },
        "candidates": candidates,
        "arms": arms,
        "attribution": {
            "comparison": comparisons,
            "predeclared_rule": "A route-switch contribution is supported on a proxy only when the selected cross-route distance exceeds both same-route controls for that same P005→P006 beat transition.",
            "proxies_supporting_rule": exceeds_both,
            "proxies_evaluated": len(selected_metrics),
            "result": attribution_result,
            "confounds": [
                "P005 is a people-free runnel insert while P006 is a two-adult marker/action panel; the story content and shot scale change in every arm.",
                "Native aspect ratios and dimensions vary by route and panel; histogram normalization cannot remove composition/crop differences.",
                "The candidates were not generated as a randomized controlled experiment, so any route-switch attribution remains directional rather than causal.",
            ],
        },
        "artifact": {
            "path": SHEET.relative_to(ROOT).as_posix(),
            "sha256": sha256(SHEET),
            "width": sheet_dimensions[0],
            "height": sheet_dimensions[1],
            "bytes": SHEET.stat().st_size,
            "repository_state": "IGNORED_LOCAL_REVIEW_LAYOUT_DERIVATIVE",
            "contains_new_art": False,
        },
        "disposition": {
            "selected_or_ranked_candidate": None,
            "owner_acceptance": None,
            "rights_clearance": None,
            "commercially_cleared": None,
            "exact_production_base": None,
            "pixel_edits": None,
        },
        "spend": {"direct_paid_api_cloud_usd": 0.0, "built_in_product_monetary_cost_usd": None, "provider_calls": 0, "uploads": 0},
        "limitations": [
            "This is a review-layout derivative of existing exact-hash candidates, not new art or a candidate edit.",
            "No candidate is selected, accepted, ranked, graded, rights-cleared, or commercially cleared.",
            "Histogram and complexity proxies are not quality measures and do not establish causal attribution by themselves.",
        ],
        "boundary": "Review evidence only; no provider execution, upload, generation, candidate edit, acceptance, rights clearance, commercial clearance, canon replacement, or exact production-base decision.",
    }


def main() -> int:
    document = build_document()
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": EVIDENCE.relative_to(ROOT).as_posix(), "sha256": sha256(EVIDENCE), "artifact": document["artifact"], "attribution": document["attribution"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
