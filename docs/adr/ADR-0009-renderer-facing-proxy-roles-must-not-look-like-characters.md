# ADR-0009: Renderer-facing proxy roles must not look like characters

## Decision

Retain geometry as a spatial-reference authority, but stop using the orange-circle/teal-triangle token pair as a renderer-facing role/count representation with FLUX.2 Klein. Before another renderer-stage control, use a proxy encoding whose components cannot be reinterpreted as a character head/body composition and whose exact-count assertions are independently machine-checkable.

## Evidence

The reproducible G07a/G07b paired control used two common seeds against fixed geometry reference assets. All four outputs retained declared side placement, kitchen/table composition, and non-contact blocking. All four transformed the single orange circle into stacked orange circles resembling a head/body pair, failing the exact-two-token assertion. This is a 0/4 exact-count pass rate despite 4/4 side-position/blocking passes; total local generation time was 220.220 seconds.

## Consequences

The geometry layer remains useful for stage, camera, occlusion, and coarse left/right layout. It is not sufficient by itself to encode a renderer-visible role token. The draft proxy bundle stays non-frozen and cannot score the frozen gauntlet. A next fictional-design control should separate spatial anchors from role labels (for example non-figurative labeled-color regions that are excluded from final art), rather than use character-like proxy shapes.
