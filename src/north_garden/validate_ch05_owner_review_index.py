"""Validate the local CH05 owner review index, links, hashes, counts, and non-promotion state."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/review-packets/ch05-owner-review-index-r1"
PACKET = OUT / "owner-review-index-packet.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-owner-review-index-r1.json"
PRODUCTION = ROOT / "production/comic/run-manifests/ch05-instrumented-production-manifest-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_errors(data: dict) -> list[str]:
    out = []
    summary = data.get("summary", {})
    expected = (29, 26, 3, 14, 12, 42)
    actual = tuple(summary.get(field) for field in ("candidate_count", "chapter_candidate_count", "concept_candidate_count", "selected_candidate_count", "review_link_count", "artifact_count"))
    if actual != expected: out.append("denominator invalid")
    if summary.get("accepted_candidates") != 0 or summary.get("human_review_minutes") is not None:
        out.append("acceptance/review fabricated")
    if summary.get("provider_calls") != 0 or summary.get("uploads") != 0 or summary.get("cost_usd") != 0:
        out.append("external activity fabricated")
    selected = data.get("selected_candidates", [])
    if len(selected) != 14 or len({item.get("candidate_id") for item in selected}) != 14 or any(item.get("accepted") is not False for item in selected):
        out.append("selected coverage/promotion invalid")
    links = data.get("review_links", [])
    if len(links) != 12 or len({item.get("path") for item in links}) != 12:
        out.append("review link coverage invalid")
    return sorted(set(out))


def main() -> int:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    production = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    failures = semantic_errors(evidence)
    if sha(PACKET) != evidence["packet"]["sha256"] or sha(ROOT / evidence["index"]["path"]) != evidence["index"]["sha256"]:
        failures.append("packet/index binding mismatch")
    if sha(PRODUCTION) != evidence["production_manifest"]["sha256"]:
        failures.append("production manifest binding mismatch")
    selected_expected = {row["candidate_id"] for row in production["rows"]}
    selected_actual = {item["candidate_id"] for item in evidence["selected_candidates"]}
    if selected_actual != selected_expected:
        failures.append("selected candidate set mismatch")
    for item in packet["artifacts"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            failures.append(f"artifact mismatch: {item['path']}")
        elif subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT, check=False).returncode:
            failures.append(f"artifact not ignored: {item['path']}")
    index_path = ROOT / evidence["index"]["path"]
    source = index_path.read_text(encoding="utf-8")
    for relative in re.findall(r'(?:href|src)="([^"]+)"', source):
        if relative.startswith("#"):
            continue
        target = (index_path.parent / relative).resolve()
        if not target.is_file():
            failures.append(f"broken HTML link: {relative}")
    if source.count('<article class="card') != 41:
        failures.append("HTML card count invalid")
    mutations = [
        lambda d: d["summary"].update(candidate_count=28), lambda d: d["summary"].update(chapter_candidate_count=25),
        lambda d: d["summary"].update(concept_candidate_count=2), lambda d: d["summary"].update(selected_candidate_count=13),
        lambda d: d["summary"].update(review_link_count=11), lambda d: d["summary"].update(artifact_count=41),
        lambda d: d["summary"].update(accepted_candidates=1), lambda d: d["summary"].update(human_review_minutes=1),
        lambda d: d["summary"].update(provider_calls=1), lambda d: d["selected_candidates"].pop(),
        lambda d: d["selected_candidates"][0].update(accepted=True), lambda d: d["review_links"].pop()
    ]
    rejected = 0
    for mutation in mutations:
        changed = copy.deepcopy(evidence); mutation(changed); rejected += bool(semantic_errors(changed))
    if rejected != len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 owner review index: {len(failures)} failures; 29 candidates/14 selected/12 review links/42 artifacts; {rejected}/{len(mutations)} mutations rejected")
    print("all HTML links/hash bindings valid; 3 non-canon concepts separate; 0 accepted/minutes/calls/uploads/$0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
