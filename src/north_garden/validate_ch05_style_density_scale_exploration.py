"""Validate owner direction, style r2, and the hash-pinned local exploration packet."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-style-density-scale-exploration-r1.json"
MANIFEST = ROOT / "docs/research/evidence/ch05-style-density-scale-review-packet-r1.json"
DECISION = ROOT / "production/decisions/ng-decision-owner-visual-direction-r2.json"
STYLE = ROOT / "production/comic/style-direction/ch05-mill-signal-r2.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"
PACKET = ROOT / "experiments/review-packets/ch05-style-density-scale-exploration-r1/review-packet.json"
HANDOFF_R1 = ROOT / "docs/research/evidence/review-authority-handoff-packet-r1.json"
HANDOFF_R2 = ROOT / "docs/research/evidence/review-authority-handoff-packet-r2.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def bundle_errors(bundle: dict, *, verify_files: bool) -> list[str]:
    evidence, manifest, decision, style, plans, packet, handoff = (bundle[key] for key in ("evidence", "manifest", "decision", "style", "plans", "packet", "handoff"))
    errors: list[str] = []
    plan_by_id = {item["panel_id"]: item for item in plans.get("plans", [])}
    candidates = evidence.get("candidates", [])
    if len(candidates) != 4 or len({item.get("candidate_id") for item in candidates}) != 4:
        errors.append("candidate inventory invalid")
    if evidence.get("execution", {}).get("input_images") != 0 or evidence.get("execution", {}).get("existing_art_uploaded") is not False:
        errors.append("text-only input boundary invalid")
    if evidence.get("execution", {}).get("adult_likeness_uploaded") is not False:
        errors.append("likeness upload boundary invalid")
    if any(evidence.get("execution", {}).get(key) is not None for key in ("model", "endpoint", "provider_request_id", "provider_usage", "provider_cost_usd")):
        errors.append("unexposed provider metadata fabricated")
    acceptance = evidence.get("acceptance", {})
    if any(acceptance.get(key) != 0 for key in ("human_reviewed_candidates", "accepted_exact_bases", "exact_repair_masks", "render_records")) or acceptance.get("production_authority") is not False:
        errors.append("candidate acceptance or authority fabricated")
    for candidate in candidates:
        plan = plan_by_id.get(candidate.get("panel_id"))
        if not plan or plan.get("plan_revision_id") != candidate.get("plan_revision_id"):
            errors.append(f"plan binding invalid: {candidate.get('candidate_id')}")
        elif plan.get("comic_direction", {}).get("lettering", {}).get("safe_zones", [{}])[0].get("anchor") != "top_right":
            errors.append(f"lettering binding invalid: {candidate.get('candidate_id')}")
        if verify_files:
            path = ROOT / candidate.get("path", "")
            if not path.is_file() or sha256(path) != candidate.get("sha256") or path.stat().st_size != candidate.get("bytes"):
                errors.append(f"candidate bytes invalid: {candidate.get('candidate_id')}")
            elif Image.open(path).size != (candidate.get("width"), candidate.get("height")):
                errors.append(f"candidate dimensions invalid: {candidate.get('candidate_id')}")
    if decision.get("approved_direction", {}).get("continue_significant_research_and_engineering") is not True:
        errors.append("owner continuation missing")
    boundary = decision.get("evidence_boundaries", {})
    if boundary.get("g07_formal_timed_decisions_complete") != 0 or boundary.get("g07_human_minutes") is not None or boundary.get("g07_deblinding_authorized") is not False:
        errors.append("formal G07 review fabricated")
    if any(boundary.get(key) is not None for key in ("exact_ch05_base_raster", "exact_ch05_repair_mask", "exact_external_input_package_authority", "distinct_ch05_production_cap_usd")):
        errors.append("exact CH05 authority fabricated")
    if style.get("medium") != "comic" or style.get("animation_shot_plan") is not None or style.get("e_conte") is not None:
        errors.append("medium boundary invalid")
    if style.get("current_exploration", {}).get("accepted_exact_bases") != 0:
        errors.append("style direction promotes exact base")
    if "No opaque lettering may cover a person or face" not in style.get("visual_language", {}).get("lettering_rule", ""):
        errors.append("owner lettering rule missing")
    if manifest.get("candidate_count") != 4 or manifest.get("human_reviewed_candidates") != 0 or manifest.get("accepted_exact_bases") != 0:
        errors.append("review manifest state invalid")
    if packet.get("state") != "READY_FOR_HUMAN_COMPARISON_UNACCEPTED" or packet.get("candidate_ids") != [item.get("candidate_id") for item in candidates]:
        errors.append("local packet state invalid")
    if handoff.get("prior_record_rewritten") is not False or handoff.get("supersedes", {}).get("sha256") != sha256(HANDOFF_R1):
        errors.append("handoff supersession invalid")
    if handoff.get("owner_direction", {}).get("sha256") != sha256(DECISION) or handoff.get("owner_direction", {}).get("qualitative_review_complete") is not True:
        errors.append("handoff owner direction invalid")
    formal = handoff.get("g07_formal_review", {})
    if formal.get("timed_decisions_complete") != 0 or formal.get("human_minutes") is not None or formal.get("deblinded") is not False:
        errors.append("handoff formal review fabricated")
    style_packet = handoff.get("new_style_packet", {})
    if style_packet.get("candidate_count") != 4 or style_packet.get("human_reviewed_candidates") != 0 or style_packet.get("accepted_exact_bases") != 0:
        errors.append("handoff style packet state invalid")
    roots = handoff.get("ch05_exact_production_roots", [])
    if len(roots) != 4 or any(item.get("current_value") is not None for item in roots):
        errors.append("handoff production roots invalid")
    if handoff.get("next_external_action") is not None or handoff.get("approvals_requested_now") != []:
        errors.append("handoff proposes unauthorized action")
    if verify_files:
        for key in ("source_evidence", "packet", "contact_sheet", "lettering_overlay"):
            ref = manifest.get(key, {})
            path = ROOT / ref.get("path", "")
            if not path.is_file() or sha256(path) != ref.get("sha256"):
                errors.append(f"packet manifest hash invalid: {key}")
        if packet.get("source_evidence_sha256") != sha256(EVIDENCE):
            errors.append("local packet evidence hash invalid")
    return sorted(set(errors))


def main() -> int:
    try:
        bundle = {
            "evidence": load(EVIDENCE), "manifest": load(MANIFEST), "decision": load(DECISION),
            "style": load(STYLE), "plans": load(PLANS), "packet": load(PACKET),
            "handoff": load(HANDOFF_R2),
        }
        errors = bundle_errors(bundle, verify_files=True)
        mutations = [
            lambda b: b["evidence"]["execution"].update(input_images=1),
            lambda b: b["evidence"]["execution"].update(existing_art_uploaded=True),
            lambda b: b["evidence"]["execution"].update(model="invented"),
            lambda b: b["evidence"]["acceptance"].update(accepted_exact_bases=1),
            lambda b: b["evidence"]["candidates"].pop(),
            lambda b: b["decision"]["evidence_boundaries"].update(g07_formal_timed_decisions_complete=20),
            lambda b: b["decision"]["evidence_boundaries"].update(g07_deblinding_authorized=True),
            lambda b: b["decision"]["evidence_boundaries"].update(exact_ch05_base_raster={}),
            lambda b: b["style"].update(animation_shot_plan={}),
            lambda b: b["style"]["current_exploration"].update(accepted_exact_bases=1),
            lambda b: b["manifest"].update(human_reviewed_candidates=4),
            lambda b: b["packet"].update(state="ACCEPTED"),
            lambda b: b["handoff"]["g07_formal_review"].update(timed_decisions_complete=20),
            lambda b: b["handoff"]["ch05_exact_production_roots"][0].update(current_value={}),
            lambda b: b["handoff"].update(next_external_action="submit"),
        ]
        rejected = 0
        for mutation in mutations:
            changed = copy.deepcopy(bundle)
            mutation(changed)
            rejected += bool(bundle_errors(changed, verify_files=False))
        if errors or rejected != len(mutations):
            for error in errors:
                print(f"FAIL: {error}", file=sys.stderr)
            if rejected != len(mutations):
                print(f"FAIL: only {rejected}/{len(mutations)} mutations rejected", file=sys.stderr)
            return 1
    except (FileNotFoundError, KeyError, json.JSONDecodeError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings (4 candidates/3 panel roles; text-only/no existing-art upload; 15/15 mutations rejected)")
    print("owner direction bound; G07 formal 0/20; CH05 exact base/mask/authority/cap remain null")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
