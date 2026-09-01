# ADR-0078: review and authority actions remain separate and blank

- Status: accepted
- Date: 2026-09-01

## Context

The authority graph identifies five roots, but a reviewer-facing handoff could still conflate G07 judgment, P036 input approval, upload scope, and production budget. A compact packet is useful only if it cannot imply that any field has been decided.

## Decision

Create a hash-bound handoff packet with one identified-human G07 review action and four distinct CH05 root items. Preserve null reviewer/session/minutes/decision/input/cap/authority/reservation fields, keep the primary-document refresh trigger separate, and leave both approval requests and next external action empty.

## Consequences

- The local packet exposes 16 blinded candidate and four repeat-pair presentations requiring 20 timed decisions; 0 are complete.
- Four CH05 roots remain exact base, exact mask, exact external authority, and distinct production cap/reservation capacity.
- G07 remains $1.057377 actual/$98.942623 available and cannot fund or authorize CH05; CH05 stays no-cap/$0.
- Eleven reproducers, 65 release checks, and frozen-target integrity are bound as current readiness evidence.
- Nineteen/nineteen fabrication/conflation/activity mutations fail; no approval is requested and no external action is proposed.
