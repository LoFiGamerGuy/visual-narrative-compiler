"""Hash and classify a local raster as a pending comic base candidate, never approval."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, UnidentifiedImageError


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
OUT_DIR = ROOT / "experiments/intake/comic-base-candidates"
ID = re.compile(r"^[a-z0-9][a-z0-9._-]+$")


class CandidateIntakeError(ValueError):
    """Raised when local candidate intake is unsafe or incomplete."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_candidate(*, panel_id: str, raster_path: Path, candidate_id: str) -> Path:
    if not ID.fullmatch(candidate_id):
        raise CandidateIntakeError("candidate_id must use lowercase safe identifier characters")
    try:
        raster = raster_path.resolve(strict=True)
    except OSError as error:
        raise CandidateIntakeError("candidate raster does not exist") from error
    if not raster.is_relative_to(ROOT):
        raise CandidateIntakeError("candidate raster must remain inside the local project root")
    try:
        with Image.open(raster) as image:
            width, height = image.size
            image_format, mode = image.format, image.mode
            image.verify()
    except (OSError, UnidentifiedImageError) as error:
        raise CandidateIntakeError("candidate is not a decodable raster") from error
    if image_format not in {"PNG", "JPEG", "WEBP"}:
        raise CandidateIntakeError("candidate raster format is unsupported")
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    panel = next((item for item in plans["plans"] if item["panel_id"] == panel_id), None)
    if panel is None:
        raise CandidateIntakeError(f"unknown ComicPanelPlan panel_id: {panel_id}")
    relative_raster = raster.relative_to(ROOT).as_posix()
    is_layout_control = any(
        marker in relative_raster
        for marker in (
            "ch05_p033_p038_sequence_layout_control_r1/",
            "ch05_p036_layout_control_r1/",
        )
    )
    record = {
        "record_type": "ComicPanelBaseRasterCandidate",
        "schema_version": "1.0",
        "record_id": candidate_id,
        "state": "PENDING_HUMAN_CLASSIFICATION_AND_BASE_APPROVAL",
        "medium": "comic",
        "animation_shot_plan": None,
        "comic_panel_plan": {
            "collection_path": PLANS.relative_to(ROOT).as_posix(),
            "collection_sha256": sha256(PLANS),
            "panel_id": panel_id,
            "plan_revision_id": panel["plan_revision_id"],
        },
        "raster": {
            "path": relative_raster,
            "sha256": sha256(raster),
            "format": image_format,
            "mode": mode,
            "width": width,
            "height": height,
        },
        "provenance": {
            "intake_method": "local_hash_only_no_copy_no_upload",
            "candidate_kind": "deterministic_layout_control_not_art" if is_layout_control else "unclassified_raster",
            "source_record_ids": [],
            "source_asset_ids": panel["asset_ids"],
            "render_record": None,
        },
        "approval_eligibility": {
            "eligible": False if is_layout_control else None,
            "reason": (
                "ADR-0027 prohibits deterministic layout controls from serving as visual evidence or approved base art."
                if is_layout_control
                else "Requires explicit human classification and art/provenance review."
            ),
        },
        "data_classification": {
            "review_status": "not_yet_performed",
            "fictional_adults_only": None,
            "real_person_likeness": None,
            "child_material": None,
            "personal_or_biometric_data": None,
            "lora_output": None,
        },
        "review": {
            "human_review_status": "not_yet_performed",
            "human_minutes": None,
            "accepted_as_base": False,
        },
        "permissions": {
            "local_repair_input_authorized": False,
            "external_upload_authorized": False,
        },
        "boundary": "Local intake records exact bytes only. It is not art acceptance, local repair approval, external upload authority, a RenderRecord, AnimationShotPlan, or E-Conte.",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{candidate_id}.json"
    if out.exists():
        existing = json.loads(out.read_text(encoding="utf-8"))
        if existing != record:
            raise CandidateIntakeError("candidate_id already exists with different immutable content")
        return out
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel-id", required=True)
    parser.add_argument("--raster", required=True, type=Path)
    parser.add_argument("--candidate-id", required=True)
    args = parser.parse_args()
    print(prepare_candidate(panel_id=args.panel_id, raster_path=args.raster, candidate_id=args.candidate_id))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
