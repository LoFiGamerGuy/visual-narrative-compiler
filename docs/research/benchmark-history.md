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

The CH05 variable-cadence assembly selects 14 existing candidates across three sequences, eight widths, and three alignments. Two consecutive builds preserve identical packet/artifact hashes; 10/10 negative controls fail. The full/phone scrolls measure 1200×14,566 and 390×4,734 with seven phone viewports. This measures deterministic local assembly and provisional cadence readability, not renderer reproducibility, human acceptance, commercial clearance, or production-base eligibility.

The CH05 transparent-lettering rehearsal builds 12 local treatments and 25 artifacts twice to an identical packet hash. All backing arms exceed 11.942:1 fifth-percentile measured black-type contrast, but current cadence footprints yield only 6.513–11.366px type and c014 fails person clearance. Twelve/twelve mutations fail. This measures backing contrast, footprint, and reviewed placement constraints—not final dialogue, font licensing, accessibility conformance, human acceptance, or production lettering.

The CH05 width/copy sweep measures 30 local cases and 31 artifacts. The first 13px passes occur only at 1200px for c005/c013 and at 1120px one-line/1200px two-line for h001; c014 is excluded. Twelve/twelve mutations fail. This measures one font, two placeholder copy shapes, one backing, and candidate-specific geometry—not a universal width, final copy, localization, semantic acceptance, or plan revision.

The CH05 outside-art comparison builds two 14-panel scrolls plus phone versions and a side-by-side sheet. Six bands render 13.975px type, change zero source pixels, and increase scroll height 480px/3.295%; 12/12 mutations fail. This proves local caption/direct-text geometry only—not speaker binding, final copy, plan authority, assembly acceptance, or production lettering.

The CH05 production-handoff compiler emits 14 exact rows/three sequences with a stable canonical row root and rejects 15/15 promotion mutations. The local owner index covers 29 candidates/14 selections/12 review links/42 artifacts, validates every HTML link/hash, and rejects 12/12 mutations. This measures evidence compilation and review ergonomics—not generation reproducibility, commercial eligibility, owner acceptance, full 50-panel rendered coverage, or executable production throughput.

The CH05 density diagnostics measure 14 phone-footprint panels and 13 adjacent feature jumps while retaining exact 26-candidate engineering triage. c005 has 0.308471 edge occupancy; c014→c015 is the maximum z-scored global-feature jump at 5.6517; 12/12 mutations fail. This is appearance-density instrumentation, not character recognition, balanced style benchmarking, aesthetic scoring, or acceptance.

The CH05 overnight release gate executes and reproduces 16/16 no-network validators in 5.259 observed seconds, rejecting 15/15 release-state mutations. It includes frozen/baseline and source-scope checks. This measures integrated evidence integrity and local reproducibility—not renderer determinism, visual acceptance, commercial clearance, or production throughput.

The CH05 remaining-panel compiler partitions 50 exact plans into 14 selected plus 12/12/12 future tranches, rejecting 13/13 manifest and 10/10 evidence mutations. It measures denominator and dependency coverage—not rendered coverage, prompt readiness, acceptance, or permission for further generation.

The append-only CH05 release r2 reproduces immutable 16-check r1 and adds two coverage checks: 18 effective checks pass through three orchestrator commands in 5.308 seconds; 13/13 mutations fail. This is release-integrity coverage, not production authorization.

The Tier A effort record derives three generation-only scenarios from 26 exact CH05 timings (1,230.058s; p10/median/p90 30.531/51.227/56.524s) and rejects 13/13 prompt/decision/cost/activity mutations. It is bounded planning evidence, not a throughput SLA, cost estimate, human-time estimate, or execution authority.

The owner decision worksheet deterministically binds 39 pending subjects to 29 candidate and ten higher-order local review links; consecutive HTML builds have exact hash `60795713…ed3a` and 8/8 boundary mutations fail. This measures offline review-surface integrity, not review completion, quality, acceptance, or human time.

The owner-decision draft validator accepts 3/3 well-formed synthetic local-draft shapes, rejects 14/14 malformed fixtures, and rejects 16/16 evidence mutations while the live contract stays empty. This is schema and boundary coverage, not owner review, event ingestion, or acceptance.

The character-assertion compiler covers 50/50 plans and the lint passes 26/26 exact CH05 prompts, including 4/4 P036 composition-only guards; 16/16 evidence mutations fail. These are metadata/string checks and do not measure rendered identity, hair, wardrobe, anatomy, or visual quality.

The manual continuity atlas covers 26/26 canonical candidates across 14 plan groups plus the selected 14 sequence, with byte-identical full-panel artifacts and 16/16 mutation rejection. Existing manual engineering labels are 17 pass/3 warn/6 fail, hair/wardrobe 26 pass, and role order 25 pass/1 fail; no automated identity measurement is claimed.

The panel-scale/cadence policy covers 50/50 plans with nine conditional roles and 520–1,200px ranges, bound to 14 selected footprints, 30 lettering cases, and outside-band measurements; 19/19 mutations fail. It is a recommendation matrix, not accepted layout, typography, or chapter throughput.

The failure-class matrix covers nine nonpass candidates and six exact repair links: five target fixes and four all-dimension passes, with 24/24 mutation rejection. The proposed P010–P013 microsequence is a bounded next experiment, not a repair-rate forecast or execution authority.

The P010–P013 preflight binds 4/4 exact plans, four hypotheses, and two unallocated repair slots with 25/25 mutation rejection. Prompts, uploads, final copy, decisions, executable rows, and spend remain zero; this is readiness-contract coverage, not rendering throughput.

Owner review index r2 validates 7/7 local links (five images/two HTML), six deterministic index artifacts, and 13/13 mutations while extending r1 without rewriting it. This is review-navigation integrity, not review completion or acceptance.

Integrated release r3 preserves a failed first attempt, rebinds the mutable registry through manifest r2, then passes 13/13 orchestrator commands / 30 effective checks in 6.202s with 23/23 mutation rejection. Frozen 16 + baseline 4 and source scope pass; this is release integrity, not art acceptance.

The chapter-scale envelope covers the remaining 36/36 plans with 36/49/72 candidate scenarios and median generation-only values of 1,844.172/2,510.123/3,688.344s; 25/25 mutations fail. These exclude queue, review, layout, lettering, release, money, and human-time estimates.

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

Expanded rebuild r2 pins r1 and produces identical two-pass inventories of 28 artifacts / nine groups / 4,868,771 bytes at root `18816d3c…e50d64`; 10/10 mutations fail. The two new files are local disconnected/hole mechanics outputs only.

The aggregate hardening release gate passes 44 unchanged core checks plus nine append-only extensions, 53/53 total, in an observed 69.752 seconds; 8/8 release-state mutations fail. Budget audit r3 separately rejects 12/12 mutations and preserves the same 18-entry/$1.057377 reconciliation. These are local integrity timings and counts, not rendering, review, or production throughput.

