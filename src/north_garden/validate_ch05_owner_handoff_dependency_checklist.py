"""Validate dependency-ordered CH05 owner handoff checklist."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-owner-handoff-dependency-checklist-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(record: dict) -> list[str]:
    summary = record.get("summary", {})
    failures = []
    actual = tuple(summary.get(key) for key in ("task_count", "candidate_review_tasks", "route_decision_tasks", "stage_1_tasks", "stage_2_tasks", "stage_3_tasks", "optional_parallel_tasks", "completed_tasks", "owner_decisions", "accepted_candidates"))
    if actual != (24, 14, 10, 19, 4, 1, 1, 0, 0, 0) or record.get("state") != "PASS_ALL_EMPTY" or summary.get("human_review_minutes") is not None:
        failures.append("checklist denominator/state invalid")
    if any(summary.get(key) != 0 for key in ("provider_calls", "uploads", "cost_usd")):
        failures.append("activity fabricated")
    if record.get("animation_shot_plan") is not None or record.get("e_conte") is not None:
        failures.append("planning boundary invalid")
    return failures


def main() -> int:
    record = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures = errors(record)
    checklist_path = ROOT / record["checklist"]["path"]
    markdown_path = ROOT / record["markdown"]["path"]
    if not checklist_path.is_file() or sha(checklist_path) != record["checklist"]["sha256"] or not markdown_path.is_file() or sha(markdown_path) != record["markdown"]["sha256"]:
        failures.append("output binding invalid")
        checklist = {}
    else:
        checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
    for item in record["inputs"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            failures.append(f"input binding invalid: {item['path']}")
    tasks = checklist.get("tasks", [])
    ids = {task.get("task_id") for task in tasks}
    if len(tasks) != 24 or len(ids) != 24 or any(dep not in ids for task in tasks for dep in task.get("dependencies", [])):
        failures.append("task/dependency coverage invalid")
    if any(task.get("decision") is not None or task.get("reviewer") is not None or task.get("human_review_minutes") is not None for task in tasks):
        failures.append("task decision/review fabricated")
    stage_by_id = {task["task_id"]: task["stage"] for task in tasks}
    if any(stage_by_id[dep] >= task["stage"] for task in tasks for dep in task["dependencies"]):
        failures.append("dependency stage order invalid")
    markdown = markdown_path.read_text(encoding="utf-8") if markdown_path.is_file() else ""
    if markdown.count("\n- [ ] [") != 24 or any(f"]({task['artifact']['absolute_path']})" not in markdown for task in tasks):
        failures.append("Markdown task/link coverage invalid")
    for task in tasks:
        path = ROOT / task["artifact"]["path"]
        if not path.is_file() or sha(path) != task["artifact"]["sha256"] or path.resolve().as_posix() != task["artifact"]["absolute_path"]:
            failures.append(f"artifact binding invalid: {task['task_id']}")
    mutations = [lambda x: x.update(state="FAIL"), lambda x: x["summary"].update(task_count=23), lambda x: x["summary"].update(candidate_review_tasks=13), lambda x: x["summary"].update(route_decision_tasks=9), lambda x: x["summary"].update(stage_1_tasks=18), lambda x: x["summary"].update(stage_2_tasks=3), lambda x: x["summary"].update(stage_3_tasks=0), lambda x: x["summary"].update(optional_parallel_tasks=0), lambda x: x["summary"].update(completed_tasks=1), lambda x: x["summary"].update(owner_decisions=1), lambda x: x["summary"].update(accepted_candidates=1), lambda x: x["summary"].update(human_review_minutes=1), lambda x: x["summary"].update(provider_calls=1), lambda x: x["summary"].update(uploads=1), lambda x: x["summary"].update(cost_usd=1), lambda x: x.update(animation_shot_plan={})]
    rejected = 0
    for mutation in mutations:
        candidate = copy.deepcopy(record); mutation(candidate); rejected += bool(errors(candidate))
    if rejected != len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 owner checklist: {len(failures)} failures; 24=14 candidate+10 route tasks; stages 19/4/1; {rejected}/{len(mutations)} mutations rejected")
    print("completed/decisions/accepted/minutes/calls/uploads/cost 0/0/0/null/0/0/$0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
