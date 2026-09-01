# ADR-0076: current evidence must have an executed reproducer matrix

- Status: accepted
- Date: 2026-09-01

## Context

The lineage index proves record and validator identity, but a valid command can still fail under the current runtime or depend on stale generated state. Current-handoff confidence therefore requires executing the commands rather than only recording them.

## Decision

Run all 11 current lineage-domain commands sequentially in their recorded order. Bind validator hashes, command arguments, normalized stdout hashes, exit state, and local timing. Require empty stderr and no command declared network-capable.

## Consequences

- All 11/11 commands pass, including the 65-check release gate, exact artifact rebuild, safe-source inventory, and G07 review gate.
- Total observed local runtime is 114.636 seconds; release/rebuild/source checks account for 79.872/23.043/8.466 seconds.
- Seventeen/seventeen command/result/hash/activity/limitation mutations fail.
- This proves current local evidence reproducibility under the measured runtime, not provider-output reproducibility across new calls.
- No request, upload, model download, external spend, human judgment, or CH05 authority is created.
