"""Compile all CH05 ComicPanelPlans into a no-render production preflight."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
ASSERTIONS = ROOT / "production/comic/hard-assertion-manifests/ch05-mill-signal-r1.json"
STYLE = ROOT / "production/comic/style-direction/ch05-mill-signal-r1.json"
SLICE = ROOT / "production/comic/demonstration-slices/ch05-p033-p038-r1.json"
P036_READINESS = ROOT / "production/comic/repair-readiness/ch05-p036-openai-r1.json"
OUT = ROOT / "experiments/results/ch05-production-preflight-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> None:
    plans, assertions, style, demo, p036 = map(read, [PLANS, ASSERTIONS, STYLE, SLICE, P036_READINESS])
    rows = plans["plans"]
    assertion_by_panel = {
        item["applicability"]: item["id"]
        for item in assertions["assertions"]
        if item.get("applicability")
    }
    demo_ids = set(demo["panel_ids"])
    cast_counts = Counter(len(row["visible_adult_cast"]) for row in rows)
    motion_modes = Counter(row["comic_direction"]["motion_mode"] for row in rows)
    safe_anchors = Counter(
        zone["anchor"]
        for row in rows
        for zone in row["comic_direction"]["lettering"]["safe_zones"]
    )
    per_panel = []
    for row in rows:
        panel_id = row["panel_id"]
        per_panel.append({
            "panel_id": panel_id,
            "plan_revision_id": row["plan_revision_id"],
            "display_order": row["display_order"],
            "visible_adult_cast": row["visible_adult_cast"],
            "visible_adult_count": len(row["visible_adult_cast"]),
            "motion_mode": row["comic_direction"]["motion_mode"],
            "lettering_safe_zones": row["comic_direction"]["lettering"]["safe_zones"],
            "asset_ids": row["asset_ids"],
            "applicable_panel_assertion": assertion_by_panel[panel_id],
            "demonstration_slice": panel_id in demo_ids,
            "base_raster_state": "MISSING_APPROVED_BASE",
            "repair_mask_state": "ABSTRACT_LAYOUT_CONTROL_ONLY" if panel_id == "ng-ch05-sc01-p036" else "NOT_PREPARED",
            "external_execution_authorized": False,
            "human_review_status": "not_yet_performed",
            "human_minutes": None,
            "accepted": False,
        })

    demo_rows = [row for row in per_panel if row["demonstration_slice"]]
    selected_average_cost = 0.198621 / 4
    selected_average_seconds = 128.347 / 4
    record = {
        "record_type": "ChapterProductionPreflight",
        "schema_version": "1.0",
        "record_id": "ng-ch05-production-preflight-r1",
        "state": "CHAPTER_INTENT_COMPILED_NO_APPROVED_BASE_ART_NO_RENDER_AUTHORITY",
        "created_at": stamp(),
        "medium": plans["medium"],
        "animation_shot_plan": plans["animation_shot_plan"],
        "sources": {
            "comic_panel_plans": {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha256(PLANS)},
            "hard_assertions": {"path": ASSERTIONS.relative_to(ROOT).as_posix(), "sha256": sha256(ASSERTIONS)},
            "style_direction": {"path": STYLE.relative_to(ROOT).as_posix(), "sha256": sha256(STYLE)},
            "demonstration_slice": {"path": SLICE.relative_to(ROOT).as_posix(), "sha256": sha256(SLICE)},
            "p036_repair_readiness": {"path": P036_READINESS.relative_to(ROOT).as_posix(), "sha256": sha256(P036_READINESS)},
        },
        "chapter_summary": {
            "planned_panels": len(rows),
            "stable_panel_ids": len({row["panel_id"] for row in rows}),
            "plan_revision_ids": len({row["plan_revision_id"] for row in rows}),
            "display_order_contiguous": [row["display_order"] for row in rows] == list(range(1, 51)),
            "cast_count_distribution": {str(key): cast_counts[key] for key in sorted(cast_counts)},
            "motion_mode_distribution": dict(sorted(motion_modes.items())),
            "lettering_safe_zone_anchor_distribution": dict(sorted(safe_anchors.items())),
            "approved_base_rasters": 0,
            "render_records": 0,
            "accepted_panels": 0,
            "authorized_human_review_minutes": None,
        },
        "demonstration_slice": {
            "panel_count": len(demo_rows),
            "panel_ids": [row["panel_id"] for row in demo_rows],
            "display_order": [row["display_order"] for row in demo_rows],
            "visible_adult_count_distribution": dict(Counter(row["visible_adult_count"] for row in demo_rows)),
            "motion_mode_distribution": dict(Counter(row["motion_mode"] for row in demo_rows)),
            "p036_layout_control_ready": p036["abstract_layout_control"]["target_mask_lettering_safe_zone_overlap_fraction"] == 0,
            "execution_authorized": False,
        },
        "arithmetic_only_selected_arm_scenario": {
            "basis": "Four fictional geometry-control OpenAI requests; not a narrative-panel forecast.",
            "observed_mean_cost_usd": f"{selected_average_cost:.6f}",
            "observed_mean_seconds": round(selected_average_seconds, 3),
            "six_request_arithmetic_cost_usd": f"{selected_average_cost * 6:.6f}",
            "six_request_arithmetic_seconds": round(selected_average_seconds * 6, 3),
            "fifty_request_arithmetic_cost_usd": f"{selected_average_cost * 50:.6f}",
            "fifty_request_arithmetic_seconds": round(selected_average_seconds * 50, 3),
            "excluded": ["retries", "repairs", "human review", "lettering", "narrative-complexity variance", "invoice variance"],
        },
        "panels": per_panel,
        "gates": {
            "local_next": "Create base-art acquisition/approval and mask-review schemas; do not render.",
            "external": "Exact provider/product/endpoint and exact fictional panel input package require authorization beyond the completed geometry bakeoff.",
            "acceptance": "Every panel needs applicable hard-assertion passes and authorized timed human review."
        },
        "limitations": [
            "Compiled intent coverage is not rendered chapter coverage.",
            "The arithmetic scenario is not a cost or throughput forecast.",
            "No smoke raster is promoted and no character-continuity evidence exists.",
            "ComicPanelPlan remains separate from any future AnimationShotPlan/E-Conte."
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
