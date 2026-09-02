# ADR-0126: Safe-source delivery parity is commit-pinned

Date: 2026-09-01

Status: Accepted

## Context

The consolidated delivery bundle links ignored generated pixels while committing only source and non-art evidence. Current working-tree inspection alone would not prove what was actually pushed.

## Decision

Pin the complete Git inventory of pushed delivery commit `a1454db0ec0fbe80bda7c88a55764047c62618b4`. Validate every blob hash, repository scope, size boundary, the exact two public controls, delivery evidence lineage, capture ancestry, current tracked scope, and remote parity. Keep ignored generated material and unrelated untracked workspace files outside the inventory.

## Evidence

- 735 tracked paths total 11,861,823 bytes.
- Captured tree is `7a7085da8b3fc320defa27233121f0afdff32c4d`.
- Inventory root is `fea9401edf72cbbaac3a5357088d7b14848886cfe7f5d163268354238063c4ca`.
- Exactly two approved public controls are tracked.
- Generated experiment paths, prohibited extensions, files over 10 MiB, credentials, generated candidate pixels, model weights/LoRAs/datasets/private references, and unrelated untracked items are all zero.
- Sixteen/sixteen mutations are rejected.

## Consequences

The pushed delivery commit has reproducible safe-source provenance. The parity record itself is an append-only descendant and does not claim that ignored review pixels were published, accepted, or commercially cleared.
