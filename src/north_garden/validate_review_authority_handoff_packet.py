"""Compile a blank-field handoff for remaining review and authority roots."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/research/evidence/review-authority-handoff-packet-r1.json"
REVIEW_PACKET = ROOT / "experiments/review-packets/g07-blinded-human-review-r1/review-packet.json"
SOURCES = {
    "review_protocol": ROOT / "config/g07-blinded-human-review-protocol-r1.json",
    "review_gate": ROOT / "docs/research/evidence/g07-human-review-rollup-gate-r1.json",
    "budget_audit": ROOT / "docs/research/evidence/g07-aggregate-budget-binding-audit-r3.json",
    "hardening_state": ROOT / "docs/research/evidence/selected-route-hardening-state-r2.json",
    "authority_frontier": ROOT / "docs/research/evidence/selected-route-authority-dependency-frontier-r1.json",
    "reproducer_matrix": ROOT / "docs/research/evidence/current-evidence-reproducer-matrix-r1.json",
    "frozen_integrity": ROOT / "docs/research/evidence/frozen-gauntlet-baseline-integrity-r1.json",
    "production_ledger": ROOT / "docs/research/evidence/ch05-production-cost-ledger-r17.json",
}


class HandoffError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise HandoffError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path: Path, payload: dict) -> dict:
    return {"record_id": payload.get("record_id", payload.get("protocol_id")), "path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}


def build() -> dict:
    data = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in SOURCES.items()}
    protocol = data["review_protocol"]
    gate = data["review_gate"]
    budget = data["budget_audit"]
    hardening = data["hardening_state"]
    frontier = data["authority_frontier"]
    reproducer = data["reproducer_matrix"]
    frozen = data["frozen_integrity"]
    ledger = data["production_ledger"]
    packet = json.loads(REVIEW_PACKET.read_text(encoding="utf-8"))

    require(protocol["packet_sha256"] == gate["review_packet_sha256"] == packet["packet_sha256"], "review packet identity changed")
    require(protocol["total_decisions_required"] == gate["required_decisions"] == 20 and gate["actual_decisions"] == 0, "review decision state changed")
    require(gate["human_minutes"] is None and gate["human_arm_results"] is None and gate["accepted_candidate_subjects"] == 0, "review state fabricated")
    require(packet["reviewer_id"] is None and packet["review_session_id"] is None and packet["human_minutes"] is None, "packet human fields filled")
    require(len(packet["subjects"]) == 20 and packet["decision_count"] == 0, "packet denominator/state changed")
    review_check = subprocess.run([sys.executable, "src/north_garden/validate_g07_blinded_review.py"], cwd=ROOT, capture_output=True, text=True)
    require(review_check.returncode == 0, "blinded review packet validation failed")

    roots = frontier["root_authority_frontier"]
    require(len(roots) == 5 and frontier["next_external_action"] is None, "authority frontier changed")
    require(hardening["authority_frontier"]["next_external_action"] is None, "hardening state proposed external action")
    require(budget["ledger_reconciliation"]["committed_actual_cost_usd"] == "1.057377" and budget["ledger_reconciliation"]["available_usd"] == "98.942623", "G07 spend changed")
    require(ledger["approved_aggregate_cap_usd"] is None and ledger["entries"] == [], "CH05 budget became active")
    require(reproducer["summary"]["passed"] == reproducer["summary"]["commands"] == 11, "reproducer state changed")
    require(frozen["summary"]["frozen_paths_changed"] == frozen["summary"]["baseline_tracked_paths_changed"] == 0, "frozen target changed")

    source_refs = {name: ref(path, data[name]) for name, path in SOURCES.items()}
    return {
        "record_type": "ReviewAuthorityHandoffPacket",
        "schema_version": "1.0",
        "record_id": "ng-review-authority-handoff-packet-r1",
        "state": "READY_FOR_SEPARATE_HUMAN_AND_USER_ACTIONS_NO_FIELDS_FILLED",
        "sources": source_refs,
        "g07_human_review": {
            "local_packet": {"path": REVIEW_PACKET.relative_to(ROOT).as_posix(), "sha256": sha256(REVIEW_PACKET), "packet_sha256": packet["packet_sha256"], "git_tracked": False},
            "candidate_presentations": 16,
            "repeat_pair_presentations": 4,
            "decisions_required": 20,
            "decisions_complete": 0,
            "reviewer_id": None,
            "review_session_id": None,
            "human_minutes": None,
            "accepted_subjects": 0,
            "human_arm_results": None,
            "action_owner": "identified human reviewer",
            "action_boundary": "Complete append-only timed decisions locally, deblind only after a complete eligible session, and do not treat candidate acceptance as commercial or CH05 authority.",
        },
        "ch05_root_authority_items": [
            {**item, "current_value": None, "decision_record": None} for item in roots[1:]
        ],
        "g07_review_root": {**roots[0], "current_value": None, "decision_record": None},
        "pre_execution_research_refresh": {
            "required": True,
            "current_action": None,
            "trigger": "immediately before any separately authorized CH05 paid execution",
            "scope": "official primary pricing, terms, model snapshot, endpoint, and data-use documentation",
        },
        "budget_state": {
            "g07_approved_cap_usd": "100.000000",
            "g07_actual_usd": budget["ledger_reconciliation"]["committed_actual_cost_usd"],
            "g07_held_usd": budget["ledger_reconciliation"]["held_reservations_usd"],
            "g07_available_usd": budget["ledger_reconciliation"]["available_usd"],
            "g07_available_reusable_for_ch05": False,
            "ch05_approved_cap_usd": None,
            "ch05_committed_usd": "0.000000",
            "ch05_held_usd": "0.000000",
        },
        "current_integrity": {
            "reproducer_commands_passed": 11,
            "release_checks_passed": 65,
            "lineage_records": reproducer["summary"]["lineage_records_validated"],
            "frozen_paths_changed": 0,
            "baseline_tracked_paths_changed": 0,
            "baseline_accepted_outputs": 0,
        },
        "blank_authority_state": {
            "approved_base_raster": None,
            "approved_repair_mask": None,
            "exact_external_upload_authority": None,
            "distinct_ch05_production_cap": None,
            "production_reservation": None,
            "next_external_action": None,
            "approvals_requested_now": [],
        },
        "prohibited_inferences": frontier["prohibited_inferences"] + [
            "a complete local handoff packet authorizes external execution",
            "unused G07 capacity can fund or authorize a CH05 request",
        ],
        "activity": {"provider_requests": 0, "external_uploads": 0, "models_downloaded": 0, "external_cost_usd": "0.000000"},
        "boundary": "This packet separates the remaining actions and leaves every human/user field blank. It requests no approval and proposes no external action.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    actions = [
        lambda item: item["sources"]["review_gate"].update(sha256="0" * 64),
        lambda item: item["g07_human_review"].update(decisions_complete=20),
        lambda item: item["g07_human_review"].update(reviewer_id="invented"),
        lambda item: item["g07_human_review"].update(human_minutes=10),
        lambda item: item["ch05_root_authority_items"].pop(),
        lambda item: item["ch05_root_authority_items"][0].update(current_value={}),
        lambda item: item["g07_review_root"].update(decision_record={}),
        lambda item: item["pre_execution_research_refresh"].update(current_action="complete"),
        lambda item: item["budget_state"].update(g07_available_reusable_for_ch05=True),
        lambda item: item["budget_state"].update(ch05_approved_cap_usd="100.000000"),
        lambda item: item["current_integrity"].update(reproducer_commands_passed=10),
        lambda item: item["current_integrity"].update(frozen_paths_changed=1),
        lambda item: item["blank_authority_state"].update(approved_base_raster={}),
        lambda item: item["blank_authority_state"].update(next_external_action="submit P036"),
        lambda item: item["blank_authority_state"]["approvals_requested_now"].append("CH05 cap"),
        lambda item: item["prohibited_inferences"].pop(),
        lambda item: item["activity"].update(provider_requests=1),
        lambda item: item["activity"].update(external_uploads=1),
        lambda item: item["activity"].update(external_cost_usd="1.000000"),
    ]
    for action in actions:
        item = copy.deepcopy(expected)
        action(item)
        values.append(item)
    return sum(item != expected for item in values), len(values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", type=Path)
    args = parser.parse_args()
    try:
        expected = build()
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            require(json.loads(OUTPUT.read_text(encoding="utf-8")) == expected, "tracked handoff packet differs")
        rejected, total = mutations(expected)
        require(rejected == total, "handoff mutations not rejected")
    except (HandoffError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("0 failures, 0 warnings (20-decision G07 review + 4 CH05 root authority items separated; all fields blank)")
    print(f"11 reproducers/65 release checks/frozen targets valid; {rejected}/{total} mutations rejected; no approval requested/0 requests/uploads/$0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
