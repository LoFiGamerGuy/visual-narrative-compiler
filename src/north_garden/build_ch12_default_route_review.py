"""Build deterministic CH12 RenderRecords, crops, and chapter review artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from build_ch06_default_route_review import (
    fit_width,
    labeled_canvas,
    rel,
    sha256,
    stack,
    target_width,
    trim_horizontal_white,
)
from build_ch11_default_route_review import create_grid, source_boxes
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch12-sc01-panel-plans-r1.json"
PROMPTS = ROOT / "production/comic/run-manifests/ch12-ch13-default-house-route-prompt-manifest-r1.json"
PACKET_DIR = ROOT / "experiments/review-packets/ch12-default-house-route-r1"
SOURCE_DIR = PACKET_DIR / "source"
EXECUTION = ROOT / "production/comic/run-manifests/ch12-default-house-route-execution-r1.json"
PACKET = ROOT / "production/comic/run-manifests/ch12-default-house-route-review-packet-r1.json"
SOURCE_FILES = {
    "ng-ch12-s01-hidden-section": "ng-ch12-s01-hidden-section.png",
    "ng-ch12-s02-ash-cut": "ng-ch12-s02-ash-cut.png",
    "ng-ch12-s03-false-cairn": "ng-ch12-s03-false-cairn.png",
    "ng-ch12-s04-separate-paths": "ng-ch12-s04-separate-paths.png",
    "ng-ch12-s05-sacrificed-cloth": "ng-ch12-s05-sacrificed-cloth.png",
    "ng-ch12-s06-truth-at-camp": "ng-ch12-s06-truth-at-camp.png",
    "ng-ch12-s07-negotiated-return": "ng-ch12-s07-negotiated-return.png",
    "ng-ch12-s08-gate-consent": "ng-ch12-s08-gate-consent.png",
}
GROUP1_RECONSTRUCTED_SECONDS = {
    "ng-ch12-s01-hidden-section": 103.445,
    "ng-ch12-s02-ash-cut": 205.204,
    "ng-ch12-s03-false-cairn": 319.651,
    "ng-ch12-s04-separate-paths": 420.731,
}
GROUP1_IDS = tuple(GROUP1_RECONSTRUCTED_SECONDS)
GROUP2_IDS = tuple(list(SOURCE_FILES)[4:])
GROUP1_ENVELOPE_SECONDS = 420.731
GROUP2_EXACT_SECONDS = {
    "ng-ch12-s05-sacrificed-cloth": 106.302,
    "ng-ch12-s06-truth-at-camp": 213.586,
    "ng-ch12-s07-negotiated-return": 316.771,
    "ng-ch12-s08-gate-consent": 427.911,
}
GROUP2_WALL_SECONDS = 427.911

# Edit only this mapping after visual audit. Omitted panel IDs remain provisional PASS.
# Format: panel_id: ("WARN" or "FAIL", ["FAILURE_CLASS"], "specific evidence note")
TRIAGE: dict[str, tuple[str, list[str], str]] = {
    "ng-ch12-sc01-p025": (
        "FAIL",
        ["AUDIBLE_SIGNAL_CAUSE_NOT_SHOWN"],
        "The socket glows at stone, but the authored forged-socket-to-iron-pin strike and audible request cadence are not visible.",
    ),
    "ng-ch12-sc01-p029": (
        "FAIL",
        ["FAILED_LEVERAGE_CAUSE_NOT_SHOWN"],
        "The root lintel blocks the route, but no attempted leverage or physical failure shows why Sigrid cannot move it alone.",
    ),
    "ng-ch12-sc01-p036": (
        "FAIL",
        ["SOREN_SHOULDER_SACRIFICE_RESET"],
        "The sealed-gate full figure restores Soren's visibly intact oatmeal left shoulder after the irreversible P024 cut.",
    ),
    "ng-ch12-sc01-p038": (
        "FAIL",
        ["SOREN_SHOULDER_SACRIFICE_RESET"],
        "The assent two-shot again renders Soren's oatmeal left shoulder intact instead of preserving the P024 sacrifice.",
    ),
    "ng-ch12-sc01-p040": (
        "FAIL",
        ["PREMATURE_UNREQUESTED_HOLLOW_STAG"],
        "A stag appears inside the opened Garden although CH12 P040 requests Crownroot and the Hollow Stag does not return until CH13 P039.",
    ),
}


def triage(panel_id: str) -> tuple[str, list[str], str]:
    return TRIAGE.get(
        panel_id,
        (
            "PASS",
            [],
            "Visual audit found no blocking story, continuity, or composition failure; owner review remains pending.",
        ),
    )


def timing_fields(sequence_id: str) -> dict[str, Any]:
    if sequence_id in GROUP1_IDS:
        return {
            "timing_group": "parallel_group_1",
            "elapsed_seconds": GROUP1_RECONSTRUCTED_SECONDS[sequence_id],
            "elapsed_source": "OUTPUT_TIMESTAMP_RECONSTRUCTED_FROM_GROUP_WALL",
            "group_elapsed_envelope_seconds": GROUP1_ENVELOPE_SECONDS,
        }
    return {
        "timing_group": "parallel_group_2",
        "elapsed_seconds": GROUP2_EXACT_SECONDS[sequence_id],
        "elapsed_source": "CLIENT_WRAPPER_DATE_NOW_AROUND_IMAGEGEN_CALL",
        "group_elapsed_envelope_seconds": GROUP2_WALL_SECONDS,
    }


def main() -> int:
    plans = sorted(json.loads(PLANS.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    prompt_doc = json.loads(PROMPTS.read_text(encoding="utf-8"))
    requests = [row for row in prompt_doc["requests"] if row["chapter"] == "CH12"]
    if len(requests) != 8 or sum(len(row["panel_ids"]) for row in requests) != 40:
        raise ValueError("CH12 must have eight preflighted five-panel sequences")
    crop_dir = PACKET_DIR / "crops"
    crop_dir.mkdir(parents=True, exist_ok=True)
    source_records = []
    candidates = []
    panel_images: dict[str, Image.Image] = {}
    for request in requests:
        sequence_id = request["sequence_id"]
        source_path = SOURCE_DIR / SOURCE_FILES[sequence_id]
        with Image.open(source_path) as opened:
            source = opened.convert("RGB")
        boxes, method = source_boxes(sequence_id, source)
        render_id = f"ng-render-{sequence_id}-r1"
        timing = timing_fields(sequence_id)
        unavailable_fields = [
            "model",
            "endpoint",
            "provider_request_id",
            "provider_usage",
            "monetary_cost_usd",
            "deterministic_seed",
        ]
        source_records.append(
            {
                "render_record_id": render_id,
                "request_id": sequence_id,
                "chapter": "CH12",
                "panel_ids": request["panel_ids"],
                "exact_prompt": request["prompt"],
                "prompt_sha256": request["prompt_sha256"],
                "input_references": request["reference_images"],
                "output": {
                    "path": rel(source_path),
                    "sha256": sha256(source_path),
                    "width": source.width,
                    "height": source.height,
                    "mime_type": "image/png",
                },
                "crop_method": method,
                "model": None,
                "endpoint": None,
                "provider_request_id": None,
                "provider_usage": None,
                "monetary_cost_usd": None,
                "deterministic_seed": None,
                **timing,
                "unavailable_fields": unavailable_fields,
                "human_review_state": "AGENT_TRIAGED_OWNER_REVIEW_PENDING",
                "human_review_minutes": None,
                "accepted": False,
                "commercially_cleared": False,
                "exact_production_base": False,
                "reproducible": False,
            }
        )
        for panel_id, box in zip(request["panel_ids"], boxes, strict=True):
            image = source.crop(tuple(box))
            image, trim = trim_horizontal_white(image)
            path = crop_dir / f"{panel_id}-default-r1.png"
            image.save(path, format="PNG", compress_level=9)
            panel_images[panel_id] = image
            state, failures, note = triage(panel_id)
            candidates.append(
                {
                    "candidate_id": f"ng-candidate-{panel_id}-default-r1",
                    "panel_id": panel_id,
                    "sequence_id": sequence_id,
                    "source_render_record_id": render_id,
                    "source_box": box,
                    "horizontal_trim": trim,
                    "path": rel(path),
                    "sha256": sha256(path),
                    "width": image.width,
                    "height": image.height,
                    "agent_triage": state,
                    "failure_classes": failures,
                    "triage_note": note,
                    "human_review_state": "OWNER_REVIEW_PENDING",
                    "human_review_minutes": None,
                    "accepted": False,
                    "commercially_cleared": False,
                    "exact_production_base": False,
                }
            )
    if [row["panel_id"] for row in candidates] != [row["panel_id"] for row in plans]:
        raise ValueError("candidate order differs from the 40 ordered CH12 plans")

    contact_cells = [
        labeled_canvas(panel_images[row["panel_id"]], f"P{row['display_order']:03d} · {row['scale_role']}", 238)
        for row in plans
    ]
    contact_path = PACKET_DIR / "ch12-contact-sheet-r1.png"
    create_grid(contact_cells).save(contact_path, format="PNG", compress_level=9)
    sequence_rows = []
    for request in requests:
        with Image.open(SOURCE_DIR / SOURCE_FILES[request["sequence_id"]]) as opened:
            sequence_rows.append(
                labeled_canvas(fit_width(opened.convert("RGB"), 1160), request["sequence_id"], 1200, 38)
            )
    sequence_path = PACKET_DIR / "ch12-sequence-contact-sheet-r1.png"
    stack(sequence_rows, 1200, 10, "#11151b").save(sequence_path, format="PNG", compress_level=9)
    reading_path = PACKET_DIR / "ch12-complete-reading-draft-r1.png"
    stack(
        [fit_width(panel_images[row["panel_id"]], target_width(row)) for row in plans],
        800,
        20,
        "#ece8df",
    ).save(reading_path, format="PNG", compress_level=9)
    phone_path = PACKET_DIR / "ch12-phone-preview-r1.png"
    stack(
        [fit_width(panel_images[row["panel_id"]], 374) for row in plans],
        390,
        10,
        "#ece8df",
    ).save(phone_path, format="PNG", compress_level=9)
    overlays = []
    for row in plans:
        image = panel_images[row["panel_id"]].copy().convert("RGBA")
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        for zone in row["comic_direction"]["lettering"]["safe_zones"]:
            x, y, width, height = zone["rect_norm"]
            box = (
                round(x * image.width),
                round(y * image.height),
                round((x + width) * image.width),
                round((y + height) * image.height),
            )
            draw.rectangle(
                box,
                fill=(35, 206, 235, 70),
                outline=(35, 206, 235, 230),
                width=max(2, image.width // 300),
            )
        overlays.append(
            labeled_canvas(
                Image.alpha_composite(image, layer).convert("RGB"),
                f"P{row['display_order']:03d} lettering-safe zone",
                238,
            )
        )
    overlay_path = PACKET_DIR / "ch12-lettering-safe-zone-overlay-r1.png"
    create_grid(overlays).save(overlay_path, format="PNG", compress_level=9)

    reconstructed_elapsed_sum = round(sum(GROUP1_RECONSTRUCTED_SECONDS.values()), 3)
    exact_elapsed_sum = round(sum(GROUP2_EXACT_SECONDS.values()), 3)
    combined_elapsed_sum = round(reconstructed_elapsed_sum + exact_elapsed_sum, 3)
    execution_doc = {
        "record_type": "BuiltInImageGenExecutionManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch12-default-house-route-execution-r1",
        "state": "EXECUTED_AGENT_TRIAGED_OWNER_REVIEW_PENDING",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "prompt_manifest": {"path": rel(PROMPTS), "sha256": sha256(PROMPTS)},
        "comic_panel_plan_collection": {"path": rel(PLANS), "sha256": sha256(PLANS)},
        "records": source_records,
        "timing_groups": [
            {
                "timing_group": "parallel_group_1",
                "request_ids": list(GROUP1_IDS),
                "measurement": "OUTPUT_TIMESTAMP_RECONSTRUCTED_FROM_GROUP_WALL",
                "group_elapsed_envelope_seconds": GROUP1_ENVELOPE_SECONDS,
                "per_request_elapsed_seconds_available": True,
                "per_request_elapsed_seconds": GROUP1_RECONSTRUCTED_SECONDS,
                "reconstructed": True,
            },
            {
                "timing_group": "parallel_group_2",
                "request_ids": list(GROUP2_IDS),
                "measurement": "CLIENT_WRAPPER_DATE_NOW_AROUND_IMAGEGEN_CALL",
                "group_wall_seconds": GROUP2_WALL_SECONDS,
                "per_request_elapsed_seconds_available": True,
                "per_request_elapsed_seconds": GROUP2_EXACT_SECONDS,
            },
        ],
        "summary": {
            "chapter": "CH12",
            "sequence_outputs": 8,
            "panel_candidates": 40,
            "authorized_reference_uses": sum(len(row["input_references"]) for row in source_records),
            "client_observed_elapsed_seconds_sum": combined_elapsed_sum,
            "reconstructed_per_request_elapsed_seconds_sum": reconstructed_elapsed_sum,
            "exact_per_request_elapsed_seconds_sum_available_subset": exact_elapsed_sum,
            "group1_client_envelope_seconds": GROUP1_ENVELOPE_SECONDS,
            "parallel_group_wall_seconds": [GROUP1_ENVELOPE_SECONDS, GROUP2_WALL_SECONDS],
            "paid_api_cloud_spend_usd": 0,
            "built_in_monetary_cost_disclosed": False,
            "accepted": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
        "timing_note": "Group 1 per-request intervals are transparently reconstructed from default-output creation timestamps anchored to the exact 420.731-second group wall; this method matches group 2 wrappers within milliseconds. Group 2 intervals are exact wrapper observations. All intervals overlap within their parallel groups, so their sum is not chapter wall time.",
        "boundary": "Ignored generated pixels are research evidence. No output was re-uploaded; null service and timing fields are unavailable, not zero.",
    }
    EXECUTION.parent.mkdir(parents=True, exist_ok=True)
    EXECUTION.write_text(
        json.dumps(execution_doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    artifacts = []
    for artifact_type, path in (
        ("contact_sheet", contact_path),
        ("sequence_contact_sheet", sequence_path),
        ("complete_reading_draft", reading_path),
        ("phone_preview", phone_path),
        ("lettering_safe_zone_overlay", overlay_path),
    ):
        with Image.open(path) as opened:
            width, height = opened.size
        artifacts.append(
            {
                "type": artifact_type,
                "path": rel(path),
                "sha256": sha256(path),
                "width": width,
                "height": height,
            }
        )
    counts = {state: sum(row["agent_triage"] == state for row in candidates) for state in ("PASS", "WARN", "FAIL")}
    packet_doc = {
        "record_type": "ComicChapterReviewPacketManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch12-default-house-route-review-packet-r1",
        "state": "OWNER_REVIEW_PENDING",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "execution_manifest": {"path": rel(EXECUTION), "sha256": sha256(EXECUTION)},
        "candidates": candidates,
        "artifacts": artifacts,
        "summary": {
            "complete_chapter": True,
            "panel_plans": 40,
            "selected_default_candidates": 40,
            "sequence_sources": 8,
            "triage": counts,
            "targeted_repairs_executed": 0,
            "whole_chapter_alternate_arms": 0,
        },
        "limitations": [
            "Agent visual triage preserves five exact failures; the other 35 candidates remain owner-review pending rather than accepted.",
            "Group 1 per-request intervals are reconstructed from output creation timestamps anchored to the exact 420.731-second group wall; they are not direct wrapper observations.",
            "P024 and P028 occur at the authored thresholds and P039 key fusion is clear; Soren's shoulder damage visibly resets at P036 and P038.",
            "Crownroot history and secondary-character identities are text-defined because new outputs cannot be re-uploaded as references.",
            "Built-in model, endpoint, request IDs, usage, monetary cost, and seeds remain unavailable.",
            "Agent triage is non-gating; acceptance, rights, clearance, reproducibility, and exact-base status remain pending or false.",
        ],
    }
    PACKET.write_text(
        json.dumps(packet_doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "artifacts": 5,
                "candidates": 40,
                "exact_elapsed_sum_available_subset": exact_elapsed_sum,
                "group1_envelope_seconds": GROUP1_ENVELOPE_SECONDS,
                "reconstructed_elapsed_sum": reconstructed_elapsed_sum,
                "packet_sha256": sha256(PACKET),
                "sequences": 8,
                "triage": counts,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
