"""Validate CH05 lettering width/copy sensitivity evidence and non-promotion boundaries."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/lettering/ch05-lettering-width-copy-sensitivity-r1.json"
REVIEW = ROOT / "production/comic/review/ch05-lettering-width-copy-sensitivity-review-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-lettering-width-copy-sensitivity-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


EXPECTED = {
    "c005": {"one_line_short": 1200, "two_line_short": 1200},
    "c013": {"one_line_short": 1200, "two_line_short": 1200},
    "h001": {"one_line_short": 1120, "two_line_short": 1200},
}


def semantic_errors(data: dict) -> list[str]:
    out = []
    summary = data.get("summary", {})
    if (summary.get("subject_count"), summary.get("copy_load_count"), summary.get("case_count"), summary.get("artifact_count")) != (3, 2, 30, 31):
        out.append("denominator invalid")
    if summary.get("minimum_passing_widths") != EXPECTED:
        out.append("width thresholds invalid")
    if summary.get("excluded_semantic_failure_count") != 1:
        out.append("semantic exclusion hidden")
    if summary.get("accepted_layouts") != 0 or summary.get("human_review_minutes") is not None:
        out.append("acceptance/review fabricated")
    if summary.get("provider_calls") != 0 or summary.get("uploads") != 0 or summary.get("cost_usd") != 0:
        out.append("external activity fabricated")
    if data.get("comic_panel_plan_revision_created") is not False or data.get("assembly_revision_created") is not False or data.get("animation_shot_plan") is not None or data.get("e_conte") is not None:
        out.append("planning boundary invalid")
    records = data.get("records", [])
    if len(records) != 30 or len({(x.get("candidate_id"), x.get("copy_id"), x.get("target_width")) for x in records}) != 30:
        out.append("case coverage invalid")
    return sorted(set(out))


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures = semantic_errors(evidence)
    if sha(MANIFEST) != evidence["manifest"]["sha256"] or sha(REVIEW) != evidence["engineering_review"]["sha256"]:
        failures.append("tracked binding mismatch")
    if manifest["excluded"][0]["candidate_id"] != "c014" or review["accepted_layouts"]:
        failures.append("exclusion/acceptance boundary invalid")
    for item in evidence["records"]:
        path = ROOT / item["preview"]["path"]
        if not path.is_file() or sha(path) != item["preview"]["sha256"]:
            failures.append(f"preview mismatch: {item['preview']['path']}")
        elif subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT, check=False).returncode:
            failures.append(f"preview not ignored: {item['preview']['path']}")
    mutations = [
        lambda d: d["summary"].update(subject_count=4), lambda d: d["summary"].update(copy_load_count=1),
        lambda d: d["summary"].update(case_count=29), lambda d: d["summary"].update(artifact_count=30),
        lambda d: d["summary"]["minimum_passing_widths"]["c005"].update(one_line_short=1120),
        lambda d: d["summary"]["minimum_passing_widths"]["h001"].update(two_line_short=1120),
        lambda d: d["summary"].update(excluded_semantic_failure_count=0), lambda d: d["summary"].update(accepted_layouts=1),
        lambda d: d["summary"].update(human_review_minutes=1), lambda d: d["summary"].update(provider_calls=1),
        lambda d: d.update(assembly_revision_created=True), lambda d: d["records"].pop()
    ]
    rejected = 0
    for mutation in mutations:
        changed = copy.deepcopy(evidence); mutation(changed); rejected += bool(semantic_errors(changed))
    if rejected != len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 lettering width/copy sensitivity: {len(failures)} failures; 3 subjects/2 loads/30 cases/31 artifacts; {rejected}/{len(mutations)} mutations rejected")
    print("minimum passing widths: c005 1200/1200, c013 1200/1200, h001 1120/1200; c014 excluded; 0 calls/uploads/$0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
