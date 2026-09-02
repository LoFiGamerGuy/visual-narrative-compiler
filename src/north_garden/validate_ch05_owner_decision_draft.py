"""Validate an exported CH05 owner-decision draft without ingesting or writing it."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "production/comic/review/ch05-owner-decision-contract-r1.json"
ALLOWED_TOP_LEVEL = {
    "record_type", "schema_version", "state", "contract_id", "contract_sha256",
    "reviewer", "decisions", "boundary",
}
ALLOWED_DECISION_FIELDS = {"subject_id", "subject_type", "decision", "notes"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_draft(draft: Any, contract: dict[str, Any], contract_sha256: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(draft, dict):
        return ["draft must be a JSON object"]
    extra = sorted(set(draft) - ALLOWED_TOP_LEVEL)
    if extra:
        errors.append(f"unsupported top-level fields: {','.join(extra)}")
    expected = {
        "record_type": "ComicOwnerDecisionDraft",
        "schema_version": "1.0",
        "state": "LOCAL_UNINGESTED_DRAFT",
        "contract_id": contract["record_id"],
        "contract_sha256": contract_sha256,
    }
    for field, value in expected.items():
        if draft.get(field) != value:
            errors.append(f"{field} mismatch")
    reviewer = draft.get("reviewer")
    if reviewer is not None and (not isinstance(reviewer, str) or not reviewer.strip() or len(reviewer) > 160):
        errors.append("reviewer must be null or a nonempty string of at most 160 characters")
    decisions = draft.get("decisions")
    if not isinstance(decisions, list):
        return errors + ["decisions must be a list"]
    subjects = {item["subject_id"]: item for item in contract["subjects"]}
    seen: set[str] = set()
    decisive = 0
    for index, item in enumerate(decisions):
        label = f"decisions[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        item_extra = sorted(set(item) - ALLOWED_DECISION_FIELDS)
        if item_extra:
            errors.append(f"{label} unsupported fields: {','.join(item_extra)}")
        subject_id = item.get("subject_id")
        if not isinstance(subject_id, str) or subject_id not in subjects:
            errors.append(f"{label} unknown subject_id")
            continue
        if subject_id in seen:
            errors.append(f"{label} duplicate subject_id")
        seen.add(subject_id)
        subject = subjects[subject_id]
        if item.get("subject_type") != subject["subject_type"]:
            errors.append(f"{label} subject_type mismatch")
        decision = item.get("decision")
        notes = item.get("notes")
        if decision is not None:
            decisive += 1
            if decision not in subject["allowed_decisions"]:
                errors.append(f"{label} decision not allowed for subject")
        if notes is not None and (not isinstance(notes, str) or len(notes) > 4000):
            errors.append(f"{label} notes must be null or at most 4000 characters")
        if decision is None and (notes is None or not isinstance(notes, str) or not notes.strip()):
            errors.append(f"{label} contains neither decision nor notes")
    if decisive and (not isinstance(reviewer, str) or not reviewer.strip()):
        errors.append("reviewer required when any decision is selected")
    boundary = draft.get("boundary")
    if not isinstance(boundary, str) or "not a hash-chained event" not in boundary:
        errors.append("draft boundary is missing or weakened")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", type=Path)
    args = parser.parse_args()
    contract_before = sha256(CONTRACT_PATH)
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    try:
        draft = json.loads(args.draft.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}")
        return 1
    failures = validate_draft(draft, contract, contract_before)
    if sha256(CONTRACT_PATH) != contract_before:
        failures.append("contract changed during read-only validation")
    print(f"CH05 owner decision draft: {'VALID_LOCAL_DRAFT_NOT_INGESTED' if not failures else 'INVALID'}; {len(failures)} failures")
    print("read-only: no event, acceptance, review time, plan revision, repository write, or generation authority")
    for failure in failures:
        print(f"FAIL: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
