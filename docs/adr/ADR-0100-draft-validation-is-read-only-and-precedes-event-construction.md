# ADR-0100: Draft validation is read-only and precedes event construction

- Status: accepted
- Date: 2026-09-01

## Context

ADR-0099 permits an offline worksheet to export a local draft but forbids treating browser state as a project decision. A malformed or stale draft could otherwise name an unknown subject, use a decision outside that subject's vocabulary, bind the wrong contract, duplicate a subject, or smuggle event/acceptance fields into draft data.

## Decision

Validate exported drafts read-only against the exact contract identifier/hash, subject type and allowed decision vocabulary. Reject duplicate/unknown subjects, unsupported fields, weakened draft boundaries, and any selected decision without a reviewer.

Do not construct timestamps, minutes, event hashes, acceptance state, ComicPanelPlan revisions, or repository writes during validation. Event construction remains a separate explicit operation after owner review.

## Consequences

- Three synthetic valid draft shapes pass; 14 malformed fixtures fail.
- Sixteen/sixteen evidence mutations fail.
- The live contract remains 39 pending subjects, zero decisions/events, and null human minutes.
- Hair, wardrobe, and role assertions can now be hardened independently without conflating visual engineering with owner judgment.
