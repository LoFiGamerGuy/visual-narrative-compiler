# ADR-0138: Duration capacity uses quantiles, not calendar or cost forecasts

Date: 2026-09-01

Status: Accepted

## Context

Chapter batches have a lifecycle and evidence order but no per-batch generation-capacity view. Human review, built-in cost, and queue timing are unavailable.

## Decision

Use exact p10/median/p90 generation seconds from 26 CH05 candidates. Allocate the prior 13-slot remaining-plan repair ceiling by reserving two for seq03 and distributing 11 across other remaining-plan counts via largest remainder. Report batch and wave generation-only ranges. Add a separate fresh 50-plan consistency arm if all existing selections are rejected.

## Evidence

- Remaining-plan arm: 36 initials + 13 repair slots = 49 candidates.
- Exact p10/median/p90 totals are 1,496.019 / 2,510.123 / 2,769.676 seconds.
- Wave candidate loads are 6 / 12 / 20 / 11.
- Fresh consistency arm: 50 initials + 18 repairs = 68 candidates; median 3,483.436 seconds.
- The 1800×1580 chart builds deterministically; visual QA moved short-bar labels outside the bars.
- Eighteen/eighteen mutations are rejected.

## Consequences

These are generation-only planning envelopes, not calendar forecasts or authorization. Review, layout, lettering, diagnostics, retries, queue time, human minutes, and built-in monetary cost remain excluded/null.
