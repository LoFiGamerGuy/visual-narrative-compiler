"""Validate the complete gated premium cel-painted CH05 prompt arm."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from validate_ch05_cross_panel_semantic_gates import validate_prompt


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-prompt-manifest-r1.json"
BASE = ROOT / "production/comic/run-manifests/ch05-complete-chapter-prompt-manifest-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
GATES = ROOT / "production/comic/contracts/ch05-cross-panel-semantic-gates-r1.json"
REFERENCES = {
    "p050_dual_identity_action": {
        "path": "experiments/review-packets/ch05-style-density-scale-exploration-r1/P050-wide-action-clean-graphic-r1.png",
        "sha256": "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d",
    },
    "p040_sigrid_face": {
        "path": "experiments/review-packets/ch05-style-density-scale-exploration-r1/P040-medium-close-cel-painted-r1.png",
        "sha256": "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a",
    },
    "p036_composition_only": {
        "path": "experiments/review-packets/ch05-style-density-scale-exploration-r1/P036-tall-lever-clear-line-corrected-r1.png",
        "sha256": "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb",
    },
}
ALLOWED = {row["sha256"] for row in REFERENCES.values()}
COVERAGE = {
    "comic_panel_plans": 50,
    "sequence_requests": 11,
    "minimum_panels_per_request": 3,
    "maximum_panels_per_request": 5,
    "cross_panel_gates": 8,
    "required_gate_phrase_bindings": 15,
}
STYLE_TERMS = (
    "premium cel-painted fantasy-adventure webcomic",
    "bold clean contours",
    "two-tier cel shadows",
    "selective atmospheric background paint",
    "reduced microtexture",
    "strong silhouettes",
    "cinematic causal action",
    "No photorealism",
    "no decorative hatching",
    "no text of any kind",
    "clearly mature fictional adults",
    "no child-coded features",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(doc: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    check(doc.get("record_type") == "CH05CompleteChapterPremiumCelPromptManifest", "record_type")
    check(doc.get("schema_version") == "1.0", "schema_version")
    check(doc.get("record_id") == "ng-ch05-complete-chapter-premium-cel-prompts-r1", "record_id")
    check(doc.get("state") == "EXACT_PROMPTS_COMPILED_NOT_EXECUTED", "state")
    check(doc.get("medium") == "comic", "medium")
    check(
        doc.get("planning_structure") == "ComicPanelPlan"
        and doc.get("animation_shot_plan") is None
        and doc.get("e_conte") is None,
        "planning boundary",
    )
    check(doc.get("coverage") == COVERAGE, "coverage")
    check(set(doc.get("authorized_reference_hashes", [])) == ALLOWED, "reference allowlist")

    sequences = doc.get("sequences", [])
    covered = [
        number
        for row in sequences
        for number in range(row.get("panel_range", [0, -1])[0], row.get("panel_range", [0, -1])[1] + 1)
    ]
    check(len(sequences) == 11 and covered == list(range(1, 51)), "ordered sequence coverage")
    check(
        [row.get("panel_count") for row in sequences] == [5, 4, 5, 5, 5, 5, 5, 5, 5, 3, 3],
        "panel count distribution",
    )
    check(
        [len(row.get("input_references", [])) for row in sequences] == [2, 2, 2, 2, 2, 2, 2, 3, 2, 2, 2],
        "reference distribution",
    )
    check(sum(len(row.get("input_references", [])) for row in sequences) == 23, "reference use count")
    check(sum(len(row.get("cross_panel_gate_phrases", [])) for row in sequences) == 15, "gate phrase count")

    for row in sequences:
        sequence_id = row.get("sequence_id")
        prompt = row.get("prompt_text", "")
        check(isinstance(sequence_id, str) and sequence_id.startswith("premium-cel-s"), f"sequence id {sequence_id}")
        check(
            prompt == "\n".join(row.get("prompt_lines", []))
            and hashlib.sha256(prompt.encode("utf-8")).hexdigest() == row.get("prompt_sha256"),
            f"prompt binding {sequence_id}",
        )
        for term in STYLE_TERMS:
            check(term in prompt, f"style/safety term {sequence_id}:{term}")
        check("transparent watercolor" not in prompt and "white-paper breathing room" not in prompt, f"style separation {sequence_id}")
        check(
            row.get("planned_output")
            == "experiments/review-packets/ch05-complete-chapter-premium-cel-r1/source-strips/"
            f"{row.get('source_sequence_id')}-premium-cel-r1.png",
            f"planned output {sequence_id}",
        )
        check(
            row.get("execution") is None
            and row.get("output") is None
            and row.get("accepted") is False
            and row.get("human_review_state") == "PENDING",
            f"pre-execution state {sequence_id}",
        )
        for reference in row.get("input_references", []):
            reference_id = reference.get("reference_id")
            expected = REFERENCES.get(reference_id)
            check(
                expected is not None
                and reference.get("path") == expected["path"]
                and reference.get("sha256") == expected["sha256"],
                f"reference allowlist {sequence_id}:{reference_id}",
            )
            if verify_files and expected is not None:
                path = ROOT / expected["path"]
                check(path.is_file() and sha256(path) == expected["sha256"], f"reference binding {sequence_id}:{reference_id}")

    contract = json.loads(GATES.read_text(encoding="utf-8"))
    check(not validate_prompt(contract, doc), "cross-panel gate validation")
    check(contract.get("summary") == {"gates": 8, "unique_affected_panels": 13, "required_prompt_bindings": 15}, "gate contract summary")

    boundary = doc.get("boundary", {})
    check(
        boundary.get("permitted_product") == "openai_builtin_imagegen"
        and all(
            boundary.get(key) == 0
            for key in (
                "direct_paid_provider_api_calls",
                "bfl_calls",
                "new_upload_classes",
                "real_person_or_child_material",
                "current_executions",
                "current_outputs",
                "accepted",
                "commercially_cleared",
                "exact_production_base",
            )
        ),
        "boundary",
    )
    expected_sources = [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}
        for path in (BASE, PLANS, GATES)
    ]
    check(doc.get("sources") == expected_sources, "source list")
    if verify_files:
        for source in doc.get("sources", []):
            path = ROOT / source.get("path", "")
            check(path.is_file() and sha256(path) == source.get("sha256"), f"source binding {source.get('path')}")
    return errors


def self_test(doc: dict[str, Any]) -> tuple[int, int]:
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "EXECUTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("e_conte", {}),
        lambda value: value["coverage"].__setitem__("cross_panel_gates", 7),
        lambda value: value["sequences"].pop(),
        lambda value: value["sequences"][0].__setitem__("prompt_text", "tampered"),
        lambda value: value["sequences"][0]["prompt_lines"].pop(),
        lambda value: value["sequences"][0]["cross_panel_gate_phrases"].pop(),
        lambda value: value["sequences"][0]["input_references"][0].__setitem__("sha256", "0" * 64),
        lambda value: value["sequences"][0]["input_references"][0].__setitem__("path", "experiments/forbidden.png"),
        lambda value: value["sequences"][0].__setitem__("accepted", True),
        lambda value: value["sequences"][0].__setitem__("planned_output", "experiments/wrong.png"),
        lambda value: value["sequences"][0].__setitem__(
            "prompt_text", value["sequences"][0]["prompt_text"].replace("two-tier cel shadows", "generic shading")
        ),
        lambda value: value["boundary"].__setitem__("direct_paid_provider_api_calls", 1),
        lambda value: value["boundary"].__setitem__("new_upload_classes", 1),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(doc)
        mutation(candidate)
        caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
                "sequences": len(document.get("sequences", [])),
                "plans": document.get("coverage", {}).get("comic_panel_plans"),
                "reference_uses": sum(len(row.get("input_references", [])) for row in document.get("sequences", [])),
                "gate_phrase_bindings": sum(
                    len(row.get("cross_panel_gate_phrases", [])) for row in document.get("sequences", [])
                ),
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
