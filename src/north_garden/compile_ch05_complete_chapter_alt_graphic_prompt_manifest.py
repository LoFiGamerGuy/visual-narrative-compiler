"""Compile exact prompts for a complete lower-density graphic CH05 style arm."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "production/comic/run-manifests/ch05-complete-chapter-prompt-manifest-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-alt-graphic-prompt-manifest-r1.json"
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
STYLE_LINE = (
    "Style/medium: clean lower-density graphic adventure webcomic; confident clear contours, simplified shadow shapes, "
    "restrained six-to-eight-color cold wet palette, selective cel-painted facial modeling, minimal texture, and no decorative hatching. "
    "Prioritize silhouettes, expressions, hands, props, and causal motion at 390-pixel phone width. Detailed anchors may use one extra value layer; "
    "dialogue/deduction/inserts must stay visibly calmer."
)
STYLE_RULE = (
    "Alternate-style control: preserve the exact story and current CH05 fictional-adult hair/wardrobe identities, but do not imitate the painterly density "
    "of the references. Use large readable shapes, decisive negative space, strong directional staging, and grounded weight shift, leverage, mud, water, cloth, smoke, twine, and footfall motion."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def transform(lines: list[str]) -> list[str]:
    result = []
    inserted = False
    for line in lines:
        if line.startswith("Style/medium:"):
            result.extend([STYLE_LINE, STYLE_RULE])
            inserted = True
        else:
            result.append(line)
    if not inserted:
        raise ValueError("base prompt lacks style line")
    result.append(
        "Alternate-arm invariant: exact specified cast per panel; fictional adults only; no child-coded features; "
        "no monsters, armor, magic, or undeclared weapons in CH05; no speech balloons, captions, labels, panel numbers, logos, signatures, or watermark."
    )
    return result


def main() -> int:
    base, plans = load(BASE), load(PLANS)
    expected_orders = [row["display_order"] for row in plans["plans"]]
    covered = []
    sequences = []
    for source in base["sequences"]:
        start, end = source["panel_range"]
        covered.extend(range(start, end + 1))
        prompt_lines = transform(source["prompt_lines"])
        prompt_text = "\n".join(prompt_lines)
        references = []
        for reference_id in source["reference_ids"]:
            reference = REFERENCES[reference_id]
            path = ROOT / reference["path"]
            if not path.is_file() or sha256(path) != reference["sha256"]:
                raise ValueError(f"authorized reference mismatch: {reference_id}")
            references.append({"reference_id": reference_id, **reference})
        sequences.append({
            "sequence_id": f"alt-graphic-{source['sequence_id']}",
            "source_sequence_id": source["sequence_id"],
            "panel_range": source["panel_range"],
            "panel_count": end - start + 1,
            "input_references": references,
            "prompt_lines": prompt_lines,
            "prompt_text": prompt_text,
            "prompt_sha256": hashlib.sha256(prompt_text.encode("utf-8")).hexdigest(),
            "planned_output": f"experiments/review-packets/ch05-complete-chapter-alt-graphic-r1/source-strips/{source['sequence_id']}-alt-graphic-r1.png",
            "execution": None,
            "output": None,
            "human_review_state": "PENDING",
            "accepted": False,
        })
    if covered != expected_orders or len(sequences) != 11:
        raise ValueError("alternate prompts must cover all 50 plans exactly once in 11 sequences")
    document = {
        "record_type": "CH05CompleteChapterAlternateGraphicPromptManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-alt-graphic-prompts-r1",
        "state": "EXACT_PROMPTS_COMPILED_NOT_EXECUTED",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "sources": [
            {"path": BASE.relative_to(ROOT).as_posix(), "sha256": sha256(BASE)},
            {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha256(PLANS)},
        ],
        "style_hypothesis": "A complete low-density graphic pass will improve phone-scale role/action clarity and rhythm while retaining current adult identities and causal storytelling.",
        "comparison_baseline": "CH05 complete-chapter r6 remains immutable and selected only as the current owner-review baseline.",
        "coverage": {"comic_panel_plans": 50, "sequence_requests": 11, "minimum_panels_per_request": 3, "maximum_panels_per_request": 5},
        "authorized_reference_hashes": sorted({row["sha256"] for row in REFERENCES.values()}),
        "sequences": sequences,
        "boundary": {
            "permitted_product": "openai_builtin_imagegen",
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
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), "sequences": len(sequences), "plans": len(covered), "reference_uses_planned": sum(len(row["input_references"]) for row in sequences)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
