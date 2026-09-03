"""Fail-closed validation for a CH05 complete-chapter route execution pair."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_RANGES = [
    [1, 5],
    [6, 9],
    [10, 14],
    [15, 19],
    [20, 24],
    [25, 29],
    [30, 34],
    [35, 39],
    [40, 44],
    [45, 47],
    [48, 50],
]
EXPECTED_SOURCE_SEQUENCE_IDS = [
    "s01-opening-departure",
    "s02-runnel-marker-trail",
    "s03-listening-twine-ridge",
    "s04-mill-reveal-bridge-warning",
    "s05-creek-marker-drum",
    "s06-ember-line-entry",
    "s07-impossible-footprints-bell",
    "s08-plank-tin-map",
    "s09-deduction-retreat-cut",
    "s10-silence-return",
    "s11-farmhouse-reversal",
]
UNAVAILABLE_FIELDS = [
    "model",
    "endpoint",
    "provider_request_id",
    "usage",
    "cost_usd",
    "deterministic_seed",
]
TEXT_ONLY_UNAVAILABLE_FIELDS = [
    "model",
    "provider",
    "endpoint",
    "provider_request_id",
    "usage",
    "cost_usd",
    "deterministic_seed",
]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXECUTION_ID_RE = re.compile(r"^exec-[0-9a-f-]{36}$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_cli_path(value: str) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else ROOT / path).resolve()


def is_safe_experiment_output(relative: Any) -> bool:
    if not isinstance(relative, str) or "\\" in relative:
        return False
    pure = Path(relative)
    if pure.suffix.lower() != ".png" or pure.is_absolute() or ".." in pure.parts:
        return False
    try:
        (ROOT / pure).resolve().relative_to(
            (ROOT / "experiments/review-packets").resolve()
        )
    except ValueError:
        return False
    return relative.startswith("experiments/review-packets/")


def ignored_untracked(relative: str) -> bool:
    ignored = (
        subprocess.run(
            ["git", "check-ignore", "--quiet", "--", relative],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )
    tracked = (
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )
    return ignored and not tracked


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def unique_strings(values: Any, expected_count: int | None = None) -> bool:
    if not isinstance(values, list) or not all(
        isinstance(value, str) for value in values
    ):
        return False
    if expected_count is None:
        return len(set(values)) == len(values)
    return len(values) == expected_count and len(set(values)) == expected_count


def validate(
    prompt: dict[str, Any],
    execution: dict[str, Any],
    prompt_path: Path,
    verify_files: bool = True,
) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)

    prompt_rows = prompt.get("sequences", [])
    execution_rows = execution.get("records", [])
    text_only_route = (
        prompt.get("record_type")
        == "CH05CompleteChapterReducedPaletteTextControlPromptManifest"
        and execution.get("record_type")
        == "CH05CompleteChapterReducedPaletteTextControlExecutionManifest"
    )
    observation_timing = isinstance(execution.get("timing_observations"), dict)
    distributed_batch_timing = isinstance(
        execution.get("timing_batches"), list
    ) and isinstance(execution.get("timing_honesty_boundary"), str)
    standard_timing = (
        isinstance(execution.get("timing_batches"), list)
        and not distributed_batch_timing
    )
    distributed_timing = observation_timing or distributed_batch_timing
    check(
        standard_timing != distributed_timing,
        "exactly one supported timing schema",
    )
    check(
        isinstance(prompt.get("record_type"), str)
        and prompt["record_type"].startswith("CH05CompleteChapter")
        and prompt["record_type"].endswith("PromptManifest"),
        "prompt record_type",
    )
    check(
        isinstance(execution.get("record_type"), str)
        and execution["record_type"].startswith("CH05CompleteChapter")
        and execution["record_type"].endswith("ExecutionManifest"),
        "execution record_type",
    )
    check(prompt.get("schema_version") == "1.0", "prompt schema_version")
    check(execution.get("schema_version") == "1.0", "execution schema_version")
    check(prompt.get("state") == "EXACT_PROMPTS_COMPILED_NOT_EXECUTED", "prompt state")
    check(
        execution.get("state") == "EXECUTED_UNACCEPTED_PENDING_HUMAN_REVIEW",
        "execution state",
    )
    for label, document in (("prompt", prompt), ("execution", execution)):
        check(document.get("medium") == "comic", f"{label} medium")
        check(
            document.get("planning_structure") == "ComicPanelPlan", f"{label} planning"
        )
        check(
            document.get("animation_shot_plan") is None,
            f"{label} AnimationShotPlan boundary",
        )
        check(document.get("e_conte") is None, f"{label} E-Conte boundary")

    try:
        prompt_relative = prompt_path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        prompt_relative = ""
        errors.append("prompt manifest path outside repository")
    check(
        execution.get("input_prompt_manifest")
        == {"path": prompt_relative, "sha256": sha256(prompt_path)},
        "prompt manifest binding",
    )
    check(
        len(prompt_rows) == 11 and len(execution_rows) == 11,
        "exact sequence denominator",
    )
    check(
        [row.get("panel_range") for row in prompt_rows] == EXPECTED_RANGES,
        "prompt ordered ranges",
    )
    check(
        [row.get("panel_range") for row in execution_rows] == EXPECTED_RANGES,
        "execution ordered ranges",
    )
    check(
        [row.get("source_sequence_id") for row in prompt_rows]
        == EXPECTED_SOURCE_SEQUENCE_IDS,
        "prompt source sequence order",
    )
    check(
        [row.get("source_sequence_id") for row in execution_rows]
        == EXPECTED_SOURCE_SEQUENCE_IDS,
        "execution source sequence order",
    )
    check(
        len({row.get("sequence_id") for row in prompt_rows}) == 11
        and [row.get("sequence_id") for row in execution_rows]
        == [row.get("sequence_id") for row in prompt_rows],
        "sequence IDs/order",
    )

    authorized_hashes = prompt.get("authorized_reference_hashes", [])
    if text_only_route:
        check(authorized_hashes == [], "text-only authorized reference hash set")
    else:
        check(
            isinstance(authorized_hashes, list)
            and bool(authorized_hashes)
            and all(
                isinstance(value, str) and SHA256_RE.fullmatch(value)
                for value in authorized_hashes
            ),
            "authorized reference hash set",
        )
    check(unique_strings(authorized_hashes), "unique authorized reference hashes")
    coverage = prompt.get("coverage", {})
    check(
        coverage.get("sequence_requests") == 11
        and coverage.get("comic_panel_plans") == 50,
        "prompt coverage summary",
    )

    output_paths: list[Any] = []
    execution_ids: list[Any] = []
    reference_use_count = 0
    elapsed_available = 0
    observed_per_output_walls: list[Decimal] = []
    concurrent_sequence_ids: list[Any] = []
    for index, (request, record) in enumerate(zip(prompt_rows, execution_rows)):
        sequence = request.get("sequence_id", f"index-{index}")
        start, end = EXPECTED_RANGES[index]
        expected_count = end - start + 1
        check(
            request.get("panel_count") == expected_count
            and record.get("panel_count") == expected_count,
            f"panel count {sequence}",
        )
        for key in (
            "sequence_id",
            "source_sequence_id",
            "panel_range",
            "panel_count",
            "prompt_text",
            "prompt_sha256",
            "input_references",
        ):
            check(
                record.get(key) == request.get(key), f"prompt parity {sequence}:{key}"
            )
        if "cross_panel_gate_phrases" in record:
            check(
                record.get("cross_panel_gate_phrases")
                == request.get("cross_panel_gate_phrases", []),
                f"gate parity {sequence}",
            )
        prompt_text = request.get("prompt_text")
        check(
            isinstance(prompt_text, str)
            and hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
            == request.get("prompt_sha256"),
            f"prompt hash {sequence}",
        )
        check(
            request.get("prompt_lines")
            == (prompt_text.splitlines() if isinstance(prompt_text, str) else []),
            f"prompt lines {sequence}",
        )
        references = request.get("input_references", [])
        reference_use_count += len(references)
        for reference in references:
            ref_path = reference.get("path", "")
            check(
                reference.get("sha256") in authorized_hashes,
                f"authorized reference {sequence}:{ref_path}",
            )
            if verify_files:
                path = ROOT / ref_path
                check(path.is_file(), f"reference exists {sequence}:{ref_path}")
                if path.is_file():
                    check(
                        sha256(path) == reference.get("sha256"),
                        f"reference hash {sequence}:{ref_path}",
                    )

        check(
            request.get("planned_output") == record.get("output", {}).get("path"),
            f"planned output binding {sequence}",
        )
        check(
            request.get("execution") is None
            and request.get("output") is None
            and request.get("human_review_state") == "PENDING"
            and request.get("accepted") is False,
            f"prompt pre-execution boundary {sequence}",
        )
        output = record.get("output", {})
        output_path = output.get("path")
        output_paths.append(output_path)
        check(is_safe_experiment_output(output_path), f"safe output path {sequence}")
        check(
            isinstance(output.get("sha256"), str)
            and SHA256_RE.fullmatch(output["sha256"]),
            f"output hash syntax {sequence}",
        )
        check(
            isinstance(output.get("width"), int)
            and not isinstance(output.get("width"), bool)
            and output["width"] > 0
            and isinstance(output.get("height"), int)
            and not isinstance(output.get("height"), bool)
            and output["height"] > 0
            and isinstance(output.get("bytes"), int)
            and not isinstance(output.get("bytes"), bool)
            and output["bytes"] > 0,
            f"output numeric metadata {sequence}",
        )
        if verify_files and is_safe_experiment_output(output_path):
            path = ROOT / output_path
            check(path.is_file(), f"output exists {sequence}")
            if path.is_file():
                check(
                    sha256(path) == output.get("sha256"),
                    f"output hash {sequence}",
                )
                check(
                    path.stat().st_size == output.get("bytes"),
                    f"output bytes {sequence}",
                )
                try:
                    with Image.open(path) as image:
                        image.verify()
                    with Image.open(path) as image:
                        check(image.format == "PNG", f"output format {sequence}")
                        check(
                            [image.width, image.height]
                            == [output.get("width"), output.get("height")],
                            f"output dimensions {sequence}",
                        )
                except (OSError, SyntaxError, ValueError) as exc:
                    errors.append(f"output decode {sequence}: {type(exc).__name__}")
                check(
                    ignored_untracked(output_path),
                    f"output ignored/untracked {sequence}",
                )

        tool = record.get("execution", {})
        execution_ids.append(tool.get("tool_service_execution_id"))
        check(
            tool.get("tool_mode") == "openai_builtin_imagegen_in_codex",
            f"tool mode {sequence}",
        )
        check(
            isinstance(tool.get("tool_service_execution_id"), str)
            and EXECUTION_ID_RE.fullmatch(tool["tool_service_execution_id"]),
            f"tool execution ID {sequence}",
        )
        check(
            tool.get("tool_service_execution_id_is_provider_request_id") is False,
            f"provider ID distinction {sequence}",
        )
        expected_unavailable_fields = (
            TEXT_ONLY_UNAVAILABLE_FIELDS if text_only_route else UNAVAILABLE_FIELDS
        )
        check(
            tool.get("unavailable_fields") == expected_unavailable_fields
            and all(tool.get(field) is None for field in expected_unavailable_fields),
            f"unavailable metadata honesty {sequence}",
        )
        if text_only_route:
            check(references == [], f"text-only zero references {sequence}")
            check(
                tool.get("referenced_image_paths_parameter") == "OMITTED"
                and tool.get("num_last_images_to_include_parameter") == "OMITTED",
                f"text-only omitted image parameters {sequence}",
            )
        if standard_timing:
            elapsed = tool.get("elapsed_seconds")
            check(
                elapsed is None or (is_number(elapsed) and elapsed > 0),
                f"elapsed metadata {sequence}",
            )
            elapsed_available += elapsed is not None
            check(
                "observed_tool_wall_seconds" not in tool
                and "concurrent_batch_id" not in tool
                and "concurrent_batch_wall_seconds" not in tool,
                f"standard timing field separation {sequence}",
            )
        elif distributed_timing:
            observed = tool.get("observed_tool_wall_seconds")
            concurrent_id = tool.get("concurrent_batch_id")
            concurrent_wall = tool.get("concurrent_batch_wall_seconds")
            check(
                "elapsed_seconds" not in tool
                and "timing_batch_id" not in tool
                and "parallel_batch_wall_seconds" not in tool,
                f"distributed timing field separation {sequence}",
            )
            check(
                tool.get("global_original_preserved") is True
                and isinstance(tool.get("global_original_path"), str)
                and bool(tool["global_original_path"]),
                f"global original provenance {sequence}",
            )
            if observed is not None:
                check(
                    is_number(observed)
                    and observed > 0
                    and concurrent_id is None
                    and concurrent_wall is None,
                    f"known per-output timing {sequence}",
                )
                if is_number(observed) and observed > 0:
                    observed_per_output_walls.append(Decimal(str(observed)))
            else:
                check(
                    isinstance(concurrent_id, str)
                    and bool(concurrent_id)
                    and is_number(concurrent_wall)
                    and concurrent_wall > 0,
                    f"concurrent timing {sequence}",
                )
                concurrent_sequence_ids.append(sequence)
            if verify_files and isinstance(tool.get("global_original_path"), str):
                global_path = Path(tool["global_original_path"])
                check(global_path.is_file(), f"global original exists {sequence}")
                if global_path.is_file():
                    check(
                        sha256(global_path) == output.get("sha256")
                        and global_path.stat().st_size == output.get("bytes"),
                        f"global original binding {sequence}",
                    )
        check(
            record.get("human_review_state") == "PENDING"
            and record.get("human_review_minutes") is None
            and all(
                record.get(field) is False
                for field in (
                    "accepted",
                    *(("rights_cleared",) if text_only_route else ()),
                    "commercially_cleared",
                    "exact_production_base",
                    "generation_reproducible",
                )
            ),
            f"no review/rights promotion {sequence}",
        )

    check(unique_strings(output_paths, 11), "unique output paths")
    check(unique_strings(execution_ids, 11), "unique tool execution IDs")
    check(
        sum(row.get("panel_count", 0) for row in prompt_rows) == 50, "prompt panel sum"
    )
    check(
        sum(row.get("panel_count", 0) for row in execution_rows) == 50,
        "execution panel sum",
    )

    summary = execution.get("summary", {})
    check(summary.get("sequence_outputs") == 11, "summary outputs")
    check(summary.get("comic_panel_plans_requested") == 50, "summary panels")
    if "planned_comic_panel_crops" in summary:
        check(summary.get("planned_comic_panel_crops") == 50, "summary planned crops")
    check(
        summary.get("authorized_reference_uses") == reference_use_count,
        "summary references",
    )
    if text_only_route:
        check(
            reference_use_count == 0 and summary.get("reference_uploads") == 0,
            "text-only summary zero references/uploads",
        )
    if standard_timing:
        batches = execution.get("timing_batches", [])
        batch_ids = [batch.get("timing_batch_id") for batch in batches]
        check(bool(batches) and unique_strings(batch_ids), "timing batch IDs")
        members: list[Any] = []
        batch_by_id: dict[Any, dict[str, Any]] = {}
        for batch in batches:
            batch_id = batch.get("timing_batch_id")
            wall = batch.get("wall_seconds")
            sequence_ids = batch.get("member_sequence_ids", [])
            check(
                isinstance(batch_id, str)
                and bool(batch_id)
                and is_number(wall)
                and wall > 0
                and isinstance(sequence_ids, list)
                and bool(sequence_ids),
                f"timing batch shape {batch_id}",
            )
            batch_by_id[batch_id] = batch
            members.extend(sequence_ids)
        check(
            unique_strings(members, 11)
            and set(members) == {row.get("sequence_id") for row in execution_rows},
            "timing batch exact membership",
        )
        for record in execution_rows:
            sequence = record.get("sequence_id")
            tool = record.get("execution", {})
            batch = batch_by_id.get(tool.get("timing_batch_id"))
            check(batch is not None, f"timing batch binding {sequence}")
            if batch is None:
                continue
            wall = batch.get("wall_seconds")
            check(
                sequence in batch.get("member_sequence_ids", [])
                and tool.get("parallel_batch_wall_seconds") == wall,
                f"timing wall binding {sequence}",
            )
            if len(batch.get("member_sequence_ids", [])) == 1:
                check(
                    tool.get("elapsed_seconds") == wall,
                    f"single timing arithmetic {sequence}",
                )
            else:
                check(
                    tool.get("elapsed_seconds") is None,
                    f"parallel timing arithmetic {sequence}",
                )
        wall_sum = sum(
            (Decimal(str(batch.get("wall_seconds", 0))) for batch in batches),
            Decimal(0),
        )
        check(
            summary.get("unique_timing_batches") == len(batches),
            "summary timing batches",
        )
        check(
            Decimal(str(summary.get("overlap_adjusted_tool_call_wall_seconds", -1)))
            == wall_sum,
            "summary timing arithmetic",
        )
        check(
            summary.get("per_output_elapsed_seconds_available") == elapsed_available,
            "summary elapsed availability",
        )
        check(
            isinstance(summary.get("timing_scope"), str)
            and bool(summary["timing_scope"]),
            "summary timing scope",
        )
        check(
            summary.get("direct_paid_provider_api_calls") == 0
            and summary.get("paid_spend_usd") == 0.0,
            "summary paid boundary",
        )
    elif observation_timing:
        observations = execution.get("timing_observations", {})
        pair = observations.get("concurrent_pair", {})
        pair_members = pair.get("member_sequence_ids", [])
        pair_wall = pair.get("batch_wall_seconds")
        pair_id = pair.get("timing_batch_id")
        check(
            unique_strings(pair_members, 2) and pair_members == concurrent_sequence_ids,
            "distributed concurrent pair membership",
        )
        check(
            isinstance(pair_id, str)
            and bool(pair_id)
            and is_number(pair_wall)
            and pair_wall > 0
            and pair.get("member_elapsed_seconds") == [None, None],
            "distributed concurrent pair shape",
        )
        for record in execution_rows:
            sequence = record.get("sequence_id")
            tool = record.get("execution", {})
            if sequence in pair_members:
                check(
                    tool.get("observed_tool_wall_seconds") is None
                    and tool.get("concurrent_batch_id") == pair_id
                    and tool.get("concurrent_batch_wall_seconds") == pair_wall,
                    f"distributed pair row binding {sequence}",
                )
            else:
                check(
                    tool.get("concurrent_batch_id") is None
                    and tool.get("concurrent_batch_wall_seconds") is None,
                    f"distributed known row binding {sequence}",
                )
        known_sum = sum(observed_per_output_walls, Decimal(0))
        non_overlap_total = known_sum + Decimal(str(pair_wall or 0))
        check(
            summary.get("per_output_wall_seconds_available")
            == len(observed_per_output_walls)
            == 9,
            "distributed known per-output count",
        )
        check(
            Decimal(str(summary.get("known_per_output_tool_wall_seconds_sum", -1)))
            == known_sum,
            "distributed known per-output Decimal sum",
        )
        check(
            summary.get("concurrent_pair_batch_wall_seconds") == pair_wall,
            "distributed pair wall summary",
        )
        check(
            Decimal(str(summary.get("non_overlap_adjusted_observed_total_seconds", -1)))
            == non_overlap_total,
            "distributed non-overlap Decimal sum",
        )
        check(
            summary.get("actual_end_to_end_wall_seconds") is None,
            "distributed actual end-to-end unavailable",
        )
        check(
            "overlap_adjusted_tool_call_wall_seconds" not in summary
            and "unique_timing_batches" not in summary
            and "per_output_elapsed_seconds_available" not in summary,
            "no false overlap-adjusted timing claim",
        )
        honesty = observations.get("honesty_boundary", "")
        check(
            isinstance(honesty, str)
            and "without a shared stopwatch" in honesty
            and "unavailable and remains null" in honesty
            and "non-overlap-adjusted observed total" in honesty
            and "not a batch-adjusted or actual end-to-end duration" in honesty,
            "distributed timing honesty boundary",
        )
        check(
            summary.get("direct_paid_provider_api_calls") == 0
            and summary.get("cost_total_usd") is None
            and "paid_spend_usd" not in summary,
            "distributed cost honesty boundary",
        )
    elif distributed_batch_timing:
        batches = execution.get("timing_batches", [])
        batch_ids = [batch.get("timing_batch_id") for batch in batches]
        expected_batch_ids = [
            "reduced-palette-text-control-s07-s09-concurrent",
            "reduced-palette-text-control-s10-s11-concurrent",
        ]
        expected_concurrent_groups = [
            [row.get("sequence_id") for row in execution_rows[6:9]],
            [row.get("sequence_id") for row in execution_rows[9:11]],
        ]
        check(batch_ids == expected_batch_ids, "timing batch IDs")
        batch_by_id: dict[Any, dict[str, Any]] = {}
        concurrent_members: list[Any] = []
        batch_walls: list[Decimal] = []
        for index, batch in enumerate(batches):
            batch_id = batch.get("timing_batch_id")
            wall = batch.get("wall_seconds")
            sequence_ids = batch.get("member_sequence_ids", [])
            expected_members = (
                expected_concurrent_groups[index]
                if index < len(expected_concurrent_groups)
                else None
            )
            check(
                isinstance(batch_id, str)
                and bool(batch_id)
                and is_number(wall)
                and wall > 0
                and sequence_ids == expected_members,
                f"distributed timing batch shape {batch_id}",
            )
            batch_by_id[batch_id] = batch
            concurrent_members.extend(sequence_ids)
            if is_number(wall) and wall > 0:
                batch_walls.append(Decimal(str(wall)))
        check(
            concurrent_members == concurrent_sequence_ids
            and unique_strings(concurrent_members, 5),
            "distributed timing batch exact membership",
        )
        for index, record in enumerate(execution_rows):
            sequence = record.get("sequence_id")
            tool = record.get("execution", {})
            if index < 6:
                check(
                    tool.get("observed_tool_wall_seconds") is not None
                    and tool.get("concurrent_batch_id") is None
                    and tool.get("concurrent_batch_wall_seconds") is None,
                    f"distributed known row binding {sequence}",
                )
                continue
            batch = batch_by_id.get(tool.get("concurrent_batch_id"))
            check(batch is not None, f"distributed batch binding {sequence}")
            if batch is not None:
                check(
                    sequence in batch.get("member_sequence_ids", [])
                    and tool.get("observed_tool_wall_seconds") is None
                    and tool.get("concurrent_batch_wall_seconds")
                    == batch.get("wall_seconds"),
                    f"distributed batch wall binding {sequence}",
                )
        known_sum = sum(observed_per_output_walls, Decimal(0))
        non_overlap_total = known_sum + sum(batch_walls, Decimal(0))
        check(
            len(observed_per_output_walls)
            == summary.get("per_output_wall_seconds_available")
            == 6,
            "distributed known per-output count",
        )
        check(
            Decimal(
                str(summary.get("known_individual_tool_wall_seconds_sum", -1))
            )
            == known_sum,
            "distributed known individual Decimal sum",
        )
        check(
            summary.get("concurrent_batch_count") == len(batches) == 2,
            "distributed concurrent batch count",
        )
        check(
            Decimal(
                str(summary.get("non_overlap_observed_arithmetic_seconds", -1))
            )
            == non_overlap_total,
            "distributed non-overlap Decimal arithmetic",
        )
        check(
            summary.get("actual_end_to_end_wall_seconds") is None,
            "distributed actual end-to-end unavailable",
        )
        check(
            "overlap_adjusted_tool_call_wall_seconds" not in summary
            and "non_overlap_adjusted_observed_total_seconds" not in summary
            and "unique_timing_batches" not in summary
            and "per_output_elapsed_seconds_available" not in summary,
            "no false overlap-adjusted timing claim",
        )
        honesty = execution.get("timing_honesty_boundary", "")
        check(
            isinstance(honesty, str)
            and "individually observed calls total" in honesty
            and "concurrent batch observed" in honesty
            and "non-overlap observed arithmetic only" in honesty
            and "Actual end-to-end wall time remains null" in honesty
            and "lacked one shared stopwatch" in honesty,
            "distributed timing honesty boundary",
        )
        check(
            summary.get("direct_paid_provider_api_calls") == 0
            and summary.get("cost_total_usd") is None
            and "paid_spend_usd" not in summary,
            "distributed cost honesty boundary",
        )
    check(
        all(
            summary.get(field) == 0
            for field in (
                "human_reviewed_outputs",
                "accepted_outputs",
                *(("rights_cleared_outputs",) if text_only_route else ()),
                "commercially_cleared_outputs",
                "exact_production_base_outputs",
            )
        ),
        "summary review/rights boundary",
    )
    boundary = execution.get("boundary", {})
    check(
        boundary.get("permitted_product") == "openai_builtin_imagegen",
        "product boundary",
    )
    check(
        all(
            boundary.get(field) == 0
            for field in (
                "direct_paid_provider_api_calls",
                "bfl_calls",
                "new_upload_classes",
                "real_person_or_child_material",
            )
        ),
        "execution provider/data boundary",
    )
    if text_only_route:
        check(
            all(
                boundary.get(field) == 0
                for field in (
                    "reference_uploads",
                    "referenced_image_paths_passed",
                    "conversation_images_included",
                    "accepted",
                    "rights_cleared",
                    "commercially_cleared",
                    "exact_production_base",
                )
            ),
            "text-only execution upload/review boundary",
        )
    prompt_boundary = prompt.get("boundary", {})
    check(
        prompt_boundary.get("permitted_product") == "openai_builtin_imagegen"
        and all(
            prompt_boundary.get(field) == 0
            for field in (
                "direct_paid_provider_api_calls",
                "bfl_calls",
                *(("reference_uploads",) if text_only_route else ()),
                "new_upload_classes",
                "real_person_or_child_material",
                "current_executions",
                "current_outputs",
                "accepted",
                "commercially_cleared",
                "exact_production_base",
            )
        ),
        "prompt provider/data/review boundary",
    )
    return errors


def mutate_reference_binding(
    prompt: dict[str, Any], execution: dict[str, Any]
) -> None:
    """Corrupt reference provenance without assuming a route has a reference."""
    prompt_references = prompt["sequences"][0]["input_references"]
    execution_references = execution["records"][0]["input_references"]
    if prompt_references:
        execution_references[0]["sha256"] = "0" * 64
        return
    forbidden_reference = {
        "reference_id": "self-test-forbidden-reference",
        "path": "experiments/self-test-forbidden-reference.png",
        "sha256": "0" * 64,
    }
    prompt_references.append(copy.deepcopy(forbidden_reference))
    execution_references.append(forbidden_reference)


def self_test(
    prompt: dict[str, Any], execution: dict[str, Any], prompt_path: Path
) -> tuple[int, int]:
    mutations: list[
        tuple[
            str,
            Callable[[dict[str, Any], dict[str, Any]], None],
            bool,
        ]
    ] = [
        (
            "execution planning",
            lambda p, e: e.__setitem__("planning_structure", "AnimationShotPlan"),
            False,
        ),
        (
            "prompt planning",
            lambda p, e: p.__setitem__("planning_structure", "AnimationShotPlan"),
            False,
        ),
        ("cross-medium field", lambda p, e: e.__setitem__("e_conte", {}), False),
        (
            "prompt manifest hash",
            lambda p, e: e["input_prompt_manifest"].__setitem__("sha256", "0" * 64),
            False,
        ),
        ("sequence denominator", lambda p, e: e["records"].pop(), False),
        (
            "panel coverage",
            lambda p, e: e["records"][1].__setitem__("panel_range", [7, 9]),
            False,
        ),
        (
            "prompt text",
            lambda p, e: e["records"][0].__setitem__("prompt_text", "tampered"),
            False,
        ),
        (
            "prompt hash",
            lambda p, e: p["sequences"][0].__setitem__("prompt_sha256", "0" * 64),
            False,
        ),
        (
            "reference binding",
            mutate_reference_binding,
            False,
        ),
        (
            "unsafe output",
            lambda p, e: e["records"][0]["output"].__setitem__(
                "path", "production/leak.png"
            ),
            False,
        ),
        (
            "output hash",
            lambda p, e: e["records"][0]["output"].__setitem__("sha256", "0" * 64),
            True,
        ),
        (
            "invented model",
            lambda p, e: e["records"][0]["execution"].__setitem__("model", "invented"),
            False,
        ),
        (
            "unavailable list",
            lambda p, e: e["records"][0]["execution"]["unavailable_fields"].pop(),
            False,
        ),
        (
            "provider ID claim",
            lambda p, e: e["records"][0]["execution"].__setitem__(
                "tool_service_execution_id_is_provider_request_id", True
            ),
            False,
        ),
        ("accepted", lambda p, e: e["records"][0].__setitem__("accepted", True), False),
        (
            "commercial claim",
            lambda p, e: e["records"][0].__setitem__("commercially_cleared", True),
            False,
        ),
        (
            "duplicate output",
            lambda p, e: e["records"][1]["output"].__setitem__(
                "path", e["records"][0]["output"]["path"]
            ),
            False,
        ),
        (
            "duplicate execution ID",
            lambda p, e: e["records"][1]["execution"].__setitem__(
                "tool_service_execution_id",
                e["records"][0]["execution"]["tool_service_execution_id"],
            ),
            False,
        ),
        (
            "summary paid",
            lambda p, e: e["summary"].__setitem__("paid_spend_usd", 1.0),
            False,
        ),
        (
            "boundary upload",
            lambda p, e: e["boundary"].__setitem__("new_upload_classes", 1),
            False,
        ),
    ]
    if isinstance(execution.get("timing_batches"), list) and not isinstance(
        execution.get("timing_honesty_boundary"), str
    ):
        mutations.extend(
            [
                (
                    "timing member",
                    lambda p, e: e["timing_batches"][0]["member_sequence_ids"].pop(),
                    False,
                ),
                (
                    "timing row wall",
                    lambda p, e: e["records"][0]["execution"].__setitem__(
                        "parallel_batch_wall_seconds", 1.0
                    ),
                    False,
                ),
                (
                    "summary wall",
                    lambda p, e: e["summary"].__setitem__(
                        "overlap_adjusted_tool_call_wall_seconds", 1.0
                    ),
                    False,
                ),
                (
                    "parallel member elapsed",
                    lambda p, e: e["records"][1]["execution"].__setitem__(
                        "elapsed_seconds", 1.0
                    ),
                    False,
                ),
            ]
        )
    elif isinstance(execution.get("timing_observations"), dict):
        mutations.extend(
            [
                (
                    "distributed actual end-to-end claim",
                    lambda p, e: e["summary"].__setitem__(
                        "actual_end_to_end_wall_seconds", 1290.989
                    ),
                    False,
                ),
                (
                    "distributed known count",
                    lambda p, e: e["summary"].__setitem__(
                        "per_output_wall_seconds_available", 10
                    ),
                    False,
                ),
                (
                    "distributed known sum",
                    lambda p, e: e["summary"].__setitem__(
                        "known_per_output_tool_wall_seconds_sum", 1064.921
                    ),
                    False,
                ),
                (
                    "distributed pair member",
                    lambda p, e: e["timing_observations"]["concurrent_pair"][
                        "member_sequence_ids"
                    ].pop(),
                    False,
                ),
                (
                    "distributed pair wall",
                    lambda p, e: e["timing_observations"][
                        "concurrent_pair"
                    ].__setitem__("batch_wall_seconds", 228.068),
                    False,
                ),
                (
                    "distributed row pair wall",
                    lambda p, e: e["records"][9]["execution"].__setitem__(
                        "concurrent_batch_wall_seconds", 228.068
                    ),
                    False,
                ),
                (
                    "distributed known row wall",
                    lambda p, e: e["records"][0]["execution"].__setitem__(
                        "observed_tool_wall_seconds", 121.9
                    ),
                    False,
                ),
                (
                    "distributed inferred member elapsed",
                    lambda p, e: e["timing_observations"][
                        "concurrent_pair"
                    ].__setitem__("member_elapsed_seconds", [100.0, None]),
                    False,
                ),
                (
                    "distributed non-overlap total",
                    lambda p, e: e["summary"].__setitem__(
                        "non_overlap_adjusted_observed_total_seconds", 1291.989
                    ),
                    False,
                ),
                (
                    "distributed false overlap-adjusted claim",
                    lambda p, e: e["summary"].__setitem__(
                        "overlap_adjusted_tool_call_wall_seconds", 1290.989
                    ),
                    False,
                ),
                (
                    "distributed honesty boundary",
                    lambda p, e: e["timing_observations"].__setitem__(
                        "honesty_boundary", "timing complete"
                    ),
                    False,
                ),
            ]
        )
    elif isinstance(execution.get("timing_batches"), list):
        mutations.extend(
            [
                (
                    "distributed actual end-to-end claim",
                    lambda p, e: e["summary"].__setitem__(
                        "actual_end_to_end_wall_seconds", 1027.652
                    ),
                    False,
                ),
                (
                    "distributed known count",
                    lambda p, e: e["summary"].__setitem__(
                        "per_output_wall_seconds_available", 7
                    ),
                    False,
                ),
                (
                    "distributed known sum",
                    lambda p, e: e["summary"].__setitem__(
                        "known_individual_tool_wall_seconds_sum", 568.301
                    ),
                    False,
                ),
                (
                    "distributed batch member",
                    lambda p, e: e["timing_batches"][0][
                        "member_sequence_ids"
                    ].pop(),
                    False,
                ),
                (
                    "distributed batch wall",
                    lambda p, e: e["timing_batches"][0].__setitem__(
                        "wall_seconds", 300.468
                    ),
                    False,
                ),
                (
                    "distributed row batch wall",
                    lambda p, e: e["records"][6]["execution"].__setitem__(
                        "concurrent_batch_wall_seconds", 300.468
                    ),
                    False,
                ),
                (
                    "distributed known row wall",
                    lambda p, e: e["records"][0]["execution"].__setitem__(
                        "observed_tool_wall_seconds", 112.201
                    ),
                    False,
                ),
                (
                    "distributed non-overlap total",
                    lambda p, e: e["summary"].__setitem__(
                        "non_overlap_observed_arithmetic_seconds", 1027.653
                    ),
                    False,
                ),
                (
                    "distributed false overlap-adjusted claim",
                    lambda p, e: e["summary"].__setitem__(
                        "overlap_adjusted_tool_call_wall_seconds", 1027.652
                    ),
                    False,
                ),
                (
                    "distributed honesty boundary",
                    lambda p, e: e.__setitem__(
                        "timing_honesty_boundary", "timing complete"
                    ),
                    False,
                ),
                (
                    "text-only image argument",
                    lambda p, e: e["records"][0]["execution"].__setitem__(
                        "referenced_image_paths_parameter", []
                    ),
                    False,
                ),
                (
                    "text-only summary upload",
                    lambda p, e: e["summary"].__setitem__("reference_uploads", 1),
                    False,
                ),
            ]
        )
    caught = 0
    for _, mutation, verify_files in mutations:
        mutated_prompt = copy.deepcopy(prompt)
        mutated_execution = copy.deepcopy(execution)
        mutation(mutated_prompt, mutated_execution)
        caught += bool(
            validate(mutated_prompt, mutated_execution, prompt_path, verify_files)
        )
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-manifest", required=True)
    parser.add_argument("--execution-manifest", required=True)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    prompt_path = resolve_cli_path(args.prompt_manifest)
    execution_path = resolve_cli_path(args.execution_manifest)
    prompt = json.loads(prompt_path.read_text(encoding="utf-8"))
    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    errors = validate(prompt, execution, prompt_path)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(prompt, execution, prompt_path)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
                "prompt_manifest": prompt_path.relative_to(ROOT).as_posix(),
                "execution_manifest": execution_path.relative_to(ROOT).as_posix(),
                "sequences": len(execution.get("records", [])),
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
