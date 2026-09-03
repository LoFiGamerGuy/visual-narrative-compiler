"""Compile the completed built-in ImageGen execution record for CH05 alternate graphic r1."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-alt-graphic-prompt-manifest-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-alt-graphic-execution-manifest-r1.json"
UNAVAILABLE = ["model", "endpoint", "provider_request_id", "usage", "cost_usd", "deterministic_seed"]

RUNS: dict[str, dict[str, Any]] = {
    "alt-graphic-s01-opening-departure": {"tool_service_execution_id": "exec-365fa1e5-eb4b-45b0-9b5a-1fe19a0d33f2", "sha256": "54d35f55e7bfbb4d761748bad9653177d68508808d02acb376eb61d013cc1d50", "width": 805, "height": 1953, "bytes": 2674155, "timing_batch_id": "b01-single", "elapsed_seconds": 91.5, "parallel_batch_wall_seconds": 91.5},
    "alt-graphic-s02-runnel-marker-trail": {"tool_service_execution_id": "exec-b3c9ec12-3cab-4ca5-9f49-773b16587900", "sha256": "0f96433c5bf60a06ee1e4900f02c023d71592ab7ca1f43f0ae48e43afdd51cbe", "width": 814, "height": 1931, "bytes": 2743149, "timing_batch_id": "b02-parallel", "elapsed_seconds": None, "parallel_batch_wall_seconds": 169.0},
    "alt-graphic-s03-listening-twine-ridge": {"tool_service_execution_id": "exec-41b244e6-5025-4a8a-9ed9-74e35e043182", "sha256": "43e95123d58c72d90cd0820d799310e71de2af940cd6ad9482f975f4ede0b4b8", "width": 816, "height": 1928, "bytes": 2430175, "timing_batch_id": "b02-parallel", "elapsed_seconds": None, "parallel_batch_wall_seconds": 169.0},
    "alt-graphic-s04-mill-reveal-bridge-warning": {"tool_service_execution_id": "exec-4f2c9e37-b43a-45f8-b989-db1d203e6876", "sha256": "2ecbb6ae1755e13b159172cb736c23b39dcace52439706c111a77ca9be5b082b", "width": 851, "height": 1847, "bytes": 2567186, "timing_batch_id": "b03-parallel", "elapsed_seconds": None, "parallel_batch_wall_seconds": 179.6},
    "alt-graphic-s05-creek-marker-drum": {"tool_service_execution_id": "exec-7d7278d8-1c1b-4844-a278-69a50d53a1f5", "sha256": "14de3a858330ebef9bbd85465c35053386debe04f1535fa475bc21dc77af234b", "width": 842, "height": 1869, "bytes": 2495826, "timing_batch_id": "b03-parallel", "elapsed_seconds": None, "parallel_batch_wall_seconds": 179.6},
    "alt-graphic-s06-ember-line-entry": {"tool_service_execution_id": "exec-b37bcdea-ebdf-4f95-ac5f-860dafc24df1", "sha256": "bfe81e7f779f147e93c387eb29f39589debd73171649f8fc2579b147f9b7383f", "width": 841, "height": 1871, "bytes": 2448987, "timing_batch_id": "b04-parallel", "elapsed_seconds": None, "parallel_batch_wall_seconds": 184.7},
    "alt-graphic-s07-impossible-footprints-bell": {"tool_service_execution_id": "exec-9c340baa-177e-4b2f-b7d5-43c45f49ae36", "sha256": "7207f631c382719a64e2131088043f4ad0a288a2cab64f01bd414df6aa1fc61c", "width": 854, "height": 1842, "bytes": 2489798, "timing_batch_id": "b04-parallel", "elapsed_seconds": None, "parallel_batch_wall_seconds": 184.7},
    "alt-graphic-s08-plank-tin-map": {"tool_service_execution_id": "exec-d5bb3d06-3f81-4c1c-9211-274ee43e92a3", "sha256": "f05d8c034646414727aa81e4e3e6ff51a43465498b6c320aa35d19c0570df2dc", "width": 851, "height": 1848, "bytes": 2832704, "timing_batch_id": "b05-parallel", "elapsed_seconds": None, "parallel_batch_wall_seconds": 182.7},
    "alt-graphic-s09-deduction-retreat-cut": {"tool_service_execution_id": "exec-436ce91c-0bda-4e64-bf7e-8272e1647aff", "sha256": "3ab936afa59448ff2629149886ba06ad3d28f5d1dbbffe68690e5e577f1e9027", "width": 830, "height": 1896, "bytes": 2388131, "timing_batch_id": "b05-parallel", "elapsed_seconds": None, "parallel_batch_wall_seconds": 182.7},
    "alt-graphic-s10-silence-return": {"tool_service_execution_id": "exec-36b024a1-a0f0-4d5c-abaf-44e4a0819757", "sha256": "331b5dc9105a0a44f3ddf738ace18e08c58b2390714b123c85c4511b7fb5a117", "width": 853, "height": 1843, "bytes": 2395609, "timing_batch_id": "b06-parallel", "elapsed_seconds": None, "parallel_batch_wall_seconds": 146.8},
    "alt-graphic-s11-farmhouse-reversal": {"tool_service_execution_id": "exec-7037c54c-d080-4336-ab5b-09c321ed4e8a", "sha256": "4bc22cd2aaf909d0d28a21a36455b839e87f5588769fc82dcf2e1e28ecc8e646", "width": 829, "height": 1898, "bytes": 2557106, "timing_batch_id": "b06-parallel", "elapsed_seconds": None, "parallel_batch_wall_seconds": 146.8},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    prompt_doc = json.loads(PROMPTS.read_text(encoding="utf-8"))
    records = []
    batch_walls: dict[str, float] = {}
    for sequence in prompt_doc["sequences"]:
        run = RUNS[sequence["sequence_id"]]
        path = ROOT / sequence["planned_output"]
        if not path.is_file() or sha256(path) != run["sha256"]:
            raise ValueError(f"missing or mismatched output: {sequence['planned_output']}")
        with Image.open(path) as image:
            if list(image.size) != [run["width"], run["height"]]:
                raise ValueError(f"dimension mismatch: {sequence['sequence_id']}")
        if path.stat().st_size != run["bytes"]:
            raise ValueError(f"byte-size mismatch: {sequence['sequence_id']}")
        batch_walls.setdefault(run["timing_batch_id"], run["parallel_batch_wall_seconds"])
        records.append({
            "sequence_id": sequence["sequence_id"],
            "source_sequence_id": sequence["source_sequence_id"],
            "panel_range": sequence["panel_range"],
            "panel_count": sequence["panel_count"],
            "prompt_text": sequence["prompt_text"],
            "prompt_sha256": sequence["prompt_sha256"],
            "input_references": sequence["input_references"],
            "execution": {
                "tool_mode": "openai_builtin_imagegen_in_codex",
                "tool_service_execution_id": run["tool_service_execution_id"],
                "tool_service_execution_id_is_provider_request_id": False,
                "timing_batch_id": run["timing_batch_id"],
                "elapsed_seconds": run["elapsed_seconds"],
                "parallel_batch_wall_seconds": run["parallel_batch_wall_seconds"],
                "model": None,
                "endpoint": None,
                "provider_request_id": None,
                "usage": None,
                "cost_usd": None,
                "deterministic_seed": None,
                "unavailable_fields": UNAVAILABLE,
            },
            "output": {"path": sequence["planned_output"], "sha256": run["sha256"], "width": run["width"], "height": run["height"], "bytes": run["bytes"]},
            "human_review_state": "PENDING",
            "human_review_minutes": None,
            "accepted": False,
            "commercially_cleared": False,
            "exact_production_base": False,
            "generation_reproducible": False,
        })
    if set(RUNS) != {row["sequence_id"] for row in prompt_doc["sequences"]}:
        raise ValueError("execution table differs from prompt sequence set")
    document = {
        "record_type": "CH05CompleteChapterAlternateGraphicExecutionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-alt-graphic-executions-r1",
        "state": "EXECUTED_UNACCEPTED_PENDING_HUMAN_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "input_prompt_manifest": {"path": PROMPTS.relative_to(ROOT).as_posix(), "sha256": sha256(PROMPTS)},
        "summary": {
            "sequence_outputs": len(records),
            "comic_panel_plans_requested": sum(row["panel_count"] for row in records),
            "authorized_reference_uses": sum(len(row["input_references"]) for row in records),
            "unique_timing_batches": len(batch_walls),
            "overlap_adjusted_tool_call_wall_seconds": round(sum(batch_walls.values()), 1),
            "timing_scope": "Codex ImageGen tool-call wall at 0.1-second precision; includes any queue, generation, and transfer time exposed to the caller.",
            "per_output_elapsed_seconds_available": sum(row["execution"]["elapsed_seconds"] is not None for row in records),
            "direct_paid_provider_api_calls": 0,
            "paid_spend_usd": 0.0,
            "human_reviewed_outputs": 0,
            "accepted_outputs": 0,
            "commercially_cleared_outputs": 0,
            "exact_production_base_outputs": 0,
        },
        "timing_batches": [{"timing_batch_id": key, "wall_seconds": value, "member_sequence_ids": [row["sequence_id"] for row in records if row["execution"]["timing_batch_id"] == key]} for key, value in batch_walls.items()],
        "records": records,
        "limitations": [
            "The built-in tool exposed no model, endpoint, provider request ID, usage, monetary cost, or deterministic seed.",
            "Codex tool-service execution IDs are provenance aids only and are not provider request IDs.",
            "Parallel execution exposes batch wall time only; per-output elapsed time is unavailable for paired batches and is not inferred.",
            "Exact prompts, references, and output hashes do not make stochastic generation reproducible.",
            "Outputs remain unaccepted review evidence and are neither commercially cleared nor an exact production base.",
        ],
        "boundary": {"permitted_product": "openai_builtin_imagegen", "direct_paid_provider_api_calls": 0, "bfl_calls": 0, "new_upload_classes": 0, "real_person_or_child_material": 0},
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), **document["summary"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
