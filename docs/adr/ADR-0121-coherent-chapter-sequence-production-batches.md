# ADR-0121: Coherent chapter sequence production batches

Date: 2026-09-01

Status: Accepted as a fail-closed production partition

## Context

The 50-plan readiness matrix is plan-complete but chapter production should operate on coherent 3–6-panel sequences, not isolated images. Story order and production readiness are distinct: the chapter must remain narratively ordered while the next experiment should target the most informative prepared sequence.

## Decision

Partition the 50 ComicPanelPlans exactly once into 12 contiguous 3–5-panel narrative batches. Preserve narrative order separately from four evidence-readiness production waves. Make P010–P013 the sole wave-1 pilot; place P014–P023 in wave 2; mill mechanics/deduction/retreat in wave 3; retain departure context and final return in wave 4 pending chapter-wide route/copy decisions.

Each sequence predeclares four review outputs: candidate contact sheet, 390px phone sheet, continuity strip, and lettering-safe-zone strip.

## Evidence

- 50 plans / 12 sequences / 3–5 panels each; every plan appears once in story order.
- Production-wave distribution 1/2/5/4.
- 48 planned review artifacts.
- Every panel carries scale role/range, cadence class, mechanism, readiness, continuity risk, and reference hypotheses.
- The 1800×1220 map is visually checked.
- 19/19 mutations are rejected.

## Consequences

- Production can advance by coherent units while final assembly preserves narrative order.
- Wave is an evidence-readiness category, not an artistic ranking or story reorder.
- Prompts, renders, acceptance, execution, calls, uploads, cost, and plan revisions remain zero.
