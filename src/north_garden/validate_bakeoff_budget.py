"""Validate aggregate reservation, reconciliation, and concurrency semantics."""
from __future__ import annotations

import json
import multiprocessing
import os
import tempfile
from pathlib import Path

import bakeoff_budget as budget


def worker(adapter_id: str, request_key: str, policy_path: str, ledger_path: str, queue) -> None:
    try:
        budget.POLICY_PATH = Path(policy_path)
        budget.LEDGER_PATH = Path(ledger_path)
        budget.LOCK_PATH = budget.LEDGER_PATH.with_suffix(".json.lock")
        os.environ[budget.CAP_ENV] = "10"
        queue.put(("ok", budget.reserve_bakeoff_request(adapter_id, request_key)))
    except Exception as error:  # surfaced to the parent as test evidence
        queue.put(("error", str(error)))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    original = (budget.POLICY_PATH, budget.LEDGER_PATH, budget.LOCK_PATH, os.environ.get(budget.CAP_ENV))
    with tempfile.TemporaryDirectory(prefix="north-garden-budget-") as directory:
        root = Path(directory)
        budget.POLICY_PATH = root / "policy.json"
        budget.LEDGER_PATH = root / "ledger.json"
        budget.LOCK_PATH = root / "ledger.lock"
        os.environ[budget.CAP_ENV] = "10"
        write_json(budget.POLICY_PATH, {
            "record_type": "AggregateBakeoffBudgetPolicy", "schema_version": "1.0", "record_id": "test-policy",
            "maximum_aggregate_cap_usd": "12", "execution_enabled": True,
            "per_request_reservation_usd": {"adapter_a": "6", "adapter_b": "6"},
            "maximum_full_bakeoff_reservation_usd": "12",
            "scope": {"adapters": ["adapter_a", "adapter_b"], "requests_per_adapter": 1},
        })
        write_json(budget.LEDGER_PATH, {
            "record_type": "AggregateBakeoffCostLedger", "schema_version": "1.0",
            "approved_aggregate_cap_usd": "10", "entries": [],
        })
        assert budget.preflight_bakeoff_budget("adapter_a")["available_usd"] == "10.000000"

        # Competing adapters cannot each treat the same aggregate cap as theirs.
        context = multiprocessing.get_context("spawn")
        queue = context.Queue()
        processes = [
            context.Process(target=worker, args=(adapter, "request-1", str(budget.POLICY_PATH), str(budget.LEDGER_PATH), queue))
            for adapter in ("adapter_a", "adapter_b")
        ]
        for process in processes:
            process.start()
        for process in processes:
            process.join(15)
            assert process.exitcode == 0
        results = [queue.get(timeout=2) for _ in processes]
        assert [state for state, _ in results].count("ok") == 1
        assert [state for state, _ in results].count("error") == 1

        reservation = next(payload for state, payload in results if state == "ok")
        held = budget.hold_for_reconciliation(
            reservation["reservation_id"], provider_request_id="provider-test-1",
            provider_usage={"images": 1}, outcome="completed_cost_pending",
        )
        assert held["state"] == "awaiting_reconciliation"
        committed = budget.reconcile_reservation(
            reservation["reservation_id"], "1.25", provider_usage={"images": 1},
        )
        assert committed["state"] == "committed" and committed["actual_cost_usd"] == "1.250000"

        second = budget.reserve_bakeoff_request("adapter_b", "request-2")
        released = budget.release_unsubmitted_reservation(second["reservation_id"], "local_preflight_failure")
        assert released["state"] == "released"
        ledger = json.loads(budget.LEDGER_PATH.read_text(encoding="utf-8"))
        assert ledger["committed_actual_cost_usd"] == "1.250000"
        assert ledger["held_reservations_usd"] == "0.000000"
        assert ledger["available_usd"] == "8.750000"

    budget.POLICY_PATH, budget.LEDGER_PATH, budget.LOCK_PATH = original[:3]
    if original[3] is None:
        os.environ.pop(budget.CAP_ENV, None)
    else:
        os.environ[budget.CAP_ENV] = original[3]
    print("0 failures, 0 warnings (aggregate bakeoff reservation ledger concurrency and reconciliation validated)")


if __name__ == "__main__":
    main()
