"""Compile the stage-aware CH12-CH13 built-in ImageGen prompt manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from compile_ch06_ch07_default_prompt_manifest import REFERENCES, sha256

ROOT = Path(__file__).resolve().parents[2]
PLANS = {
    "CH12": ROOT / "production/comic/ch12-sc01-panel-plans-r1.json",
    "CH13": ROOT / "production/comic/ch13-sc01-panel-plans-r1.json",
}
DECISIONS = {
    "CH12": ROOT / "production/decisions/ng-decision-ch12-map-lied-prompt-promotion-r1.json",
    "CH13": ROOT / "production/decisions/ng-decision-ch13-north-garden-prompt-promotion-r1.json",
}
OUTPUT = ROOT / "production/comic/run-manifests/ch12-ch13-default-house-route-prompt-manifest-r1.json"
MARKDOWN = ROOT / "docs/research/ch12-ch13-default-house-route-preflight-r1.md"
ADR = ROOT / "docs/adr/ADR-0212-promote-ch12-ch13-with-stage-aware-rupture-and-crownroot-controls.md"

TEXT_REPLACEMENTS = {
    "The frost-green TWO HANDS mark on the real brass key and stone splits along its engraved seam and goes dark as unilateral plans diverge.":
        "A frost-green nonverbal paired-hand-and-threshold emblem on the real brass key and stone splits along its engraved seam and goes dark as unilateral plans diverge, without readable letters.",
    "On the physical map margin they write separate authority, veto, halt, disclosure, and restart rules covering route, measured load, bodies, and material risk.":
        "On the physical map margin their two independent adult hands divide five blank ruled sections and place distinct nonverbal route, load, halt, disclosure, and restart marks; exact rule copy is reserved for local lettering.",
    "Both adults state intent and assent; only then does TWO HANDS, ONE THRESHOLD return across the real brass key and forged socket.":
        "Both adults visibly state intent and assent; only then does a frost-green nonverbal paired-hand-and-threshold emblem return across the real brass key and forged socket without readable letters.",
    "At day-five dawn injured Soren levers the fused Reach in the real gate socket while Sigrid closes a continuous plaid-flag route; green summer opens under winter sky as Crownroot speaks Hearth Warden.":
        "At day-five dawn injured Soren levers the fused Reach in the real gate socket while Sigrid closes a continuous plaid-flag route; green summer opens under winter sky and Crownroot stirs beyond the gate as both adults react to an unheard address, with exact dialogue reserved for local lettering.",
    "Condensation writes SINGLE KEEPER REQUIRED on a real glass door while one adult-hand-shaped brass recess opens beneath it.":
        "Condensation forms a frost-green nonverbal single-hand warning emblem on a real glass door while one adult-hand-shaped brass recess opens beneath it, without readable letters.",
    "Old maintenance tallies show each solo keeper carried the network until bodily rooting, while a shared-custodian mark remains unfinished.":
        "Old maintenance tallies show repeated nonverbal single-hand load glyphs ending in root patterns while an unfinished paired-hand custodian mark remains visible, without readable letters or human remains.",
    "Frost-green letters form on the fused tool's real socket—BOUNDARYWRIGHT WARDEN—earned through redirected load without sole ownership or injury cure.":
        "A frost-green nonverbal boundary-and-load class emblem forms on the fused tool's real socket, earned through redirected load without sole ownership or injury cure and without readable letters.",
    "On Sigrid's real bow grip and brass route plate, THORNPATH MARSHAL records that she made the seven-stop route usable by others.":
        "On Sigrid's real bow grip and brass route plate, a frost-green nonverbal seven-stop route class emblem records shared usability without readable letters.",
}


def json_text(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def visual_beat(raw: str) -> str:
    return TEXT_REPLACEMENTS.get(raw, raw)


def uses_mechanics_reference(panels: list[dict[str, Any]]) -> bool:
    joined = " ".join(panel["narrative_beat"].lower() for panel in panels)
    return any(
        token in joined
        for token in ("lever", "brace", "weight", "hauls", "counterweight", "load-bearing", "anchors the rope")
    )


def stage_invariant(chapter_id: str, sequence_id: str) -> str:
    if chapter_id == "CH13":
        return (
            "All five panels retain Soren's missing left oatmeal shoulder panel, Sigrid's shortened plaid cape with existing route-flag ties, "
            "and the brass boundary key permanently fused into Warden's Reach; never restore, separate, or duplicate them."
        )
    number = int(sequence_id.split("-s", maxsplit=1)[1][:2])
    if number <= 4:
        return (
            "Across all five panels Soren's oatmeal shoulder and Sigrid's full plaid cape remain intact, and the brass key remains separate from Warden's Reach; "
            "do not preview later damage or fusion."
        )
    if number == 5:
        return (
            "Panels 1-3 keep Soren's oatmeal shoulder intact; in Panel 4 he visibly cuts away the reinforced left shoulder panel, and Panel 5 retains that exact missing panel. "
            "Sigrid's plaid remains intact and the brass key remains separate throughout."
        )
    if number == 6:
        return (
            "Soren's left oatmeal shoulder panel is already missing. Panels 1-2 keep Sigrid's plaid cape intact; in Panel 3 she cuts it into route flags and shortens it, "
            "and Panels 4-5 retain the shortened cape and those same flags. The brass key remains separate throughout."
        )
    if number == 7:
        return (
            "All five panels retain Soren's missing left oatmeal shoulder panel and Sigrid's shortened plaid cape with route flags; the brass key remains separate from Warden's Reach."
        )
    return (
        "All five panels retain Soren's missing left oatmeal shoulder panel and Sigrid's shortened plaid cape with route flags. "
        "Panels 1-3 keep the brass key separate; in Panel 4 pressure permanently fuses it into Warden's Reach, and Panel 5 retains the fused tool."
    )


def sequence_prompt(chapter_id: str, chapter: dict[str, Any], sequence: dict[str, Any], panels: list[dict[str, Any]]) -> str:
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
Scene/backdrop: {chapter['chapter_title']}; use only the locations, weather, fictional adults, creatures, and objects named in the specifications.
Style/medium: mature clean graphic webcomic with restrained painterly color and selective premium cel finish; clear silhouettes, controlled density, expressive mature faces, readable hands, natural material wear, and phone-readable action.
Panel specifications:
{chr(10).join(lines)}
Stage-aware continuity: {stage_invariant(chapter_id, sequence['sequence_id'])}
Character/gear invariants: SOREN is a clearly fictional adult with a weathered angular face, light stubble, and short-to-medium swept-back light-brown to dark-blond wavy hair—never black or bright blond. His movement-limited left lower leg keeps a padded rigid quarry brace; no spontaneous healing, running, jumping, or easy stairs. His work-derived armor retains recognizable pale oatmeal quilted-coat ancestry beneath practical removable guards. Warden's Reach is one simple long wooden polehook with a forged socket and pruning hook—never a gun, firearm, crossbow, spear-gun, or complex machine. SIGRID is a clearly fictional adult with an athletic mature build, angular face, dark brows, and dark-brown to near-black hair in a compact low bun or practical braid—never blond or loose red curls. Her practical armor retains recognizable dark blue-brown plaid ancestry over gray-green layers and removable guards. Her owned compact recurved bow remains a simple bow and her utility seax remains a short practical single-edged knife. TAMSIN_REEVE, if present, is a clearly fictional mature adult courier-cartographer with medium chestnut-brown hair in one practical braid, visibly distinct from Sigrid, practical non-sexualized field clothing, and a supported injured lower leg; never blond or black-haired. HALVOR_KEST, if present, is a clearly fictional mature adult marshal with dark iron-brown close-cropped hair, gray temples, and a short matching beard—never blond, clean-shaven, or Soren-like. Every BRIAR_COMPACT_WORKER is a clearly fictional mature adult in practical work protection; no minors or anonymous crowd duplication. Never substitute one named role for another.
Creature invariants: CROWNROOT is an enormous non-human botanical and architectural root-cistern guardian integrated with old irrigation, brass, glasshouse, and keeper mechanisms—never a human figure, human corpse, exposed body, humanoid monster, gore creature, tentacle spectacle, or generic tree giant. Adult-scale tools, harnesses, hand-shaped recesses, impressions, and tokens are historical evidence only, never human remains. A HOLLOW STAG is a full-grown non-human ecological guardian with grounded wood, bark, hollow antler, and quadrupedal deer-like geometry—never a human hybrid or juvenile animal. A MIREBACK is a full-grown quadrupedal peat-root-and-slate creature with grounded mass and a visible root knot—never humanoid, dragon, glowing demon, gore creature, or generic dinosaur.
Story invariants: the Garden Ledger appears only as restrained frost-green light, traces, or nonverbal emblems attached to real brass, iron, stone, water, glass, condensation, map, socket, tool, or route surfaces. Render no readable Ledger words; planned dialogue, rule, class, bond, and status copy will be lettered locally. Preserve injury, route, map, key, fused-tool, garment-damage, irrigation, glasshouse, gate, and Crownroot state across panels.
Lettering composition: reserve the quiet regions declared by the ComicPanelPlans, but render no letters, captions, speech balloons, status prose, sound effects, panel numbers, logos, signatures, or watermark. Never cover faces, adult bodies, important hands, bow, seax, Warden's Reach, brace, map, key, fused socket, route flags, wire, glass, water, keeper mechanisms, creature root knots, or story evidence.
Motion: render literal braced foot placement, leverage, root pressure, pipe pressure, counterweight travel, water force, glass or soil shift, rope and wire tension, cloth cutting, flag timing, injury response, and weight transfer only where named. Do not substitute generic speed-line texture or unexplained energy spectacle.
Constraints: adult-only fictional cast; no child; no child-coded person; no youth; no real-person likeness; no celebrity likeness; no biometric identity data; no sexualization or fetish styling; no modern objects, extra people, duplicated people, swapped roles, changed hair colors, changed signature garment ancestry, premature or reset garment damage, premature or reversed key fusion, unexplained weapons, guns, extra monsters, gore, readable text, logo, or watermark."""


