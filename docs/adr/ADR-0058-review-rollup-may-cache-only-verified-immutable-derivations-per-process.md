# ADR-0058: review rollup may cache only verified immutable derivations per process

- Status: accepted
- Date: 2026-09-01

## Context

The fail-closed G07 rollup rebuilt and re-encoded the exact blinded packet inside every fixture and mutation compile. One suite pass therefore derived the same packet five times, taking 10.615 seconds while adding no new evidence.

## Decision

Derive and validate the packet and expected deblinding mapping root once in `main`, then pass that root to subsequent compiles in the same process. Keep the standalone `compile_rollup` fallback that recomputes the root when a verified root is not supplied. Do not cache across processes or trust caller-supplied mappings without root comparison.

## Consequences

- The pending gate hash remains `927e76a3…224b78c`, and 9/9 pending/fixture/coverage/mapping mutations still fail.
- Five optimized wall-clock samples are 1.700–1.709 seconds, median 1.706 seconds, versus the pinned 10.615-second suite baseline: 83.93% lower elapsed time / 6.22x speedup on this machine.
- Review state remains 0/20 decisions, null minutes, zero accepted, and no human arm results, composite, ranking, or route change.
- This is validator runtime engineering, not human-review or provider-throughput evidence.
