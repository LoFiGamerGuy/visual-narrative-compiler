"""Exercise the CH05 decision-draft validator with synthetic fixtures and export evidence."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from validate_ch05_owner_decision_draft import CONTRACT_PATH, ROOT, sha256, validate_draft


OUTPUT = ROOT / "docs/research/evidence/ch05-owner-decision-draft-validator-r1.json"
BOUNDARY = "Draft export only; not a hash-chained event, acceptance, plan revision, or project state."


def canonical(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    contract_sha = sha256(CONTRACT_PATH)
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    subject = contract["subjects"][0]
    valid = {
        "record_type": "ComicOwnerDecisionDraft", "schema_version": "1.0",
        "state": "LOCAL_UNINGESTED_DRAFT", "contract_id": contract["record_id"],
        "contract_sha256": contract_sha, "reviewer": "synthetic-validator-fixture",
        "decisions": [{"subject_id": subject["subject_id"], "subject_type": subject["subject_type"],
                       "decision": subject["allowed_decisions"][0], "notes": "Synthetic only; not an owner decision."}],
        "boundary": BOUNDARY,
    }
    cases = []

    def mutate(case_id: str, fn) -> None:
        candidate = copy.deepcopy(valid)
        fn(candidate)
        failures = validate_draft(candidate, contract, contract_sha)
        cases.append({"case_id": case_id, "expected": "REJECT", "result": "REJECT" if failures else "ACCEPT",
                      "failure_count": len(failures), "failure_categories": failures})

    mutate("wrong_record_type", lambda x: x.update(record_type="ComicOwnerDecisionEvent"))
    mutate("wrong_schema", lambda x: x.update(schema_version="2.0"))
    mutate("wrong_state", lambda x: x.update(state="INGESTED"))
    mutate("wrong_contract_id", lambda x: x.update(contract_id="wrong"))
    mutate("wrong_contract_hash", lambda x: x.update(contract_sha256="0" * 64))
    mutate("unknown_subject", lambda x: x["decisions"][0].update(subject_id="unknown"))
    mutate("duplicate_subject", lambda x: x["decisions"].append(copy.deepcopy(x["decisions"][0])))
    mutate("wrong_subject_type", lambda x: x["decisions"][0].update(subject_type="NONCANON_CONCEPT"))
    mutate("decision_outside_vocabulary", lambda x: x["decisions"][0].update(decision="ACCEPT_AS_EXACT_PRODUCTION_BASE"))
    mutate("missing_reviewer", lambda x: x.update(reviewer=None))
    mutate("fabricated_review_time", lambda x: x.update(active_minutes=1))
    mutate("event_hash_field", lambda x: x["decisions"][0].update(event_sha256="0" * 64))
    mutate("empty_entry", lambda x: x["decisions"][0].update(decision=None, notes=None))
    mutate("weakened_boundary", lambda x: x.update(boundary="Ready for ingestion."))
    valid_cases = [
        ("empty_export", {**valid, "reviewer": None, "decisions": []}),
        ("notes_only", {**valid, "reviewer": None, "decisions": [{"subject_id": subject["subject_id"], "subject_type": subject["subject_type"], "decision": None, "notes": "Compare hand pose."}]}),
        ("one_synthetic_decision", valid),
    ]
    valid_results = [{"case_id": name, "result": "ACCEPT_AS_LOCAL_DRAFT" if not validate_draft(value, contract, contract_sha) else "REJECT"} for name, value in valid_cases]
    rejected = sum(item["result"] == "REJECT" for item in cases)
    if rejected != len(cases) or any(item["result"] != "ACCEPT_AS_LOCAL_DRAFT" for item in valid_results):
        raise SystemExit("draft validator fixture matrix failed")
    if sha256(CONTRACT_PATH) != contract_sha or contract["event_contract"]["events"] or contract["summary"]["completed_decisions"]:
        raise SystemExit("contract state changed")
    evidence = {
        "record_type": "CH05OwnerDecisionDraftValidatorEvidence", "schema_version": "1.0",
        "record_id": "ng-ch05-owner-decision-draft-validator-evidence-r1",
        "state": "READ_ONLY_VALIDATOR_READY_CONTRACT_UNCHANGED",
        "validator": {"path": "src/north_garden/validate_ch05_owner_decision_draft.py",
                      "sha256": sha256(ROOT / "src/north_garden/validate_ch05_owner_decision_draft.py")},
        "contract": {"path": CONTRACT_PATH.relative_to(ROOT).as_posix(), "sha256": contract_sha,
                     "subject_count": 39, "completed_decisions": 0, "events": 0, "human_review_minutes": None},
        "fixture_matrix": {"valid_fixture_count": len(valid_results), "valid_results": valid_results,
                           "negative_fixture_count": len(cases), "negative_rejected": rejected,
                           "negative_results": cases, "matrix_root_sha256": canonical({"valid": valid_results, "negative": cases})},
        "activity": {"owner_drafts_read": 0, "events_created": 0, "contract_writes": 0, "plan_revisions": 0,
                     "provider_calls": 0, "uploads": 0, "external_cost_usd": 0},
        "limitations": ["Synthetic fixtures prove schema rejection behavior, not owner review completion.",
                        "A valid local draft is still not an event and cannot update project state.",
                        "Event timestamp, active-minute, reviewer-attestation, and hash-chain construction remain a separate explicit operation."],
        "boundary": "Validation is read-only and never ingests, promotes, accepts, revises, uploads, or executes a draft.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(evidence, indent=2) + "\n")
    print(f"CH05 owner decision draft validator: 3/3 valid local fixtures; {rejected}/{len(cases)} negative fixtures rejected")
    print(f"contract unchanged: 39 subjects / 0 decisions / 0 events / null minutes; evidence {sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
