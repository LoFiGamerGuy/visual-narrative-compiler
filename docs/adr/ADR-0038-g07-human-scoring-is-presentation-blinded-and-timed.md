# ADR-0038: G07 human scoring is presentation-blinded and timed

- Status: accepted
- Date: 2026-09-01

## Context

The G07 candidates have exact automated drift/cost/latency evidence and non-gating agent triage, but no authorized human judgments or measured human minutes. Provider labels can bias qualitative review, and manually entered durations or incomplete case coverage would make arm comparisons unreliable.

## Decision

Present all 16 candidates as neutral deterministic PNGs whose decoded RGB bytes match their sources. Assign provider-hidden, case-balanced blind IDs and four hidden-arm independent-repeat pairs. Require one append-only timed decision for each of 20 subjects and the exact case-specific assertion list for every decision.

Do not include provider/model names, source paths, request IDs, or costs in the presentation packet. Deblind only after a complete valid review session. Keep presentation files and review sessions ignored under `experiments/`; track only the non-art protocol roots and validation code.

## Consequences

- Reviewer-facing format and file extension no longer reveal a provider arm.
- Role binding/order/count, shared-set blocking, target change, no-change, side effects, and repeat limitations have explicit judgments.
- Incomplete, reordered, untimed, hash-drifted, or assertion-incomplete sessions cannot become evidence.
- Presentation blinding is procedural, not cryptographic secrecy against a reviewer who inspects repository source evidence.
- Protocol construction creates no human decision: current decisions are 0/20, minutes null, accepted subjects zero.
