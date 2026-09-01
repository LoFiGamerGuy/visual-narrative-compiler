# ADR-0065: rebuild inventories advance append-only with new artifact groups

- Status: accepted
- Date: 2026-09-01

## Context

Rebuild r1 deliberately bounded eight artifact groups. Adding disconnected/hole outputs to r1 would change its 26-file root and erase the scope of its original reproducibility claim.

## Decision

Issue rebuild r2, pinning r1 and its root. Preserve all commands/groups/exclusions, append the disconnected/hole validator and ninth output group, then perform two complete expanded rebuilds.

## Consequences

- R2 inventories 28 artifacts / nine groups / 4,868,771 bytes with identical roots `18816d3c…e50d64` across both passes.
- The only new artifacts are the disconnected/hole support and selected alpha.
- Ten/ten supersession, rewrite, group/count/root/identity/artifact/activity mutations fail.
- Provider output, timestamps, human evidence, and external runtimes remain excluded; no cross-platform or visual-quality claim follows.
