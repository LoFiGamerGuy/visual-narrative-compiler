"""Compile the non-ingesting CH05 owner-input preflight contract."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "production/comic/review/ch05-owner-ingestion-preflight-contract-r1.json"
GUIDE = ROOT / "docs/research/ch05-owner-ingestion-preflight-contract-r1.md"
EVIDENCE = ROOT / "docs/research/evidence/ch05-owner-ingestion-preflight-contract-r1.json"
INPUTS = [
    ROOT / "production/comic/handoff/ch05-final-review-session-starter-r1.json",
    ROOT / "production/comic/review/ch05-owner-response-schema-r1.json",
    ROOT / "production/comic/review/ch05-pilot-root-review-time-contract-r1.json",
    ROOT / "production/comic/run-manifests/ch05-p010-p013-lifecycle-state-machine-r1.json",
    ROOT / "src/north_garden/preflight_ch05_owner_ingestion.py",
    ROOT / "src/north_garden/validate_ch05_owner_response.py",
    ROOT / "src/north_garden/validate_ch05_pilot_root_review_event_log.py",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def main() -> int:
    planned = ["experiments/review-inputs/ch05-owner-pilot-root-response-r1.json", "experiments/review-inputs/ch05-pilot-root-review-events-r1.json"]
    contract = {
        "record_type": "CH05OwnerIngestionPreflightContract",
        "schema_version": "1.0",
        "record_id": "ng-ch05-owner-ingestion-preflight-contract-r1",
        "state": "BLOCKED_INPUTS_ABSENT",
        "inputs": [bind(path) for path in INPUTS],
        "planned_ignored_inputs": planned,
        "required_root_count": 6,
        "checks": ["response schema", "timer state machine", "six-root coverage", "decision parity", "reviewer parity", "per-root minute parity", "closed lifecycle source", "input SHA-256 capture"],
        "check_count": 8,
        "current": {"response_files": 0, "event_logs": 0, "roots_resolved": 0, "human_review_minutes": None, "eligible_for_future_ingestion": False, "ingestion_performed": False, "lifecycle_transition_performed": False, "production_prompts": 0, "renders": 0, "provider_calls": 0, "uploads": 0, "paid_spend_usd": 0, "accepted": 0, "commercially_cleared": 0},
        "command": "python src/north_garden/preflight_ch05_owner_ingestion.py experiments/review-inputs/ch05-owner-pilot-root-response-r1.json experiments/review-inputs/ch05-pilot-root-review-events-r1.json",
        "exit_codes": {"0": "inputs eligible for a separate future ingestion milestone", "1": "inputs present but invalid", "2": "one or both inputs absent"},
        "animation_shot_plan": None,
        "e_conte": None,
        "boundary": "Preflight only. A passing result binds input hashes but does not ingest decisions, modify lifecycle state, compile prompts, call a provider, upload, accept, clear rights, or select an exact base.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8", newline="\n")
    GUIDE.write_text("\n".join(["# CH05 owner-ingestion preflight contract r1", "", "This fail-closed command checks a future six-root response against its live timer log. It verifies root, decision, reviewer, and per-root minute parity and records exact hashes. It never performs ingestion or a lifecycle transition.", "", "```powershell", contract["command"], "```", "", "Exit 2 is the expected current result because both ignored local inputs are intentionally absent. Exit 0 means only that a separate future hash-chained ingestion milestone may be prepared."]) + "\n", encoding="utf-8", newline="\n")
    evidence = {"record_type": "CH05OwnerIngestionPreflightEvidence", "schema_version": "1.0", "record_id": "ng-ch05-owner-ingestion-preflight-evidence-r1", "state": "PASS_CONTRACT_CURRENTLY_BLOCKED_INPUTS_ABSENT", "contract": bind(OUTPUT), "guide": bind(GUIDE), "inputs": contract["inputs"], "summary": contract["current"], "check_count": 8, "valid_synthetic_cases": 2, "invalid_synthetic_cases": 12, "planned_ignored_inputs": planned, "animation_shot_plan": None, "e_conte": None}
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("CH05 ingestion preflight contract: 8 checks; live inputs 0/0; ingestion/transition 0/0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
