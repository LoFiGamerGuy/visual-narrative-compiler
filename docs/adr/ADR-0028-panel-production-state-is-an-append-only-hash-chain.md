# ADR-0028: panel production state is an append-only hash chain

- Status: accepted
- Date: 2026-09-01

## Context

Chapter production has multiple independent gates: base and mask approval, exact external authority, aggregate budget reservation, provider submission, cost reconciliation, RenderRecord completion, hard-assertion review, measured human minutes, and acceptance. A mutable status field could skip or rewrite any of them and would make retries hard to audit.

## Decision

Represent each panel run as a `ComicPanelRunLedger` with an append-only SHA-256 event chain and an explicit transition graph. Events bind stable panel/revision IDs and cannot skip lifecycle gates. Provider submission requires a prior exact-scope authority and aggregate reservation; completion requires request identity, timing, outputs, RenderRecord, and cost-reconciliation references. Acceptance requires a completed positive-minute review and passing hard assertions.

Reservation declarations are not trusted alone. A separate validation binds reservation ID, adapter, held/committed state, provider request ID, and actual cost to an exact supplied aggregate ledger. Released, missing, or mismatched entries fail closed.

## Consequences

- P033–P038 remain at `BASE_APPROVAL_PENDING`; no run is executable.
- Retries become new events/ledgers rather than edits to historical attempts.
- A rejected or accepted terminal run cannot silently advance.
- Comic run ledgers remain separate from `ComicPanelPlan`, `RenderRecord`, and future `AnimationShotPlan / E-Conte` records.
