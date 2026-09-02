# ADR-0111: Local review hub and exact link manifest

Date: 2026-09-01

Status: Accepted

## Context

Owner review index r2 predates the chapter-scale envelope and RenderRecord audit. Final handoff also requires direct links to every contact sheet, sequence packet, lettering overlay, and strongest individual candidate. Depending on ad hoc prose risks omission and stale local paths.

## Decision

1. Extend r2 append-only with a deterministic r3 local hub; do not rewrite r1 or r2.
2. Compile a tracked, hash-pinned artifact manifest plus generated Markdown containing repository-relative and current absolute local paths.
3. Treat the 14 strongest-candidate links as a provisional engineering shortlist only. Do not turn link inclusion into acceptance or commercial clearance.
4. Keep every linked generated pixel and local HTML packet ignored and unpublished.

## Evidence

- R3 hub: 12 links (10 images, two HTML), 11 ignored build artifacts, two byte-identical builds, and 13/13 rejected mutations.
- Exact link manifest: 99 unique artifacts and 99 categorized links: four review hubs, ten contact sheets, nine sequence deliverables, 34 lettering overlays/comparisons, 14 provisional strongest candidates, three non-canon LitRPG concepts, 11 diagnostic/policy sheets, and 14 packet records.
- Manifest validator rejects 15/15 mutations and validates every path, hash, byte count, ignore state, absolute path, and Markdown link.
- Attempt 1 is preserved: its validator incorrectly expected 100 unique artifacts, 33 lettering overlays, and 13 diagnostic sheets. Observed compiler output was left unchanged; only declared expectations were corrected.

## Consequences

- `experiments/review-packets/ch05-owner-review-index-r3/index.html` is the current single local review entry point.
- `docs/research/ch05-review-links-r1.md` is the exhaustive direct-link handoff for this workspace.
- Absolute links must be recompiled if the repository moves.
- Owner decisions, acceptance, publication, calls, uploads, cost, and human minutes remain zero/zero/zero/zero/zero/$0/null.
