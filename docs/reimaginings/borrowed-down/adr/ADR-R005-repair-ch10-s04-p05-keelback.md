# ADR-R005 — Target only CH10-S04-P05 for keelback anatomy repair

- Status: accepted for owner-review draft
- Date: 2026-09-03

## Context

The original CH10-S04 sheet communicated the chain release, but its fifth selected cell rendered the adult keelback mother as a toothed reptilian predator. That contradicted the visual bible's smooth black-crescent anatomy and risked changing the moral meaning of the rescue.

## Decision

Preserve the failed original sheet and its five selected crops as diagnostic evidence. Use that exact sheet as an inspected, hash-pinned ImageGen edit target, then promote only the edited bottom-middle crop as CH10-S04-P05. Rebuild the canonical sheet by inserting the edited fifth cell into the original sheet so cells 1–4 and 6 remain the original pixels.

## Evidence

- The original output remains classified `FAIL` with `keelback_anatomy_violation_toothed_reptilian_predator`.
- The replacement RenderRecord stores the exact edit prompt, both input references, elapsed time, output hashes, and null unavailable provider fields.
- The comparison proves 299 of 299 non-target selected-panel hashes remained unchanged.
- The promoted panel has no teeth, reptilian snout, predatory eyes, or hostile pose.

## Consequences

The active volume contains no failed sequence. The original failure remains auditable rather than overwritten. The replacement is still owner-review-pending, unaccepted, commercially uncleared, and non-reproducible unless proven otherwise.
