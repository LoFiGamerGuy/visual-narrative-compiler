# ADR-0160: Final handoff audit separates consensus from temporal lineage

Date: 2026-09-01

Status: Accepted

## Context

The final hub, links, closeout, release, source, provenance, starter, preflight, and cost ledger were compiled at different append-only milestones. Treating every changed count as a conflict would incorrectly invalidate immutable historical snapshots; ignoring differences would hide genuine drift.

## Decision

Join nine current records into a consistency matrix. Require exact agreement on 12 consensus facts and classify immutable release-r12's 873-path source count versus later source-r4/closeout-r3's 934 paths as one explicit expected temporal-lineage difference. Reject any unexplained conflict or authority expansion.

## Evidence

- Twelve/twelve consensus facts agree: candidates, plans, batches, review links, priority links, pilot roots, cost milestones, release checks, provenance records, owner inputs, authority activity, and provider activity.
- Zero unexplained conflicts.
- One expected lineage delta: 873 to 934 paths (+61) after release r12.
- Owner inputs/decisions/acceptance/clearance/execution/provider calls/uploads/spend remain zero/null.
- Twenty-five/twenty-five mutations fail.

## Consequences

The handoff distinguishes valid append-only history from schema/count drift without rewriting source records. Any future owner input or production transition must create a new record rather than changing this audit.