Selector-consumer compatibility validates six direct source consumers, three immutable evidence bindings, and six focused validators against canonically identical r1/r2 pipelines and P036/P044 profiles; 15/15 mutations fail. This measures provenance compatibility only, not visual quality, review, or production readiness.

The selected-route authority frontier validates a 20-node/20-edge acyclic graph with five root authority items, 0/20 G07 decisions, and four root/nine total P036 blockers; 18/18 mutations fail. This is dependency accounting, not authority, execution, or acceptance.

Safe-source r2 pins pushed commit `43fc787` with 387 paths / 8,535,516 bytes, tree `4e85a8c3…5f70b`, and inventory root `53af7d04…13d6b`; 13/13 mutations fail and prohibited/generated/oversize counts remain zero. This is source integrity, not artifact or production evidence.

Release gate r2 runs the immutable 53-check r1 result plus seven post-r1 validators: 60/60 pass in an observed 79.280 seconds and 11/11 mutations fail. This is local release-integrity timing, not renderer, reviewer, or production throughput.

Selected-route handoff r2 preserves all r1 renderer measurements and blocked production counts while binding three topology passes, 28 rebuilt artifacts, 60/60 release checks, 387 safe-source paths, five root authority items, and 37 zero-cost milestones; 18/18 mutations fail. This is current cross-evidence provenance, not new renderer evidence.

The P036 prerequisite lattice exhausts 16/16 subsets: 15/15 partial states are blocked, the complete fixture is metadata-only, the complete non-fixture proxy attempt is blocked, and 17/17 mutations fail. This is fail-closed combinatorial coverage, not production authority or throughput.

Release gate r3 runs the immutable 60-check r2 result plus five handoff/lattice/ledger checks: 65/65 pass in an observed 80.178 seconds and 16/16 mutations fail. This is local integration timing and boundary integrity, not renderer, review, or production throughput.

Safe-source r3 pins pushed commit `00498df` with 412 paths / 8,791,840 bytes, tree `3052f539…cc6d1`, and inventory root `a3a0c65c…3e618`; 13/13 mutations fail and generated/prohibited/oversize counts remain zero. This is source integrity only.

The current evidence index resolves 11 domains across 32 exact lineage records and validates every supersession/validator hash; 18/18 mutations fail. This is provenance-navigation coverage, not renderer, review, or production throughput.

The executable reproducer matrix runs all 11 current-domain commands successfully in 114.636 seconds; nested release/rebuild/source timings are 79.872/23.043/8.466 seconds and 17/17 mutations fail. This is local evidence-runtime coverage, not provider or human throughput.

Frozen-target integrity compares 16 authoritative v2.1.1 and four tracked baseline paths from `f505788` to `00498df`: all are byte-identical; baseline stays 0/24 accepted/no tuning and 15/15 mutations fail. This is immutability evidence, not a renderer rerun.

The review/authority handoff separates one 20-decision G07 task from four CH05 root items, keeps every field blank, binds 11 reproducers/65 release checks/frozen integrity, and rejects 19/19 mutations. This is handoff integrity, not completed review or authority.

Reproducer matrix r2 passes 11/11 commands in 115.394 seconds using stable terminal-result hashes; release r4 passes the immutable 65-check r3 base plus nine extensions, 74/74 in 197.859 seconds, with 18/18 mutations rejected. The first r4 attempt failed on an overbroad mutable diagnostic binding and was not hidden or rewritten.

Provider-document chronology binds four sections/19 official links to 19 exact provider records; documentation leads the earliest attempt/positive-cost request by 490/695 seconds and 16/16 mutations fail. This is pre-spend provenance, not a claim that live terms never change.

The autonomous closeout binds 12/12 operating requirements and rejects 22/22 mutations while preserving 16 candidates/$1.057377, G07 0/20, 74/74 release checks, 11 reproducers, 50 ComicPanelPlans, and zero CH05 outcomes/cap. This closes engineering scope only, not human review or production authority.

Final release r5 runs immutable r4 (74 checks) plus five chronology/closeout/ledger checks: 79/79 pass in 198.132 seconds and 18/18 mutations fail. It validates engineering closeout while explicitly retaining incomplete review and production authority.

Safe-source r4 pins pushed commit `f1803bd` with 459 paths / 9,234,040 bytes, tree `aaab99df…35e0c`, and inventory root `1ce5104c…b41e6`; 13/13 mutations fail and generated/prohibited/oversize counts remain zero. This is final source/Git provenance, not production readiness.

Owner-directed style/density/scale exploration produces four local text-only candidates at 1693×929, 944×1666, 1122×1402, and 1023×1537 across three panel-format roles. The first P036 prompt produces a climb instead of lever action; the corrected prompt materially improves grounding and causal span. Two packet rebuilds reproduce exact contact-sheet/overlay hashes `3295256b…b7bebd` / `e03e9c0d…38e02`, and 12/12 boundary mutations fail. These are qualitative research candidates with unavailable built-in-tool cost/model metadata, not renderer throughput or accepted production evidence.

CH05 overnight production r1 registers 20 candidates across 14 ComicPanelPlans, three sequences, four styles, and four text-only controls in 919.389 observed seconds (45.969-second mean). Provisional per-style all-six-dimension results are cel-painted 4/4, clear-line watercolor 3/6 with two warnings/one failure, limited ink 3/5 with one warning/one failure, and clean graphic 2/5 with three failures; role coverage is imbalanced, so these are engineering triage counts rather than a global style score. The deterministic evidence validator passes with all output/prompt/reference/artifact hashes exact and all generated pixels ignored.

CH05 cadence hardening r1 adds six candidates in 310.669 seconds (51.778-second mean): five pass all six engineering dimensions and one is a preserved duplicate-plank diagnostic. The missing cel-painted wide-action arm passes, three source safe-zone collisions are corrected, and single-plank reach-and-brace wording resolves the P036 lever-induced geometry failure. Combined overnight/hardening evidence is 26 candidates, 14 distinct plans, and 1,230.058 observed seconds; built-in cost/model/request/seed remain unavailable.

Future LitRPG concept r1 adds three non-canon candidates. Two equipment sheets and one wide monster-action concept preserve hair/identity/wardrobe lineage and phone silhouettes; exact cross-concept armor replication remains untested because concept outputs were not re-uploaded. ADR-0109 reconciles exact candidate records to 154.978 concept seconds (51.659-second mean), 1,385.036 seconds across all 29 candidates, and 39 reference uses; earlier 155.766/1,385.824-second summaries remain historical evidence. This is visual-development evidence, not CH05 throughput, canon, acceptance, or commercial clearance.

