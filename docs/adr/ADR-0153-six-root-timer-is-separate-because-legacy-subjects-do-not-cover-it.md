# ADR-0153: Six-root timer is separate because legacy subjects do not cover it

Date: 2026-09-01

Status: Accepted

## Context

The immutable 39-subject review timer predates the exact pilot-root response contract. Only three roots map directly; `lettering_semantics`, `p010_p013_finish_rhythm`, and `p010_p013_copy` have no timer subject. Claiming full coverage would fabricate review-time provenance.

## Decision

Keep the 39-subject contract unchanged and create a separate append-only six-root live-timer contract. Use identical live-only event semantics but exact root IDs and allowed decisions. Do not infer or backfill time.

## Evidence

- Six roots partition into three exact legacy mappings and three explicitly missing mappings.
- The new contract has four event types, seven fields, and six rules.
- Three/three valid synthetic logs pass and 12/12 malformed logs fail.
- Nineteen/nineteen evidence mutations are rejected.
- Actual events/completions/minutes/decisions remain 0/0/null/0.

## Consequences

Future response minutes can be proven without rewriting history or conflating candidate/sequence review with root-decision review. Validation still does not ingest decisions or enable production.
