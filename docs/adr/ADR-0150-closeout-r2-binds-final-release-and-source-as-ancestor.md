# ADR-0150: Closeout r2 binds final release and source as ancestor

Date: 2026-09-01

Status: Accepted

## Context

Closeout r1 predates release r11 and safe-source r3. Rewriting r1 would erase its exact compile boundary; claiming that r3 inventories a later closeout record would be self-referential.

## Decision

Create append-only closeout r2. Bind release r11, safe-source r3, current parity, and a refreshed changed-file inventory. Represent r3 correctly as an exact ancestor capture rather than pretending it contains r2.

## Evidence

- The handoff preserves 29 candidates, 50 plans, 12 batches, 122 resources, and 67 priority direct links.
- Release 74, safe-source 873 paths/13,394,576 bytes, frozen 16 + baseline 4, and 73 zero-cost milestones reconcile.
- The current base has 410 changed paths and 65 ADRs since `e011cac`; `HEAD` equaled `origin/main` at compile.
- The final capture is a verified ancestor of the base commit.
- Twenty-one/twenty-one mutations are rejected.

## Consequences

The final handoff exposes current evidence without self-referential provenance or promotion. Closeout r1 and all historical source captures remain immutable.
