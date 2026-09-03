"""Compile a text-only reduced-palette CH05 complete-chapter control.

This arm intentionally uploads no reference pixels.  It isolates whether the
authorized character references are dominating requested style/density while
keeping the exact ComicPanelPlan story and cross-panel semantic gates.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "production/comic/run-manifests/ch05-complete-chapter-prompt-manifest-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
GATES = ROOT / "production/comic/contracts/ch05-cross-panel-semantic-gates-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-prompt-manifest-r1.json"

STYLE = (
    "Style/medium: low-density reduced-palette poster comic with crisp mature adventure drawing, broad matte gouache shapes, "
    "and restrained paper grain. Use only 3–5 dominant value/color masses per panel, one clean focal contour hierarchy, and "
    "large deliberate negative-space fields. Backgrounds are simplified silhouettes, never fully textured environments. "
    "Render localized physical detail only where the active clue or contact demands it. Avoid cloth weave, individual stones, "
    "foliage-by-foliage rendering, pore detail, crosshatching, photorealism, cinematic depth-of-field, glossy 3D rendering, "
    "grayscale wash, or text of any kind. Faces, hands, props, motion, and cause-and-effect must remain readable at 390-pixel width."
)
DENSITY = (
    "Reduced-palette control: action/reveal anchors may use five broad masses plus one localized contact texture; dialogue, "
    "deduction, travel, transition, and object inserts use three or four broad masses with visibly more negative space. Express "
    "mud, water, smoke, twine tension, leverage, weight shift, footfalls, and cloth drag through silhouette and overlap, not noise."
)
TEXT_ONLY = (
    "Text-only control: no input images or reference pixels are supplied. Reconstruct the two recurring fictional adults solely "
    "from the written continuity descriptions in this prompt. Do not introduce a younger-looking interpretation."
)
INVARIANT = (
    "Text-only reduced-palette arm invariant: exact specified cast; clearly mature fictional adults; stable Soren short-to-medium "
    "wavy light-brown/dark-blond swept-back hair and pale oatmeal coat; stable Sigrid dark-brown/near-black low bun or compact braid "
    "and dark blue-brown plaid wrap; no child-coded features, monsters, armor, magic, undeclared weapons, speech balloons, captions, "
    "labels, panel numbers, sound effects, logos, signatures, or watermark."
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform(lines: list[str], gate_phrases: list[str]) -> list[str]:
    result: list[str] = []
    inserted_style = False
    inserted_control = False
    for line in lines:
        if line.startswith("Input images:"):
            result.append(TEXT_ONLY)
            inserted_control = True
        elif line.startswith("Style/medium:"):
            result.extend((STYLE, DENSITY))
            inserted_style = True
        else:
            result.append(line)
    if not inserted_control or not inserted_style:
        raise ValueError("base prompt lacks required input/style lines")
    if gate_phrases:
        result.append("Cross-panel semantic gates (literal visual requirements): " + "; ".join(gate_phrases) + ".")
    result.append(INVARIANT)
    return result


def main() -> int:
    base = json.loads(BASE.read_text(encoding="utf-8"))
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    gate_document = json.loads(GATES.read_text(encoding="utf-8"))
    phrases_by_order: dict[int, list[str]] = {}
    for gate in gate_document["gates"]:
        for panel_id, phrase in gate["required_prompt_phrases"].items():
            phrases_by_order.setdefault(int(panel_id.rsplit("p", 1)[1]), []).append(phrase)

    expected = [row["display_order"] for row in plans["plans"]]
    covered: list[int] = []
    sequences: list[dict[str, Any]] = []
    for source in base["sequences"]:
        start, end = source["panel_range"]
        covered.extend(range(start, end + 1))
        gates = [phrase for order in range(start, end + 1) for phrase in phrases_by_order.get(order, [])]
        lines = transform(source["prompt_lines"], gates)
        prompt = "\n".join(lines)
        sequences.append(
            {
                "sequence_id": f"reduced-palette-text-control-{source['sequence_id']}",
                "source_sequence_id": source["sequence_id"],
                "panel_range": source["panel_range"],
                "panel_count": end - start + 1,
                "input_references": [],
                "cross_panel_gate_phrases": gates,
                "prompt_lines": lines,
                "prompt_text": prompt,
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "planned_output": (
                    "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/source-strips/"
                    f"{source['sequence_id']}-reduced-palette-text-control-r1.png"
                ),
                "execution": None,
                "output": None,
                "human_review_state": "PENDING",
                "accepted": False,
            }
        )
    if covered != expected or len(sequences) != 11:
        raise ValueError("text-only control must cover all 50 plans in canonical order")

    document = {
        "record_type": "CH05CompleteChapterReducedPaletteTextControlPromptManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-reduced-palette-text-control-prompts-r1",
        "state": "EXACT_PROMPTS_COMPILED_NOT_EXECUTED",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "sources": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}
            for path in (BASE, PLANS, GATES)
        ],
        "style_hypothesis": (
            "Removing all reference-pixel conditioning while enforcing three-to-five broad masses will materially reduce density; "
            "the tradeoff may be weaker cross-sequence face, hair, and wardrobe continuity."
        ),
        "selection_context": (
            "Complete-chapter causal control for reference-style lock-in, not a replacement, acceptance, commercial-clearance, "
            "or exact-production-base decision."
        ),
        "coverage": {
            "comic_panel_plans": 50,
            "sequence_requests": 11,
            "minimum_panels_per_request": 3,
            "maximum_panels_per_request": 5,
            "cross_panel_gates": 8,
            "required_gate_phrase_bindings": 15,
        },
        "density_control": {
            "broad_value_color_masses_per_panel": [3, 5],
            "anchor_mass_maximum": 5,
            "calm_beat_mass_range": [3, 4],
            "localized_texture_targets_per_panel_maximum": 1,
            "reference_pixel_conditioning": False,
        },
        "authorized_reference_hashes": [],
        "boundary": {
            "permitted_product": "openai_builtin_imagegen",
            "direct_paid_provider_api_calls": 0,
            "bfl_calls": 0,
            "reference_uploads": 0,
            "new_upload_classes": 0,
            "real_person_or_child_material": 0,
            "current_executions": 0,
            "current_outputs": 0,
            "accepted": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
        "sequences": sequences,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "sha256": sha256(OUTPUT),
        "sequences": len(sequences),
        "plans": len(covered),
        "reference_uses_planned": 0,
        "gate_phrase_bindings": sum(len(row["cross_panel_gate_phrases"]) for row in sequences),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
