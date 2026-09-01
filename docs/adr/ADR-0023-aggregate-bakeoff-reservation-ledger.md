# ADR-0023: all paid bakeoff adapters share one reservation ledger

- Status: accepted
- Date: 2026-09-01

## Context

The four provider adapters previously read the same environment cap independently. Concurrent or sequential invocations could therefore each treat the aggregate authorization as a per-adapter allowance. Provider billing may also lag image delivery, so releasing unknown charges immediately would understate obligations.

## Decision

Every paid G07 request must atomically reserve its provider-specific documented ceiling through `src/north_garden/bakeoff_budget.py` before network submission. The single ledger is `docs/research/evidence/g07-bakeoff-cost-ledger-r1.json`; policy and ceilings are in `config/g07-bakeoff-budget-policy-r1.json`.

Committed actual cost plus all reserved or awaiting-reconciliation amounts may never exceed the lower of the local approved cap and the policy maximum. A possibly billable request retains its full reservation until provider usage or billing is reconciled. Only a request proven not submitted may release at zero cost. Duplicate active/committed adapter-request keys are refused.

## Consequences

- No adapter can independently consume the full aggregate cap.
- Provider failures are budget-conservative until reconciled.
- A request whose actual charge exceeds its ceiling stops for manual authority review rather than expanding the cap silently.
- The ledger does not select a renderer, change frozen gauntlet semantics, or authorize any additional data class.
