"""Validate owner review index r3 links, r2 extension, and zero-decision boundary."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-owner-review-index-r3.json"
CONTRACT = ROOT / "production/comic/review/ch05-owner-decision-contract-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(record: dict) -> list[str]:
    summary = record.get("summary", {})
    expected = (29, 14, 39, 12, 10, 2, 11)
    actual = tuple(summary.get(key) for key in ("candidate_count", "selected_candidate_count", "pending_subject_count", "link_count", "image_link_count", "html_link_count", "artifact_count"))
    failures = []
    if actual != expected:
        failures.append("index denominators invalid")
    if any(summary.get(key) != 0 for key in ("owner_decisions", "accepted_candidates", "provider_calls", "uploads", "cost_usd")) or summary.get("human_review_minutes") is not None:
        failures.append("review/activity fabricated")
    return failures


def main() -> int:
    record = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures = errors(record)
    packet = ROOT / record["packet"]["path"]
    if not packet.is_file() or sha(packet) != record["packet"]["sha256"]:
        failures.append("packet binding invalid")
    elif subprocess.run(["git", "check-ignore", "-q", str(packet)], cwd=ROOT, check=False).returncode:
        failures.append("packet not ignored")
    if sha(ROOT / record["extends"]["path"]) != record["extends"]["sha256"]:
        failures.append("r2 extension binding invalid")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if sha(CONTRACT) != record["contract"]["sha256"] or contract["summary"]["completed_decisions"] != 0 or contract["event_contract"]["events"]:
        failures.append("contract binding/state invalid")
    for item in record["links"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            failures.append(f"broken link {item['id']}")
    index = ROOT / record["index"]["path"]
    if not index.is_file() or sha(index) != record["index"]["sha256"]:
        failures.append("index binding invalid")
    else:
        source = index.read_text(encoding="utf-8")
        if any(token in source for token in ("fetch(", "XMLHttpRequest", "WebSocket", "<form", "http://", "https://")):
            failures.append("network/form capability found")
        if len(re.findall(r"<article>", source)) != 12:
            failures.append("HTML card denominator invalid")
    mutations = [
        lambda x: x["summary"].update(candidate_count=28),
        lambda x: x["summary"].update(selected_candidate_count=13),
        lambda x: x["summary"].update(pending_subject_count=38),
        lambda x: x["summary"].update(link_count=11),
        lambda x: x["summary"].update(image_link_count=9),
        lambda x: x["summary"].update(html_link_count=1),
        lambda x: x["summary"].update(artifact_count=10),
        lambda x: x["summary"].update(owner_decisions=1),
        lambda x: x["summary"].update(accepted_candidates=1),
        lambda x: x["summary"].update(provider_calls=1),
        lambda x: x["summary"].update(uploads=1),
        lambda x: x["summary"].update(cost_usd=1),
        lambda x: x["summary"].update(human_review_minutes=1),
    ]
    rejected = 0
    for mutation in mutations:
        candidate = copy.deepcopy(record)
        mutation(candidate)
        rejected += bool(errors(candidate))
    if rejected != len(mutations):
        failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 owner review index r3: {len(failures)} failures; 12 links/10 images/2 HTML/11 artifacts; {rejected}/{len(mutations)} mutations rejected")
    print("29 candidates/14 selected/39 pending; decisions/accepted/calls/uploads/cost 0/0/0/0/$0")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
