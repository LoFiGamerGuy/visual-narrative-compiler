# Complete-chapter semantic graph validator r1

The pre-prompt validator now checks whether a filled full-chapter plan is narratively and operationally coherent—not merely valid JSON.

## Measured synthetic result

- Positive: 1/1 synthetic adult-only, non-canon chapter graph passes.
- Adversarial: 23/23 malformed variants fail.
- Coverage: planning boundary; forbidden pre-promotion fields; opening/closing change; panel identity/order; six phases; fictional-adult roles; scale/density cadence; safe lettering geometry; panel continuity edges; sequence order/contiguity/coverage; progression canon binding.
- North Garden story beats/plans, prompts, calls, uploads, candidates, acceptance/rights decisions: all zero.

The adversarial suite catches cross-medium leakage, executable state, prompt/model leakage, unchanged closing state, count/identity/order errors, missing/misnamed phases, undeclared and child-coded roles, invalid scale/density cadence, missing/out-of-bounds lettering zones, broken continuity, sequence size/order/overlap/ID errors, and undeclared or weak progression bindings.

Evidence: [semantic validator record](C:/AgentWorkspaces/anime-pipeline/docs/research/evidence/complete-chapter-semantic-graph-validator-r1.json) and [ADR-0178](C:/AgentWorkspaces/anime-pipeline/docs/adr/ADR-0178-fail-closed-on-chapter-semantic-graph-before-prompt-promotion.md).

Limitation: the positive fixture is synthetic and only six panels long. It proves semantic rule behavior, not story quality, chapter pacing, renderer performance, or current CH05 conformance.
