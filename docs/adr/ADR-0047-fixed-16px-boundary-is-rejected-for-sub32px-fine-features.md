# ADR-0047: fixed 16px boundary is rejected for sub-32px fine features

- Status: accepted
- Date: 2026-09-01

## Context

P036's 16-pixel inward boundary works on a large contextual mask. P044 explicitly supplies blade/twine contact and was selected to test a finer scale without changing renderer, mask geometry, or story intent.

## Decision

Apply the fixed 16-pixel policy unchanged to one connected abstract support containing an 18-pixel blade and 12-pixel taut twine, clipped away from two protected hand regions. Do not tune within the experiment.

Reject the fixed policy for this control because it leaves zero fully replaced core pixels for both blade and twine. Preserve the positive constraints separately: one support component, zero protected-hand overlap, zero lettering overlap, and zero exterior change.

## Consequences

- A single absolute feather width is not portable across the observed P036 and P044 control scales.
- The failure does not reject P044, the selected provider route, or inward compositing as a mechanism.
- The next experiment may compare boundary widths on the exact same geometry; it may not widen/redraw support or author a production mask.
- No P044 policy or input approval exists.
