# ADR-0142: Integrated release r10 binds current delivery and narrow live scope

Date: 2026-09-01

Status: Accepted

## Context

Release r9 predates duration capacity, the operator playbook, delivery bundle r2, hub r6, link manifest r4, and cost ledger r27. Current tracked-source validation also reports a live path count that necessarily changes after later safe-source commits.

## Decision

Extend immutable r9 with eight independent current domains. Normalize only the decimal path count in the tracked-source validator's diagnostic line; preserve its exit code, all other stdout, script hash, scope semantics, and every evidence binding.

## Evidence

- Nine/nine orchestrated commands pass in 89.568 seconds, representing immutable 58 plus eight = 66 effective checks.
- The independent release validator reproduces all commands and rejects 34/34 mutations.
- Effective state binds 29 candidates, 50 plans, 12 batches, 117 links, 49/68 capacity arms, 12 operating steps, 68 zero-cost milestones, frozen 16, and baseline 4.
- Network-capable commands, provider calls, uploads, downloads, paid spend, decisions, acceptance, commercial clearance, and executable panels remain zero; review minutes remain null.

## Consequences

R10 is the current integrated engineering gate. The narrow live diagnostic normalization is explicit and cannot expand to inventory, semantic, or arbitrary stdout changes.
