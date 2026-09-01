# ADR-0054: seam-review summary fields must be derived from the session chain

- Status: accepted
- Date: 2026-09-01

## Context

RenderRecord v2.1 originally checked the shape of a seam-session reference and duplicated reviewer/minutes/assertion fields. Without loading the referenced session, those summaries could disagree with its immutable event chain or could count a validation fixture as real human evidence.

## Decision

Load and hash-check the exact visual-measurement subject and timed-review session. Validate the session event chain, subject, reviewer, derived active minutes, fixture eligibility, terminal decision, and the boundary/causality/protected-semantics/lettering-clearance assertions. Duplicated RenderRecord fields must exactly match the session-derived values.

## Consequences

- The completed synthetic fixture binds the tracked exact-base measurement packet as its sole review subject and computes three active minutes from START to COMPLETE.
- Its accepted four-assertion decision can validate mechanics, but `validation_fixture=true` keeps `review_evidence_eligible=false`.
- A real RenderRecord would require a non-fixture session whose derived eligibility is true.
- Eighteen/eighteen RenderRecord mutations now reject session hash, reviewer, timing, subject/evidence hash, outcome, and unknown-state contradictions.
- Real CH05 seam sessions, human minutes, and accepted outcomes remain zero/null/zero.