The all-candidate RenderRecord audit resolves 29/29 prompts, candidate files, output hashes, dimensions, elapsed times, review states, and input references. Six service fields are explicitly unavailable (`model`, `endpoint`, `request_id`, `provider_usage`, `provider_cost`, and `seed`) in every record. The audit rejects 27/27 mutations and the timing reconciliation rejects 12/12; all 29 candidates remain pending and unaccepted.

Integrated release r4 preserves the 30-check r3 chain and adds three exact evidence validators. Four/four orchestrator commands pass in 6.934 seconds, 33 effective checks are represented, and 23/23 mutations fail. Frozen 16 plus baseline 4 remain exact; this is release integrity, not art acceptance or production authority.

Owner review index r3 adds a deterministic 12-card local entry point with ten image and two HTML links; two builds are byte-identical and 13/13 mutations fail. The exhaustive link manifest resolves 99 unique ignored local artifacts and 99 categorized links, with every hash, byte count, ignore state, absolute path, and Markdown target validated; 15/15 mutations fail. A mistaken 100-artifact first expectation is retained as failed evidence rather than hidden.

The measured route recommendation binds four role allocations and ten still-null owner decisions. Cel-painted is 5/6 all-pass, clear-line 5/8 with successful targeted repairs, limited ink 4/6 but density-conditional, and clean graphic 3/6 as a blocking control. Seventeen/seventeen mutations fail. This selects an engineering mechanism by observed behavior, not visual appeal, while leaving acceptance/commercial/exact-base state open.

The P010–P013 production-manifest dry run binds four exact rows, three reference hypotheses, two bounded repair slots, five planned review artifacts, and five production stages. All prompt/output/service/review fields remain null and all execution/promotion activity remains zero; 20/20 mutations fail.

The P010–P013 review contract binds 44 empty candidate checks, five unbuilt artifacts, 11 failure classes, and five promotion rules before rendering. Candidate/sequence review and repair state remains empty; 17/17 mutations fail. This prevents review criteria from drifting around the eventual outputs.

Integrated release r5 preserves the 33-check r4 chain and adds five independent post-r4 validators. Six/six commands pass in 9.346 seconds, 38 effective checks are represented, and 26/26 mutations fail. The release binds 99 artifacts and the next four-slot/44-check production-review shape without granting execution or acceptance.

The 50-plan readiness matrix partitions exactly into 14 selected-evidence, four dry-run, eight other Tier A, and 24 backlog rows. Fourteen plans have 26 existing candidates; every plan has continuity/scale/mechanism data, while every next prompt and promotion field remains closed. The visually checked map is 1600×1900 and 20/20 mutations fail.

The minimal reference-risk plan assigns 42 metadata hypotheses across 50 plans: 18 no-person text-only, P050 25, P040 16, and P036 composition-only one. Risk classes are 18/9/22/1 low/medium/high/critical-guarded. The 1600×1900 map is visually checked and 20/20 mutations fail; the initial 43-use estimate remains preserved as failed evidence.

The live-only review timer binds 39 subjects, four transitions, seven fields, and six rules. Three valid synthetic logs pass and 12 malformed logs fail; a 20-second active fixture derives 0.333333 minutes. Sixteen/sixteen evidence mutations fail, while actual review minutes remain null.

The owner handoff checklist binds 24 linked tasks—14 candidate and ten route—in dependency stages 19/4/1, with one optional non-canon task. Every prerequisite points to an earlier stage and 16/16 mutations fail; no decision or minute is recorded.

Integrated release r6 preserves the 38-check r5 chain and adds four independent validators. Five/five commands pass in 9.946 seconds, 42 effective checks are represented, and 26/26 mutations fail. Fifty plans, 42 references, 24 owner tasks, and 39 timer subjects are release-bound without execution or review activity.

The chapter production-batch manifest partitions 50 plans into 12 contiguous sequences of 3–5 panels and four readiness waves distributed 1/2/5/4. Forty-eight review artifacts are predeclared, the 1800×1220 map is visually checked, and 19/19 mutations fail. Narrative order remains distinct from production readiness.

The lettering-semantics matrix partitions 50 plans into 16 silent inserts, 14 protected action/motion, 13 caption-or-silence, six speech/reaction, and one attributed-speech row. All copy remains null and overlap/acceptance stays zero. The 1600×1900 map is visually checked and 16/16 mutations fail.

Owner hub r4 links six current resources and builds byte-identically; 15/15 mutations fail. Link manifest r2 preserves 99 r1 artifacts and adds six, producing 105 exact links (104 ignored local/one tracked metadata); 14/14 mutations fail.

Integrated release r7 preserves the 42-check r6 chain and adds four independent validators. Five/five commands pass in 14.531 seconds, 46 effective checks are represented, and 25/25 mutations fail. Twelve batches, 50 lettering rows, and 105 links are release-bound without prompt or promotion state.

The consolidated delivery bundle binds 29 candidates, 14 represented CH05 plans, 50 total plans, 12 sequence batches, 105 review links, 14 strongest candidates, ten owner decisions, and eight explicit limitations. Its 21/21 mutation suite rejects altered counts, timing, reference use, spend, decisions, acceptance, executable state, parity, and cross-medium planning. This is handoff completeness evidence, not a visual-quality benchmark or promotion.

Safe-source delivery parity pins pushed commit `a1454db` at 735 paths/11,861,823 bytes, tree `7a7085da…c4d`, and inventory root `fea9401e…4ca`. Two public controls and zero generated/prohibited/oversize/credential paths are tracked; 16/16 mutations fail. Ignored pixels and unrelated untracked items remain out of the release inventory.

Integrated release r8 preserves the 46-check r7 chain and adds delivery, cost-ledger, and safe-source extensions. Four/four commands pass in 30.259 seconds, 49 effective checks are represented, and 26/26 mutations fail. The gate binds the measured handoff and 735-path source capture without granting promotion or execution.

R8 post-commit reproduction exposed one expected dynamic stdout mismatch: the live tracked-safe-source path count increased after committing r8. Compatibility r1 preserves that failure and normalizes only the numeric diagnostic on one of four commands; all 4/4 normalized outputs match and 10/10 mutations fail. No inventory or semantic field is normalized.

The compact final reproducer matrix runs seven independent domains in 47.129 seconds. All seven pass, the underlying release represents 49 checks, and 20/20 matrix mutations fail. Only safe-source/current-scope live count diagnostics normalize; script, input, captured inventory, frozen, cost, and remote-lineage evidence remain exact.

The P010–P013 unlock contract identifies six exact owner-decision roots, four deferred choices, and 14 existing-candidate reviews. It keeps the next pilot at four slots/two repair slots/five planned artifacts while prompt/render/promotion remains 0/0/0. Seventeen/seventeen mutations fail; broad approval is direction, not structured acceptance.

The P010–P013 prompt blueprint adds four exact draft hashes with 4/4 lint pass, three authorized-reference hypotheses across two unique hashes, and one text-only object control. Fifteen/fifteen mutations fail. Production prompt fields remain null, making this preparation evidence rather than execution throughput.

