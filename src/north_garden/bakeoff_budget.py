"""Cross-provider reservation ledger for the fictional G07 bakeoff.

The approved cap is aggregate.  Every paid adapter must reserve against this
single ledger before submitting a request.  A reservation remains held when a
provider may have charged but exact cost is not yet known.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterator


ROOT = Path(__file__).resolve().parents[2]
CAP_ENV = "NORTH_GARDEN_APPROVED_BAKEOFF_CAP_USD"
POLICY_PATH = ROOT / "config/g07-bakeoff-budget-policy-r1.json"
LEDGER_PATH = ROOT / "docs/research/evidence/g07-bakeoff-cost-ledger-r1.json"
LOCK_PATH = LEDGER_PATH.with_suffix(LEDGER_PATH.suffix + ".lock")
MONEY_QUANTUM = Decimal("0.000001")


class BudgetError(RuntimeError):
    """Raised before network submission when aggregate budget safety fails."""


def stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def money(value: object, field: str) -> Decimal:
    try:
        parsed = Decimal(str(value)).quantize(MONEY_QUANTUM)
    except (InvalidOperation, ValueError) as error:
        raise BudgetError(f"{field} must be a plain finite decimal") from error
    if not parsed.is_finite() or parsed < 0:
        raise BudgetError(f"{field} must be a non-negative finite decimal")
    return parsed


def money_text(value: Decimal) -> str:
    return format(value.quantize(MONEY_QUANTUM), "f")


@contextmanager
def exclusive_lock(path: Path, timeout_seconds: float = 10.0) -> Iterator[None]:
    """Take a one-byte OS lock that is released automatically on process exit."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+b")
    try:
        if handle.seek(0, os.SEEK_END) == 0:
            handle.write(b"0")
            handle.flush()
        deadline = time.monotonic() + timeout_seconds
        while True:
            try:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as error:
                if time.monotonic() >= deadline:
                    raise BudgetError("timed out acquiring aggregate bakeoff budget lock") from error
                time.sleep(0.025)
        yield
    finally:
        try:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BudgetError(f"cannot load required budget file {path.relative_to(ROOT)}") from error


def atomic_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def validated_policy(adapter_id: str) -> tuple[dict, Decimal]:
    policy = load_json(POLICY_PATH)
    if policy.get("record_type") != "AggregateBakeoffBudgetPolicy" or policy.get("schema_version") != "1.0":
        raise BudgetError("aggregate bakeoff budget policy schema is invalid")
    if not policy.get("execution_enabled"):
        raise BudgetError("paid bakeoff execution is disabled until current primary documentation is recorded")
    policy_cap = money(policy.get("maximum_aggregate_cap_usd"), "maximum_aggregate_cap_usd")
    scope = policy.get("scope", {})
    adapters = scope.get("adapters", [])
    requests_per_adapter = scope.get("requests_per_adapter")
    if not isinstance(requests_per_adapter, int) or requests_per_adapter <= 0 or not adapters:
        raise BudgetError("budget policy scope is invalid")
    reservations = policy.get("per_request_reservation_usd", {})
    if set(reservations) != set(adapters):
        raise BudgetError("every and only scoped adapter must have a reservation ceiling")
    full_bakeoff = sum(
        (money(reservations[item], f"per_request_reservation_usd.{item}") * requests_per_adapter for item in adapters),
        Decimal("0"),
    )
    declared_full = money(policy.get("maximum_full_bakeoff_reservation_usd"), "maximum_full_bakeoff_reservation_usd")
    if full_bakeoff != declared_full or full_bakeoff > policy_cap:
        raise BudgetError("full-bakeoff reservation total is inconsistent with policy or exceeds its cap")
    approved = money(os.environ.get(CAP_ENV, ""), CAP_ENV)
    if approved <= 0 or approved > policy_cap:
        raise BudgetError(f"{CAP_ENV} must be positive and no greater than {money_text(policy_cap)}")
    if adapter_id not in reservations:
        raise BudgetError(f"no documented reservation ceiling exists for adapter {adapter_id}")
    reservation = money(reservations[adapter_id], f"per_request_reservation_usd.{adapter_id}")
    if reservation <= 0:
        raise BudgetError(f"reservation ceiling for {adapter_id} must be positive")
    return policy, min(approved, policy_cap)


def preflight_bakeoff_budget(adapter_id: str) -> dict:
    """Validate aggregate policy/cap/capacity without writing a reservation."""
    policy, cap = validated_policy(adapter_id)
    amount = money(policy["per_request_reservation_usd"][adapter_id], "reservation")
    with exclusive_lock(LOCK_PATH):
        ledger = load_json(LEDGER_PATH)
        committed, held = ledger_totals(ledger)
    if committed + held + amount > cap:
        raise BudgetError(f"insufficient aggregate budget capacity for {adapter_id}")
    return {
        "adapter_id": adapter_id,
        "approved_aggregate_cap_usd": money_text(cap),
        "per_request_reservation_usd": money_text(amount),
        "committed_actual_cost_usd": money_text(committed),
        "held_reservations_usd": money_text(held),
        "available_usd": money_text(cap - committed - held),
        "policy_id": policy["record_id"],
    }


