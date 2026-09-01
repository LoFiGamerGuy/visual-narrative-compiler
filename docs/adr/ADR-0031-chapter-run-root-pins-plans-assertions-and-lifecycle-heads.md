# ADR-0031: chapter run root pins plans, assertions, and lifecycle heads

- Status: accepted
- Date: 2026-09-01

## Context

Chapter-scale status can look healthier if reports omit missing panels, change plan revisions, swap assertions, or count only attempted/accepted items. Per-panel records need a compact chapter identity that detects those changes while preserving the full 50-panel denominator.

## Decision

Compute a deterministic SHA-256 chapter root over ordered tuples of stable panel ID, plan revision ID, applicable hard-assertion hash, and run-ledger chain head. The tracked CH05 r1 root covers display order 1–50 and starts every panel at `BASE_APPROVAL_PENDING`. Stage reports always retain all 50 planned panels and separately report attempted, completed, reviewed, and accepted counts.

Compiler timing and task counts remain separate from provider/human throughput. A changed root requires an explicit new manifest revision and explanation; it cannot silently replace r1.

## Consequences

- CH05 r1 root is `0498d79f705334babc60420a974a910a08c9bb9e15fb782d50f9335f43673664`.
- Plan, assertion, chain-head, or panel-order mutations are detectable.
- The six-panel demonstration slice remains a subset, not the chapter denominator.
- The root proves record integrity only; it is not rendered coverage or acceptance.