Independent blueprint validation passes the four real rows and rejects 28/28 malformed fixtures: age/likeness 2, continuity/role 5, causal/lettering 3, reference boundary 4, and promotion/schema 14. This is robustness evidence for draft validation, not render quality.

The P010–P013 pre-render builder dry-run passes with four absent candidate slots, five `NOT_BUILT` outputs, 44 empty checks, four safe-zone hypotheses, and 17/17 mutation rejection. It is packet-readiness evidence; no build/render timing or visual result exists yet.

The pilot lifecycle state machine exhausts 121 state pairs: 11 legal transitions and 110 illegal/unconfigured pairs. Its four-edge repair loop is capped at two slots, and 18/18 mutations fail. This measures workflow guard coverage, not art or provider behavior.

The chapter lifecycle application covers 50 plans/12 batches with one lifecycle-entered and 11 not entered, preserving waves 1/2/5/4. Seven reusable contract classes are separated from eight batch-specific evidence classes; 49 review artifacts are planned and 22/22 mutations fail. The 1900×1480 map is visually checked.

Owner hub r5 builds byte-identically with seven links and two ignored local artifacts; 16/16 mutations fail. Exact link manifest r3 preserves 105 prior bindings and reaches 112 resources (106 ignored/six tracked); 15/15 mutations fail.

Integrated release r9 uses the compatible 49-check r8 base plus nine extensions. Ten/ten commands pass in 83.926 seconds, 58 effective checks are represented, and 30/30 mutations fail. Ledger r26 records 64 local zero-external-cost milestones.

Chapter duration capacity uses 30.531/51.227/56.524-second p10/median/p90 candidate timing. The 49-candidate remaining-plan arm totals 1,496.019/2,510.123/2,769.676 seconds; the fresh 68-candidate arm has 3,483.436-second median. Wave loads are 6/12/20/11. Human time and built-in cost remain null.

The production operating playbook validates 12 steps, 11 shell commands, one agent-only action, five local-ready steps, one owner-action step, and six blocked steps. Eighteen/eighteen mutations fail. This is operational-readiness evidence, not execution.

Delivery bundle r2 binds the current 29-candidate/50-plan/12-batch body, 112 review links, 14 strongest candidates, ten unresolved route/rights decisions, six unresolved pilot roots, 58 integrated checks, and 12 playbook steps. Its 27/27 mutation suite rejects denominator, parity, time, spend, decision, acceptance, execution, and cross-medium changes. The 49/68 capacity arms remain planning envelopes rather than quality or throughput forecasts.

Owner hub r6 rebuilds byte-identically with five current-delivery links and two ignored local artifacts; 17/17 mutations fail. Exact link manifest r4 preserves 112 bindings and reaches 117 resources (108 ignored/nine tracked); 15/15 mutations fail. Ledger r27 records 68 zero-external-cost milestones and zero external requests/uploads/$0 paid spend.

Integrated release r10 preserves the 58-check r9 base and adds eight current-delivery domains. Nine/nine commands pass in 89.568 seconds, 66 effective checks are represented, and 34/34 mutations fail. Only the decimal live tracked-path diagnostic normalizes; no evidence inventory or semantic state is normalized.

Safe-source parity r2 pins pushed commit `479f7ca` at 835 paths/12,795,182 bytes, tree `c67628dc…0d04`, and inventory root `ae1563f8…fa22`. Two approved controls and zero generated/prohibited/oversize/credential/model/dataset/private-reference paths are tracked; 17/17 mutations fail.

Final evidence reproducer matrix r2 passes 7/7 current domains in 108.029 seconds and rejects 23/23 mutations on independent replay. It binds release 66 checks, 29 candidates, 50 plans, 117 links, 835 safe paths, frozen 16 + baseline 4, and 68 zero-cost milestones; only two live tracked-count diagnostics normalize.

The owner-defaults packet binds ten evidence-backed recommendations as six pilot roots plus four deferred choices. Sixteen/sixteen mutations fail; all structured owner decisions and promotion state remain empty. The future LitRPG recommendation advances three motifs only to a separate proposal, not CH05 canon.

Owner hub r7 rebuilds byte-identically with five final-evidence links and one ignored artifact; 17/17 mutations fail. Exact link manifest r5 preserves 117 bindings and reaches 122 resources (109 ignored/13 tracked); 15/15 mutations fail.

Closeout bundle r1 reconciles 29 candidates, 50 plans, 12 batches, 122 resources, and 67 explicit high-priority links (10 contact sheets/9 sequence packets/34 lettering overlays/14 strongest). It binds a 393-path/62-ADR base inventory and rejects 24/24 mutations without promotion.

Integrated release r11 uses the current seven-domain reproducer over immutable r10 and adds eight final extensions. Nine/nine commands pass in 133.281 seconds, 74 effective checks are represented, and 29/29 mutations fail. Ledger r28 records 73 zero-external-cost milestones.

Final safe-source r3 pins pushed commit `b13d87b` at 873 paths/13,394,576 bytes, tree `b6569cd0…5e6e`, and root `49e6a5a0…a192`; 17/17 mutations fail. Final remote parity also passes release 74, closeout, frozen integrity, and current tracked scope.

Closeout r2 binds final release 74, safe-source 873, cost 73, current parity, and a refreshed 410-path/65-ADR inventory while preserving all 67 direct review links. The source capture is correctly modeled as an ancestor; 21/21 mutations fail.

Final model/license/provenance audit reconciles 29 records, 39 uses, three hashes, and six unavailable fields × 29 records. All acceptance/clearance/reproducibility counts remain zero; 24/24 mutations fail. This is provenance completeness, not a commercial-use conclusion.

The owner-response schema validates one null template and two synthetic complete responses while rejecting 20/20 malformed fixtures and 19/19 evidence mutations. It validates only six exact roots and performs no ingestion or authority expansion.

The separate six-root live timer records the architecture mismatch with the 39-subject timer: three exact mappings and three missing. Three/three valid logs pass, 12/12 malformed fail, and 19/19 evidence mutations fail; no live event exists.

The final review-session starter binds eight dependency-ordered steps across the current 122-resource hub and 67 priority links. State partitions as 1 ready/4 owner-action/2 blocked/1 intentionally unimplemented; both planned local inputs remain absent and 25/25 mutations fail. This measures handoff completeness, not review completion or production readiness.

The owner-ingestion preflight performs eight checks and returns expected exit 2 in the live absent-input state. Two deterministic valid synthetic replays pass, 12 malformed cross-file pairs fail, and 19 evidence mutations fail. Root, decision, reviewer, per-root minute, lifecycle, and hash parity are tested without ingestion or state transition.

