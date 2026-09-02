"""Validate the bounded CH05 cadence-hardening plan and exact reference boundary."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "production/comic/overnight/ch05-cadence-hardening-plan-r1.json"
PROFILE = ROOT / "production/comic/continuity/ch05-fictional-adult-visual-profile-r1.json"
PANELS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(plan: dict, profile: dict, panels: dict, verify_files: bool = True) -> list[str]:
    out: list[str] = []
    candidates = plan.get("candidates", [])
    refs = {item["reference_id"]: item for item in profile.get("authorized_references", [])}
    panel_ids = {item["panel_id"] for item in panels.get("plans", [])}
    if len(candidates) != 6 or len({item.get("candidate_id") for item in candidates}) != 6:
        out.append("candidate denominator invalid")
    if len({item.get("panel_id") for item in candidates}) != 5:
        out.append("panel denominator invalid")
    if sum(not item.get("reference_ids") for item in candidates) != 1:
        out.append("text-only control denominator invalid")
    if plan.get("medium") != "comic" or plan.get("animation_shot_plan") is not None or plan.get("e_conte") is not None:
        out.append("ComicPanelPlan-only boundary invalid")
    if "built-in ImageGen" not in " ".join(plan.get("boundaries", [])) or "No direct paid API" not in " ".join(plan.get("boundaries", [])):
        out.append("provider/spend boundary invalid")
    for item in candidates:
        if item.get("panel_id") not in panel_ids or item.get("style_id") not in plan.get("style_families", {}):
            out.append(f"candidate plan/style invalid: {item.get('candidate_id')}")
        if any(ref not in refs for ref in item.get("reference_ids", [])):
            out.append(f"candidate reference invalid: {item.get('candidate_id')}")
    if len(refs) != 3:
        out.append("authorized reference count invalid")
    if verify_files:
        for ref in refs.values():
            path = ROOT / ref["path"]
            if not path.is_file() or sha256(path) != ref["sha256"]:
                out.append(f"reference bytes invalid: {ref['reference_id']}")
    return sorted(set(out))


def main() -> int:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    panels = json.loads(PANELS.read_text(encoding="utf-8"))
    failures = errors(plan, profile, panels)
    mutations = [
        lambda p, r: p["candidates"].pop(),
        lambda p, r: p["candidates"][1].update(candidate_id="h001"),
        lambda p, r: p.update(animation_shot_plan={}),
        lambda p, r: p.update(medium="animation"),
        lambda p, r: p["candidates"][0].update(reference_ids=["unknown"]),
        lambda p, r: p["candidates"][0].update(style_id="unknown"),
        lambda p, r: p["candidates"][0].update(panel_id="unknown"),
        lambda p, r: p["boundaries"].clear(),
        lambda p, r: r["authorized_references"].pop(),
    ]
    rejected = 0
    for mutation in mutations:
        changed_plan, changed_profile = copy.deepcopy(plan), copy.deepcopy(profile)
        mutation(changed_plan, changed_profile)
        rejected += bool(errors(changed_plan, changed_profile, panels, False))
    if rejected != len(mutations):
        failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 cadence hardening plan: {len(failures)} failures; 6 candidates/5 plans/3 exact refs; {rejected}/{len(mutations)} mutations rejected")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
