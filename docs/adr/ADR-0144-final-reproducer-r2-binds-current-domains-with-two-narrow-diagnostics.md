# ADR-0144: Final reproducer r2 binds current domains with two narrow diagnostics

Date: 2026-09-01

Status: Accepted

## Context

Final reproducer r1 targets the earlier r8/r1 delivery state. Current review needs one compact entry point for release r10, delivery r2, safe-source r2, current cost, and current remote lineage.

## Decision

Create append-only final reproducer matrix r2 with seven independent local domains. Normalize only the decimal tracked-path phrase emitted by safe-source and current-scope validation; bind exact scripts, arguments, input hashes, exit codes, remaining stdout, and normalized stdout hashes.

## Evidence

- Seven/seven domains pass in 108.029 seconds.
- Independent replay passes and rejects 23/23 adversarial mutations.
- Effective state binds 29 candidates, 50 plans, 117 review resources, 835 captured safe paths, frozen 16, baseline 4, 68 zero-cost milestones, and release r10's 66 checks.
- Current delivery/source/release ancestry and `main`/origin configuration pass.
- Network-capable commands, provider activity, spend, owner decisions, acceptance, and executable panels remain zero; human review minutes remain null.

## Consequences

Current handoff reproducibility can be checked with one command while historical r1 remains immutable. The two declared normalizations cannot mask inventory, hash, state, or promotion changes.
