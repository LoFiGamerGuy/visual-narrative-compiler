"""Validate exact CH05 local review-link manifest and generated Markdown handoff."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "production/comic/review/ch05-review-artifact-link-manifest-r1.json"
MARKDOWN = ROOT / "docs/research/ch05-review-links-r1.md"
EXPECTED_COUNTS = {
    "review_hubs": 4,
    "contact_sheets": 10,
    "sequence_packets": 9,
    "lettering_overlays": 34,
    "strongest_candidates": 14,
    "noncanon_litrpg_concepts": 3,
    "diagnostic_and_policy_sheets": 11,
    "packet_records": 14,
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(record: dict) -> list[str]:
    failures = []
    if record.get("category_counts") != EXPECTED_COUNTS or record.get("unique_artifact_count") != 99:
        failures.append("artifact/category denominator invalid")
    summary = record.get("summary", {})
    if (summary.get("candidate_count"), summary.get("selected_candidate_count")) != (29, 14):
        failures.append("candidate denominator invalid")
    if any(summary.get(key) != 0 for key in ("owner_decisions", "accepted_candidates", "provider_calls", "uploads", "cost_usd")) or summary.get("human_review_minutes") is not None:
        failures.append("review/activity fabricated")
    paths = [item.get("path") for item in record.get("artifacts", [])]
    if len(paths) != len(set(paths)) or len(paths) != record.get("unique_artifact_count"):
        failures.append("artifact path uniqueness invalid")
    return failures


def main() -> int:
    record = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = errors(record)
    markdown = MARKDOWN.read_text(encoding="utf-8")
    for item in record["artifacts"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"] or path.resolve().as_posix() != item["absolute_path"] or path.stat().st_size != item["bytes"]:
            failures.append(f"artifact binding invalid: {item['path']}")
            continue
        if subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT, check=False).returncode:
            failures.append(f"artifact not ignored: {item['path']}")
        if f"]({item['absolute_path']})" not in markdown:
            failures.append(f"Markdown link missing: {item['path']}")
    if markdown.count("\n- [") != sum(EXPECTED_COUNTS.values()):
        failures.append("Markdown category-link denominator invalid")
    mutations = [
        lambda x: x.update(unique_artifact_count=98),
        lambda x: x["category_counts"].update(contact_sheets=9),
        lambda x: x["category_counts"].update(sequence_packets=8),
        lambda x: x["category_counts"].update(lettering_overlays=33),
        lambda x: x["category_counts"].update(strongest_candidates=13),
        lambda x: x["category_counts"].update(noncanon_litrpg_concepts=2),
        lambda x: x["summary"].update(candidate_count=28),
        lambda x: x["summary"].update(selected_candidate_count=13),
        lambda x: x["summary"].update(owner_decisions=1),
        lambda x: x["summary"].update(accepted_candidates=1),
        lambda x: x["summary"].update(provider_calls=1),
        lambda x: x["summary"].update(uploads=1),
        lambda x: x["summary"].update(cost_usd=1),
        lambda x: x["summary"].update(human_review_minutes=1),
        lambda x: x["artifacts"].append(copy.deepcopy(x["artifacts"][0])),
    ]
    rejected = 0
    for mutation in mutations:
        candidate = copy.deepcopy(record)
        mutation(candidate)
        rejected += bool(errors(candidate))
    if rejected != len(mutations):
        failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 review-link manifest: {len(failures)} failures; {record['unique_artifact_count']} unique artifacts / {sum(EXPECTED_COUNTS.values())} categorized links; {rejected}/{len(mutations)} mutations rejected")
    print("generated pixels tracked/published/accepted 0/0/0; calls/uploads/cost 0/0/$0")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
