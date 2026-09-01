"""Build deterministic G07 provider review instrumentation and contact sheets.

Pixel comparisons diagnose global drift only. They do not infer subject count,
role binding, semantic edit success, production acceptance, or human review.
"""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "experiments/renderer-bakeoffs/g07-fictional-bakeoff-r1.json"
OUT = ROOT / "experiments/results/g07-provider-bakeoff-instrumentation-r1.json"
REVIEW_DIR = ROOT / "experiments/reviews/renderer-bakeoff-g07-fictional-r1"
RECORD_DIRS = {
    "openai_gpt_image_2": ROOT / "experiments/records/openai_gpt_image2_g07_bakeoff_r1",
    "gemini_3_1_flash_image": ROOT / "experiments/records/gemini_flash_image_g07_bakeoff_r1",
    "grok_imagine_image_2": ROOT / "experiments/records/xai_grok_imagine_g07_bakeoff_r1",
    "bfl_flux_2": ROOT / "experiments/records/bfl_flux2_g07_bakeoff_r1",
}
ORDER = ["g07a-independent-01", "g07a-independent-02", "g07a-target-change", "g07a-no-change"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def pixels(path: Path, size: tuple[int, int] | None = None) -> np.ndarray:
    image = Image.open(path).convert("RGB")
    if size and image.size != size:
        image = image.resize(size, Image.Resampling.LANCZOS)
    return np.asarray(image, dtype=np.int16)


def compare(reference: Path, candidate: Path) -> dict:
    candidate_image = Image.open(candidate).convert("RGB")
    a = pixels(reference, candidate_image.size)
    b = np.asarray(candidate_image, dtype=np.int16)
    delta = np.abs(a - b)
    changed = np.any(delta > 8, axis=2)
    return {
        "reference_path": reference.relative_to(ROOT).as_posix(),
        "reference_sha256": sha256(reference),
        "candidate_path": candidate.relative_to(ROOT).as_posix(),
        "candidate_sha256": sha256(candidate),
        "comparison_size": list(candidate_image.size),
        "changed_pixel_fraction_threshold_gt_8": round(float(changed.mean()), 9),
        "mean_absolute_channel_difference_0_255": round(float(delta.mean()), 6),
        "root_mean_square_channel_difference_0_255": round(float(np.sqrt(np.mean(delta.astype(np.float64) ** 2))), 6),
        "limitation": "Reference is resized to candidate dimensions; metric measures full-frame raster drift, not semantic correctness.",
    }


def tile(path: Path, label: str, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    fitted = ImageOps.contain(image, (size[0] - 20, size[1] - 44), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, "white")
    canvas.paste(fitted, ((size[0] - fitted.width) // 2, 34 + (size[1] - 44 - fitted.height) // 2))
    ImageDraw.Draw(canvas).text((10, 10), label, fill="black")
    return canvas


def contact_sheet(adapter_id: str, source: Path, nochange_source: Path, candidates: dict[str, Path]) -> Path:
    cell = (620, 430)
    items = [
        (source, "SOURCE: G07a control"),
        (candidates["g07a-independent-01"], "independent-01"),
        (candidates["g07a-independent-02"], "independent-02"),
        (nochange_source, "SOURCE: no-change reference"),
        (candidates["g07a-target-change"], "target-change"),
        (candidates["g07a-no-change"], "no-change"),
    ]
    sheet = Image.new("RGB", (cell[0] * 3, cell[1] * 2), "#d9d9d9")
    for index, (path, label) in enumerate(items):
        sheet.paste(tile(path, f"{adapter_id} | {label}", cell), ((index % 3) * cell[0], (index // 3) * cell[1]))
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    path = REVIEW_DIR / f"{adapter_id}-contact-sheet-r1.jpg"
    sheet.save(path, quality=92, subsampling=0)
    return path


def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    source = ROOT / plan["source_assets"]["g07a-control"]["path"]
    nochange_source = ROOT / plan["source_assets"]["g07a-nochange-reference"]["path"]
    result = {
        "record_type": "RendererBakeoffInstrumentation",
        "schema_version": "1.0",
        "record_id": "ng-g07-provider-bakeoff-instrumentation-r1",
        "state": "COMPLETE_DIAGNOSTICS_PENDING_AUTHORIZED_HUMAN_REVIEW",
        "created_at": stamp(),
        "plan": {"path": PLAN.relative_to(ROOT).as_posix(), "sha256": sha256(PLAN)},
        "adapters": {},
        "acceptance_boundary": "Diagnostics do not accept candidates. Role/count/blocking and target-edit assertions still require review under the linked manifest; human minutes remain null.",
    }
    for adapter_id, record_dir in RECORD_DIRS.items():
        records = {}
        candidates = {}
        for request_id in ORDER:
            record_path = record_dir / f"{request_id}.json"
            record = json.loads(record_path.read_text(encoding="utf-8"))
            candidate = ROOT / record["candidate"]["path"]
            if sha256(candidate) != record["candidate"]["sha256"]:
                raise SystemExit(f"candidate hash mismatch: {candidate}")
            records[request_id] = {
                "record_path": record_path.relative_to(ROOT).as_posix(),
                "record_sha256": sha256(record_path),
                "candidate_path": candidate.relative_to(ROOT).as_posix(),
                "candidate_sha256": sha256(candidate),
                "elapsed_seconds": record["elapsed_seconds"],
                "cost_usd": record["cost_usd"],
                "human_review_status": record["human_review_status"],
                "human_minutes": record["human_minutes"],
                "accepted": record["accepted"],
            }
            candidates[request_id] = candidate
        sheet = contact_sheet(adapter_id, source, nochange_source, candidates)
        result["adapters"][adapter_id] = {
            "records": records,
            "summary": {
                "required_candidates": 4,
                "total_elapsed_seconds": round(sum(item["elapsed_seconds"] for item in records.values()), 3),
                "mean_elapsed_seconds": round(sum(item["elapsed_seconds"] for item in records.values()) / 4, 3),
                "total_cost_usd": f"{sum(float(item['cost_usd']) for item in records.values()):.6f}",
                "authorized_human_reviews": 0,
                "accepted_candidates": 0,
            },
            "diagnostics": {
                "independent_repeat_drift": compare(candidates["g07a-independent-01"], candidates["g07a-independent-02"]),
                "target_change_global_drift_from_control": compare(source, candidates["g07a-target-change"]),
                "no_change_global_drift_from_reference": compare(nochange_source, candidates["g07a-no-change"]),
            },
            "contact_sheet": {"path": sheet.relative_to(ROOT).as_posix(), "sha256": sha256(sheet)},
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