def decision(chapter_id: str, document: dict[str, Any]) -> dict[str, Any]:
    slug = "map-lied" if chapter_id == "CH12" else "north-garden"
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
            "stage_aware_garments": "CH12_P024_SOREN_SHOULDER_SACRIFICE_CH12_P028_SIGRID_PLAID_FLAGS_NO_RESET",
            "stage_aware_key": "CH12_P039_BRASS_KEY_FUSES_INTO_WARDENS_REACH_NO_EARLY_FUSION_OR_REVERSAL",
            "tamsin_hair": "medium_chestnut_brown_single_practical_braid_never_blond_or_black",
            "halvor_identity": "dark_iron_brown_close_crop_gray_temples_short_beard_never_blond_or_soren_like",
            "soren_injury": "padded_rigid_left_lower_leg_brace_persistent_no_spontaneous_healing",
            "crownroot": "nonhuman_botanical_architectural_root_cistern_guardian_no_human_remains_or_gore",
            "ledger_words": "WITHHELD_FROM_GENERATED_PIXELS_FOR_LOCAL_LETTERING",
            "status": "PROVISIONAL_TEXT_PROMPT_ANCHORS_NOT_CANON_ACCEPTANCE",
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
        "adr": "ADR-0212",
    }


def preflight_markdown(reference_uses: int) -> str:
    return "\n".join([
        "# CH12–CH13 default house-route preflight r1",
        "",
        "Sixteen chronological built-in ImageGen sequence requests cover all 80 CH12–CH13 ComicPanelPlans exactly once.",
        "",
        f"- Authorized reference uses: {reference_uses} across only three previously authorized fictional-adult hashes.",
        "- One left-to-right five-panel row per request; one panel candidate per plan; no wholesale alternate style arms.",
        "- Sequence-specific invariants prevent premature or reset coat/plaid damage and premature or reversed brass-key fusion.",
        "- Soren's fixed hair and persistent brace, Sigrid's fixed dark tied-back hair, Tamsin's chestnut braid, and Halvor's dark gray-templed bearded identity are explicit.",
        "- Crownroot is constrained to non-human botanical/architectural cistern geometry; historical adult tools and recesses are not remains.",
        "- Hollow Stag and Mireback are full-grown grounded non-human creatures; no juvenile, humanoid, gore, or generic-monster substitution.",
        "- Seven rule/dialogue/class/bond/status treatments are withheld from generated pixels for deterministic local lettering or nonverbal physical emblems.",
        "- New outputs remain ineligible for re-upload; provider calls, outputs, and paid API/cloud spend remain zero at preflight.",
        "",
        "This preflight changes no provider, upload class, license conclusion, acceptance, commercial clearance, or exact-production-base status.",
        "",
    ])


