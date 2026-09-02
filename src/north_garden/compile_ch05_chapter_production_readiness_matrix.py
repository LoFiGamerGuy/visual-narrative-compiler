"""Compile 50-plan CH05 production-readiness state and local review map."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
COVERAGE = ROOT / "production/comic/coverage/ch05-remaining-panel-priority-r1.json"
SCALE = ROOT / "production/comic/layout/ch05-panel-scale-cadence-policy-r1.json"
ASSERTIONS = ROOT / "production/comic/continuity/ch05-character-assertion-manifest-r1.json"
RENDER_INDEX = ROOT / "production/comic/run-manifests/ch05-built-in-renderrecord-index-r1.json"
NEXT = ROOT / "production/comic/run-manifests/ch05-p010-p013-production-manifest-dry-run-r1.json"
ROUTE = ROOT / "production/comic/recommendations/ch05-pipeline-route-recommendation-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-chapter-production-readiness-matrix-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-chapter-production-readiness-matrix-r1.json"
CHART = ROOT / "experiments/review-packets/ch05-chapter-production-readiness-r1/ch05-chapter-readiness-map-r1.png"

MECHANISM_BY_ROLE = {
    "WIDE_DIRECTIONAL_ANCHOR": ["cel_painted", "clear_line_watercolor"],
    "WIDE_ENVIRONMENTAL_MOTION": ["clear_line_watercolor"],
    "TALL_OR_WIDE_DUAL_CAUSAL": ["clear_line_watercolor", "cel_painted"],
    "MEDIUM_SINGLE_CAUSAL": ["clear_line_watercolor"],
    "MEDIUM_TWO_SHOT": ["cel_painted"],
    "MEDIUM_CHARACTER_CLUE": ["cel_painted"],
    "SMALL_OBJECT_INSERT": ["limited_ink_flat"],
    "SMALL_SENSORY_INSERT": ["limited_ink_flat", "clear_line_watercolor"],
    "MEDIUM_SENSORY_REACTION": ["cel_painted"],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def engineering_class(results: dict) -> str:
    values = list(results.values())
    if "FAIL" in values:
        return "FAIL"
    if "WARN" in values:
        return "WARN"
    return "PASS"


def build_chart(rows: list[dict]) -> None:
    CHART.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1600, 1900
    image = Image.new("RGB", (width, height), "#10151c")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((38, 24), "CH05 · 50-plan production readiness r1", fill="#eef3f8", font=font)
    draw.text((38, 45), "Evidence state, not execution or acceptance", fill="#ffcf88", font=font)
    colors = {"EVIDENCE_SELECTED_OWNER_PENDING": "#3d7654", "DRY_RUN_OWNER_GATES_PENDING": "#336b8c", "PRIORITIZED_NO_DRY_RUN": "#8a6a2e", "BACKLOG_PLAN_ONLY": "#4a5260"}
    legend = [("selected evidence", colors["EVIDENCE_SELECTED_OWNER_PENDING"]), ("P010–P013 dry run", colors["DRY_RUN_OWNER_GATES_PENDING"]), ("Tier A no dry run", colors["PRIORITIZED_NO_DRY_RUN"]), ("Tier B/C backlog", colors["BACKLOG_PLAN_ONLY"])]
    x = 38
    for label, color in legend:
        draw.rectangle((x, 68, x + 18, 86), fill=color)
        draw.text((x + 24, 70), label, fill="#dce4ec", font=font)
        x += 230
    cell_w, cell_h, gap = 286, 164, 10
    start_x, start_y = 38, 110
    for index, row in enumerate(rows):
        column, line = index % 5, index // 5
        left = start_x + column * (cell_w + gap)
        top = start_y + line * (cell_h + gap)
        right, bottom = left + cell_w, top + cell_h
        draw.rounded_rectangle((left, top, right, bottom), radius=8, fill=colors[row["readiness_class"]], outline="#8593a3", width=1)
        plan = row["panel_id"].split("-")[-1].upper()
        draw.text((left + 10, top + 8), f"{plan} · {row['coverage_state']} · {row['readiness_class'].split('_')[0]}", fill="white", font=font)
        draw.text((left + 10, top + 32), row["scale_role"].replace("_", " ")[:34], fill="#e7edf3", font=font)
        draw.text((left + 10, top + 54), f"width {row['width_range_px'][0]}–{row['width_range_px'][1]} · cast {len(row['visible_adult_cast'])}", fill="#d2dbe4", font=font)
        draw.text((left + 10, top + 76), f"candidates {row['existing_candidate_count']} · {row['engineering_rollup']}", fill="#d2dbe4", font=font)
        draw.text((left + 10, top + 98), f"next prompt null · accepted 0", fill="#ffe0a8", font=font)
        draw.text((left + 10, top + 120), f"blockers {len(row['blockers'])}", fill="#ffe0a8", font=font)
    image.save(CHART, optimize=False)


def main() -> int:
    plans = json.loads(PLANS.read_text(encoding="utf-8"))["plans"]
    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))["rows"]
    scale = json.loads(SCALE.read_text(encoding="utf-8"))["rows"]
    assertions = json.loads(ASSERTIONS.read_text(encoding="utf-8"))["plans"]
    records = json.loads(RENDER_INDEX.read_text(encoding="utf-8"))["records"]
    next_rows = json.loads(NEXT.read_text(encoding="utf-8"))["rows"]
    by_coverage = {row["panel_id"]: row for row in coverage}
    by_scale = {row["panel_id"]: row for row in scale}
    by_assertion = {row["panel_id"]: row for row in assertions}
    by_candidate: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        if record["candidate_class"] == "CH05_COMIC_PANEL_CANDIDATE":
            by_candidate[record["comic_panel_plan_id"]].append(record)
    dry_panels = {row["panel_id"] for row in next_rows}
    rows = []
    for plan in plans:
        panel_id = plan["panel_id"]
        cov, sizing, continuity = by_coverage[panel_id], by_scale[panel_id], by_assertion[panel_id]
        candidates = by_candidate.get(panel_id, [])
        classes = [engineering_class(record["engineering_review"]["results"]) for record in candidates]
        if "PASS" in classes:
            rollup = "AT_LEAST_ONE_PASS"
        elif "WARN" in classes:
            rollup = "WARN_ONLY_AVAILABLE"
        elif "FAIL" in classes:
            rollup = "FAIL_ONLY_AVAILABLE"
        else:
            rollup = "NO_CANDIDATE"
        coverage_state = cov["coverage_state"]
        if coverage_state == "selected":
            readiness = "EVIDENCE_SELECTED_OWNER_PENDING"
            blockers = ["owner_candidate_decision", "final_copy_or_silence", "commercial_clearance", "exact_production_base_decision"]
        elif panel_id in dry_panels:
            readiness = "DRY_RUN_OWNER_GATES_PENDING"
            blockers = ["owner_route_decision", "candidate_style_review", "microsequence_cadence", "final_copy_or_silence", "exact_reference_selection", "commercial_clearance"]
        elif coverage_state == "A":
            readiness = "PRIORITIZED_NO_DRY_RUN"
            blockers = ["style_size_hypothesis", "production_manifest", "review_contract", "final_copy_or_silence", "exact_reference_selection", "commercial_clearance"]
        else:
            readiness = "BACKLOG_PLAN_ONLY"
            blockers = ["tranche_priority", "style_size_hypothesis", "production_manifest", "review_contract", "final_copy_or_silence", "exact_reference_selection", "commercial_clearance"]
        rows.append(
            {
                "display_order": plan["display_order"],
                "panel_id": panel_id,
                "plan_revision_id": plan["plan_revision_id"],
                "plan_canonical_sha256": cov["plan_canonical_sha256"],
                "narrative_beat": plan["narrative_beat"],
                "narrative_function": cov["narrative_function"],
                "motion_mode": cov["motion_mode"],
                "coverage_state": coverage_state,
                "visible_adult_cast": continuity["visible_adult_cast"],
                "continuity_assertions_present": True,
                "scale_role": sizing["scale_role"],
                "width_range_px": sizing["width_range_px"],
                "recommended_mechanisms": MECHANISM_BY_ROLE[sizing["scale_role"]],
                "existing_candidate_ids": [record["candidate_id"] for record in candidates],
                "existing_candidate_count": len(candidates),
                "engineering_classes": classes,
                "engineering_rollup": rollup,
                "current_selected_candidate_id": sizing["current_selected_candidate_id"],
                "p010_p013_dry_run_row": panel_id in dry_panels,
                "next_production_prompt": None,
                "final_copy_bound": False,
                "owner_accepted": False,
                "commercially_cleared": False,
                "execution_ready": False,
                "comic_panel_plan_revision_created": False,
                "readiness_class": readiness,
                "blockers": blockers,
            }
        )
    build_chart(rows)
    counts = {key: sum(row["readiness_class"] == key for row in rows) for key in ("EVIDENCE_SELECTED_OWNER_PENDING", "DRY_RUN_OWNER_GATES_PENDING", "PRIORITIZED_NO_DRY_RUN", "BACKLOG_PLAN_ONLY")}
    manifest = {
        "record_type": "ComicChapterProductionReadinessMatrix",
        "schema_version": "1.0",
        "record_id": "ng-ch05-chapter-production-readiness-matrix-r1",
        "state": "FIFTY_PLAN_FAIL_CLOSED_READINESS_OWNER_PENDING",
        "medium": "comic",
        "inputs": [binding(path) for path in (PLANS, COVERAGE, SCALE, ASSERTIONS, RENDER_INDEX, NEXT, ROUTE)],
        "summary": {"plan_count": 50, "selected_evidence": counts["EVIDENCE_SELECTED_OWNER_PENDING"], "dry_run_rows": counts["DRY_RUN_OWNER_GATES_PENDING"], "tier_a_without_dry_run": counts["PRIORITIZED_NO_DRY_RUN"], "backlog_plan_only": counts["BACKLOG_PLAN_ONLY"], "plans_with_existing_candidates": sum(bool(row["existing_candidate_count"]) for row in rows), "existing_ch05_candidates": sum(row["existing_candidate_count"] for row in rows), "next_prompt_count": 0, "final_copy_bound": 0, "owner_accepted": 0, "commercially_cleared": 0, "execution_ready": 0, "plan_revisions": 0, "provider_calls": 0, "uploads": 0, "cost_usd": 0, "human_review_minutes": None},
        "rows": rows,
        "chart": {"path": CHART.relative_to(ROOT).as_posix(), "sha256": sha(CHART), "dimensions": [1600, 1900]},
        "comic_panel_plan_revision_created": False,
        "animation_shot_plan": None,
        "e_conte": None,
        "boundary": "Read-only readiness join. No prompt, plan, review, provider, upload, acceptance, commercial, or execution state changes.",
    }
    OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    evidence = {"record_type": "ComicChapterProductionReadinessMatrixEvidence", "schema_version": "1.0", "record_id": "ng-ch05-chapter-production-readiness-matrix-evidence-r1", "state": "PASS_OWNER_PENDING", "manifest": binding(OUTPUT), "inputs": manifest["inputs"], "summary": manifest["summary"], "chart": manifest["chart"], "animation_shot_plan": None, "e_conte": None}
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"CH05 chapter readiness: 50 = selected {counts['EVIDENCE_SELECTED_OWNER_PENDING']} + dry-run {counts['DRY_RUN_OWNER_GATES_PENDING']} + Tier-A {counts['PRIORITIZED_NO_DRY_RUN']} + backlog {counts['BACKLOG_PLAN_ONLY']}")
    print("next prompts/copy/accepted/commercial/executable/revisions/calls/uploads/cost 0/0/0/0/0/0/0/0/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
