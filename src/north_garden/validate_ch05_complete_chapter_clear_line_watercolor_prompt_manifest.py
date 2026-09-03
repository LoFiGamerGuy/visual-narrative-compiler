"""Validate the complete gated clear-line watercolor CH05 prompt arm."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from validate_ch05_cross_panel_semantic_gates import validate_prompt


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-prompt-manifest-r1.json"
GATES = ROOT / "production/comic/contracts/ch05-cross-panel-semantic-gates-r1.json"
ALLOWED = {"cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d", "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a", "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb"}


def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(doc: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []; check = lambda condition, message: None if condition else errors.append(message)
    check(doc.get("record_type") == "CH05CompleteChapterClearLineWatercolorPromptManifest", "record_type")
    check(doc.get("state") == "EXACT_PROMPTS_COMPILED_NOT_EXECUTED", "state")
    check(doc.get("planning_structure") == "ComicPanelPlan" and doc.get("animation_shot_plan") is None and doc.get("e_conte") is None, "planning boundary")
    check(doc.get("coverage") == {"comic_panel_plans": 50, "sequence_requests": 11, "minimum_panels_per_request": 3, "maximum_panels_per_request": 5, "cross_panel_gates": 8, "required_gate_phrase_bindings": 15}, "coverage")
    check(set(doc.get("authorized_reference_hashes", [])) == ALLOWED, "reference allowlist")
    sequences = doc.get("sequences", []); covered = [n for row in sequences for n in range(row.get("panel_range", [0, -1])[0], row.get("panel_range", [0, -1])[1] + 1)]
    check(len(sequences) == 11 and covered == list(range(1, 51)), "ordered sequence coverage")
    check([len(row.get("input_references", [])) for row in sequences] == [2, 2, 2, 2, 2, 2, 2, 3, 2, 2, 2], "reference distribution")
    check(sum(len(row.get("cross_panel_gate_phrases", [])) for row in sequences) == 15, "gate phrase count")
    for row in sequences:
        prompt = row.get("prompt_text", "")
        check(prompt == "\n".join(row.get("prompt_lines", [])) and hashlib.sha256(prompt.encode("utf-8")).hexdigest() == row.get("prompt_sha256"), f"prompt binding {row.get('sequence_id')}")
        for term in ("mature clear-line adventure webcomic", "white-paper breathing room", "No photorealism", "fictional adults", "no child-coded features"):
            check(term in prompt, f"style/safety term {row.get('sequence_id')}:{term}")
        check(row.get("execution") is None and row.get("output") is None and row.get("accepted") is False and row.get("human_review_state") == "PENDING", f"pre-execution state {row.get('sequence_id')}")
        for ref in row.get("input_references", []):
            check(ref.get("sha256") in ALLOWED, f"reference allowlist {row.get('sequence_id')}")
            if verify_files:
                path = ROOT / ref.get("path", ""); check(path.is_file() and sha256(path) == ref.get("sha256"), f"reference binding {row.get('sequence_id')}")
    contract = json.loads(GATES.read_text(encoding="utf-8")); check(not validate_prompt(contract, doc), "cross-panel gate validation")
    boundary = doc.get("boundary", {}); check(boundary.get("permitted_product") == "openai_builtin_imagegen" and all(boundary.get(key) == 0 for key in ("direct_paid_provider_api_calls", "bfl_calls", "new_upload_classes", "real_person_or_child_material", "current_executions", "current_outputs", "accepted", "commercially_cleared", "exact_production_base")), "boundary")
    if verify_files:
        for source in doc.get("sources", []):
            path = ROOT / source.get("path", ""); check(path.is_file() and sha256(path) == source.get("sha256"), f"source binding {source.get('path')}")
    return errors


def self_test(doc: dict[str, Any]) -> tuple[int, int]:
    mutations = [lambda d: d.__setitem__("state", "EXECUTED"), lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"), lambda d: d["coverage"].__setitem__("cross_panel_gates", 7), lambda d: d["sequences"].pop(), lambda d: d["sequences"][0].__setitem__("prompt_text", "tampered"), lambda d: d["sequences"][0]["prompt_lines"].pop(), lambda d: d["sequences"][0]["cross_panel_gate_phrases"].pop(), lambda d: d["sequences"][0]["input_references"][0].__setitem__("sha256", "0" * 64), lambda d: d["sequences"][0].__setitem__("accepted", True), lambda d: d["boundary"].__setitem__("direct_paid_provider_api_calls", 1)]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(doc); mutation(candidate); caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); doc = json.loads(MANIFEST.read_text(encoding="utf-8")); errors = validate(doc); caught = total = 0
    if args.self_test:
        caught, total = self_test(doc)
        if caught != total: errors.append(f"self-test {caught}/{total}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "sequences": len(doc.get("sequences", [])), "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True)); return 0 if not errors else 1


if __name__ == "__main__": raise SystemExit(main())
