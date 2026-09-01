# ADR-0067: selector r2 does not force historical consumer migration

- Status: accepted
- Date: 2026-09-01

## Context

Selector r2 adds one panel-neutral disconnected/hole mechanics control while preserving the two panel profiles from r1. Existing RenderRecord v2.1 projections, chapter readiness records, exact-base fixture evidence, and selected-route state bind r1 by exact hash. Repointing them merely because r2 exists would rewrite their provenance.

## Decision

Keep all existing r1 bindings immutable. Treat r2 as an append-only topology-coverage contract. A future evidence revision may bind r2 explicitly, but the panel-neutral control must never resolve through the panel-profile consumer interface.

## Consequences

- The six-entry selection pipeline and both complete profile objects are canonically identical between r1 and r2.
- Six source consumers and three immutable evidence bindings remain exact and valid against r1.
- Six/six focused consumer validators pass, including RenderRecord v2.1's 18/18 mutation suite.
- `disconnected_holed_support` resolves to no panel profile and remains ineligible for profile, policy, or visual acceptance.
- Fifteen/fifteen compatibility mutations fail. No record rewrite, production profile, provider request, upload, or cost occurs.

