# ADR-0127: Integrated release r8 binds delivery, source, and cost evidence

Date: 2026-09-01

Status: Accepted

## Context

Release r7 covers chapter sequence, lettering, and review-link evidence but predates the consolidated delivery bundle and commit-pinned safe-source capture.

## Decision

Preserve r7 byte-for-byte and add three independent extensions: delivery-bundle validation, CH05 cost-ledger r24 validation, and safe-source delivery parity validation. Use ancestry mode for the pinned source capture so later append-only commits cannot invalidate its historical pushed-parity claim.

## Evidence

- Four/four orchestrator commands pass in 30.259 observed seconds.
- 46 immutable base checks plus three extensions equals 49 effective checks.
- Twenty-six/twenty-six release-state mutations are rejected.
- Effective state binds 29 candidates, 50 plans, 12 batches, 105 review links, 14 strongest candidates, ten pending owner decisions, 735 safe-source paths, and 52 zero-external-cost milestones.
- Frozen v2.1.1 16-path and `baseline_legacy` four-path integrity remain inherited.
- Acceptance, commercial clearance, executable panels, owner decisions, calls, uploads, downloads, and paid spend remain zero; human minutes remain null.

## Consequences

Release r8 is the current integrated handoff gate. It does not ingest review, accept or commercially clear art, compile prompts, authorize generation/upload, revise ComicPanelPlans, or create cross-medium planning records.
