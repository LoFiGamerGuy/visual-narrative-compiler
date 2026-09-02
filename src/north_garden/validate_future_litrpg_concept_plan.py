"""Validate the bounded non-canon future LitRPG concept plan."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/concepts/future-litrpg-visual-concepts-r1.json"
PROFILE = ROOT / "production/comic/continuity/ch05-fictional-adult-visual-profile-r1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(plan: dict, profile: dict, verify: bool = True) -> list[str]:
    out: list[str] = []
    candidates = plan.get("candidates", [])
    refs = {item["reference_id"]: item for item in profile.get("authorized_references", [])}
    if len(candidates) != 3 or len({item.get("candidate_id") for item in candidates}) != 3:
        out.append("candidate denominator invalid")
    if plan.get("canon_status") != "NONCANON_FUTURE_EXPLORATION" or plan.get("production_planning_record") is not False:
        out.append("non-canon boundary invalid")
    if plan.get("comic_panel_plan_revision") is not None or plan.get("animation_shot_plan") is not None or plan.get("e_conte") is not None:
        out.append("planning boundary invalid")
    boundaries = " ".join(plan.get("boundaries", []))
    for phrase in ("built-in ImageGen", "No direct paid API", "not a CH05 ComicPanelPlan"):
        if phrase.lower() not in boundaries.lower():
            out.append(f"boundary phrase missing: {phrase}")
    for candidate in candidates:
        if any(ref not in refs for ref in candidate.get("reference_ids", [])):
            out.append(f"unauthorized ref: {candidate.get('candidate_id')}")
        if "Non-canon" not in candidate.get("request", ""):
            out.append(f"non-canon prompt missing: {candidate.get('candidate_id')}")
    if len(refs) != 3:
        out.append("reference denominator invalid")
    if verify:
        for ref in refs.values():
            path = ROOT / ref["path"]
            if not path.is_file() or sha256(path) != ref["sha256"]:
                out.append(f"reference hash invalid: {ref['reference_id']}")
    return sorted(set(out))


def main() -> int:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    failures = errors(plan, profile)
    mutations = [
        lambda p, r: p["candidates"].pop(),
        lambda p, r: p["candidates"][1].update(candidate_id="l001"),
        lambda p, r: p.update(canon_status="CANON"),
        lambda p, r: p.update(production_planning_record=True),
        lambda p, r: p.update(comic_panel_plan_revision={}),
        lambda p, r: p["candidates"][0].update(reference_ids=["unknown"]),
        lambda p, r: p["boundaries"].clear(),
        lambda p, r: r["authorized_references"].pop(),
    ]
    rejected = 0
    for mutation in mutations:
        changed_plan, changed_profile = copy.deepcopy(plan), copy.deepcopy(profile)
        mutation(changed_plan, changed_profile)
        rejected += bool(errors(changed_plan, changed_profile, False))
    if rejected != len(mutations):
        failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"future LitRPG concept plan: {len(failures)} failures; 3 non-canon candidates/3 exact refs; {rejected}/{len(mutations)} mutations rejected")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
