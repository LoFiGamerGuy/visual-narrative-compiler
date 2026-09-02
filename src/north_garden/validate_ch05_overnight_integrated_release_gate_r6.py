"""Validate and reproduce append-only CH05 overnight integrated release gate r6."""
from __future__ import annotations

import copy, hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs/research/evidence/ch05-overnight-integrated-release-gate-r5.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-overnight-integrated-release-gate-r6.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(record: dict) -> list[str]:
    summary = record.get("summary", {}); state = record.get("effective_state", {}); failures = []
    actual = tuple(summary.get(key) for key in ("base_effective_command_count", "extension_command_count", "effective_command_count", "orchestrator_commands", "passed", "failed"))
    if actual != (38, 4, 42, 5, 5, 0) or record.get("state") != "PASS": failures.append("gate denominator/state invalid")
    zero = ("network_capable_commands", "provider_calls", "uploads", "downloads", "cost_usd", "accepted_candidates", "executable_panels", "owner_decisions", "live_review_events")
    if any(summary.get(key) != 0 for key in zero) or summary.get("human_review_minutes") is not None: failures.append("activity/promotion/review fabricated")
    if record.get("comic_panel_plan_revision_created") is not False or record.get("animation_shot_plan") is not None or record.get("e_conte") is not None: failures.append("planning boundary invalid")
    expected = {"candidates": 29, "review_artifacts": 99, "comic_panel_plans": 50, "readiness_selected": 14, "readiness_dry_run": 4, "readiness_tier_a": 8, "readiness_backlog": 24, "reference_hypotheses": 42, "text_only_plans": 18, "critical_reference_guards": 1, "owner_tasks": 24, "owner_task_stages": [19, 4, 1], "timer_subjects": 39, "next_prompts": 0, "frozen_paths": 16, "baseline_paths": 4}
    if state != expected: failures.append("effective state invalid")
    results = record.get("results", [])
    if len(results) != 5 or any(item.get("return_code") != 0 or item.get("network_capable") is not False or item.get("stderr") for item in results): failures.append("result coverage/state invalid")
    return sorted(set(failures))


def main() -> int:
    record = json.loads(EVIDENCE.read_text(encoding="utf-8")); failures = errors(record)
    if sha(BASE) != record["supersedes"]["sha256"]: failures.append("base r5 binding mismatch")
    for item in record["results"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["script_sha256"]: failures.append(f"script mismatch: {item['path']}"); continue
        done = subprocess.run([sys.executable, str(path)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        stdout = done.stdout.replace("\r\n", "\n").strip() + "\n"
        if done.returncode != 0 or done.stderr or hashlib.sha256(stdout.encode()).hexdigest() != item["stdout_sha256"]: failures.append(f"reproducer mismatch: {item['path']}")
    mutations = [lambda x: x.update(state="FAIL"), lambda x: x["summary"].update(base_effective_command_count=37), lambda x: x["summary"].update(extension_command_count=3), lambda x: x["summary"].update(effective_command_count=41), lambda x: x["summary"].update(orchestrator_commands=4), lambda x: x["summary"].update(passed=4), lambda x: x["summary"].update(failed=1), lambda x: x["summary"].update(provider_calls=1), lambda x: x["summary"].update(uploads=1), lambda x: x["summary"].update(downloads=1), lambda x: x["summary"].update(cost_usd=1), lambda x: x["summary"].update(accepted_candidates=1), lambda x: x["summary"].update(executable_panels=1), lambda x: x["summary"].update(owner_decisions=1), lambda x: x["summary"].update(live_review_events=1), lambda x: x["summary"].update(human_review_minutes=1), lambda x: x["effective_state"].update(readiness_selected=13), lambda x: x["effective_state"].update(reference_hypotheses=41), lambda x: x["effective_state"].update(text_only_plans=17), lambda x: x["effective_state"].update(critical_reference_guards=0), lambda x: x["effective_state"].update(owner_tasks=23), lambda x: x["effective_state"].update(owner_task_stages=[18,4,1]), lambda x: x["effective_state"].update(timer_subjects=38), lambda x: x["effective_state"].update(next_prompts=1), lambda x: x["results"].pop(), lambda x: x.update(animation_shot_plan={})]
    rejected = 0
    for mutation in mutations: candidate = copy.deepcopy(record); mutation(candidate); rejected += bool(errors(candidate))
    if rejected != len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 overnight integrated release r6: {len(failures)} failures; immutable 38 + 4 = 42 effective checks; {rejected}/{len(mutations)} mutations rejected")
    print("50 plans/42 refs/24 tasks/39 timer subjects; frozen 16 + baseline 4; 0 prompts/review/accepted/executable/calls/uploads/$0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__": raise SystemExit(main())
