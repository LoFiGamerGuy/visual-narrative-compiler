"""Compile completed built-in ImageGen executions for CH05 premium-cel r1."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-prompt-manifest-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-execution-manifest-r1.json"
UNAVAILABLE = ["model", "endpoint", "provider_request_id", "usage", "cost_usd", "deterministic_seed"]
RUNS: dict[str, dict[str, Any]] = {
    "premium-cel-s01-opening-departure": {"id": "exec-d04ed89c-e73c-45b5-aed2-4b590aa68638", "sha": "fc5dd34772640a2acee40a88a296db66f1d749a9cbec8f3a9615686538bf1d2f", "w": 863, "h": 1822, "bytes": 2726313, "batch": "pc01-parallel", "elapsed": None, "wall": 239.1},
    "premium-cel-s02-runnel-marker-trail": {"id": "exec-d89a1ca9-ef46-41a2-a0ed-56f6fd7fe90d", "sha": "365e14526ef91f5fb8f426832f02afe598768fc962a6766f8faf5d4ce2b84031", "w": 841, "h": 1870, "bytes": 2852351, "batch": "pc01-parallel", "elapsed": None, "wall": 239.1},
    "premium-cel-s03-listening-twine-ridge": {"id": "exec-3bbcf116-57a4-4568-a55f-c57d878f1b85", "sha": "ac38e19d17593a393a4e86f58b50c3d0598bb105f2476358326080635136ca97", "w": 853, "h": 1844, "bytes": 2527903, "batch": "pc02-parallel", "elapsed": None, "wall": 205.6},
    "premium-cel-s04-mill-reveal-bridge-warning": {"id": "exec-bacf383e-83c6-49e5-9d5c-aaf769cad654", "sha": "77ab6a830e16b6d80872336e26f2d74301d577a602c356028267a8223622e3ea", "w": 832, "h": 1890, "bytes": 2685500, "batch": "pc02-parallel", "elapsed": None, "wall": 205.6},
    "premium-cel-s05-creek-marker-drum": {"id": "exec-a569d74a-9056-477c-bb26-6bd92862cff9", "sha": "176f22e1ec13b4f45163dcafb8663c7ebce780512a8f898163c76ed4ccf6a95b", "w": 824, "h": 1908, "bytes": 2494166, "batch": "pc03-parallel", "elapsed": None, "wall": 218.2},
    "premium-cel-s06-ember-line-entry": {"id": "exec-b0654532-469f-49ee-b31b-be6e62393451", "sha": "eeb5dbb3111c1db241bd6b86ecf2046f3e564864d61f923edfb03802a331f0bd", "w": 842, "h": 1869, "bytes": 2509174, "batch": "pc03-parallel", "elapsed": None, "wall": 218.2},
    "premium-cel-s07-impossible-footprints-bell": {"id": "exec-fbbdbfeb-3ee2-4539-88be-340da3965a26", "sha": "710f94d8864ace2941016c854f7609f608199a89735d3a543011f3cd2f95a7bb", "w": 829, "h": 1898, "bytes": 2621436, "batch": "pc04-parallel", "elapsed": None, "wall": 230.6},
    "premium-cel-s08-plank-tin-map": {"id": "exec-bf2b775d-f617-45f7-9c92-0f6668d3b17a", "sha": "6deb5472711b20cfdca7f266bef6ef25e33e56467a5bcb5da56604233094e856", "w": 842, "h": 1868, "bytes": 2957398, "batch": "pc04-parallel", "elapsed": None, "wall": 230.6},
    "premium-cel-s09-deduction-retreat-cut": {"id": "exec-a6b8bec4-9af9-41c7-a169-48b442e029bb", "sha": "659c737dc87f2f0fde66c86941446fa1946b9a307cae7932f1dd0ccc3bb4c6a6", "w": 852, "h": 1846, "bytes": 2386407, "batch": "pc05-parallel", "elapsed": None, "wall": 221.7},
    "premium-cel-s10-silence-return": {"id": "exec-77032c6c-a2e8-4dd8-accc-75f97322063b", "sha": "07ee33cbe04c59ba092391a2137db14c3bdc6b9db8cdedfaf02487953a904f14", "w": 864, "h": 1821, "bytes": 2325154, "batch": "pc05-parallel", "elapsed": None, "wall": 221.7},
    "premium-cel-s11-farmhouse-reversal": {"id": "exec-6b038c9d-8fd4-42a7-b5fe-c89983b96e7f", "sha": "d613edb3b92e151c0589765a131f244959ca0507378e4171f74bdaffd1c358a7", "w": 853, "h": 1844, "bytes": 2766164, "batch": "pc06-single", "elapsed": 118.8, "wall": 118.8},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    prompt_doc = json.loads(PROMPTS.read_text(encoding="utf-8"))
    records: list[dict[str, Any]] = []
    batches: dict[str, float] = {}
    for sequence in prompt_doc["sequences"]:
        run = RUNS[sequence["sequence_id"]]
        path = ROOT / sequence["planned_output"]
        if not path.is_file() or sha256(path) != run["sha"] or path.stat().st_size != run["bytes"]:
            raise ValueError(f"output binding: {sequence['sequence_id']}")
        with Image.open(path) as image:
            if image.format != "PNG" or image.size != (run["w"], run["h"]):
                raise ValueError(f"decode/dimensions: {sequence['sequence_id']}")
        if run["batch"] in batches and batches[run["batch"]] != run["wall"]:
            raise ValueError(f"inconsistent batch wall: {run['batch']}")
        batches.setdefault(run["batch"], run["wall"])
        records.append(
            {
                "sequence_id": sequence["sequence_id"],
                "source_sequence_id": sequence["source_sequence_id"],
                "panel_range": sequence["panel_range"],
                "panel_count": sequence["panel_count"],
                "prompt_text": sequence["prompt_text"],
                "prompt_sha256": sequence["prompt_sha256"],
                "input_references": sequence["input_references"],
                "cross_panel_gate_phrases": sequence["cross_panel_gate_phrases"],
                "execution": {
                    "tool_mode": "openai_builtin_imagegen_in_codex",
                    "tool_service_execution_id": run["id"],
                    "tool_service_execution_id_is_provider_request_id": False,
                    "timing_batch_id": run["batch"],
                    "elapsed_seconds": run["elapsed"],
                    "parallel_batch_wall_seconds": run["wall"],
                    "model": None,
                    "endpoint": None,
                    "provider_request_id": None,
                    "usage": None,
                    "cost_usd": None,
                    "deterministic_seed": None,
                    "unavailable_fields": UNAVAILABLE,
                },
                "output": {
                    "path": sequence["planned_output"],
                    "sha256": run["sha"],
                    "width": run["w"],
                    "height": run["h"],
                    "bytes": run["bytes"],
                },
                "human_review_state": "PENDING",
                "human_review_minutes": None,
                "accepted": False,
                "commercially_cleared": False,
                "exact_production_base": False,
                "generation_reproducible": False,
            }
        )
    if set(RUNS) != {row["sequence_id"] for row in prompt_doc["sequences"]}:
        raise ValueError("execution table differs from prompt sequence set")
    document = {
        "record_type": "CH05CompleteChapterPremiumCelExecutionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-premium-cel-executions-r1",
        "state": "EXECUTED_UNACCEPTED_PENDING_HUMAN_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "input_prompt_manifest": {"path": PROMPTS.relative_to(ROOT).as_posix(), "sha256": sha256(PROMPTS)},
        "summary": {
            "sequence_outputs": len(records),
            "comic_panel_plans_requested": sum(row["panel_count"] for row in records),
            "planned_comic_panel_crops": 50,
            "authorized_reference_uses": sum(len(row["input_references"]) for row in records),
            "unique_timing_batches": len(batches),
            "overlap_adjusted_tool_call_wall_seconds": round(sum(batches.values()), 1),
            "timing_scope": "Codex ImageGen tool-call wall at 0.1-second precision; includes any queue, generation, and transfer time exposed to the caller.",
            "per_output_elapsed_seconds_available": sum(row["execution"]["elapsed_seconds"] is not None for row in records),
            "direct_paid_provider_api_calls": 0,
            "paid_spend_usd": 0.0,
            "human_reviewed_outputs": 0,
            "accepted_outputs": 0,
            "commercially_cleared_outputs": 0,
            "exact_production_base_outputs": 0,
        },
        "timing_batches": [
            {
                "timing_batch_id": batch_id,
                "wall_seconds": wall,
                "member_sequence_ids": [row["sequence_id"] for row in records if row["execution"]["timing_batch_id"] == batch_id],
            }
            for batch_id, wall in batches.items()
        ],
        "records": records,
        "limitations": [
            "The built-in tool exposed no model, endpoint, provider request ID, usage, monetary cost, or deterministic seed.",
            "Codex tool-service execution IDs are provenance aids only and are not provider request IDs.",
            "Parallel execution exposes batch wall only; paired per-output elapsed time remains null.",
            "The final singleton exposes individual elapsed time; it is not inferred for paired outputs.",
            "Prompt-gate presence does not prove pixel compliance.",
            "Exact prompts, references, and output hashes do not make stochastic generation reproducible.",
            "Outputs remain unaccepted and commercially uncleared.",
        ],
        "boundary": {
            "permitted_product": "openai_builtin_imagegen",
            "direct_paid_provider_api_calls": 0,
            "bfl_calls": 0,
            "new_upload_classes": 0,
            "real_person_or_child_material": 0,
        },
    }
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), **document["summary"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
