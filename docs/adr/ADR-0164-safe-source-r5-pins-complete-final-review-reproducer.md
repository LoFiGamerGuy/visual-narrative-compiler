# ADR-0164: Safe-source r5 pins complete final review reproducer

Date: 2026-09-01

Status: Accepted

## Context

Safe-source r4 predates final reproducer r3, hub r9/link r7, and the candidate disposition worksheet. The final pushed frontier should contain the exact compact validation path delivered to the owner.

## Decision

Commit and push the r5 validator, then capture that exact pushed commit. Bind safe-source r4 ancestry, reproducer r3, link r7, and the null candidate worksheet without self-inventory.

## Evidence

- Captured pushed commit: `eafe1ef`.
- 971 tracked paths and 14,675,859 bytes.
- Tree: `4bcd007bb6d643a83f6a074d9ed169b7195eb4e2`.
- Inventory root: `7c5cb05b1b1bfc7398215a49da6a2a4f4ef7767783c0d9a725e79289b78ab2df`.
- Ten reproducer domains, 134 review links, 14 worksheet candidates, and 112 worksheet checks bound.
- Two public controls and zero generated/prohibited/credential/model/dataset/private-reference/unrelated tracked paths.
- Eighteen/eighteen mutations fail.

## Consequences

The complete review reproducer and owner surface are now inside a pushed safe-source frontier, while generated pixels and review responses remain local/ignored. The capture remains an ancestor of its append-only evidence record.
