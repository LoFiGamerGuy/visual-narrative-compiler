"""Validate the CH05 reduced-palette, text-only complete-chapter preflight."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from validate_ch05_cross_panel_semantic_gates import validate_contract, validate_prompt

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / (
    "production/comic/run-manifests/"
    "ch05-complete-chapter-reduced-palette-text-control-prompt-manifest-r1.json"
)
BASE = (
    ROOT
    / "production/comic/run-manifests/ch05-complete-chapter-prompt-manifest-r1.json"
)
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
GATES = ROOT / "production/comic/contracts/ch05-cross-panel-semantic-gates-r1.json"
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
EXPECTED_PANEL_COUNTS = [5, 4, 5, 5, 5, 5, 5, 5, 5, 3, 3]
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
COVERAGE = {
    "comic_panel_plans": 50,
    "sequence_requests": 11,
    "minimum_panels_per_request": 3,
    "maximum_panels_per_request": 5,
    "cross_panel_gates": 8,
    "required_gate_phrase_bindings": 15,
}
DENSITY_CONTROL = {
    "broad_value_color_masses_per_panel": [3, 5],
    "anchor_mass_maximum": 5,
    "calm_beat_mass_range": [3, 4],
    "localized_texture_targets_per_panel_maximum": 1,
    "reference_pixel_conditioning": False,
}
TEXT_ONLY = (
    "Text-only control: no input images or reference pixels are supplied. Reconstruct the two recurring fictional adults solely "
    "from the written continuity descriptions in this prompt. Do not introduce a younger-looking interpretation."
)
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
INVARIANT = (
    "Text-only reduced-palette arm invariant: exact specified cast; clearly mature fictional adults; stable Soren short-to-medium "
    "wavy light-brown/dark-blond swept-back hair and pale oatmeal coat; stable Sigrid dark-brown/near-black low bun or compact braid "
    "and dark blue-brown plaid wrap; no child-coded features, monsters, armor, magic, undeclared weapons, speech balloons, captions, "
    "labels, panel numbers, sound effects, logos, signatures, or watermark."
)
GATE_PREFIX = "Cross-panel semantic gates (literal visual requirements): "
IMAGE_REFERENCE_RE = re.compile(r"\bimage\s+[123]\b", re.IGNORECASE)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def safe_planned_output(relative: Any, source_sequence_id: Any) -> bool:
    if not isinstance(relative, str) or not isinstance(source_sequence_id, str):
        return False
    expected = (
        "experiments/review-packets/ch05-complete-chapter-reduced-palette-text-control-r1/"
        f"source-strips/{source_sequence_id}-reduced-palette-text-control-r1.png"
    )
    if relative != expected or "\\" in relative or ".." in Path(relative).parts:
        return False
    try:
        (ROOT / relative).resolve().relative_to(
            (ROOT / "experiments/review-packets").resolve()
        )
    except ValueError:
        return False
    return True


def expected_gate_phrases(contract: dict[str, Any]) -> dict[int, list[str]]:
    phrases: dict[int, list[str]] = {}
    for gate in contract.get("gates", []):
        for panel_id, phrase in gate.get("required_prompt_phrases", {}).items():
            order = int(panel_id.rsplit("p", 1)[1])
            phrases.setdefault(order, []).append(phrase)
    return phrases


def validate(document: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    contract = json.loads(GATES.read_text(encoding="utf-8"))
    gates_by_order = expected_gate_phrases(contract)

    check(
        document.get("record_type")
        == "CH05CompleteChapterReducedPaletteTextControlPromptManifest",
        "record_type",
    )
    check(document.get("schema_version") == "1.0", "schema_version")
    check(
        document.get("record_id")
        == "ng-ch05-complete-chapter-reduced-palette-text-control-prompts-r1",
        "record_id",
    )
    check(document.get("state") == "EXACT_PROMPTS_COMPILED_NOT_EXECUTED", "state")
    check(document.get("medium") == "comic", "medium")
    check(
        document.get("planning_structure") == "ComicPanelPlan"
        and document.get("animation_shot_plan") is None
        and document.get("e_conte") is None,
        "ComicPanelPlan-only boundary",
    )
    check(document.get("coverage") == COVERAGE, "coverage summary")
    check(document.get("density_control") == DENSITY_CONTROL, "density control")
    check(document.get("authorized_reference_hashes") == [], "zero authorized hashes")
    check(not validate_contract(contract), "gate contract validity")
    check(
        contract.get("summary")
        == {"gates": 8, "unique_affected_panels": 13, "required_prompt_bindings": 15},
        "gate contract denominator",
    )

    rows = document.get("sequences", [])
    check(len(rows) == 11, "sequence denominator")
    check([row.get("panel_range") for row in rows] == EXPECTED_RANGES, "ordered ranges")
    check(
        [row.get("panel_count") for row in rows] == EXPECTED_PANEL_COUNTS,
        "panel-count distribution",
    )
    check(
        [row.get("source_sequence_id") for row in rows] == EXPECTED_SOURCE_SEQUENCE_IDS,
        "source sequence order",
    )
    check(
        [row.get("sequence_id") for row in rows]
        == [
            f"reduced-palette-text-control-{value}"
            for value in EXPECTED_SOURCE_SEQUENCE_IDS
        ],
        "sequence IDs/order",
    )
    covered = [
        order
        for row in rows
        for order in range(
            row.get("panel_range", [0, -1])[0],
            row.get("panel_range", [0, -1])[1] + 1,
        )
    ]
    check(covered == list(range(1, 51)), "exact P001-P050 coverage")
    check(
        all(row.get("input_references") == [] for row in rows),
        "zero input references",
    )

    observed_gate_phrases: list[str] = []
    for index, row in enumerate(rows):
        sequence_id = row.get("sequence_id", f"index-{index}")
        prompt = row.get("prompt_text", "")
        lines = row.get("prompt_lines", [])
        start, end = EXPECTED_RANGES[index]
        assigned_gates = [
            phrase
            for order in range(start, end + 1)
            for phrase in gates_by_order.get(order, [])
        ]
        observed_gate_phrases.extend(row.get("cross_panel_gate_phrases", []))
        check(
            row.get("cross_panel_gate_phrases") == assigned_gates,
            f"exact gate bindings {sequence_id}",
        )
        expected_gate_line = GATE_PREFIX + "; ".join(assigned_gates) + "."
        gate_lines = [
            line
            for line in lines
            if isinstance(line, str) and line.startswith(GATE_PREFIX)
        ]
        check(
            gate_lines == ([expected_gate_line] if assigned_gates else []),
            f"gate prompt line {sequence_id}",
        )
        check(
            isinstance(prompt, str)
            and isinstance(lines, list)
            and all(isinstance(line, str) for line in lines)
            and prompt == "\n".join(lines)
            and hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            == row.get("prompt_sha256"),
            f"prompt/hash binding {sequence_id}",
        )
        check(TEXT_ONLY in lines, f"explicit zero-reference instruction {sequence_id}")
        check(
            STYLE in lines and DENSITY in lines,
            f"explicit 3-5-mass style {sequence_id}",
        )
        check(
            lines and lines[-1] == INVARIANT,
            f"repeated adult continuity invariant {sequence_id}",
        )
        check(
            "clearly mature fictional adults" in prompt
            and "Soren short-to-medium wavy light-brown/dark-blond swept-back hair and pale oatmeal coat"
            in prompt
            and "Sigrid dark-brown/near-black low bun or compact braid and dark blue-brown plaid wrap"
            in prompt,
            f"mature adult hair/wardrobe continuity {sequence_id}",
        )
        check(
            "no child-coded features, monsters, armor, magic, undeclared weapons"
            in prompt,
            f"no-child/no-new-canon boundary {sequence_id}",
        )
        check(
            "speech balloons, captions, labels, panel numbers, sound effects, logos, signatures, or watermark"
            in prompt,
            f"text/mark ban {sequence_id}",
        )
        check(
            "Input images:" not in prompt, f"no input-images instruction {sequence_id}"
        )
        check(
            not IMAGE_REFERENCE_RE.search(prompt),
            f"no Image 1/2/3 phrase {sequence_id}",
        )
        check(
            safe_planned_output(
                row.get("planned_output"), row.get("source_sequence_id")
            ),
            f"planned output boundary {sequence_id}",
        )
        if verify_files and isinstance(row.get("planned_output"), str):
            check(
                ignored_untracked(row["planned_output"]),
                f"planned output ignored/untracked {sequence_id}",
            )
        check(
            row.get("execution") is None
            and row.get("output") is None
            and row.get("human_review_state") == "PENDING"
            and row.get("accepted") is False,
            f"unexecuted/unaccepted row state {sequence_id}",
        )

    expected_flat = [
        phrase
        for start, end in EXPECTED_RANGES
        for order in range(start, end + 1)
        for phrase in gates_by_order.get(order, [])
    ]
    check(len(contract.get("gates", [])) == 8, "exact eight gates")
    check(
        len(observed_gate_phrases) == 15 and observed_gate_phrases == expected_flat,
        "exact fifteen gate phrase bindings",
    )
    check(not validate_prompt(contract, document), "cross-panel prompt gate validation")

    expected_sources = [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}
        for path in (BASE, PLANS, GATES)
    ]
    check(document.get("sources") == expected_sources, "source bindings")
    if verify_files:
        for source in document.get("sources", []):
            path = ROOT / source.get("path", "")
            check(
                path.is_file() and sha256(path) == source.get("sha256"),
                f"source hash {source.get('path')}",
            )

    boundary = document.get("boundary", {})
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
                "reference_uploads",
                "new_upload_classes",
                "real_person_or_child_material",
                "current_executions",
                "current_outputs",
                "accepted",
                "commercially_cleared",
                "exact_production_base",
            )
        ),
        "zero execution/upload/spend/acceptance authority",
    )
    return errors


def rebind_prompt(row: dict[str, Any], prompt: str) -> None:
    row["prompt_text"] = prompt
    row["prompt_lines"] = prompt.splitlines()
    row["prompt_sha256"] = hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def mutate_prompt(document: dict[str, Any], index: int, old: str, new: str) -> None:
    row = document["sequences"][index]
    rebind_prompt(row, row["prompt_text"].replace(old, new))


def self_test(document: dict[str, Any]) -> tuple[int, int]:
    fake_reference = {
        "reference_id": "forbidden",
        "path": "experiments/forbidden.png",
        "sha256": "0" * 64,
    }
    mutations: list[Callable[[dict[str, Any]], None]] = [
        lambda value: value.__setitem__("state", "EXECUTED"),
        lambda value: value.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda value: value.__setitem__("animation_shot_plan", {}),
        lambda value: value.__setitem__("e_conte", {}),
        lambda value: value["coverage"].__setitem__("cross_panel_gates", 7),
        lambda value: value["density_control"].__setitem__(
            "broad_value_color_masses_per_panel", [3, 6]
        ),
        lambda value: value["authorized_reference_hashes"].append("0" * 64),
        lambda value: value["sequences"][0]["input_references"].append(fake_reference),
        lambda value: value["sequences"].pop(),
        lambda value: value["sequences"].reverse(),
        lambda value: value["sequences"][0].__setitem__("panel_range", [2, 5]),
        lambda value: value["sequences"][0].__setitem__("sequence_id", "duplicate"),
        lambda value: value["sequences"][0].__setitem__("prompt_sha256", "0" * 64),
        lambda value: value["sequences"][0]["prompt_lines"].pop(),
        lambda value: mutate_prompt(
            value, 0, "Text-only control:", "Image 1 reference:"
        ),
        lambda value: mutate_prompt(value, 0, TEXT_ONLY, "No reference details."),
        lambda value: mutate_prompt(
            value,
            0,
            "3–5 dominant value/color masses",
            "3–8 dominant value/color masses",
        ),
        lambda value: mutate_prompt(
            value, 0, "clearly mature fictional adults", "fictional characters"
        ),
        lambda value: mutate_prompt(
            value,
            0,
            "Soren short-to-medium wavy light-brown/dark-blond swept-back hair and pale oatmeal coat",
            "Soren continuity unspecified",
        ),
        lambda value: mutate_prompt(
            value,
            0,
            "Sigrid dark-brown/near-black low bun or compact braid and dark blue-brown plaid wrap",
            "Sigrid continuity unspecified",
        ),
        lambda value: mutate_prompt(
            value,
            0,
            "no child-coded features, monsters, armor, magic, undeclared weapons",
            "no monsters",
        ),
        lambda value: mutate_prompt(
            value,
            0,
            "speech balloons, captions, labels, panel numbers, sound effects, logos, signatures, or watermark",
            "no captions",
        ),
        lambda value: value["sequences"][0]["cross_panel_gate_phrases"].pop(),
        lambda value: value["sequences"][0].__setitem__(
            "planned_output", "production/comic/leak.png"
        ),
        lambda value: value["sequences"][0].__setitem__("execution", {}),
        lambda value: value["sequences"][0].__setitem__("output", {}),
        lambda value: value["sequences"][0].__setitem__("accepted", True),
        lambda value: value["sources"][0].__setitem__("sha256", "0" * 64),
        lambda value: value["boundary"].__setitem__("reference_uploads", 1),
        lambda value: value["boundary"].__setitem__(
            "direct_paid_provider_api_calls", 1
        ),
        lambda value: value["boundary"].__setitem__("current_outputs", 1),
        lambda value: value["boundary"].__setitem__("commercially_cleared", 1),
    ]
    caught = 0
    for mutation in mutations:
        candidate = copy.deepcopy(document)
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
                "gates": document.get("coverage", {}).get("cross_panel_gates"),
                "gate_phrase_bindings": sum(
                    len(row.get("cross_panel_gate_phrases", []))
                    for row in document.get("sequences", [])
                ),
                "reference_uses": sum(
                    len(row.get("input_references", []))
                    for row in document.get("sequences", [])
                ),
                "self_test": f"{caught}/{total}" if args.self_test else None,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
