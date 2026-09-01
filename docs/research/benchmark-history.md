# Benchmark history

## v2.1.1 semantic benchmark

- Semantic source: `research/authoritative/v2.1.1/bench/gauntlet.json`
- Source SHA-256: `f826b0f1d06ed5a999667bde23ba0d04f8ebb22f516095034dab62c7541ae9ae`
- Status: semantically frozen. Executable harness remains adapter-dependent and is not frozen.

## `baseline_legacy` Stage A - 2026-08-31

| Field | Result |
| --- | --- |
| Cases / seeds | 12 / 2 |
| Renderer generations | 24 |
| Completed records | 24 |
| Total generation time | 903.79 s |
| Mean generation time | 37.66 s |
| Accepted candidates | 0 |
| Human review minutes | unmeasured (agent visual triage only) |
| API/cloud cost | none; local execution |
| Local electricity/depreciation | unmeasured |
| Hard failure | G11a/101 and G11a/202 produced an extra child |
| Result | rejected for further benchmark evaluation without tuning |

Full per-case decisions and failure tags are in `experiments/results/baseline_legacy_stage_a_20260831.json`.

## `sequential_inpaint_per_character` P07 preflight - 2026-08-31

This is not a benchmark result. It is retained here so an operational smoke is not mistaken for a semantic Stage-A score.

| Field | Result |
| --- | --- |
| Requests / seeds | one legacy P07 repair request / 2 |
| Renderer generations | 4 (two passes per seed) |
| Total / mean generation time | 108.42 s / 27.105 s |
| Mechanical-smoke accepted candidates | 1 (seed 101 only) |
| Production accepted candidates | 0 |
| Failed assertion | seed 202 omitted Sigrid after the second pass |
| Bundle state | `DRAFT_LEGACY_LIMITED_NOT_FROZEN` |
| Stage-A state | planned-but-not-executable; required case assets are explicit |

Full record: `experiments/results/sequential_inpaint_p07_smoke_20260831.json`.

## `sequential_inpaint_per_character` G07a/G07b controls - 2026-08-31

This is a role-swap preflight, not a Stage-A result. The frozen cases are grounded while the adapter uses a declared legacy 2D plate; the bundle is therefore `DRAFT_LEGACY_LIMITED_NOT_FROZEN`.

| Field | Result |
| --- | --- |
| Semantic cases / smoke seeds | G07a, G07b / 101, 202 |
| Smoke renderer generations | 8 |
| Total / mean renderer time | 216.70 s / 27.09 s |
| Valid no-change control MAE | 0.0084 (zero-mask reconstruction) |
| Invalid-control diagnostic | active-mask denoise-zero erased target region (0.3283 target MAE) |
| Provisional role-binding passes | 4/4 in agent visual triage |
| Fully passed blocking assertions | 2/4; one failure, one indeterminate |
| Production accepted candidates | 0 |
| Main limitation | broad target masks confound actor repair and set alteration |

Full record: `experiments/results/sequential_inpaint_g07_controls_20260831.json`.

## `actor_matte_legacy_composite_control` G07a/G07b - 2026-08-31

This is a deterministic asset/stage control, not a renderer result.

| Field | Result |
| --- | --- |
| Cases | G07a, G07b |
| Diffusion generations | 0 |
| Base plate retained outside actor/shadow influence | 91.60% / 91.31% of pixels unchanged |
| Role assertions | 2/2 pass in agent visual triage |
| Seated-at-table assertion | 0/2 pass |
| Production accepted candidates | 0 |
| Main limitation | actor plates embed furniture and do not encode reusable pose/prop separation |

Full record: `experiments/results/actor_matte_g07_controls_20260831.json`.

## `flux2_klein_4b_local` geometry-proxy G07 stage-conditioning smoke - 2026-09-01

This is a draft fictional-proxy bundle, not a frozen Stage-A result. It has no person or child input.

| Field | Result |
| --- | --- |
| Semantic references / runs | G07a/G07b / 3 |
| Total / mean renderer time | 103.829 s / 34.610 s |
| Proxy hard-assertion pass | 2/3 in agent triage |
| Role/count failure | G07b seed 7502 duplicated the orange token |
| Production accepted candidates | 0 |
| Bundle state | `DRAFT_FICTIONAL_PROXY_STAGE_NOT_FROZEN` |
| Main limitation | proxy-only identity; one extra-token failure; no target-local repair evidence |

Full record: `experiments/results/flux2_klein_geometry_proxy_g07_smoke_20260901.json`.

## Deterministic fictional tile-proxy QA calibration - 2026-09-01

This is derived control calibration, not a renderer score or real-panel QA result.

| Field | Result |
| --- | --- |
| Valid reference control | 1/1 pass |
| Duplicate marker injection | rejected |
| Missing marker injection | rejected |
| Role-swap injection | rejected |
| Sensor authority | non-gating; fixed proxy-stage regions only |

Full record: `experiments/results/proxy_tile_qa_injections_20260901.json`.

## `flux2_klein_4b_local` fictional proxy smoke and reference edit - 2026-09-01