def adr_markdown(reference_uses: int) -> str:
    return "\n".join([
        "# ADR-0212: Promote CH12–CH13 with stage-aware rupture and Crownroot controls",
        "",
        "## Status",
        "",
        "Accepted for exact built-in ImageGen prompt preflight and chronological execution only.",
        "",
        "## Context",
        "",
        "ADR-0204 authorized provisional ComicPanelPlan/canon authoring but no prompt or render work. The owner's later authorization permits continued built-in ImageGen chapter production. CH12–CH13 contain irreversible garment damage, a mid-sequence key fusion, a transformed-keeper reveal, and progression copy that require narrower controls than CH10–CH11.",
        "",
        "## Decision",
        "",
        "1. Compile one default route of sixteen five-panel requests covering all 80 CH12–CH13 ComicPanelPlans exactly once.",
        "2. Use only the OpenAI built-in ImageGen product and the same three owner-authorized fictional-adult reference hashes.",
        "3. Apply sequence-specific state so Soren's shoulder sacrifice begins at CH12 P024, Sigrid's plaid flags begin at P028, and brass-key fusion begins at P039; forbid previews and resets.",
        "4. Define Crownroot as a non-human botanical/architectural root-cistern guardian and all historical keeper objects as adult-scale evidence without bodies, remains, or gore.",
        "5. Lock adult hair, injury, garment ancestry, fused-tool geometry, Halvor identity, Hollow Stag maturity, and Mireback anatomy in text because generated outputs cannot be re-uploaded.",
        "6. Withhold planned dialogue, rules, class, bond, and status wording from generated pixels and retain it for local lettering; use nonverbal physical-surface emblems where needed.",
        "7. Preserve one candidate per panel, zero whole-chapter alternate arms, and at most two narrow attempts per exact failed panel.",
        "",
        "## Evidence",
        "",
        f"Sixteen requests cover 80 unique plans with {reference_uses} uses of only the three authorized hashes. Plan continuity already passes 58/58 authoring mutations. Prompt, plan, reference, stage-transition, safety, anti-duplication, execution-null, and promotion bindings are validated before execution. Provider calls, outputs, uploads, and paid API/cloud spend are zero at preflight.",
        "",
        "## Consequences",
        "",
        "CH12 is ready for chronological built-in execution after validator passage, followed by CH13 without resetting state. Crownroot and secondary-character appearance remain text-defined stochastic limitations. Model, endpoint, request ID, usage, cost, seed, reproducibility, acceptance, rights, commercial clearance, and exact-base status remain unavailable, false, or pending. New outputs remain ineligible for re-upload.",
        "",
    ])


