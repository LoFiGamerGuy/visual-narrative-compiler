# ADR-0107: Current release rebinds mutable registry without rewriting r1

- Status: accepted
- Date: 2026-09-01

## Context

Integrated release r3 attempt 1 failed because immutable release r2 reproduced a historical manifest validator whose r1 compile inputs included the whole model/license registry file. Later append-only registry notes changed that file hash. Source scope itself passed, and the original 14 manifest rows, prompts, pixels, row root, and gates had not changed.

## Decision

Preserve the failed attempt. Keep release r1/r2 and manifest r1 byte-identical. Add manifest r2 as a pointer that rebinds the current registry to the exact r1 row root with zero row rewrite.

For r3 compatibility, rerun 17 current base checks and pin the historical manifest-validator pass; run the new current manifest-r2 validator as an extension. Normalize only the tracked-safe-path count integer, never failure text or return codes.

## Consequences

- Manifest r2 retains 14 rows/three sequences/14 plans with zero executable, accepted, commercial, lettering-ready, or reproducible rows; 15/15 mutations fail.
- Release r3 passes 13/13 orchestrator commands and 30 effective checks in 6.202 seconds; 23/23 mutations fail.
- Frozen v2.1.1 16 paths and four `baseline_legacy` paths remain byte-identical; baseline remains 0/24 accepted/no tuning.
- The failed attempt hash `160aad9f…f94c` remains evidence; the successful release hash is `f1685919…df7c`.
