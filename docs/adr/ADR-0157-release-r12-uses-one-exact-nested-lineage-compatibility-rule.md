# ADR-0157: Release r12 uses one exact nested-lineage compatibility rule

Date: 2026-09-01

Status: Accepted

## Context

The first r12 run passed all ten current extensions but immutable r11 failed because its final-reproducer-r2 dependency now reports one nested `integrated_release_r10` lineage mismatch after later append-only commits. Rewriting r10, r11, or the final reproducer would destroy historical evidence.

## Decision

Preserve the 10/11 attempt and add a compatibility validator that accepts only the exact r11 return code, empty stderr, full stdout, and single named nested-reproducer mismatch. Continue to validate r11's recorded state and reject mutations. Use that wrapper as the immutable 74-check base of r12, then run ten current extensions including frozen and tracked-source integrity.

## Evidence

- Attempt 1 is preserved with 10/11 passing and only the final-reproducer-r2 mismatch.
- The compatibility validator accepts the exact mismatch and rejects 8/8 r11 state mutations.
- Release r12 passes 11/11 commands in 139.975 seconds, representing 84 effective checks.
- Independent replay passes and rejects 33/33 state, activity, planning, result, normalization, and denominator mutations.
- Ledger r29 records 82 zero-external-cost milestones with 0 requests, 0 uploads, and $0 paid API/cloud spend.

## Consequences

Historical releases remain immutable and later append-only lineage is explicit. The compatibility rule cannot accept a second mismatch, stderr, changed wording, changed return code, broader normalization, or altered promotion state. Owner inputs, ingestion, prompts, acceptance, rights, and execution remain closed.
