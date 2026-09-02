"""Validate and reproduce append-only CH05 overnight integrated release gate r2."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs/research/evidence/ch05-overnight-integrated-release-gate-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-overnight-integrated-release-gate-r2.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_errors(data: dict) -> list[str]:
    out = []
    s = data.get("summary", {})
    if (s.get("base_command_count"), s.get("extension_command_count"), s.get("effective_command_count"), s.get("orchestrator_commands"), s.get("passed"), s.get("failed")) != (16, 2, 18, 3, 3, 0) or data.get("state") != "PASS":
        out.append("gate denominator/state invalid")
    if any(s.get(field) != 0 for field in ("network_capable_commands", "provider_calls", "uploads", "downloads", "cost_usd", "accepted_candidates", "executable_panels")) or s.get("human_review_minutes") is not None:
        out.append("activity/promotion/review fabricated")
    if data.get("comic_panel_plan_revision_created") is not False or data.get("animation_shot_plan") is not None or data.get("e_conte") is not None:
        out.append("planning boundary invalid")
    coverage = data.get("effective_coverage", {})
    if coverage != {"comic_panel_plans": 50, "selected": 14, "tier_a": 12, "tier_b": 12, "tier_c": 12}:
        out.append("coverage invalid")
    results = data.get("results", [])
    if len(results) != 3 or any(item.get("return_code") != 0 or item.get("network_capable") is not False or item.get("stderr") for item in results):
        out.append("result coverage/state invalid")
    return sorted(set(out))


def main() -> int:
    data = json.loads(EVIDENCE.read_text(encoding="utf-8")); failures = semantic_errors(data)
    if sha(BASE) != data["supersedes"]["sha256"]:
        failures.append("base r1 binding mismatch")
    for item in data["results"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["script_sha256"]:
            failures.append(f"script mismatch: {item['path']}"); continue
        completed = subprocess.run([sys.executable, str(path)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240)
        stdout = completed.stdout.replace("\r\n", "\n").strip() + "\n"
        if completed.returncode != 0 or completed.stderr or hashlib.sha256(stdout.encode("utf-8")).hexdigest() != item["stdout_sha256"]:
            failures.append(f"reproducer mismatch: {item['path']}")
    mutations = [
        lambda d: d.update(state="FAIL"), lambda d: d["summary"].update(base_command_count=15),
        lambda d: d["summary"].update(extension_command_count=1), lambda d: d["summary"].update(effective_command_count=17),
        lambda d: d["summary"].update(passed=2), lambda d: d["summary"].update(failed=1),
        lambda d: d["summary"].update(provider_calls=1), lambda d: d["summary"].update(accepted_candidates=1),
        lambda d: d["effective_coverage"].update(comic_panel_plans=49), lambda d: d["effective_coverage"].update(tier_a=11),
        lambda d: d["results"].pop(), lambda d: d["results"][0].update(return_code=1), lambda d: d.update(animation_shot_plan={})
    ]
    rejected = 0
    for mutation in mutations:
        changed = copy.deepcopy(data); mutation(changed); rejected += bool(semantic_errors(changed))
    if rejected != len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 overnight integrated release r2: {len(failures)} failures; immutable 16 + 2 coverage = 18 effective checks; {rejected}/{len(mutations)} mutations rejected")
    print("50 plans = 14 selected + 12/12/12; frozen/source inherited through reproduced r1; 0 accepted/executable/calls/uploads/$0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