This is an adapter-operational and proxy repair smoke, not a frozen benchmark score. It uses neither real-person nor child inputs.

| Field | Result |
| --- | --- |
| Initial role-order proxy runs | 2, seeds 7301 / 7302 |
| Initial total / mean renderer time | 35.122 s / 17.561 s |
| Visual proxy role/table assertions | 2/2 pass in agent triage |
| Reference-conditioned edit | seed 7401, orange-right to green-right |
| Edit renderer time | 35.307 s |
| Edit scene/role assertions | pass in agent triage |
| Pixel change diagnostic | 83.58% pixels changed; full-frame bounding box |
| Production accepted candidates | 0 |
| Main limitation | global reference-conditioned redraw; no demonstrated target-local/no-change guarantee |

Full record: `experiments/results/flux2_klein_proxy_smoke_20260901.json`.

## External fictional G07 pre-execution control — 2026-09-01

This is governance and adapter-readiness evidence, not a benchmark result and not a renderer score.

| Field | Result |
| --- | --- |
| Provider arms | OpenAI GPT Image 2, Gemini 3.1 Flash Image, Grok Imagine Image 2.0, BFL FLUX.2 Pro |
| Frozen semantic mutation | none |
| Credential presence | 4/4 pass; values not printed or stored |
| Local source hash checks | 4/4 pass |
| Data-boundary checks | 4/4 pass |
| BFL public controls | 2/2 exact byte-hash pass |
| Aggregate ledger concurrency | pass; competing reservations cannot independently consume cap |
| Real committed / held spend | $0 / $0 |
| Full-bakeoff reservation ceiling | $4.20 against $100 approved aggregate cap |
| Accepted candidates | 0; no provider request yet |

## External fictional G07 partial execution — 2026-09-01

This is immutable execution/cost evidence awaiting cross-provider human review, not a mechanism score.

| Field | Result |
| --- | --- |
| Completed requests | 5/16: OpenAI 4/4, Gemini 1/4 |
| Provider generation time | OpenAI 128.347 s; Gemini first POST 11.006 s |
| Retrieval/repair overhead | Gemini existing-interaction GET 0.863 s; no repeat generation |
| Exact output hashes recorded | 5/5 |
| Provider request IDs and usage | 5/5 |
| Reconciled documented-rate estimate | $0.265809 |
| Held reservation / available cap | $0 / $99.734191 |
| Human review / accepted | 0 reviewed / 0 accepted |

Later in the same milestone, Gemini reached 4/4 (46.173 seconds, $0.268756 documented-rate estimate). xAI then produced one paid execution failure: $0.07 exact provider ticks and 8.899 seconds, but no candidate because its temporary output URL returned HTTP 403. That failure is operational evidence and is excluded from renderer-quality assertions.

## External fictional G07 completed comparison — 2026-09-01

| Field | Result |
| --- | --- |
| Required candidates | 16/16, four per provider |
| Required-candidate time | 299.995 s |
| Required-candidate cost | $0.987377 |
| Additional paid failure | xAI URL transport, 8.899 s / $0.07 / no candidate |
| Aggregate ledger | $1.057377 committed / $0 held / $98.942623 available |
| Core proxy triage | 16/16 non-gating agent pass; human review pending |
| Human minutes / accepted | null / 0 |
| Selected hardening mechanism | OpenAI GPT Image 2 via ADR-0025; not production acceptance |

Local selected-route hardening then demonstrated byte-identical no-change and zero exterior pixel change under a deterministic target mask at $0 additional external cost. Its rectangular seam remains unacceptable, so no benchmark score or art acceptance follows.

## CH05 chapter-production preflight — 2026-09-01

This is compiler/readiness evidence, not rendered coverage or a benchmark score.

| Field | Result |
| --- | --- |
| Approved ComicPanelPlans | 50/50 compiled |
| Cast-count distribution | 18 zero / 15 one / 17 two adults |
| Motion distribution | 26 observation / 10 directional / 10 sensory / 4 practical |
| Approved bases / RenderRecords / accepted | 0 / 0 / 0 |
| P036 smoke causal/lettering overlap | 64.7059%; mask authoring blocked |
| Abstract P036 mask/lettering overlap | 0%; layout proxy only |
| Demonstration slice | P033–P038, local no-render |
| New provider spend/uploads | $0 / 0 |

The follow-on P033–P038 no-network packet remains 0/6 executable with 36 structured, untimed review tasks. Three source-derived continuity chains validate, while 10/10 malformed/partial gate mutations are rejected. These are compiler controls, not rendered-panel or quality scores.

The deterministic sequence-control follow-up reproduces 13/13 pinned output hashes across consecutive builds, matches role counts 2/2/0/2/0/0, and has 0 story-occupancy pixels in lettering safe zones. Three continuity-color chains pass. ADR-0027 excludes all of these from visual-continuity and art-quality scoring.

The lifecycle-ledger control leaves 6/6 panels at base-approval pending and rejects 18/18 illegal transition, chain-tamper, and aggregate reservation-binding mutations. This is production-state integrity evidence, not a renderer benchmark or accepted-panel result.
