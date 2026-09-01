# ADR-0053: numeric boundary measurement does not equal seam acceptance

- Status: accepted
- Date: 2026-09-01

## Context

The v2.1 outcome contract requires exact-base visual-boundary evidence, but a hash reference alone does not specify how exterior preservation, the boundary band, or no-change identity were measured. Numeric discontinuity reduction can also be overread as human seam acceptance.

## Decision

Use a candidate-bound measurement packet that pins exact base, candidate, support, inward-alpha, selector profile, topology evidence, method, measurements, no-change short circuit, and review presentation. Keep numeric measurement and human review as separate fields and states.

## Consequences

- The synthetic P036 fixture measures 64,992 support pixels, 35,150 transition pixels, 27,366 full-core pixels, exact-zero exterior change, and 98.838% mean boundary-distance reduction against its derived hard reference.
- The no-change fixture is byte-identical and invokes no provider.
- The presentation is bound to exact source hashes, but its session, decision, and human minutes remain null and acceptance remains false.
- Fourteen/fourteen hash, metric, no-change, review, fixture, and activity mutations fail.
- These values are validation mechanics, not approved art, narrative applicability, visual quality, human acceptance, or production evidence.
