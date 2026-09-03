"""Compile a gated, complete CH05 mature clear-line watercolor style arm."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "production/comic/run-manifests/ch05-complete-chapter-prompt-manifest-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
GATES = ROOT / "production/comic/contracts/ch05-cross-panel-semantic-gates-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-prompt-manifest-r1.json"
REFERENCES = {
    "p050_dual_identity_action": {"path": "experiments/review-packets/ch05-style-density-scale-exploration-r1/P050-wide-action-clean-graphic-r1.png", "sha256": "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d"},
    "p040_sigrid_face": {"path": "experiments/review-packets/ch05-style-density-scale-exploration-r1/P040-medium-close-cel-painted-r1.png", "sha256": "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a"},
    "p036_composition_only": {"path": "experiments/review-packets/ch05-style-density-scale-exploration-r1/P036-tall-lever-clear-line-corrected-r1.png", "sha256": "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb"},
}
STYLE = "Style/medium: mature clear-line adventure webcomic with crisp dark-brown ink contours and controlled transparent watercolor washes; broad low-detail color shapes, white-paper breathing room, restrained cold wet palette, selective facial modeling, and strong silhouettes. No photorealism, decorative crosshatching, or dense microtexture. Preserve readable action and expressions at 390-pixel phone width."
STYLE_RULE = "Style-arm control: treat detailed reveal/action anchors with selective wash depth while dialogue, deduction, travel, and object inserts use visibly fewer marks and larger quiet shapes; physical weight, mud, water, cloth, smoke, twine, leverage, and footfalls remain causal rather than decorative."


def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def transform(lines: list[str], addenda: list[str]) -> list[str]:
    result: list[str] = []; inserted = False
    for line in lines:
        if line.startswith("Style/medium:"):
            result.extend([STYLE, STYLE_RULE]); inserted = True
        else:
            result.append(line)
    if not inserted: raise ValueError("base prompt lacks Style/medium line")
    if addenda: result.append("Cross-panel semantic gates (literal visual requirements): " + "; ".join(addenda) + ".")
    result.append("Clear-line arm invariant: exact specified cast; clearly mature fictional adults; stable Soren light-brown/dark-blond hair and oatmeal coat; stable Sigrid dark tied hair and plaid wrap; no child-coded features, monsters, armor, magic, undeclared weapons, speech balloons, captions, labels, panel numbers, logos, signatures, or watermark.")
    return result


def main() -> int:
    base, plans, gate_doc = (json.loads(path.read_text(encoding="utf-8")) for path in (BASE, PLANS, GATES))
    phrases_by_order: dict[int, list[str]] = {}
    for gate in gate_doc["gates"]:
        for panel_id, phrase in gate["required_prompt_phrases"].items():
            phrases_by_order.setdefault(int(panel_id.rsplit("p", 1)[1]), []).append(phrase)
    expected = [row["display_order"] for row in plans["plans"]]
    covered: list[int] = []; sequences: list[dict[str, Any]] = []
    for source in base["sequences"]:
        start, end = source["panel_range"]; covered.extend(range(start, end + 1))
        addenda = [phrase for order in range(start, end + 1) for phrase in phrases_by_order.get(order, [])]
        lines = transform(source["prompt_lines"], addenda); prompt = "\n".join(lines)
        references = []
        for reference_id in source["reference_ids"]:
            ref = REFERENCES[reference_id]; path = ROOT / ref["path"]
            if not path.is_file() or sha256(path) != ref["sha256"]: raise ValueError(f"authorized reference mismatch: {reference_id}")
            references.append({"reference_id": reference_id, **ref})
        sequences.append({"sequence_id": f"clear-line-watercolor-{source['sequence_id']}", "source_sequence_id": source["sequence_id"], "panel_range": source["panel_range"], "panel_count": end - start + 1, "input_references": references, "cross_panel_gate_phrases": addenda, "prompt_lines": lines, "prompt_text": prompt, "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(), "planned_output": f"experiments/review-packets/ch05-complete-chapter-clear-line-watercolor-r1/source-strips/{source['sequence_id']}-clear-line-watercolor-r1.png", "execution": None, "output": None, "human_review_state": "PENDING", "accepted": False})
    if covered != expected or len(sequences) != 11: raise ValueError("prompt arm must cover 50 plans in canonical order")
    document = {"record_type": "CH05CompleteChapterClearLineWatercolorPromptManifest", "schema_version": "1.0", "record_id": "ng-ch05-complete-chapter-clear-line-watercolor-prompts-r1", "state": "EXACT_PROMPTS_COMPILED_NOT_EXECUTED", "medium": "comic", "planning_structure": "ComicPanelPlan", "animation_shot_plan": None, "e_conte": None, "sources": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in (BASE, PLANS, GATES)], "style_hypothesis": "A distinctly lower-mark clear-line watercolor chapter plus explicit cross-panel gates will preserve hair/wardrobe and improve phone-scale rhythm while reducing the semantic regressions found in the alternate graphic arm.", "selection_context": "r6 remains the strongest current route; this is a complete-chapter hardening/style-separation experiment, not a preselected replacement.", "coverage": {"comic_panel_plans": 50, "sequence_requests": 11, "minimum_panels_per_request": 3, "maximum_panels_per_request": 5, "cross_panel_gates": 8, "required_gate_phrase_bindings": 15}, "authorized_reference_hashes": sorted({row["sha256"] for row in REFERENCES.values()}), "sequences": sequences, "boundary": {"permitted_product": "openai_builtin_imagegen", "direct_paid_provider_api_calls": 0, "bfl_calls": 0, "new_upload_classes": 0, "real_person_or_child_material": 0, "current_executions": 0, "current_outputs": 0, "accepted": 0, "commercially_cleared": 0, "exact_production_base": 0}}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True); OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT), "sequences": len(sequences), "plans": len(covered), "reference_uses_planned": sum(len(row["input_references"]) for row in sequences), "gate_phrase_bindings": sum(len(row["cross_panel_gate_phrases"]) for row in sequences)}, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
