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

Production-budget separation rejects bakeoff-only authority and validates an isolated synthetic reserve/hold/reconcile/release cycle. Candidate intake hash-matches 6/6 deterministic controls but grants 0 approvals or uploads. These are governance/compiler results; provider spend and accepted-panel evidence are unchanged.

Candidate promotion blocks 6/6 deterministic controls and 8/8 prohibited/incomplete review mutations. A synthetic fixture reaches only a validation-only non-approval state. This is gate coverage, not human-review or accepted-art evidence.

The 50-panel run compiler reproduces its pinned root 30/30 times (median 9.120 ms, p95 10.178 ms; 4/4 root mutations detected). All 50 remain base-pending and 250 review task instances remain untimed. Local compiler timing is excluded from provider/human throughput claims.

Review/progress validation computes a paused 15-minute fixture exactly, rejects 10/10 timer mutations and 22/22 combined run/budget/review mutations, and keeps real CH05 at 0/50 accepted with null minutes. The separate retry fixture produces 2/50 accepted from 3 attempts/1 retry and is excluded from real metrics.

Selected-route offline P036 preflight exposes 4/4 real blockers, blocks 6/6 prerequisite mutations, and contains no client/body/executor. The full local suite passes 21/21 checks in 2.652 seconds. These are readiness/integrity measurements; renderer quality and accepted-panel evidence are unchanged.

Submission-journal simulation validates pre-submit release, unknown-outcome hold/non-retry, and recovered completion; duplicate keys plus 11/11 transition/tamper/budget mutations fail. It is crash-integrity evidence only and creates no provider execution result.

Production evidence schemas validate synthetic success/failure/unknown outcomes and reject 12/12 completeness/contradiction mutations. Unknown incidents cannot contain RenderRecords or candidates. This is schema coverage, not new rendering evidence.

G07 evidence-vault validation hash-matches 19/19 provider records and 16/16 candidates under root `e84b0402…6d3ab`, rejects 5/5 manifest mutations, and proves zero generated experiment paths are tracked. It reconciles $1.057377 total paid and $0 held, including the paid xAI failure and single-charge Gemini recovery. This is retention/accounting integrity only; pending human review, accepted count, renderer-quality evidence, and mechanism selection are unchanged.

The local restoration rehearsal verifies 38/38 exact archive members and rejects 5/5 missing/extra/corrupt/path-escape/duplicate mutations. Archive size is 19,879,277 bytes and SHA-256 is `64bea215…69cad7`. This is recoverability instrumentation, not an additional renderer sample, benchmark score, review, or production result.

The blinded G07 protocol verifies 16/16 neutral candidate presentations and 4/4 hidden-arm repeat pairs, requiring 20 timed assertion decisions; 13/13 identity/order/coverage/timing mutations fail. Actual decisions remain 0, minutes null, and accepted subjects zero. This adds review readiness, not human renderer-quality evidence or a new selection decision.

The fail-closed review rollup binds 4/4 arms and 16/16 candidates to separate cost, latency, drift, assertion, and failure-tag dimensions; 9/9 pending/fixture/coverage/mapping mutations fail. With review still pending it emits no human arm results, composite score, rank, or route change. Renderer-quality evidence and ADR-0025 remain unchanged.

Selected-route boundary hardening compares seven inward-only compositor variants. The 16-pixel cosine boundary is the sole predeclared-rule pass: 91.263% artificial-jump reduction, 99.462% central green signal, zero exterior changes, and zero P036 lettering overlap; 8/8 evidence mutations fail. This is fictional-proxy compositor mechanics, not visual acceptance or narrative-panel evidence.

P036 current-mask topology retains 79.032% core and 1/1 component under the 16-pixel policy with zero exterior/lettering changes, but the source mask is a perfect rectangle and exercises no thin, concave, holed, or multi-component topology. The narrative-topology assertion is therefore not tested, not passed.

The P036 causal-shape control selects 8px context padding from five variants under the fixed 16px boundary: 42.107% connected union core, 4/4 causal features above 15% core retention, rectangularity 0.215863, and zero exterior/lettering change; 10/10 mutations fail. This advances abstract repair topology mechanics only, not panel art or mask approval.

The local repair policy pins those mechanics but leaves real P036 preflight at four blockers and zero request capability. Proxy controls fail production-input promotion; 11/11 policy/input/authority/reservation mutations fail. This is policy/gate coverage, not a render or accepted panel.

P036 readiness r2 pins r1 plus policy/mechanics/budget/preflight evidence while retaining four blockers and zero approved inputs or activity; 11/11 immutability/gate/input/execution/medium mutations fail. It is a readiness revision, not an additional renderer benchmark sample.

CH05 repair-policy coverage retains 50/50 panels: four explicit causal candidates, one exact panel policy, three policy-absent candidates, and 46 without plan-level applicability. No panel is executable and 10/10 denominator/policy-leak/execution mutations fail. This is chapter compiler coverage, not rendered or accepted coverage.

The next-control information-gain record compares the three policy-absent causal panels and selects P044 only for a bounded blade/twine topology stress control; 8/8 selection/mechanism/authority mutations fail. No production policy, mask, renderer sample, or acceptance follows.

