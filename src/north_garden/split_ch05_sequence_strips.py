"""Deterministically split hash-pinned CH05 sequence strips into panel images.

The source strips and panel crops remain ignored local research pixels.  This
tool only reads an explicit manifest, verifies every source byte and crop, and
writes non-promoted derivatives plus a machine-readable report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "production/comic/run-manifests/ch05-sequence-strip-crops-r1.json"
DEFAULT_OUTPUT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r1/panels"
DEFAULT_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r1/panel-split-report.json"
PLAN_SOURCE = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"


class SplitError(ValueError):
    """Raised when the manifest or a generated derivative fails closed."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def contained_path(relative: Any, prefix: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise SplitError(f"path must be non-empty and project-relative: {relative!r}")
    path = (ROOT / relative).resolve()
    try:
        normalized = path.relative_to(ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise SplitError(f"path escapes repository: {relative}") from exc
    if not normalized.startswith(prefix):
        raise SplitError(f"path must remain under {prefix}: {relative}")
    return path


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("record_type") != "CH05SequenceStripCropManifest":
        raise SplitError("unexpected record_type")
    if data.get("schema_version") != "1.0" or data.get("medium") != "comic":
        raise SplitError("manifest must be schema 1.0 comic data")
    if data.get("planning_structure") != "ComicPanelPlan":
        raise SplitError("planning_structure must be ComicPanelPlan")
    if data.get("animation_shot_plan") is not None or data.get("e_conte") is not None:
        raise SplitError("AnimationShotPlan and E-Conte must remain null")
    plan_ref = data.get("comic_panel_plan_source", {})
    expected_plan = PLAN_SOURCE.relative_to(ROOT).as_posix()
    if plan_ref.get("path") != expected_plan or plan_ref.get("sha256") != sha256(PLAN_SOURCE):
        raise SplitError("ComicPanelPlan source path/hash mismatch")
    if not isinstance(data.get("sequences"), list) or not data["sequences"]:
        raise SplitError("sequences must be a non-empty array")
    return data


def save_deterministic(image: Image.Image, path: Path) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with Image.open(path) as current:
            same_pixels = current.convert("RGB").tobytes() == image.convert("RGB").tobytes()
            same_size = current.size == image.size
        if not (same_pixels and same_size):
            raise SplitError(f"refusing to overwrite non-identical derivative: {path}")
    else:
        image.convert("RGB").save(path, format="PNG", compress_level=9, optimize=False)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
        "width": image.width,
        "height": image.height,
        "bytes": path.stat().st_size,
    }


def split(manifest_path: Path, output_dir: Path, report_path: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    plan_data = json.loads(PLAN_SOURCE.read_text(encoding="utf-8"))
    expected = [row["panel_id"] for row in sorted(plan_data["plans"], key=lambda row: row["display_order"])]
    produced: list[dict[str, Any]] = []
    observed: list[str] = []

    for sequence in manifest["sequences"]:
        source = sequence.get("source", {})
        source_path = contained_path(source.get("path"), "experiments/review-packets/")
        if not source_path.is_file() or sha256(source_path) != source.get("sha256"):
            raise SplitError(f"source missing or hash mismatch: {source.get('path')}")
        with Image.open(source_path) as opened:
            image = opened.convert("RGB")
        if [image.width, image.height] != [source.get("width"), source.get("height")]:
            raise SplitError(f"source dimensions mismatch: {source.get('path')}")
        crops = sequence.get("crops")
        if not isinstance(crops, list) or not crops:
            raise SplitError(f"sequence {sequence.get('sequence_id')} has no crops")
        for crop in crops:
            panel_id = crop.get("panel_id")
            box = crop.get("box")
            if not isinstance(panel_id, str) or not isinstance(box, list) or len(box) != 4:
                raise SplitError("every crop requires panel_id and four-value box")
            if any(isinstance(value, bool) or not isinstance(value, int) for value in box):
                raise SplitError(f"crop box must contain integers: {panel_id}")
            left, top, right, bottom = box
            if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
                raise SplitError(f"crop outside source bounds: {panel_id} {box}")
            if panel_id in observed:
                raise SplitError(f"duplicate panel crop: {panel_id}")
            observed.append(panel_id)
            panel_number = int(panel_id.rsplit("p", 1)[1])
            destination = output_dir / f"p{panel_number:03d}-sequence-derived-r1.png"
            artifact = save_deterministic(image.crop((left, top, right, bottom)), destination)
            produced.append({
                "display_order": panel_number,
                "panel_id": panel_id,
                "sequence_id": sequence.get("sequence_id"),
                "source": source,
                "crop_box": box,
                "output": artifact,
            })

    if observed != expected:
        raise SplitError(f"crop coverage/order differs from 50 approved plans: {len(observed)} rows")
    report = {
        "record_type": "CH05SequenceStripSplitReport",
        "schema_version": "1.0",
        "state": "DERIVATIVES_BUILT_UNACCEPTED",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "manifest": {
            "path": manifest_path.relative_to(ROOT).as_posix(),
            "sha256": sha256(manifest_path),
        },
        "summary": {
            "sequence_sources": len(manifest["sequences"]),
            "panels_produced": len(produced),
            "complete_plan_coverage": len(produced) == len(expected),
            "source_hashes_verified": len(manifest["sequences"]),
            "crop_bounds_verified": len(produced),
        },
        "panels": produced,
        "boundary": "Ignored local derivatives only; no acceptance, commercial clearance, or exact production base selection.",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if report_path.exists() and report_path.read_text(encoding="utf-8") != encoded:
        raise SplitError(f"refusing to overwrite non-identical report: {report_path}")
    report_path.write_text(encoded, encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    args = parser.parse_args()
    report = split(Path(args.manifest).resolve(), Path(args.output_dir).resolve(), Path(args.report).resolve())
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
