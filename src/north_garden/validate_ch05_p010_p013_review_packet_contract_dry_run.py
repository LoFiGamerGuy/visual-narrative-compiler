"""Validate fail-closed P010-P013 review-packet contract dry run."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-p010-p013-review-packet-contract-dry-run-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(record: dict) -> list[str]:
    summary = record.get("summary", {})
    expected = (4, 11, 5, 0, 0, 0, 0, 0)
    actual = tuple(summary.get(key) for key in ("candidate_slots", "required_checks_per_candidate", "planned_artifacts", "built_artifacts", "completed_candidate_reviews", "sequence_decisions", "repair_slots_allocated", "accepted_candidates"))
    failures = []
    if actual != expected or record.get("state") != "PASS_FAIL_CLOSED":
        failures.append("review denominator/state invalid")
    if any(summary.get(key) != 0 for key in ("provider_calls", "uploads", "cost_usd")) or summary.get("human_review_minutes") is not None:
        failures.append("activity/review fabricated")
    if record.get("failure_vocabulary_count") != 11 or record.get("promotion_rule_count") != 5:
        failures.append("failure/promotion denominator invalid")
    if record.get("animation_shot_plan") is not None or record.get("e_conte") is not None:
        failures.append("planning boundary invalid")
    return failures


def main() -> int:
    record = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures = errors(record)
    contract_path = ROOT / record["contract"]["path"]
    if not contract_path.is_file() or sha(contract_path) != record["contract"]["sha256"]:
        failures.append("contract binding invalid")
        contract = {}
    else:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    for item in record["inputs"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            failures.append(f"input binding invalid: {item['path']}")
    reviews = contract.get("candidate_reviews", [])
    required = contract.get("required_checks", [])
    if len(reviews) != 4 or len(required) != 11 or any(set(row.get("checks", {})) != set(required) for row in reviews):
        failures.append("candidate/check coverage invalid")
    if any(any(value is not None for value in row.get("checks", {}).values()) or row.get("output_sha256") is not None or row.get("source_dimensions") is not None or row.get("phone_preview_dimensions") is not None or row.get("failure_classes") != [] or row.get("repair_slot") is not None or row.get("reviewer") is not None or row.get("human_review_minutes") is not None or row.get("decision") is not None for row in reviews):
        failures.append("candidate review state not empty")
    artifacts = contract.get("planned_artifacts", [])
    if len(artifacts) != 5 or any(item.get("state") != "NOT_BUILT" or item.get("path") is not None or item.get("sha256") is not None or item.get("dimensions") is not None for item in artifacts):
        failures.append("planned artifact state invalid")
    sequence = contract.get("sequence_review", {})
    if any(value is not None for value in sequence.values()):
        failures.append("sequence review fabricated")
    repair = contract.get("repair_allocation", {})
    if repair != {"maximum_slots": 2, "allocated_slots": 0, "broad_reroll": False, "passing_rows_must_be_preserved": True}:
        failures.append("repair boundary invalid")
    if contract.get("comic_panel_plan_revision_created") is not False or contract.get("animation_shot_plan") is not None or contract.get("e_conte") is not None:
        failures.append("contract planning boundary invalid")
    mutations = [
        lambda x: x.update(state="FAIL"),
        lambda x: x["summary"].update(candidate_slots=3),
        lambda x: x["summary"].update(required_checks_per_candidate=10),
        lambda x: x["summary"].update(planned_artifacts=4),
        lambda x: x["summary"].update(built_artifacts=1),
        lambda x: x["summary"].update(completed_candidate_reviews=1),
        lambda x: x["summary"].update(sequence_decisions=1),
        lambda x: x["summary"].update(repair_slots_allocated=1),
        lambda x: x["summary"].update(accepted_candidates=1),
        lambda x: x["summary"].update(provider_calls=1),
        lambda x: x["summary"].update(uploads=1),
        lambda x: x["summary"].update(cost_usd=1),
        lambda x: x["summary"].update(human_review_minutes=1),
        lambda x: x.update(failure_vocabulary_count=10),
        lambda x: x.update(promotion_rule_count=4),
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
    print(f"CH05 P010-P013 review contract: {len(failures)} failures; 4 slots/11 checks/5 artifacts/11 failure classes; {rejected}/{len(mutations)} mutations rejected")
    print("pixels/reviews/decisions/repairs/accepted/calls/uploads/cost 0/0/0/0/0/0/0/$0")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
