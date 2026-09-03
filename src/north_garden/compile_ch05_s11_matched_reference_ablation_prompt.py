"""Compile a one-request S11 reference-ablation control from the flat arm.

The prompt keeps the flat-gouache wording byte-for-byte except for replacing
the input-image instruction with a text-only statement.  No reference pixels
are attached.  This is narrower than the full reduced-palette arm, whose style
wording is also stricter, and therefore provides a less-confounded comparison.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-prompt-manifest-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-s11-flat-gouache-reference-ablation-prompt-r1.json"
TARGET = "flat-graphic-gouache-s11-farmhouse-reversal"
REPLACEMENT = (
    "Text-only ablation: no input images or reference pixels are supplied. Reconstruct the same two recurring fictional adults "
    "only from the written Soren and Sigrid continuity descriptions below; preserve mature proportions and the exact wardrobe."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_ablation(
    *,
    target: str,
    output: Path,
    record_type: str,
    record_id: str,
    ablation_sequence_id: str,
    planned_output: str,
    sequence_label: str,
) -> dict:
    """Compile one flat-gouache row with only its input-image line replaced."""
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = [row for row in source["sequences"] if row["sequence_id"] == target]
    if len(rows) != 1:
        raise ValueError(f"flat prompt manifest must contain exactly one {sequence_label} row")
    original = rows[0]
    lines = list(original["prompt_lines"])
    input_indexes = [index for index, line in enumerate(lines) if line.startswith("Input images:")]
    if input_indexes != [3]:
        raise ValueError(f"{sequence_label} input-image instruction moved or changed shape")
    lines[input_indexes[0]] = REPLACEMENT
    prompt = "\n".join(lines)
    changed_indexes = [index for index, (before, after) in enumerate(zip(original["prompt_lines"], lines, strict=True)) if before != after]
    if changed_indexes != [3]:
        raise ValueError("reference ablation must change exactly one prompt line")
    record = {
        "sequence_id": ablation_sequence_id,
        "source_sequence_id": original["source_sequence_id"],
        "panel_range": original["panel_range"],
        "panel_count": original["panel_count"],
        "input_references": [],
        "cross_panel_gate_phrases": original["cross_panel_gate_phrases"],
        "prompt_lines": lines,
        "prompt_text": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "planned_output": planned_output,
        "execution": None,
        "output": None,
        "human_review_state": "PENDING",
        "accepted": False,
    }
    document = {
        "record_type": record_type,
        "schema_version": "1.0",
        "record_id": record_id,
        "state": "EXACT_PROMPT_COMPILED_NOT_EXECUTED",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "source_prompt_manifest": {"path": SOURCE.relative_to(ROOT).as_posix(), "sha256": sha256(SOURCE)},
        "comparison_contract": {
            "source_sequence_id": target,
            "changed_prompt_line_indexes_zero_based": changed_indexes,
            "unchanged_prompt_line_count": len(lines) - len(changed_indexes),
            "changed_factor": "remove_reference_pixel_conditioning",
            "style_wording_changed": False,
            "story_or_gate_wording_changed": False,
            "input_reference_count_source": len(original["input_references"]),
            "input_reference_count_ablation": 0,
            "causal_limit": (
                "The necessary input-instruction replacement remains a wording change; one stochastic pair cannot prove a "
                "general causal effect, but is less confounded than the separate reduced-palette arm."
            ),
        },
        "sequence": record,
        "boundary": {
            "permitted_product": "openai_builtin_imagegen",
            "reference_uploads": 0,
            "direct_paid_provider_api_calls": 0,
            "bfl_calls": 0,
            "new_upload_classes": 0,
            "real_person_or_child_material": 0,
            "current_executions": 0,
            "current_outputs": 0,
            "accepted": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
    }
    output.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return document


def main() -> int:
    document = compile_ablation(
        target=TARGET,
        output=OUTPUT,
        record_type="CH05S11MatchedReferenceAblationPrompt",
        record_id="ng-ch05-s11-flat-gouache-reference-ablation-prompt-r1",
        ablation_sequence_id="flat-gouache-reference-ablation-s11-farmhouse-reversal",
        planned_output=(
            "experiments/review-packets/ch05-s11-flat-gouache-reference-ablation-r1/"
            "s11-farmhouse-reversal-flat-gouache-no-reference-r1.png"
        ),
        sequence_label="S11",
    )
    record = document["sequence"]
    print(json.dumps({
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "sha256": sha256(OUTPUT),
        "panel_count": record["panel_count"],
        "reference_uploads": 0,
        "changed_prompt_lines": len(document["comparison_contract"]["changed_prompt_line_indexes_zero_based"]),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
