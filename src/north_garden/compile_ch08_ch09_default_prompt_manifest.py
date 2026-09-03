"""Compile the one-route CH08-CH09 built-in ImageGen prompt manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from compile_ch06_ch07_default_prompt_manifest import REFERENCES, sha256

ROOT = Path(__file__).resolve().parents[2]
PLANS = {
    "CH08": ROOT / "production/comic/ch08-sc01-panel-plans-r1.json",
    "CH09": ROOT / "production/comic/ch09-sc01-panel-plans-r1.json",
}
DECISIONS = {
    "CH08": ROOT / "production/decisions/ng-decision-ch08-root-road-prompt-promotion-r1.json",
    "CH09": ROOT / "production/decisions/ng-decision-ch09-black-weir-prompt-promotion-r1.json",
}
OUTPUT = ROOT / "production/comic/run-manifests/ch08-ch09-default-house-route-prompt-manifest-r1.json"
MARKDOWN = ROOT / "docs/research/ch08-ch09-default-house-route-preflight-r1.md"

TEXT_REPLACEMENTS = {
    "a brief frost-green ROAD TENDED inscription travels across real brass": "a brief frost-green nonverbal route glyph travels across real brass without readable letters",
    "a brief frost-green ROUTE KEEPER inscription on those physical surfaces": "a brief frost-green nonverbal keeper glyph on those physical surfaces without readable letters",
    "frost-green letters form BELOW / ROUTE UNCONFIRMED": "a frost-green nonverbal route glyph forms without readable letters",
    "Frost-green letters rise in condensation on the socket—WAYFINDER PATH / EARNED BY RETURN—": "A frost-green nonverbal Wayfinder emblem rises in condensation on the socket without readable letters, then",
}


def visual_beat(raw: str) -> str:
    value = raw
    for source, replacement in TEXT_REPLACEMENTS.items():
        value = value.replace(source, replacement)
    return value


def uses_mechanics_reference(panels: list[dict[str, Any]]) -> bool:
    joined = " ".join(panel["narrative_beat"].lower() for panel in panels)
    return any(
        token in joined
        for token in ("lever", "brace", "weight", "hauls", "counterweight", "load-bearing", "anchors the rope")
    )


def sequence_prompt(chapter: dict[str, Any], panels: list[dict[str, Any]]) -> str:
    reference_rows = REFERENCES if uses_mechanics_reference(panels) else REFERENCES[:2]
    references = "\n".join(reference["role"] for reference in reference_rows)
    lines = []
    for order, panel in enumerate(panels, start=1):
        cast = ", ".join(panel["visible_adult_cast"]) or "NO PEOPLE"
        lines.append(
            f"Panel {order} ({panel['panel_id']}; {panel['scale_role']}; {panel['density_class']}): "
            f"{visual_beat(panel['narrative_beat'])} Composition: {panel['composition_intent']} Visible cast: {cast}."
        )
    return f"""Use case: illustration-story
