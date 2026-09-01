"""Compile all 50 CH05 plans into deterministic initial run ledgers."""
from __future__ import annotations

import hashlib
import json
import time
from collections import Counter
from pathlib import Path

from comic_run_ledger import append_event, canonical_sha256, new_ledger, validate_ledger


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
ASSERTIONS = ROOT / "production/comic/hard-assertion-manifests/ch05-mill-signal-r1.json"
DEMO = ROOT / "production/comic/demonstration-slices/ch05-p033-p038-r1.json"
OUT = ROOT / "experiments/results/ch05-50-panel-run-manifest-r1.json"
EVENT_TIME = "2026-09-01T16:26:24Z"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_manifest() -> dict:
    started = time.perf_counter()
    plans = json.loads(PLANS.read_text(encoding="utf-8"))
    assertions = json.loads(ASSERTIONS.read_text(encoding="utf-8"))
    demo = json.loads(DEMO.read_text(encoding="utf-8"))
    assertion_by_panel = {
        item["applicability"]: item
        for item in assertions["assertions"]
        if item.get("applicability")
    }
    demo_ids = set(demo["panel_ids"])
    rows = []
    for plan in plans["plans"]:
        panel_id = plan["panel_id"]
        ledger = new_ledger(
            ledger_id=f"{panel_id}-chapter-run-ledger-r1",
            panel_id=panel_id,
            plan_revision_id=plan["plan_revision_id"],
        )
        ledger = append_event(
            ledger,
            event_id=f"{panel_id}-base-pending-chapter-r1",
            occurred_at=EVENT_TIME,
            to_state="BASE_APPROVAL_PENDING",
            data={"reason": "No approved base raster exists; candidate intake and layout controls do not grant approval."},
        )
        ledger_errors = validate_ledger(ledger)
        if ledger_errors:
            raise ValueError(f"invalid generated ledger {panel_id}: {ledger_errors}")
        assertion = assertion_by_panel[panel_id]
        rows.append({
            "panel_id": panel_id,
            "plan_revision_id": plan["plan_revision_id"],
            "display_order": plan["display_order"],
            "applicable_hard_assertion_id": assertion["id"],
            "applicable_hard_assertion_sha256": canonical_sha256(assertion),
            "visible_adult_count": len(plan["visible_adult_cast"]),
            "motion_mode": plan["comic_direction"]["motion_mode"],
            "demonstration_slice": panel_id in demo_ids,
            "current_state": ledger["current_state"],
            "event_count": len(ledger["events"]),
            "chain_head_sha256": ledger["events"][-1]["event_sha256"],
            "executable": False,
            "render_record": None,
            "human_review_status": "not_yet_performed",
            "human_minutes": None,
            "accepted": False,
        })

    root_items = [
        {
            "panel_id": item["panel_id"],
            "plan_revision_id": item["plan_revision_id"],
            "applicable_hard_assertion_sha256": item["applicable_hard_assertion_sha256"],
            "chain_head_sha256": item["chain_head_sha256"],
        }
        for item in rows
    ]
    elapsed_ms = (time.perf_counter() - started) * 1000
    return {
        "record_type": "ComicChapterRunManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-50-panel-run-manifest-r1",
        "state": "CHAPTER_COMPILED_ALL_BASE_APPROVAL_PENDING_NO_EXECUTION",
        "medium": "comic",
        "animation_shot_plan": None,
        "sources": {
            "comic_panel_plans": {"path": PLANS.relative_to(ROOT).as_posix(), "sha256": sha256(PLANS)},
            "hard_assertions": {"path": ASSERTIONS.relative_to(ROOT).as_posix(), "sha256": sha256(ASSERTIONS)},
            "demonstration_slice": {"path": DEMO.relative_to(ROOT).as_posix(), "sha256": sha256(DEMO)},
        },
        "chapter_root_sha256": canonical_sha256({"panels": root_items}),
        "summary": {
            "panel_count": len(rows),
            "display_order_contiguous": [item["display_order"] for item in rows] == list(range(1, 51)),
            "stage_denominators": {
                "planned": len(rows),
                "base_approval_pending": sum(item["current_state"] == "BASE_APPROVAL_PENDING" for item in rows),
                "local_base_approved": 0,
                "local_repair_ready": 0,
                "external_authority_ready": 0,
                "budget_reserved": 0,
                "submitted": 0,
                "render_record_complete": 0,
                "human_review_complete": 0,
                "accepted": 0,
            },
            "visible_adult_count_distribution": dict(sorted(Counter(item["visible_adult_count"] for item in rows).items())),
            "motion_mode_distribution": dict(sorted(Counter(item["motion_mode"] for item in rows).items())),
            "demonstration_slice_panels": sum(item["demonstration_slice"] for item in rows),
            "executable_panels": 0,
            "provider_requests": 0,
            "external_uploads": 0,
            "external_cost_usd": "0.000000",
            "human_minutes": None,
        },
        "review_workload_structure": {
            "per_panel_task_kinds": [
                "base provenance and data classification",
                "applicable hard assertion",
                "lettering safe zone",
                "continuity dependencies",
                "accept/reject and measured minutes",
            ],
            "task_instances": len(rows) * 5,
            "human_minutes": None,
            "note": "Task instances are not a duration estimate.",
        },
        "local_compile_elapsed_ms": round(elapsed_ms, 3),
        "panels": rows,
        "limitations": [
            "Initial ledger compilation is not base-art, renderer, visual-continuity, or acceptance evidence.",
            "Compile time measures local record processing only, not provider or human throughput.",
            "No production budget, external upload, or provider execution is authorized.",
        ],
    }


def main() -> None:
    record = compile_manifest()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
