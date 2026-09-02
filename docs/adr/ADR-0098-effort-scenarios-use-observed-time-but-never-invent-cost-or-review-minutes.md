# ADR-0098: Effort scenarios use observed time but never invent cost or review minutes

- Status: accepted
- Date: 2026-09-01

## Context

The 26 CH05 production-research candidates total 1,230.058 observed built-in generation seconds. Candidate elapsed p10/median/p90 is 30.531/51.227/56.524 seconds; 17/26 pass all engineering dimensions and 9/26 are warn/fail. Built-in monetary cost/usage and timed owner-review minutes are unavailable.

Tier A contains 12 plans. Three nonexecuted scenarios describe one initial per plan (12), one initial plus four bounded repair slots (16), and two arms per plan (24). Four repair slots round 12 × the observed 9/26 non-pass fraction; this is a planning allowance, not a forecast.

## Decision

Use the 16-candidate scenario as the post-review planning envelope only if Tier A is later authorized. Keep monetary cost and human-review time null. Do not label unknown built-in cost `$0` or convert untimed review into an estimate.

Keep all 12 provisional style/size assignments as hypotheses with zero prompts and zero execution authority. Use the 39-subject append-only decision contract to record exact candidate, concept, sequence, cadence, style, density, and lettering choices before any Tier A prompt compilation.

## Consequences

- The median observed generation-only scenario times are 614.724s/819.632s/1,229.448s for 12/16/24 candidates.
- No scenario includes queue delay, retries beyond its candidate count, human review, downstream layout, or commercial clearance work.
- No owner decision, prompt, provider call, upload, or acceptance is fabricated.
