"""Validate S11 reference-ablation execution and three-column review evidence."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from build_ch05_r6_alt_graphic_comparison import metric
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / "production/comic/run-manifests/ch05-s11-flat-gouache-reference-ablation-prompt-r1.json"
FLAT_EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-execution-manifest-r1.json"
TEXT_EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-execution-manifest-r1.json"
EXECUTION = ROOT / "production/comic/run-manifests/ch05-s11-flat-gouache-reference-ablation-execution-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-s11-flat-gouache-reference-ablation-comparison-r1.json"
ABLATION_LOCAL = ROOT / "experiments/review-packets/ch05-s11-flat-gouache-reference-ablation-r1/s11-farmhouse-reversal-flat-gouache-no-reference-r1.png"
ABLATION_GLOBAL = Path("C:/Users/gosne/.codex/generated_images/01a05d7c-0ac3-7872-8fa8-3fb9c14f6eaa/exec-0fa79c2c-7369-4a5f-b013-f240c542d9db.png")
EXECUTION_ID = "exec-0fa79c2c-7369-4a5f-b013-f240c542d9db"
OUTPUT_SHA256 = "c5f66a8cd7b4cd4d3f8fcbe5066e7a77d031a7341617e2eb9b3829da167aa1f3"
ORDER = (
    "flat_with_authorized_refs",
    "matched_flat_no_reference",
    "stricter_reduced_palette_no_reference",
)
UNAVAILABLE = ["model", "provider", "endpoint", "provider_request_id", "usage", "cost_usd", "deterministic_seed"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def bind(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def find_s11(document: dict[str, Any]) -> dict[str, Any]:
    rows = [row for row in document["records"] if row["source_sequence_id"] == "s11-farmhouse-reversal"]
    if len(rows) != 1:
        raise ValueError("source execution must contain exactly one S11")
    return rows[0]


def image_facts(path: Path) -> tuple[str, int, int, int]:
    with Image.open(path) as opened:
        if opened.format != "PNG":
            raise ValueError(f"not PNG: {path}")
        width, height = opened.size
    return sha256(path), width, height, path.stat().st_size


def measured(path: Path) -> dict[str, float]:
    with Image.open(path) as opened:
        image = opened.convert("RGB")
    return metric(image, path.stat().st_size)


def subtract(after: dict[str, float], before: dict[str, float]) -> dict[str, float]:
    return {key: round(after[key] - before[key], 6) for key in before}


def validate(execution: dict[str, Any], evidence: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    prompt = load(PROMPT)
    flat_manifest = load(FLAT_EXECUTION)
    text_manifest = load(TEXT_EXECUTION)
    flat = find_s11(flat_manifest)
    text = find_s11(text_manifest)
    prompt_row = prompt["sequence"]

    check(
        execution.get("record_type") == "CH05S11MatchedReferenceAblationExecution"
        and execution.get("schema_version") == "1.0"
        and execution.get("record_id") == "ng-ch05-s11-flat-gouache-reference-ablation-execution-r1"
        and execution.get("state") == "EXECUTED_UNACCEPTED_PENDING_HUMAN_REVIEW",
        "execution identity/state",
    )
    check(
        execution.get("planning_structure") == "ComicPanelPlan"
        and execution.get("animation_shot_plan") is None
        and execution.get("e_conte") is None,
        "execution planning boundary",
    )
    check(execution.get("input_prompt_manifest") == bind(PROMPT), "prompt manifest binding")
    check(execution.get("comparison_contract") == prompt.get("comparison_contract"), "comparison contract binding")
    check(
        prompt["comparison_contract"].get("changed_prompt_line_indexes_zero_based") == [3]
        and prompt["comparison_contract"].get("unchanged_prompt_line_count") == 15
        and prompt["comparison_contract"].get("style_wording_changed") is False
        and prompt["comparison_contract"].get("story_or_gate_wording_changed") is False,
        "single-line matched design",
    )
    flat_lines = flat["prompt_text"].splitlines()
    ablation_lines = prompt_row["prompt_text"].splitlines()
    changed = [index for index, (before, after) in enumerate(zip(flat_lines, ablation_lines, strict=True)) if before != after]
    check(changed == [3] and len(flat_lines) == 16, "actual one-line prompt difference")
    check(
        hashlib.sha256(prompt_row["prompt_text"].encode("utf-8")).hexdigest() == prompt_row["prompt_sha256"],
        "prompt text hash",
    )

    record = execution.get("record", {})
    check(
        record.get("sequence_id") == prompt_row["sequence_id"]
        and record.get("source_sequence_id") == "s11-farmhouse-reversal"
        and record.get("panel_range") == [48, 50]
        and record.get("panel_count") == 3
        and record.get("prompt_text") == prompt_row["prompt_text"]
        and record.get("prompt_sha256") == prompt_row["prompt_sha256"]
        and record.get("input_references") == [],
        "execution prompt/plan record",
    )
    run = record.get("execution", {})
    check(
        run.get("tool_mode") == "openai_builtin_imagegen_in_codex"
        and run.get("tool_service_execution_id") == EXECUTION_ID
        and run.get("tool_service_execution_id_is_provider_request_id") is False
        and run.get("observed_tool_wall_seconds") == 48.2,
        "tool execution provenance/timing",
    )
    check(
        run.get("global_original_path") == ABLATION_GLOBAL.as_posix()
        and run.get("global_original_preserved") is True
        and run.get("referenced_image_paths_parameter") == "OMITTED"
        and run.get("num_last_images_to_include_parameter") == "OMITTED",
        "global original/reference-argument boundary",
    )
    check(run.get("unavailable_fields") == UNAVAILABLE and all(run.get(field) is None for field in UNAVAILABLE), "null unavailable fields")
    check(sha256(ABLATION_LOCAL) == sha256(ABLATION_GLOBAL) == OUTPUT_SHA256, "local/global output hashes")
    check(ABLATION_LOCAL.read_bytes() == ABLATION_GLOBAL.read_bytes(), "local/global byte identity")
    output = record.get("output", {})
    output_facts = image_facts(ABLATION_LOCAL)
    check(
        output
        == {
            "path": ABLATION_LOCAL.relative_to(ROOT).as_posix(),
            "sha256": output_facts[0],
            "width": output_facts[1],
            "height": output_facts[2],
            "bytes": output_facts[3],
        }
        and output_facts == (OUTPUT_SHA256, 852, 1846, 2376174),
        "ablation output binding",
    )
    check(
        record.get("human_review_state") == "PENDING"
        and record.get("human_review_minutes") is None
        and all(
            record.get(key) is False
            for key in ("accepted", "rights_cleared", "commercially_cleared", "exact_production_base", "generation_reproducible")
        ),
        "execution review/rights boundary",
    )
    check(
        execution.get("summary")
        == {
            "sequence_outputs": 1,
            "comic_panel_plans": 3,
            "authorized_reference_uses": 0,
            "reference_uploads": 0,
            "known_tool_wall_seconds": 48.2,
            "direct_paid_provider_api_calls": 0,
            "cost_total_usd": None,
            "human_reviewed_outputs": 0,
            "accepted_outputs": 0,
            "rights_cleared_outputs": 0,
            "commercially_cleared_outputs": 0,
            "exact_production_base_outputs": 0,
        },
        "execution summary",
    )
    boundary = execution.get("boundary", {})
    check(all(value == 0 for key, value in boundary.items() if key != "permitted_product"), "zero execution boundary")
    check(
        boundary.get("permitted_product") == "openai_builtin_imagegen"
        and any("one changed input-instruction line cannot prove" in line.lower() for line in execution.get("limitations", [])),
        "execution causal limitation",
    )

    check(
        evidence.get("record_type") == "CH05S11MatchedReferenceAblationComparison"
        and evidence.get("schema_version") == "1.0"
        and evidence.get("record_id") == "ng-ch05-s11-flat-gouache-reference-ablation-comparison-r1"
        and evidence.get("state") == "MEASURED_PENDING_HUMAN_REVIEW",
        "review evidence identity/state",
    )
    check(
        evidence.get("planning_structure") == "ComicPanelPlan"
        and evidence.get("animation_shot_plan") is None
        and evidence.get("e_conte") is None,
        "review planning boundary",
    )
    check(evidence.get("inputs") == [bind(PROMPT), bind(EXECUTION), bind(FLAT_EXECUTION), bind(TEXT_EXECUTION)], "review input bindings")
    design = evidence.get("comparison_design", {})
    check(
        design.get("panel_range") == [48, 50]
        and design.get("candidate_count") == 3
        and design.get("matched_pair") == list(ORDER[:2])
        and design.get("matched_pair_changed_prompt_line_indexes_zero_based") == [3]
        and design.get("matched_pair_unchanged_prompt_line_count") == 15
        and design.get("matched_pair_style_wording_changed") is False
        and design.get("matched_pair_story_or_gate_wording_changed") is False
        and design.get("stricter_control") == ORDER[2],
        "review comparison design",
    )

    candidates = evidence.get("candidates", [])
    check([row.get("comparison_role") for row in candidates] == list(ORDER), "candidate order/roles")
    source_records = (flat, record, text)
    source_manifests = (FLAT_EXECUTION, EXECUTION, TEXT_EXECUTION)
    expected_references = (2, 0, 0)
    metrics: dict[str, dict[str, float]] = {}
    for key, candidate, source_record, source_manifest, refs in zip(
        ORDER, candidates, source_records, source_manifests, expected_references, strict=True
    ):
        path = ROOT / source_record["output"]["path"]
        facts = image_facts(path)
        expected_output = {"path": path.relative_to(ROOT).as_posix(), "sha256": facts[0], "width": facts[1], "height": facts[2], "bytes": facts[3]}
        metrics[key] = measured(path)
        check(candidate.get("execution_manifest") == bind(source_manifest), f"candidate execution binding: {key}")
        check(
            candidate.get("sequence_id") == source_record["sequence_id"]
            and candidate.get("prompt_sha256") == source_record["prompt_sha256"]
            and candidate.get("input_reference_count") == refs
            and candidate.get("output") == expected_output
            and candidate.get("metrics") == metrics[key],
            f"candidate source/metrics: {key}",
        )
        check(
            candidate.get("human_review_state") == "PENDING"
            and candidate.get("human_review_minutes") is None
            and all(
                candidate.get(field) is False
                for field in ("accepted", "rights_cleared", "commercially_cleared", "exact_production_base")
            ),
            f"candidate review/rights boundary: {key}",
        )

    expected_deltas = {
        "matched_no_reference_minus_reference_backed_flat": subtract(metrics[ORDER[1]], metrics[ORDER[0]]),
        "stricter_no_reference_minus_reference_backed_flat": subtract(metrics[ORDER[2]], metrics[ORDER[0]]),
        "stricter_no_reference_minus_matched_no_reference": subtract(metrics[ORDER[2]], metrics[ORDER[1]]),
    }
    check(evidence.get("metric_deltas") == expected_deltas, "metric deltas")
    method = evidence.get("metric_method", {})
    check(
        method.get("normalization_width_px") == 390
        and "FIND_EDGES" in method.get("edge_density_ge_32", "")
        and "do not measure" in method.get("interpretation", ""),
        "metric definitions/limitations",
    )

    artifacts = evidence.get("artifacts", {})
    expected_artifacts = {
        "native_three_column": (2737, 2013),
        "phone_390px_three_column": (1246, 1010),
    }
    for key, dimensions in expected_artifacts.items():
        item = artifacts.get(key, {})
        path = ROOT / item.get("path", "missing")
        check(path.is_file(), f"artifact exists: {key}")
        if path.is_file():
            facts = image_facts(path)
            check(
                item.get("sha256") == facts[0]
                and (item.get("width"), item.get("height")) == dimensions == (facts[1], facts[2])
                and item.get("bytes") == facts[3]
                and item.get("repository_state") == "IGNORED_LOCAL_REVIEW_ARTIFACT",
                f"artifact binding: {key}",
            )

    check(
        evidence.get("human_review_state") == "PENDING"
        and evidence.get("human_review_minutes") is None
        and all(
            evidence.get(field) == 0
            for field in (
                "accepted_candidates",
                "rights_cleared_candidates",
                "commercially_cleared_candidates",
                "exact_production_base_candidates",
            )
        ),
        "review evidence disposition boundary",
    )
    check(
        evidence.get("spend") == {"direct_paid_api_cloud_usd": 0.0, "built_in_product_monetary_cost_usd": None},
        "spend boundary",
    )
    limitations = evidence.get("limitations", [])
    check(
        any("one changed input-instruction line cannot prove general causality" in line.lower() for line in limitations)
        and any("also changes style instructions" in line for line in limitations)
        and any("no candidate is accepted" in line.lower() for line in limitations),
        "review causal/style/disposition limitations",
    )
    check("ComicPanelPlan remains the sole planning structure" in evidence.get("boundary", ""), "review boundary")
    return errors


def self_test(execution: dict[str, Any], evidence: dict[str, Any]) -> tuple[int, int]:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("execution", lambda value: value.__setitem__("record_id", "bad")),
        ("execution", lambda value: value["input_prompt_manifest"].__setitem__("sha256", "0" * 64)),
        ("execution", lambda value: value["record"].__setitem__("prompt_sha256", "f" * 64)),
        ("execution", lambda value: value["record"].__setitem__("input_references", ["leak"])),
        ("execution", lambda value: value["record"]["execution"].__setitem__("tool_service_execution_id", "bad")),
        ("execution", lambda value: value["record"]["execution"].__setitem__("observed_tool_wall_seconds", 0)),
        ("execution", lambda value: value["record"]["execution"].__setitem__("provider_request_id", EXECUTION_ID)),
        ("execution", lambda value: value["record"]["output"].__setitem__("sha256", "0" * 64)),
        ("execution", lambda value: value["record"].__setitem__("accepted", True)),
        ("execution", lambda value: value["summary"].__setitem__("reference_uploads", 1)),
        ("execution", lambda value: value["summary"].__setitem__("cost_total_usd", 0.0)),
        ("evidence", lambda value: value.__setitem__("planning_structure", "AnimationShotPlan")),
        ("evidence", lambda value: value["inputs"][1].__setitem__("sha256", "0" * 64)),
        ("evidence", lambda value: value["comparison_design"].__setitem__("matched_pair_changed_prompt_line_indexes_zero_based", [])),
        ("evidence", lambda value: value["candidates"][0].__setitem__("input_reference_count", 0)),
        ("evidence", lambda value: value["candidates"][1]["metrics"].__setitem__("edge_density_ge_32", 1.0)),
        ("evidence", lambda value: value["metric_deltas"]["matched_no_reference_minus_reference_backed_flat"].__setitem__("edge_density_ge_32", 0.0)),
        ("evidence", lambda value: value["artifacts"]["phone_390px_three_column"].__setitem__("sha256", "0" * 64)),
        ("evidence", lambda value: value.__setitem__("human_review_state", "COMPLETE")),
        ("evidence", lambda value: value.__setitem__("accepted_candidates", 1)),
        ("evidence", lambda value: value["spend"].__setitem__("built_in_product_monetary_cost_usd", 0.0)),
        ("evidence", lambda value: value.__setitem__("limitations", [])),
    ]
    caught = 0
    for target, mutation in mutations:
        execution_candidate = copy.deepcopy(execution)
        evidence_candidate = copy.deepcopy(evidence)
        mutation(execution_candidate if target == "execution" else evidence_candidate)
        caught += bool(validate(execution_candidate, evidence_candidate))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    execution = load(EXECUTION)
    evidence = load(EVIDENCE)
    errors = validate(execution, evidence)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(execution, evidence)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