Owner hub r8 builds byte-identically with six links and one ignored artifact; 22/22 mutations fail. Exact link manifest r6 preserves 122 prior bindings and reaches 128 resources (110 ignored/18 tracked); 17/17 mutations fail.

Final-review release r12 preserves a 10/11 attempt, then uses one exact nested-lineage compatibility rule over immutable r11. The successful run passes 11/11 commands in 139.975 seconds, represents 84 checks, and independently rejects 33/33 mutations. Ledger r29 totals 82 zero-cost milestones.

Final safe-source r4 pins pushed commit `df41783` at 934 paths/14,070,835 bytes, tree `f5d1a7b6…e0c53`, and root `c512c072…1f07`. Two controls and zero generated/prohibited/credential/model/dataset/private-reference paths are tracked; 19/19 mutations fail.

Closeout r3 binds 29 candidates/50 plans/12 batches/128 resources/67 priority links to release 84, source 934, cost 82, provenance 29, and frozen 16 + baseline 4. Its pushed compile base spans 471 paths/74 ADRs; 25/25 mutations fail.

The final handoff matrix joins nine current records: 12/12 consensus facts agree, zero unexplained conflicts remain, one expected 873→934 source-lineage delta is disclosed, and 25/25 mutations fail.

The strongest-candidate worksheet binds 14 exact hashes and 112 visual checks. One valid synthetic response passes, 14 malformed/authority-expanding responses fail, and 16 evidence mutations fail; the tracked template remains unfilled.

Owner hub r9 builds byte-identically with six links and rejects 22/22 mutations. Exact link manifest r7 preserves 128 prior bindings and reaches 134 resources (111 ignored/23 tracked); 19/19 mutations fail.

Final review reproducer r3 passes 10/10 domains in 166.588 seconds and independently rejects 29/29 mutations. It binds 29/50/12/134/67/112, release 84, source 934, cost 82, frozen 16 + baseline 4, and current remote parity.

Post-reproducer safe-source r5 pins pushed commit `eafe1ef` at 971 paths/14,675,859 bytes, tree `4bcd007b…b4e2`, and root `7c5cb05b…ab2df`; 18/18 mutations fail with pixels/prohibited material excluded.

Completion readiness binds 12 deliverables, 134 exact links, 67 priority links, all requested counts/timing/failures/recommendations/limitations/decisions, and current source parity; 41/41 mutations fail. This is handoff completeness, not visual or commercial acceptance.

Final integrated release r13 passes 9/9 commands in 194.497 seconds across 18 effective domains and independently rejects 33/33 mutations. Cost ledger r30 reaches 91 zero-external-cost milestones.

The post-r13 delivery audit binds nine ordered owner-review resources and rejects 27/27 mutations. It is the final navigation layer and preserves ten unresolved decisions plus zero owner/promotion/provider activity.

Terminal post-pointer integrity passes r13/pointer/link/frozen/scope/source/remote checks and rejects 24/24 mutations. Four pending audit files are separated from nine unrelated untracked user items.

Final push record r1 binds terminal ancestor `153bff7`, exact parity, 996 tracked paths, nine excluded user items, and rejects 21/21 mutations.

Final push r2 preserves r1's pending-ADR bookkeeping failure, corrects the unrelated-item denominator to nine at ancestor `7842cce`, and rejects 21/21 mutations.

## CH05 complete-chapter sequence production and targeted repair — 2026-09-02

Eleven sequence-strip generations cover all 50 approved ComicPanelPlans, producing 50 deterministic panel crops and a 1200×24960 current r3 long scroll plus 390×8112 phone edition. Two repair calls add four panel-level candidates: P001 alone and a P031-P033 strip. Current r3 agent triage is 45 PASS / 5 WARN / 0 FAIL, up from r2's 43/7/0. Targeted repairs preserve 49/49 and 47/47 non-target panel hashes, demonstrating exact assembly no-change stability. Stochastic rerun reproducibility remains unmeasured because no identical request was repeated and the built-in product exposes no seed or model snapshot.

The route is selected on 50/50 coverage, role/count/order, 32-panel cast continuity, causal legibility, phone readability, lettering clearance, and hash-exact target/no-change behavior—not on visual appeal alone. Remaining warnings are P029, P032, P036, P039, and P043. The most informative next repair is P036's continuous plank-to-tin leverage path.

P036 r4 then changes exactly one panel and preserves 49/49 non-target hashes. The new 852×1846 source makes one continuous plank, distinct bracing/lifting roles, and tip-to-tin contact readable in the 390×8567 chapter phone scroll. Agent triage improves to 46 PASS / 4 WARN / 0 FAIL; P036 moves to PASS while its raised-beam footing remains an explicit aesthetic/canon-review limitation. The current full chapter is 1200×26360.

R5 changes only P039/P043 and preserves 48/48 immediate non-target hashes, including P040-P042. The current scroll is 1200×27465 and the phone edition is 390×8926. Agent triage improves to 48 PASS / 2 WARN / 0 FAIL. The test also exposes a prompt-versus-plan failure class: exact P043 leaves the open tin, while the prior prompt mistakenly left all contents despite P046 retaining the map. ADR-0173 records the correction without rewriting the original evidence.

R6 selects P029 from a final two-panel strip and keeps its P032 mate diagnostic-only. P029's enter/guard roles pass; P032 remains WARN after two attempts. The selected assembly preserves 49/49 non-target hashes and reaches 49 PASS / 1 WARN / 0 FAIL at 1200×27636 (phone 390×8982). ADR-0174 freezes stochastic CH05 repair because another same-route P032 attempt has lower information value than owner review or deterministic local compositing.

The r6 release gate binds 17 exact source records and eight current review artifacts, verifies ignored/untracked pixel state, and rejects 10/10 adversarial mutations. It separately reports 1,592.908 summed execution observations and approximately 1,200.7 overlap-adjusted wall seconds, preventing the former from being mislabeled as latency. The 63-plan source inventory establishes a measured next-production boundary: CH05 is full-chapter review ready; CH01-CH04 are scene-fragment regression inputs only.

Cross-chapter regression then validates 23/23 selected source hashes and two deterministic derivatives, with 10/10 malformed records rejected. Its main finding is continuity rather than renderer quality: CH02-CH04 hair/color roles conflict with the current CH05 contract. Because renderer eras, review states, and compositions differ, the packet is explicitly ineligible as a fair renderer benchmark or biometric identity test.

The complete-chapter authoring contract compiles byte-identically from five exact evidence sources and rejects 15/15 malformed fixtures. It binds six story phases, 18 panel fields, three cadence classes, nine scale roles, and nine acceptance gates while its blank template remains non-executable. This measures contract integrity only; no new North Garden story or renderer result exists.

The companion semantic graph validator passes 1/1 synthetic positive and rejects 23/23 adversarial variants across 11 domains. It demonstrates fail-closed phase/order/continuity/lettering/progression behavior before prompts exist; it does not measure narrative quality or renderer performance.

