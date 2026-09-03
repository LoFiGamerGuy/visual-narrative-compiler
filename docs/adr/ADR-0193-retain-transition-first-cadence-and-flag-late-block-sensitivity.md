# ADR-0193: Retain transition-first cadence and flag late-block sensitivity

## Status

Accepted as an engineering recommendation for owner review. No art, route, sequence, rights status, or exact production base is accepted.

## Context

ADR-0188 selected a sequence-level cadence of reduced-palette S01, R6 S02-S08, and premium cel S09-S11. The optimizer is lexicographic, so a unique optimum can still depend on which objectives are included and ordered.

The zero-upload sensitivity audit in `docs/research/evidence/ch05-cadence-objective-sensitivity-audit-r1.json` enumerates 1,728,000 hard-feasible assignments and reruns the optimizer under eight leave-one-secondary-objective-out variants. Hard constraints remain zero combined semantic/identity failures, zero semantic failures, and zero identity failures.

Seven variants reproduce the recorded three-block assignment. Removing adjacent-route-transition minimization alone changes S10 and S11 from premium cel to R6, increases transitions from two to three, and reduces semantic warnings from three to two. All nine tested optima are unique, so this is objective-inclusion sensitivity rather than a tie.

The exact eight-field Pareto frontier contains three assignments. The recorded cadence has two transitions, three semantic warnings, four overall failures, and two lettering failures. The nearest alternative has three transitions, two semantic warnings, four overall failures, and two lettering failures. A third alternative reduces secondary warnings further only by increasing transitions, overall failures, and lettering failures to five, nine, and six.

## Decision

Retain the recorded three-block cadence for owner review because it is stable under seven of eight objective omissions and uniquely enforces the declared transition-first chapter policy. Label S10-S11 premium cel as policy-sensitive rather than inevitable.

Do not rerender or edit from this metadata-only sensitivity result. If the owner dislikes the late block, the smallest next visual experiment is a sequence-level S10-S11 comparison against the already available R6 alternative, with no within-sequence cherry-picking.

## Consequences

The review handoff can explain the real tradeoff: two transitions with three semantic warnings versus three transitions with two semantic warnings. Pareto status is not an art-quality score, acceptance, or commercial determination.

The audit used no provider, upload, new pixel, generated candidate, paid spend, or human-review decision. ComicPanelPlan remains the only active planning structure; AnimationShotPlan and E-Conte remain null.
