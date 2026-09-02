# ADR-0149: Final source capture includes release and audit code

Date: 2026-09-01

Status: Accepted

## Context

Safe-source r2 predates closeout and release r11. A final capture should include the final gate and the audit tools themselves before its inventory is emitted.

## Decision

Commit and push the r3 capture and final-remote-audit tools first, then pin pushed commit `b13d87b66dd7b0877ac364ec0a4bef0168e6beb6` as safe-source r3. Keep prior captures immutable.

## Evidence

- 873 tracked paths total 13,394,576 bytes.
- Git tree is `b6569cd07601fbde3e067e73dbcff48019a25e6e`; inventory root is `49e6a5a083402721b6e846a45cd2f75b05830437bd9162c4045f11afdf5da192`.
- Exactly two approved public controls are tracked.
- Generated experiment paths, candidate pixels, prohibited extensions, files over 10 MiB, credentials, models/LoRAs/datasets/private references, and unrelated untracked items in the inventory are zero.
- Seventeen/seventeen capture mutations are rejected.
- Final remote parity confirms `main`/origin configuration, capture ancestry, release r11 at 74 checks, closeout, frozen integrity, and current source scope.

## Consequences

The final published safe-source lineage contains release r11 and its audit code while generated art remains local, ignored, unpublished, unaccepted, and commercially uncleared.
