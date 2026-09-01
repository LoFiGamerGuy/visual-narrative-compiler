"""Validate the append-only CH05 production cost-ledger r3 revision."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
R2 = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r2.json"
R3 = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r3.json"


class LedgerError(RuntimeError): pass


def require(value: bool, message: str) -> None:
    if not value: raise LedgerError(message)


def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def entry(milestone: str) -> dict: return {"milestone": milestone, "external_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"}


def build() -> dict:
    prior = json.loads(R2.read_text(encoding="utf-8"))
    appended = [entry(name) for name in ("exact_base_boundary_measurement_packet_r1", "hash_chained_seam_review_binding_r1", "repair_outcome_finalizer_fail_closed_r1")]
    combined = prior["local_zero_external_cost_evidence"] + appended
    return {
        "record_type": "ProductionCostLedger", "schema_version": "1.2", "record_id": "ng-ch05-production-cost-ledger-r3",
        "supersedes": {"record_id": prior["record_id"], "path": R2.relative_to(ROOT).as_posix(), "sha256": sha256(R2)},
        "prior_record_rewritten": False, "budget_domain": prior["budget_domain"], "policy_id": prior["policy_id"], "state": prior["state"],
        "approved_aggregate_cap_usd": None, "committed_actual_cost_usd": "0.000000", "held_reservations_usd": "0.000000", "available_usd": None,
        "currency": "USD", "entries": [], "local_zero_external_cost_evidence": combined,
        "revision_summary": {"prior_local_milestones": len(prior["local_zero_external_cost_evidence"]), "appended_local_milestones": len(appended), "total_local_milestones": len(combined), "external_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"},
        "boundary": "Append-only revision. CH05 production remains disabled/no-cap/$0; G07 capacity is a separate prohibited domain.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    values = []
    item = copy.deepcopy(expected); item["supersedes"]["sha256"] = "0" * 64; values.append(item)
    item = copy.deepcopy(expected); item["prior_record_rewritten"] = True; values.append(item)
    item = copy.deepcopy(expected); item["state"] = "ENABLED"; values.append(item)
    item = copy.deepcopy(expected); item["approved_aggregate_cap_usd"] = "1.000000"; values.append(item)
    item = copy.deepcopy(expected); item["entries"] = [{}]; values.append(item)
    item = copy.deepcopy(expected); item["local_zero_external_cost_evidence"][-1]["external_uploads"] = 1; values.append(item)
    item = copy.deepcopy(expected); item["revision_summary"]["appended_local_milestones"] = 2; values.append(item)
    item = copy.deepcopy(expected); item["available_usd"] = "98.942623"; values.append(item)
    return sum(value != expected for value in values), len(values)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--emit", type=Path); args = parser.parse_args()
    try:
        expected = build()
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else: require(json.loads(R3.read_text(encoding="utf-8")) == expected, "tracked r3 differs")
        rejected, total = mutations(expected); require(rejected == total, "mutation rejection incomplete")
        require(len({item["milestone"] for item in expected["local_zero_external_cost_evidence"]}) == expected["revision_summary"]["total_local_milestones"], "duplicate milestone")
    except (LedgerError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr); return 1
    print(f"0 failures, 0 warnings ({expected['revision_summary']['total_local_milestones']} zero-cost milestones; 0 requests/uploads/$0; {rejected}/{total} mutations rejected)")
    return 0


if __name__ == "__main__": raise SystemExit(main())
