# ADR-0034: unknown provider outcome is held and not retried

- Status: accepted
- Date: 2026-09-01

## Context

A process may fail after a paid request crosses the submission boundary but before a provider request ID, response, cost, or RenderRecord is persisted. Blind retry can duplicate spend and outputs; releasing the reservation can understate obligations.

## Decision

Create a deterministic idempotency key from adapter, stable panel/revision, exact input-package hash, and attempt ordinal before submission. Record append-only journal events around reservation and submission boundaries. Once `SUBMISSION_STARTED`, a crash enters `OUTCOME_UNKNOWN`; the full reservation remains held and the attempt cannot retry.

Recovery must bind the original provider request ID, capture exact output hashes/timing, reconcile actual cost, persist the RenderRecord, and only then complete. Only a proven pre-submit abort may release its reservation and authorize a consecutively numbered, explicitly superseding retry. Aggregate ledger state/request/cost must agree with the journal.

## Consequences

- Future executors must journal before any network call.
- Unknown outcomes are operational incidents, not ordinary failures or zero-cost events.
- Duplicate idempotency keys across journals fail closed.
- This ADR adds no executor, external authority, or current spend.
