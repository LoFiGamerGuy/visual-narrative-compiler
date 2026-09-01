# ADR-0070: release gate r2 nests r1 instead of expanding it

- Status: accepted
- Date: 2026-09-01

## Context

Release gate r1 established a measured 53-check boundary. Selector compatibility, the authority frontier, safe-source r2, and later cost ledgers were added afterward. Adding them to r1 would change the meaning of its tracked result.

## Decision

Issue release gate r2. Execute the complete r1 gate as an immutable 53-check base, then run seven named post-r1 validators. Pin r1 by exact report and script hashes and retain timing only as a nondeterministic observation.

## Consequences

- R2 passes 60/60 local checks and rejects 11/11 supersession/base/extension/activity/boundary mutations.
- The observed local runtime is 79.280 seconds: 69.944 seconds for r1 and 9.335 seconds for seven extensions.
- R1 remains byte- and count-stable; its historical 44-core-plus-nine-extension result is not rewritten.
- Network requests, provider calls, uploads, downloads, and external cost remain zero.
- A pass creates no G07 human review, CH05 input approval, upload authority, production cap, provider outcome, acceptance, or commercial clearance.
