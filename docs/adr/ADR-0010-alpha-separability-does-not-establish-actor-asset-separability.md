# ADR-0010: Alpha separability does not establish actor-asset separability

## Decision

Treat alpha/matte QA as a distinct gate from neutral-background keying. A plate is not reusable merely because it can be keyed cleanly: it must also exclude attached foreign foreground objects, encode a usable pose/camera, and satisfy the multi-role asset requirements.

## Evidence

The sole provisional Soren plate was keyed deterministically from its flat background with zero sampled-corner false positives and a 21.75% foreground mask. The matte preview nevertheless retains a long dark foreground artifact attached near the hands. This is exactly the type of semantic contamination color keying cannot remove.

## Consequences

The current legacy actor-plate route has no verified reusable Soren or Sigrid asset for G07 compositing. Do not run alpha-matte or two-role compositor follow-ons using these plates. A future actor-asset experiment must use a different local control mechanism and explicitly QA both alpha and foreign-content absence.
