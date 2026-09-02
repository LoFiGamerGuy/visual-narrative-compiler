"""Validate measured CH05 route recommendation, style r10, and decision matrix."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-route-recommendation-and-review-matrix-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(record: dict) -> list[str]:
    summary = record.get("summary", {})
    failures = []
    expected = (4, 4, 10, 29, 26, 14, 50)
    actual = tuple(summary.get(key) for key in ("styles", "role_allocations", "decisions", "candidate_count", "ch05_candidate_count", "selected", "plans"))
    if actual != expected or record.get("state") != "PASS_OWNER_REVIEW_PENDING":
        failures.append("recommendation denominator/state invalid")
    zero = ("owner_decisions", "accepted_candidates", "prompts", "executable_rows", "provider_calls", "uploads", "cost_usd")
    if any(summary.get(key) != 0 for key in zero) or summary.get("human_review_minutes") is not None:
        failures.append("decision/activity/promotion fabricated")
    if record.get("review_links") != {"unique_artifacts": 99, "strongest_candidates": 14}:
        failures.append("review link denominator invalid")
    return failures


def main() -> int:
    record = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures = errors(record)
    for item in record["outputs"] + record["source_bindings"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            failures.append(f"binding invalid: {item['path']}")
    route = json.loads((ROOT / record["outputs"][0]["path"]).read_text(encoding="utf-8"))
    matrix = json.loads((ROOT / record["outputs"][1]["path"]).read_text(encoding="utf-8"))
    style = json.loads((ROOT / record["outputs"][2]["path"]).read_text(encoding="utf-8"))
    measured = route.get("measured_basis", {})
    if route.get("not_based_on") != "visual appeal alone" or len(route.get("role_allocation", [])) != 4:
        failures.append("route basis/allocation invalid")
    if (measured.get("candidate_count"), measured.get("ch05_candidate_count"), measured.get("selected_sequence_count"), measured.get("comic_panel_plan_count"), measured.get("observed_generation_seconds"), measured.get("reference_uses")) != (29, 26, 14, 50, 1385.036, 39):
        failures.append("measured basis invalid")
    if route.get("owner_acceptance") is not False or route.get("commercial_clearance") is not False or route.get("exact_production_base_selected") is not False:
        failures.append("route promotion invalid")
    if matrix.get("decision_count") != 10 or len(matrix.get("decisions", [])) != 10 or any(row.get("owner_decision") is not None or row.get("reviewer") is not None or row.get("human_review_minutes") is not None for row in matrix.get("decisions", [])):
        failures.append("decision matrix state invalid")
    if matrix.get("prompt_count") != 0 or matrix.get("executable_rows") != 0 or matrix.get("comic_panel_plan_revision_created") is not False or matrix.get("animation_shot_plan") is not None or matrix.get("e_conte") is not None:
        failures.append("planning/execution boundary invalid")
    if style.get("supersedes", {}).get("record_id") != "ng-comic-style-ch05-mill-signal-r9" or style.get("animation_shot_plan") is not None or style.get("e_conte") is not None:
        failures.append("style lineage/planning boundary invalid")
    mutations = [
        lambda x: x.update(state="FAIL"),
        lambda x: x["summary"].update(styles=3),
        lambda x: x["summary"].update(role_allocations=3),
        lambda x: x["summary"].update(decisions=9),
        lambda x: x["summary"].update(candidate_count=28),
        lambda x: x["summary"].update(ch05_candidate_count=25),
        lambda x: x["summary"].update(selected=13),
        lambda x: x["summary"].update(plans=49),
        lambda x: x["summary"].update(owner_decisions=1),
        lambda x: x["summary"].update(accepted_candidates=1),
        lambda x: x["summary"].update(prompts=1),
        lambda x: x["summary"].update(executable_rows=1),
        lambda x: x["summary"].update(provider_calls=1),
        lambda x: x["summary"].update(uploads=1),
        lambda x: x["summary"].update(cost_usd=1),
        lambda x: x["summary"].update(human_review_minutes=1),
        lambda x: x.update(review_links={"unique_artifacts": 98, "strongest_candidates": 14}),
    ]
    rejected = 0
    for mutation in mutations:
        candidate = copy.deepcopy(record)
        mutation(candidate)
        rejected += bool(errors(candidate))
    if rejected != len(mutations):
        failures.append(f"only {rejected}/{len(mutations)} mutations rejected")
    print(f"CH05 route recommendation/matrix: {len(failures)} failures; 4 styles/4 allocations/10 decisions; {rejected}/{len(mutations)} mutations rejected")
    print("29 candidates/50 plans/99 links; owner decisions/accepted/prompts/executable/calls/uploads/cost 0/0/0/0/0/0/$0")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
