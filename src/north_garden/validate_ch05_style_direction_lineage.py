"""Validate append-only CH05 ComicStyleDirection r1-r9 lineage and non-promotion boundaries."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "production/comic/style-direction"
PATHS = [DIR / f"ch05-mill-signal-r{index}.json" for index in range(1, 10)]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_errors(records: list[dict]) -> list[str]:
    out = []
    if len(records) != 9 or [item.get("record_id") for item in records] != [f"ng-comic-style-ch05-mill-signal-r{i}" for i in range(1, 10)]:
        out.append("revision coverage invalid")
    if any(item.get("medium") != "comic" or item.get("animation_shot_plan") is not None or item.get("e_conte") is not None for item in records):
        out.append("medium/planning boundary invalid")
    for index in range(1, len(records)):
        prior_path = PATHS[index - 1]
        supersedes = records[index].get("supersedes", {})
        if supersedes.get("record_id") != records[index - 1].get("record_id") or supersedes.get("path") != prior_path.relative_to(ROOT).as_posix() or supersedes.get("sha256") != sha(prior_path):
            out.append(f"supersession invalid: r{index + 1}")
    latest = records[-1]
    if latest.get("state") != "MEASURED_ROLE_AWARE_ROUTE_OWNER_REVIEW_PENDING":
        out.append("latest state invalid")
    evidence = latest.get("evidence", {})
    expected = {
        "docs/research/evidence/ch05-overnight-production-r1.json",
        "docs/research/evidence/ch05-cadence-hardening-r1.json",
        "docs/research/evidence/ch05-variable-cadence-assembly-r1.json",
        "docs/research/evidence/ch05-transparent-lettering-rehearsal-r1.json",
        "docs/research/evidence/ch05-lettering-width-copy-sensitivity-r1.json",
        "docs/research/evidence/ch05-outside-art-lettering-band-r1.json",
        "docs/research/evidence/ch05-continuity-style-density-r1.json",
    }
    observed = set(evidence.get("generation", [])) | set(evidence.get("lettering", [])) | {evidence.get("cadence"), evidence.get("continuity_style_density")}
    if observed != expected or any(not (ROOT / path).is_file() for path in observed):
        out.append("latest evidence coverage invalid")
    if evidence.get("human_accepted_candidates") != 0 or evidence.get("human_accepted_lettering_treatments") != 0:
        out.append("acceptance fabricated")
    return sorted(set(out))


def main() -> int:
    records = [json.loads(path.read_text(encoding="utf-8")) for path in PATHS]
    failures = semantic_errors(records)
    mutations = [
        lambda d: d.pop(), lambda d: d[1].update(record_id="wrong"), lambda d: d[2].update(medium="animation"),
        lambda d: d[3].update(animation_shot_plan={}), lambda d: d[4]["supersedes"].update(sha256="0" * 64),
        lambda d: d[5]["supersedes"].update(record_id="wrong"), lambda d: d[6].update(e_conte={}),
        lambda d: d[8]["evidence"].update(human_accepted_candidates=1),
        lambda d: d[8].update(state="ACCEPTED"), lambda d: d[8]["evidence"]["generation"].pop(),
        lambda d: d[8]["evidence"].update(human_accepted_lettering_treatments=1)
    ]
    rejected = 0
    for mutation in mutations:
        changed = copy.deepcopy(records); mutation(changed); rejected += bool(semantic_errors(changed))
    if rejected != len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 style direction lineage: {len(failures)} failures; 9 append-only revisions/7 current evidence records; {rejected}/{len(mutations)} mutations rejected")
    print("latest r9 role-aware cel/clear-line route; owner accepted candidates/lettering 0/0; AnimationShotPlan/E-Conte null")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
