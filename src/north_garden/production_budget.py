"""Separate, fail-closed aggregate budget domain for CH05 production."""
from __future__ import annotations

import json
import os
import uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path

from bakeoff_budget import atomic_write, exclusive_lock


ROOT = Path(__file__).resolve().parents[2]
CAP_ENV = "NORTH_GARDEN_APPROVED_PRODUCTION_CAP_USD"
BAKEOFF_CAP_ENV = "NORTH_GARDEN_APPROVED_BAKEOFF_CAP_USD"
DOMAIN = "NORTH_GARDEN_CH05_PRODUCTION"
POLICY_PATH = ROOT / "config/ch05-production-budget-policy-r1.json"
LEDGER_PATH = ROOT / "docs/research/evidence/ch05-production-cost-ledger-r1.json"
LOCK_PATH = LEDGER_PATH.with_suffix(LEDGER_PATH.suffix + ".lock")
QUANTUM = Decimal("0.000001")


class ProductionBudgetError(RuntimeError):
    """Raised before production submission when authority or budget is absent."""


def money(value: object, field: str, *, positive: bool = False) -> Decimal:
    try:
        parsed = Decimal(str(value)).quantize(QUANTUM)
    except (InvalidOperation, ValueError) as error:
        raise ProductionBudgetError(f"{field} must be a finite decimal") from error
    if not parsed.is_finite() or parsed < 0 or (positive and parsed <= 0):
        raise ProductionBudgetError(f"{field} must be {'positive' if positive else 'non-negative'}")
    return parsed


def text(value: Decimal) -> str:
    return format(value.quantize(QUANTUM), "f")


