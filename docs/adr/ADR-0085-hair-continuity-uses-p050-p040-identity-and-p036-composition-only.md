# ADR-0085: hair continuity uses P050/P040 identity and P036 composition only

- Status: accepted
- Date: 2026-09-01

## Context

The three owner-authorized fictional references conflict on hair. P050 depicts light-brown/dark-blond-haired Soren and dark-brown-haired Sigrid. P040 independently reinforces dark-haired Sigrid. The corrected P036 composition instead depicts dark-haired Soren and blond Sigrid. Using all three as undifferentiated identity references would amplify drift during multi-panel generation.

## Decision

Use P050 as the primary dual-character identity/wardrobe/action reference and P040 as the primary Sigrid face/hair reference. Use P036 only for vertical composition, lever staging, and clear-line treatment. Every reference-conditioned prompt must explicitly override P036 hair: Soren remains light brown/dark blond; Sigrid remains dark brown/near black.

Issue a provisional fictional-adult visual profile. It is an engineering continuity control pending owner review, not a real-person identity model or immutable biological canon.

## Consequences

- Hair color and tied-back silhouette become explicit per-role assertions rather than implicit style cues.
- P036 remains useful without silently swapping the protagonists.
- Text-only controls test whether the profile can carry identity without reference pixels.
- CH05 wardrobe remains the oatmeal coat/plaid wrap. Armor, weapon, upgraded-clothing, and monster examples stay non-canon until separately promoted.
- No new provider, upload class, direct API spend, child content, real likeness, or commercial-clearance claim is introduced.
