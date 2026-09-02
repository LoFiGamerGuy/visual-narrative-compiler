# ADR-0170: Final push r2 preserves and corrects r1 bookkeeping failure

Date: 2026-09-01

Status: Accepted

## Decision

Preserve r1 and its validator failure in commit `7842cce`, then supersede it append-only. R2 records terminal ancestor `7842cce`, exactly nine unrelated user-owned untracked items, two pending r2 source files, and the exact failure cause: pending ADR-0169 was misclassified as unrelated.

## Evidence

R2 passes input/hash/lineage/parity checks and rejects 21/21 mutations. R13 remains 9/9 commands across 18 domains; all owner/provider/promotion state remains zero/null.

## Consequences

The failed record remains auditable while r2 is the authoritative final push record.
