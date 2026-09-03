"""Compile exact built-in ImageGen execution evidence for CH05 flat-graphic gouache r1."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-prompt-manifest-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-execution-manifest-r1.json"
UNAVAILABLE = ["model", "endpoint", "provider_request_id", "usage", "cost_usd", "deterministic_seed"]
RUNS: dict[str, dict[str, Any]] = {
    "flat-graphic-gouache-s01-opening-departure": {
        "execution_id": "exec-64702d63-4a95-495c-ba62-6e5a7bc1fbae",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a05d7c-0ac3-7872-8fa8-3fb9c14f6eaa/exec-64702d63-4a95-495c-ba62-6e5a7bc1fbae.png",
        "observed_tool_wall_seconds": 120.9,
    },
    "flat-graphic-gouache-s02-runnel-marker-trail": {
        "execution_id": "exec-1463d1ca-8497-4478-b714-8d73561c23ff",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a05d7c-0ac3-7872-8fa8-3fb9c14f6eaa/exec-1463d1ca-8497-4478-b714-8d73561c23ff.png",
        "observed_tool_wall_seconds": 107.0,
    },
    "flat-graphic-gouache-s03-listening-twine-ridge": {
        "execution_id": "exec-9eafd592-2a2b-4593-bbc1-6b18e9006c83",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a05d7c-0ac3-7872-8fa8-3fb9c14f6eaa/exec-9eafd592-2a2b-4593-bbc1-6b18e9006c83.png",
        "observed_tool_wall_seconds": 119.0,
    },
    "flat-graphic-gouache-s04-mill-reveal-bridge-warning": {
        "execution_id": "exec-a6e3571c-43da-485f-901c-265d43d96785",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-b225-7882-8dd1-4bd93e37d750/exec-a6e3571c-43da-485f-901c-265d43d96785.png",
        "observed_tool_wall_seconds": 125.761,
    },
    "flat-graphic-gouache-s05-creek-marker-drum": {
        "execution_id": "exec-6901b1f7-389c-43ef-8662-0819950c494f",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-b225-7882-8dd1-4bd93e37d750/exec-6901b1f7-389c-43ef-8662-0819950c494f.png",
        "observed_tool_wall_seconds": 125.313,
    },
    "flat-graphic-gouache-s06-ember-line-entry": {
        "execution_id": "exec-44085b1e-4484-483d-9c19-f1e48b749a9a",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-b225-7882-8dd1-4bd93e37d750/exec-44085b1e-4484-483d-9c19-f1e48b749a9a.png",
        "observed_tool_wall_seconds": 120.947,
    },
    "flat-graphic-gouache-s07-impossible-footprints-bell": {
        "execution_id": "exec-fa60a531-20f7-480d-bbb7-6641f0362d01",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-d2bb-7123-ad79-763c499a4aee/exec-fa60a531-20f7-480d-bbb7-6641f0362d01.png",
        "observed_tool_wall_seconds": 123.0,
    },
    "flat-graphic-gouache-s08-plank-tin-map": {
        "execution_id": "exec-a3b74540-8a04-4f48-aeee-414a35fabffc",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-d2bb-7123-ad79-763c499a4aee/exec-a3b74540-8a04-4f48-aeee-414a35fabffc.png",
        "observed_tool_wall_seconds": 105.0,
    },
    "flat-graphic-gouache-s09-deduction-retreat-cut": {
        "execution_id": "exec-8dc1318d-23b3-478d-9736-2ae5de3d40be",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-d2bb-7123-ad79-763c499a4aee/exec-8dc1318d-23b3-478d-9736-2ae5de3d40be.png",
        "observed_tool_wall_seconds": 117.0,
    },
    "flat-graphic-gouache-s10-silence-return": {
        "execution_id": "exec-d410ea4d-c817-4365-9539-357734ef9454",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-f431-77e3-86f2-d4aaaf9cd7c0/exec-d410ea4d-c817-4365-9539-357734ef9454.png",
        "observed_tool_wall_seconds": None,
        "concurrent_batch_id": "flat-graphic-gouache-s10-s11-concurrent",
    },
    "flat-graphic-gouache-s11-farmhouse-reversal": {
        "execution_id": "exec-c71a73c6-ed01-4941-b426-b4e576a42f95",
        "global_original": "C:/Users/gosne/.codex/generated_images/01a06436-f431-77e3-86f2-d4aaaf9cd7c0/exec-c71a73c6-ed01-4941-b426-b4e576a42f95.png",
        "observed_tool_wall_seconds": None,
        "concurrent_batch_id": "flat-graphic-gouache-s10-s11-concurrent",
    },
}
CONCURRENT_PAIR_WALL_SECONDS = 227.068
KNOWN_PER_OUTPUT_SUM_SECONDS = 1063.921
NON_OVERLAP_ADJUSTED_OBSERVED_TOTAL_SECONDS = 1290.989


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    prompt_document = json.loads(PROMPTS.read_text(encoding="utf-8"))
    sequences = prompt_document["sequences"]
    if set(RUNS) != {row["sequence_id"] for row in sequences} or len(sequences) != 11:
        raise ValueError("execution table must exactly match the eleven prompt sequences")

    records: list[dict[str, Any]] = []
    for sequence in sequences:
        sequence_id = sequence["sequence_id"]
        run = RUNS[sequence_id]
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
        records.append(
            {
                "sequence_id": sequence_id,
                "source_sequence_id": sequence["source_sequence_id"],
                "panel_range": sequence["panel_range"],
                "panel_count": sequence["panel_count"],
                "prompt_text": sequence["prompt_text"],
                "prompt_sha256": sequence["prompt_sha256"],
                "input_references": sequence["input_references"],
                "cross_panel_gate_phrases": sequence["cross_panel_gate_phrases"],
                "execution": {
                    "tool_mode": "openai_builtin_imagegen_in_codex",
                    "tool_service_execution_id": run["execution_id"],
                    "tool_service_execution_id_is_provider_request_id": False,
                    "global_original_path": global_path.as_posix(),
                    "global_original_preserved": True,
                    "observed_tool_wall_seconds": run["observed_tool_wall_seconds"],
                    "concurrent_batch_id": run.get("concurrent_batch_id"),
                    "concurrent_batch_wall_seconds": (
                        CONCURRENT_PAIR_WALL_SECONDS if run.get("concurrent_batch_id") else None
                    ),
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
                    "sha256": output_hash,
                    "width": width,
                    "height": height,
                    "bytes": output_path.stat().st_size,
                },
                "human_review_state": "PENDING",
                "human_review_minutes": None,
                "accepted": False,
                "commercially_cleared": False,
                "exact_production_base": False,
                "generation_reproducible": False,
            }
        )

    known_sum = round(
        sum(row["execution"]["observed_tool_wall_seconds"] or 0 for row in records), 3
    )
    if known_sum != KNOWN_PER_OUTPUT_SUM_SECONDS:
        raise ValueError(f"known per-output timing sum changed: {known_sum}")
    non_overlap_total = round(known_sum + CONCURRENT_PAIR_WALL_SECONDS, 3)
    if non_overlap_total != NON_OVERLAP_ADJUSTED_OBSERVED_TOTAL_SECONDS:
        raise ValueError(f"non-overlap-adjusted arithmetic changed: {non_overlap_total}")

    document = {
        "record_type": "CH05CompleteChapterFlatGraphicGouacheExecutionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-flat-graphic-gouache-executions-r1",
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
            "authorized_reference_uses": sum(len(row["input_references"]) for row in records),
            "per_output_wall_seconds_available": sum(
                row["execution"]["observed_tool_wall_seconds"] is not None for row in records
            ),
            "known_per_output_tool_wall_seconds_sum": known_sum,
            "concurrent_pair_batch_wall_seconds": CONCURRENT_PAIR_WALL_SECONDS,
            "non_overlap_adjusted_observed_total_seconds": non_overlap_total,
            "actual_end_to_end_wall_seconds": None,
            "direct_paid_provider_api_calls": 0,
            "cost_total_usd": None,
            "human_reviewed_outputs": 0,
            "accepted_outputs": 0,
            "commercially_cleared_outputs": 0,
            "exact_production_base_outputs": 0,
        },
        "timing_observations": {
            "concurrent_pair": {
                "timing_batch_id": "flat-graphic-gouache-s10-s11-concurrent",
                "member_sequence_ids": [
                    "flat-graphic-gouache-s10-silence-return",
                    "flat-graphic-gouache-s11-farmhouse-reversal",
                ],
                "batch_wall_seconds": CONCURRENT_PAIR_WALL_SECONDS,
                "member_elapsed_seconds": [None, None],
            },
            "honesty_boundary": (
                "S03-S11 ran across parallel agent caller lanes without a shared stopwatch. Actual overlap-adjusted end-to-end wall "
                "time is unavailable and remains null. The non-overlap-adjusted observed total is only the arithmetic sum of nine "
                "known per-output walls plus the separately observed S10/S11 concurrent-pair batch wall; it is not a batch-adjusted "
                "or actual end-to-end duration."
            ),
            "preflight_arithmetic_correction": (
                "The initially supplied aggregate values 1064.921 and 1291.989 seconds were each 1.000 second above the arithmetic "
                "sum of the unchanged exact observations. This manifest records the recomputed 1063.921 and 1290.989-second values; "
                "the incorrect aggregates are context only and are not evidence claims."
            ),
        },
        "records": records,
        "limitations": [
            "The built-in tool exposed no model, endpoint, provider request ID, usage, monetary cost, or deterministic seed.",
            "Codex tool-service execution IDs are provenance aids only and are not provider request IDs.",
            "S03-S11 used parallel caller lanes without one shared stopwatch; actual overlap-adjusted end-to-end wall is unavailable.",
            "S10/S11 expose one concurrent-pair batch wall and null member elapsed times; no member times are inferred.",
            "The 1290.989-second figure is explicitly non-overlap-adjusted arithmetic, not an actual or batch-adjusted total.",
            "Prompt-gate presence does not prove pixel compliance or style-hypothesis success.",
            "Exact prompts, references, execution IDs, and output hashes do not make stochastic generation reproducible.",
            "Outputs remain pending human review, unaccepted, commercially uncleared, and not exact production bases.",
        ],
        "boundary": {
            "permitted_product": "openai_builtin_imagegen",
            "direct_paid_provider_api_calls": 0,
            "bfl_calls": 0,
            "new_upload_classes": 0,
            "real_person_or_child_material": 0,
            "accepted": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
    }
    OUTPUT.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output": OUTPUT.relative_to(ROOT).as_posix(),
                "sha256": sha256(OUTPUT),
                **document["summary"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
