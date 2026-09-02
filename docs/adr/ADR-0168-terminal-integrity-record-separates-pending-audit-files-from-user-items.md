# ADR-0168: Terminal integrity record separates pending audit files from user items

Date: 2026-09-01

Status: Accepted

## Context

At terminal audit compile time, four new integrity files are necessarily untracked alongside nine persistent user-owned unrelated items. Treating all 13 as one exclusion class would obscure which files are intended for the final commit.

## Decision

Record the four pending integrity files separately from the nine persistent unrelated user items. Require r13, pointer, safe-source ancestry, frozen/baseline, tracked scope, and current remote parity to pass; require zero unrelated items tracked.

## Evidence

- R13: 9/9 commands and 18 domains; pointer: nine steps; review inventory: 134 links.
- Compile-time tracked paths: 991; safe-source r5 capture: 971 paths and an exact ancestor.
- Frozen/baseline and tracked-source checks pass; compile HEAD equals origin/main.
- Nine persistent unrelated items remain excluded; four named integrity files are pending the final commit.
- Twenty-four/twenty-four mutations fail.

## Consequences

The final commit can add only the audit artifacts while preserving user-owned workspace material. After push, the four pending files become tracked and the nine unrelated items remain the only untracked set.
