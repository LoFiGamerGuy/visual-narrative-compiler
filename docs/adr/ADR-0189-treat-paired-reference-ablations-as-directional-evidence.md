# ADR-0189: Treat paired S01/S11 reference ablations as directional evidence only

## Status

Accepted as an interpretation boundary for engineering research. It is not an acceptance, rights, or provider-policy decision.

## Context

The S01 comparison in `docs/research/evidence/ch05-s01-flat-gouache-reference-ablation-comparison-r1.json` (`f518412e7fbad81c530b5122060ee918bf94aed01b7011ce7f48191bb4ab8a30`) and S11 comparison in `docs/research/evidence/ch05-s11-flat-gouache-reference-ablation-comparison-r1.json` (`cbd14efc9487403c1daee324632de6a0fdcd11c2f9a05fb3662837a22ce16861`) each contain one reference-backed flat-gouache strip, one matched no-reference strip, and one stricter reduced-palette no-reference strip.

For the matched no-reference result relative to the reference-backed result, edge density changes by -0.068096 at S01 and -0.029169 at S11; native PNG bytes/pixel changes by -0.188811 and -0.045402. Grayscale entropy changes slightly upward by 0.057907 and 0.064727. Each pair changes exactly the input-reference instruction while preserving its story and style wording.

The full zero-upload reduced-palette route separately produces 43 semantic PASS / 4 WARN / 3 FAIL, preserves role-correct mature-adult hair and wardrobe in 32/32 cast-visible panels, and uses zero reference bindings or uploads.

## Decision

Treat the two matched pairs as directional evidence that a text-only, zero-upload route remains technically viable and may reduce two density proxies in these two sequences.

Do not claim that reference removal caused the measured changes, that references generally increase density, that no-reference generation generally preserves identity, or that references are unnecessary. The samples are stochastic, there is only one matched pair per sequence, and the stricter reduced-palette control also changes style instructions.

Keep zero-upload text-only generation available as a controlled production option and comparison arm. Any broader reference-policy or continuity conclusion requires replicated matched requests and owner review of exact identity, action, and story behavior.

## Consequences

No additional upload class, provider authority, purchase, or paid API use follows from this decision. Human review remains pending, stochastic reproducibility remains unmeasured, and no compared candidate is accepted, rights-cleared, commercially cleared, or selected as an exact production base.
