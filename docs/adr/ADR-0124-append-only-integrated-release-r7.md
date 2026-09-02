# ADR-0124: Append-only integrated release r7

Date: 2026-09-01

Status: Accepted

## Context

Four post-r6 validators cover coherent sequence batches, chapter-wide lettering semantics, owner hub r4, and exhaustive review links r2.

## Decision

Extend immutable r6 with all four validators, preserving 42 effective checks and adding no normalization.

## Evidence

- Five/five orchestrator commands pass in 14.531 observed seconds.
- 42 immutable base checks + four extensions = 46 effective checks.
- 25/25 release-state mutations are rejected.
- Effective state binds 12 sequences, 50 lettering rows, 105 review links, 24 owner tasks, and zero next prompts.
- Frozen v2.1.1 16-path and `baseline_legacy` four-path validation remain inherited.
- Review, decisions, acceptance, execution, provider activity, and cost remain zero/null.

## Consequences

Release r7 is the current integrated engineering gate. It does not bind final copy, ingest review, authorize generation/upload, revise plans, accept art, or grant commercial clearance.
