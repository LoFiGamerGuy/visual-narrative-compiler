# ADR-0128: R8 compatibility normalizes only the live tracked count

Date: 2026-09-01

Status: Accepted

## Context

Release r8 passed before commit, then its exact post-commit reproduction failed in the safe-source child command. The pinned 735-path inventory, hashes, return code, and semantic state were unchanged; only `validate_tracked_source_scope.py` reported the larger live tracked-path count created by committing r8 itself.

## Decision

Preserve r8 and the failed post-commit attempt. Add an append-only compatibility validator that replaces only the decimal prefix in the phrase `N tracked safe-source paths` for the safe-source command. Do not normalize inventory contents, hashes, scripts, return codes, other stdout, stderr, release state, or activity fields.

## Evidence

- The original r8 validator retains 26/26 semantic mutation rejection and reports exactly one reproducer mismatch.
- Four/four compatibility reproductions have matching normalized stdout hashes.
- Exactly one of four commands uses `TRACKED_COUNT_ONLY`; the other three use no normalization.
- The captured inventory remains 735 paths / 11,861,823 bytes at root `fea9401e…4ca`.
- Ten/ten compatibility-scope and state mutations are rejected.

## Consequences

Future release wrappers must use the narrow r8 compatibility validator rather than the raw r8 validator. The historical r8 evidence and failed attempt remain unchanged and auditable.
