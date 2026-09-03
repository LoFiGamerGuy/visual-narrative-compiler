"""Validate complete CH05 alternate graphic ImageGen execution evidence."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/run-manifests/ch05-complete-chapter-alt-graphic-execution-manifest-r1.json"
UNAVAILABLE = ["model", "endpoint", "provider_request_id", "usage", "cost_usd", "deterministic_seed"]
ALLOWED = {"cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d", "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a", "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb"}
ALLOWED_REFS = {
    ("experiments/review-packets/ch05-style-density-scale-exploration-r1/P050-wide-action-clean-graphic-r1.png", "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d"),
    ("experiments/review-packets/ch05-style-density-scale-exploration-r1/P040-medium-close-cel-painted-r1.png", "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a"),
    ("experiments/review-packets/ch05-style-density-scale-exploration-r1/P036-tall-lever-clear-line-corrected-r1.png", "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(doc: dict[str, Any], verify_files: bool = True) -> list[str]:
    errors: list[str] = []
    check = lambda condition, message: None if condition else errors.append(message)
    check(doc.get("record_type") == "CH05CompleteChapterAlternateGraphicExecutionManifest", "record_type")
    check(doc.get("state") == "EXECUTED_UNACCEPTED_PENDING_HUMAN_REVIEW", "state")
    check(doc.get("planning_structure") == "ComicPanelPlan", "planning_structure")
    check(doc.get("animation_shot_plan") is None and doc.get("e_conte") is None, "cross-medium fields")
    records = doc.get("records", [])
    check(len(records) == 11 and len({row.get("sequence_id") for row in records}) == 11, "records")
    covered = [number for row in records for number in range(row.get("panel_range", [0, -1])[0], row.get("panel_range", [0, -1])[1] + 1)]
    check(covered == list(range(1, 51)), "ordered panel coverage")
    check(sum(len(row.get("input_references", [])) for row in records) == 23, "reference uses")
    check(all(ref.get("sha256") in ALLOWED for row in records for ref in row.get("input_references", [])), "reference allowlist")
    check(all((ref.get("path"), ref.get("sha256")) in ALLOWED_REFS for row in records for ref in row.get("input_references", [])), "reference exact path/hash pairs")
    check([len(row.get("input_references", [])) for row in records] == [2, 2, 2, 2, 2, 2, 2, 3, 2, 2, 2], "reference distribution")
    check(all(hashlib.sha256(row.get("prompt_text", "").encode("utf-8")).hexdigest() == row.get("prompt_sha256") for row in records), "prompt hashes")
    check(len({row.get("execution", {}).get("tool_service_execution_id") for row in records}) == 11, "unique tool execution ids")
    prompt_path = ROOT / doc.get("input_prompt_manifest", {}).get("path", "")
    prompt_doc = json.loads(prompt_path.read_text(encoding="utf-8")) if verify_files and prompt_path.is_file() else None
    if prompt_doc is not None:
        prompt_rows = prompt_doc.get("sequences", [])
        check(len(prompt_rows) == len(records), "prompt record count")
        for record, prompt in zip(records, prompt_rows):
            for key in ("sequence_id", "source_sequence_id", "panel_range", "panel_count", "prompt_text", "prompt_sha256", "input_references"):
                check(record.get(key) == prompt.get(key), f"prompt parity {record.get('sequence_id')}:{key}")
            check(record.get("output", {}).get("path") == prompt.get("planned_output"), f"planned output parity {record.get('sequence_id')}")
    for row in records:
        execution = row.get("execution", {})
        check(execution.get("tool_mode") == "openai_builtin_imagegen_in_codex", f"tool mode {row.get('sequence_id')}")
        check(str(execution.get("tool_service_execution_id", "")).startswith("exec-"), f"tool execution id {row.get('sequence_id')}")
        check(execution.get("tool_service_execution_id_is_provider_request_id") is False, f"provider id distinction {row.get('sequence_id')}")
        check(execution.get("unavailable_fields") == UNAVAILABLE and all(execution.get(key) is None for key in UNAVAILABLE), f"unavailable contract {row.get('sequence_id')}")
        check(row.get("human_review_state") == "PENDING" and row.get("human_review_minutes") is None, f"review state {row.get('sequence_id')}")
        check(all(row.get(key) is False for key in ("accepted", "commercially_cleared", "exact_production_base", "generation_reproducible")), f"decision state {row.get('sequence_id')}")
        if verify_files:
            output = row.get("output", {})
            raw_path = output.get("path", "")
            check(isinstance(raw_path, str) and not Path(raw_path).is_absolute() and ".." not in Path(raw_path).parts, f"safe output path {row.get('sequence_id')}")
            path = ROOT / raw_path
            check(path.is_file(), f"output missing {row.get('sequence_id')}")
            if path.is_file():
                check(sha256(path) == output.get("sha256") and path.stat().st_size == output.get("bytes"), f"output binding {row.get('sequence_id')}")
                try:
                    with Image.open(path) as image:
                        check(image.format == "PNG" and list(image.size) == [output.get("width"), output.get("height")], f"output decode/dimensions {row.get('sequence_id')}")
                except OSError:
                    errors.append(f"output decode/dimensions {row.get('sequence_id')}")
                ignored = subprocess.run(["git", "check-ignore", "--quiet", "--", raw_path], cwd=ROOT).returncode == 0
                tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", raw_path], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
                check(ignored and not tracked, f"output ignored/untracked {row.get('sequence_id')}")
            for ref in row.get("input_references", []):
                ref_path = ROOT / ref.get("path", "")
                check(ref_path.is_file() and sha256(ref_path) == ref.get("sha256"), f"reference binding {row.get('sequence_id')}")
    batches = doc.get("timing_batches", [])
    check(len(batches) == 6 and round(sum(row.get("wall_seconds", 0) for row in batches), 1) == 954.3, "timing batches")
    expected_batches = {
        "b01-single": (91.5, ["alt-graphic-s01-opening-departure"]),
        "b02-parallel": (169.0, ["alt-graphic-s02-runnel-marker-trail", "alt-graphic-s03-listening-twine-ridge"]),
        "b03-parallel": (179.6, ["alt-graphic-s04-mill-reveal-bridge-warning", "alt-graphic-s05-creek-marker-drum"]),
        "b04-parallel": (184.7, ["alt-graphic-s06-ember-line-entry", "alt-graphic-s07-impossible-footprints-bell"]),
        "b05-parallel": (182.7, ["alt-graphic-s08-plank-tin-map", "alt-graphic-s09-deduction-retreat-cut"]),
        "b06-parallel": (146.8, ["alt-graphic-s10-silence-return", "alt-graphic-s11-farmhouse-reversal"]),
    }
    observed_batches = {row.get("timing_batch_id"): (row.get("wall_seconds"), row.get("member_sequence_ids")) for row in batches}
    check(observed_batches == expected_batches, "exact timing partition")
    for row in records:
        batch = expected_batches.get(row.get("execution", {}).get("timing_batch_id"))
        check(batch is not None and row["sequence_id"] in batch[1] and row["execution"].get("parallel_batch_wall_seconds") == batch[0], f"record timing membership {row.get('sequence_id')}")
    check([row["execution"].get("elapsed_seconds") for row in records] == [91.5] + [None] * 10, "per-output timing availability")
    summary = doc.get("summary", {})
    check(summary.get("sequence_outputs") == 11 and summary.get("comic_panel_plans_requested") == 50 and summary.get("authorized_reference_uses") == 23, "summary counts")
    check(summary.get("overlap_adjusted_tool_call_wall_seconds") == 954.3 and summary.get("per_output_elapsed_seconds_available") == 1 and "tool-call wall" in summary.get("timing_scope", ""), "summary timing")
    check(summary.get("direct_paid_provider_api_calls") == 0 and summary.get("paid_spend_usd") == 0.0, "summary spend")
    check(all(summary.get(key) == 0 for key in ("human_reviewed_outputs", "accepted_outputs", "commercially_cleared_outputs", "exact_production_base_outputs")), "summary decisions")
    check(doc.get("boundary") == {"permitted_product": "openai_builtin_imagegen", "direct_paid_provider_api_calls": 0, "bfl_calls": 0, "new_upload_classes": 0, "real_person_or_child_material": 0}, "boundary")
    if verify_files:
        source = doc.get("input_prompt_manifest", {})
        path = ROOT / source.get("path", "")
        check(path.is_file() and sha256(path) == source.get("sha256"), "prompt manifest binding")
    return errors


def self_test(doc: dict[str, Any]) -> tuple[int, int]:
    mutations = [
        lambda d: d.__setitem__("state", "ACCEPTED"),
        lambda d: d.__setitem__("planning_structure", "AnimationShotPlan"),
        lambda d: d["records"].pop(),
        lambda d: d["records"][0].__setitem__("panel_range", [2, 5]),
        lambda d: d["records"][0].__setitem__("prompt_text", "tampered"),
        lambda d: d["records"][0]["input_references"][0].__setitem__("sha256", "0" * 64),
        lambda d: d["records"][0]["execution"].__setitem__("model", "invented"),
        lambda d: d["records"][0]["execution"].__setitem__("tool_service_execution_id_is_provider_request_id", True),
        lambda d: d["records"][0].__setitem__("accepted", True),
        lambda d: d["timing_batches"][0].__setitem__("wall_seconds", 1.0),
        lambda d: d["summary"].__setitem__("paid_spend_usd", 1.0),
        lambda d: d["boundary"].__setitem__("bfl_calls", 1),
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
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "records": len(doc.get("records", [])), "self_test": f"{caught}/{total}" if args.self_test else None}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
