# ADR-0177: Separate full-chapter story authoring from render prompts

- Status: Accepted
- Date: 2026-09-02

## Context

CH05 demonstrated that efficient chapter production needs a complete narrative/cadence/continuity contract before sequence prompts are written. Without that layer, story invention, continuity decisions, lettering geometry, and rendering instructions can become entangled inside provider prompts and are difficult to review or version independently.

The next chapter currently has no approved chapter-scale ComicPanelPlan collection. A reusable contract can prepare the pipeline without fabricating story or pretending an empty template is executable.

## Decision

1. Require six generic narrative functions in a full chapter: opening/orientation, movement/escalation, threshold/entry, causal interaction/evidence, deduction/choice/consequence, and reversal/return/closure.
2. Require explicit stable panel identity, plan revision, story beat, composition, adult cast, sequence, scale/density role, continuity carry-in/out, and collision-safe lettering policy before prompt promotion.
3. Use CH05's measured 3-5-panel sequence range and nine scale roles as guidance, not as a mandatory chapter length.
4. Require explicit progression bindings for armor, weapons, upgraded clothing, monsters, classes, or system UI. Null means absent, not implicitly authorized.
5. Keep the reusable template empty, with no record/story identity, panels, sequences, prompts, promotion, or executable state.
6. Preserve separate human visual acceptance, commercial-clearance, and exact-production-base decisions.

## Consequences

- A complete approved story can move into sequence production without a bespoke schema redesign.
- Narrative and canon changes stay reviewable outside renderer prompts.
- The current template grants no authority to generate, upload, spend, accept, or change canon.