Asset type: North Garden {chapter['chapter_title']} five-panel chronological webcomic sequence strip
Primary request: Render exactly five clearly separated panels in the numbered narrative order below as one coherent left-to-right story strip. Use one row only, with clean light gutters. Do not add visible panel numbers, grid labels, captions, or a second comic row. Preserve causal state and object positions from panel to panel.
Input images:
{references}
Scene/backdrop: {chapter['chapter_title']}; use only the locations, weather, fictional adults, creature, and objects named in the specifications.
Style/medium: mature clean graphic webcomic with restrained painterly color and selective premium cel finish; clear silhouettes, controlled density, expressive mature faces, readable hands, natural material wear, and phone-readable action.
Panel specifications:
{chr(10).join(lines)}
Character/gear invariants: SOREN is a clearly fictional adult with a weathered angular face, light stubble, and short-to-medium swept-back light-brown to dark-blond wavy hair—never black or bright blond. His evolved road gear visibly retains the pale oatmeal work coat beneath quilted shoulder repair and thin practical guards. Warden's Reach is an improvised long wooden polehook made from a hay-fork shaft and pruning hook—never a gun, firearm, crossbow, or complex machine. SIGRID is a clearly fictional adult with an athletic mature build, angular face, dark brows, and dark-brown to near-black hair in a compact low bun or practical braid—never blond or loose red curls. Her evolved road gear visibly retains the dark blue-brown plaid as a secured weather cape with a scorched edge over practical gray-green layers; her compact recurved bow remains a simple bow. TAMSIN_REEVE, if present, is a clearly fictional adult courier-cartographer with medium chestnut-brown hair in one practical braid, visibly distinct from Sigrid, practical non-sexualized field clothing, and a wrapped injured lower leg; never blond or black-haired.
Story invariants: the Garden Ledger appears only as restrained frost-green light or nonverbal emblems attached to real brass, stone, wire, water, condensation, glass, map, or tool surfaces. Render no readable Ledger words; planned copy will be lettered later. The Hollow Stag, if present, is a large mature fictional root-and-bark stag with hollow antlers, grounded animal anatomy, visible weight, and boundary-wire interaction—not a humanoid, generic deer, undead gore creature, dragon, or glowing demon.
Lettering composition: reserve the quiet regions declared by the ComicPanelPlans, but render no letters, captions, speech balloons, status prose, sound effects, panel numbers, logos, signatures, or watermark. Never cover faces, adult bodies, important hands, weapons, tools, map, key, wire, rope, injury brace, antlers, route marks, or story objects.
Motion: render literal foot placement, bow draw, polehook leverage, rope tension, water force, stone shift, branch load, wire pull, cloth movement, injury response, and weight transfer only where named. Do not substitute generic speed-line texture.
Constraints: adult-only fictional cast; no child; no child-coded person; no youth; no real-person likeness; no celebrity likeness; no biometric identity data; no sexualization or fetish styling; no modern objects, extra people, duplicated people, swapped roles, changed hair colors, changed signature garment ancestry, unexplained weapons, guns, extra monsters, gore, readable text, logo, or watermark."""


def decision(chapter_id: str, document: dict[str, Any]) -> dict[str, Any]:
    slug = "root-road" if chapter_id == "CH08" else "black-weir"
    return {
        "record_type": "ComicPanelPlanPromptPromotionDecision",
        "schema_version": "1.0",
        "record_id": f"ng-decision-{chapter_id.lower()}-{slug}-prompt-promotion-r1",
        "state": "APPROVED_FOR_EXACT_PROMPT_PREFLIGHT_NOT_YET_EXECUTED",
        "chapter": chapter_id,
        "source_plan": {
            "path": PLANS[chapter_id].relative_to(ROOT).as_posix(),
            "sha256": sha256(PLANS[chapter_id]),
            "panel_count": len(document["plans"]),
        },
        "approved_mechanism": "OPENAI_BUILT_IN_IMAGEGEN_ONLY",
        "approved_reference_hashes": [reference["sha256"] for reference in REFERENCES],
        "default_candidates_per_panel": 1,
        "whole_chapter_alternate_style_arms": 0,
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "visual_continuity_decisions": {
            "tamsin_hair": "medium_chestnut_brown_single_practical_braid_never_blond_or_black",
            "status": "PROVISIONAL_TEXT_PROMPT_ANCHOR_TO_PREVENT_CH07_DRIFT_NOT_CANON_ACCEPTANCE",
            "ledger_words": "WITHHELD_FROM_GENERATED_PIXELS_FOR_LOCAL_LETTERING",
        },
        "boundary": {
            "prompt_authoring_approved": True,
            "execution_requires_manifest_preflight_pass": True,
            "direct_paid_api": False,
            "bfl": False,
            "new_provider": False,
            "new_upload_class": False,
            "real_person_or_adult_likeness": False,
            "child_related_material": False,
            "private_reference": False,
            "lora_or_dataset": False,
            "accepted_or_commercially_cleared": False,
        },
        "adr": "ADR-0203",
    }


def main() -> int:
    documents = {chapter_id: json.loads(path.read_text(encoding="utf-8")) for chapter_id, path in PLANS.items()}
    for chapter_id, path in DECISIONS.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(decision(chapter_id, documents[chapter_id]), indent=2) + "\n", encoding="utf-8", newline="\n")
    requests = []
    for chapter_id, document in documents.items():
        by_id = {panel["panel_id"]: panel for panel in document["plans"]}
        for sequence in document["sequences"]:
            panels = [by_id[panel_id] for panel_id in sequence["panel_ids"]]
            prompt = sequence_prompt(document, panels)
            reference_rows = REFERENCES if uses_mechanics_reference(panels) else REFERENCES[:2]
            requests.append(
                {
                    "request_id": sequence["sequence_id"],
                    "chapter": chapter_id,
                    "sequence_id": sequence["sequence_id"],
                    "panel_ids": sequence["panel_ids"],
                    "prompt": prompt,
                    "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                    "reference_images": reference_rows,
                    "reference_count": len(reference_rows),
                    "execution_state": "PREFLIGHTED_NOT_EXECUTED",
                    "output": None,
                    "elapsed_seconds": None,
                    "model": None,
                    "endpoint": None,
                    "provider_request_id": None,
                    "usage": None,
                    "monetary_cost_usd": None,
                    "deterministic_seed": None,
                }
            )
    manifest = {
        "record_type": "MultiChapterBuiltInImageGenPromptManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch08-ch09-default-house-route-prompt-manifest-r1",
        "state": "PREFLIGHT_READY_FOR_AUTHORIZED_BUILT_IN_EXECUTION",
        "mechanism": "OPENAI_BUILT_IN_IMAGEGEN_ONLY",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "anti_duplication": {
            "chapter_count": 2,
            "sequence_requests": 16,
            "panel_plan_coverage": 80,
            "default_candidates_per_panel": 1,
            "whole_chapter_alternate_style_arms": 0,
            "targeted_repair_cap_per_failed_panel": 2,
        },
        "promotion_decisions": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)} for path in DECISIONS.values()
        ],
        "authorized_reference_boundary": {
            "images": REFERENCES,
            "only_these_exact_hashes": True,
            "new_generated_outputs_may_be_reuploaded": False,
            "bfl_uploads": 0,
            "other_provider_uploads": 0,
        },
        "requests": requests,
        "summary": {
            "chapters": 2,
            "sequences": len(requests),
            "panel_plans": sum(len(request["panel_ids"]) for request in requests),
            "reference_uses": sum(request["reference_count"] for request in requests),
            "provider_calls": 0,
            "outputs": 0,
            "paid_api_spend_usd": 0,
        },
        "limitations": [
            "CH08/CH09 evolved clothing, weapons, Hollow Stag, injury brace, and Wayfinder state are text-defined because new outputs cannot be re-uploaded as continuity references.",
            "Tamsin's chestnut-brown braid is a provisional prompt anchor introduced after measured CH07 hair drift, not art acceptance or canon-base selection.",
            "Planned Ledger wording is replaced by nonverbal physical glow/emblems so copy remains a local lettering operation.",
            "Built-in model, endpoint, provider request ID, usage, monetary cost, and deterministic seed remain unavailable unless exposed at execution.",
            "Five-panel generation is stochastic; output layout and story order require deterministic local validation.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    MARKDOWN.write_text(
        "\n".join(
            [
                "# CH08–CH09 default house-route preflight r1",
                "",
                "Sixteen chronological built-in ImageGen sequence requests cover all 80 CH08–CH09 ComicPanelPlans exactly once.",
                "",
                f"- Authorized reference uses: {manifest['summary']['reference_uses']} across only three previously authorized hashes.",
                "- One left-to-right five-panel row per request; no panel numbers, grid labels, status prose, or generator lettering.",
                "- Evolved oatmeal/plaid-derived armor, fixed hair, Warden's Reach polehook form, compact bow, physical Ledger emblems, Hollow Stag anatomy, and later braced-leg continuity are explicit.",
                "- Tamsin receives a provisional medium-chestnut braid prompt anchor to prevent the measured CH07 blond drift.",
                "- Default candidates: one per panel; wholesale alternate style arms: zero; new outputs remain ineligible for re-upload.",
                "- Provider calls, outputs, and paid API/cloud spend remain zero at preflight.",
                "",
                "This preflight changes no provider, upload class, license conclusion, acceptance, commercial clearance, or exact-production-base status.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"requests": len(requests), "panels": manifest["summary"]["panel_plans"], "reference_uses": manifest["summary"]["reference_uses"], "sha256": sha256(OUTPUT)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
