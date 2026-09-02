# ADR-0158: Safe-source r4 pins final review release and contracts

Date: 2026-09-01

Status: Accepted

## Context

Safe-source r3 predates release r12, the strict owner response/timer/starter/preflight contracts, and owner hub r8/link r6. A final source claim should inventory a pushed commit containing those artifacts without self-referencing its own inventory record.

## Decision

Commit and push the r4 validator first, then capture that exact pushed commit. Bind immutable r3 ancestry, release r12, link r6, and the final review starter. Preserve ignored pixels and unrelated workspace items outside the tracked inventory.

## Evidence

- Captured pushed commit: `df41783`.
- 934 tracked paths and 14,070,835 bytes.
- Tree: `f5d1a7b65635874eb7b3048f14e7f61a419e0c53`.
- Inventory root: `c512c072d378cefce2f20c9bb154ad2bee83a411229964c06a310e864df71f07`.
- Two public controls; zero generated experiment paths, generated candidate pixels, prohibited extensions, credentials, oversize files, model/LoRA/dataset/private-reference paths, or unrelated untracked items.
- Nineteen/nineteen mutations fail.

## Consequences

The pushed source frontier now contains release r12 and every current review-session contract while generated art remains local and ignored. The capture is an ancestor of its append-only evidence record, avoiding impossible self-inventory.
