# ADR-0123: Current owner hub r4 and link manifest r2

Date: 2026-09-01

Status: Accepted

## Context

Owner hub r3 and the 99-artifact link manifest predate four chapter-scale maps and the dependency-ordered checklist. Rewriting either would break historical handoff hashes.

## Decision

Extend both append-only. Owner hub r4 links r3, the tracked checklist, and the readiness, reference-risk, sequence-batch, and lettering maps. Link manifest r2 preserves all 99 r1 artifacts and adds those six current resources.

## Evidence

- Hub r4: six links (four images, one HTML, one text), five ignored build artifacts, two byte-identical builds, 15/15 mutations rejected.
- Link manifest r2: 105 = 99 + six unique resources; 104 ignored local artifacts + one tracked checklist.
- Every current path, absolute path, hash, byte count, Git state, and Markdown link validates.
- 14/14 link-manifest mutations are rejected.

## Consequences

- `experiments/review-packets/ch05-owner-review-index-r4/index.html` is the current single local review entry point.
- `docs/research/ch05-review-links-r2.md` is the exhaustive current absolute-link inventory.
- Generated pixels remain ignored, unpublished, unaccepted, and commercially uncleared.
- Decisions, review minutes, provider activity, and cost remain zero/null.
