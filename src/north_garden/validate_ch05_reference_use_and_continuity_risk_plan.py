"""Validate CH05 metadata-only reference-use and continuity-risk plan."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-reference-use-and-continuity-risk-plan-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(record: dict) -> list[str]:
    summary = record.get("summary", {})
    failures = []
    keys = ("plan_count", "text_only_plans", "reference_hypothesis_uses", "p050_hypotheses", "p040_hypotheses", "p036_composition_hypotheses", "low_risk", "medium_risk", "high_risk", "critical_guarded")
    expected = (50, 18, 42, 25, 16, 1, 18, 9, 22, 1)
    if tuple(summary.get(key) for key in keys) != expected or record.get("state") != "PASS_ZERO_UPLOAD":
        failures.append("risk/reference denominator invalid")
    zero = ("reference_uploads", "automated_identity_inferences", "next_prompt_count", "owner_accepted", "execution_ready", "provider_calls", "cost_usd")
    if any(summary.get(key) != 0 for key in zero) or summary.get("human_review_minutes") is not None:
        failures.append("activity/inference/promotion fabricated")
    if record.get("animation_shot_plan") is not None or record.get("e_conte") is not None:
        failures.append("planning boundary invalid")
    return failures


def main() -> int:
    record = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures = errors(record)
    plan_path = ROOT / record["plan"]["path"]
    if not plan_path.is_file() or sha(plan_path) != record["plan"]["sha256"]:
        failures.append("plan binding invalid")
        plan = {}
    else:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    for item in record["inputs"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            failures.append(f"input binding invalid: {item['path']}")
    chart = ROOT / record["chart"]["path"]
    if not chart.is_file() or sha(chart) != record["chart"]["sha256"] or subprocess.run(["git", "check-ignore", "-q", str(chart)], cwd=ROOT, check=False).returncode:
        failures.append("chart binding/ignore invalid")
    else:
        with Image.open(chart) as image:
            if list(image.size) != record["chart"]["dimensions"]:
                failures.append("chart dimensions invalid")
    rows = plan.get("rows", [])
    if len(rows) != 50 or [row.get("display_order") for row in rows] != list(range(1, 51)):
        failures.append("row coverage/order invalid")
    if any(row.get("reference_uploads") != 0 or row.get("next_prompt") is not None or row.get("automated_identity_inference") is not False or row.get("owner_accepted") is not False or row.get("execution_ready") is not False for row in rows):
        failures.append("row boundary invalid")
    p036 = next((row for row in rows if row.get("panel_id") == "ng-ch05-sc01-p036"), {})
    if p036.get("continuity_risk") != "CRITICAL_GUARDED" or "p036_composition_only" not in p036.get("reference_hypotheses", []) or "P036_SWAPPED_HAIR_COMPOSITION_REFERENCE" not in p036.get("risk_flags", []):
        failures.append("P036 guard invalid")
    no_people = [row for row in rows if not row.get("visible_adult_cast")]
    if len(no_people) != 18 or any(row.get("reference_hypotheses") for row in no_people):
        failures.append("no-person text-only boundary invalid")
    mutations = [
        lambda x: x.update(state="FAIL"), lambda x: x["summary"].update(plan_count=49), lambda x: x["summary"].update(text_only_plans=17), lambda x: x["summary"].update(reference_hypothesis_uses=41), lambda x: x["summary"].update(p050_hypotheses=24), lambda x: x["summary"].update(p040_hypotheses=15), lambda x: x["summary"].update(p036_composition_hypotheses=2), lambda x: x["summary"].update(low_risk=17), lambda x: x["summary"].update(medium_risk=8), lambda x: x["summary"].update(high_risk=21), lambda x: x["summary"].update(critical_guarded=0), lambda x: x["summary"].update(reference_uploads=1), lambda x: x["summary"].update(automated_identity_inferences=1), lambda x: x["summary"].update(next_prompt_count=1), lambda x: x["summary"].update(owner_accepted=1), lambda x: x["summary"].update(execution_ready=1), lambda x: x["summary"].update(provider_calls=1), lambda x: x["summary"].update(cost_usd=1), lambda x: x["summary"].update(human_review_minutes=1), lambda x: x.update(animation_shot_plan={})]
    rejected = 0
    for mutation in mutations:
        candidate = copy.deepcopy(record)
        mutation(candidate)
        rejected += bool(errors(candidate))
    if rejected != len(mutations):
        failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 reference risk: {len(failures)} failures; 50 plans/42 hypotheses/18 text-only/1 P036 guard; {rejected}/{len(mutations)} mutations rejected")
    print("uploads/identity inference/prompts/accepted/executable/calls/cost 0/0/0/0/0/0/$0")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
