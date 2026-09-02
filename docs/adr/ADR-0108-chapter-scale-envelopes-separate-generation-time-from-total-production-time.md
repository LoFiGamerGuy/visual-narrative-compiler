# ADR-0108: Chapter-scale envelopes separate generation time from total production time

- Status: accepted
- Date: 2026-09-01

## Context

CH05 has 14 provisional selected plans and 36 remaining plans in three 12-plan tiers. The observed 26-candidate basis provides generation elapsed p10/median/p90, but the built-in product exposes no monetary cost and no timed owner review exists.

Treating candidate generation seconds as total chapter throughput would omit queueing, retained failures, packet construction, owner review, layout, lettering, and release validation.

## Decision

Publish three generation-only scenarios for the remaining 36: one initial per plan (36), one initial plus 13 bounded repair slots (49), and two arms per plan (72). Derive 13 as `ceil(36 × 9/26)` from the observed nonpass fraction, but label it an allowance rather than a forecast.

Keep monetary cost and human review minutes null. Stage the work through current owner review, P010–P013, Tier A remainder, Tier B, Tier C, and chapter layout/lettering acceptance.

## Consequences

- Median generation-only seconds are 1,844.172 / 2,510.123 / 3,688.344 for 36/49/72 candidates.
- Remaining cadence demand is dominated by nine small object inserts, eight medium character clues, six small sensory inserts, and six wide directional anchors.
- Every one of the 36 rows remains prompt-null and nonexecutable; 25/25 mutations fail.
- The envelope is not an SLA, cost estimate, review-time estimate, or authorization to execute.
