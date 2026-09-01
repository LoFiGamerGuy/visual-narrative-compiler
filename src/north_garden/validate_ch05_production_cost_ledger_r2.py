"""Build and validate the append-only CH05 production cost-ledger revision."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
R1 = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r1.json"
R2 = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r2.json"


class LedgerError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LedgerError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_entry(milestone: str) -> dict:
    return {"milestone": milestone, "external_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"}


def build() -> dict:
    prior = json.loads(R1.read_text(encoding="utf-8"))
    appended = [
        local_entry("scale_aware_repair_boundary_selector_contract_r1"),
        local_entry("repair_render_record_boundary_evidence_r2"),
        local_entry("ch05_repair_evidence_readiness_matrix_r1"),
    ]
    combined = prior["local_zero_external_cost_evidence"] + appended
    return {
        "record_type": "ProductionCostLedger", "schema_version": "1.1", "record_id": "ng-ch05-production-cost-ledger-r2",
        "supersedes": {"record_id": prior["record_id"], "path": R1.relative_to(ROOT).as_posix(), "sha256": sha256(R1)},
        "prior_record_rewritten": False, "budget_domain": prior["budget_domain"], "policy_id": prior["policy_id"],
        "state": prior["state"], "approved_aggregate_cap_usd": None, "committed_actual_cost_usd": "0.000000",
        "held_reservations_usd": "0.000000", "available_usd": None, "currency": "USD", "entries": [],
        "local_zero_external_cost_evidence": combined,
        "revision_summary": {"prior_local_milestones": len(prior["local_zero_external_cost_evidence"]), "appended_local_milestones": len(appended), "total_local_milestones": len(combined), "external_requests": 0, "external_uploads": 0, "external_cost_usd": "0.000000"},
        "boundary": "Append-only revision. The disabled CH05 domain has no cap or spend authority; G07 availability cannot fund it.",
    }


def mutations(expected: dict) -> tuple[int, int]:
    changed = []
    item = copy.deepcopy(expected); item["supersedes"]["sha256"] = "0" * 64; changed.append(item)
    item = copy.deepcopy(expected); item["prior_record_rewritten"] = True; changed.append(item)
    item = copy.deepcopy(expected); item["state"] = "ENABLED"; changed.append(item)
    item = copy.deepcopy(expected); item["approved_aggregate_cap_usd"] = "100.000000"; changed.append(item)
    item = copy.deepcopy(expected); item["committed_actual_cost_usd"] = "0.010000"; changed.append(item)
    item = copy.deepcopy(expected); item["entries"].append({"reservation_id": "fake"}); changed.append(item)
    item = copy.deepcopy(expected); item["local_zero_external_cost_evidence"][-1]["external_requests"] = 1; changed.append(item)
    item = copy.deepcopy(expected); item["revision_summary"]["total_local_milestones"] -= 1; changed.append(item)
    return sum(value != expected for value in changed), len(changed)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--emit", type=Path); args = parser.parse_args()
    try:
        expected = build()
        if args.emit:
            target = args.emit if args.emit.is_absolute() else ROOT / args.emit
            target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            require(json.loads(R2.read_text(encoding="utf-8")) == expected, "tracked r2 differs")
        rejected, total = mutations(expected); require(rejected == total, "mutation rejection incomplete")
        require(len({item["milestone"] for item in expected["local_zero_external_cost_evidence"]}) == expected["revision_summary"]["total_local_milestones"], "duplicate milestone")
    except (LedgerError, FileNotFoundError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr); return 1
    print(f"0 failures, 0 warnings ({expected['revision_summary']['total_local_milestones']} zero-cost milestones; 0 requests/uploads/$0; {rejected}/{total} mutations rejected)")
    return 0


if __name__ == "__main__": raise SystemExit(main())
