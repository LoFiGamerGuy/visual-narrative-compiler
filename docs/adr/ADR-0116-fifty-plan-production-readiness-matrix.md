# ADR-0116: Fifty-plan production-readiness matrix

Date: 2026-09-01

Status: Accepted as a read-only planning join

## Context

Coverage, scale, continuity, candidate, route, dry-run, copy, and authority evidence existed in separate records. Without an exact 50-plan join, a production queue could mistake selected evidence for acceptance or a prioritized plan for prompt readiness.

## Decision

Compile one row per ComicPanelPlan with exact coverage tier, cast assertions, scale role/range, recommended mechanisms, existing candidate history, engineering rollup, selected candidate, P010–P013 dry-run membership, fail-closed state, readiness class, and explicit blockers.

## Evidence

- 50 = 14 selected-evidence + four P010–P013 dry-run + eight other Tier A + 24 Tier B/C backlog rows.
- Fourteen plans have 26 existing CH05 candidates; every plan has continuity assertions and a conditional scale role.
- Every next-production prompt is null; copy, acceptance, commercial clearance, execution, and plan revision are false/zero.
- The 1600×1900 local map is visually checked and keeps all 50 cells legible.
- 20/20 state/denominator/planning mutations are rejected.

## Consequences

- Selected engineering evidence is not conflated with owner acceptance.
- P010–P013 is visibly more prepared than other uncovered plans but remains blocked by six explicit gates.
- Tier A and backlog plans cannot skip hypothesis, manifest, review-contract, copy/reference, commercial, or owner gates.
- No prompt, provider activity, upload, plan revision, or production promotion is created.