Post-CH05 integrated release r1 passes 10/10 commands and 93 effective checks in 4.481 seconds; its own validator rejects 12/12 mutations. The gate includes r6 production/assembly, 63-plan inventory, 23-panel regression, authoring and semantic contracts, frozen/baseline, tracked-source scope, and remote parity. This is a release-integrity measurement, not new visual evidence.

The r6 owner pointer binds ten review artifacts, 13 strongest candidates, two P032 candidates, and three authority-separated decision groups; 12/12 mutations fail. It is navigation evidence only and does not add a visual score or acceptance result.

The complete alternate-graphic preflight covers 50/50 plans in 11 exact 3-5-panel prompts and rejects 12/12 malformed fixtures. It plans 23 authorized reference uses and zero paid/provider-budget activity. No renderer-quality result exists until execution; R6 remains the unchanged comparison baseline.
## CH05 r6 versus alternate-graphic full-chapter comparison — 2026-09-02

Both arms cover the same 50 ordered ComicPanelPlans. The alternate arm adds 11 strips and 50 crops in 954.3 seconds of overlap-adjusted ImageGen tool-call wall. Its non-gating triage is 36 PASS / 7 WARN / 7 FAIL with 50/50 hair-and-wardrobe continuity. R6's preserved panel-local triage remains 49/1/0; the new supplemental cross-panel gate audit is 47/1/2 because P001 preempts the smoke reversal and P041 remains visibly hot/pluming.

At 390-pixel normalization and equal panel weight, r6 versus alternate aggregate measurements are: edge density 0.220004 versus 0.215718, grayscale entropy 6.889241 versus 6.837860 bits, and source PNG bytes/native pixel 1.623124 versus 1.608028. These small changes do not support a material density advantage and do not measure artistic quality. The selected engineering route remains r6 plus explicit cross-panel gates.

## CH05 three-route full-chapter comparison — 2026-09-02

The gated clear-line-watercolor arm covers the same 50 plans with 11 outputs, 50 crops, and 23 reference uses in 1,090.0 seconds of overlap-adjusted tool-call wall. Its non-gating semantic triage is 45 PASS / 2 WARN / 3 FAIL, versus alternate graphic 36/7/7 and r6's supplemental cross-panel audit 47/1/2. Hair and wardrobe pass 50/50 on both new complete arms. Clear-line transfers three important failures to pass—P029 independent entry roles, P036 continuous shared leverage, and P041 fully extinguished drum—but retains P001 departure, P039 mark-count composition, and P043 map-possession failures.

At 390-pixel normalization and equal panel weight, r6 / alternate / clear-line measurements are edge density 0.220004 / 0.215718 / 0.244026, grayscale entropy 6.889241 / 6.837860 / 7.025710 bits, and source PNG bytes/native pixel 1.623124 / 1.608028 / 1.698281. The nominal clear-line style is therefore the densest by all three proxies. It leads style development for contour, character, and causal-action clarity—not for density—and cannot replace the semantically stronger r6 base wholesale.

## CH05 four-route and hybrid benchmark — 2026-09-02

Four complete 50-panel routes compare 200 aligned candidates. Supplemental semantic counts are r6 47/1/2, clear-line 45/2/3, premium cel 40/5/5, and alternate graphic 36/7/7. Premium-cel equal-panel measurements are edge density 0.227841, grayscale entropy 6.934245 bits, and PNG bytes/native pixel 1.656707; it falls between r6 and clear-line on the first two proxies and remains more compressed-byte-dense than r6. The style is a useful panel source but not a clear low-density route.

The targeted semantic repair tranche changes only P001/P032/P039: two PASS and one WARN at exact phone review size. The derived review-only hybrid then reaches 49 PASS / 1 WARN / 0 FAIL without selecting a known-failing candidate. This rollup measures semantic integration, not finish continuity: 33 adjacent route transitions remain visible and prevent production-base promotion.

## CH05 flat and reduced-palette complete-chapter controls — 2026-09-03

Flat graphic-gouache covers all 50 plans in 11 outputs and measures 41 PASS / 6 WARN / 3 FAIL semantically, but only 16/7/27 overall because lettering is 19/6/25 and style compliance is 0/0/50. Reduced-palette text control also covers all 50 plans in 11 outputs, without references or uploads. It measures 43/4/3 semantic, 43/7/0 phone, 17/6/27 lettering, 12/7/31 style, and 6/6/38 overall. On visible-cast panels, reduced-palette identity/hair/wardrobe is 32/32; 18 plans have no visible adult cast.

At 390-pixel normalization and equal panel weight, flat versus reduced aggregate complexity is edge density 0.211280 versus 0.149995, grayscale entropy 6.897733 versus 6.572611 bits, and PNG bytes/native pixel 1.581633 versus 1.397747. Reduced-palette therefore separates on all three density proxies, but the large style and lettering failure counts prevent interpreting lower density as better production fitness.

## CH05 six-route sequence-cadence benchmark — 2026-09-03

The current comparison joins 300 candidates from r6, alternate graphic, clear-line watercolor, premium cel, flat graphic-gouache, and reduced-palette text control. Semantic PASS/WARN/FAIL is respectively 47/1/2, 36/7/7, 45/2/3, 40/5/5, 41/6/3, and 43/4/3. The sequence-constrained optimizer recommends reduced-palette S01, r6 S02-S08, and premium cel S09-S11, assigning 5/34/11 panels with two sequence route transitions. It reduces the prior review-only hybrid's 33 adjacent transitions by 31 while prohibiting within-sequence cherry-picking.

The assembled review cadence measures 47 PASS / 3 WARN / 0 FAIL over 50 panels; P003, P032, and P045 retain warnings. This is a cadence recommendation rather than wholesale renderer selection. It does not prove the block boundaries are production-continuous, and no art is accepted or promoted.

## CH05 S01/S11 reference-ablation benchmark — 2026-09-03

For S01, matched no-reference minus reference-backed flat-gouache changes entropy / edge density / PNG bytes per native pixel by +0.057907 / -0.068096 / -0.188811. For S11 the same deltas are +0.064727 / -0.029169 / -0.045402. Stricter reduced-palette minus matched no-reference is -0.574205 / -0.015176 / -0.106527 at S01 and -0.024050 / -0.011826 / -0.063436 at S11.

Each matched comparison contains only one stochastic pair and one required changed input-instruction line. The stricter control changes style instructions as well as omitting references. These benchmarks cannot isolate a general causal effect of reference conditioning, and the complexity metrics do not score identity, narrative success, art quality, or commercial suitability.

## CH05 sequence-boundary continuity audit — 2026-09-03

The non-gating audit compares two cross-route pairs against four adjacent within-route controls using luminance-histogram and 64-bin RGB mean-channel total-variation distances. P005→P006 measures 1.120982× and 1.168896× the mean of its adjacent controls. Both ratios exceed the local mean, but neither cross-route distance exceeds both individual controls; this supports manual review priority, not a style-only causal claim.

