# CH05 cadence objective-sensitivity audit r1

The recorded three-block cadence is not fully invariant, but it is stable under seven of eight leave-one-secondary-objective-out variants. This audit uses only the existing six-route status table; it creates no pixels and makes no acceptance or production-base decision.

Route abbreviations: `RPT` reduced-palette text control, `R6` R6, `CEL` premium cel, `CLW` clear-line watercolor, `ALT` alternate graphic, `FGG` flat graphic-gouache. Assignments run S01 through S11.

## Method

Hard constraints remain zero combined semantic/identity failures, zero semantic failures, and zero identity failures. Each variant removes exactly one of eight secondary objectives while retaining the original order of the other seven. There are 1,728,000 hard-feasible assignments across the 11 sequences.

## Leave-one-out results

| Dropped objective | Matches baseline | Optimal ties | Transitions | Semantic WARN | Overall FAIL | Lettering FAIL | Assignment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `adjacent_route_transitions` | no | 1 | 3 | 2 | 4 | 2 | `RPT / R6 / R6 / R6 / R6 / R6 / R6 / R6 / CEL / R6 / R6` |
| `combined_semantic_identity_warnings` | yes | 1 | 2 | 3 | 4 | 2 | `RPT / R6 / R6 / R6 / R6 / R6 / R6 / R6 / CEL / CEL / CEL` |
| `semantic_warnings` | yes | 1 | 2 | 3 | 4 | 2 | `RPT / R6 / R6 / R6 / R6 / R6 / R6 / R6 / CEL / CEL / CEL` |
| `identity_warnings` | yes | 1 | 2 | 3 | 4 | 2 | `RPT / R6 / R6 / R6 / R6 / R6 / R6 / R6 / CEL / CEL / CEL` |
| `overall_failures` | yes | 1 | 2 | 3 | 4 | 2 | `RPT / R6 / R6 / R6 / R6 / R6 / R6 / R6 / CEL / CEL / CEL` |
| `lettering_failures` | yes | 1 | 2 | 3 | 4 | 2 | `RPT / R6 / R6 / R6 / R6 / R6 / R6 / R6 / CEL / CEL / CEL` |
| `combined_overall_lettering_warnings` | yes | 1 | 2 | 3 | 4 | 2 | `RPT / R6 / R6 / R6 / R6 / R6 / R6 / R6 / CEL / CEL / CEL` |
| `stable_route_preference_sum` | yes | 1 | 2 | 3 | 4 | 2 | `RPT / R6 / R6 / R6 / R6 / R6 / R6 / R6 / CEL / CEL / CEL` |

Seven variants reproduce `RPT / R6 / R6 / R6 / R6 / R6 / R6 / R6 / CEL / CEL / CEL`. Removing `adjacent_route_transitions` alone changes S10-S11 to R6: `RPT / R6 / R6 / R6 / R6 / R6 / R6 / R6 / CEL / R6 / R6`. This adds one transition (2→3) while reducing semantic warnings (3→2). Every tested optimum is unique, so the change is objective-inclusion sensitivity, not a score tie.

## Exact Pareto frontier

| Point | Baseline | Transitions | Semantic WARN | Overall FAIL | Lettering FAIL | Secondary WARN | Assignment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| pareto_01 | yes | 2 | 3 | 4 | 2 | 3 | `RPT / R6 / R6 / R6 / R6 / R6 / R6 / R6 / CEL / CEL / CEL` |
| pareto_02 | no | 3 | 2 | 4 | 2 | 2 | `RPT / R6 / R6 / R6 / R6 / R6 / R6 / R6 / CEL / R6 / R6` |
| pareto_03 | no | 5 | 2 | 9 | 6 | 1 | `RPT / R6 / R6 / R6 / R6 / R6 / RPT / R6 / CEL / R6 / R6` |

The baseline and both alternatives are nondominated over the eight recorded secondary fields. The third point changes S07 to reduced-palette and S10-S11 to R6; its one secondary warning is purchased with five transitions, nine overall failures, and six lettering failures. Pareto status is not a quality or production recommendation.

## Conclusion

Retain the three-block cadence for owner review: it is stable to seven of eight objective omissions and uniquely implements the declared transition-first policy. Record S10-S11 premium cel as policy-sensitive rather than inevitable. No promotion, rerender, or provider action follows.

## Limitations

- Leave-one-out does not test every ordering or weighting of secondary objectives.
- The exact Pareto frontier covers recorded categorical counts, not visual quality or human preference.
- Reviews remain non-gating; owner acceptance, rights clearance, canon change, and exact-production-base selection remain null.
- Provider calls, uploads, new pixels, and direct paid spend are zero.

Input: `docs/research/evidence/ch05-six-route-comparison-r1.json` — SHA-256 `c40d3a945704639855135cda4d011529f13c5c71d857b7807914823d7e248229`.

Machine-readable evidence: `docs/research/evidence/ch05-cadence-objective-sensitivity-audit-r1.json`.
