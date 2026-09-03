"""Compile the current hash-bound CH05 r6 owner-review pointer."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_OUT = ROOT / "docs/research/evidence/ch05-r6-owner-review-start-here-r1.json"
MARKDOWN_OUT = ROOT / "docs/research/ch05-r6-owner-review-start-here-r1.md"
SOURCES = [
    ROOT / "docs/research/evidence/ch05-complete-chapter-release-r6.json",
    ROOT / "production/comic/run-manifests/ch05-complete-chapter-production-manifest-r6.json",
    ROOT / "production/comic/run-manifests/ch05-complete-chapter-assembly-manifest-r6.json",
    ROOT / "docs/research/evidence/cross-chapter-comic-regression-r1.json",
    ROOT / "production/comic/style-direction/north-garden-cross-chapter-continuity-r1.json",
    ROOT / "docs/research/evidence/comic-panel-plan-chapter-inventory-r1.json",
    ROOT / "production/comic/contracts/complete-chapter-comicpanelplan-authoring-contract-r1.json",
    ROOT / "docs/research/evidence/complete-chapter-semantic-graph-validator-r1.json",
    ROOT / "docs/research/evidence/post-ch05-complete-chapter-integrated-release-r1.json",
    ROOT / "docs/research/ch05-complete-chapter-review-handoff-r6.md",
]
STRONGEST_IDS = [
    "ng-ch05-sc01-p001", "ng-ch05-sc01-p017", "ng-ch05-sc01-p020", "ng-ch05-sc01-p029",
    "ng-ch05-sc01-p031", "ng-ch05-sc01-p033", "ng-ch05-sc01-p036", "ng-ch05-sc01-p039",
    "ng-ch05-sc01-p043", "ng-ch05-sc01-p044", "ng-ch05-sc01-p048", "ng-ch05-sc01-p049",
    "ng-ch05-sc01-p050",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def binding(path: Path) -> dict[str, str]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def absolute(relative: str) -> str:
    return (ROOT / relative).as_posix()


def selected_artifact(panel: dict[str, Any], assembly_entry: dict[str, Any]) -> dict[str, Any]:
    candidate = panel["candidate"]
    return {
        "panel_id": panel["panel_id"], "display_order": panel["display_order"],
        "candidate_id": assembly_entry["candidate_id"],
        "path": candidate["path"], "sha256": candidate["sha256"],
        "width_px": candidate["width_px"], "height_px": candidate["height_px"],
        "owner_review_state": panel["review"]["human_state"], "accepted": panel["review"]["accepted"],
    }


def main() -> int:
    release, production, assembly, cross, continuity, inventory, contract, semantic, integrated, _ = [load(path) if path.suffix == ".json" else {} for path in SOURCES]
    panel_map = {row["panel_id"]: row for row in production["panels"]}
    assembly_map = {row["panel_id"]: row for row in assembly["entries"]}
    strongest = [selected_artifact(panel_map[panel_id], assembly_map[panel_id]) for panel_id in STRONGEST_IDS]
    selected_p032 = selected_artifact(panel_map["ng-ch05-sc01-p032"], assembly_map["ng-ch05-sc01-p032"])
    diagnostic = production["diagnostic_candidates"][0]
    warning_candidates = [
        {**selected_p032, "status": "SELECTED_WARN"},
        {
            "panel_id": diagnostic["panel_id"], "display_order": 32,
            "candidate_id": diagnostic["candidate_id"], "path": diagnostic["output"]["path"],
            "sha256": diagnostic["output"]["sha256"], "width_px": diagnostic["output"]["width"],
            "height_px": diagnostic["output"]["height"], "owner_review_state": diagnostic["human_review_state"],
            "accepted": diagnostic["accepted"], "status": "DIAGNOSTIC_WARN_NOT_SELECTED",
        },
    ]
    artifacts = [{**row, "section": "CH05_COMPLETE_CHAPTER"} for row in release["review_artifacts"]]
    artifacts += [{**row, "section": "CROSS_CHAPTER_CONTINUITY"} for row in cross["artifacts"]]
    document = {
        "record_type": "CH05R6OwnerReviewStartHere",
        "schema_version": "1.0",
        "record_id": "ng-ch05-r6-owner-review-start-here-r1",
        "state": "NAVIGATION_READY_OWNER_REVIEW_PENDING",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "source_bindings": [binding(path) for path in SOURCES],
        "measured_summary": {
            "chapter_panels": release["measured_summary"]["selected_chapter_panels"],
            "panel_candidates": release["measured_summary"]["panel_level_candidates"],
            "raster_outputs": release["measured_summary"]["built_in_raster_outputs"],
            "agent_triage": release["measured_summary"]["agent_triage"],
            "review_artifacts": len(artifacts),
            "strongest_candidates": len(strongest),
            "warning_candidates": len(warning_candidates),
            "chapter_inventory_plans": inventory["summary"]["total_current_panel_plans"],
            "cross_chapter_panels": cross["summary"]["panels"],
            "integrated_release_commands": integrated["summary"]["orchestrator_commands"],
            "integrated_release_effective_checks": integrated["summary"]["effective_checks"],
            "human_review_minutes": None,
            "accepted": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
        "review_order": [row["kind"] for row in artifacts],
        "review_artifacts": artifacts,
        "strongest_candidates": strongest,
        "warning_candidates": warning_candidates,
        "decision_groups": {
            "visual": [
                {"decision_id": "ch05_r6_overall_visual_disposition", "state": "PENDING"},
                {"decision_id": "p032_orientation_disposition", "state": "PENDING"},
                {"decision_id": "lettering_density_and_overlap", "state": "PENDING"},
                {"decision_id": "preferred_style_and_cadence_adjustments", "state": "PENDING"},
            ],
            "canon": [
                {"decision_id": "ch05_identity_contract_vs_historical_hair_colors", "state": "PENDING"},
                {"decision_id": "future_wardrobe_armor_weapon_progression", "state": "PENDING"},
                {"decision_id": "future_monster_class_and_system_ui_introduction", "state": "PENDING"},
            ],
            "rights_and_production": [
                {"decision_id": "commercial_clearance", "state": "NOT_EVALUATED"},
                {"decision_id": "exact_production_base", "state": "NOT_EVALUATED"},
                {"decision_id": "historical_panel_replacement", "state": "NOT_AUTHORIZED"},
            ],
        },
        "pipeline_next_state": {
            "full_chapter_authoring_contract": binding(SOURCES[6]),
            "semantic_validation": {"positive": "1/1", "adversarial": "23/23"},
            "next_full_chapter_render_ready": False,
            "reason": "No approved chapter-scale ComicPanelPlan source exists beyond CH05.",
        },
        "boundary": {"publication": 0, "provider_calls": 0, "uploads": 0, "generation": 0, "owner_decisions_recorded": 0, "acceptance": 0, "commercial_decisions": 0},
    }
    EVIDENCE_OUT.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_OUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    lines = [
        "# CH05 r6 owner review — start here", "",
        "R6 is the current complete 50-panel reading draft: **49 PASS / 1 WARN / 0 FAIL** in non-gating agent triage. Nothing is automatically accepted, commercially cleared, or declared an exact production base.", "",
        "## Review the chapter", "",
    ]
    for index, row in enumerate(artifacts, 1):
        label = row["kind"].replace("_", " ").title()
        lines.append(f"{index}. [{label}]({absolute(row['path'])}) — {row['width_px']} × {row['height_px']}, SHA-256 `{row['sha256']}`.")
    lines += ["", "## Strongest current panels", ""]
    for row in strongest:
        lines.append(f"- [{row['panel_id'].split('-')[-1].upper()}]({absolute(row['path'])}) — {row['width_px']} × {row['height_px']}, SHA-256 `{row['sha256']}`.")
    lines += ["", "## One unresolved panel", ""]
    for row in warning_candidates:
        label = "selected" if row["status"] == "SELECTED_WARN" else "diagnostic, not selected"
        lines.append(f"- [P032 {label}]({absolute(row['path'])}) — {row['width_px']} × {row['height_px']}, SHA-256 `{row['sha256']}`.")
    lines += [
        "", "P032's toe-versus-heel direction remains ambiguous at phone width after two targeted attempts. Decide whether the clue reads well enough, needs deterministic local repair, or needs a revised ComicPanelPlan.", "",
        "## Keep these decisions separate", "",
        "- Visual: overall R6 disposition, P032, lettering density/overlap, and preferred style/cadence changes.",
        "- Canon: current CH05 hair/wardrobe contract versus historical colors, and when armor/weapons/monsters/classes/UI enter the story.",
        "- Rights/production: commercial clearance, exact-production-base status, and any replacement of historical selected panels.", "",
        "## Engineering evidence", "",
        f"- [R6 release record]({absolute(SOURCES[0].relative_to(ROOT).as_posix())})",
        f"- [Cross-chapter continuity record]({absolute(SOURCES[3].relative_to(ROOT).as_posix())})",
        f"- [Chapter inventory]({absolute(SOURCES[5].relative_to(ROOT).as_posix())})",
        f"- [Complete-chapter authoring contract]({absolute(SOURCES[6].relative_to(ROOT).as_posix())})",
        f"- [Semantic graph evidence]({absolute(SOURCES[7].relative_to(ROOT).as_posix())})",
        f"- [Integrated release]({absolute(SOURCES[8].relative_to(ROOT).as_posix())}) — 10/10 commands, 93 effective checks.", "",
        "Measured totals: 16 raster outputs, 59 panel candidates, 34 authorized reference uses, approximately 1,200.7 seconds overlap-adjusted generation wall time, and $0 direct paid API/cloud spend. Built-in monetary cost/model/endpoint/request IDs/usage/seed remain unavailable. Human review minutes remain null.", "",
        "The next full chapter is not render-ready because CH01-CH04 contain only scene fragments. The new authoring contract is ready for an approved chapter-scale story without embedding canon invention in render prompts.",
    ]
    MARKDOWN_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"evidence": EVIDENCE_OUT.relative_to(ROOT).as_posix(), "evidence_sha256": sha256(EVIDENCE_OUT), "markdown": MARKDOWN_OUT.relative_to(ROOT).as_posix(), "markdown_sha256": sha256(MARKDOWN_OUT), "artifacts": len(artifacts), "strongest": len(strongest), "warnings": len(warning_candidates)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
