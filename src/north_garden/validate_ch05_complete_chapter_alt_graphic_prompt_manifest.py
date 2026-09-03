"""Validate the complete lower-density graphic CH05 prompt arm before execution."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-complete-chapter-alt-graphic-prompt-manifest-r1.json"
ALLOWED = {
    "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d",
    "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a",
    "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(doc: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    check(doc.get("record_type") == "CH05CompleteChapterAlternateGraphicPromptManifest", "record_type")
    check(doc.get("state") == "EXACT_PROMPTS_COMPILED_NOT_EXECUTED", "state")
    check(doc.get("planning_structure") == "ComicPanelPlan", "planning_structure")
    check(doc.get("animation_shot_plan") is None and doc.get("e_conte") is None, "cross-medium fields")
    check(doc.get("coverage") == {"comic_panel_plans": 50, "sequence_requests": 11, "minimum_panels_per_request": 3, "maximum_panels_per_request": 5}, "coverage")
    check(set(doc.get("authorized_reference_hashes", [])) == ALLOWED, "reference allowlist")
    sequences = doc.get("sequences", [])
    check(len(sequences) == 11 and len({row.get("sequence_id") for row in sequences}) == 11, "sequences")
    covered = [number for row in sequences for number in range(row.get("panel_range", [0, -1])[0], row.get("panel_range", [0, -1])[1] + 1)]
    check(covered == list(range(1, 51)), "exact ordered coverage")
    check(all(row.get("panel_count") == row["panel_range"][1] - row["panel_range"][0] + 1 for row in sequences), "panel counts")
    check(all(row.get("prompt_text") == "\n".join(row.get("prompt_lines", [])) for row in sequences), "prompt text")
    check(all(hashlib.sha256(row.get("prompt_text", "").encode("utf-8")).hexdigest() == row.get("prompt_sha256") for row in sequences), "prompt hashes")
    required_terms = ["clean lower-density graphic adventure webcomic", "fictional adults only", "no child-coded features", "no monsters, armor, magic, or undeclared weapons", "no speech balloons"]
    for row in sequences:
        prompt = row.get("prompt_text", "")
        for term in required_terms:
            check(term in prompt, f"required prompt term {row.get('sequence_id')}:{term}")
        check(row.get("execution") is None and row.get("output") is None, f"pre-execution state {row.get('sequence_id')}")
        check(row.get("accepted") is False and row.get("human_review_state") == "PENDING", f"review state {row.get('sequence_id')}")
        for reference in row.get("input_references", []):
            check(reference.get("sha256") in ALLOWED, f"reference hash {row.get('sequence_id')}")
            if verify_files:
                path = ROOT / reference.get("path", "")
                check(path.is_file(), f"reference missing {reference.get('path')}")
                if path.is_file():
                    check(sha256(path) == reference.get("sha256"), f"reference mismatch {reference.get('path')}")
    boundary = doc.get("boundary", {})
    check(boundary.get("permitted_product") == "openai_builtin_imagegen", "permitted product")
    check(all(boundary.get(key) == 0 for key in ("direct_paid_provider_api_calls", "bfl_calls", "new_upload_classes", "real_person_or_child_material", "current_executions", "current_outputs", "accepted", "commercially_cleared", "exact_production_base")), "boundary")
    if verify_files:
        for source in doc.get("sources", []):
            path = ROOT / source.get("path", "")
            check(path.is_file() and sha256(path) == source.get("sha256"), f"source binding {source.get('path')}")
    return errors


def self_test(doc: dict[str, Any]) -> tuple[int, int]:
    mutations = [
        lambda d: d.__setitem__("state", "EXECUTED"),
        lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda d: d["coverage"].__setitem__("comic_panel_plans", 49),
        lambda d: d["authorized_reference_hashes"].append("0" * 64),
        lambda d: d["sequences"].pop(),
        lambda d: d["sequences"][1].__setitem__("panel_range", [5, 9]),
        lambda d: d["sequences"][0].__setitem__("prompt_text", "tampered"),
        lambda d: d["sequences"][0]["prompt_lines"].pop(),
        lambda d: d["sequences"][0].__setitem__("execution", {}),
        lambda d: d["sequences"][0].__setitem__("accepted", True),
        lambda d: d["sequences"][0]["input_references"][0].__setitem__("sha256", "0" * 64),
        lambda d: d["boundary"].__setitem__("direct_paid_provider_api_calls", 1),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(doc)
        mutation(candidate)
        caught += bool(validate(candidate, verify_files=False))
    return caught, len(mutations)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = validate(doc)
    caught = total = 0
    if args.self_test:
        caught, total = self_test(doc)
        if caught != total:
            errors.append(f"self-test {caught}/{total}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "sequences": len(doc.get("sequences", [])), "plans": doc.get("coverage", {}).get("comic_panel_plans"), "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
