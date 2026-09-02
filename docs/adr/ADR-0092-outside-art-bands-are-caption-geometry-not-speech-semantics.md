# ADR-0092: Outside-art bands are caption geometry, not speech semantics

- Status: accepted
- Date: 2026-09-01

## Context

Two deterministic full-scroll demonstrations add light caption bands or dark direct gutter text above c005, c013, and c014 while preserving every source pixel. Both render two-line review copy at 13.975px on a 390px phone canvas. Six band instances add 480px (3.295%) to the 1200px scroll. Visual review favors the light band for association with the following panel; dark direct text is quieter but more weakly grouped. Neither treatment contains a tail or speaker binding.

## Decision

Carry the light outside-art band as the next plan-level option for narration, deduction, or caption semantics on narrow panels. Retain dark direct gutter text only as a comparison arm. Do not use either treatment for attributed character speech without explicit speaker/tail semantics.

The c014 demonstration proves a zero-overlap geometric route but does not repair P044's current ComicPanelPlan. Any production use requires an explicit ComicPanelPlan lettering-strategy revision and a new assembly revision.

## Consequences

- Narrow visual cadence can coexist with 13px-plus phone type without obscuring art.
- Outside-art geometry adds measurable scroll height and must be budgeted in chapter rhythm.
- Silent inserts remain the default; bands are used only when script function justifies them.
- No copy, dialogue, plan, assembly, treatment, art, or production base is accepted.
