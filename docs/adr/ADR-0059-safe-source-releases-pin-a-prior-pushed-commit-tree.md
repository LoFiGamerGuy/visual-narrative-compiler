# ADR-0059: safe-source releases pin a prior pushed commit tree

- Status: accepted
- Date: 2026-09-01

## Context

A manifest stored inside the commit it identifies cannot include its own final commit ID without a self-reference. Reporting only the working tree also cannot prove what was pushed.

## Decision

Capture the exact already-pushed parent commit, tree, and every blob's path/mode/size/Git object ID/SHA-256. Store that manifest in the following commit. Separately validate that the captured commit is an ancestor, current tracked scope remains safe, and current HEAD matches `origin/main` after push.

## Consequences

- Release baseline `f5057885…c64ad3` pins 346 paths / 8,184,364 bytes, tree `df2c40bb…c5e67`, and inventory root `2993f2d4…a52cde`.
- Exactly the two approved public controls are present; generated experiment paths, prohibited model/key extensions, and files over 10 MiB are zero.
- Eight/eight commit/tree/count/root/blob/exclusion mutations fail.
- Generated candidates, `.env`/credentials, models/LoRAs, datasets/private references, local runtimes, local manifests, and archives remain explicitly excluded.
