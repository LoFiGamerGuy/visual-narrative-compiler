"""Compile the validator-facing CH05 complete-chapter production manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
PROMPTS = ROOT / "production/comic/run-manifests/ch05-complete-chapter-prompt-manifest-r1.json"
CROPS = ROOT / "production/comic/run-manifests/ch05-sequence-strip-crops-r1.json"
SPLIT_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r1/panel-split-report.json"
BUILD_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r1/review/build-report.json"
LETTERING_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r1/lettered/lettering-build-report.json"
CONTINUITY_REPORT = ROOT / "experiments/review-packets/ch05-complete-chapter-draft-r1/review/continuity-sheet-report.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-complete-chapter-production-manifest-r1.json"

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
HAIR = {"soren": "light-brown to dark-blond; consistent cut and silhouette", "sigrid": "dark-brown to near-black; consistent cut and silhouette"}
WARDROBE = {"soren": "pale oatmeal work coat", "sigrid": "practical plaid wrap"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(value: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / value["path"]
    if sha256(path) != value["sha256"]:
        raise ValueError(f"artifact hash mismatch: {path}")
    return {"path": value["path"], "sha256": value["sha256"], "width_px": value["width"], "height_px": value["height"]}


def main() -> int:
    plan_doc = json.loads(PLAN.read_text(encoding="utf-8"))
    plans = sorted(plan_doc["plans"], key=lambda row: row["display_order"])
    prompt_doc = json.loads(PROMPTS.read_text(encoding="utf-8"))
    prompt_sequences = {row["sequence_id"]: row for row in prompt_doc["sequences"]}
    crop_doc = json.loads(CROPS.read_text(encoding="utf-8"))
    crop_sequences = {row["sequence_id"]: row for row in crop_doc["sequences"]}
    split = json.loads(SPLIT_REPORT.read_text(encoding="utf-8"))
    split_by_panel = {row["panel_id"]: row for row in split["panels"]}
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    lettering = json.loads(LETTERING_REPORT.read_text(encoding="utf-8"))
    continuity = json.loads(CONTINUITY_REPORT.read_text(encoding="utf-8"))
    if [row["panel_id"] for row in plans] != list(split_by_panel):
        raise ValueError("split report does not preserve canonical panel order")
    panels = []
    for plan in plans:
        split_row = split_by_panel[plan["panel_id"]]
        sequence = prompt_sequences[split_row["sequence_id"]]
        source_sequence = crop_sequences[split_row["sequence_id"]]
        prompt_text = "\n".join(sequence["prompt_lines"])
        references = [{**REFERENCES[ref_id], "upload_target": "openai_builtin_imagegen"} for ref_id in sequence["reference_ids"]]
        candidate = split_row["output"]
        panels.append({
            "panel_id": plan["panel_id"],
            "plan_revision_id": plan["plan_revision_id"],
            "display_order": plan["display_order"],
            "status": "RENDERED",
            "sequence_id": sequence["sequence_id"],
            "source_service_execution_id": sequence["source_service_execution_id"],
            "prompt_text": prompt_text,
            "prompt_sha256": hashlib.sha256(prompt_text.encode("utf-8")).hexdigest(),
            "input_references": references,
            "source_strip": source_sequence["source"],
            "crop_box": split_row["crop_box"],
            "candidate": {
                "path": candidate["path"],
                "sha256": candidate["sha256"],
                "width_px": candidate["width"],
                "height_px": candidate["height"],
                "elapsed_seconds": sequence["elapsed_seconds"],
                "timing_scope": "shared sequence-generation completion offset; all crops from the same sequence share this observation",
                "service": {
                    "tool": "OpenAI built-in ImageGen in Codex; exact sequence strip followed by deterministic local crop",
                    "model": None,
                    "endpoint": None,
                    "request_id": None,
                    "provider_usage": None,
                    "provider_cost_usd": None,
                    "seed": None,
                    "unavailable_fields": ["model", "endpoint", "request_id", "provider_usage", "provider_cost_usd", "seed"],
                },
            },
            "diagnosis": None,
            "lettering_safe": {
                "zones": plan["comic_direction"]["lettering"]["safe_zones"],
                "protects": ["faces", "people", "important_hands", "story_objects"],
                "transparency_overlap_allowed_only_if_readable": True,
                "review_state": "PENDING",
            },
            "continuity": {"hair": HAIR, "wardrobe": WARDROBE, "review_state": "PENDING"},
            "review": {
                "human_state": "PENDING",
                "human_review_minutes": None,
                "decision": "PENDING_OWNER_REVIEW",
                "accepted": False,
                "commercially_cleared": False,
                "exact_production_base": False,
            },
        })
    review_artifacts = [
        {"kind": "chapter_scroll", **artifact(lettering["artifacts"]["lettered_long_scroll"])},
        {"kind": "contact_sheet", **artifact(build["artifacts"]["contact_sheet"])},
        {"kind": "phone_preview", **artifact(lettering["artifacts"]["lettered_phone_scroll"])},
        {"kind": "lettering_overlay", **artifact(build["artifacts"]["long_scroll_lettering_overlay"])},
        {"kind": "continuity_sheet", **artifact(continuity["artifact"])},
    ]
    manifest = {
        "record_type": "CH05CompleteChapterProductionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-complete-chapter-production-manifest-r1",
        "state": "COMPLETE_READING_DRAFT_PENDING_OWNER_REVIEW",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "comic_panel_plan_source": {"path": PLAN.relative_to(ROOT).as_posix(), "sha256": sha256(PLAN)},
        "provider_policy": {
            "permitted_product": "openai_builtin_imagegen",
            "external_provider_uploads": 0,
            "direct_paid_provider_api_calls": 0,
            "uploaded_reference_hashes": [value["sha256"] for value in REFERENCES.values()],
        },
        "reference_allowlist": [{**value, "provider_product": "openai_builtin_imagegen", "data_class": "fictional_adults"} for value in REFERENCES.values()],
        "source_bindings": [
            {"path": PROMPTS.relative_to(ROOT).as_posix(), "sha256": sha256(PROMPTS)},
            {"path": CROPS.relative_to(ROOT).as_posix(), "sha256": sha256(CROPS)},
            {"path": SPLIT_REPORT.relative_to(ROOT).as_posix(), "sha256": sha256(SPLIT_REPORT)},
            {"path": BUILD_REPORT.relative_to(ROOT).as_posix(), "sha256": sha256(BUILD_REPORT)},
            {"path": LETTERING_REPORT.relative_to(ROOT).as_posix(), "sha256": sha256(LETTERING_REPORT)},
            {"path": CONTINUITY_REPORT.relative_to(ROOT).as_posix(), "sha256": sha256(CONTINUITY_REPORT)},
        ],
        "panels": panels,
        "review_bundle": {"artifacts": review_artifacts},
        "limitations": [
            "The built-in product does not expose model snapshot, endpoint, provider request ID, usage, cost, or deterministic seed.",
            "Parallel-call elapsed values are observed orchestration completion offsets derived from file timestamps and batch wall time, not provider-side latency.",
            "Each panel is a deterministic crop of a multi-panel source strip; source-strip generation is not independently reproducible.",
            "Agent review is pending and cannot establish acceptance, commercial clearance, or exact production-base status.",
            "P001 departure geography may read toward rather than away from the farmhouse and remains a known diagnostic candidate for targeted replacement.",
        ],
    }
    OUTPUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"panels": len(panels), "review_artifacts": len(review_artifacts), "output": OUTPUT.relative_to(ROOT).as_posix(), "sha256": sha256(OUTPUT)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
