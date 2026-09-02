"""Validate the CH05 owner-ingestion preflight contract and adversarial behavior."""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from preflight_ch05_owner_ingestion import preflight

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/ch05-owner-ingestion-preflight-contract-r1.json"
TEMPLATE = ROOT / "production/comic/review/ch05-owner-response-template-r1.json"
TIMER = ROOT / "production/comic/review/ch05-pilot-root-review-time-contract-r1.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_errors(document: dict) -> list[str]:
    summary = document.get("summary", {})
    expected = (0, 0, 0, None, False, False, False, 0, 0, 0, 0, 0, 0, 0)
    keys = ("response_files", "event_logs", "roots_resolved", "human_review_minutes", "eligible_for_future_ingestion", "ingestion_performed", "lifecycle_transition_performed", "production_prompts", "renders", "provider_calls", "uploads", "paid_spend_usd", "accepted", "commercially_cleared")
    out = []
    if document.get("state") != "PASS_CONTRACT_CURRENTLY_BLOCKED_INPUTS_ABSENT" or tuple(summary.get(key) for key in keys) != expected:
        out.append("state/current summary invalid")
    if document.get("check_count") != 8 or document.get("valid_synthetic_cases") != 2 or document.get("invalid_synthetic_cases") != 12:
        out.append("test/check denominators invalid")
    if document.get("animation_shot_plan") is not None or document.get("e_conte") is not None:
        out.append("planning boundary invalid")
    return out


def fixtures() -> tuple[dict, dict]:
    response = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    response.update(state="OWNER_RESPONSE_COMPLETE_NOT_INGESTED", valid_for_ingestion=True)
    timer = json.loads(TIMER.read_text(encoding="utf-8"))
    start = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
    events = []
    for index, row in enumerate(response["decisions"]):
        root_id = row["decision_id"]
        row.update(owner_decision=row["recommended_value"], reviewer="synthetic-owner", human_review_minutes=1.0)
        when = start + timedelta(minutes=index * 2)
        events.extend([
            {"event_id": f"synthetic-{index}-start", "subject_id": root_id, "event_type": "REVIEW_STARTED", "reviewer": "synthetic-owner", "occurred_at_utc": when.isoformat().replace("+00:00", "Z"), "active_delta_seconds": None, "decision": None},
            {"event_id": f"synthetic-{index}-complete", "subject_id": root_id, "event_type": "REVIEW_COMPLETED", "reviewer": "synthetic-owner", "occurred_at_utc": (when + timedelta(minutes=1)).isoformat().replace("+00:00", "Z"), "active_delta_seconds": 60.0, "decision": row["owner_decision"]},
        ])
    event_log = {"record_type": "ComicPilotRootReviewTimeEventLog", "schema_version": "1.0", "record_id": "synthetic-valid-six-root-log", "contract_record_id": timer["record_id"], "contract_sha256": sha(TIMER), "capture_mode": "LIVE_TIMER_ONLY", "events": events}
    return response, event_log


def run_case(folder: Path, response: dict, event_log: dict) -> dict:
    response_path, log_path = folder / "response.json", folder / "events.json"
    response_path.write_text(json.dumps(response, indent=2) + "\n", encoding="utf-8")
    log_path.write_text(json.dumps(event_log, indent=2) + "\n", encoding="utf-8")
    return preflight(response_path, log_path)


def main() -> int:
    document = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    failures = evidence_errors(document)
    for key in ("contract", "guide"):
        path = ROOT / document[key]["path"]
        if not path.is_file() or sha(path) != document[key]["sha256"]:
            failures.append(f"binding invalid: {key}")
    for item in document["inputs"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            failures.append(f"input invalid: {item['path']}")
    absent = preflight(ROOT / document["planned_ignored_inputs"][0], ROOT / document["planned_ignored_inputs"][1])
    if absent["state"] != "BLOCKED_INPUTS_ABSENT" or absent["eligible_for_future_ingestion"]:
        failures.append("absent mode did not fail closed")

    response, event_log = fixtures()
    rejected = 0
    with tempfile.TemporaryDirectory(dir=ROOT / "experiments", prefix="ch05-preflight-") as raw:
        folder = Path(raw)
        valid = run_case(folder, response, event_log)
        second = run_case(folder, copy.deepcopy(response), copy.deepcopy(event_log))
        if not valid["eligible_for_future_ingestion"] or valid["root_parity_count"] != 6 or valid["ingestion_performed"] or valid["lifecycle_transition_performed"]:
            failures.append("valid synthetic case failed or expanded authority")
        if valid != second:
            failures.append("valid replay is not deterministic")
        mutations = []
        def add(mutator):
            r, e = copy.deepcopy(response), copy.deepcopy(event_log); mutator(r, e); mutations.append((r, e))
        add(lambda r, e: r["decisions"][0].update(owner_decision=r["decisions"][0]["allowed_values"][1]))
        add(lambda r, e: r["decisions"][0].update(reviewer="other-reviewer"))
        add(lambda r, e: r["decisions"][0].update(human_review_minutes=2.0))
        add(lambda r, e: r["decisions"].pop())
        add(lambda r, e: e["events"].pop())
        add(lambda r, e: e["events"][1].update(decision="INVALID"))
        add(lambda r, e: e["events"][1].update(event_type="REVIEW_PAUSED"))
        add(lambda r, e: e["events"][1].update(event_id=e["events"][0]["event_id"]))
        add(lambda r, e: r.update(state="UNFILLED_TEMPLATE"))
        add(lambda r, e: r.update(candidate_acceptance="ACCEPT"))
        add(lambda r, e: e["events"][1].update(occurred_at_utc="2026-09-01T11:59:00Z"))
        add(lambda r, e: e.update(contract_sha256="0" * 64))
        for mutated_response, mutated_log in mutations:
            rejected += not run_case(folder, mutated_response, mutated_log)["eligible_for_future_ingestion"]
    if rejected != 12:
        failures.append(f"only {rejected}/12 malformed input cases rejected")

    evidence_mutations = [lambda x: x.update(state="FAIL"), lambda x: x.update(check_count=7), lambda x: x.update(valid_synthetic_cases=1), lambda x: x.update(invalid_synthetic_cases=11), lambda x: x.update(animation_shot_plan={})]
    for key in ("response_files", "event_logs", "roots_resolved", "human_review_minutes", "eligible_for_future_ingestion", "ingestion_performed", "lifecycle_transition_performed", "production_prompts", "renders", "provider_calls", "uploads", "paid_spend_usd", "accepted", "commercially_cleared"):
        evidence_mutations.append(lambda x, key=key: x["summary"].update({key: 1}))
    evidence_rejected = 0
    for mutate in evidence_mutations:
        altered = copy.deepcopy(document); mutate(altered); evidence_rejected += bool(evidence_errors(altered))
    if evidence_rejected != len(evidence_mutations):
        failures.append(f"only {evidence_rejected}/{len(evidence_mutations)} evidence mutations rejected")
    print(f"CH05 ingestion preflight: {len(failures)} failures; 2/2 valid deterministic + {rejected}/12 malformed rejected; {evidence_rejected}/{len(evidence_mutations)} evidence mutations rejected")
    print("live response/log/decisions/minutes/ingestion/transition 0/0/0/null/0/0")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
