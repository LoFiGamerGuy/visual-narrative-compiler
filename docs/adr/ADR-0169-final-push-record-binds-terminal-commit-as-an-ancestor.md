# ADR-0169: Final push record binds terminal commit as an ancestor

Date: 2026-09-01

Status: Accepted

## Decision

Record pushed commit `153bff7` as the terminal validated ancestor, with exact main/origin parity, 996 tracked paths, nine excluded user-owned untracked items, r13 9/9/18, 134 links, 29 candidates, and ten remaining decisions. The record itself is append-only and therefore lands in a later final commit.

## Evidence

The record validates 21/21 mutations, all input hashes, commit ancestry, remote parity, and zero owner/provider/promotion activity.

## Consequences

The final response may cite the later containing commit while retaining `153bff7` as the exact pre-record terminal state. Owner review remains next.
