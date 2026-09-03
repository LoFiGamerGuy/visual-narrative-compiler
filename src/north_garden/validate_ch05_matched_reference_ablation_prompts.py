"""Validate byte-stable S11 and preflight-only S01 matched ablation prompts."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from compile_ch05_s11_matched_reference_ablation_prompt import REPLACEMENT

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-prompt-manifest-r1.json"
S11 = ROOT / "production/comic/run-manifests/ch05-s11-flat-gouache-reference-ablation-prompt-r1.json"
S01 = ROOT / "production/comic/run-manifests/ch05-s01-flat-gouache-reference-ablation-prompt-r1.json"
S11_COMPATIBILITY_SHA256 = "7215fbb8958604bda0f044f190c16d68c85d90bdabad5f27fc70974dac7f1823"
SPECS = {
    "S11": {
        "path": S11,
        "target": "flat-graphic-gouache-s11-farmhouse-reversal",
        "record_type": "CH05S11MatchedReferenceAblationPrompt",
        "record_id": "ng-ch05-s11-flat-gouache-reference-ablation-prompt-r1",
        "sequence_id": "flat-gouache-reference-ablation-s11-farmhouse-reversal",
        "panel_range": [48, 50],
        "panel_count": 3,
        "planned_output": (
            "experiments/review-packets/ch05-s11-flat-gouache-reference-ablation-r1/"
            "s11-farmhouse-reversal-flat-gouache-no-reference-r1.png"
        ),
    },
    "S01": {
        "path": S01,
        "target": "flat-graphic-gouache-s01-opening-departure",
        "record_type": "CH05S01MatchedReferenceAblationPrompt",
        "record_id": "ng-ch05-s01-flat-gouache-reference-ablation-prompt-r1",
        "sequence_id": "flat-gouache-reference-ablation-s01-opening-departure",
        "panel_range": [1, 5],
        "panel_count": 5,
        "planned_output": (
            "experiments/review-packets/ch05-s01-flat-gouache-reference-ablation-r1/"
            "s01-opening-departure-flat-gouache-no-reference-r1.png"
        ),
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_row(source: dict[str, Any], target: str) -> dict[str, Any]:
    rows = [row for row in source["sequences"] if row["sequence_id"] == target]
    if len(rows) != 1:
        raise ValueError(f"source row cardinality: {target}")
    return rows[0]


def validate_document(label: str, document: dict[str, Any], source: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(f"{label}: {message}")

    spec = SPECS[label]
    original = source_row(source, spec["target"])
    record = document.get("sequence", {})
    check(
        document.get("record_type") == spec["record_type"]
        and document.get("schema_version") == "1.0"
        and document.get("record_id") == spec["record_id"]
        and document.get("state") == "EXACT_PROMPT_COMPILED_NOT_EXECUTED"
        and document.get("medium") == "comic",
        "identity/state",
    )
    check(
        document.get("planning_structure") == "ComicPanelPlan"
        and document.get("animation_shot_plan") is None
        and document.get("e_conte") is None,
        "ComicPanelPlan-only boundary",
    )
    check(
        document.get("source_prompt_manifest")
        == {"path": SOURCE.relative_to(ROOT).as_posix(), "sha256": sha256(SOURCE)},
        "source binding",
    )
    contract = document.get("comparison_contract", {})
    check(
        contract.get("source_sequence_id") == spec["target"]
        and contract.get("changed_prompt_line_indexes_zero_based") == [3]
        and contract.get("unchanged_prompt_line_count") == len(original["prompt_lines"]) - 1
        and contract.get("changed_factor") == "remove_reference_pixel_conditioning"
        and contract.get("style_wording_changed") is False
        and contract.get("story_or_gate_wording_changed") is False
        and contract.get("input_reference_count_source") == 2
        and contract.get("input_reference_count_ablation") == 0,
        "comparison contract",
    )
    check(
        isinstance(contract.get("causal_limit"), str)
        and "one stochastic pair cannot prove a general causal effect" in contract["causal_limit"],
        "causal limitation",
    )
    check(
        record.get("sequence_id") == spec["sequence_id"]
        and record.get("source_sequence_id") == original["source_sequence_id"]
        and record.get("panel_range") == spec["panel_range"]
        and record.get("panel_count") == spec["panel_count"]
        and record.get("planned_output") == spec["planned_output"],
        "sequence identity/coverage/output path",
    )
    check(record.get("input_references") == [], "zero input references")
    check(record.get("cross_panel_gate_phrases") == original["cross_panel_gate_phrases"], "gate preservation")
    lines = record.get("prompt_lines", [])
    check(len(lines) == len(original["prompt_lines"]), "prompt line denominator")
    if len(lines) == len(original["prompt_lines"]):
        changed = [index for index, (before, after) in enumerate(zip(original["prompt_lines"], lines, strict=True)) if before != after]
        check(changed == [3], "exactly one changed line")
        check(lines[3] == REPLACEMENT, "exact zero-reference replacement")
        check(lines[:3] == original["prompt_lines"][:3] and lines[4:] == original["prompt_lines"][4:], "style/story/gate byte preservation")
    prompt_text = "\n".join(lines)
    check(record.get("prompt_text") == prompt_text, "prompt text/line equivalence")
    check(
        record.get("prompt_sha256") == hashlib.sha256(prompt_text.encode("utf-8")).hexdigest(),
        "prompt hash",
    )
    adult_safety = "fictional mature adults only" in prompt_text or (
        "fictional adults only" in prompt_text and "mature proportions" in prompt_text
    )
    practical_clothing = "practical non-sexualized clothing" in prompt_text or "practical non-sexualized clothes" in prompt_text
    safety_phrases = (
        "no child-coded features",
        "stable Soren light-brown/dark-blond hair and oatmeal coat",
        "stable Sigrid dark tied hair and plaid wrap",
    )
    check(
        adult_safety and practical_clothing and all(phrase in prompt_text for phrase in safety_phrases),
        "adult/identity/wardrobe safety phrases",
    )
    check(
        record.get("execution") is None
        and record.get("output") is None
        and record.get("human_review_state") == "PENDING"
        and record.get("accepted") is False,
        "preflight-only record",
    )
    boundary = document.get("boundary", {})
    check(boundary.get("permitted_product") == "openai_builtin_imagegen", "permitted product")
    check(
        all(value == 0 for key, value in boundary.items() if key != "permitted_product")
        and boundary.get("reference_uploads") == 0
        and boundary.get("direct_paid_provider_api_calls") == 0
        and boundary.get("current_executions") == 0
        and boundary.get("current_outputs") == 0,
        "zero upload/execution/output boundary",
    )
    return errors


def validate(s11: dict[str, Any], s01: dict[str, Any]) -> list[str]:
    source = load(SOURCE)
    errors = [*validate_document("S11", s11, source), *validate_document("S01", s01, source)]
    if sha256(S11) != S11_COMPATIBILITY_SHA256:
        errors.append("S11: emitted r1 bytes changed")
    # This validator authenticates the immutable preflight record. A later output
    # may exist only when a separate execution manifest binds it; filesystem
    # existence does not retroactively rewrite the preflight's zero-execution state.
    return errors


def self_test(s11: dict[str, Any], s01: dict[str, Any]) -> tuple[int, int]:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("S01", lambda value: value.__setitem__("record_id", "bad")),
        ("S01", lambda value: value.__setitem__("planning_structure", "AnimationShotPlan")),
        ("S01", lambda value: value.__setitem__("animation_shot_plan", {})),
        ("S01", lambda value: value["source_prompt_manifest"].__setitem__("sha256", "0" * 64)),
        ("S01", lambda value: value["comparison_contract"].__setitem__("changed_prompt_line_indexes_zero_based", [2, 3])),
        ("S01", lambda value: value["comparison_contract"].__setitem__("style_wording_changed", True)),
        ("S01", lambda value: value["comparison_contract"].__setitem__("input_reference_count_ablation", 1)),
        ("S01", lambda value: value["sequence"].__setitem__("input_references", ["leak"])),
        ("S01", lambda value: value["sequence"]["prompt_lines"].__setitem__(4, "changed story")),
        ("S01", lambda value: value["sequence"].__setitem__("prompt_sha256", "f" * 64)),
        ("S01", lambda value: value["sequence"].__setitem__("cross_panel_gate_phrases", [])),
        ("S01", lambda value: value["sequence"].__setitem__("execution", {})),
        ("S01", lambda value: value["sequence"].__setitem__("accepted", True)),
        ("S01", lambda value: value["boundary"].__setitem__("reference_uploads", 2)),
        ("S01", lambda value: value["boundary"].__setitem__("current_executions", 1)),
        ("S11", lambda value: value.__setitem__("record_id", "changed-s11")),
        ("S11", lambda value: value["sequence"].__setitem__("input_references", ["leak"])),
        ("S11", lambda value: value["sequence"]["prompt_lines"].__setitem__(3, "different replacement")),
    ]
    caught = 0
    source = load(SOURCE)
    for label, mutation in mutations:
        candidate = copy.deepcopy(s01 if label == "S01" else s11)
        mutation(candidate)
        caught += bool(validate_document(label, candidate, source))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    s11 = load(S11)
    s01 = load(S01)
    errors = validate(s11, s01)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(s11, s01)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "FAIL",
                "errors": errors,
                "self_test": f"{caught}/{total}" if args.self_test else None,
                "s11_compatibility_sha256": sha256(S11),
                "s01_manifest": S01.relative_to(ROOT).as_posix(),
                "s01_manifest_sha256": sha256(S01),
                "s01_prompt_sha256": s01.get("sequence", {}).get("prompt_sha256"),
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
