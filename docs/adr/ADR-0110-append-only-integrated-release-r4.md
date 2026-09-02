# ADR-0110: Append-only integrated release r4

Date: 2026-09-01

Status: Accepted

## Context

Integrated release r3 preserves 30 effective checks through an immutable release chain. Three subsequent evidence domains now require release binding: the chapter-scale production envelope, the exact future-LitRPG timing reconciliation, and the all-29 RenderRecord completeness audit.

## Decision

Extend r3 append-only with one validator for each new domain. Do not rewrite r3 or its historical stdout. R4 has four orchestrator commands: the complete r3 reproducer plus three extensions.

## Evidence

- `docs/research/evidence/ch05-overnight-integrated-release-gate-r4.json`
- 4/4 commands pass in 6.934 observed seconds.
- 30 immutable base checks + 3 extensions = 33 effective checks.
- 23/23 release-record mutations are rejected.
- 29 RenderRecords, 39 reference uses, and 1,385.036 observed generation seconds reconcile.
- Frozen v2.1.1 covers 16 paths; `baseline_legacy` covers four paths and remains untuned.
- Provider calls/uploads/downloads/cost and accepted/executable/owner-decision state remain zero; human minutes remain null.

## Consequences

Passing r4 establishes evidence integrity only. It does not accept art, infer unavailable service metadata, authorize generation or uploads, revise ComicPanelPlans, establish commercial clearance, or turn chapter scenarios into execution authority.
