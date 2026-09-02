"""Compile exact 50-panel CH05 selected/uncovered coverage and three non-generative priority tranches."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
HANDOFF = ROOT / "production/comic/run-manifests/ch05-instrumented-production-manifest-r1.json"
OUTPUT = ROOT / "production/comic/coverage/ch05-remaining-panel-priority-r1.json"
OUT = ROOT / "experiments/review-packets/ch05-remaining-panel-priority-r1"
FONT_PATH = Path("C:/Windows/Fonts/arialbd.ttf")
FONT_SHA = "e8f4e3baf6cc35fed6fcce3a540e8b39e8f6cda1d22a28f2ec8f526fef7a43f5"

TIERS = [
    {
        "tier": "A", "state": "NEXT_HIGHEST_INFORMATION_AFTER_OWNER_REVIEW", "groups": [
            {"group_id": "trail_sensory_and_twine", "orders": [10, 11, 12, 13, 14, 15], "context_orders": [9, 16],
             "rationale": "Completes the underrepresented water/twine/redirection clue chain between selected trail movement and the spoken distance hypothesis."},
            {"group_id": "mill_reveal_and_red_cloth", "orders": [17, 18, 20, 21, 22, 23], "context_orders": [19, 24],
             "rationale": "Adds the mill reveal, false smoke origin, creek crossing, red-cloth trap, protected-object choice, and loading-door approach around selected bridge warning."}
        ]
    },
    {
        "tier": "B", "state": "SECOND_PRODUCTION_TRANCHE", "groups": [
            {"group_id": "smoke_bell_and_entry", "orders": [24, 25, 27, 28, 30, 31], "context_orders": [26, 29, 32],
             "rationale": "Completes drum/ember/twine/bell mechanics and establishes the mill interior plus first dry-footprint discontinuity around selected heat test and wall entry."},
            {"group_id": "interior_false_tracks_and_tin_map", "orders": [32, 33, 34, 37, 38, 39], "context_orders": [31, 35, 36, 40],
             "rationale": "Builds the reversed-footprint/bell suspense and closes the selected plank/tin action into the marked-map deduction."}
        ]
    },
    {
        "tier": "C", "state": "CONNECTIVE_COMPLETION_TRANCHE", "groups": [
            {"group_id": "departure_marker_connective", "orders": [4, 5, 6, 7, 8], "context_orders": [3, 9],
             "rationale": "Fills reaction, runnel, marker, and map-fold connective beats after the selected first clue; important for full chapter flow but lower new-mechanism information."},
            {"group_id": "spoken_distance_hypothesis", "orders": [16], "context_orders": [15, 17],
             "rationale": "Only explicit says-beat; final copy remains absent, so it is isolated as a future dialogue/lettering test rather than silently scripted."},
            {"group_id": "signal_shutdown_and_return", "orders": [41, 42, 43, 45, 47, 48], "context_orders": [40, 44, 46, 49, 50],
             "rationale": "Completes drum extinction, second bell, retreat, post-cut silence, climb, and farmhouse-smoke reveal around the selected final causal/return anchors."}
        ]
    }
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def category(plan: dict) -> str:
    order = plan["display_order"]
    if order <= 4: return "departure_orientation"
    if order <= 16: return "trail_clue_chain"
    if order <= 29: return "mill_approach"
    if order <= 40: return "mill_interior"
    return "signal_and_return"


def draw_map(rows: list[dict], font_path: Path) -> Image.Image:
    colors = {"selected": (46, 139, 103), "A": (62, 139, 205), "B": (218, 158, 52), "C": (125, 132, 145)}
    image = Image.new("RGB", (1500, 980), (235, 237, 241)); draw = ImageDraw.Draw(image)
    title = ImageFont.truetype(str(font_path), 30); body = ImageFont.truetype(str(font_path), 17); small = ImageFont.truetype(str(font_path), 14)
    draw.text((35, 25), "CH05 50-ComicPanelPlan coverage and remaining priority tranches", font=title, fill=(18, 21, 26))
    draw.text((35, 70), "Green selected 14 · blue Tier A next 12 · gold Tier B 12 · gray Tier C 12 · no plan revision or generation", font=body, fill=(70, 75, 82))
    cell_w, cell_h, gap = 134, 130, 9
    x0, y0 = 35, 125
    for index, row in enumerate(rows):
        col, line = index % 10, index // 10
        x, y = x0 + col * (cell_w + gap), y0 + line * (cell_h + gap)
        fill = colors[row["coverage_state"]]
        draw.rounded_rectangle((x, y, x + cell_w, y + cell_h), radius=10, fill=fill)
        draw.text((x + 10, y + 9), f"P{row['order']:03d}", font=body, fill="white")
        draw.text((x + 10, y + 40), row["motion_mode"].replace("held_", "held ").replace("directional_", "dir ").replace("practical_", "practical ")[:17], font=small, fill="white")
        draw.text((x + 10, y + 68), row["narrative_function"].replace("_", " ")[:17], font=small, fill="white")
        draw.text((x + 10, y + 98), "selected" if row["coverage_state"] == "selected" else f"Tier {row['coverage_state']}", font=small, fill="white")
    y = 850
    for index, (label, color) in enumerate(colors.items()):
        x = 40 + index * 280
        draw.rectangle((x, y, x + 25, y + 25), fill=color); draw.text((x + 36, y + 2), label, font=body, fill=(40, 45, 52))
    draw.text((35, 920), "Priority is production-evidence order, not canon importance or art acceptance. Final execution requires owner review and a new bounded milestone.", font=body, fill=(70, 75, 82))
    return image


def main() -> int:
    if not FONT_PATH.is_file() or sha(FONT_PATH) != FONT_SHA: raise SystemExit("hash-pinned coverage font unavailable or changed")
    plans = json.loads(PLANS.read_text(encoding="utf-8")); handoff = json.loads(HANDOFF.read_text(encoding="utf-8"))
    plan_by_order = {plan["display_order"]: plan for plan in plans["plans"]}
    plan_order_by_id = {plan["panel_id"]: plan["display_order"] for plan in plans["plans"]}
    selected_orders = {plan_order_by_id[row["panel_id"]] for row in handoff["rows"]}
    tier_by_order = {}
    for tier in TIERS:
        for group in tier["groups"]:
            for order in group["orders"]:
                if order in tier_by_order: raise SystemExit(f"duplicate tier order: {order}")
                tier_by_order[order] = tier["tier"]
    uncovered = set(range(1, 51)) - selected_orders
    if set(tier_by_order) != uncovered: raise SystemExit("tier denominator does not equal uncovered plans")
    rows = []
    for order in range(1, 51):
        plan = plan_by_order[order]
        cast_count = len(plan["visible_adult_cast"])
        rows.append({
            "order": order, "panel_id": plan["panel_id"], "plan_revision_id": plan["plan_revision_id"],
            "plan_canonical_sha256": canonical_sha(plan), "coverage_state": "selected" if order in selected_orders else tier_by_order[order],
            "narrative_function": category(plan), "motion_mode": plan["comic_direction"]["motion_mode"],
            "cast_occupancy": "no_visible_adult" if cast_count == 0 else "single_adult" if cast_count == 1 else "dual_adult",
            "narrative_beat": plan["narrative_beat"], "final_copy_bound": False,
            "comic_panel_plan_revision_created": False, "production_executable": False
        })
    selected_rows = [row for row in rows if row["coverage_state"] == "selected"]
    uncovered_rows = [row for row in rows if row["coverage_state"] != "selected"]
    motion_total = Counter(row["motion_mode"] for row in rows); motion_selected = Counter(row["motion_mode"] for row in selected_rows)
    function_total = Counter(row["narrative_function"] for row in rows); function_selected = Counter(row["narrative_function"] for row in selected_rows)
    cast_total = Counter(row["cast_occupancy"] for row in rows); cast_selected = Counter(row["cast_occupancy"] for row in selected_rows)
    OUT.mkdir(parents=True, exist_ok=True)
    map_path = OUT / "ch05-coverage-priority-map-r1.png"
    chart = draw_map(rows, FONT_PATH); chart.save(map_path, optimize=False)
    packet = {
        "record_type": "CH05RemainingPanelPriorityPacket", "schema_version": "1.0", "record_id": "ng-ch05-remaining-panel-priority-packet-r1",
        "state": "LOCAL_PRIORITY_ANALYSIS_NO_EXECUTION", "chart": {"path": map_path.relative_to(ROOT).as_posix(), "sha256": sha(map_path), "width": chart.width, "height": chart.height},
        "selected_count": len(selected_rows), "uncovered_count": len(uncovered_rows), "tier_counts": dict(sorted(Counter(row["coverage_state"] for row in uncovered_rows).items())),
        "provider_calls": 0, "uploads": 0, "cost_usd": 0, "human_review_minutes": None, "accepted_new_plans": 0
    }
    packet_path = OUT / "remaining-panel-priority-packet.json"
    with packet_path.open("w", encoding="utf-8", newline="\n") as handle: handle.write(json.dumps(packet, indent=2) + "\n")
    result = {
        "record_type": "ComicChapterRemainingPanelPriority", "schema_version": "1.0", "record_id": "ng-ch05-remaining-panel-priority-r1",
        "state": "PRIORITIZED_LOCAL_ONLY_OWNER_REVIEW_BEFORE_ANY_NEW_GENERATION", "medium": "comic",
        "comic_panel_plan_collection": {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha(PLANS)},
        "selected_handoff": {"path": HANDOFF.relative_to(ROOT).as_posix(), "sha256": sha(HANDOFF)},
        "comic_panel_plan_revision_created": False, "animation_shot_plan": None, "e_conte": None,
        "summary": {"plan_count": 50, "selected_count": 14, "uncovered_count": 36, "tier_a_count": 12, "tier_b_count": 12, "tier_c_count": 12,
                    "production_executable": 0, "accepted_new_plans": 0, "provider_calls": 0, "uploads": 0, "cost_usd": 0, "human_review_minutes": None},
        "coverage": {
            "motion_mode": {key: {"total": motion_total[key], "selected": motion_selected[key], "uncovered": motion_total[key] - motion_selected[key]} for key in sorted(motion_total)},
            "narrative_function": {key: {"total": function_total[key], "selected": function_selected[key], "uncovered": function_total[key] - function_selected[key]} for key in sorted(function_total)},
            "cast_occupancy": {key: {"total": cast_total[key], "selected": cast_selected[key], "uncovered": cast_total[key] - cast_selected[key]} for key in sorted(cast_total)},
        },
        "priority_tiers": TIERS, "rows": rows, "row_root_sha256": canonical_sha(rows),
        "chart": packet["chart"], "local_packet": {"path": packet_path.relative_to(ROOT).as_posix(), "sha256": sha(packet_path)},
        "decision": "After owner review, Tier A is the next highest-information 12-panel tranche. Do not generate it automatically: the current run already has 29 candidates and exact candidate/style/cadence decisions should inform the next bounded generation milestone.",
        "boundaries": [
            "Priority orders production evidence; it does not revise canon, rank story importance, or accept art.",
            "All 50 exact ComicPanelPlans remain unchanged and visible; selected plus Tier A/B/C is an exact disjoint partition.",
            "No final copy, new prompt, provider call, upload, spend, or executable panel is created.",
            "ComicPanelPlan remains the only active production-planning structure; AnimationShotPlan/E-Conte remain null."
        ]
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle: handle.write(json.dumps(result, indent=2) + "\n")
    print(f"compiled CH05 remaining coverage: 14 selected + 12 A + 12 B + 12 C = 50; row root {result['row_root_sha256']}; {OUTPUT.relative_to(ROOT)} {sha(OUTPUT)}")
    print("motion coverage", json.dumps(result["coverage"]["motion_mode"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
