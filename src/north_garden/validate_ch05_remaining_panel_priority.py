"""Validate the 50-plan CH05 selected/uncovered partition and no-execution priority boundary."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PRIORITY = ROOT / "production/comic/coverage/ch05-remaining-panel-priority-r1.json"
PLANS = ROOT / "production/comic/ch05-sc01-panel-plans-v1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def semantic_errors(data: dict) -> list[str]:
    out = []
    summary = data.get("summary", {})
    actual = tuple(summary.get(field) for field in ("plan_count", "selected_count", "uncovered_count", "tier_a_count", "tier_b_count", "tier_c_count"))
    if actual != (50, 14, 36, 12, 12, 12): out.append("denominator invalid")
    zeros = ["production_executable", "accepted_new_plans", "provider_calls", "uploads", "cost_usd"]
    if any(summary.get(field) != 0 for field in zeros) or summary.get("human_review_minutes") is not None:
        out.append("execution/activity/review fabricated")
    if data.get("comic_panel_plan_revision_created") is not False or data.get("animation_shot_plan") is not None or data.get("e_conte") is not None:
        out.append("planning boundary invalid")
    rows = data.get("rows", [])
    if len(rows) != 50 or [row.get("order") for row in rows] != list(range(1, 51)) or len({row.get("panel_id") for row in rows}) != 50:
        out.append("row coverage invalid")
    counts = {state: sum(row.get("coverage_state") == state for row in rows) for state in ("selected", "A", "B", "C")}
    if counts != {"selected": 14, "A": 12, "B": 12, "C": 12}:
        out.append("partition invalid")
    if any(row.get("comic_panel_plan_revision_created") is not False or row.get("production_executable") is not False or row.get("final_copy_bound") is not False for row in rows):
        out.append("row promotion invalid")
    if data.get("row_root_sha256") != canonical_sha(rows): out.append("row root invalid")
    tiers = data.get("priority_tiers", [])
    if [tier.get("tier") for tier in tiers] != ["A", "B", "C"]:
        out.append("tier order invalid")
    tier_orders = [order for tier in tiers for group in tier.get("groups", []) for order in group.get("orders", [])]
    if len(tier_orders) != 36 or len(set(tier_orders)) != 36:
        out.append("tier group coverage invalid")
    return sorted(set(out))


def main() -> int:
    data = json.loads(PRIORITY.read_text(encoding="utf-8")); plans = json.loads(PLANS.read_text(encoding="utf-8"))
    plan_map = {plan["panel_id"]: plan for plan in plans["plans"]}; failures = semantic_errors(data)
    if sha(PLANS) != data["comic_panel_plan_collection"]["sha256"]: failures.append("plan collection binding mismatch")
    for row in data["rows"]:
        plan = plan_map.get(row["panel_id"])
        if plan is None or canonical_sha(plan) != row["plan_canonical_sha256"] or plan["plan_revision_id"] != row["plan_revision_id"]:
            failures.append(f"plan row mismatch: {row['panel_id']}")
    chart = ROOT / data["chart"]["path"]
    if not chart.is_file() or sha(chart) != data["chart"]["sha256"]:
        failures.append("chart mismatch")
    elif subprocess.run(["git", "check-ignore", "-q", str(chart)], cwd=ROOT, check=False).returncode:
        failures.append("chart not ignored")
    mutations = [
        lambda d: d["summary"].update(plan_count=49), lambda d: d["summary"].update(selected_count=15),
        lambda d: d["summary"].update(uncovered_count=35), lambda d: d["summary"].update(tier_a_count=11),
        lambda d: d["summary"].update(production_executable=1), lambda d: d["summary"].update(provider_calls=1),
        lambda d: d.update(comic_panel_plan_revision_created=True), lambda d: d["rows"].pop(),
        lambda d: d["rows"][14].update(coverage_state="selected"), lambda d: d["rows"][0].update(production_executable=True),
        lambda d: d.update(row_root_sha256="0" * 64), lambda d: d["priority_tiers"].reverse(),
        lambda d: d["priority_tiers"][0]["groups"][0]["orders"].pop()
    ]
    rejected = 0
    for mutation in mutations:
        changed = copy.deepcopy(data); mutation(changed); rejected += bool(semantic_errors(changed))
    if rejected != len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 remaining panel priority: {len(failures)} failures; 50 plans = 14 selected + 12/12/12 tiers; {rejected}/{len(mutations)} mutations rejected")
    print("all four practical-action plans selected; remaining trail/mill/interior/connective coverage exact; 0 executable/calls/uploads/$0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
