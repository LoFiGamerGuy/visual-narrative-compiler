"""Validate 50-plan CH05 production-readiness matrix."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-chapter-production-readiness-matrix-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(record: dict) -> list[str]:
    summary = record.get("summary", {})
    failures = []
    expected = (50, 14, 4, 8, 24, 14, 26)
    actual = tuple(summary.get(key) for key in ("plan_count", "selected_evidence", "dry_run_rows", "tier_a_without_dry_run", "backlog_plan_only", "plans_with_existing_candidates", "existing_ch05_candidates"))
    if actual != expected or record.get("state") != "PASS_OWNER_PENDING":
        failures.append("readiness denominator/state invalid")
    zero = ("next_prompt_count", "final_copy_bound", "owner_accepted", "commercially_cleared", "execution_ready", "plan_revisions", "provider_calls", "uploads", "cost_usd")
    if any(summary.get(key) != 0 for key in zero) or summary.get("human_review_minutes") is not None:
        failures.append("readiness activity/promotion fabricated")
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
    chart = ROOT / record["chart"]["path"]
    if not chart.is_file() or sha(chart) != record["chart"]["sha256"] or subprocess.run(["git", "check-ignore", "-q", str(chart)], cwd=ROOT, check=False).returncode:
        failures.append("chart binding/ignore invalid")
    else:
        with Image.open(chart) as image:
            if list(image.size) != record["chart"]["dimensions"]:
                failures.append("chart dimensions invalid")
    rows = manifest.get("rows", [])
    if len(rows) != 50 or [row.get("display_order") for row in rows] != list(range(1, 51)) or len({row.get("panel_id") for row in rows}) != 50:
        failures.append("row coverage/order invalid")
    if any(row.get("continuity_assertions_present") is not True or row.get("next_production_prompt") is not None or row.get("final_copy_bound") is not False or row.get("owner_accepted") is not False or row.get("commercially_cleared") is not False or row.get("execution_ready") is not False or row.get("comic_panel_plan_revision_created") is not False for row in rows):
        failures.append("row fail-closed state invalid")
    expected_classes = {"EVIDENCE_SELECTED_OWNER_PENDING": 14, "DRY_RUN_OWNER_GATES_PENDING": 4, "PRIORITIZED_NO_DRY_RUN": 8, "BACKLOG_PLAN_ONLY": 24}
    if {key: sum(row.get("readiness_class") == key for row in rows) for key in expected_classes} != expected_classes:
        failures.append("row readiness partition invalid")
    mutations = [
        lambda x: x.update(state="FAIL"),
        lambda x: x["summary"].update(plan_count=49),
        lambda x: x["summary"].update(selected_evidence=13),
        lambda x: x["summary"].update(dry_run_rows=3),
        lambda x: x["summary"].update(tier_a_without_dry_run=7),
        lambda x: x["summary"].update(backlog_plan_only=23),
        lambda x: x["summary"].update(plans_with_existing_candidates=13),
        lambda x: x["summary"].update(existing_ch05_candidates=25),
        lambda x: x["summary"].update(next_prompt_count=1),
        lambda x: x["summary"].update(final_copy_bound=1),
        lambda x: x["summary"].update(owner_accepted=1),
        lambda x: x["summary"].update(commercially_cleared=1),
        lambda x: x["summary"].update(execution_ready=1),
        lambda x: x["summary"].update(plan_revisions=1),
        lambda x: x["summary"].update(provider_calls=1),
        lambda x: x["summary"].update(uploads=1),
        lambda x: x["summary"].update(cost_usd=1),
        lambda x: x["summary"].update(human_review_minutes=1),
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
    print(f"CH05 chapter readiness: {len(failures)} failures; 50=14 selected+4 dry-run+8 Tier-A+24 backlog; {rejected}/{len(mutations)} mutations rejected")
    print("next prompts/copy/accepted/commercial/executable/revisions/calls/uploads/cost 0/0/0/0/0/0/0/0/$0")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
