"""Validate the overnight plan, reference authority, continuity profile, and prompt build."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/overnight/ch05-overnight-production-plan-r1.json"
PROFILE = ROOT / "production/comic/continuity/ch05-fictional-adult-visual-profile-r1.json"
PANELS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(bundle: dict, verify_files: bool) -> list[str]:
    plan, profile, panels = bundle["plan"], bundle["profile"], bundle["panels"]
    out = []
    candidates = plan.get("candidates", [])
    ids = [item.get("candidate_id") for item in candidates]
    panel_by_id = {item["panel_id"]: item for item in panels.get("plans", [])}
    refs = {item["reference_id"]: item for item in profile.get("authorized_references", [])}
    if len(candidates) != 20 or len(set(ids)) != 20:
        out.append("candidate target invalid")
    if len({item.get("panel_id") for item in candidates}) != 14:
        out.append("distinct panel denominator invalid")
    if len(plan.get("sequences", [])) != 3 or len(plan.get("style_families", {})) != 4:
        out.append("sequence/style denominator invalid")
    if sum(not item.get("reference_ids") for item in candidates) != 4:
        out.append("text-only control count invalid")
    for candidate in candidates:
        panel = panel_by_id.get(candidate.get("panel_id"))
        if panel is None or candidate.get("style_id") not in plan.get("style_families", {}):
            out.append(f"candidate binding invalid: {candidate.get('candidate_id')}")
        if any(ref not in refs for ref in candidate.get("reference_ids", [])):
            out.append(f"reference binding invalid: {candidate.get('candidate_id')}")
    for sequence in plan.get("sequences", []):
        if not set(sequence.get("candidate_ids", [])).issubset(set(ids)):
            out.append(f"sequence candidate invalid: {sequence.get('sequence_id')}")
        if not set(sequence.get("panel_ids", [])).issubset(set(panel_by_id)):
            out.append(f"sequence panel invalid: {sequence.get('sequence_id')}")
    if plan.get("medium") != "comic" or plan.get("animation_shot_plan") is not None or plan.get("e_conte") is not None:
        out.append("medium boundary invalid")
    boundaries = plan.get("boundaries", {})
    if boundaries.get("authorized_product") != "OpenAI built-in ImageGen in Codex" or boundaries.get("direct_paid_api") is not False:
        out.append("provider boundary invalid")
    if boundaries.get("authorized_reference_count") != 3 or boundaries.get("generated_pixels_git_tracked") is not False or boundaries.get("production_base_selection") is not None:
        out.append("authority/retention boundary invalid")
    roles = profile.get("roles", {})
    if "never black" not in roles.get("SOREN", {}).get("hair", "") or "never blond" not in roles.get("SIGRID", {}).get("hair", ""):
        out.append("hair continuity assertion invalid")
    if len(refs) != 3 or refs.get("p036_composition_only", {}).get("role", "").find("non-authoritative") < 0:
        out.append("reference role boundary invalid")
    if verify_files:
        for reference in refs.values():
            path = ROOT / reference["path"]
            if not path.is_file() or sha256(path) != reference["sha256"]:
                out.append(f"authorized reference invalid: {reference['reference_id']}")
    return sorted(set(out))


def main() -> int:
    try:
        bundle = {"plan": json.loads(PLAN.read_text(encoding="utf-8")), "profile": json.loads(PROFILE.read_text(encoding="utf-8")), "panels": json.loads(PANELS.read_text(encoding="utf-8"))}
        found = errors(bundle, True)
        actions = [
            lambda b: b["plan"]["candidates"].pop(),
            lambda b: b["plan"]["candidates"][0].update(candidate_id="c002"),
            lambda b: b["plan"].update(animation_shot_plan={}),
            lambda b: b["plan"]["boundaries"].update(direct_paid_api=True),
            lambda b: b["plan"]["boundaries"].update(authorized_reference_count=4),
            lambda b: b["plan"]["boundaries"].update(production_base_selection={}),
            lambda b: b["plan"]["candidates"][0].update(reference_ids=["unapproved"]),
            lambda b: b["plan"]["candidates"][0].update(style_id="unknown"),
            lambda b: b["profile"]["roles"]["SIGRID"].update(hair="blond"),
            lambda b: b["profile"]["authorized_references"].pop(),
            lambda b: b["profile"]["authorized_references"][2].update(role="identity reference"),
            lambda b: b["plan"].update(medium="animation"),
        ]
        rejected = 0
        for action in actions:
            changed = copy.deepcopy(bundle); action(changed); rejected += bool(errors(changed, False))
        if found or rejected != len(actions):
            for item in found: print(f"FAIL: {item}", file=sys.stderr)
            if rejected != len(actions): print(f"FAIL: only {rejected}/{len(actions)} mutations rejected", file=sys.stderr)
            return 1
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr); return 1
    print("0 failures, 0 warnings (20 candidates/14 plans/3 sequences/4 styles; 3 exact refs; 12/12 mutations rejected)")
    print("ComicPanelPlan-only; built-in ImageGen only; direct paid API disabled; generated pixels ignored/unaccepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