def read(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProductionBudgetError(f"cannot load {path}") from error


def exact_authority_errors(authority: dict, adapter: dict) -> list[str]:
    errors = []
    if authority.get("external_upload_authorized") is not True:
        errors.append("external upload is not authorized")
    for field in ("record_id", "path", "sha256"):
        if not authority.get(field):
            errors.append(f"authority {field} is missing")
    scope = authority.get("external_scope", {})
    expected = {
        "external_provider": adapter.get("external_provider"),
        "external_model_snapshot": adapter.get("external_model_snapshot"),
        "external_endpoint": adapter.get("external_endpoint"),
    }
    for field, value in expected.items():
        if not value or scope.get(field) != value:
            errors.append(f"authority scope mismatch: {field}")
    if not authority.get("panel_input_package_sha256"):
        errors.append("exact panel input package hash is missing")
    return errors


def totals(ledger: dict) -> tuple[Decimal, Decimal]:
    committed = Decimal("0")
    held = Decimal("0")
    for entry in ledger.get("entries", []):
        if entry.get("state") == "committed":
            committed += money(entry.get("actual_cost_usd"), "actual_cost_usd")
        elif entry.get("state") in {"reserved", "awaiting_reconciliation"}:
            held += money(entry.get("reserved_usd"), "reserved_usd")
    return committed, held


def validate_domain(policy: dict, ledger: dict) -> None:
    if policy.get("record_type") != "ProductionBudgetPolicy" or policy.get("budget_domain") != DOMAIN:
        raise ProductionBudgetError("production policy schema/domain is invalid")
    if ledger.get("record_type") != "ProductionCostLedger" or ledger.get("budget_domain") != DOMAIN:
        raise ProductionBudgetError("production ledger schema/domain is invalid; bakeoff ledger reuse is prohibited")
    if ledger.get("policy_id") != policy.get("record_id"):
        raise ProductionBudgetError("production ledger policy binding is invalid")


def preflight_production_budget(adapter_id: str, authority: dict) -> dict:
    policy, ledger = read(POLICY_PATH), read(LEDGER_PATH)
    validate_domain(policy, ledger)
    if policy.get("bakeoff_budget_reuse_prohibited") is not True:
        raise ProductionBudgetError("policy must explicitly prohibit bakeoff budget reuse")
    if not policy.get("execution_enabled"):
        raise ProductionBudgetError("CH05 production execution is disabled; G07 bakeoff authority does not apply")
    policy_cap = money(policy.get("maximum_aggregate_cap_usd"), "maximum_aggregate_cap_usd", positive=True)
    production_cap = money(os.environ.get(CAP_ENV), CAP_ENV, positive=True)
    if production_cap > policy_cap:
        raise ProductionBudgetError("production environment cap exceeds policy maximum")
    adapters = policy.get("approved_adapters", {})
    if adapter_id not in adapters:
        raise ProductionBudgetError(f"adapter is not approved in production domain: {adapter_id}")
    adapter = adapters[adapter_id]
    authority_errors = exact_authority_errors(authority, adapter)
    if authority_errors:
        raise ProductionBudgetError("; ".join(authority_errors))
    reservation = money(adapter.get("per_request_reservation_usd"), "per_request_reservation_usd", positive=True)
    with exclusive_lock(LOCK_PATH):
        ledger = read(LEDGER_PATH)
        validate_domain(policy, ledger)
        committed, held = totals(ledger)
    cap = min(policy_cap, production_cap)
    if committed + held + reservation > cap:
        raise ProductionBudgetError("insufficient aggregate CH05 production budget capacity")
    return {
        "budget_domain": DOMAIN,
        "adapter_id": adapter_id,
        "approved_aggregate_cap_usd": text(cap),
        "reservation_usd": text(reservation),
        "committed_actual_cost_usd": text(committed),
        "held_reservations_usd": text(held),
        "available_usd": text(cap - committed - held),
        "bakeoff_cap_environment_ignored": bool(os.environ.get(BAKEOFF_CAP_ENV)),
        "authority_record_id": authority["record_id"],
    }


def reserve_production_request(adapter_id: str, request_key: str, authority: dict) -> dict:
    preflight = preflight_production_budget(adapter_id, authority)
    policy = read(POLICY_PATH)
    cap = money(preflight["approved_aggregate_cap_usd"], "approved cap", positive=True)
    amount = money(preflight["reservation_usd"], "reservation", positive=True)
    with exclusive_lock(LOCK_PATH):
        ledger = read(LEDGER_PATH)
        validate_domain(policy, ledger)
        if any(item.get("request_key") == request_key and item.get("state") != "released" for item in ledger.get("entries", [])):
            raise ProductionBudgetError(f"request already has a production reservation: {request_key}")
        committed, held = totals(ledger)
        if committed + held + amount > cap:
            raise ProductionBudgetError("aggregate CH05 production cap would be exceeded")
        entry = {
            "reservation_id": f"ng-ch05-production-budget-{uuid.uuid4()}",
            "budget_domain": DOMAIN,
            "adapter_id": adapter_id,
            "request_key": request_key,
            "authority_record_id": authority["record_id"],
            "panel_input_package_sha256": authority["panel_input_package_sha256"],
            "state": "reserved",
            "reserved_usd": text(amount),
            "actual_cost_usd": None,
            "provider_request_id": None,
        }
        ledger.setdefault("entries", []).append(entry)
        committed, held = totals(ledger)
        ledger.update({
            "approved_aggregate_cap_usd": text(cap),
            "committed_actual_cost_usd": text(committed),
            "held_reservations_usd": text(held),
            "available_usd": text(cap - committed - held),
        })
        atomic_write(LEDGER_PATH, ledger)
    return entry


def _update_reservation(reservation_id: str, updater) -> dict:
    policy = read(POLICY_PATH)
    with exclusive_lock(LOCK_PATH):
        ledger = read(LEDGER_PATH)
        validate_domain(policy, ledger)
        entry = next((item for item in ledger.get("entries", []) if item.get("reservation_id") == reservation_id), None)
        if entry is None:
            raise ProductionBudgetError(f"unknown production reservation: {reservation_id}")
        updater(entry)
        cap = money(ledger.get("approved_aggregate_cap_usd"), "approved_aggregate_cap_usd", positive=True)
        committed, held = totals(ledger)
        if committed + held > cap:
            raise ProductionBudgetError("production ledger obligations exceed aggregate cap")
        ledger.update({
            "committed_actual_cost_usd": text(committed),
            "held_reservations_usd": text(held),
            "available_usd": text(cap - committed - held),
        })
        atomic_write(LEDGER_PATH, ledger)
        return dict(entry)


def hold_production_reservation(reservation_id: str, *, provider_request_id: str, outcome: str) -> dict:
    """Bind a submitted request and keep the full ceiling held until reconciliation."""
    def update(entry: dict) -> None:
        if entry.get("state") not in {"reserved", "awaiting_reconciliation"}:
            raise ProductionBudgetError(f"reservation cannot be held from state {entry.get('state')}")
        existing = entry.get("provider_request_id")
        if existing and existing != provider_request_id:
            raise ProductionBudgetError("reservation is already bound to another provider request")
        entry.update({
            "state": "awaiting_reconciliation",
            "provider_request_id": provider_request_id,
            "outcome": outcome,
        })
    return _update_reservation(reservation_id, update)


def reconcile_production_reservation(reservation_id: str, actual_cost_usd: object, *, outcome: str) -> dict:
    """Commit exact/estimated actual cost without exceeding the reserved ceiling."""
    actual = money(actual_cost_usd, "actual_cost_usd")
    def update(entry: dict) -> None:
        if entry.get("state") not in {"reserved", "awaiting_reconciliation"}:
            raise ProductionBudgetError(f"reservation cannot be reconciled from state {entry.get('state')}")
        reserved = money(entry.get("reserved_usd"), "reserved_usd", positive=True)
        if actual > reserved:
            raise ProductionBudgetError("actual cost exceeds reserved production ceiling; incident review required")
        entry.update({"state": "committed", "actual_cost_usd": text(actual), "outcome": outcome})
    return _update_reservation(reservation_id, update)


def release_unsubmitted_production_reservation(reservation_id: str, *, outcome: str) -> dict:
    """Release only a reservation proven not submitted to a provider."""
    def update(entry: dict) -> None:
        if entry.get("state") != "reserved" or entry.get("provider_request_id"):
            raise ProductionBudgetError("only an unsubmitted production reservation may be released")
        entry.update({"state": "released", "outcome": outcome})
    return _update_reservation(reservation_id, update)
