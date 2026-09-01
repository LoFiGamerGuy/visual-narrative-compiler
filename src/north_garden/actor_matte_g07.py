"""Deterministic actor-matte composite control for frozen G07 role swaps.

This is not a renderer competitor or a grounded benchmark result.  It reuses
existing local adult actor plates and calibrated 2D staging to isolate a simple
question exposed by broad-mask inpainting: can the recurring kitchen remain
bit-preserved outside explicitly composited actor/shadow influence regions?
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
COMFY = ROOT / "ComfyUI"
GAUNTLET = ROOT / "research/authoritative/v2.1.1/bench/gauntlet.json"
OUT = ROOT / "experiments/outputs/actor_matte_g07_v1"
RECORDS = ROOT / "experiments/records/actor_matte_g07_v1"
MANIFEST = ROOT / "manifests/experiments/actor-matte-g07-controls-v1.json"
FROZEN_SHA256 = "f826b0f1d06ed5a999667bde23ba0d04f8ebb22f516095034dab62c7541ae9ae"

sys.path.insert(0, str(ROOT / "garden"))
from stage import build, H_SEATED  # noqa: E402
from rooms_def import TABLE  # noqa: E402

CASES = {
    "G07a": [
        ("SOREN", "pg_pl_dio_sit_00002_.png", 0.34, False),
        ("SIGRID", "pg_pl_thal_sit_00002_.png", 0.68, True),
    ],
    "G07b": [
        ("SIGRID", "pg_pl_thal_sit_00002_.png", 0.34, False),
        ("SOREN", "pg_pl_dio_sit_00002_.png", 0.68, True),
    ],
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def frozen() -> dict[str, dict]:
    if digest(GAUNTLET) != FROZEN_SHA256:
        raise RuntimeError("frozen gauntlet hash changed; refusing actor-matte control")
    by_id = {case["id"]: case for case in json.loads(GAUNTLET.read_text(encoding="utf-8"))["render_cases"]}
    for case_id, expected in (("G07a", {"left": "SOREN", "right": "SIGRID"}), ("G07b", {"left": "SIGRID", "right": "SOREN"})):
        if by_id[case_id]["manifest"]["layout"] != expected or by_id[case_id]["spatial_mode"] != "grounded":
            raise RuntimeError(f"unexpected frozen definition for {case_id}")
    return {key: by_id[key] for key in CASES}


def stage_sources() -> list[dict[str, str]]:
    paths = [ROOT / "garden/stage.py", ROOT / "garden/rooms_def.py", ROOT / "garden/panelcomp.py", Path(TABLE.path)]
    for _, filename, _, _ in sum((items for items in CASES.values()), []):
        paths.append(COMFY / "output" / filename)
    seen: set[Path] = set()
    return [{"path": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(p)} for p in paths if p.exists() and not (p in seen or seen.add(p))]


def declared_manifest() -> dict:
    cases = frozen()
    return {
        "manifest_id": "actor-matte-g07-controls-v1",
        "state": "NON_SCORING_LEGACY_COMPOSITE_CONTROL",
        "semantic_source": str(GAUNTLET.relative_to(ROOT)).replace("\\", "/"),
        "semantic_source_sha256": FROZEN_SHA256,
        "sources": stage_sources(),
        "cases": [{
            "case_id": case_id,
            "semantic_description": case["description"],
            "semantic_spatial_mode": "grounded",
            "legacy_execution_limitation": "Calibrated 2D compositor only; it preserves the semantic declaration but cannot establish canonical 3D grounding.",
            "actor_placements": [{"role": role, "x": x, "depth": 0.55 if role == "SOREN" else 0.50, "real_height": "H_SEATED", "flip": flip} for role, _, x, flip in CASES[case_id]],
            "hard_assertion_manifest": {"count": {"exact": 2}, "roles": case["manifest"]["layout"], "set": "KITCHEN", "interaction": "both seated at table, not touching", "forbidden": ["extra person", "child", "duplicate character", "role swap"]}
        } for case_id, case in cases.items()]
    }


def write_manifest() -> Path:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(declared_manifest(), indent=2) + "\n", encoding="utf-8")
    return MANIFEST


def compose(case_id: str) -> Path:
    manifest = declared_manifest()
    case = next(item for item in manifest["cases"] if item["case_id"] == case_id)
    OUT.mkdir(parents=True, exist_ok=True); RECORDS.mkdir(parents=True, exist_ok=True)
    output = OUT / f"{case_id.lower()}-actor-matte-composite-r1.png"
    record_path = RECORDS / f"{case_id.lower()}-actor-matte-composite-r1.json"
    if output.exists() or record_path.exists():
        raise FileExistsError(f"refusing to overwrite immutable composite revision for {case_id}")
    figures = [{"path": str(COMFY / "output" / filename), "x": x, "depth": 0.55 if role == "SOREN" else 0.50, "real_h": H_SEATED, "flip": flip} for role, filename, x, flip in CASES[case_id]]
    base = Image.open(TABLE.path).convert("RGB")
    composed = build(TABLE, figures, size=base.size)
    composed.save(output)
    a = np.asarray(base, dtype=np.int16); b = np.asarray(composed, dtype=np.int16)
    changed = np.any(a != b, axis=2)
    record = {
        "schema_version": "1.0", "adapter": "actor_matte_legacy_composite_control", "adapter_version": "1.0",
        "case_id": case_id, "semantic_source_sha256": FROZEN_SHA256, "input_state": case,
        "started_at": stamp(), "ended_at": stamp(), "execution": "deterministic local Pillow compositor; no diffusion renderer call",
        "sources": stage_sources(), "base_plate": {"path": str(Path(TABLE.path).relative_to(ROOT)).replace("\\", "/"), "sha256": digest(Path(TABLE.path))},
        "output": {"path": str(output.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(output)},
        "measurements": {"changed_pixel_fraction": float(changed.mean()), "unchanged_pixel_fraction": float((~changed).mean()), "base_to_output_mean_absolute_change": float(np.abs(a-b).mean()/255.0)},
        "human_review_status": "not_reviewed", "human_minutes": None, "accepted_output": None,
        "status": "completed_non_scoring_control"
    }
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true"); parser.add_argument("--case", choices=sorted(CASES))
    args = parser.parse_args()
    if args.write_manifest: print(write_manifest())
    elif args.case: print(compose(args.case))
    else: parser.error("choose --write-manifest or --case")
