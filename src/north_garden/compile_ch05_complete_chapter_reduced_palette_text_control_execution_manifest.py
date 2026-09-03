"""Compile exact text-only ImageGen execution evidence for CH05 reduced-palette r1."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-prompt-manifest-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-execution-manifest-r1.json"
UNAVAILABLE = ["model", "provider", "endpoint", "provider_request_id", "usage", "cost_usd", "deterministic_seed"]
RUNS: dict[str, dict[str, Any]] = {
    "reduced-palette-text-control-s01-opening-departure": {
        "execution_id": "exec-6580cddb-29dd-4c86-b5a6-556e07c3c195",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a05d7c-0ac3-7872-8fa8-3fb9c14f6eaa/exec-6580cddb-29dd-4c86-b5a6-556e07c3c195.png",
        "elapsed": 112.2,
    },
    "reduced-palette-text-control-s02-runnel-marker-trail": {
        "execution_id": "exec-f438177f-a50d-4033-b9f6-696a2594b42d",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a05d7c-0ac3-7872-8fa8-3fb9c14f6eaa/exec-f438177f-a50d-4033-b9f6-696a2594b42d.png",
        "elapsed": 121.0,
    },
    "reduced-palette-text-control-s03-listening-twine-ridge": {
        "execution_id": "exec-c2f816e0-a71e-4c8f-b7d8-50f3efbde984",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a05d7c-0ac3-7872-8fa8-3fb9c14f6eaa/exec-c2f816e0-a71e-4c8f-b7d8-50f3efbde984.png",
        "elapsed": 50.1,
    },
    "reduced-palette-text-control-s04-mill-reveal-bridge-warning": {
        "execution_id": "exec-fe8ba879-45ed-43ec-aaeb-9284088b8b3c",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-d2bb-7123-ad79-763c499a4aee/exec-fe8ba879-45ed-43ec-aaeb-9284088b8b3c.png",
        "elapsed": 113.0,
    },
    "reduced-palette-text-control-s05-creek-marker-drum": {
        "execution_id": "exec-f464fba1-2743-4804-9a38-7ba61627389c",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-d2bb-7123-ad79-763c499a4aee/exec-f464fba1-2743-4804-9a38-7ba61627389c.png",
        "elapsed": 118.0,
    },
    "reduced-palette-text-control-s06-ember-line-entry": {
        "execution_id": "exec-5b7e6843-85b0-4700-95ba-029e1f22d1a4",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-d2bb-7123-ad79-763c499a4aee/exec-5b7e6843-85b0-4700-95ba-029e1f22d1a4.png",
        "elapsed": 54.0,
    },
    "reduced-palette-text-control-s07-impossible-footprints-bell": {
        "execution_id": "exec-3bf7391c-ab0c-4dd5-b3a7-7a97c6628e44",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-f431-77e3-86f2-d4aaaf9cd7c0/exec-3bf7391c-ab0c-4dd5-b3a7-7a97c6628e44.png",
        "elapsed": None,
        "batch": "reduced-palette-text-control-s07-s09-concurrent",
        "batch_wall": 300.467,
    },
    "reduced-palette-text-control-s08-plank-tin-map": {
        "execution_id": "exec-8a89400b-8bf5-491a-a997-d30b60e47ca0",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-f431-77e3-86f2-d4aaaf9cd7c0/exec-8a89400b-8bf5-491a-a997-d30b60e47ca0.png",
        "elapsed": None,
        "batch": "reduced-palette-text-control-s07-s09-concurrent",
        "batch_wall": 300.467,
    },
    "reduced-palette-text-control-s09-deduction-retreat-cut": {
        "execution_id": "exec-f12262d2-a3c7-4be3-9d1e-7edb3c525075",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-f431-77e3-86f2-d4aaaf9cd7c0/exec-f12262d2-a3c7-4be3-9d1e-7edb3c525075.png",
        "elapsed": None,
        "batch": "reduced-palette-text-control-s07-s09-concurrent",
        "batch_wall": 300.467,
    },
    "reduced-palette-text-control-s10-silence-return": {
        "execution_id": "exec-796bc669-b881-44e7-8919-c234c39aaee4",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-f431-77e3-86f2-d4aaaf9cd7c0/exec-796bc669-b881-44e7-8919-c234c39aaee4.png",
        "elapsed": None,
        "batch": "reduced-palette-text-control-s10-s11-concurrent",
        "batch_wall": 158.885,
    },
    "reduced-palette-text-control-s11-farmhouse-reversal": {
        "execution_id": "exec-4b33b9b1-dfa6-46c3-98b6-2f55d9afb0dc",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-f431-77e3-86f2-d4aaaf9cd7c0/exec-4b33b9b1-dfa6-46c3-98b6-2f55d9afb0dc.png",
        "elapsed": None,
        "batch": "reduced-palette-text-control-s10-s11-concurrent",
        "batch_wall": 158.885,
    },
}
KNOWN_INDIVIDUAL_SUM_SECONDS = 568.3
NON_OVERLAP_OBSERVED_ARITHMETIC_SECONDS = 1027.652


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    prompt_document = json.loads(PROMPTS.read_text(encoding="utf-8"))
    sequences = prompt_document["sequences"]
    if len(sequences) != 11 or set(RUNS) != {row["sequence_id"] for row in sequences}:
        raise ValueError("execution table must exactly match the eleven prompt sequences")
    if prompt_document.get("authorized_reference_hashes") not in ([], None):
        raise ValueError("text-only prompt manifest must authorize zero reference hashes")

    records: list[dict[str, Any]] = []
    batches: dict[str, dict[str, Any]] = {}
    for sequence in sequences:
        sequence_id = sequence["sequence_id"]
        run = RUNS[sequence_id]
        if sequence.get("input_references") != []:
            raise ValueError(f"text-only sequence has input references: {sequence_id}")
        output_path = ROOT / sequence["planned_output"]
        global_path = Path(run["global_original"])
        if not output_path.is_file():
            raise ValueError(f"planned output missing: {sequence_id}")
        if not global_path.is_file():
            raise ValueError(f"global original missing: {sequence_id}")
        output_hash = sha256(output_path)
        if sha256(global_path) != output_hash:
            raise ValueError(f"planned output is not an exact global-original copy: {sequence_id}")
        with Image.open(output_path) as image:
            if image.format != "PNG":
                raise ValueError(f"output is not PNG: {sequence_id}")
            width, height = image.size
            image.verify()

        batch_id = run.get("batch")
        if batch_id:
            observation = batches.setdefault(
                batch_id,
                {"timing_batch_id": batch_id, "wall_seconds": run["batch_wall"], "member_sequence_ids": []},
            )
            if observation["wall_seconds"] != run["batch_wall"]:
                raise ValueError(f"inconsistent concurrent batch wall: {batch_id}")
            observation["member_sequence_ids"].append(sequence_id)
        records.append(
            {
                "sequence_id": sequence_id,
                "source_sequence_id": sequence["source_sequence_id"],
                "panel_range": sequence["panel_range"],
                "panel_count": sequence["panel_count"],
                "prompt_text": sequence["prompt_text"],
                "prompt_sha256": sequence["prompt_sha256"],
                "input_references": [],
                "cross_panel_gate_phrases": sequence["cross_panel_gate_phrases"],
                "execution": {
                    "tool_mode": "openai_builtin_imagegen_in_codex",
                    "tool_service_execution_id": run["execution_id"],
                    "tool_service_execution_id_is_provider_request_id": False,
                    "global_original_path": global_path.as_posix(),
                    "global_original_preserved": True,
                    "referenced_image_paths_parameter": "OMITTED",
                    "num_last_images_to_include_parameter": "OMITTED",
                    "observed_tool_wall_seconds": run["elapsed"],
                    "concurrent_batch_id": batch_id,
                    "concurrent_batch_wall_seconds": run.get("batch_wall"),
                    "model": None,
                    "provider": None,
                    "endpoint": None,
                    "provider_request_id": None,
                    "usage": None,
                    "cost_usd": None,
                    "deterministic_seed": None,
                    "unavailable_fields": UNAVAILABLE,
                },
                "output": {
                    "path": sequence["planned_output"],
                    "sha256": output_hash,
                    "width": width,
                    "height": height,
                    "bytes": output_path.stat().st_size,
                },
                "human_review_state": "PENDING",
                "human_review_minutes": None,
                "accepted": False,
                "rights_cleared": False,
                "commercially_cleared": False,
                "exact_production_base": False,
                "generation_reproducible": False,
            }
        )

    known_sum = round(sum(row["execution"]["observed_tool_wall_seconds"] or 0 for row in records), 3)
    if known_sum != KNOWN_INDIVIDUAL_SUM_SECONDS:
        raise ValueError(f"known individual timing sum changed: {known_sum}")
    non_overlap = round(known_sum + sum(batch["wall_seconds"] for batch in batches.values()), 3)
    if non_overlap != NON_OVERLAP_OBSERVED_ARITHMETIC_SECONDS:
        raise ValueError(f"non-overlap observed arithmetic changed: {non_overlap}")

    document = {
        "record_type": "CH05CompleteChapterReducedPaletteTextControlExecutionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-reduced-palette-text-control-executions-r1",
        "state": "EXECUTED_UNACCEPTED_PENDING_HUMAN_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "input_prompt_manifest": {
            "path": PROMPTS.relative_to(ROOT).as_posix(),
            "sha256": sha256(PROMPTS),
        },
        "summary": {
            "sequence_outputs": len(records),
            "comic_panel_plans_requested": sum(row["panel_count"] for row in records),
            "planned_comic_panel_crops": 50,
            "authorized_reference_uses": 0,
            "reference_uploads": 0,
            "per_output_wall_seconds_available": sum(row["execution"]["observed_tool_wall_seconds"] is not None for row in records),
            "known_individual_tool_wall_seconds_sum": known_sum,
            "concurrent_batch_count": len(batches),
            "non_overlap_observed_arithmetic_seconds": non_overlap,
            "actual_end_to_end_wall_seconds": None,
            "direct_paid_provider_api_calls": 0,
            "cost_total_usd": None,
            "human_reviewed_outputs": 0,
            "accepted_outputs": 0,
            "rights_cleared_outputs": 0,
            "commercially_cleared_outputs": 0,
            "exact_production_base_outputs": 0,
        },
        "timing_batches": list(batches.values()),
        "timing_honesty_boundary": (
            "Six individually observed calls total 568.3 seconds. The S07-S09 concurrent batch observed 300.467 seconds and the "
            "S10-S11 concurrent batch observed 158.885 seconds; their member elapsed values remain null. Adding those independent "
            "observations gives 1027.652 seconds of non-overlap observed arithmetic only. Actual end-to-end wall time remains null "
            "because parallel caller lanes lacked one shared stopwatch."
        ),
        "records": records,
        "limitations": [
            "The built-in tool exposed no model, provider, endpoint, provider request ID, usage, monetary cost, or deterministic seed.",
            "Codex tool-service execution IDs are provenance aids only and are not provider request IDs.",
            "S07-S09 and S10-S11 have concurrent batch walls and null member elapsed times; no member times are inferred.",
            "The 1027.652-second figure is non-overlap observed arithmetic, not actual end-to-end wall time.",
            "Prompt-gate presence does not prove pixel compliance or style-hypothesis success.",
            "Exact prompts, execution IDs, and output hashes do not make stochastic generation reproducible.",
            "Outputs remain pending human review, unaccepted, rights-uncleared, commercially uncleared, and not exact production bases.",
        ],
        "boundary": {
            "permitted_product": "openai_builtin_imagegen",
            "reference_uploads": 0,
            "referenced_image_paths_passed": 0,
            "conversation_images_included": 0,
            "direct_paid_provider_api_calls": 0,
            "bfl_calls": 0,
            "new_upload_classes": 0,
            "real_person_or_child_material": 0,
            "accepted": 0,
            "rights_cleared": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), **document["summary"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
