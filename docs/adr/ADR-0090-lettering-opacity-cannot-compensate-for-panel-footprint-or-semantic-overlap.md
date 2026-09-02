# ADR-0090: Lettering opacity cannot compensate for panel footprint or semantic overlap

- Status: accepted
- Date: 2026-09-01

## Context

Twelve local treatments compare 96%, 88%, and 76% light backings on c005/c014 texture outliers and c013/h001 clean controls. Every treatment retains strong measured black-type contrast (minimum fifth-percentile ratio 11.942:1), but two-line review copy renders at only 6.513–11.366px at the panels' actual 390px-scroll footprints. None reaches the declared 13px target. Visual inspection also finds that P044/c014's top-right safe zone overlaps Soren's clothed upper arm/person area; opacity cannot cure that placement failure.

## Decision

Carry 88% as the next general translucent-backing arm, not as an accepted default. Treat phone-size type and semantic clearance as gates before opacity preference.

Keep small causal/object inserts silent or extremely low-text by default. If P044 requires text, revise its ComicPanelPlan lettering strategy before production; do not place a balloon in the tested c014 zone. If a two-line balloon is required on another narrow panel, increase its chapter-layout footprint or revise the safe field rather than shrinking type below the declared target.

## Consequences

- c014 fails the current balloon-placement rehearsal despite high measured contrast.
- c005, c013, and h001 preserve protected-content clearance, but their tested two-line copy remains below target phone size.
- Review-copy results do not revise canon, dialogue, plans, acceptance, or commercial status.
- The next experiment measures width and copy-length sensitivity locally; it requires no provider, upload, or spend.
