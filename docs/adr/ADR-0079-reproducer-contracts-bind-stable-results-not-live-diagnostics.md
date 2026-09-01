# ADR-0079: reproducer contracts bind stable results, not live diagnostics

- Status: accepted
- Date: 2026-09-01

## Context

Release gate r4 initially failed after the safe-source validator correctly reported a newer live tracked-path count. Reproducer matrix r1 had hashed its full stdout, accidentally treating that mutable leading diagnostic as part of the evidence semantics even though the pinned source inventory and terminal validation result were unchanged.

## Decision

Preserve matrix r1 and issue r2. Continue binding commands, validator hashes, exit state, and no-network expectations, but hash only the last two stable terminal result lines. Explicitly exclude mutable leading diagnostics and document the narrower identity. Use matrix r2 in release gate r4.

## Consequences

- Matrix r2 passes 11/11 commands in an observed 115.394 seconds and rejects 17/17 mutations.
- Release r4 passes the immutable 65-check r3 base plus nine extensions, 74/74 total, in 197.859 seconds and rejects 18/18 mutations.
- The failed first r4 attempt remains visible in the experiment log; no prior evidence was rewritten.
- No semantic validator, frozen target, review boundary, or authority gate was weakened.
- G07 remains 0/20 and CH05 remains zero outcomes/no cap; no approval or external action is proposed.
