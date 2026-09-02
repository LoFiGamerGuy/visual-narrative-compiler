"""Compile metadata-only reference hypotheses and continuity risks for all 50 CH05 plans."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
READINESS = ROOT / "production/comic/run-manifests/ch05-chapter-production-readiness-matrix-r1.json"
PROFILE = ROOT / "production/comic/continuity/ch05-fictional-adult-visual-profile-r1.json"
ASSERTIONS = ROOT / "production/comic/continuity/ch05-character-assertion-manifest-r1.json"
OUTPUT = ROOT / "production/comic/continuity/ch05-reference-use-and-continuity-risk-plan-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-reference-use-and-continuity-risk-plan-r1.json"
CHART = ROOT / "experiments/review-packets/ch05-reference-use-continuity-risk-r1/ch05-reference-risk-map-r1.png"

CATALOG = {
    "p050_dual_identity_action": {"sha256": "cb1e7b496397ff0f37c07c241b7a4b5beec137d3d26c48c3cbfad60734b8c83d", "identity_authority": "SOREN_AND_SIGRID", "boundary": "dual hair, wardrobe, silhouette, and blocking anchor"},
    "p040_sigrid_face": {"sha256": "c0a2be11cc9a51ecfbb490d490135df88e7b575b794240b002b1427ba64b6b4a", "identity_authority": "SIGRID_ONLY", "boundary": "Sigrid face, dark tied hair, plaid wrap, and cel-painted close anchor"},
    "p036_composition_only": {"sha256": "50f6413eeab39f35da00524a79c6e71d821f6b84da939487575324c4ad7743eb", "identity_authority": "NONE", "boundary": "composition only; swapped hair colors are non-authoritative"},
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def hypotheses(row: dict) -> list[str]:
    cast = row["visible_adult_cast"]
    if not cast:
        result = []
    elif cast == ["SIGRID"]:
        result = ["p040_sigrid_face"]
    elif cast == ["SOREN"]:
        result = ["p050_dual_identity_action"]
    else:
        result = ["p050_dual_identity_action"]
        if row["scale_role"] in {"MEDIUM_TWO_SHOT", "MEDIUM_SENSORY_REACTION", "TALL_OR_WIDE_DUAL_CAUSAL"}:
            result.append("p040_sigrid_face")
    if row["panel_id"] == "ng-ch05-sc01-p036":
        result.append("p036_composition_only")
    return result


def risk(row: dict, refs: list[str]) -> tuple[str, list[str]]:
    cast = row["visible_adult_cast"]
    flags = []
    if row["panel_id"] == "ng-ch05-sc01-p036":
        flags.extend(["P036_SWAPPED_HAIR_COMPOSITION_REFERENCE", "DUAL_CAUSAL_HAND_OBJECT_GEOMETRY", "ROLE_ORDER_LITERALIZATION"])
        return "CRITICAL_GUARDED", flags
    if cast == ["SOREN"]:
        flags.extend(["DUAL_REFERENCE_MAY_ADD_SIGRID", "SOREN_HAIR_COLOR", "OATMEAL_COAT", "SINGLE_CAST_ENFORCEMENT"])
        return "HIGH", flags
    if len(cast) == 2 and row["scale_role"] in {"WIDE_DIRECTIONAL_ANCHOR", "TALL_OR_WIDE_DUAL_CAUSAL", "MEDIUM_TWO_SHOT"}:
        flags.extend(["ROLE_ORDER_LITERALIZATION", "HAIR_COLOR_SEPARATION", "WARDROBE_SEPARATION", "EXTRA_PERSON_PROHIBITION"])
        return "HIGH", flags
    if cast == ["SIGRID"]:
        flags.extend(["SIGRID_DARK_TIED_HAIR", "PLAID_WRAP", "SINGLE_CAST_ENFORCEMENT"])
        return "MEDIUM", flags
    if len(cast) == 2:
        flags.extend(["HAIR_COLOR_SEPARATION", "WARDROBE_SEPARATION", "ROLE_ORDER_LITERALIZATION"])
        return "MEDIUM", flags
    flags.extend(["NO_PERSON_ENFORCEMENT", "SINGLE_STORY_OBJECT", "NO_REFERENCE_LEAKAGE"])
    return "LOW", flags


def build_chart(rows: list[dict]) -> None:
    CHART.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1600, 1900), "#10151c")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((38, 24), "CH05 · reference-use and continuity risk r1", fill="#eef3f8", font=font)
    draw.text((38, 45), "Metadata hypotheses only · zero uploads · no identity inference", fill="#ffcf88", font=font)
    colors = {"LOW": "#3d7654", "MEDIUM": "#776f35", "HIGH": "#9a5f31", "CRITICAL_GUARDED": "#8b3e56"}
    x = 38
    for label in ("LOW", "MEDIUM", "HIGH", "CRITICAL_GUARDED"):
        draw.rectangle((x, 68, x + 18, 86), fill=colors[label])
        draw.text((x + 24, 70), label.replace("_", " "), fill="#dce4ec", font=font)
        x += 205
    cell_w, cell_h, gap = 286, 164, 10
    for index, row in enumerate(rows):
        column, line = index % 5, index // 5
        left, top = 38 + column * (cell_w + gap), 110 + line * (cell_h + gap)
        draw.rounded_rectangle((left, top, left + cell_w, top + cell_h), radius=8, fill=colors[row["continuity_risk"]], outline="#8593a3", width=1)
        plan = row["panel_id"].split("-")[-1].upper()
        draw.text((left + 10, top + 8), f"{plan} · {row['continuity_risk'].replace('_', ' ')}", fill="white", font=font)
        draw.text((left + 10, top + 32), f"cast {','.join(row['visible_adult_cast']) or 'NONE'}", fill="#e7edf3", font=font)
        draw.text((left + 10, top + 54), f"refs {len(row['reference_hypotheses'])}: {','.join(row['reference_hypotheses']) or 'text-only'}"[:43], fill="#d2dbe4", font=font)
        draw.text((left + 10, top + 76), row["risk_flags"][0].replace("_", " ")[:39], fill="#ffe0a8", font=font)
        draw.text((left + 10, top + 98), f"checks {len(row['required_manual_checks'])} · uploads 0", fill="#d2dbe4", font=font)
        draw.text((left + 10, top + 120), "prompt null · identity inference 0", fill="#d2dbe4", font=font)
    image.save(CHART, optimize=False)


def main() -> int:
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    assertions = {row["panel_id"]: row for row in json.loads(ASSERTIONS.read_text(encoding="utf-8"))["plans"]}
    rows = []
    for source in readiness["rows"]:
        refs = hypotheses(source)
        level, flags = risk(source, refs)
        checks = ["visible cast count", "hair color and style", "canonical wardrobe", "mature adult anatomy", "role staging", "hands and story object", "lettering/content clearance", "phone silhouette"] if source["visible_adult_cast"] else ["no person", "single story object", "causal direction", "phone readability", "reference leakage absent"]
        rows.append({"display_order": source["display_order"], "panel_id": source["panel_id"], "plan_revision_id": source["plan_revision_id"], "visible_adult_cast": source["visible_adult_cast"], "role_assertion_count": len(assertions[source["panel_id"]]["role_assertions"]), "scale_role": source["scale_role"], "reference_hypotheses": refs, "reference_uploads": 0, "next_prompt": None, "continuity_risk": level, "risk_flags": flags, "required_manual_checks": checks, "automated_identity_inference": False, "owner_accepted": False, "execution_ready": False})
    build_chart(rows)
    risk_counts = {level: sum(row["continuity_risk"] == level for row in rows) for level in ("LOW", "MEDIUM", "HIGH", "CRITICAL_GUARDED")}
    ref_counts = {ref: sum(ref in row["reference_hypotheses"] for row in rows) for ref in CATALOG}
    text_only = sum(not row["reference_hypotheses"] for row in rows)
    total_uses = sum(len(row["reference_hypotheses"]) for row in rows)
    record = {"record_type": "ComicReferenceUseAndContinuityRiskPlan", "schema_version": "1.0", "record_id": "ng-ch05-reference-use-and-continuity-risk-plan-r1", "state": "METADATA_HYPOTHESES_ZERO_UPLOAD_OWNER_PENDING", "medium": "comic", "inputs": [binding(path) for path in (READINESS, PROFILE, ASSERTIONS)], "authorized_reference_catalog": CATALOG, "summary": {"plan_count": 50, "text_only_plans": text_only, "reference_hypothesis_uses": total_uses, "p050_hypotheses": ref_counts["p050_dual_identity_action"], "p040_hypotheses": ref_counts["p040_sigrid_face"], "p036_composition_hypotheses": ref_counts["p036_composition_only"], "low_risk": risk_counts["LOW"], "medium_risk": risk_counts["MEDIUM"], "high_risk": risk_counts["HIGH"], "critical_guarded": risk_counts["CRITICAL_GUARDED"], "reference_uploads": 0, "automated_identity_inferences": 0, "next_prompt_count": 0, "owner_accepted": 0, "execution_ready": 0, "provider_calls": 0, "cost_usd": 0, "human_review_minutes": None}, "rows": rows, "chart": {"path": CHART.relative_to(ROOT).as_posix(), "sha256": sha(CHART), "dimensions": [1600, 1900]}, "comic_panel_plan_revision_created": False, "animation_shot_plan": None, "e_conte": None, "boundary": "Reference-use hypotheses only. No upload, prompt, identity inference, acceptance, execution, or plan revision."}
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    evidence = {"record_type": "ComicReferenceUseAndContinuityRiskPlanEvidence", "schema_version": "1.0", "record_id": "ng-ch05-reference-use-and-continuity-risk-plan-evidence-r1", "state": "PASS_ZERO_UPLOAD", "plan": binding(OUTPUT), "inputs": record["inputs"], "summary": record["summary"], "chart": record["chart"], "animation_shot_plan": None, "e_conte": None}
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"CH05 reference risk: 50 plans/{total_uses} hypotheses/{text_only} text-only; LOW {risk_counts['LOW']} MEDIUM {risk_counts['MEDIUM']} HIGH {risk_counts['HIGH']} GUARDED {risk_counts['CRITICAL_GUARDED']}")
    print("uploads/identity inference/prompts/accepted/executable/calls/cost 0/0/0/0/0/0/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
