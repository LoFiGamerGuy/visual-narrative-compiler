"""Build deterministic CH13 RenderRecords, crops, and chapter review artifacts."""
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
PLANS = ROOT / "production/comic/ch13-sc01-panel-plans-r1.json"
PROMPTS = ROOT / "production/comic/run-manifests/ch12-ch13-default-house-route-prompt-manifest-r1.json"
PACKET_DIR = ROOT / "experiments/review-packets/ch13-default-house-route-r1"
SOURCE_DIR = PACKET_DIR / "source"
EXECUTION = ROOT / "production/comic/run-manifests/ch13-default-house-route-execution-r1.json"
PACKET = ROOT / "production/comic/run-manifests/ch13-default-house-route-review-packet-r1.json"
SOURCE_FILES = {
    "ng-ch13-s01-summer-under-winter": "ng-ch13-s01-summer-under-winter.png",
    "ng-ch13-s02-moving-glass": "ng-ch13-s02-moving-glass.png",
    "ng-ch13-s03-crownroot-demand": "ng-ch13-s03-crownroot-demand.png",
    "ng-ch13-s04-soil-water-load": "ng-ch13-s04-soil-water-load.png",
    "ng-ch13-s05-seven-node-circle": "ng-ch13-s05-seven-node-circle.png",
    "ng-ch13-s06-boundary-heart": "ng-ch13-s06-boundary-heart.png",
    "ng-ch13-s07-co-keeper-choice": "ng-ch13-s07-co-keeper-choice.png",
    "ng-ch13-s08-wider-branches": "ng-ch13-s08-wider-branches.png",
}
ELAPSED_SECONDS = {
    "ng-ch13-s01-summer-under-winter": 102.489,
    "ng-ch13-s02-moving-glass": 199.087,
    "ng-ch13-s03-crownroot-demand": 315.404,
    "ng-ch13-s04-soil-water-load": 421.512,
    "ng-ch13-s05-seven-node-circle": 83.021,
    "ng-ch13-s06-boundary-heart": 175.313,
    "ng-ch13-s07-co-keeper-choice": 282.961,
    "ng-ch13-s08-wider-branches": 399.711,
}
GROUP_WALL_SECONDS = [421.512, 399.711]

