"""Split a hash-pinned targeted CH05 repair strip into declared panel crops."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "production/comic/run-manifests/ch05-targeted-clue-chain-crops-r1.json"
DEFAULT_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r3/repairs/clue-chain-crop-report.json"
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project_path(raw: str, *, ignored_output: bool = False) -> Path:
    rel = Path(raw.replace("\\", "/"))
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"unsafe project path: {raw}")
    path = (ROOT / rel).resolve()
    path.relative_to(ROOT.resolve())
    if ignored_output and not path.relative_to(ROOT).as_posix().startswith("experiments/review-packets/"):
        raise ValueError(f"output must remain under ignored review packets: {raw}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("record_type") != "CH05TargetedRepairCropManifest" or data.get("planning_structure") != "ComicPanelPlan":
        raise ValueError("invalid targeted crop manifest")
    if data.get("animation_shot_plan") is not None or data.get("e_conte") is not None:
        raise ValueError("targeted crops must remain ComicPanelPlan-only")
    source_row = data["source"]
    source = project_path(source_row["path"])
    if sha256(source) != source_row["sha256"]:
        raise ValueError("targeted strip source hash mismatch")
    plan_doc = json.loads(PLAN.read_text(encoding="utf-8"))
    revisions = {row["panel_id"]: row["plan_revision_id"] for row in plan_doc["plans"]}
    produced: list[dict[str, Any]] = []
    with Image.open(source) as opened:
        image = opened.convert("RGB")
        if (image.width, image.height) != (source_row["width"], source_row["height"]):
            raise ValueError("targeted strip dimensions mismatch")
        for row in data["panels"]:
            panel_id = row["panel_id"]
            if revisions.get(panel_id) != row["plan_revision_id"]:
                raise ValueError(f"plan revision mismatch: {panel_id}")
            left, top, right, bottom = row["crop_box"]
            if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
                raise ValueError(f"crop outside source: {panel_id}")
            destination = project_path(row["output"], ignored_output=True)
            destination.parent.mkdir(parents=True, exist_ok=True)
            crop = image.crop((left, top, right, bottom))
            if destination.exists():
                with Image.open(destination) as current:
                    if current.convert("RGB").tobytes() != crop.tobytes() or current.size != crop.size:
                        raise ValueError(f"refusing to overwrite non-identical crop: {destination}")
            else:
                crop.save(destination, format="PNG", compress_level=9, optimize=False)
            produced.append({
                "panel_id": panel_id,
                "plan_revision_id": row["plan_revision_id"],
                "crop_box": row["crop_box"],
                "artifact": {
                    "path": destination.relative_to(ROOT).as_posix(),
                    "sha256": sha256(destination),
                    "width": crop.width,
                    "height": crop.height,
                    "bytes": destination.stat().st_size,
                },
            })
    report = {
        "record_type": "CH05TargetedRepairCropReport",
        "schema_version": "1.0",
        "state": "THREE_CROPS_BUILT_PENDING_OWNER_REVIEW",
        "manifest": {"path": manifest_path.relative_to(ROOT).as_posix(), "sha256": sha256(manifest_path)},
        "source": source_row,
        "panels": produced,
        "boundary": "Ignored local derivatives only; no acceptance or promotion.",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(report, indent=2) + "\n"
    if report_path.exists() and report_path.read_text(encoding="utf-8") != encoded:
        raise ValueError("refusing to overwrite non-identical crop report")
    report_path.write_text(encoded, encoding="utf-8", newline="\n")
    print(json.dumps({"panels": len(produced), "report_sha256": sha256(report_path), "artifacts": [row["artifact"] for row in produced]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
