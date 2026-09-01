# ADR-0044: repair-readiness revisions are append-only and gate-complete

- Status: accepted
- Date: 2026-09-01

## Context

P036 repair mechanics have advanced since readiness r1, but r1 is historical evidence and must not be rewritten. A newer record must distinguish local policy progress from actual production inputs and execution authority.

## Decision

Create readiness r2 as a new immutable record that pins r1's exact hash, the current ComicPanelPlan, selected route, local repair policy, measured boundary/causal evidence, disabled production policy/zero ledger, and current offline preflight.

Report every required production gate in the record. Keep approved base, approved mask, exact upload authority, reservation, request, journal, RenderRecord, candidate, review minutes, and acceptance null or zero. Keep `AnimationShotPlan` and E-Conte explicitly null.

## Consequences

- R1 remains unchanged and independently verifiable.
- Mechanics progress is visible without reducing the four production blockers.
- Proxy controls remain zero eligible bases/masks/uploads.
- Eleven/eleven immutability, gate, input, execution, medium, and review mutations fail.
- Production remains disabled with no cap, $0 committed, and $0 held.
