# ADR-0099: Owner review drafts are not project decisions

- Status: accepted
- Date: 2026-09-01

## Context

The owner decision contract has 39 pending subjects and zero decisions, events, or measured review minutes. A single browsable surface is useful, but browser selections lack an immutable session, event time, reviewer attestation, and contract-validated ingestion.

## Decision

Provide an ignored, offline worksheet bound to the exact contract and owner-review index. It may export a `LOCAL_UNINGESTED_DRAFT` JSON file, but it cannot modify the repository, contract, ComicPanelPlans, acceptance state, or generation authority.

Treat a draft as project evidence only after a separate fail-closed ingestion validator checks the contract hash, subject identifiers, allowed decisions, completeness rules, and append-only event envelope. Until then, all 39 subjects remain pending.

## Consequences

- One local HTML surface links 29 candidates and ten higher-order review artifacts.
- Consecutive builds are byte-identical; all 39 links resolve and 8/8 boundary mutations fail.
- Network calls, uploads, repository writes, recorded decisions, and human-review minutes remain 0/0/0/0/null.
- The next milestone is a validator for exported drafts, exercised only on synthetic local fixtures.