P039→P040 measures 0.902299× and 0.894237× its adjacent means, so neither proxy supports above-local-mean risk at the later boundary. The audit is confounded by narrative content, shot scale, crop, and aspect ratio. It changes no route, acceptance, or rights state. The next benchmark is a zero-upload three-arm P005→P006 control using existing selected reduced→r6, all-reduced, and all-r6 candidates with panel IDs/story beats held fixed.

The completed three-arm control measures selected reduced→r6 at 0.521210 luminance / 0.519582 RGB distance, all-reduced at 0.510071 / 0.472000, and all-r6 at 0.555130 / 0.551442. Selected-to-control-mean ratios are 0.978613 and 1.015362, and the selected transition exceeds both same-route controls on 0/2 proxies. Under the predeclared rule, route-switch contribution is not isolated. This does not erase the manual finish-continuity concern; it limits the engineering conclusion to owner review with no new render/edit recommendation.

## CH05 six-route/cadence integrated-release benchmark — 2026-09-03

The append-only release runs 15 local validators and one read-only remote-parity domain in 31.918454 seconds. All 16 domains pass; 14 upstream self-test suites reject 298/298 mutations and the integrated-record validator rejects 26/26 mutations. This is an integrity/replay benchmark, not a render-quality or production-throughput measurement. It adds zero provider calls, uploads, generation, candidates, acceptance, or paid spend.

## CH05 cadence objective-sensitivity benchmark — 2026-09-03

The exact optimizer audit covers 1,728,000 hard-feasible 11-sequence assignments. Seven/eight leave-one-secondary-objective-out variants reproduce reduced-palette S01, R6 S02-S08, and premium cel S09-S11. Removing adjacent-transition minimization alone changes S10-S11 to R6, producing three transitions and two semantic warnings instead of two transitions and three warnings. All variant optima are unique. The exact eight-field Pareto frontier has three assignments. This measures policy sensitivity over existing categorical evaluations, not visual quality, owner preference, renderer reproducibility, or rights.

## CH05 overnight closeout benchmark — 2026-09-03

The final release passes nine domains in 42.965 seconds. Seven upstream self-test suites reject 135/135 mutations; the closeout record rejects 30/30 mutations. The art/output denominator is 76 service rasters and 312 panel candidates/crops, of which 300 form the aligned six-route comparison. Thirteen outputs used zero references and two remain unsplit sequence-level ablation diagnostics. These are exact manifest reconciliations, not quality, acceptance, cost, or end-to-end throughput measurements.

## CH05 terminal handoff benchmark — 2026-09-03

The terminal matrix passes 8/8 domains in 78.819 seconds, with 124/124 upstream and 32/32 record mutations rejected. The final start page binds ten ignored local visuals and seven supporting documents; inventory r3 binds 316 changed tracked files across 28 commits with zero prohibited/generated paths. This is an integrity/navigation benchmark, not art quality, acceptance, rights, or render throughput.

## CH06–CH13 story-breadth baseline — 2026-09-03

The new baseline is eight required chronological chapters, 40 target panels and eight sequences per chapter, totaling 320 target panels. Every chapter must inherit the exact prior closing-state key, change at least five declared state categories, contain at least two causal setpieces, and end in a distinct state. The initial arc record satisfies all eight chapter carries and rejects 23/23 adversarial mutations.

The anti-duplication baseline is one default candidate per panel, zero alternate-style coverage before a complete chronological chapter exists, at most 10% named-question alternative coverage afterward, and at most two targeted repairs per failed panel. These are production-efficiency and narrative-breadth controls, not art-quality measurements.

## CH06–CH07 complete-authoring benchmark — 2026-09-03

The first batch contains 2 complete chapters, 80 unique panel plans, 16 contiguous sequences, and 12 chapter-phase declarations. Exact CH06 final to CH07 initial continuity carry passes. The dedicated validator rejects 25/25 changes spanning cross-medium leakage, execution/prompt/model leakage, panel count/order/identity, adult-only cast, protected lettering, continuity, chapter-state linkage, sequence structure, anti-duplication caps, and substantive unique beats.

This is an authoring-completeness benchmark, not a render, art-quality, acceptance, rights, or throughput result.

## CH06–CH07 default-route preflight — 2026-09-03

| Measure | Result |
|---|---:|
| Complete chapters covered | 2 |
| ComicPanelPlans covered | 80 / 80 |
| Five-panel sequence requests | 16 |
| Duplicate panel coverage | 0 |
| Whole-chapter alternate arms | 0 |
| Authorized reference uses | 38 |
| Validator result | PASS |
| Adversarial fixtures rejected | 24 / 24 |
| Provider calls / outputs | 0 / 0 |
| Paid API/cloud spend | $0 |

This measures execution readiness, not visual quality, acceptance, reproducibility, rights, commercial clearance, or exact-production-base fitness.

## CH06 complete default-route benchmark — 2026-09-03

| Measure | Result |
|---|---:|
| Complete chronological chapters produced after CH05 | 1 |
| Sequence sources / panel candidates | 8 / 40 |
| ComicPanelPlan coverage | 40 / 40 |
| Agent triage PASS / WARN / FAIL | 38 / 1 / 1 |
| Required review artifacts | 5 / 5 |
| Authorized reference uses | 17 |
| Alternate whole-chapter arms / targeted repairs | 0 / 0 |
| Adversarial validator mutations rejected | 16 / 16 |
| Paid API/cloud spend | $0 |

P020 is a role-separation warning and P030 is an unrequested-text failure. Built-in monetary cost and per-request elapsed time are unavailable. This benchmark does not establish human acceptance, rights, commercial clearance, reproducibility, or exact-base fitness.

## CH08–CH09 complete-authoring benchmark — 2026-09-03

The second batch adds 2 complete chapters, 80 unique panels, 16 contiguous sequences, all six phases per chapter, and exact CH07→CH08→CH09 continuity. Post-CH05 breadth is now 4 complete authored chapters/160 panels, of which CH06 has a complete generated default route. The dedicated validator rejects 35/35 mutations spanning state carry, adult/cross-medium boundaries, identity/hair drift, physical Ledger binding, panel/sequence coverage, progression, and execution leakage.

This is an authoring and continuity result, not prompt promotion, visual acceptance, rights clearance, or production execution.

## CH07 complete default-route benchmark — 2026-09-03

| Measure | Result |
|---|---:|
| Complete chronological chapter | 1 × 40 panels |
| Sequence sources / panel candidates | 8 / 40 |
| Agent triage PASS / WARN / FAIL | 37 / 1 / 2 |
| Review artifacts | 5 / 5 |
| Authorized reference uses | 21 |
| Client-observed request-interval sum | 2,370.565 s |
| Parallel group wall intervals | 497.196 s / 460.672 s |
| Alternate arms / targeted repairs | 0 / 0 |
| Adversarial mutations rejected | 17 / 17 |
| Paid API/cloud spend | $0 |

