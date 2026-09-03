# ADR-0173: P043 leaves the open tin, not every item; the map remains for P046

- Status: Accepted canon-preserving correction; owner narrative review pending
- Date: 2026-09-02

## Context

The exact P043 ComicPanelPlan says, “They leave the tin open on the stone and retreat together.” P046 separately says Sigrid keeps the creek map inside her wrap. The original sequence-generation prompt expanded P043 to “leave the opened tin and contents on the stone,” creating an avoidable continuity ambiguity with P046.

## Decision

Treat the ComicPanelPlans as authoritative. P043 must clearly leave the open tin on the stone while keeping the map eligible for P046. The r5 repair therefore shows the open tin in the foreground and Sigrid securing the folded map during the retreat. P040-P042 remain byte-identical.

The original prompt and crop remain immutable diagnostic evidence; this ADR records the conflict rather than rewriting it silently.

## Consequences

P039's upstream mark and P043's tin/map continuity can be reviewed as one object-continuity pair without weakening the deduction, dying ember, or ringing-bell beats between them. The exact third-mark symbol remains provisional and requires owner narrative review. No ComicPanelPlan revision, dialogue approval, acceptance, or rights decision is implied.
