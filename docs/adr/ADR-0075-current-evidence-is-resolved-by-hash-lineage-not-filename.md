# ADR-0075: current evidence is resolved by hash lineage, not filename

- Status: accepted
- Date: 2026-09-01

## Context

The project now has multiple append-only revisions across budget, selector, rebuild, release, source, handoff, and cost evidence. Filenames communicate revision intent but do not prove that every `supersedes` pointer matches the prior bytes or identify the current validator consistently.

## Decision

Create a machine-validated current-evidence index. For each domain, follow exact `supersedes` path/identity/hash links from the declared current record to the root, and bind a no-network reproducer command and validator hash.

## Consequences

- Eleven current domains resolve across 32 exact lineage records; the CH05 cost chain contributes 14 append-only revisions.
- Every supersession identity/hash and current validator path/hash validates.
- Current summary remains 65/65 release checks, 412 safe-source paths, 41 zero-cost milestones, G07 0/20, and CH05 zero accepted/no cap.
- Eighteen/eighteen lineage/current-state/activity mutations fail.
- The index is navigation and provenance evidence only; it creates no experiment result, review, authority, or acceptance.
