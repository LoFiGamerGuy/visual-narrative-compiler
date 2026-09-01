# ADR-0066: release validation keeps the pinned core and append-only extensions separate

- Status: accepted
- Date: 2026-09-01

## Context

The historical CH05 instrumentation suite is pinned at 44 checks. Later safe-source, aggregate-budget, transport, selected-route state, topology, selector, rebuild, and cost-ledger validators must be checked together without changing that suite's count or frozen semantics. Transport hardening also changed two adapter source hashes after aggregate-budget audit r2 was recorded.

## Decision

Create a separate hardening-release orchestrator. It executes the unchanged 44-check suite first, then nine named append-only validators. Preserve aggregate-budget audit r2 and issue r3 with the new adapter hashes and an exact r2 supersession binding; never rewrite historical evidence to make a release gate pass.

## Consequences

- The release gate passes 44 core plus nine extension checks, 53/53 total, and rejects 8/8 release-state mutations.
- Aggregate-budget audit r3 confirms 4/4 adapters use the shared ledger before paid submission, reconciles 18 entries and $1.057377 actual spend, and rejects 12/12 mutations.
- The tracked timing observation is 69.752 seconds on this local runtime and is explicitly nondeterministic.
- The gate performs zero network requests, provider calls, uploads, model downloads, or external spend.
- A pass is mechanics and governance evidence only. It creates no human review, art acceptance, commercial clearance, production cap, upload authority, or CH05 outcome.
