"""Controlled legacy-only G07 role-swap smoke for sequential inpainting.

G07a/G07b semantic intent remains frozen and grounded.  This module never
claims its calibrated 2D plate is canonical grounded evidence: it builds a
non-scoring adapter preflight with explicit legacy-stage limitations, target
masks, no-change controls, and assertion-led review records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from pathlib import Path

from PIL import Image, ImageDraw

from .sequential_inpaint import (
    COMFY, ROOT, custom_node_versions, digest, graph, model_inventory,
    post_and_wait, runtime_snapshot, stamp, metrics,
)

GAUNTLET = ROOT / "research/authoritative/v2.1.1/bench/gauntlet.json"
ASSETS = COMFY / "input/experiments/sequential_inpaint_g07_v1"
RECORDS = ROOT / "experiments/records/sequential_inpaint_g07_v1"
PLANS = ROOT / "manifests/experiments/sequential-inpaint-g07-controls-v1.json"
SOURCE_PLATE = COMFY / "output/rm_table_00001_.png"
OUTPUT_G07 = COMFY / "output/sequential_inpaint_g07_v1"
W, H = 1216, 832
FROZEN_SHA256 = "f826b0f1d06ed5a999667bde23ba0d04f8ebb22f516095034dab62c7541ae9ae"

CASES = {
    "G07a": {"left": "SOREN", "right": "SIGRID"},
    "G07b": {"left": "SIGRID", "right": "SOREN"},
}
IDENTITY = {
    "SOREN": ("soren_v1.safetensors", "Soren, adult man with dark wavy hair and short beard"),
    "SIGRID": ("sigrid_v1.safetensors", "Sigrid, adult woman with thick curly red-auburn hair and freckles"),
}


def sha_json(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def frozen_cases() -> dict[str, dict]:
    if digest(GAUNTLET) != FROZEN_SHA256:
        raise RuntimeError("frozen gauntlet hash changed; refusing to construct control assets")
    all_cases = {c["id"]: c for c in json.loads(GAUNTLET.read_text(encoding="utf-8"))["render_cases"]}
    selected = {case_id: all_cases[case_id] for case_id in CASES}
    for case_id, case in selected.items():
        expected = CASES[case_id]
        if case["spatial_mode"] != "grounded" or case["manifest"]["layout"] != expected:
            raise RuntimeError(f"unexpected frozen semantics for {case_id}")
    return selected


def asset_paths(case_id: str) -> dict[str, Path]:
    root = ASSETS / case_id
    return {"plate": root / "legacy_table_plate_v1.png", "left": root / "left_target_mask_v1.png", "right": root / "right_target_mask_v1.png", "none": root / "no_change_zero_mask_v1.png"}


def prepare() -> dict[str, dict[str, str]]:
    frozen_cases()
    if not SOURCE_PLATE.exists():
        raise FileNotFoundError(SOURCE_PLATE)
    result: dict[str, dict[str, str]] = {}
    # Fixed, disjoint target areas deliberately leave a centre seam. They are
    # legacy experiment controls, not actor mattes or a canonical stage asset.
    rects = {"left": (85, 205, 575, 760), "right": (640, 205, 1130, 760)}
    for case_id in CASES:
        paths = asset_paths(case_id)
        paths["plate"].parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE_PLATE, paths["plate"])
        for side, rect in rects.items():
            mask = Image.new("L", (W, H), 0)
            ImageDraw.Draw(mask).rounded_rectangle(rect, radius=24, fill=255)
            mask.save(paths[side])
        Image.new("L", (W, H), 0).save(paths["none"])
        result[case_id] = {name: str(path.relative_to(ROOT)).replace("\\", "/") for name, path in paths.items()}
    return result


def plan() -> dict:
    frozen = frozen_cases()
    assets = prepare()
    cases = []
    for case_id, assignment in CASES.items():
        cases.append({
            "case_id": case_id,
            "semantic_description": frozen[case_id]["description"],
            "semantic_spatial_mode": frozen[case_id]["spatial_mode"],
            "legacy_execution_limitation": "Calibrated 2D room plate plus rectangular masks; not a canonical 3D stage, actor matte, or valid grounded benchmark implementation.",
            "asset_hashes": {name: digest(ROOT / relative) for name, relative in assets[case_id].items()},
            "layout": assignment,
            "hard_assertion_manifest": {
                "count": {"exact": 2},
                "roles": {"left": assignment["left"], "right": assignment["right"]},
                "set": "KITCHEN",
                "interaction": "both seated at table, not touching",
                "forbidden": ["extra person", "child", "duplicate character", "role swap"],
                "spatial_mode_requirement": "grounded semantic intent retained; legacy execution cannot prove canonical grounding"
            },
            "no_change_control": {
                "seed": 101,
                "denoise": 0.0,
                "mask": "no_change_zero_mask_v1.png",
                "purpose": "Measure VAE/workflow reconstruction drift without an active inpaint region before interpreting identity repair. Active-mask denoise-zero output is retained separately as an invalid-control diagnostic."
            },
            "smoke_seeds": [101, 202]
        })
    return {"manifest_id": "sequential-inpaint-g07-controls-v1", "state": "NON_SCORING_LEGACY_PREFLIGHT", "semantic_source": str(GAUNTLET.relative_to(ROOT)).replace("\\", "/"), "semantic_source_sha256": FROZEN_SHA256, "cases": cases}


def write_plan() -> Path:
    PLANS.parent.mkdir(parents=True, exist_ok=True)
    payload = plan()
    PLANS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return PLANS


def prompt_for(character: str, side: str) -> tuple[str, str]:
    lora, identity = IDENTITY[character]
    prompt = (
        "drawn manhwa comic panel, old farmhouse kitchen at night, warm woodstove, table, two-person quiet domestic scene, "
        "bold ink outline, cel shading, " + identity + f", seated on the {side} side of the table, not touching the other adult, no other person"
    )
    return lora, prompt


def execute(case_id: str, seed: int, control: bool, suffix: str | None) -> Path:
    manifest = plan()
    case = next(item for item in manifest["cases"] if item["case_id"] == case_id)
    paths = asset_paths(case_id)
    RECORDS.mkdir(parents=True, exist_ok=True)
    control_name = "nochange" if control else "smoke"
    ext = f"-{suffix}" if suffix else ""
    record_path = RECORDS / f"{case_id.lower()}-seed-{seed}-{control_name}{ext}.json"
    if record_path.exists():
        raise FileExistsError(f"refusing to overwrite immutable record: {record_path}")
    record = {
        "schema_version": "1.0", "adapter": "sequential_inpaint_per_character", "adapter_version": "g07-controls-v1",
        "case_id": case_id, "semantic_source_sha256": FROZEN_SHA256, "input_state": case,
        "control_type": control_name, "seed": seed, "started_at": stamp(), "runtime": runtime_snapshot(),
        "custom_node_versions": custom_node_versions(), "model_hashes": model_inventory(),
        "source_code": {"path": "src/north_garden/sequential_inpaint_g07.py", "sha256": digest(Path(__file__))},
        "dependency_source": {"path": "src/north_garden/sequential_inpaint.py", "sha256": digest(ROOT / "src/north_garden/sequential_inpaint.py")},
        "human_review_status": "not_reviewed", "human_minutes": None, "accepted_output": None, "steps": []
    }
    prior = paths["plate"]
    steps = [("left", case["layout"]["left"])] if control else [("left", case["layout"]["left"]), ("right", case["layout"]["right"])]
    for index, (side, character) in enumerate(steps, 1):
        lora, prompt = prompt_for(character, side)
        workflow = graph(
            str(prior.relative_to(COMFY / "input")).replace("\\", "/"),
            str(paths["none" if control else side].relative_to(COMFY / "input")).replace("\\", "/"), prompt, lora, seed + index - 1,
            f"sequential_inpaint_g07_v1/{case_id}_seed{seed}_{control_name}_{index}_{character.lower()}",
            denoise=0.0 if control else 1.0,
        )
        started = time.perf_counter()
        prompt_id, filename = post_and_wait(workflow, f"g07-{case_id}-{seed}-{control_name}-{side}")
        output = OUTPUT_G07 / filename
        next_input = paths["plate"].parent / f"{case_id}_seed{seed}_{control_name}_{index}_{character.lower()}.png"
        shutil.copy2(output, next_input)
        record["steps"].append({
            "side": side, "character": character, "lora": lora, "prompt": prompt, "workflow": workflow,
            "workflow_sha256": sha_json(workflow), "input": {"path": str(prior.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(prior)},
            "mask": {"path": str(paths["none" if control else side].relative_to(ROOT)).replace("\\", "/"), "sha256": digest(paths["none" if control else side])},
            "output": {"path": str(output.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(output)},
            "prompt_id": prompt_id, "generation_seconds": round(time.perf_counter() - started, 3),
            "measurements": metrics(prior, output, paths[side])
        })
        prior = next_input
    record["ended_at"] = stamp(); record["status"] = "completed"
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true"); parser.add_argument("--write-plan", action="store_true")
    parser.add_argument("--case", choices=sorted(CASES)); parser.add_argument("--seed", type=int)
    parser.add_argument("--no-change", action="store_true"); parser.add_argument("--record-suffix")
    args = parser.parse_args()
    if args.prepare: print(json.dumps(prepare(), indent=2))
    elif args.write_plan: print(write_plan())
    elif args.case and args.seed is not None: print(execute(args.case, args.seed, args.no_change, args.record_suffix))
    else: parser.error("choose --prepare, --write-plan, or --case CASE --seed SEED")
