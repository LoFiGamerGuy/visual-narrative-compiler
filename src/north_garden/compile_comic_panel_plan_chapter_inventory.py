"""Inventory chapter-scale ComicPanelPlan readiness without inventing missing canon."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
JSON_OUT = ROOT / "docs/research/evidence/comic-panel-plan-chapter-inventory-r1.json"
MD_OUT = ROOT / "docs/research/comic-panel-plan-chapter-inventory-r1.md"
ROWS = [
    ("CH01", "production/comic/ch01-sc01-panel-plans-v2.json", "production/comic/panel-revisions/ch01-sc01-initial-import-r1.json", "production/editions/north-garden-research-edition-002.json", "SCENE_FRAGMENT_ONLY"),
    ("CH02", "production/comic/ch02-sc01-panel-plans-v1.json", "production/comic/panel-revisions/ch02-sc01-historical-import-r1.json", "production/editions/north-garden-ch02-research-edition-001.json", "SCENE_FRAGMENT_ONLY"),
    ("CH03", "production/comic/ch03-sc01-panel-plans-v1.json", "production/comic/panel-revisions/ch03-sc01-imagegen-r1.json", "production/editions/north-garden-ch03-imagegen-draft-edition-001.json", "SCENE_FRAGMENT_ONLY"),
    ("CH04", "production/comic/ch04-sc01-panel-plans-v1.json", "production/comic/panel-revisions/ch04-sc01-imagegen-r1.json", "production/editions/north-garden-ch04-imagegen-draft-edition-001.json", "SCENE_FRAGMENT_ONLY"),
    ("CH05", "production/comic/ch05-sc01-panel-plans-v1.json", "production/comic/run-manifests/ch05-complete-chapter-production-manifest-r6.json", "docs/research/evidence/ch05-complete-chapter-release-r6.json", "FULL_CHAPTER_REVIEW_READY"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def bind(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    return {"path": relative, "sha256": sha256(path), "bytes": path.stat().st_size}


def main() -> int:
    chapters = []
    for chapter, plan_rel, revision_rel, edition_rel, readiness in ROWS:
        plan = load(ROOT / plan_rel)
        plans = plan.get("plans", [])
        if plan.get("record_type") != "ComicPanelPlanCollection":
            raise ValueError(f"unexpected planning record: {plan_rel}")
        if plan.get("animation_shot_plan") is not None or plan.get("e_conte") is not None:
            raise ValueError(f"cross-medium field populated: {plan_rel}")
        ids = [row["panel_id"] for row in plans]
        if len(ids) != len(set(ids)):
            raise ValueError(f"duplicate panel ids: {plan_rel}")
        chapter_row = {
            "chapter": chapter,
            "readiness": readiness,
            "plan_source": bind(plan_rel),
            "record_id": plan["record_id"],
            "panel_count": len(plans),
            "panel_ids": ids,
            "planning_structure": "ComicPanelPlan",
            "animation_shot_plan": None,
            "e_conte": None,
            "art_or_revision_binding": bind(revision_rel),
            "edition_or_release_binding": bind(edition_rel),
        }
        if chapter == "CH05":
            release = load(ROOT / edition_rel)
            chapter_row["candidate_count"] = release["measured_summary"]["panel_level_candidates"]
            chapter_row["selected_panel_count"] = release["measured_summary"]["selected_chapter_panels"]
            chapter_row["review_state"] = release["state"]
        else:
            revisions = load(ROOT / revision_rel).get("revisions", [])
            chapter_row["candidate_count"] = len(revisions)
            chapter_row["selected_panel_count"] = len(revisions)
            chapter_row["review_state"] = load(ROOT / edition_rel).get("publication_state", "UNSPECIFIED")
        chapters.append(chapter_row)

    full = [row["chapter"] for row in chapters if row["readiness"] == "FULL_CHAPTER_REVIEW_READY"]
    fragments = [row["chapter"] for row in chapters if row["readiness"] == "SCENE_FRAGMENT_ONLY"]
    result = {
        "record_type": "ComicPanelPlanChapterInventory",
        "schema_version": "1.0",
        "record_id": "ng-comic-panel-plan-chapter-inventory-r1",
        "state": "CURRENT_SOURCE_INVENTORY",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "summary": {
            "chapters_inventoried": len(chapters),
            "full_chapter_review_ready": full,
            "scene_fragment_only": fragments,
            "total_current_panel_plans": sum(row["panel_count"] for row in chapters),
            "next_full_chapter_render_ready": False,
        },
        "chapters": chapters,
        "decision": {
            "current_production_baseline": "CH05 r6",
            "next_action": "HARDEN_REUSABLE_CHAPTER_PIPELINE_AND_REQUEST_OR_AUTHOR_APPROVED_FULL_COMICPANELPLAN_BEFORE_NEXT_CHAPTER_RENDER",
            "reason": "CH01-CH04 each contain only one 3-4-panel scene fragment; treating any as a complete chapter would fabricate missing narrative and cadence.",
        },
        "boundary": {
            "new_panel_plans_created": 0,
            "canon_changes": 0,
            "provider_calls": 0,
            "uploads": 0,
            "generated_pixels": 0,
            "commercial_or_acceptance_decisions": 0,
        },
    }
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    lines = [
        "# ComicPanelPlan chapter inventory r1", "",
        "CH05 r6 is the only current full-chapter review candidate. CH01-CH04 are useful continuity/story probes, but each contains only one 3-4-panel scene fragment.", "",
        "| Chapter | Current plans | Status | Art/revision state |", "|---|---:|---|---|",
    ]
    for row in chapters:
        lines.append(f"| {row['chapter']} | {row['panel_count']} | `{row['readiness']}` | `{row['review_state']}` |")
    lines += [
        "", "## Production decision", "",
        "Keep CH05 r6 as the current complete-chapter baseline. Reuse CH01-CH04 only for local continuity and pipeline regression tests. Do not call a 3-4-panel fragment a completed chapter or infer missing story beats.", "",
        "The next full chapter needs an approved chapter-scale ComicPanelPlan collection before rendering. Until then, local work can continue on release validation, continuity instrumentation, lettering, deterministic assembly, and cross-chapter regression coverage.", "",
        "No panel plan, canon fact, provider call, upload, generated pixel, acceptance, or commercial-use decision was created by this inventory.",
    ]
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"json": JSON_OUT.relative_to(ROOT).as_posix(), "sha256": sha256(JSON_OUT), "markdown": MD_OUT.relative_to(ROOT).as_posix(), "full": full, "fragments": fragments, "plans": result["summary"]["total_current_panel_plans"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