# Edit only this mapping after visual audit. Omitted panel IDs remain provisional PASS.
# Format: panel_id: ("WARN" or "FAIL", ["FAILURE_CLASS"], "specific evidence note")
TRIAGE: dict[str, tuple[str, list[str], str]] = {
    "ng-ch13-sc01-p020": (
        "FAIL",
        ["SOREN_SHOULDER_SACRIFICE_RESET"],
        "The rear action view restores Soren's oatmeal left shoulder panel after CH12's irreversible gate-splint sacrifice.",
    ),
    "ng-ch13-sc01-p031": (
        "FAIL",
        ["SOREN_SHOULDER_SACRIFICE_RESET"],
        "Soren's visible left shoulder is again fully enclosed by an intact oatmeal coat while he seats the fused Reach.",
    ),
    "ng-ch13-sc01-p036": (
        "FAIL",
        ["SOREN_SHOULDER_SACRIFICE_RESET", "CROWNROOT_HUMAN_FACE_RELIEF_AMBIGUITY"],
        "The hero reveal restores Soren's shoulder panel and gives the non-human Crownroot a conspicuous human-face relief, weakening both irreversible state and creature ontology.",
    ),
    "ng-ch13-sc01-p039": (
        "FAIL",
        ["SOREN_SHOULDER_SACRIFICE_RESET"],
        "The returning-company rear view presents Soren's oatmeal shoulder as intact instead of preserving the sacrificed panel.",
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


def save_artifacts(plans: list[dict[str, Any]], requests: list[dict[str, Any]], panel_images: dict[str, Image.Image]) -> list[dict[str, Any]]:
    contact = PACKET_DIR / "ch13-contact-sheet-r1.png"
    create_grid([labeled_canvas(panel_images[p["panel_id"]], f"P{p['display_order']:03d} · {p['scale_role']}", 238) for p in plans]).save(contact, "PNG", compress_level=9)
    rows = []
    for request in requests:
        with Image.open(SOURCE_DIR / SOURCE_FILES[request["sequence_id"]]) as opened:
            rows.append(labeled_canvas(fit_width(opened.convert("RGB"), 1160), request["sequence_id"], 1200, 38))
    sequence = PACKET_DIR / "ch13-sequence-contact-sheet-r1.png"
    stack(rows, 1200, 10, "#11151b").save(sequence, "PNG", compress_level=9)
    reading = PACKET_DIR / "ch13-complete-reading-draft-r1.png"
    stack([fit_width(panel_images[p["panel_id"]], target_width(p)) for p in plans], 800, 20, "#ece8df").save(reading, "PNG", compress_level=9)
    phone = PACKET_DIR / "ch13-phone-preview-r1.png"
    stack([fit_width(panel_images[p["panel_id"]], 374) for p in plans], 390, 10, "#ece8df").save(phone, "PNG", compress_level=9)
    overlays = []
    for plan in plans:
        image = panel_images[plan["panel_id"]].copy().convert("RGBA")
        layer = Image.new("RGBA", image.size)
        draw = ImageDraw.Draw(layer)
        for zone in plan["comic_direction"]["lettering"]["safe_zones"]:
            x, y, width, height = zone["rect_norm"]
            box = (round(x * image.width), round(y * image.height), round((x + width) * image.width), round((y + height) * image.height))
            draw.rectangle(box, fill=(35, 206, 235, 70), outline=(35, 206, 235, 230), width=max(2, image.width // 300))
        overlays.append(labeled_canvas(Image.alpha_composite(image, layer).convert("RGB"), f"P{plan['display_order']:03d} lettering-safe zone", 238))
    overlay = PACKET_DIR / "ch13-lettering-safe-zone-overlay-r1.png"
    create_grid(overlays).save(overlay, "PNG", compress_level=9)
    result = []
    for kind, path in (("contact_sheet", contact), ("sequence_contact_sheet", sequence), ("complete_reading_draft", reading), ("phone_preview", phone), ("lettering_safe_zone_overlay", overlay)):
        with Image.open(path) as opened:
            result.append({"type": kind, "path": rel(path), "sha256": sha256(path), "width": opened.width, "height": opened.height})
    return result


def main() -> int:
    plans = sorted(json.loads(PLANS.read_text(encoding="utf-8"))["plans"], key=lambda row: row["display_order"])
    prompt_doc = json.loads(PROMPTS.read_text(encoding="utf-8"))
    requests = [row for row in prompt_doc["requests"] if row["chapter"] == "CH13"]
    if len(requests) != 8 or sum(len(row["panel_ids"]) for row in requests) != 40:
        raise ValueError("CH13 must have eight preflighted five-panel sequences")
    crop_dir = PACKET_DIR / "crops"
    crop_dir.mkdir(parents=True, exist_ok=True)
    records, candidates, panel_images = [], [], {}
    for request in requests:
        sequence_id = request["sequence_id"]
        source_path = SOURCE_DIR / SOURCE_FILES[sequence_id]
        with Image.open(source_path) as opened:
            source = opened.convert("RGB")
        boxes, method = source_boxes(sequence_id, source)
        render_id = f"ng-render-{sequence_id}-r1"
        records.append({
            "render_record_id": render_id, "request_id": sequence_id, "chapter": "CH13", "panel_ids": request["panel_ids"],
            "exact_prompt": request["prompt"], "prompt_sha256": request["prompt_sha256"], "input_references": request["reference_images"],
            "output": {"path": rel(source_path), "sha256": sha256(source_path), "width": source.width, "height": source.height, "mime_type": "image/png"},
            "crop_method": method, "model": None, "endpoint": None, "provider_request_id": None, "provider_usage": None,
            "monetary_cost_usd": None, "deterministic_seed": None, "elapsed_seconds": ELAPSED_SECONDS[sequence_id],
            "elapsed_source": "CLIENT_WRAPPER_DATE_NOW_AROUND_IMAGEGEN_CALL",
            "unavailable_fields": ["model", "endpoint", "provider_request_id", "provider_usage", "monetary_cost_usd", "deterministic_seed"],
            "human_review_state": "AGENT_TRIAGED_OWNER_REVIEW_PENDING", "human_review_minutes": None,
            "accepted": False, "commercially_cleared": False, "exact_production_base": False, "reproducible": False,
        })
        for panel_id, box in zip(request["panel_ids"], boxes, strict=True):
            image, trim = trim_horizontal_white(source.crop(tuple(box)))
            path = crop_dir / f"{panel_id}-default-r1.png"
            image.save(path, "PNG", compress_level=9)
            panel_images[panel_id] = image
            state, failures, note = triage(panel_id)
            candidates.append({
                "candidate_id": f"ng-candidate-{panel_id}-default-r1", "panel_id": panel_id, "sequence_id": sequence_id,
                "source_render_record_id": render_id, "source_box": box, "horizontal_trim": trim, "path": rel(path),
                "sha256": sha256(path), "width": image.width, "height": image.height, "agent_triage": state,
                "failure_classes": failures, "triage_note": note, "human_review_state": "OWNER_REVIEW_PENDING",
                "human_review_minutes": None, "accepted": False, "commercially_cleared": False, "exact_production_base": False,
            })
    if [c["panel_id"] for c in candidates] != [p["panel_id"] for p in plans]:
        raise ValueError("candidate order differs from the 40 ordered CH13 plans")
    artifacts = save_artifacts(plans, requests, panel_images)
    execution = {
        "record_type": "BuiltInImageGenExecutionManifest", "schema_version": "1.0", "record_id": "ng-ch13-default-house-route-execution-r1",
        "state": "EXECUTED_AGENT_TRIAGED_OWNER_REVIEW_PENDING", "medium": "comic", "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None, "e_conte": None, "prompt_manifest": {"path": rel(PROMPTS), "sha256": sha256(PROMPTS)},
        "comic_panel_plan_collection": {"path": rel(PLANS), "sha256": sha256(PLANS)}, "records": records,
        "summary": {"chapter": "CH13", "sequence_outputs": 8, "panel_candidates": 40,
            "authorized_reference_uses": sum(len(r["input_references"]) for r in records),
            "client_observed_elapsed_seconds_sum": round(sum(ELAPSED_SECONDS.values()), 3), "parallel_group_wall_seconds": GROUP_WALL_SECONDS,
            "paid_api_cloud_spend_usd": 0, "built_in_monetary_cost_disclosed": False, "accepted": 0, "commercially_cleared": 0, "exact_production_base": 0},
        "timing_note": "Exact per-request wrapper intervals overlap within two parallel groups; their sum is not chapter wall time.",
        "boundary": "Ignored generated pixels are research evidence. No output was re-uploaded; null service fields are unavailable, not zero.",
    }
    EXECUTION.write_text(json.dumps(execution, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    counts = {state: sum(c["agent_triage"] == state for c in candidates) for state in ("PASS", "WARN", "FAIL")}
    packet = {
        "record_type": "ComicChapterReviewPacketManifest", "schema_version": "1.0", "record_id": "ng-ch13-default-house-route-review-packet-r1",
        "state": "OWNER_REVIEW_PENDING", "medium": "comic", "planning_structure": "ComicPanelPlan", "animation_shot_plan": None, "e_conte": None,
        "execution_manifest": {"path": rel(EXECUTION), "sha256": sha256(EXECUTION)}, "candidates": candidates, "artifacts": artifacts,
        "summary": {"complete_chapter": True, "panel_plans": 40, "selected_default_candidates": 40, "sequence_sources": 8,
            "triage": counts, "targeted_repairs_executed": 0, "whole_chapter_alternate_arms": 0},
        "limitations": [
            "Agent visual audit records 36 PASS and 4 FAIL candidates through the explicit TRIAGE mapping; owner review remains pending.",
            "Crownroot geometry, fused-tool continuity, irreversible garment damage, and late secondary-character identities remain stochastic visual-review requirements.",
            "Built-in model, endpoint, request IDs, usage, monetary cost, and seeds remain unavailable.",
            "Agent triage is non-gating; acceptance, rights, clearance, reproducibility, and exact-base status remain pending or false.",
        ],
    }
    PACKET.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"artifacts": 5, "candidates": 40, "elapsed_sum": execution["summary"]["client_observed_elapsed_seconds_sum"], "packet_sha256": sha256(PACKET), "sequences": 8, "triage": counts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
