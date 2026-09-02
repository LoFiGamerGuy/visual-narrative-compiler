"""Validate and reproduce append-only CH05 overnight integrated release gate r5."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs/research/evidence/ch05-overnight-integrated-release-gate-r4.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-overnight-integrated-release-gate-r5.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(record: dict) -> list[str]:
    summary = record.get("summary", {})
    state = record.get("effective_state", {})
    failures = []
    actual = tuple(summary.get(key) for key in ("base_effective_command_count", "extension_command_count", "effective_command_count", "orchestrator_commands", "passed", "failed"))
    if actual != (33, 5, 38, 6, 6, 0) or record.get("state") != "PASS":
        failures.append("gate denominator/state invalid")
    zero_fields = ("network_capable_commands", "provider_calls", "uploads", "downloads", "cost_usd", "accepted_candidates", "executable_panels", "owner_decisions")
    if any(summary.get(key) != 0 for key in zero_fields) or summary.get("human_review_minutes") is not None:
        failures.append("activity/promotion/review fabricated")
    if record.get("comic_panel_plan_revision_created") is not False or record.get("animation_shot_plan") is not None or record.get("e_conte") is not None:
        failures.append("planning boundary invalid")
    expected = {"candidates": 29, "renderrecords": 29, "review_artifacts": 99, "strongest_shortlist": 14, "owner_hub_links": 12, "style_role_allocations": 4, "route_decisions": 10, "comic_panel_plans": 50, "next_microsequence_plans": 4, "next_candidate_slots": 4, "next_repair_slots": 2, "next_review_checks": 44, "next_planned_artifacts": 5, "next_prompts": 0, "frozen_paths": 16, "baseline_paths": 4}
    if state != expected:
        failures.append("effective state invalid")
    results = record.get("results", [])
    if len(results) != 6 or any(item.get("return_code") != 0 or item.get("network_capable") is not False or item.get("stderr") for item in results):
        failures.append("result coverage/state invalid")
    return sorted(set(failures))


def main() -> int:
    record = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures = errors(record)
    if sha(BASE) != record["supersedes"]["sha256"]:
        failures.append("base r4 binding mismatch")
    for item in record["results"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["script_sha256"]:
            failures.append(f"script mismatch: {item['path']}")
            continue
        done = subprocess.run([sys.executable, str(path)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        stdout = done.stdout.replace("\r\n", "\n").strip() + "\n"
        if done.returncode != 0 or done.stderr or hashlib.sha256(stdout.encode()).hexdigest() != item["stdout_sha256"]:
            failures.append(f"reproducer mismatch: {item['path']}")
    mutations = [
        lambda x: x.update(state="FAIL"),
        lambda x: x["summary"].update(base_effective_command_count=32),
        lambda x: x["summary"].update(extension_command_count=4),
        lambda x: x["summary"].update(effective_command_count=37),
        lambda x: x["summary"].update(orchestrator_commands=5),
        lambda x: x["summary"].update(passed=5),
        lambda x: x["summary"].update(failed=1),
        lambda x: x["summary"].update(provider_calls=1),
        lambda x: x["summary"].update(uploads=1),
        lambda x: x["summary"].update(downloads=1),
        lambda x: x["summary"].update(cost_usd=1),
        lambda x: x["summary"].update(accepted_candidates=1),
        lambda x: x["summary"].update(executable_panels=1),
        lambda x: x["summary"].update(owner_decisions=1),
        lambda x: x["summary"].update(human_review_minutes=1),
        lambda x: x["effective_state"].update(review_artifacts=98),
        lambda x: x["effective_state"].update(strongest_shortlist=13),
        lambda x: x["effective_state"].update(owner_hub_links=11),
        lambda x: x["effective_state"].update(style_role_allocations=3),
        lambda x: x["effective_state"].update(route_decisions=9),
        lambda x: x["effective_state"].update(next_microsequence_plans=3),
        lambda x: x["effective_state"].update(next_candidate_slots=3),
        lambda x: x["effective_state"].update(next_review_checks=43),
        lambda x: x["effective_state"].update(next_prompts=1),
        lambda x: x["results"].pop(),
        lambda x: x.update(animation_shot_plan={}),
    ]
    rejected = 0
    for mutation in mutations:
        candidate = copy.deepcopy(record)
        mutation(candidate)
        rejected += bool(errors(candidate))
    if rejected != len(mutations):
        failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 overnight integrated release r5: {len(failures)} failures; immutable 33 + 5 = 38 effective checks; {rejected}/{len(mutations)} mutations rejected")
    print("29 candidates/99 artifacts/10 decisions/4 next slots/44 checks; frozen 16 + baseline 4; 0 accepted/executable/calls/uploads/$0")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
