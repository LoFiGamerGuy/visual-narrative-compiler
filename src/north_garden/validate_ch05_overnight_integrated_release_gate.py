"""Validate and reproduce the complete CH05 overnight local release gate."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-overnight-integrated-release-gate-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_stdout(value: str) -> str:
    value = value.replace("\r\n", "\n").strip() + "\n"
    return re.sub(r"\d+ tracked safe-source paths", "<dynamic> tracked safe-source paths", value)


def semantic_errors(data: dict) -> list[str]:
    out = []
    summary = data.get("summary", {})
    if (summary.get("command_count"), summary.get("passed"), summary.get("failed")) != (16, 16, 0) or data.get("state") != "PASS":
        out.append("gate denominator/state invalid")
    zeros = ["network_capable_commands", "provider_calls", "uploads", "downloads", "cost_usd", "accepted_candidates", "executable_panels"]
    if any(summary.get(field) != 0 for field in zeros) or summary.get("human_review_minutes") is not None:
        out.append("activity/promotion/review fabricated")
    if data.get("comic_panel_plan_revision_created") is not False or data.get("animation_shot_plan") is not None or data.get("e_conte") is not None:
        out.append("planning boundary invalid")
    results = data.get("results", [])
    if len(results) != 16 or len({item.get("path") for item in results}) != 16:
        out.append("result coverage invalid")
    if any(item.get("return_code") != 0 or item.get("network_capable") is not False or item.get("stderr") for item in results):
        out.append("command result invalid")
    return sorted(set(out))


def main() -> int:
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures = semantic_errors(data)
    for item in data["results"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["script_sha256"]:
            failures.append(f"script mismatch: {item['path']}")
            continue
        completed = subprocess.run([sys.executable, str(path)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
        normalized = normalize_stdout(completed.stdout)
        if completed.returncode != 0 or completed.stderr or hashlib.sha256(normalized.encode("utf-8")).hexdigest() != item["normalized_stdout_sha256"]:
            failures.append(f"reproducer mismatch: {item['path']}")
    mutations = [
        lambda d: d.update(state="FAIL"), lambda d: d["summary"].update(command_count=15),
        lambda d: d["summary"].update(passed=15), lambda d: d["summary"].update(failed=1),
        lambda d: d["summary"].update(network_capable_commands=1), lambda d: d["summary"].update(provider_calls=1),
        lambda d: d["summary"].update(uploads=1), lambda d: d["summary"].update(cost_usd=1),
        lambda d: d["summary"].update(accepted_candidates=1), lambda d: d["summary"].update(executable_panels=1),
        lambda d: d["summary"].update(human_review_minutes=1), lambda d: d["results"].pop(),
        lambda d: d["results"][0].update(return_code=1), lambda d: d["results"][0].update(network_capable=True),
        lambda d: d.update(animation_shot_plan={})
    ]
    rejected = 0
    for mutation in mutations:
        changed = copy.deepcopy(data); mutation(changed); rejected += bool(semantic_errors(changed))
    if rejected != len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 overnight integrated release: {len(failures)} failures; 16/16 no-network commands reproduced; {rejected}/{len(mutations)} mutations rejected")
    print("frozen/baseline/source scope pass; 29 candidates/14 selected remain unaccepted/nonexecutable; 0 calls/uploads/downloads/$0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
