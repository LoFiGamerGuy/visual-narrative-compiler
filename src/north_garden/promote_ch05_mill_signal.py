"""Promote approved CH05 development intent into new pre-render comic records.

This is deliberately a one-way, r1 record creation tool. It never edits the
development script and never turns visual-smoke samples into accepted art.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEVELOPMENT = ROOT / "research/development/clean-ch05-mill-signal-r1.json"
DECISION = ROOT / "production/decisions/ng-decision-ch05-mill-signal-promotion-r1.json"
OUTPUTS = {
    "story": ROOT / "production/canon/story-state/ch05-sc01-r1.json",
    "assets": ROOT / "production/assets/asset-registry-ch05-r1.json",
    "beat": ROOT / "production/scene-beats/ch05-sc01-mill-signal-r1.json",
    "style": ROOT / "production/comic/style-direction/ch05-mill-signal-r1.json",
    "plans": ROOT / "production/comic/ch05-sc01-panel-plans-v1.json",
    "assertions": ROOT / "production/comic/hard-assertion-manifests/ch05-mill-signal-r1.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def motion_for(beat: str) -> tuple[str, str]:
    lower = beat.lower()
    if any(term in lower for term in ("run", "climb", "cross", "walk", "follow", "circle", "leave", "retreat", "step")):
        return "directional_motion", "Use one clear travel vector; reserve motion marks for feet, water, cloth, or map edge rather than filling the frame."
    if any(term in lower for term in ("reach", "braces", "cuts", "signals", "tests")):
        return "practical_action", "Make the causal hand/object relationship legible before adding atmospheric texture."
    if any(term in lower for term in ("rings", "drip", "smoke", "disappears", "goes out", "still")):
        return "held_sensory_event", "Use restrained line/vibration or smoke flow only at the event source; preserve surrounding negative space."
    return "held_observation", "Prioritize silhouette, eyeline, and one readable story object; do not add decorative action marks."


def lettering_for(index: int, cast: list[str]) -> dict[str, object]:
    if not cast:
        return {"state": "NO_DIALOGUE_EXPECTED", "safe_zones": [{"anchor": "top", "rect_norm": [0.25, 0.04, 0.50, 0.16]}]}
    anchor = "top_left" if index % 2 else "top_right"
    x = 0.04 if anchor == "top_left" else 0.66
    return {"state": "LOW_TEXT_LOAD_PROPOSED_PENDING_SCRIPT_DIALOGUE", "safe_zones": [{"anchor": anchor, "rect_norm": [x, 0.04, 0.30, 0.18]}], "rule": "Protect this zone from faces, hands, story props, and dense crosshatching; later lettering layout may supersede it."}


def main() -> None:
    development = json.loads(DEVELOPMENT.read_text(encoding="utf-8"))
    decision = json.loads(DECISION.read_text(encoding="utf-8"))
    assert decision["state"] == "APPROVED_FOR_CANON_AND_COMIC_PANEL_PLAN_DEVELOPMENT"
    assert decision["source_development_script_sha256"] == sha256(DEVELOPMENT)
    for path in OUTPUTS.values():
        if path.exists():
            raise SystemExit(f"refusing to overwrite immutable promotion output: {path}")
    panels = development["panels"]
    story = {
        "record_type": "StoryState", "schema_version": "1.0", "record_id": "ng-story-ch05-sc01-r1",
        "scope": "CH05_SC01_APPROVED_COMIC_DEVELOPMENT_PRE_RENDER", "fictional_cast": ["SOREN", "SIGRID"],
        "set": "FARMHOUSE_DAWN_TRAIL_ABANDONED_WATER_MILL_RIDGE_RETURN", "timeline_state": "MORNING_AFTER_SMOKE_COLUMN",
        "wardrobe_state": {"SOREN": "pale oatmeal work coat", "SIGRID": "practical plaid wrap over expedition clothing"},
        "narrative_state": "The fictional adult pair investigate a smoke signal at an abandoned mill and return toward an unexpectedly active farmhouse.",
        "promotion_decision": str(DECISION.relative_to(ROOT)).replace("\\", "/"),
        "source_limit": "Approved current comic development intent; pre-render only. It does not establish renderer choice, final art, commercial clearance, adult likeness, canonical grounded set, or animation direction.",
    }
    assets = {
        "record_type": "AssetRegistry", "schema_version": "1.0", "record_id": "ng-assets-ch05-sc01-r1", "story_state_id": story["record_id"],
        "assets": [
            {"asset_id": "ng-identity-soren-fictional-design-r1", "kind": "fictional_character_design", "state": "GENERATIVE_REFERENCE_CONTINUITY_UNVERIFIED", "usable_for": "current comic-development research only", "not_usable_for": "adult likeness, commercial lock, animation authority"},
            {"asset_id": "ng-identity-sigrid-fictional-design-r1", "kind": "fictional_character_design", "state": "GENERATIVE_REFERENCE_CONTINUITY_UNVERIFIED", "usable_for": "current comic-development research only", "not_usable_for": "adult likeness, commercial lock, animation authority"},
            {"asset_id": "ng-set-mill-signal-2d-direction-r1", "kind": "set_direction", "state": "COMIC_2D_ONLY_PRE_RENDER_NOT_CANONICAL_STAGE", "usable_for": "CH05 comic planning", "not_usable_for": "grounded canonical set or animation shot"},
        ],
    }
    beat = {
        "record_type": "SceneBeat", "schema_version": "1.0", "record_id": "ng-beat-ch05-sc01-mill-signal-r1", "story_state_id": story["record_id"],
        "narrative_intent": "A dawn clue becomes an exploration of an abandoned mill, a practical discovery, and a reversal that sends the pair back to the farmhouse.",
        "comic_direction_boundary": "Direction is contained in ComicPanelPlans and ComicStyleDirection; AnimationShotPlan/E-Conte is intentionally absent.",
        "development_source": str(DEVELOPMENT.relative_to(ROOT)).replace("\\", "/"),
    }
    style = {
        "record_type": "ComicStyleDirection", "schema_version": "1.0", "record_id": "ng-comic-style-ch05-mill-signal-r1", "medium": "comic", "animation_shot_plan": None,
        "state": "PRE_RENDER_DIRECTION_NOT_EXECUTION_PROVENANCE", "visual_language": {
            "line_and_value": "Use controlled dark-fantasy ink contrast, but reserve low-detail breathing space around silhouettes, lettering zones, and story objects.",
            "density_rule": "Every panel needs a primary read at phone width: one action or object, one dominant value mass, and one protected low-density area. Background texture must yield to the read.",
            "motion_rule": "Use selective directional marks only for a causally necessary event (footfall splash, smoke drift, bell vibration, taut twine, running cloth). Do not apply manga speed lines as a global texture.",
            "lettering_rule": "Plans carry proposed normalized safe zones, not final balloons. Lettering remains a later comic-layout artifact and is never inferred from raster art.",
        },
    }
    plan_rows = []
    assertions = []
    for source in panels:
        order = source["display_order"]
        motion, direction_note = motion_for(source["beat"])
        panel_id = f"ng-ch05-sc01-p{order:03d}"
        cast = source["visible_adult_cast"]
        plan_rows.append({
            "panel_id": panel_id, "plan_revision_id": f"{panel_id}-plan-r1", "display_order": order, "development_panel_id": source["panel_id"],
            "spatial_mode": "2d_only", "scene_beat_id": beat["record_id"], "asset_ids": ["ng-set-mill-signal-2d-direction-r1", *(["ng-identity-soren-fictional-design-r1"] if "SOREN" in cast else []), *(["ng-identity-sigrid-fictional-design-r1"] if "SIGRID" in cast else [])],
            "spatial_stage_contract_id": None, "spatial_assignments": [], "narrative_beat": source["beat"], "composition_intent": source["composition"],
            "visible_adult_cast": cast, "comic_direction": {"motion_mode": motion, "direction_note": direction_note, "lettering": lettering_for(order, cast)},
        })
        assertions.append({"id": f"p{order:03d}_core_read", "applicability": panel_id, "severity": "hard", "requirement": f"{source['beat']} Composition requirement: {source['composition']}."})
    plans = {
        "record_type": "ComicPanelPlanCollection", "schema_version": "2.0", "record_id": "ng-comic-plans-ch05-sc01-r1", "story_state_id": story["record_id"], "medium": "comic", "animation_shot_plan": None,
        "identity_boundary": "panel_id is stable across corrections; plan_revision_id versions intent and is not display order.", "promotion_decision": str(DECISION.relative_to(ROOT)).replace("\\", "/"), "plans": plan_rows,
    }
    manifest = {
        "record_type": "HardAssertionManifest", "schema_version": "1.0", "record_id": "ng-hard-assertions-ch05-mill-signal-r1", "state": "APPROVED_CURRENT_COMIC_PRE_RENDER_NOT_BENCHMARK", "medium": "comic", "animation_shot_plan": None,
        "intent_scope": {"panel_plan_collection": str(OUTPUTS['plans'].relative_to(ROOT)).replace("\\", "/"), "spatial_mode": "2d_only", "boundary": "No grounded-stage, final-art, commercial, or animation inference."},
        "review_rule": "Research acceptance requires every applicable hard assertion and an authorized timed human review; agent visual triage is non-gating.",
        "assertions": [{"id": "fictional_adult_design_only", "severity": "hard", "requirement": "Use only fictional adult character design inputs; no real-person/adult-likeness input or child data."}, {"id": "comic_single_panel", "severity": "hard", "requirement": "One undivided comic panel with declared composition; final lettering is evaluated through a separate layout artifact."}, {"id": "practical_wardrobe", "severity": "hard", "requirement": "Soren retains pale oatmeal work coat and Sigrid retains practical plaid wrap unless an explicit future panel plan revision says otherwise."}, *assertions],
    }
    payloads = {"story": story, "assets": assets, "beat": beat, "style": style, "plans": plans, "assertions": manifest}
    for key, payload in payloads.items():
        OUTPUTS[key].parent.mkdir(parents=True, exist_ok=True)
        OUTPUTS[key].write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("Created " + ", ".join(str(path.relative_to(ROOT)).replace("\\", "/") for path in OUTPUTS.values()))


if __name__ == "__main__":
    main()