def ledger_totals(ledger: dict) -> tuple[Decimal, Decimal]:
    committed = Decimal("0")
    held = Decimal("0")
    for entry in ledger.get("entries", []):
        state = entry.get("state")
        if state == "committed":
            committed += money(entry["actual_cost_usd"], "actual_cost_usd")
        elif state in {"reserved", "awaiting_reconciliation"}:
            held += money(entry["reserved_usd"], "reserved_usd")
    return committed, held


def refresh_totals(ledger: dict, cap: Decimal) -> None:
    committed, held = ledger_totals(ledger)
    ledger["approved_aggregate_cap_usd"] = money_text(cap)
    ledger["committed_actual_cost_usd"] = money_text(committed)
    ledger["held_reservations_usd"] = money_text(held)
    ledger["available_usd"] = money_text(cap - committed - held)
    ledger["updated_at"] = stamp()


def reserve_bakeoff_request(adapter_id: str, request_key: str) -> dict:
    """Atomically reserve one documented request ceiling before submission."""
    policy, cap = validated_policy(adapter_id)
    amount = money(policy["per_request_reservation_usd"][adapter_id], "reservation")
    with exclusive_lock(LOCK_PATH):
        ledger = load_json(LEDGER_PATH)
        if ledger.get("record_type") != "AggregateBakeoffCostLedger":
            raise BudgetError("aggregate bakeoff cost ledger schema is invalid")
        duplicates = [
            entry for entry in ledger.get("entries", [])
            if entry.get("adapter_id") == adapter_id and entry.get("request_key") == request_key
            and entry.get("state") != "released"
        ]
        if duplicates:
            raise BudgetError(f"request {adapter_id}/{request_key} already has an active or committed ledger entry")
        committed, held = ledger_totals(ledger)
        if committed + held + amount > cap:
            raise BudgetError(
                f"aggregate cap would be exceeded: committed={money_text(committed)}, "
                f"held={money_text(held)}, requested={money_text(amount)}, cap={money_text(cap)}"
            )
        reservation_id = f"ng-g07-budget-{uuid.uuid4()}"
        entry = {
            "reservation_id": reservation_id,
            "adapter_id": adapter_id,
            "request_key": request_key,
            "state": "reserved",
            "reserved_usd": money_text(amount),
            "actual_cost_usd": None,
            "reserved_at": stamp(),
            "reconciled_at": None,
            "provider_request_id": None,
            "provider_usage": None,
            "outcome": None,
            "policy_id": policy["record_id"],
        }
        ledger.setdefault("entries", []).append(entry)
        refresh_totals(ledger, cap)
        atomic_write(LEDGER_PATH, ledger)
        return dict(entry)


def _update_reservation(reservation_id: str, updater) -> dict:
    with exclusive_lock(LOCK_PATH):
        ledger = load_json(LEDGER_PATH)
        cap = money(ledger.get("approved_aggregate_cap_usd"), "approved_aggregate_cap_usd")
        entry = next((item for item in ledger.get("entries", []) if item.get("reservation_id") == reservation_id), None)
        if entry is None:
            raise BudgetError(f"unknown reservation {reservation_id}")
        updater(entry)
        refresh_totals(ledger, cap)
        committed, held = ledger_totals(ledger)
        if committed + held > cap:
            raise BudgetError("ledger invariant violated: obligations exceed aggregate cap")
        atomic_write(LEDGER_PATH, ledger)
        return dict(entry)


def hold_for_reconciliation(
    reservation_id: str,
    *,
    provider_request_id: str | None,
    provider_usage: object,
    outcome: str,
) -> dict:
    """Retain the full ceiling when a submitted request's exact cost is unknown."""
    def update(entry: dict) -> None:
        if entry.get("state") != "reserved":
            raise BudgetError(f"reservation {reservation_id} is not in reserved state")
        entry.update({
            "state": "awaiting_reconciliation",
            "provider_request_id": provider_request_id,
            "provider_usage": provider_usage,
            "outcome": outcome,
        })

    return _update_reservation(reservation_id, update)


def reconcile_reservation(
    reservation_id: str,
    actual_cost_usd: object,
    *,
    provider_request_id: str | None = None,
    provider_usage: object = None,
) -> dict:
    """Commit actual billed cost and release the unused reservation balance."""
    actual = money(actual_cost_usd, "actual_cost_usd")

    def update(entry: dict) -> None:
        if entry.get("state") not in {"reserved", "awaiting_reconciliation"}:
            raise BudgetError(f"reservation {reservation_id} cannot be reconciled from {entry.get('state')}")
        if actual > money(entry["reserved_usd"], "reserved_usd"):
            raise BudgetError("actual cost exceeds its reservation; manual authority review is required")
        entry.update({
            "state": "committed",
            "actual_cost_usd": money_text(actual),
            "reconciled_at": stamp(),
            "provider_request_id": provider_request_id or entry.get("provider_request_id"),
            "provider_usage": provider_usage if provider_usage is not None else entry.get("provider_usage"),
        })

    return _update_reservation(reservation_id, update)


def release_unsubmitted_reservation(reservation_id: str, reason: str) -> dict:
    """Release only when callers can prove no paid request was submitted."""
    def update(entry: dict) -> None:
        if entry.get("state") != "reserved":
            raise BudgetError(f"reservation {reservation_id} is not releasable")
        entry.update({"state": "released", "outcome": f"not_submitted:{reason}", "reconciled_at": stamp()})

    return _update_reservation(reservation_id, update)