The P044 fixed-width stress leaves 0 fully replaced core pixels for an 18px blade and 12px twine under the unchanged 16px boundary, despite one support component and zero protected/lettering/exterior change; 9/9 mutations fail. This rejects absolute-width portability on the control, not the panel or provider route.

P044 adaptive-width control selects 5px as the widest topology pass on unchanged support (18.496% union / 22.945% blade / 18.170% twine core); 6px is the first larger failure and 9/9 mutations fail. This is topology mechanics without visual seam or production-policy evidence.

The scale-aware selector keeps P036=16px and P044=5px as separate local profiles with 2 topology passes but 0 exact-panel visual passes, 0 timed seam reviews, and 0 production-ready profiles; 10/10 width/visual/generalization mutations fail. It is a gate contract, not renderer-quality evidence.

The append-only v2.1 repair evidence contract validates synthetic completed, explicit-failure, and outcome-unknown paths and rejects 15/15 evidence contradictions. Completed fixtures require the full selector/topology/exact-base/exterior/no-change/timed-seam chain; failure and unknown states cannot fabricate it. This is schema/integrity coverage, not a renderer-quality observation, real human review, accepted panel, or production result.

The 50-row repair-evidence matrix measures four explicit candidate panels, two local selector/topology profiles, one panel policy, and zero production inputs, authority, budget reservations, exact-base visual results, seam reviews, v2.1 RenderRecords, candidates, or acceptances; 13/13 inference/fabrication mutations fail. This is chapter-denominator readiness evidence, not rendered or accepted coverage.

The synthetic exact-base packet measures 64,992 support / 35,150 transition / 27,366 full-core pixels, exact exterior equality, 98.838% fixture boundary-distance reduction, and byte-identical no-change; 14/14 mutations fail. Its review remains pending with null minutes, so it adds measurement-instrument coverage only—not real panel, renderer-quality, narrative, or acceptance evidence.

V2.1 completed-fixture validation now derives seam subject, event-chain integrity, reviewer, three active minutes, fixture ineligibility, decision, and four assertions from exact referenced records; 18/18 contradictions fail. This is provenance validation only: the accepted fixture decision is not eligible human evidence and does not change the real zero-review/zero-acceptance state.

The repair finalizer reports nine real P036 blockers and emits no outcome, while two synthetic validation finalizations are digest-identical and fixture promotion fails; 10/10 mutations fail. This measures fail-closed finalization mechanics, not provider, candidate, human-review, or production throughput.

The pinned instrumentation runtime matches CPython 3.14.6, Pillow 12.3.0, and numpy 2.5.1 with exact interpreter/source hashes; a no-write bootstrap completes 43/43 checks in 26.524 seconds and 10/10 runtime mutations fail. This is local reproducibility/readiness timing, not provider or human production throughput.

Two consecutive selected-route rebuilds produce the same 26-file, eight-group, 4,862,061-byte root `0a04832b…d3f3b18`; 8/8 mutations fail. This exact-byte result is bounded to enumerated local artifacts and the measured runtime; it excludes provider outputs, human evidence, timestamps, and throughput claims.

The fail-closed G07 rollup validator improves from 10.615 seconds to a five-run median 1.706 seconds (83.93% lower / 6.22x) by reusing one already-verified mapping root per process. Gate bytes and 9/9 mutations are unchanged. This is local validation runtime, not actual reviewer or provider throughput.

Safe-source baseline `f505788` contains 346 tracked paths / 8,184,364 bytes with exact tree `df2c40bb…c5e67` and SHA-256 inventory root `2993f2d4…a52cde`; 8/8 mutations fail and generated/prohibited/oversize counts are zero. This is source-release integrity, not generated-artifact retention or production output.

Static/no-network aggregate-budget audit confirms 4/4 paid adapters reserve before paid submission with no local cap; 18 ledger entries reconcile to 17 committed/one release/zero held and $1.057377 actual; 10/10 mutations fail. This is post-run control integrity, not new provider execution.

Transport audit confirms four HTTPS endpoints, verified native TLS on every `urlopen`, explicit HTTPS guards on provider-returned Gemini/BFL URLs, exact two input hashes, and six intact prohibited classes; 9/9 mutations fail. This is static security/data-boundary evidence with zero network activity.

The cross-evidence hardening state preserves OpenAI as engineering route only: selected arm four candidates/$0.198621/128.347s, G07 review 0/20/null/zero, chapter 50 plans/four explicit/two profiles/one policy/nine blockers/zero outcomes; 15/15 promotion mutations fail. It is a handoff state, not a new score or result.

Panel-neutral disconnected/hole stress selects local 8px on fixed ring+32px geometry, retaining two cores at 62.915%/25.936% with exact hole/exterior; 12/12 mutations fail. This expands abstract topology coverage only, not panel applicability or visual acceptance.

Selector r2 preserves two exact panel profiles (P036=16px/P044=5px) and records the 8px disconnected/hole result only as a generic control: three topology passes, zero exact-panel visual/review/production-ready passes; 13/13 promotions fail. No universal width is inferred.
