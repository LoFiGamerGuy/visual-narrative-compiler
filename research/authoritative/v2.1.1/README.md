# North Garden — Visual Narrative Compiler research package
**v2.1 · 2026-08-31**

## Read in this order

| # | File | Why |
|---|---|---|
| 1 | `docs/CORRECTIONS_V2_1.md` | **Start here.** Post-verification corrections. Authoritative where it conflicts with anything else |
| 2 | `docs/HANDOFF_CODEX_V2.md` | The owner's handoff instruction and execution order |
| 3 | `docs/RESEARCH_BRIEF_V2.md` | Findings, contrary evidence, re-ranked open questions |
| 4 | `docs/ARCHITECTURE_V0_1.md` | Data model, storage, renderer boundary, generation stack, QA architecture |
| 5 | `docs/DECISION_LOG.md` | KEEP / REPLACE / RETIRE / UNRESOLVED on every prior finding |
| 6 | `bench/CONTINUITY_GAUNTLET.md` + `bench/gauntlet.json` | The frozen benchmark. **Import IDs unchanged** |
| 7 | `registry/POLICY_LICENSE_REGISTRY.md` | Licence, policy, compute economics, child-safety register |
| 8 | `registry/CANDIDATE_REGISTRY.md` + `candidates.json` | 53 candidates with licence/hardware/maintenance/role |
| 9 | `docs/EXPERIMENT_BACKLOG.md` | Experiments with explicit stop/go criteria |
| 10 | `docs/NEXT_ACTIONS.md` | Sequenced plan, purchases, what not to do |

## Conflict-resolution order

1. Reproducible LOCAL_EXPERIMENT evidence and existing working code
2. Current official licence/policy/model documentation
3. `docs/CORRECTIONS_V2_1.md` and the owner's handoff corrections
4. The v2 research package and its cited evidence
5. The older Master Brief's hypotheses

**Do not silently reconcile conflicts. Record them in an ADR.**

*This ordering is canonical. `scripts/validate_research_package.py` fails the package if any other document states a different one.*

## The rule that would have prevented every error in v2.0

For any claim that gates a **spend**, a **platform**, or a **legal boundary**: fetch the
**primary artifact** — the LICENSE file, the policy page, the model card — not a description
of it. All three v2.0 errors came from a stale or secondary source outranking a current
primary one, and evidence tags did not catch them, because **tags describe provenance, not
currency**.

## Governing rule

> A research/engineering cycle that produces only infrastructure has failed.

Every cycle must also push the pipeline through real narrative material and produce at least
one accepted, instrumented page. Those outputs are the production dataset and expose the real
bottlenecks. The modal failure for solo pipeline projects is infrastructure that works and
goes unused.

## Benchmark at a glance

**All counts below are computed from `bench/gauntlet.json` — see `PACKAGE_STATUS.md`, which is generated. Never hand-edit a count.**

**40 render cases** — 10 Neutral · 10 Occlusion · 10 Interaction · 6 set-continuity · 4 VFX/expression.
**10 paired-variant relations** (20 cases) across five axes: `left_right_swap`, `near_far_swap`,
`depth_role_swap`, `focus_role_swap`, `interaction_role_swap`. Each pair carries a
`variant_discriminator` — the manifest key that must differ — so the pair is executable, not prose.

**Derived, and NOT renderer generations:** 4 QA no-change controls (12 comparisons) measuring
fabricated-error rate, and 8 QA error-injection cases measuring detection recall by error class.

**Stage A** smoke = 12 cases × 2 seeds. **Stage B** full = 40 × 3 seeds = **120 renderer generations** per finalist.
Identity reported as **Correct / Blend / Swap** (mutually exclusive), plus recall **and**
false-alarm rate, candidates-per-acceptance, and **human minutes**.

⚠️ The benchmark is **semantically frozen** (G01–G30 intent immutable) but is **not yet an executable
frozen harness** — see `executable_bundle_status` in `gauntlet.json`.
