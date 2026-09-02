# ADR-0143: Safe-source r2 pins current release without generated pixels

Date: 2026-09-01

Status: Accepted

## Context

Safe-source parity r1 predates the current delivery bundle, owner hub metadata, cost ledger, and integrated release. A current commit-pinned inventory is needed without tracking ignored generated art or unrelated workspace material.

## Decision

Capture pushed commit `479f7ca7bdc878371db7243e84cc45b6cfef9c07` as append-only safe-source parity r2. Bind every Git path, mode, byte count, blob ID, SHA-256, tree hash, and inventory root; keep r1 immutable.

## Evidence

- 835 tracked paths total 12,795,182 bytes.
- Git tree is `c67628dc7027c16b5e07ebd9cad10d5dbc0a0d04`; inventory root is `ae1563f8a86eed7a68d34b14b38a4c0a2337ac40de6fa90f54513bc815a5fa22`.
- Exactly two approved public controls are tracked.
- Generated experiment paths, candidate pixels, prohibited extensions, files over 10 MiB, credentials, models/LoRAs/datasets/private references, and unrelated untracked items in the inventory are all zero.
- Seventeen/seventeen mutations are rejected; the captured commit was `HEAD` and `origin/main` at emission.

## Consequences

The published safe-source boundary now includes delivery r2 and release r10 evidence while generated pixels remain local, ignored, unpublished, unaccepted, and commercially uncleared.
