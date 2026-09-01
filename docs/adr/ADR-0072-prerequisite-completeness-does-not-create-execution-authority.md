# ADR-0072: prerequisite completeness does not create execution authority

- Status: accepted
- Date: 2026-09-01

## Context

P036 has four root preflight prerequisites: approved base, approved mask, exact external authority, and a distinct production reservation. Independent mutation tests existed, but they did not enumerate the complete Boolean lattice or expose cascading dependencies between inputs, package hash, authority, and reservation.

## Decision

Exhaust all 16 prerequisite subsets using only the existing validation fixtures. Require every incomplete subset to remain blocked. Permit the complete validation-only subset to emit metadata only, and separately require the same proxy set to fail outside fixture mode.

## Consequences

- All 16/16 subsets are exercised; 15/15 partial subsets emit no envelope.
- The complete fixture emits one `SYNTHETIC_VALIDATION_ONLY` metadata envelope with null request body and no network executor.
- The complete non-fixture attempt is blocked by proxy-input ineligibility and emits no envelope.
- Seventeen/seventeen lattice/promotion/activity mutations fail.
- No real base, mask, authority, reservation, request, upload, cost, RenderRecord, or acceptance is created.
