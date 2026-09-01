"""Reconcile one ledger reservation and its linked RenderRecord."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bakeoff_budget import ROOT, atomic_write, reconcile_reservation, release_unsubmitted_reservation, stamp


RECORD_ROOT = (ROOT / "experiments/records").resolve()


def record_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    if not path.is_relative_to(RECORD_ROOT) or path.suffix.lower() != ".json":
        raise argparse.ArgumentTypeError("record must be a JSON file below experiments/records")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reservation_id")
    parser.add_argument("--record", required=True, type=record_path)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--actual-cost-usd")
    action.add_argument("--release-unsubmitted")
    parser.add_argument(
        "--method",
        choices=["actual_provider_cost", "usage_rate_reconciliation_estimate"],
        default="actual_provider_cost",
        help="Provenance for a nonzero reconciliation; estimates must be explicit.",
    )
    parser.add_argument("--calculation-note")
    args = parser.parse_args()

    record = json.loads(args.record.read_text(encoding="utf-8"))
    linked = record.get("budget_reservation", {})
    if linked.get("reservation_id") != args.reservation_id:
        raise SystemExit("RenderRecord reservation does not match requested ledger entry")
    if args.actual_cost_usd is not None:
        entry = reconcile_reservation(
            args.reservation_id, args.actual_cost_usd,
            provider_request_id=record.get("request_id"), provider_usage=record.get("provider_usage"),
            reconciliation_method=args.method,
        )
        method = args.method
    else:
        entry = release_unsubmitted_reservation(args.reservation_id, args.release_unsubmitted)
        method = "proven_unsubmitted_zero_cost"
    record["budget_reservation"] = entry
    record["cost_usd"] = entry.get("actual_cost_usd") or "0.000000"
    record["cost_reconciliation"] = {
        "method": method,
        "reconciled_at": stamp(),
        "reason": args.release_unsubmitted,
        "calculation_note": args.calculation_note,
    }
    atomic_write(args.record, record)
    print(json.dumps({
        "record": args.record.relative_to(ROOT).as_posix(),
        "reservation_id": args.reservation_id,
        "state": entry["state"],
        "cost_usd": record["cost_usd"],
    }, indent=2))


if __name__ == "__main__":
    main()
