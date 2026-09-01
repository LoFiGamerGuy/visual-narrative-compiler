# ADR-0049: topology width and visual boundary acceptance are separate gates

- Status: accepted
- Date: 2026-09-01

## Context

P036 and P044 local controls select different widths, 16 and 5 pixels. Both retain abstract topology, but neither has an exact approved panel base/candidate with timed seam review. A selector that treats topology as visual acceptance would promote proxy mechanics into production readiness.

## Decision

Use a scale-aware selector contract with separate gates for exact panel/support binding, topology width ceiling, exact-base visual discontinuity, exterior/no-change, timed human seam review, and production authority.

Do not define a universal width. Keep P036=16 and P044=5 as distinct local profiles. Mark both visual-discontinuity gates blocked on absent exact approved panel bases/candidates; keep P044 policy-absent and P036 production-blocked.

## Consequences

- Width cannot be inherited across panels or selected from motion mode.
- A topology pass cannot become a visual pass.
- Proxy visual metrics cannot transfer to panel art.
- Current state is two local topology passes, zero exact-panel visual passes, zero timed seam reviews, and zero production-ready profiles.
- Ten/ten gate, width, visual, production, and generalization mutations fail.
