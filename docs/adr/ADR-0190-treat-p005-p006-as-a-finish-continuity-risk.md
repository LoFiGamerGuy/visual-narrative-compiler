# ADR-0190: Treat P005-to-P006 as a finish-continuity risk

## Status

Accepted as an engineering review constraint. This does not reject or accept any panel, route, sequence assignment, rights position, or exact production base.

## Context

The measured sequence cadence reduces the chapter from 33 adjacent route transitions to two while preserving 47 semantic PASS / 3 WARN / 0 FAIL. A complete review-only scroll shows that the two remaining transitions are not equally cohesive.

The deterministic boundary audit in `docs/research/evidence/ch05-sequence-cadence-boundary-audit-r1.json` (`1aadf213f9a6f1253c4386392b663791a3fcf6ae9db8887268b0566936f8cc0d`) compares each cross-route boundary with the two neighboring within-route pairs. At P005-to-P006, luminance and RGB histogram distances are respectively 1.120982 and 1.168896 times the adjacent-control mean. Manual review agrees that the high-key, sparse reduced-palette object insert cuts conspicuously to a cool, dense R6 action panel. The proxy does not exceed both individual controls because P004-to-P005 is itself a large content/shot change, so it cannot attribute the difference to style alone.

At P039-to-P040, the same ratios are 0.902299 and 0.894237. The shared dark-mill, cool-exterior, and earth-tone value structure makes that boundary comparatively cohesive, although different focal characters prevent a same-face continuity claim.

## Decision

Keep the three-block cadence as the strongest current complete-chapter review route, but do not use it as finish-continuity evidence while P005-to-P006 remains unresolved.

The next boundary experiment is a zero-upload, no-new-pixel, three-arm attribution control using already generated candidates for the same panel IDs and story beats:

- selected reduced-palette P005 to R6 P006;
- reduced-palette P005 to reduced-palette P006;
- R6 P005 to R6 P006.

Compare the three pairs at matched presentation size, preserving exact source hashes. Do not generate a replacement, apply a color grade, or alter P039-to-P040 unless this existing-evidence control first shows that such work is informative.

## Consequences

The current chapter remains immediately reviewable and semantically strong, while its most visible finish risk is explicit rather than averaged away. Histogram, entropy, edge, and byte-density measurements remain non-quality proxies confounded by shot, subject, aspect ratio, and content. Owner acceptance, commercial rights, exact-base selection, and production promotion remain separate and null.