def build_outputs() -> tuple[dict[str, dict[str, Any]], dict[str, Any], str, str]:
    documents = {chapter_id: json.loads(path.read_text(encoding="utf-8")) for chapter_id, path in PLANS.items()}
    decisions = {chapter_id: decision(chapter_id, documents[chapter_id]) for chapter_id in PLANS}
    requests = []
    for chapter_id, document in documents.items():
        by_id = {panel["panel_id"]: panel for panel in document["plans"]}
        for sequence in document["sequences"]:
            panels = [by_id[panel_id] for panel_id in sequence["panel_ids"]]
            prompt = sequence_prompt(chapter_id, document, sequence, panels)
            reference_rows = REFERENCES if uses_mechanics_reference(panels) else REFERENCES[:2]
            requests.append({
                "request_id": sequence["sequence_id"],
                "chapter": chapter_id,
                "sequence_id": sequence["sequence_id"],
                "panel_ids": sequence["panel_ids"],
                "prompt": prompt,
                "prompt_sha256": text_sha256(prompt),
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
            })
    reference_uses = sum(request["reference_count"] for request in requests)
    manifest = {
        "record_type": "MultiChapterBuiltInImageGenPromptManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch12-ch13-default-house-route-prompt-manifest-r1",
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
            {
                "path": DECISIONS[chapter_id].relative_to(ROOT).as_posix(),
                "sha256": text_sha256(json_text(decisions[chapter_id])),
            }
            for chapter_id in PLANS
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
            "reference_uses": reference_uses,
            "provider_calls": 0,
            "outputs": 0,
            "paid_api_spend_usd": 0,
        },
        "limitations": [
            "CH12 garment damage and key fusion are sequence-timed text controls; five-panel generation may still preview, omit, or reset a state transition.",
            "Crownroot, its transformed-keeper history, the Hollow Stag, and late secondary-character identities are text-defined because new outputs cannot be re-uploaded as continuity references.",
            "Planned dialogue, negotiated rules, class names, bond words, and status copy are replaced by nonverbal physical emblems or withheld for local lettering.",
            "Built-in model, endpoint, provider request ID, usage, monetary cost, and deterministic seed remain unavailable unless exposed at execution.",
            "Five-panel generation is stochastic; output layout, chronology, anatomy, role binding, and story order require deterministic local validation and human review.",
        ],
    }
    return decisions, manifest, preflight_markdown(reference_uses), adr_markdown(reference_uses)


def main() -> int:
    decisions, manifest, markdown, adr = build_outputs()
    for chapter_id, path in DECISIONS.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json_text(decisions[chapter_id]), encoding="utf-8", newline="\n")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json_text(manifest), encoding="utf-8", newline="\n")
    MARKDOWN.write_text(markdown, encoding="utf-8", newline="\n")
    ADR.write_text(adr, encoding="utf-8", newline="\n")
    print(json.dumps({
        "requests": len(manifest["requests"]),
        "panels": manifest["summary"]["panel_plans"],
        "reference_uses": manifest["summary"]["reference_uses"],
        "sha256": sha256(OUTPUT),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
