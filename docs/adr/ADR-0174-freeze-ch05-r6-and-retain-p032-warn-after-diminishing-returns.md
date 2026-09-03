# ADR-0174: Freeze CH05 r6 and retain P032 WARN after diminishing returns

- Status: Accepted engineering stop rule; owner review pending
- Date: 2026-09-02

## Context

R5 had two agent WARN panels: P029 role separation and P032 reversed footprint orientation. One final paired generation produced a strong P029 repair, but its P032 crop still did not make broad toe versus narrow heel direction unambiguous at 390 pixels. This is the second targeted P032 attempt.

## Decision

Select only P029 from the final strip. Keep the new P032 crop as diagnostic evidence, retain the prior P032 selection in the complete chapter, and leave P032 as WARN. Freeze further stochastic CH05 visual repairs until owner review.

Any future P032 work should test a deterministic local visual aid/composite, an explicit plan revision, or a different authorized rendering mechanism. Repeating the same built-in prompt strategy is lower information.

## Evidence

- R6 changes one selected panel and preserves 49/49 non-target r5 source hashes.
- P029 clearly separates Sigrid entering through the collapsed wall from Soren guarding outside.
- Current non-gating triage is 49 PASS / 1 WARN / 0 FAIL.
- P032 has two preserved repair attempts; both improve print visibility but not enough to prove reversed orientation at phone width.
- The newest P032 candidate is explicitly diagnostic and absent from r6 assembly.

## Consequences

R6 becomes the CH05 owner-review baseline. The one remaining warning is visible rather than hidden. Generation capacity can now move to chapter planning/production or a separate non-canon LitRPG design track without endless micro-repair.

No human acceptance, canon revision, commercial clearance, or exact production-base decision is made.
