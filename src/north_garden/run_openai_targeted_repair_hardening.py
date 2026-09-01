"""Local-only hardening of the selected G07 OpenAI mechanism.

Uses already-returned fictional proxy evidence. It performs no network call,
provider request, external upload, or CH05 render.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps

from openai_gpt_image2_bakeoff import ROOT, source_provenance


SOURCE = ROOT / "experiments/outputs/blender_kitchen_control_bundle_v2/g07a-role-id-r1.png"
NOCHANGE_SOURCE = ROOT / "experiments/outputs/blender_kitchen_control_bundle_v2/g07a-no-change-r1.png"
TARGET_PROVIDER = ROOT / "experiments/outputs/openai_gpt_image2_g07_bakeoff_r1/g07a-target-change.png"
TARGET_RECORD = ROOT / "experiments/records/openai_gpt_image2_g07_bakeoff_r1/g07a-target-change.json"
CH05_PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
OUT_DIR = ROOT / "experiments/outputs/openai_targeted_repair_hardening_r1"
RESULT = ROOT / "experiments/results/openai-targeted-repair-hardening-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def target_bbox(source: np.ndarray) -> tuple[int, int, int, int]:
    teal = (source[:, :, 1] > source[:, :, 0] + 15) & (source[:, :, 2] > source[:, :, 0] + 15)
    ys, xs = np.where(teal)
    if not len(xs):
        raise SystemExit("teal target proxy not detected")
    pad = 12
    return (
        max(0, int(xs.min()) - pad),
        max(0, int(ys.min()) - pad),
        min(source.shape[1], int(xs.max()) + 1 + pad),
        min(source.shape[0], int(ys.max()) + 1 + pad),
    )


def contact_sheet(paths: list[tuple[Path, str]], output: Path) -> None:
    cell = (620, 430)
    sheet = Image.new("RGB", (cell[0] * 2, cell[1] * 2), "#d9d9d9")
    for index, (path, label) in enumerate(paths):
        image = Image.open(path).convert("RGB")
        fitted = ImageOps.contain(image, (cell[0] - 20, cell[1] - 44), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", cell, "white")
        tile.paste(fitted, ((cell[0] - fitted.width) // 2, 34 + (cell[1] - 44 - fitted.height) // 2))
        ImageDraw.Draw(tile).text((10, 10), label, fill="black")
        sheet.paste(tile, ((index % 2) * cell[0], (index // 2) * cell[1]))
    sheet.save(output, quality=92, subsampling=0)


def main() -> None:
    target_record = json.loads(TARGET_RECORD.read_text(encoding="utf-8"))
    if target_record["candidate"]["sha256"] != sha256(TARGET_PROVIDER):
        raise SystemExit("selected provider candidate hash mismatch")
    source_image = Image.open(SOURCE).convert("RGB")
    source = np.asarray(source_image, dtype=np.int16)
    bbox = target_bbox(source)
    provider_resized = Image.open(TARGET_PROVIDER).convert("RGB").resize(source_image.size, Image.Resampling.LANCZOS)
    mask = Image.new("L", source_image.size, 0)
    ImageDraw.Draw(mask).rectangle(bbox, fill=255)
    composite = Image.composite(provider_resized, source_image, mask)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    composite_path = OUT_DIR / "g07a-target-change-masked-composite-r1.png"
    mask_path = OUT_DIR / "g07a-target-mask-r1.png"
    nochange_path = OUT_DIR / "g07a-no-change-short-circuit-r1.png"
    sheet_path = OUT_DIR / "g07a-hardening-contact-sheet-r1.jpg"
    composite.save(composite_path)
    mask.save(mask_path)
    shutil.copyfile(NOCHANGE_SOURCE, nochange_path)
    contact_sheet([
        (SOURCE, "source control"),
        (TARGET_PROVIDER, "selected provider target output"),
        (composite_path, "deterministic target-mask composite"),
        (nochange_path, "no-change short circuit"),
    ], sheet_path)

    output = np.asarray(composite, dtype=np.int16)
    mask_bool = np.asarray(mask) > 0
    changed = np.any(output != source, axis=2)
    inside = output[mask_bool]
    green_dominant = (inside[:, 1] > inside[:, 0] + 10) & (inside[:, 1] > inside[:, 2] + 5)

    plans = json.loads(CH05_PLANS.read_text(encoding="utf-8"))
    panel = next(item for item in plans["plans"] if item["panel_id"] == "ng-ch05-sc01-p036")
    record = {
        "record_type": "RendererHardeningExperiment",
        "schema_version": "1.0",
        "record_id": "ng-openai-targeted-repair-hardening-r1",
        "state": "COMPLETED_LOCAL_PROXY_HARDENING_CH05_EXECUTION_NOT_AUTHORIZED",
        "created_at": stamp(),
        "selection_adr": "docs/adr/ADR-0025-select-openai-gpt-image-2-for-bounded-targeted-repair-hardening.md",
        "selected_mechanism": "gpt-image-2-2026-04-21",
        "inputs": {
            "source": {"path": SOURCE.relative_to(ROOT).as_posix(), "sha256": sha256(SOURCE)},
            "nochange_source": {"path": NOCHANGE_SOURCE.relative_to(ROOT).as_posix(), "sha256": sha256(NOCHANGE_SOURCE)},
            "provider_target_candidate": {"path": TARGET_PROVIDER.relative_to(ROOT).as_posix(), "sha256": sha256(TARGET_PROVIDER)},
            "provider_render_record": {"path": TARGET_RECORD.relative_to(ROOT).as_posix(), "sha256": sha256(TARGET_RECORD)},
        },
        "method": {
            "target_mask": "deterministic rectangle from the teal proxy's color-segmented bounding box plus 12 source pixels",
            "target_bbox_xyxy": list(bbox),
            "target_provider_resize": "Lanczos to source raster dimensions",
            "nochange": "byte-copy short circuit; no renderer invocation",
            "source_provenance": source_provenance(Path(__file__).resolve()),
        },
        "outputs": {
            "target_mask": {"path": mask_path.relative_to(ROOT).as_posix(), "sha256": sha256(mask_path)},
            "target_composite": {"path": composite_path.relative_to(ROOT).as_posix(), "sha256": sha256(composite_path)},
            "nochange_short_circuit": {"path": nochange_path.relative_to(ROOT).as_posix(), "sha256": sha256(nochange_path)},
            "contact_sheet": {"path": sheet_path.relative_to(ROOT).as_posix(), "sha256": sha256(sheet_path)},
        },
        "measurements": {
            "target_mask_fraction": round(float(mask_bool.mean()), 9),
            "target_changed_inside_mask_fraction": round(float(changed[mask_bool].mean()), 9),
            "target_changed_outside_mask_fraction": round(float(changed[~mask_bool].mean()), 9),
            "target_green_dominant_inside_mask_fraction": round(float(green_dominant.mean()), 9),
            "nochange_byte_identical": sha256(NOCHANGE_SOURCE) == sha256(nochange_path),
            "additional_provider_requests": 0,
            "additional_external_cost_usd": "0.000000",
        },
        "narrative_panel_applicability": {
            "comic_panel_plan_collection": {"path": CH05_PLANS.relative_to(ROOT).as_posix(), "sha256": sha256(CH05_PLANS), "record_type": plans["record_type"]},
            "panel_id": panel["panel_id"],
            "plan_revision_id": panel["plan_revision_id"],
            "visible_adult_cast": panel["visible_adult_cast"],
            "motion_mode": panel["comic_direction"]["motion_mode"],
            "lettering_safe_zones": panel["comic_direction"]["lettering"]["safe_zones"],
            "animation_shot_plan": plans["animation_shot_plan"],
            "execution_state": "NOT_RENDERED_EXTERNAL_UPLOAD_BEYOND_APPROVED_BAKEOFF_NOT_AUTHORIZED",
            "missing_high_information_input": "panel-specific approved base raster and target mask tied to the causal hand/plank relationship",
        },
        "review": {"human_review_status": "not_yet_performed", "human_minutes": None, "accepted": False},
        "limitations": [
            "A rectangular proxy mask proves exterior preservation mechanics, not boundary quality on characters, hands, hair, props, or lettering.",
            "The selected provider output is unaccepted research evidence.",
            "No recurring-character continuity or CH05 narrative art is tested.",
            "No external upload, provider call, AnimationShotPlan, or E-Conte record is created."
        ],
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(RESULT)


if __name__ == "__main__":
    main()
