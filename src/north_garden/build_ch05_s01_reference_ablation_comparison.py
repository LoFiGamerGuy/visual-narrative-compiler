"""Build the instrumented S01 matched-reference-ablation comparison."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from build_ch05_r6_alt_graphic_comparison import metric
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / "production/comic/run-manifests/ch05-s01-flat-gouache-reference-ablation-prompt-r1.json"
FLAT_EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-execution-manifest-r1.json"
TEXT_EXECUTION = ROOT / "production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-execution-manifest-r1.json"
EXECUTION = ROOT / "production/comic/run-manifests/ch05-s01-flat-gouache-reference-ablation-execution-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-s01-flat-gouache-reference-ablation-comparison-r1.json"
OUT = ROOT / "experiments/review-packets/ch05-s01-flat-gouache-reference-ablation-r1/review"
NATIVE = OUT / "s01-reference-ablation-three-column-native-r1.png"
PHONE = OUT / "s01-reference-ablation-three-column-390px-r1.png"
ABLATION_LOCAL = ROOT / "experiments/review-packets/ch05-s01-flat-gouache-reference-ablation-r1/s01-opening-departure-flat-gouache-no-reference-r1.png"
ABLATION_GLOBAL = Path("C:/Users/gosne/.codex/generated_images/01a05d7c-0ac3-7872-8fa8-3fb9c14f6eaa/exec-1fc3bdb1-219d-43f2-b262-c6742d434ba9.png")
EXECUTION_ID = "exec-1fc3bdb1-219d-43f2-b262-c6742d434ba9"
OUTPUT_SHA256 = "10c8d88164f5ce00227001a0b76f9f32eb4e9ef2e5b116ec61f103a334974af6"
LABELS = {
    "flat_with_authorized_refs": "FLAT + AUTHORIZED REFS",
    "matched_flat_no_reference": "MATCHED FLAT / NO REFS",
    "stricter_reduced_palette_no_reference": "STRICTER REDUCED / NO REFS",
}
ORDER = tuple(LABELS)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def bind(path: Path) -> dict[str, Any]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def open_rgb(path: Path) -> Image.Image:
    with Image.open(path) as opened:
        return opened.convert("RGB")


def image_binding(path: Path) -> dict[str, Any]:
    with Image.open(path) as opened:
        width, height = opened.size
        if opened.format != "PNG":
            raise ValueError(f"not PNG: {path}")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
        "width": width,
        "height": height,
        "bytes": path.stat().st_size,
    }


def artifact(path: Path) -> dict[str, Any]:
    return {**image_binding(path), "repository_state": "IGNORED_LOCAL_REVIEW_ARTIFACT"}


def find_s01(document: dict[str, Any]) -> dict[str, Any]:
    rows = [row for row in document["records"] if row["source_sequence_id"] == "s01-opening-departure"]
    if len(rows) != 1:
        raise ValueError("execution manifest must contain exactly one S01 record")
    return rows[0]


def draw_comparison(images: dict[str, Image.Image], path: Path, phone: bool) -> None:
    gap, margin, header = 18, 20, 112
    if phone:
        prepared = {
            key: image.resize((390, max(1, round(image.height * 390 / image.width))), Image.Resampling.LANCZOS)
            for key, image in images.items()
        }
        column_width = 390
    else:
        prepared = {key: image.copy() for key, image in images.items()}
        column_width = max(image.width for image in prepared.values())
    canvas = Image.new(
        "RGB",
        (margin * 2 + 3 * column_width + 2 * gap, header + max(image.height for image in prepared.values()) + margin),
        "#171b20",
    )
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 12), "CH05 S01 REFERENCE-ABLATION COMPARISON", fill="#f4f1e8", font=font(26, True))
    draw.text(
        (margin, 48),
        "Same flat prompt except one necessary input-instruction line; reduced-palette is a stricter text-only context.",
        fill="#c4ccd3",
        font=font(14),
    )
    ref_counts = {"flat_with_authorized_refs": 2, "matched_flat_no_reference": 0, "stricter_reduced_palette_no_reference": 0}
    for index, key in enumerate(ORDER):
        x = margin + index * (column_width + gap)
        draw.text((x, 74), LABELS[key], fill="#f4f1e8", font=font(15, True))
        draw.text((x, 94), f"input references: {ref_counts[key]}", fill="#9da8b0", font=font(12))
        image = prepared[key]
        canvas.paste(image, (x + (column_width - image.width) // 2, header))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, "PNG", compress_level=6, optimize=False)


def delta(after: dict[str, float], before: dict[str, float]) -> dict[str, float]:
    return {key: round(after[key] - before[key], 6) for key in before}


def main() -> int:
    prompt = load(PROMPT)
    flat_manifest = load(FLAT_EXECUTION)
    text_manifest = load(TEXT_EXECUTION)
    flat = find_s01(flat_manifest)
    text = find_s01(text_manifest)
    ablation = prompt["sequence"]

    contract = prompt["comparison_contract"]
    if contract["changed_prompt_line_indexes_zero_based"] != [3] or contract["unchanged_prompt_line_count"] != 17:
        raise ValueError("matched ablation must change exactly line 3 and preserve 17 lines")
    if ablation["input_references"] != [] or text["input_references"] != [] or len(flat["input_references"]) != 2:
        raise ValueError("reference counts differ from comparison contract")
    flat_lines = flat["prompt_text"].splitlines()
    ablation_lines = ablation["prompt_text"].splitlines()
    changed = [index for index, (left, right) in enumerate(zip(flat_lines, ablation_lines, strict=True)) if left != right]
    if changed != [3]:
        raise ValueError("source and ablation prompts must differ at exactly one input-instruction line")
    if hashlib.sha256(ablation["prompt_text"].encode("utf-8")).hexdigest() != ablation["prompt_sha256"]:
        raise ValueError("ablation prompt hash mismatch")

    if sha256(ABLATION_LOCAL) != OUTPUT_SHA256 or sha256(ABLATION_GLOBAL) != OUTPUT_SHA256:
        raise ValueError("ablation local/global output hash mismatch")
    if ABLATION_LOCAL.read_bytes() != ABLATION_GLOBAL.read_bytes():
        raise ValueError("ablation local output differs from global original")
    output = image_binding(ABLATION_LOCAL)
    if (output["width"], output["height"], output["bytes"]) != (852, 1846, 2369798):
        raise ValueError("ablation output dimensions or byte count mismatch")

    execution = {
        "record_type": "CH05S01MatchedReferenceAblationExecution",
        "schema_version": "1.0",
        "record_id": "ng-ch05-s01-flat-gouache-reference-ablation-execution-r1",
        "state": "EXECUTED_UNACCEPTED_PENDING_HUMAN_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "input_prompt_manifest": bind(PROMPT),
        "comparison_contract": contract,
        "record": {
            "sequence_id": ablation["sequence_id"],
            "source_sequence_id": ablation["source_sequence_id"],
            "panel_range": ablation["panel_range"],
            "panel_count": ablation["panel_count"],
            "prompt_text": ablation["prompt_text"],
            "prompt_sha256": ablation["prompt_sha256"],
            "input_references": [],
            "execution": {
                "tool_mode": "openai_builtin_imagegen_in_codex",
                "tool_service_execution_id": EXECUTION_ID,
                "tool_service_execution_id_is_provider_request_id": False,
                "global_original_path": ABLATION_GLOBAL.as_posix(),
                "global_original_preserved": True,
                "referenced_image_paths_parameter": "OMITTED",
                "num_last_images_to_include_parameter": "OMITTED",
                "observed_tool_wall_seconds": 110.4,
                "model": None,
                "provider": None,
                "endpoint": None,
                "provider_request_id": None,
                "usage": None,
                "cost_usd": None,
                "deterministic_seed": None,
                "unavailable_fields": [
                    "model",
                    "provider",
                    "endpoint",
                    "provider_request_id",
                    "usage",
                    "cost_usd",
                    "deterministic_seed",
                ],
            },
            "output": output,
            "human_review_state": "PENDING",
            "human_review_minutes": None,
            "accepted": False,
            "rights_cleared": False,
            "commercially_cleared": False,
            "exact_production_base": False,
            "generation_reproducible": False,
        },
        "summary": {
            "sequence_outputs": 1,
            "comic_panel_plans": 5,
            "authorized_reference_uses": 0,
            "reference_uploads": 0,
            "known_tool_wall_seconds": 110.4,
            "direct_paid_provider_api_calls": 0,
            "cost_total_usd": None,
            "human_reviewed_outputs": 0,
            "accepted_outputs": 0,
            "rights_cleared_outputs": 0,
            "commercially_cleared_outputs": 0,
            "exact_production_base_outputs": 0,
        },
        "limitations": [
            "The built-in tool exposed no model, provider, endpoint, provider request ID, usage, monetary cost, or deterministic seed.",
            "The Codex tool-service execution ID is a provenance aid, not a provider request ID.",
            "One stochastic pair and one changed input-instruction line cannot prove a general causal effect.",
        ],
        "boundary": {
            "permitted_product": "openai_builtin_imagegen",
            "reference_uploads": 0,
            "referenced_image_paths_passed": 0,
            "conversation_images_included": 0,
            "direct_paid_provider_api_calls": 0,
            "bfl_calls": 0,
            "new_upload_classes": 0,
            "real_person_or_child_material": 0,
            "accepted": 0,
            "rights_cleared": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
    }
    EXECUTION.write_text(json.dumps(execution, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    candidates = {
        "flat_with_authorized_refs": {"record": flat, "manifest": FLAT_EXECUTION},
        "matched_flat_no_reference": {"record": execution["record"], "manifest": EXECUTION},
        "stricter_reduced_palette_no_reference": {"record": text, "manifest": TEXT_EXECUTION},
    }
    images: dict[str, Image.Image] = {}
    measurements: dict[str, dict[str, float]] = {}
    candidate_rows: list[dict[str, Any]] = []
    for key in ORDER:
        candidate = candidates[key]
        record = candidate["record"]
        image_path = ROOT / record["output"]["path"]
        if sha256(image_path) != record["output"]["sha256"]:
            raise ValueError(f"source output hash mismatch: {key}")
        images[key] = open_rgb(image_path)
        measurements[key] = metric(images[key], image_path.stat().st_size)
        candidate_rows.append(
            {
                "comparison_role": key,
                "label": LABELS[key],
                "execution_manifest": bind(candidate["manifest"]),
                "sequence_id": record["sequence_id"],
                "prompt_sha256": record["prompt_sha256"],
                "input_reference_count": len(record["input_references"]),
                "output": image_binding(image_path),
                "metrics": measurements[key],
                "human_review_state": "PENDING",
                "human_review_minutes": None,
                "accepted": False,
                "rights_cleared": False,
                "commercially_cleared": False,
                "exact_production_base": False,
            }
        )

    draw_comparison(images, NATIVE, phone=False)
    draw_comparison(images, PHONE, phone=True)
    deltas = {
        "matched_no_reference_minus_reference_backed_flat": delta(
            measurements["matched_flat_no_reference"], measurements["flat_with_authorized_refs"]
        ),
        "stricter_no_reference_minus_reference_backed_flat": delta(
            measurements["stricter_reduced_palette_no_reference"], measurements["flat_with_authorized_refs"]
        ),
        "stricter_no_reference_minus_matched_no_reference": delta(
            measurements["stricter_reduced_palette_no_reference"], measurements["matched_flat_no_reference"]
        ),
    }
    evidence = {
        "record_type": "CH05S01MatchedReferenceAblationComparison",
        "schema_version": "1.0",
        "record_id": "ng-ch05-s01-flat-gouache-reference-ablation-comparison-r1",
        "state": "MEASURED_PENDING_HUMAN_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "inputs": [bind(PROMPT), bind(EXECUTION), bind(FLAT_EXECUTION), bind(TEXT_EXECUTION)],
        "comparison_design": {
            "panel_range": [1, 5],
            "candidate_count": 3,
            "matched_pair": ["flat_with_authorized_refs", "matched_flat_no_reference"],
            "matched_pair_changed_prompt_line_indexes_zero_based": [3],
            "matched_pair_unchanged_prompt_line_count": 17,
            "matched_pair_style_wording_changed": False,
            "matched_pair_story_or_gate_wording_changed": False,
            "stricter_control": "stricter_reduced_palette_no_reference",
        },
        "metric_method": {
            "normalization_width_px": 390,
            "grayscale_entropy_bits": "Shannon entropy of 390px-normalized 8-bit luminance histogram.",
            "edge_density_ge_32": "FIND_EDGES pixels >=32 after removing the one-pixel border, divided by remaining pixels.",
            "png_bytes_per_native_pixel": "Native PNG file bytes divided by native width x height.",
            "interpretation": "Complexity proxies support visual comparison only; they do not measure identity, narrative success, or quality.",
        },
        "candidates": candidate_rows,
        "metric_deltas": deltas,
        "artifacts": {"native_three_column": artifact(NATIVE), "phone_390px_three_column": artifact(PHONE)},
        "review_questions": [
            "Does removing reference conditioning alter Soren/Sigrid hair, wardrobe, face, or role binding?",
            "Does the matched no-reference result preserve departure direction, map, changed tracks, reaction, and runnel causality?",
            "Does the stricter reduced-palette instruction reduce density without losing phone-readable geography and clues?",
        ],
        "human_review_state": "PENDING",
        "human_review_minutes": None,
        "accepted_candidates": 0,
        "rights_cleared_candidates": 0,
        "commercially_cleared_candidates": 0,
        "exact_production_base_candidates": 0,
        "spend": {"direct_paid_api_cloud_usd": 0.0, "built_in_product_monetary_cost_usd": None},
        "limitations": [
            "One stochastic matched pair and one changed input-instruction line cannot prove general causality.",
            "The stricter reduced-palette control also changes style instructions, so its differences cannot be attributed only to reference removal.",
            "Complexity metrics do not measure character identity, causal storytelling, artistic quality, or commercial suitability.",
            "All visual judgments remain pending human review; no candidate is accepted, rights-cleared, commercially cleared, or an exact production base.",
        ],
        "boundary": "Research comparison only. ComicPanelPlan remains the sole planning structure; no acceptance, rights, or exact-base decision is made.",
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "execution": {**bind(EXECUTION), "output_sha256": OUTPUT_SHA256},
                "evidence": bind(EVIDENCE),
                "metrics": measurements,
                "deltas": deltas,
                "artifacts": evidence["artifacts"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
