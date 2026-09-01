# ADR-0055: repair-outcome finalization requires terminal real evidence

- Status: accepted
- Date: 2026-09-01

## Context

Validators can prove that a complete RenderRecord is internally coherent, but current CH05 state has no approved inputs, authority, reservation, completed journal, provider candidate, eligible seam review, or cost reconciliation. A finalizer must not construct an outcome from partial readiness or synthetic fixtures.

## Decision

Require terminal journal, v2.1 RenderRecord, exact candidate/measurement, eligible non-fixture seam session, and reconciled provider cost before real finalization. Keep request/network construction outside the finalizer. Permit deterministic synthetic finalization only when explicitly invoked in validation-fixture mode, and reject fixture promotion to real mode.

## Consequences

- Real P036 reports nine explicit blockers and emits no RenderRecord, candidate, review, request, or cost.
- Two identical synthetic finalizations produce identical record, journal, and ledger digests.
- Changing the fixture flag cannot promote the synthetic lifecycle because record state and review eligibility then contradict the real contract.
- Ten/ten blocker, fabricated-output, fixture, network, activity, and medium mutations fail.
- No production authority, external upload, or spend follows.
