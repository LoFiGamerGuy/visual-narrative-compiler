# ADR-0120: Append-only integrated release r6

Date: 2026-09-01

Status: Accepted

## Context

Four independent post-r5 domains now cover chapter readiness, minimal reference/continuity risk, live-only review-time instrumentation, and dependency-ordered owner handoff.

## Decision

Extend immutable r5 with all four validators, preserving its 38 effective checks and adding no compatibility normalization.

## Evidence

- Five/five orchestrator commands pass in 9.946 observed seconds.
- 38 immutable base checks + four extensions = 42 effective checks.
- 26/26 release-state mutations are rejected.
- Effective state binds 50 plans, 42 reference hypotheses, 18 text-only rows, one critical P036 guard, 24 owner tasks, and 39 timer subjects.
- Frozen v2.1.1 16-path and `baseline_legacy` four-path integrity remain inherited.
- Prompts, live review events, decisions, acceptance, execution, calls, uploads, downloads, and cost remain zero; minutes remain null.

## Consequences

Release r6 establishes evidence integrity only. It does not authorize generation, ingest review, infer identity, upload references, revise plans, accept art, or grant commercial clearance.
