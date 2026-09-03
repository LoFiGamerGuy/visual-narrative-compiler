"""Compile the one-route CH06-CH07 built-in ImageGen prompt manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PLANS = {
    "CH06": ROOT / "production/comic/ch06-sc01-panel-plans-r1.json",
    "CH07": ROOT / "production/comic/ch07-sc01-panel-plans-r1.json",
}
DECISIONS = {
    "CH06": ROOT / "production/decisions/ng-decision-ch06-house-answered-prompt-promotion-r1.json",
    "CH07": ROOT / "production/decisions/ng-decision-ch07-mireback-gate-prompt-promotion-r1.json",
}
OUTPUT = ROOT / "production/comic/run-manifests/ch06-ch07-default-house-route-prompt-manifest-r1.json"
MARKDOWN = ROOT / "docs/research/ch06-ch07-default-house-route-preflight-r1.md"


REFERENCES = [
    {
        "path": "experiments/review-packets/ch05-style-density-scale-exploration-r1/P050-wide-action-clean-graphic-r1.png",
        "sha256": "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d",
        "role": "Image 1: fictional-adult Soren/Sigrid wardrobe, paired silhouette, restrained action, and clean graphic-painterly direction",
    },
    {
        "path": "experiments/review-packets/ch05-style-density-scale-exploration-r1/P040-medium-close-cel-painted-r1.png",
        "sha256": "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a",
        "role": "Image 2: fictional-adult Sigrid dark tied-back hair, plaid-wrap identity, face maturity, and restrained cel-painted finish",
    },
    {
        "path": "experiments/review-packets/ch05-style-density-scale-exploration-r1/P036-tall-lever-clear-line-corrected-r1.png",
        "sha256": "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb",
        "role": "Image 3: composition-only reference for readable two-adult leverage and grounded force paths; not hair identity authority",
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sequence_prompt(chapter: dict[str, Any], sequence: dict[str, Any], panels: list[dict[str, Any]]) -> str:
    panel_lines = []
    for order, panel in enumerate(panels, start=1):
        cast = ", ".join(panel["visible_adult_cast"]) or "NO PEOPLE"
        panel_lines.append(
            f"Panel {order} ({panel['panel_id']}; {panel['scale_role']}; {panel['density_class']}): "
            f"{panel['narrative_beat']} Composition: {panel['composition_intent']} Visible cast: {cast}."
        )
    uses_leverage = any(
        token in " ".join(panel["narrative_beat"].lower() for panel in panels)
        for token in ("lever", "weight", "gatepost", "polehook", "counterweight")
    )
    reference_lines = [reference["role"] for reference in REFERENCES[:2]]
    if uses_leverage:
        reference_lines.append(REFERENCES[2]["role"])
    references = "\n".join(reference_lines)
    beats = "\n".join(panel_lines)
    return f"""Use case: illustration-story
Asset type: North Garden {chapter['chapter_title']} five-panel chronological webcomic sequence strip
Primary request: Render exactly five clearly separated panels in the numbered order below as one coherent story sequence. Preserve causal state and object positions from panel to panel.
Input images:
{references}
Scene/backdrop: {chapter['chapter_title']}; use only the locations, weather, people, creature, and objects named in the five panel specifications.
Style/medium: mature clean graphic webcomic with restrained painterly color and selective premium cel finish; natural fabric wear, wet stone, mud, timber, peat, root, slate, and practical tools; polished but phone-readable.
Composition/framing: one horizontal five-panel strip with clean light gutters; vary panel width according to the declared scale role; strong silhouettes, explicit geography, expressive mature faces, and literal hand/tool/terrain contact.
Panel specifications:
{beats}
Character invariants: SOREN is a clearly fictional adult with mature proportions, weathered angular face, light stubble where visible, light-brown to dark-blond short-to-medium wavy hair swept back—never black or bright blond—and a pale oatmeal work coat in the exact carried condition. SIGRID is a clearly fictional adult with mature proportions, athletic build, angular face, dark brows, dark-brown to near-black hair in a compact low bun or practical braid—never blond or loose red curls—and a dark blue-brown plaid wrap in the exact carried condition. TAMSIN_REEVE, if present, is a clearly fictional adult courier-cartographer in practical non-sexualized field clothing with a wrapped injured lower leg; she must remain visually distinct from Sigrid.
Story invariants: the Garden Ledger appears only as restrained frost-green inscription on real brass, stone, water, glass, map, or tool surfaces; never as a floating game HUD. Mireback, if present, is a heavy peat-root-slate creature with readable mass, joints, vulnerable root-knot, and terrain interaction—not a generic dragon, humanoid, or glowing demon.
Lettering composition: reserve quiet upper-left or upper-right regions matching the panel plans, but render no letters, captions, balloons, sound effects, symbols pretending to be prose, logos, signatures, or watermark. Never place visual clutter over faces, adult bodies, important hands, weapons, tools, the brass key, maps, twine, the boundary wheel, the root-knot, or other story objects.
Motion: show causal weight shift, leverage, mud displacement, water flow, cloth pull, branch drag, projectile impact, and object vibration only where named. Do not substitute generic speed-line texture.
Constraints: adult-only fictional cast; no child; no child-coded person; no youth; no real-person likeness; no celebrity likeness; no biometric identity data; no sexualization or fetish styling; no modern objects, extra people, duplicated people, swapped roles, changed hair colors, changed signature garments, unexplained weapons, extra monsters, gore, text, logo, or watermark."""


def decision(chapter_id: str, document: dict[str, Any]) -> dict[str, Any]:
    slug = "house-answered" if chapter_id == "CH06" else "mireback-gate"
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
        "adr": "ADR-0197",
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
            prompt = sequence_prompt(document, sequence, panels)
            panel_beats = " ".join(panel["narrative_beat"].lower() for panel in panels)
            uses_leverage = any(
                token in panel_beats for token in ("lever", "weight", "gatepost", "polehook", "counterweight")
            )
            reference_rows = REFERENCES if uses_leverage else REFERENCES[:2]
            request_id = sequence["sequence_id"]
            requests.append(
                {
                    "request_id": request_id,
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
        "record_id": "ng-ch06-ch07-default-house-route-prompt-manifest-r1",
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
            "Built-in model, endpoint, provider request ID, usage, monetary cost, and deterministic seed are unavailable unless exposed at execution.",
            "Five-panel strips are stochastic and require deterministic local gutter/crop validation before they count as panel candidates.",
            "Tamsin and Mireback have no image reference; their first appearance is text-defined and may require bounded continuity repair.",
            "No prompt result is accepted, commercially cleared, reproducible, or an exact production base by generation alone.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    MARKDOWN.write_text(
        "\n".join(
            [
                "# CH06–CH07 default house-route preflight r1",
                "",
                "One built-in ImageGen sequence request is planned for each of 16 chronological five-panel sequences, covering all 80 CH06–CH07 ComicPanelPlans exactly once.",
                "",
                f"- Reference uses: {manifest['summary']['reference_uses']} across only three previously authorized hashes.",
                "- Default candidates: one per panel; whole-chapter alternate style arms: zero.",
                "- New outputs may not be re-uploaded as references.",
                "- Every exact prompt requires mature fictional adults, fixed Soren/Sigrid hair and signature garments, protected lettering regions, literal causal action, and no child/real-person/private/training material.",
                "- Model, endpoint, provider request ID, usage, monetary cost, and seed remain unavailable before execution.",
                "",
                "This preflight authorizes only the already approved OpenAI built-in ImageGen route and only after validator PASS. It does not authorize a direct paid API, BFL, another provider, a new upload class, acceptance, commercial clearance, or exact-base selection.",
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
