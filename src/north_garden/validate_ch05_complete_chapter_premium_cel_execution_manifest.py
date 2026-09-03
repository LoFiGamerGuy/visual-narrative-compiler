"""Validate complete CH05 premium-cel built-in ImageGen execution evidence."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-execution-manifest-r1.json"
PROMPTS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-prompt-manifest-r1.json"
UNAVAILABLE = ["model", "endpoint", "provider_request_id", "usage", "cost_usd", "deterministic_seed"]
REFERENCE_DISTRIBUTION = [2, 2, 2, 2, 2, 2, 2, 3, 2, 2, 2]
ALLOWED_REFERENCE_HASHES = {
    "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d",
    "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a",
    "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb",
}
EXPECTED_EXECUTION_IDS = [
    "exec-d04ed89c-e73c-45b5-aed2-4b590aa68638",
    "exec-d89a1ca9-ef46-41a2-a0ed-56f6fd7fe90d",
    "exec-3bbcf116-57a4-4568-a55f-c57d878f1b85",
    "exec-bacf383e-83c6-49e5-9d5c-aaf769cad654",
    "exec-a569d74a-9056-477c-bb26-6bd92862cff9",
    "exec-b0654532-469f-49ee-b31b-be6e62393451",
    "exec-fbbdbfeb-3ee2-4539-88be-340da3965a26",
    "exec-bf2b775d-f617-45f7-9c92-0f6668d3b17a",
    "exec-a6b8bec4-9af9-41c7-a169-48b442e029bb",
    "exec-77032c6c-a2e8-4dd8-accc-75f97322063b",
    "exec-6b038c9d-8fd4-42a7-b5fe-c89983b96e7f",
]
EXPECTED_BATCHES = [
    ("pc01-parallel", 239.1, ["premium-cel-s01-opening-departure", "premium-cel-s02-runnel-marker-trail"]),
    ("pc02-parallel", 205.6, ["premium-cel-s03-listening-twine-ridge", "premium-cel-s04-mill-reveal-bridge-warning"]),
    ("pc03-parallel", 218.2, ["premium-cel-s05-creek-marker-drum", "premium-cel-s06-ember-line-entry"]),
    ("pc04-parallel", 230.6, ["premium-cel-s07-impossible-footprints-bell", "premium-cel-s08-plank-tin-map"]),
    ("pc05-parallel", 221.7, ["premium-cel-s09-deduction-retreat-cut", "premium-cel-s10-silence-return"]),
    ("pc06-single", 118.8, ["premium-cel-s11-farmhouse-reversal"]),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ignored_untracked(relative: str) -> bool:
    ignored = subprocess.run(["git", "check-ignore", "--quiet", "--", relative], cwd=ROOT).returncode == 0
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", relative],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0
    return ignored and not tracked


def validate(document: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    rows = document.get("records", [])
    prompt_document = json.loads(PROMPTS.read_text(encoding="utf-8"))
    prompts = prompt_document["sequences"]

    check(document.get("record_type") == "CH05CompleteChapterPremiumCelExecutionManifest", "record_type")
    check(document.get("schema_version") == "1.0", "schema_version")
    check(document.get("record_id") == "ng-ch05-complete-chapter-premium-cel-executions-r1", "record_id")
    check(document.get("state") == "EXECUTED_UNACCEPTED_PENDING_HUMAN_REVIEW", "state")
    check(document.get("medium") == "comic", "medium")
    check(
        document.get("planning_structure") == "ComicPanelPlan"
        and document.get("animation_shot_plan") is None
        and document.get("e_conte") is None,
        "planning boundary",
    )
    check(
        document.get("input_prompt_manifest")
        == {"path": PROMPTS.relative_to(ROOT).as_posix(), "sha256": sha256(PROMPTS)},
        "prompt manifest binding",
    )
    execution_ids = [row.get("execution", {}).get("tool_service_execution_id") for row in rows]
    check(execution_ids == EXPECTED_EXECUTION_IDS and len(set(execution_ids)) == 11, "records/execution IDs")
    coverage = [number for row in rows for number in range(row.get("panel_range", [0, -1])[0], row.get("panel_range", [0, -1])[1] + 1)]
    check(coverage == list(range(1, 51)), "ordered panel coverage")
    check([row.get("panel_count") for row in rows] == [5, 4, 5, 5, 5, 5, 5, 5, 5, 3, 3], "panel counts")
    check([len(row.get("input_references", [])) for row in rows] == REFERENCE_DISTRIBUTION, "reference distribution")
    check(sum(len(row.get("cross_panel_gate_phrases", [])) for row in rows) == 15, "cross-panel gate bindings")

    for row, prompt in zip(rows, prompts):
        sequence_id = row.get("sequence_id")
        for key in (
            "sequence_id",
            "source_sequence_id",
            "panel_range",
            "panel_count",
            "prompt_text",
            "prompt_sha256",
            "input_references",
            "cross_panel_gate_phrases",
        ):
            check(row.get(key) == prompt.get(key), f"prompt parity {sequence_id}:{key}")
        check(row.get("output", {}).get("path") == prompt.get("planned_output"), f"output parity {sequence_id}")
        check(hashlib.sha256(row.get("prompt_text", "").encode("utf-8")).hexdigest() == row.get("prompt_sha256"), f"prompt hash {sequence_id}")
        for reference in row.get("input_references", []):
            check(reference.get("sha256") in ALLOWED_REFERENCE_HASHES, f"reference allowlist {sequence_id}")
            if verify_files:
                reference_path = ROOT / reference.get("path", "")
                check(
                    reference_path.is_file() and sha256(reference_path) == reference.get("sha256"),
                    f"reference bytes/hash {sequence_id}",
                )
        execution = row.get("execution", {})
        check(execution.get("tool_mode") == "openai_builtin_imagegen_in_codex", f"tool mode {sequence_id}")
        check(execution.get("unavailable_fields") == UNAVAILABLE and all(execution.get(key) is None for key in UNAVAILABLE), f"unavailable metadata {sequence_id}")
        check(execution.get("tool_service_execution_id_is_provider_request_id") is False, f"execution/provider ID distinction {sequence_id}")
        check(
            row.get("human_review_state") == "PENDING"
            and row.get("human_review_minutes") is None
            and all(row.get(key) is False for key in ("accepted", "commercially_cleared", "exact_production_base", "generation_reproducible")),
            f"review boundary {sequence_id}",
        )
        if verify_files:
            output = row.get("output", {})
            relative = output.get("path", "")
            path = ROOT / relative
            check(path.is_file(), f"output missing {sequence_id}")
            if path.is_file():
                check(sha256(path) == output.get("sha256") and path.stat().st_size == output.get("bytes"), f"output bytes/hash {sequence_id}")
                with Image.open(path) as image:
                    check(image.format == "PNG" and [image.width, image.height] == [output.get("width"), output.get("height")], f"output decode/dimensions {sequence_id}")
                check(ignored_untracked(relative), f"output ignored/untracked {sequence_id}")

    expected_batch_rows = [
        {"timing_batch_id": batch_id, "wall_seconds": wall, "member_sequence_ids": members}
        for batch_id, wall, members in EXPECTED_BATCHES
    ]
    check(document.get("timing_batches") == expected_batch_rows, "timing batch partition")
    batch_by_id = {batch_id: (wall, members) for batch_id, wall, members in EXPECTED_BATCHES}
    for row in rows:
        execution = row.get("execution", {})
        batch = batch_by_id.get(execution.get("timing_batch_id"))
        check(batch is not None, f"record batch ID {row.get('sequence_id')}")
        if batch is not None:
            check(row.get("sequence_id") in batch[1], f"record batch membership {row.get('sequence_id')}")
            check(execution.get("parallel_batch_wall_seconds") == batch[0], f"record batch wall {row.get('sequence_id')}")
    check([row.get("execution", {}).get("elapsed_seconds") for row in rows] == [None] * 10 + [118.8], "individual timing availability")

    summary = document.get("summary", {})
    check(
        (
            summary.get("sequence_outputs"),
            summary.get("comic_panel_plans_requested"),
            summary.get("planned_comic_panel_crops"),
            summary.get("authorized_reference_uses"),
            summary.get("unique_timing_batches"),
            summary.get("overlap_adjusted_tool_call_wall_seconds"),
            summary.get("per_output_elapsed_seconds_available"),
        )
        == (11, 50, 50, 23, 6, 1234.0, 1),
        "summary counts/timing",
    )
    check(
        summary.get("direct_paid_provider_api_calls") == 0
        and summary.get("paid_spend_usd") == 0.0
        and all(summary.get(key) == 0 for key in ("human_reviewed_outputs", "accepted_outputs", "commercially_cleared_outputs", "exact_production_base_outputs")),
        "summary spend/review boundary",
    )
    check(
        summary.get("timing_scope")
        == "Codex ImageGen tool-call wall at 0.1-second precision; includes any queue, generation, and transfer time exposed to the caller.",
        "timing scope",
    )
    check(
        document.get("boundary")
        == {
            "permitted_product": "openai_builtin_imagegen",
            "direct_paid_provider_api_calls": 0,
            "bfl_calls": 0,
            "new_upload_classes": 0,
            "real_person_or_child_material": 0,
        },
        "boundary",
    )
    return errors


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "ACCEPTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value["input_prompt_manifest"].__setitem__("sha256", "0" * 64),
        lambda value: value["records"].pop(),
        lambda value: value["records"][0].__setitem__("prompt_text", "tampered"),
        lambda value: value["records"][0]["execution"].__setitem__("tool_service_execution_id", value["records"][1]["execution"]["tool_service_execution_id"]),
        lambda value: value["records"][0]["execution"].__setitem__("tool_service_execution_id", "exec-00000000-0000-0000-0000-000000000000"),
        lambda value: value["records"][0]["execution"].__setitem__("model", "invented"),
        lambda value: value["records"][0]["execution"].__setitem__("elapsed_seconds", 239.1),
        lambda value: value["records"][0].__setitem__("accepted", True),
        lambda value: value["timing_batches"][0]["member_sequence_ids"].pop(),
        lambda value: value["records"][0]["execution"].__setitem__("parallel_batch_wall_seconds", 1.0),
        lambda value: value["summary"].__setitem__("planned_comic_panel_crops", 49),
        lambda value: value["summary"].__setitem__("overlap_adjusted_tool_call_wall_seconds", 2468.0),
        lambda value: value["summary"].__setitem__("paid_spend_usd", 1.0),
        lambda value: value["boundary"].__setitem__("bfl_calls", 1),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
        mutation(candidate)
        caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = validate(document)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(document)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
                "records": len(document.get("records", [])),
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
