"""Validate tracked evidence binding for the CH05 50-plan coverage/priority partition."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIORITY = ROOT / "production/comic/coverage/ch05-remaining-panel-priority-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-remaining-panel-priority-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_errors(data: dict) -> list[str]:
    out = []
    summary = data.get("summary", {})
    if tuple(summary.get(field) for field in ("plan_count", "selected_count", "uncovered_count", "tier_a_count", "tier_b_count", "tier_c_count")) != (50, 14, 36, 12, 12, 12):
        out.append("denominator invalid")
    if any(summary.get(field) != 0 for field in ("production_executable", "accepted_new_plans", "provider_calls", "uploads", "cost_usd")) or summary.get("human_review_minutes") is not None:
        out.append("execution/activity/review fabricated")
    if data.get("comic_panel_plan_revision_created") is not False or data.get("animation_shot_plan") is not None or data.get("e_conte") is not None:
        out.append("planning boundary invalid")
    tiers = data.get("priority_tiers", [])
    orders = [order for tier in tiers for group in tier.get("groups", []) for order in group.get("orders", [])]
    if [tier.get("tier") for tier in tiers] != ["A", "B", "C"] or len(orders) != 36 or len(set(orders)) != 36:
        out.append("tier coverage invalid")
    return sorted(set(out))


def main() -> int:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8")); priority = json.loads(PRIORITY.read_text(encoding="utf-8"))
    failures = semantic_errors(evidence)
    if sha(PRIORITY) != evidence["priority_manifest"]["sha256"] or evidence["row_root_sha256"] != priority["row_root_sha256"]:
        failures.append("priority binding mismatch")
    if evidence["coverage"] != priority["coverage"] or evidence["chart"] != priority["chart"]:
        failures.append("coverage/chart mismatch")
    mutations = [
        lambda d: d["summary"].update(plan_count=49), lambda d: d["summary"].update(selected_count=15),
        lambda d: d["summary"].update(uncovered_count=35), lambda d: d["summary"].update(tier_a_count=11),
        lambda d: d["summary"].update(production_executable=1), lambda d: d["summary"].update(accepted_new_plans=1),
        lambda d: d["summary"].update(provider_calls=1), lambda d: d.update(comic_panel_plan_revision_created=True),
        lambda d: d["priority_tiers"].pop(), lambda d: d["priority_tiers"][0]["groups"][0]["orders"].pop()
    ]
    rejected = 0
    for mutation in mutations:
        changed = copy.deepcopy(evidence); mutation(changed); rejected += bool(semantic_errors(changed))
    if rejected != len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 remaining priority evidence: {len(failures)} failures; exact 50 = 14 + 12/12/12; {rejected}/{len(mutations)} mutations rejected")
    print("Tier A trail/twine + mill/red-cloth; all plans unchanged; 0 accepted/executable/calls/uploads/$0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
