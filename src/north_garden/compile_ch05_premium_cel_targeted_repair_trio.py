"""Compile the generation-disabled CH05 P001/P032/P039 targeted-repair manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
GATES = ROOT / "production/comic/contracts/ch05-cross-panel-semantic-gates-r1.json"
PROFILE = ROOT / "production/comic/continuity/ch05-fictional-adult-visual-profile-r1.json"
PREMIUM_ARM = ROOT / "production/comic/run-manifests/ch05-complete-chapter-premium-cel-prompt-manifest-r1.json"
OUTPUT = ROOT / "production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-r1.json"

REFERENCE_IDS = ("p050_dual_identity_action", "p040_sigrid_face")
TARGETS: dict[int, dict[str, Any]] = {
    1: {
        "prompt_revision_id": "ng-ch05-p001-premium-cel-clean-graphic-repair-prompt-r1",
        "gate_ids": ["cold_farmhouse_until_reversal", "departure_vector"],
        "format_role": "wide_directional_departure_anchor",
        "planned_dimensions": {"width_px": 1536, "height_px": 1024},
        "lettering_safe_zone": "upper left",
        "exact_repair_contract": [
            "Unmistakable left-to-right downhill-away travel vector.",
            "The cold, dark farmhouse is physically behind both adults and upslope, never ahead of them.",
            "Both adults' backs, gazes, torsos, and leading feet point downhill away from the farmhouse.",
            "Farmhouse chimney and windows show no smoke, glow, firelight, or lit panes.",
            "Sigrid leads by one grounded stride and Soren follows without reversing role order.",
        ],
        "panel_direction": (
            "Wide single panel at damp dawn. Place the farmhouse high in the rear-left background and the descending trail moving "
            "clearly toward the lower-right foreground. Sigrid is one stride ahead, Soren follows. Show their backs or three-quarter "
            "backs, downhill gazes, forward weight shifts, downhill-leading feet, damp coat and wrap movement, and grounded footfalls. "
            "The house must read as the place they have left, not their destination. Keep the upper-left lettering field quiet without "
            "hiding the cold chimney, either adult, face silhouette, or travel vector."
        ),
        "negative_constraints": (
            "No uphill walking, no walking toward or facing the farmhouse, no farmhouse ahead, no frontal arrival pose, no chimney "
            "smoke, no vapor resembling smoke, no glow, no lit window, no firelight, no sunrise flare behind the chimney."
        ),
    },
    32: {
        "prompt_revision_id": "ng-ch05-p032-premium-cel-clean-graphic-repair-prompt-r1",
        "gate_ids": ["impossible_far_bank_prints"],
        "format_role": "deep-perspective-causal-clue",
        "planned_dimensions": {"width_px": 1024, "height_px": 1536},
        "lettering_safe_zone": "upper right",
        "exact_repair_contract": [
            "Soren stands on the near bank and does not cross the water.",
            "No footprints or footprint-like marks appear on the near bank, in the water, or on stepping stones.",
            "Oversized, readable footprints begin only on dry ground beyond the far water edge.",
            "Every far-bank print has an asymmetric heel and toe shape pointing back toward Soren and camera.",
            "Water gap and bank separation remain readable at phone width without labels or arrows.",
        ],
        "panel_direction": (
            "Single tall deep-perspective panel from just behind Soren on the near bank. His oatmeal shoulder and light-brown hair frame "
            "the near foreground without covering the clue. A clear uninterrupted creek separates him from the far dry bank. On that "
            "far dry ground only, render a short row of deliberately oversized asymmetric boot impressions: broad toe shapes visibly "
            "nearest the camera/Soren side of each print and narrower heels farther away, so the prints face back toward Soren/camera. "
            "Use broad simple shapes and strong value separation. Keep the upper-right lettering field quiet and clear of Soren and prints."
        ),
        "negative_constraints": (
            "No near-bank prints, no prints in water, no stepping-stone prints, no symmetrical ovals, no tiny unreadable marks, no tracks "
            "pointing away from Soren, no second person, no Sigrid, no arrows, labels, captions, or diagram notation."
        ),
    },
    39: {
        "prompt_revision_id": "ng-ch05-p039-premium-cel-clean-graphic-repair-prompt-r1",
        "gate_ids": ["third_upstream_mark"],
        "format_role": "sparse-map-deduction-insert",
        "planned_dimensions": {"width_px": 1024, "height_px": 1536},
        "lettering_safe_zone": "upper left",
        "exact_repair_contract": [
            "One uninterrupted map view simultaneously shows exactly one square farmhouse symbol, one circle mill symbol, and one distinct third upstream mark at the torn edge.",
            "All three marks remain individually readable at phone width and are not split across panels or paper fragments.",
            "The creek line visibly links the spatial reading while the third mark continues upstream beyond the torn edge.",
            "Soren's oatmeal-sleeved adult finger points precisely at the third mark, not the square or circle.",
            "No written labels, legend, numbers, arrows, or extra symbol-like clutter compete with the three marks.",
        ],
        "panel_direction": (
            "Single sparse top-down map close-up, not a collage and not multiple panels. In one uninterrupted paper surface show the creek "
            "line, one small square farmhouse symbol, one circle mill symbol, and a clearly different third upstream mark placed at the "
            "torn paper edge. All three symbols must be visible simultaneously with generous blank separation. Soren's mature hand enters "
            "from the lower-right in an oatmeal sleeve and his fingertip stops exactly on the third torn-edge mark. A restrained partial "
            "Soren profile may appear only if it does not reduce map clarity. Keep the upper-left lettering field quiet without covering "
            "the map or any mark."
        ),
        "negative_constraints": (
            "No separate paper fragment, no cropped-off symbol, no sequential inset, no hidden square or circle, no fourth mark, no finger "
            "on the farmhouse or mill, no written words, labels, legend, compass letters, numbers, arrows, or decorative rune clutter."
        ),
    },
}

STYLE = (
    "Premium cel-painted / clean graphic hybrid fantasy-adventure webcomic: broad clean shapes, bold controlled contours, shaped "
    "two-tier cel shadows, restrained painterly atmosphere, low microtexture, strong silhouettes, explicit causal geometry, and "
    "phone-width clarity. Keep the image illustrative rather than photorealistic; avoid decorative hatching and density that competes "
    "with the target clue."
)
SAFETY = (
    "Fictional mature adults only with mature proportions and practical non-sexualized clothing. Soren has short-to-medium wavy "
    "light-brown/dark-blond swept-back hair, never black, and a pale oatmeal work coat over muted blue-gray layers. Sigrid, if visible, "
    "has dark-brown/near-black tied-back hair, never blond, and a dark blue-brown plaid wrap over gray-green layers. No child-coded "
    "features, real-person likeness, sexualization, extra people, monsters, armor, magic, or undeclared weapons."
)
TEXT = "No text: no balloons, captions, words, letters, labels, sound effects, panel numbers, logos, signatures, or watermark."


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    plan_doc = json.loads(PLANS.read_text(encoding="utf-8"))
    gate_doc = json.loads(GATES.read_text(encoding="utf-8"))
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    plan_by_order = {row["display_order"]: row for row in plan_doc["plans"]}
    gate_by_id = {row["gate_id"]: row for row in gate_doc["gates"]}
    reference_by_id = {row["reference_id"]: row for row in profile["authorized_references"]}

    references = []
    for reference_id in REFERENCE_IDS:
        reference = reference_by_id[reference_id]
        path = ROOT / reference["path"]
        if not path.is_file() or sha256(path) != reference["sha256"]:
            raise ValueError(f"authorized reference hash mismatch: {reference_id}")
        references.append(reference)

    requests = []
    for order, target in TARGETS.items():
        plan = plan_by_order[order]
        gate_bindings = []
        for gate_id in target["gate_ids"]:
            gate = gate_by_id[gate_id]
            required_phrase = gate["required_prompt_phrases"].get(plan["panel_id"])
            if required_phrase is None:
                raise ValueError(f"gate {gate_id} does not bind {plan['panel_id']}")
            gate_bindings.append(
                {"gate_id": gate_id, "panel_id": plan["panel_id"], "required_prompt_phrase": required_phrase}
            )

        prompt_lines = [
            "Use case: illustration-story",
            f"Asset type: North Garden CH05 targeted repair, exact ComicPanelPlan P{order:03d}, one standalone panel",
            (
                "Input images: Image 1 is the exact authorized fictional-adult P050 dual-character identity, hair, wardrobe, silhouette, "
                "and clean-graphic action reference. Image 2 is the exact authorized fictional-adult P040 Sigrid face, dark-hair, plaid-wrap, "
                "and premium-cel finish reference. Use them only for fictional identity/wardrobe/style continuity; obey this request's exact "
                "cast and do not add a referenced person who is absent from the ComicPanelPlan."
            ),
            f"ComicPanelPlan beat: {plan['narrative_beat']}",
            f"Exact panel direction: {target['panel_direction']}",
            "Exact repair requirements: " + " ".join(target["exact_repair_contract"]),
            "Negative constraints: " + target["negative_constraints"],
            STYLE,
            SAFETY,
            TEXT,
            "Cross-panel semantic gates (literal visual requirements): "
            + "; ".join(row["required_prompt_phrase"] for row in gate_bindings)
            + ".",
            (
                f"Output: exactly one standalone P{order:03d} panel, no gutters, no contact sheet, no alternate, composed for "
                f"{target['planned_dimensions']['width_px']}x{target['planned_dimensions']['height_px']} delivery and readable at 390px phone width."
            ),
        ]
        prompt_text = "\n".join(prompt_lines)
        requests.append(
            {
                "request_id": f"ch05-premium-cel-repair-p{order:03d}-r1",
                "panel_id": plan["panel_id"],
                "display_order": order,
                "comic_panel_plan_revision_id": plan["plan_revision_id"],
                "comic_panel_plan_canonical_sha256": canonical_sha256(plan),
                "comic_panel_plan_revision_created": False,
                "prompt_revision_id": target["prompt_revision_id"],
                "narrative_beat": plan["narrative_beat"],
                "composition_intent": plan["composition_intent"],
                "visible_adult_cast": plan["visible_adult_cast"],
                "lettering_safe_zones": plan["comic_direction"]["lettering"]["safe_zones"],
                "format_role": target["format_role"],
                "planned_dimensions": target["planned_dimensions"],
                "phone_preview_width_px": 390,
                "input_references": [dict(row) for row in references],
                "reference_use_count": 2,
                "cross_panel_gate_bindings": gate_bindings,
                "exact_repair_contract": target["exact_repair_contract"],
                "prompt_lines": prompt_lines,
                "prompt_text": prompt_text,
                "prompt_sha256": hashlib.sha256(prompt_text.encode("utf-8")).hexdigest(),
                "planned_output": (
                    "experiments/review-packets/ch05-premium-cel-targeted-repair-trio-r1/source-panels/"
                    f"P{order:03d}-premium-cel-clean-graphic-hybrid-r1.png"
                ),
                "execution": None,
                "output": None,
                "render_record": None,
                "provider_model": None,
                "provider_endpoint": None,
                "provider_request_id": None,
                "provider_usage": None,
                "provider_cost_usd": None,
                "elapsed_seconds": None,
                "human_review_state": "PENDING_NOT_RENDERED",
                "human_review_minutes": None,
                "accepted": False,
                "commercially_cleared": False,
                "exact_production_base": False,
            }
        )

    document = {
        "record_type": "CH05PremiumCelTargetedRepairTrioPreflightManifest",
        "schema_version": "1.0",
        "record_id": "ng-ch05-premium-cel-targeted-repair-trio-r1",
        "state": "EXACT_PROMPTS_COMPILED_NOT_EXECUTED",
        "medium": "comic",
        "planning_structure": "ComicPanelPlan",
        "animation_shot_plan": None,
        "e_conte": None,
        "sources": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}
            for path in (PLANS, GATES, PROFILE, PREMIUM_ARM)
        ],
        "selection_context": (
            "Smallest targeted semantic-repair trio after the complete premium-cel arm. Each request changes only one failed or "
            "ambiguous panel and preserves the passing chapter sequence as non-target context."
        ),
        "style_hypothesis": (
            "A premium-cel/clean-graphic hybrid with broader shapes and lower clue-field density can retain character continuity while "
            "making departure direction, heel/toe orientation, and simultaneous map-mark count readable at phone width."
        ),
        "coverage": {
            "comic_panel_plans": 3,
            "panel_orders": [1, 32, 39],
            "standalone_requests": 3,
            "planned_outputs": 3,
            "outputs_per_request": 1,
            "references_per_request": 2,
            "planned_reference_uses": 6,
            "cross_panel_gates": 4,
            "gate_phrase_bindings": 4,
        },
        "authorized_reference_ids": list(REFERENCE_IDS),
        "authorized_reference_hashes": [row["sha256"] for row in references],
        "requests": requests,
        "request_root_sha256": canonical_sha256(requests),
        "execution_preflight": {
            "compiler_complete": True,
            "validator_required_before_generation": True,
            "generation_started": False,
            "current_reference_uploads": 0,
            "current_provider_calls": 0,
            "current_outputs": 0,
            "current_spend_usd": 0,
        },
        "boundary": {
            "permitted_product": "openai_builtin_imagegen",
            "permitted_upload_class": "two_exact_hash_pinned_project_generated_fictional_adult_references_only",
            "direct_paid_provider_api_calls": 0,
            "bfl_calls": 0,
            "gemini_calls": 0,
            "xai_calls": 0,
            "new_upload_classes": 0,
            "real_person_or_child_material": 0,
            "training_or_publication_authority": 0,
            "current_executions": 0,
            "current_outputs": 0,
            "accepted": 0,
            "commercially_cleared": 0,
            "exact_production_base": 0,
        },
        "limitations": [
            "This preflight contains prompts and planned outputs but no generated pixels or visual compliance result.",
            "Built-in product model, endpoint, request ID, seed, usage, and cost remain null until exposed by a later execution.",
            "Prompt constraints cannot guarantee geometry; each output requires exact gate and phone-width human review.",
            "No generated art is accepted, commercially cleared, or promoted as an exact production base by this manifest.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "output": OUTPUT.relative_to(ROOT).as_posix(),
                "sha256": sha256(OUTPUT),
                "requests": len(requests),
                "planned_outputs": len(requests),
                "reference_uses": sum(row["reference_use_count"] for row in requests),
                "gate_bindings": sum(len(row["cross_panel_gate_bindings"]) for row in requests),
                "provider_calls": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
