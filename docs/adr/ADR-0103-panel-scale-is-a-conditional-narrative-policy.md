# ADR-0103: Panel scale is a conditional narrative policy

- Status: accepted
- Date: 2026-09-01

## Context

The selected 14 already use eight widths from 560 to 1,040 source pixels. Lettering tests show that the three tested two-line in-art treatments need 1,200px for the declared 13px phone-type target, while outside-art bands can reach 13.975px without changing source pixels but add 3.295% scroll height and lack speech semantics.

A single chapter-wide aspect ratio or width would erase the intended contrast between action/reveal anchors, character deductions, causal tall panels, quiet transitions, and silent object inserts.

## Decision

Use nine conditional scale roles across all 50 ComicPanelPlans. Recommend 1,040–1,200px for dual directional anchors, 700–1,040px for causal action depending on geometry, 720–1,040px for character/reaction beats, and 520–760px for silent object/sensory inserts.

Treat these as ranges, not accepted layouts. Exact final copy can force a 1,200px test or a ComicPanelPlan revision for caption/direct-text semantics. Opacity never compensates for inadequate type size or overlap with people, faces, hands, or story objects.

## Consequences

- All 50 plans receive a deterministic conditional role; one existing plan explicitly contains dialogue and remains unbound.
- The policy is based on 14 selected layout rows, 30 lettering cases, the outside-band comparison, and density evidence.
- The chart and policy build byte-identically; 19/19 evidence mutations fail.
- No final copy, accepted layout, plan revision, provider call, upload, or external cost is created.
