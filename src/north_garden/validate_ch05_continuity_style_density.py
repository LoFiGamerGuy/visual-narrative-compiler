"""Validate CH05 style/density diagnostics and prevent identity/acceptance overclaims."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "experiments/review-packets/ch05-continuity-style-density-r1/continuity-style-density-packet.json"
REVIEW = ROOT / "production/comic/review/ch05-continuity-style-density-review-r1.json"
EVIDENCE = ROOT / "docs/research/evidence/ch05-continuity-style-density-r1.json"


EXPECTED_STYLE = {
    "cel_painted": {"pass": 5, "warn": 0, "fail": 1},
    "clear_line_watercolor": {"pass": 5, "warn": 2, "fail": 1},
    "limited_ink_flat": {"pass": 4, "warn": 1, "fail": 1},
    "clean_graphic": {"pass": 3, "warn": 0, "fail": 3},
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_errors(data: dict) -> list[str]:
    out = []
    summary = data.get("summary", {})
    actual = tuple(summary.get(field) for field in ("selected_candidate_count", "style_triage_candidate_count", "style_count", "sequence_count", "adjacent_pair_count", "artifact_count"))
    if actual != (14, 26, 4, 3, 13, 4): out.append("denominator invalid")
    if summary.get("accepted_candidates") != 0 or summary.get("human_review_minutes") is not None:
        out.append("acceptance/review fabricated")
    if summary.get("provider_calls") != 0 or summary.get("uploads") != 0 or summary.get("cost_usd") != 0:
        out.append("external activity fabricated")
    if data.get("comic_panel_plan_revision_created") is not False or data.get("assembly_revision_created") is not False or data.get("animation_shot_plan") is not None or data.get("e_conte") is not None:
        out.append("planning boundary invalid")
    if data.get("style_engineering_results_all_26") != EXPECTED_STYLE:
        out.append("style triage counts invalid")
    jump = data.get("max_adjacent_jump", {})
    if (jump.get("from_candidate"), jump.get("to_candidate"), jump.get("distance"), jump.get("sequence_break")) != ("c014", "c015", 5.6517, False):
        out.append("max jump invalid")
    records = data.get("selected_records", [])
    if len(records) != 14 or len({item.get("candidate_id") for item in records}) != 14:
        out.append("selected record coverage invalid")
    return sorted(set(out))


def main() -> int:
    packet = json.loads(PACKET.read_text(encoding="utf-8")); review = json.loads(REVIEW.read_text(encoding="utf-8")); evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures = semantic_errors(evidence)
    if sha(PACKET) != evidence["local_packet"]["sha256"] or sha(REVIEW) != evidence["engineering_review"]["sha256"]:
        failures.append("packet/review binding mismatch")
    if "cannot detect identity" not in evidence["limitations"][0] or review["accepted_candidates"] != 0:
        failures.append("identity/acceptance boundary missing")
    for item in evidence["artifacts"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            failures.append(f"artifact mismatch: {item['path']}")
        elif subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=ROOT, check=False).returncode:
            failures.append(f"artifact not ignored: {item['path']}")
    mutations = [
        lambda d: d["summary"].update(selected_candidate_count=13), lambda d: d["summary"].update(style_triage_candidate_count=25),
        lambda d: d["summary"].update(style_count=3), lambda d: d["summary"].update(sequence_count=2),
        lambda d: d["summary"].update(adjacent_pair_count=12), lambda d: d["summary"].update(artifact_count=3),
        lambda d: d["summary"].update(accepted_candidates=1), lambda d: d["summary"].update(provider_calls=1),
        lambda d: d["style_engineering_results_all_26"]["cel_painted"].update(pass_=6),
        lambda d: d["max_adjacent_jump"].update(distance=1.0), lambda d: d["selected_records"].pop(),
        lambda d: d.update(animation_shot_plan={})
    ]
    rejected = 0
    for mutation in mutations:
        changed = copy.deepcopy(evidence); mutation(changed); rejected += bool(semantic_errors(changed))
    if rejected != len(mutations): failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 continuity/style/density: {len(failures)} failures; 14 selected/26 triage/4 styles/13 jumps/4 artifacts; {rejected}/{len(mutations)} mutations rejected")
    print("max appearance jump c014->c015 5.6517; manual hair/wardrobe pass remains separate; 0 accepted/calls/uploads/$0")
    for failure in failures: print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
