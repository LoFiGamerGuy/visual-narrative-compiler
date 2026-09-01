# ADR-0035: unknown outcome is an incident, not a RenderRecord

- Status: accepted
- Date: 2026-09-01

## Context

At crash boundaries, a provider may have accepted a request while no candidate bytes, final timing, usage, or cost are available locally. Creating a nominal RenderRecord at that point would fabricate outputs/completion and could release or retry a still-billable request.

## Decision

Emit `ProviderSubmissionIncident` for `OUTCOME_UNKNOWN`. It binds the exact journal head/idempotency key/input package and held aggregate reservation, records recovery actions, and requires candidate files and RenderRecord to remain absent.

Emit `RenderRecord` only for known terminal outcomes. Success requires exact candidates, request/provider identity, timing, usage or an explicit unavailable reason, cost reconciliation, and pending human-review state. An explicit failed/reconciled outcome has no candidates and binds a separate failure record. Neither variant is accepted automatically.

## Consequences

- Unknown incidents remain non-retryable and cost-pending.
- Failed executions retain spend/failure evidence without fake candidates.
- Completed candidates remain review-pending until a separate timed decision.
- Synthetic schema fixtures are clearly marked and do not become CH05 records.
