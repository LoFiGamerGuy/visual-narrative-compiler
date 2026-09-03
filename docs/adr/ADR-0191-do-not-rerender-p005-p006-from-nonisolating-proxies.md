# ADR-0191: Do not rerender P005-to-P006 from non-isolating proxies

## Status

Accepted as an engineering recommendation. The owner-facing visual-risk flag remains; no candidate, route, or production base is accepted or rejected.

## Context

ADR-0190 identified the selected reduced-palette P005-to-R6 P006 cut as visually abrupt and required an existing-pixel attribution control before proposing a render or edit.

The three-arm control in `docs/research/evidence/ch05-p005-p006-route-attribution-control-r1.json` (`22cf4860e4bf892c347396a6f9e98b9286805c60f0e1bc34f7944f0c03fc53ce`) holds the two ComicPanelPlan IDs and review-cell geometry fixed while comparing:

- selected text P005 to R6 P006: luminance/RGB histogram distance `0.521210 / 0.519582`;
- all-text P005 to P006: `0.510071 / 0.472000`;
- all-R6 P005 to P006: `0.555130 / 0.551442`.

The selected pair is `0.978613 / 1.015362` times the two-control mean and exceeds neither pair of same-route controls. The predeclared two-proxy rule therefore does not isolate the route switch as the source of abruptness. The people-free insert to two-adult action change, shot scale, native aspect, crop, resize, and non-randomized candidates remain confounds.

## Decision

Keep P005-to-P006 visible as an owner review question, but do not spend a new render, upload, or pixel edit on the basis of these proxies. Retain the current three-block cadence for review because it remains semantically strong and the route-switch attribution test did not identify a deterministic repair target.

If the owner rejects the cut visually, the next experiment must begin from that explicit visual disposition and compare a single specified change. Do not infer a need for global style matching, reference-policy changes, or a wholesale route replacement.

## Consequences

The project avoids a low-information stochastic retry while preserving the exact review risk. Histogram and complexity proxies remain non-quality measurements and support no causal style claim. Calls, uploads, new art, edits, spend, acceptance, rights clearance, commercial clearance, and exact-base selection remain zero or null.
