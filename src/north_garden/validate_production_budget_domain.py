"""Prove G07 budget cannot authorize CH05 production and validate a synthetic domain."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import production_budget as budget


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def must_fail(label: str, action, failures: list[str]) -> None:
    try:
        action()
    except budget.ProductionBudgetError:
        return
    failures.append(f"preflight unexpectedly passed: {label}")


def main() -> int:
    failures = []
    original = (budget.POLICY_PATH, budget.LEDGER_PATH, budget.LOCK_PATH, os.environ.get(budget.CAP_ENV), os.environ.get(budget.BAKEOFF_CAP_ENV))
    authority = {
        "record_id": "test-authority", "path": "test/authority.json", "sha256": "0" * 64,
        "external_upload_authorized": True, "panel_input_package_sha256": "1" * 64,
        "external_scope": {
            "external_provider": "test-provider", "external_model_snapshot": "test-model",
            "external_endpoint": "https://example.invalid/v1/edit",
        },
    }
    os.environ[budget.BAKEOFF_CAP_ENV] = "100"
    os.environ.pop(budget.CAP_ENV, None)
    must_fail("bakeoff cap only", lambda: budget.preflight_production_budget("test", authority), failures)
    os.environ[budget.CAP_ENV] = "100"
    must_fail("tracked production policy disabled", lambda: budget.preflight_production_budget("test", authority), failures)

    with tempfile.TemporaryDirectory(prefix="north-garden-production-budget-") as directory:
        root = Path(directory)
        budget.POLICY_PATH = root / "policy.json"
        budget.LEDGER_PATH = root / "ledger.json"
        budget.LOCK_PATH = root / "ledger.lock"
        policy = {
            "record_type": "ProductionBudgetPolicy", "schema_version": "1.0", "record_id": "test-policy",
            "budget_domain": budget.DOMAIN, "execution_enabled": True, "bakeoff_budget_reuse_prohibited": True,
            "maximum_aggregate_cap_usd": "2.00",
            "approved_adapters": {"test": {
                "external_provider": "test-provider", "external_model_snapshot": "test-model",
                "external_endpoint": "https://example.invalid/v1/edit", "per_request_reservation_usd": "1.00",
            }},
        }
        ledger = {
            "record_type": "ProductionCostLedger", "schema_version": "1.0", "record_id": "test-ledger",
            "budget_domain": budget.DOMAIN, "policy_id": "test-policy", "entries": [],
        }
        write(budget.POLICY_PATH, policy)
        write(budget.LEDGER_PATH, ledger)
        os.environ[budget.CAP_ENV] = "2"
        preflight = budget.preflight_production_budget("test", authority)
        if preflight["available_usd"] != "2.000000" or not preflight["bakeoff_cap_environment_ignored"]:
            failures.append("synthetic domain preflight accounting is incorrect")
        reservation = budget.reserve_production_request("test", "panel-1", authority)
        if reservation["state"] != "reserved" or reservation["budget_domain"] != budget.DOMAIN:
            failures.append("synthetic production reservation is invalid")
        if budget.preflight_production_budget("test", authority)["available_usd"] != "1.000000":
            failures.append("synthetic production hold was not aggregated")
        must_fail("duplicate request", lambda: budget.reserve_production_request("test", "panel-1", authority), failures)
        held = budget.hold_production_reservation(
            reservation["reservation_id"], provider_request_id="provider-request-1", outcome="completed_cost_pending"
        )
        if held["state"] != "awaiting_reconciliation":
            failures.append("submitted production reservation was not held")
        must_fail(
            "actual exceeds reservation",
            lambda: budget.reconcile_production_reservation(reservation["reservation_id"], "1.01", outcome="invalid"),
            failures,
        )
        committed = budget.reconcile_production_reservation(
            reservation["reservation_id"], "0.60", outcome="completed_cost_reconciled"
        )
        if committed["state"] != "committed" or committed["actual_cost_usd"] != "0.600000":
            failures.append("production cost reconciliation is incorrect")
        second = budget.reserve_production_request("test", "panel-2", authority)
        current = json.loads(budget.LEDGER_PATH.read_text(encoding="utf-8"))
        if current["available_usd"] != "0.400000":
            failures.append("committed plus held production totals are incorrect")
        released = budget.release_unsubmitted_production_reservation(second["reservation_id"], outcome="local_preflight_failure")
        if released["state"] != "released" or budget.preflight_production_budget("test", authority)["available_usd"] != "1.400000":
            failures.append("unsubmitted production reservation release is incorrect")
        wrong = {**authority, "external_scope": {**authority["external_scope"], "external_model_snapshot": "wrong"}}
        must_fail("authority scope mismatch", lambda: budget.preflight_production_budget("test", wrong), failures)
        bakeoff_ledger = {"record_type": "AggregateBakeoffCostLedger", "record_id": "bakeoff", "entries": []}
        write(budget.LEDGER_PATH, bakeoff_ledger)
        must_fail("bakeoff ledger substituted", lambda: budget.preflight_production_budget("test", authority), failures)

    budget.POLICY_PATH, budget.LEDGER_PATH, budget.LOCK_PATH = original[:3]
    for name, value in ((budget.CAP_ENV, original[3]), (budget.BAKEOFF_CAP_ENV, original[4])):
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value
    for failure in failures:
        print(f"failure: {failure}")
    if failures:
        return 1
    print("0 failures, 0 warnings (bakeoff capacity cannot authorize CH05; synthetic production reservation aggregates correctly)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
