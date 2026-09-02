# ADR-0134: Pilot lifecycle forbids transition skips and rights conflation

Date: 2026-09-01

Status: Accepted

## Context

Separate draft, unlock, render, review, repair, and rights records exist, but their permitted ordering was implicit.

## Decision

Define 11 states and 11 guarded transitions from draft through independently reviewed rights/exact-base status. Exhaust all 121 state pairs. Permit a four-edge review/repair loop capped at two one-class repairs; preserve passing rows and prohibit broad rerolls. Keep provisional engineering acceptance separate from both commercial clearance and exact-base eligibility.

## Evidence

- Eleven legal transitions and 110 illegal or unconfigured pairs are exact.
- Current state is `DRAFT_BLUEPRINTED` with zero enabled transitions.
- The repair loop is review → allocation → targeted render → rebuilt packet → review, with maximum two slots.
- Six invariants preserve ComicPanelPlan-only scope, data/reference boundaries, exact RenderRecords, live review timing, diagnostic failures, and rights separation.
- Eighteen/eighteen mutations are rejected.

## Consequences

No state transition occurs from defining the machine. Future tooling must provide every edge guard rather than skipping directly to render, acceptance, or rights claims.
