"""Validate the fail-closed CH05 P010-P013 production-manifest dry run."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-p010-p013-production-manifest-dry-run-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row_root(rows: list[dict]) -> str:
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()


def errors(record: dict) -> list[str]:
    summary = record.get("summary", {})
    failures = []
    expected = (4, 4, 2, 6, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0)
    keys = ("plan_count", "initial_candidate_slots", "maximum_repair_slots", "maximum_candidate_envelope", "prompt_count", "rendered_candidates", "reference_hypothesis_uses", "reference_uploads", "execution_ready_rows", "accepted_candidates", "comic_panel_plan_revisions", "provider_calls", "uploads", "cost_usd")
    if tuple(summary.get(key) for key in keys) != expected or summary.get("human_review_minutes") is not None or record.get("state") != "PASS_FAIL_CLOSED_OWNER_GATES_PENDING":
        failures.append("dry-run denominator/state invalid")
    if record.get("planned_review_artifact_count") != 5 or record.get("production_stage_count") != 5:
        failures.append("planned artifact/stage denominator invalid")
    if record.get("animation_shot_plan") is not None or record.get("e_conte") is not None:
        failures.append("planning boundary invalid")
    return failures


def main() -> int:
    record = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures = errors(record)
    manifest_path = ROOT / record["manifest"]["path"]
    if not manifest_path.is_file() or sha(manifest_path) != record["manifest"]["sha256"]:
        failures.append("manifest binding invalid")
        manifest = {}
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for item in record["inputs"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            failures.append(f"input binding invalid: {item['path']}")
    rows = manifest.get("rows", [])
    if len(rows) != 4 or row_root(rows) != record.get("row_root_sha256") or row_root(rows) != manifest.get("row_root_sha256"):
        failures.append("row coverage/root invalid")
    expected_panels = ["ng-ch05-sc01-p010", "ng-ch05-sc01-p011", "ng-ch05-sc01-p012", "ng-ch05-sc01-p013"]
    if [row.get("panel_id") for row in rows] != expected_panels:
        failures.append("panel sequence invalid")
    null_fields = ("final_copy", "prompt", "prompt_sha256", "output_sha256", "dimensions", "elapsed_seconds", "model", "endpoint", "request_id", "provider_usage", "provider_cost_usd", "seed", "failure", "human_review_minutes", "acceptance_decision")
    if any(any(row.get(field) is not None for field in null_fields) or row.get("reference_uploads") != 0 or row.get("owner_accepted") is not False or row.get("commercially_cleared") is not False or row.get("execution_ready") is not False or row.get("comic_panel_plan_revision_created") is not False for row in rows):
        failures.append("row fail-closed state invalid")
    gates = manifest.get("gates", {})
    if gates.get("all_required_before_prompt_compilation") is not True or gates.get("prompts_may_be_compiled_now") is not False or any(value is not False for key, value in gates.items() if key not in ("all_required_before_prompt_compilation", "prompts_may_be_compiled_now")):
        failures.append("gate state invalid")
    mutations = [
        lambda x: x.update(state="FAIL"),
        lambda x: x["summary"].update(plan_count=3),
        lambda x: x["summary"].update(initial_candidate_slots=3),
        lambda x: x["summary"].update(maximum_repair_slots=1),
        lambda x: x["summary"].update(maximum_candidate_envelope=5),
        lambda x: x["summary"].update(prompt_count=1),
        lambda x: x["summary"].update(rendered_candidates=1),
        lambda x: x["summary"].update(reference_hypothesis_uses=2),
        lambda x: x["summary"].update(reference_uploads=1),
        lambda x: x["summary"].update(execution_ready_rows=1),
        lambda x: x["summary"].update(accepted_candidates=1),
        lambda x: x["summary"].update(comic_panel_plan_revisions=1),
        lambda x: x["summary"].update(provider_calls=1),
        lambda x: x["summary"].update(uploads=1),
        lambda x: x["summary"].update(cost_usd=1),
        lambda x: x["summary"].update(human_review_minutes=1),
        lambda x: x.update(planned_review_artifact_count=4),
        lambda x: x.update(production_stage_count=4),
        lambda x: x.update(animation_shot_plan={}),
        lambda x: x.update(e_conte={}),
    ]
    rejected = 0
    for mutation in mutations:
        candidate = copy.deepcopy(record)
        mutation(candidate)
        rejected += bool(errors(candidate))
    if rejected != len(mutations):
        failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 P010-P013 manifest dry run: {len(failures)} failures; 4 rows/3 reference hypotheses/5 planned artifacts; {rejected}/{len(mutations)} mutations rejected")
    print("prompts/renders/executable/calls/uploads/cost/accepted/plan revisions 0/0/0/0/0/$0/0/0")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