The request-interval sum overlaps and is not total wall time. P009, P030, and P040 preserve exact continuity/text/prop findings. Human acceptance, rights, commercial clearance, reproducibility, and exact-base fitness remain open.

## CH08–CH09 default-route preflight benchmark — 2026-09-03

Sixteen requests cover 80 unique plans with 40 authorized reference uses, zero duplicate coverage, zero whole-chapter alternate arms, and zero provider calls at preflight. All requests bind one-row/no-number layout, no generated prose, fixed hair and garment ancestry, Warden's Reach anti-gun geometry, physical Ledger emblems, and adult-only data boundaries. The validator rejects 27/27 mutations.

This is execution readiness, not rendered quality, acceptance, rights, clearance, reproducibility, or exact-base selection.

## CH11 complete default-route benchmark — 2026-09-03

| Measure | Result |
|---|---:|
| Complete chronological chapter | 1 × 40 panels |
| Sequence sources / panel candidates | 8 / 40 |
| Agent triage PASS / WARN / FAIL | 35 / 1 / 4 |
| Review artifacts | 5 / 5 |
| Authorized reference uses | 21 |
| Overlapping request-interval sum | 2,214.860 s |
| Parallel group walls | 442.406 s / 429.358 s |
| Alternate arms / repairs | 0 / 0 |
| Adversarial mutations rejected | 19 / 19 |
| Paid API/cloud spend | $0 |

The chapter completes the Orchard Siege and exposes a repeated unreferenced-secondary-character continuity weakness: four Halvor actions drift to a Soren-like blond adult. This is provisional agent triage, not human acceptance or rights clearance.

## CH10 complete default-route benchmark — 2026-09-03

| Measure | Result |
|---|---:|
| Complete chronological chapter | 1 × 40 panels |
| Sequence sources / panel candidates | 8 / 40 |
| Agent triage PASS / WARN / FAIL | 37 / 0 / 3 |
| Review artifacts | 5 / 5 |
| Authorized reference uses | 23 |
| Overlapping request-interval sum | 2,045.824 s |
| Parallel group walls | 403.285 s / 414.710 s |
| Alternate arms / repairs | 0 / 0 |
| Adversarial mutations rejected | 17 / 17 |
| Paid API/cloud spend | $0 |

The chapter materially advances setting, faction, equipment, injury, mission ethics, and threat state. Three exact localized failures remain; this is diagnostic agent triage, not acceptance.

## CH10–CH11 complete-authoring benchmark — 2026-09-03

The third batch adds 2 complete chapters, 80 unique panels, 16 five-panel sequences, all six phases per chapter, and exact CH09→CH10→CH11 continuity. Post-CH05 authored breadth is now 6 complete chapters/240 panels. Persistent injury constraints, earned equipment/classes, adult faction roles, siege causality, physical Ledger binding, and protected lettering are explicit. The validator rejects 41/41 adversarial mutations.

This is authoring evidence only; it does not grant prompt, render, acceptance, rights, or commercial authority.

## CH08 complete default-route benchmark — 2026-09-03

| Measure | Result |
|---|---:|
| Complete chronological chapter | 1 × 40 panels |
| Sequence sources / panel candidates | 8 / 40 |
| Agent triage PASS / WARN / FAIL | 39 / 1 / 0 |
| Review artifacts | 5 / 5 |
| Authorized reference uses | 20 |
| Overlapping request-interval sum | 2,158.140 s |
| Parallel group walls | 430.624 s / 437.107 s |
| Alternate arms / repairs | 0 / 0 |
| Adversarial mutations rejected | 16 / 16 |
| Paid API/cloud spend | $0 |

Relative to CH07, exact blocking generated-prose, panel-number, and gun-like-prop failure classes fell from present to absent. This is provisional agent triage, not human acceptance or rights clearance.

## CH12–CH13 complete-authoring benchmark — 2026-09-03

The fourth authoring batch adds 2 complete chapters, 80 unique panels, 16 five-panel sequences, all six phases per chapter, and exact CH11→CH12→CH13 continuity. Post-CH05 authored breadth is now 8 complete chapters/320 panels. Strategic rupture/reconciliation, consent rules, irreversible costume damage, equipment fusion, living-monster resolution, earned classes, an operational base, and the wider network hook are explicit. Semantic checks pass and 58/58 adversarial mutations are rejected.

This is authoring evidence only; prompts, pixels, provider calls, uploads, acceptance, rights, and commercial clearance remain absent or pending.

## CH09 complete default-route benchmark — 2026-09-03

| Measure | Result |
|---|---:|
| Complete chronological chapter | 1 × 40 panels |
| Sequence sources / panel candidates | 8 / 40 |
| Agent triage PASS / WARN / FAIL | 39 / 1 / 0 |
| Review artifacts | 5 / 5 |
| Authorized reference uses | 20 |
| Overlapping request-interval sum | 2,177.960 s |
| Parallel group walls | 437.501 s / 417.841 s |
| Alternate arms / repairs | 0 / 0 |
| Adversarial mutations rejected | 16 / 16 |
| Paid API/cloud spend | $0 |

The route preserves injury and leadership progression across all eight sequences and introduces no blocking generated prose, panel number, hair-color, or gun-like-prop failure. P037 remains one forensic-clarity warning. This is agent triage, not human acceptance or rights clearance.

## CH06–CH09 progression-review benchmark — 2026-09-03

| Measure | Result |
|---|---:|
| Complete visual chapters | 4 |
| Ordered panel candidates | 160 |
| Chronological source sequences | 32 |
| Combined PASS / WARN / FAIL | 153 / 4 / 3 |
| Cross-chapter review artifacts | 3 |
| Fixed-ordinal sampler panels | 36 |
| Whole-chapter alternate arms | 0 |
| Validator mutations rejected | 10 / 10 |
| New calls / uploads / paid spend | 0 / 0 / $0 |

The hub measures breadth and makes progression reviewable; it does not normalize per-chapter failures or infer candidate acceptance.

## CH10–CH11 default-route preflight benchmark — 2026-09-03

Sixteen requests cover 80 unique plans with 44 authorized reference uses, zero duplicate panel coverage, one candidate per plan, zero whole-chapter alternate arms, and zero provider calls at preflight. All requests bind one-row/no-number layout, local class/status/bond lettering, persistent brace and injury, forged anti-firearm polehook, owned bow/seax, garment ancestry, fictional-adult faction roles, grounded Mireback anatomy, and the exact reference boundary. The validator rejects 27/27 mutations.

This is execution readiness, not rendered quality, acceptance, rights, clearance, reproducibility, or exact-base selection.
