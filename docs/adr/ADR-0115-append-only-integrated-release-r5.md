# ADR-0115: Append-only integrated release r5

Date: 2026-09-01

Status: Accepted

## Context

Five independently reproducible validators were added after r4: owner index r3, the exact 99-artifact link manifest, the measured route/decision matrix, the P010–P013 production-manifest dry run, and the P010–P013 review-contract dry run.

## Decision

Extend immutable r4 with all five validators. Count the owner hub and exhaustive link inventory separately because they have different source, ignore, link, and mutation boundaries.

## Evidence

- Six/six orchestrator commands pass in 9.346 observed seconds.
- 33 immutable base checks + five extensions = 38 effective checks.
- 26/26 release-state mutations are rejected.
- Effective state binds 29 candidates, 99 review artifacts, a 14-candidate shortlist, ten pending route decisions, four next candidate slots, two repair slots, and 44 next-review checks.
- Frozen v2.1.1 16-path and `baseline_legacy` four-path validation remain inherited and passing.
- Calls/uploads/downloads/cost, owner decisions, accepted candidates, and executable panels remain zero; human minutes remain null.

## Consequences

Passing r5 establishes integrated evidence integrity only. It does not accept art, ingest decisions, compile prompts, authorize uploads, revise ComicPanelPlans, grant commercial clearance, or select an exact production base.
