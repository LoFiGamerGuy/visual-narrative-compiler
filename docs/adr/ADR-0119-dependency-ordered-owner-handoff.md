# ADR-0119: Dependency-ordered owner handoff

Date: 2026-09-01

Status: Accepted as a read-only decision aid

## Context

The current owner surface spans 14 provisional strongest candidates and ten route/density/lettering/P010/non-canon/authority questions. A flat list obscures which choices can proceed in parallel and which genuinely depend on earlier decisions.

## Decision

Compile 24 exact, linked tasks and order them by prerequisites only—not by a preference score:

- Stage 1: 14 individual candidate reviews plus foundational route, c005 density, c014 punctuation, lettering semantics, and optional non-canon taste review.
- Stage 2: lettering visual arm, P010–P013 finish rhythm, P010–P013 copy/silence, and shortlist rollup after their prerequisites.
- Stage 3: commercial-clearance and exact-production-base authority after route and candidate dispositions.

Keep the non-canon LitRPG task optional and non-blocking for CH05.

## Evidence

- 24 = 14 candidate + ten route tasks.
- Stage counts 19/4/1; one optional parallel task.
- Every task links an exact local artifact with path/hash.
- All decision, reviewer, and minute fields remain null.
- Dependency targets exist and always point to an earlier stage.
- 16/16 evidence mutations are rejected.

## Consequences

- The checklist reduces navigation and invalid ordering without claiming to prioritize owner preferences.
- Commercial and exact-base review cannot be mistaken for a style or engineering decision.
- The checklist does not ingest approval, start a timer, authorize generation/upload, or accept art.
