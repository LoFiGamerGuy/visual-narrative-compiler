# North Garden production and research goal

Build a durable, model-agnostic production system for serialized 50-90 panel webcomic chapters, with a future animation research branch. The immediate product is not a new image workflow: it is a measured loop that can keep shipping narrative material while reducing accepted-panel failure rate and human minutes.

## Success measures

- recurring characters, role bindings, wardrobe, props, timeline state, and sets remain correct at chapter scale;
- every accepted panel and repair is addressable, reproducible, and revisioned;
- panels use declared assertions and explicit spatial mode (`grounded`, `cheated`, or `2d_only`);
- renderer, model, ComfyUI graph, cloud vendor, and identity mechanism are replaceable execution details;
- experiments report accepted-panel rate, failure tags, candidates, time/cost, and human minutes;
- each research cycle also yields at least one accepted, instrumented narrative page or meaningful sequence.

## Working boundaries

Shared canonical state flows through `Canon / Story State -> Asset Registry -> SceneBeat / NarrativeIntent`. Comic execution uses `ComicPanelPlan`; future animation uses `AnimationShotPlan / E-Conte`. `RenderRecord` is provenance for an execution attempt, never the directing record.

No child likeness data, child identity training, digital double, voice clone, or child image upload may enter the system. Adult likeness material is sensitive and local by default. Commercial eligibility of a weight, service, or output route is an explicit, dated registry decision, not an inferred property of an architecture family.

## Rolling autonomous program

The program continues across bounded milestones until it has produced multiple instrumented chapter-scale webcomic drafts and a measured production-path recommendation. A milestone may finish only when its evidence, records, validation, costs, limitations, and next decision are written down. Completion of a milestone immediately creates the next evidence-supported milestone; status reporting is not a stopping condition.

### Operating sequence

1. Run the provider-neutral, fictional-only G07 bakeoff before selecting a production-oriented execution arm. The initial candidates are Gemini 3.1 Flash Image, Grok Imagine Image 2.0, OpenAI GPT Image 2, BFL FLUX.2 where terms support it, and a managed-GPU Qwen Image Edit 2511 profile. Use the exact control/review protocol in `docs/research/frontier-renderer-paths-20260901.md`.
2. Compare all evidence against the immutable `baseline_legacy` failure profile. Select or reject mechanisms through ADRs; never tune `baseline_legacy` to improve its score.
3. Harden only the selected execution paths: explicit adapter contracts, case assets, assertion manifests, render/cost provenance, targeted repair, and reproducibility checks.
4. Use the best permitted path to produce an instrumented chapter draft, review and correct it through immutable panel-addressable revisions, then repeat for further chapter drafts. CH03 and CH04 are two three-panel frontier-art research drafts that exercise this chain. Their immutable edition, lint, review, and readiness records explicitly report that they remain below the 50-panel lower bound, pending human review, unaccepted, unreproducible, and not commercially cleared. The clean 50-panel CH05 Mill Signal development script has now been explicitly approved for canon/story/asset/scene-beat and `ComicPanelPlan` development through `production/decisions/ng-decision-ch05-mill-signal-promotion-r1.json`; its original four visual-smoke candidates remain unaccepted, provenance-limited research. CH05 plans carry a separate comic style/density/motion/lettering direction record and must never be represented as `AnimationShotPlan / E-Conte` records.

### Current milestone and exit condition

The initial fictional G07 bakeoff is complete: 16/16 required candidates plus one paid xAI transport failure, $1.057377 aggregate committed cost, $0 held, exact hashes/requests/timings, four pending-human review packets, non-gating instrumentation, and ADR-0025's measured selection of OpenAI GPT Image 2 for bounded hardening. The first local hardening experiment also completes: no-change is byte-identical at zero new cost and target-mask compositing has exactly 0% exterior change, but its rectangular seam is not acceptable art.

The chapter-scale input-instrumentation milestone is complete without a new external upload. All 50 CH05 `ComicPanelPlan` records compile; the P033–P038 packet has 0 executable panels, 36 structured but untimed review tasks, and three source-derived continuity chains. P036's unaccepted smoke art is blocked by a 64.7059% causal-region/lettering-zone conflict; a separate abstract control proves 0% overlap but is not art or provider input. Local base approval, mask approval, and exact external authority are independent fail-closed gates under ADR-0026.

The deterministic sequence portion of the current milestone is complete: 6/6 output pairs are hash-stable across consecutive builds, all planned role counts match, story occupancy has zero lettering-safe-zone pixels, and three continuity-token chains validate. ADR-0027 limits these results to compiler evidence, not visual continuity or art acceptance.

The adversarial run-state milestone is complete. Six hash-chained P033–P038 ledgers remain at `BASE_APPROVAL_PENDING`; a full synthetic lifecycle validates, while 18/18 illegal transitions, hash tampers, and aggregate-reservation binding mutations fail. ADR-0028 requires exact reservation/adapter/request/cost reconciliation before a RenderRecord can advance to timed assertion review and acceptance.

The budget-domain and local-intake milestone is complete. ADR-0029 separates the disabled CH05 production policy/ledger/environment from G07; bakeoff capacity alone, a production environment value alone, and a substituted bakeoff ledger all fail. Synthetic production reserve/hold/reconcile/release accounting passes without real authority or spend. Six deterministic controls hash-match local candidate intake while remaining unclassified, unapproved, and rejected by the base gate under ADR-0030.

The immutable candidate-review/promotion milestone is complete. All 6/6 deterministic controls are policy-ineligible even when supplied superficially complete review fields. A synthetic eligible fixture exercises review mechanics but is forced into a non-approval state; 8/8 missing or prohibited review mutations fail. Approved bases/uploads remain 0/0 and human minutes remain null.

The 50-panel run-manifest milestone is complete. The pinned chapter root reproduces 30/30 local compiles; median compile time is 9.120 ms, p95 10.178 ms, peak traced allocation 1,802,668 bytes, and 4/4 plan/assertion/chain/order mutations are detected. All 50 panels remain base-pending, the six-panel slice remains a subset, 250 review task instances carry null minutes, and executable/accepted/provider/cost counts remain zero.

The immutable review/progress milestone is complete. A paused synthetic session computes exactly 15 active minutes and rejects 10/10 timer/decision/chain mutations. Terminal run ledgers now bind exact session digests and reject 22/22 combined lifecycle/budget/review mutations. The real chapter rollup remains 0/50 accepted with null minutes/$0; an isolated synthetic retry scenario reports 2/50 accepted, 3 attempts across 2 panels, 1 retry, 15 fixture-only minutes, and $0.45 fixture cost without leaking into real evidence.

The selected-route offline-preflight milestone is complete. P036 stops independently on missing approved base, mask, exact authority, and distinct production reservation; it has no client/network import, API-key access, request body, or executor. A synthetic complete prerequisite set produces metadata only and 6/6 mutations block it. The consolidated offline suite passes 21/21 checks in 2.652 seconds with exact safe-source/public-control validation and no provider/upload/cost activity.

The crash-safe journaling milestone is complete. A proven pre-submit abort releases and permits an explicitly superseding retry; a post-boundary unknown outcome retains the aggregate hold and blocks retry. Synthetic recovery binds the original provider ID, output/timing, exact cost, and RenderRecord before completion. Duplicate keys plus 11/11 transition, chain, reservation-state, request-ID, and cost mutations fail. No executor or authority was added.

The production evidence-schema milestone is complete. Synthetic success and explicit-failure RenderRecords preserve journal/input/output/request/timing/usage/cost/review fields; unknown outcome is a held-reservation incident with no candidate or RenderRecord. Twelve/twelve missing or contradictory evidence mutations fail. Real CH05 RenderRecords/candidates/acceptance remain zero.

The G07 local evidence-vault milestone is complete. The tracked non-art manifest pins 19/19 provider records and 16/16 candidate artifacts under vault root `e84b0402…6d3ab`; all bytes and candidate decodes validate, five/five manifest mutations fail, BFL inputs remain exactly the two approved controls, and Git tracks zero generated experiment paths. Cost reconciliation remains $0.987377 for required candidates plus the $0.07 xAI failure, $1.057377 aggregate paid, $0 held. Human minutes remain null and all candidates remain unaccepted under ADR-0036.

The G07 evidence-restoration milestone is complete. A deterministic ignored local archive contains exactly 38 entries: the manifest, two public controls, 19 provider records, and 16 candidates. All members verify directly without extraction; repeated construction is byte-identical; five/five missing, extra, corrupt, path-escaping, and duplicate mutations fail. The 19,879,277-byte archive hashes to `64bea215…69cad7`. ADR-0037 records that this same-disk rehearsal is not off-device backup and grants no rerender authority.

The blinded G07 human-review instrumentation milestone is complete. Sixteen neutral PNG presentations preserve exact decoded RGB content and four provider-hidden repeat pairs cover the independent samples. Packet root `4b1e5f0c…478161` requires 20 append-only timed decisions across role binding/order/count, shared set/blocking, target/no-change behavior, side effects, and repeat limitations. Thirteen/thirteen identity-leak, ordering, coverage, timing, hash, and assertion mutations fail. Actual decisions remain 0/20, human minutes null, accepted subjects zero under ADR-0038.

The fail-closed G07 review-rollup milestone is complete. Four/four arms and 16/16 candidates bind to exact cost, latency, and three drift dimensions. Only a complete eligible exact-packet session with the vault-derived mapping root can add assertion/tag results. Nine/nine pending, fixture, coverage, and mapping mutations fail. Pending state remains 0/20 decisions, null human minutes, zero accepted, and null human arm results; no composite score, rank, or automatic route change exists under ADR-0039.

The selected-route mask-boundary milestone is complete. Seven exact-hash local variants compare hard and 2/4/8/16/24/32-pixel inward cosine boundaries. Only 16 pixels meets the predeclared rule: 91.263% artificial-jump reduction, unchanged 99.462% central green signal, zero exterior changed pixels, and zero P036 lettering overlap. Eight/eight evidence mutations fail. ADR-0040 selects only this compositor policy for the next mechanics test; provider route and art acceptance are unchanged, with 0 calls/uploads/$0.

The P036 mask-topology compatibility milestone is complete. The current mask is exactly one filled axis-aligned rectangle, not irregular causal geometry. The 16-pixel policy retains 79.032% fully replaced core, preserves 1/1 component, and changes zero exterior/lettering pixels, but exercises no concavity, holes, multiple components, or thin features. Eight/eight overclaim/tamper mutations fail; ADR-0041 marks irregular narrative topology not tested.

The P036 causal-shape topology milestone is complete. Five context paddings were measured with the fixed 16-pixel boundary. Eight pixels is the narrowest predeclared-rule pass: 42.107% connected union core; plank/reach/hand/tin retain 45.468%/44.470%/48.692%/38.384% core; rectangularity 0.215863 exercises concavity and the 42-pixel reach exercises a thin feature; exterior and lettering change remain zero. Ten/ten mutations fail. ADR-0042 keeps the outputs abstract, unapproved, and unauthorized for provider input.

The selected-route repair-policy non-promotion milestone is complete. The versioned policy binds P036/`p036_core_read`, OpenAI snapshot/endpoint, 16-pixel boundary, 8-pixel context, exact exterior, and byte-identical no-change. All three abstract controls are explicitly ineligible as production bases/masks/uploads. Real preflight retains four blockers with no envelope/body/client/executor; non-fixture proxy promotion fails; 11/11 mutations fail under ADR-0043.

The immutable P036 repair-readiness r2 milestone is complete. R2 pins r1's unchanged hash, P036 ComicPanelPlan, selected route, local policy, boundary/causal evidence, disabled production policy/zero ledger, and exact offline preflight. It retains four blockers, zero eligible proxy inputs, null base/mask/authority/reservation/request/journal/RenderRecord/candidate/review, and explicit null AnimationShotPlan/E-Conte. Eleven/eleven mutations fail under ADR-0044. The production ledger now records five additional zero-cost milestones while remaining no-cap/$0 committed/$0 held.

The chapter-scale repair-policy coverage milestone is complete. All 50 plans remain in order. P019/P026/P036/P044 are the four explicit causal practical-action candidates; only exact P036 has a mechanics policy, three are policy-absent, and 46 have no explicit plan-level repair applicability. No mask is inferred and no P036 policy leaks. Ten/ten mutations fail; approved bases/masks/executable panels/requests/uploads/acceptances remain zero, minutes null, cost $0 under ADR-0045.

The next-policy information-gain milestone is complete. P019/P026/P044 were compared only against uncovered mechanics. P044 uniquely supplies explicit bounded blade/twine contact below twice the 16-pixel feather without requiring P026's new diffuse-effect mechanism. Eight/eight mutations fail. ADR-0046 selects one P044 deterministic abstract control only; no policy, production mask, provider route, or external action changes.

The P044 fixed-boundary stress milestone is complete. The exact 18-pixel blade/12-pixel twine support is one connected component, clipped from protected hands, and clear of lettering. Applying 16 pixels unchanged leaves zero fully replaced core pixels for both features, while protected/lettering/exterior change remains zero. Nine/nine mutations fail. ADR-0047 rejects the fixed width for this control without rejecting P044, the provider route, or the inward-compositor mechanism.

The P044 adaptive-width milestone is complete. On unchanged hash-pinned geometry, widths 1/2/3/4/5/6/8/10/12/16 were compared. Five pixels is the widest pass: 18.496% union, 22.945% blade, and 18.170% twine fully replaced core with one core component; six is the first larger failure. Protected/lettering/exterior change remains zero and 9/9 mutations fail. ADR-0048 keeps this a local control, not a universal formula or P044 policy.

The scale-aware boundary-selector milestone is complete. P036=16px and P044=5px remain distinct local profiles; both pass topology controls while both lack exact approved-panel-base visual-boundary evidence and timed seam review. The contract has no universal width and zero production-ready profiles/masks/requests/uploads. Ten/ten gate, width-leak, visual-overclaim, production, and generalization mutations fail under ADR-0049.

The repair RenderRecord boundary-evidence milestone is complete. Append-only v2.1 completed records bind the exact selector/profile/width, support/alpha, topology, exact-base visual, exterior/no-change, and timed seam-review chain. Explicit failures retain only known input/topology bindings; v1.1 unknown incidents reject every boundary-outcome field. Fifteen/fifteen mutations fail and the consolidated offline suite passes 37/37 in 24.757 seconds under ADR-0050. All real CH05 outcomes remain absent.

The full-denominator CH05 repair-evidence readiness milestone is complete. All 50 ComicPanelPlans remain visible: four explicit repair candidates, two selector/topology profiles, and one panel policy. Exact approved bases/masks/authority/reservations/visual-boundary results/seam reviews/v2.1 RenderRecords/candidates/acceptances are all zero, minutes null, and cost $0. Thirteen/thirteen inference/fabrication mutations fail under ADR-0052. ADR-0051 also restores the pinned r1 cost-ledger bytes and advances later zero-cost evidence through append-only r2; the suite passes 39/39.

The exact-base boundary-measurement milestone is complete. A synthetic exact-byte packet binds base/candidate/support/alpha/profile/topology and measures 64,992 support, 35,150 transition, 27,366 full-core pixels, exact exterior, 98.838% fixture-specific boundary-distance reduction, and byte-identical no-change. Its review presentation is hash-bound but session/minutes/decision remain null/false; 14/14 mutations fail under ADR-0053. The suite passes 40/40.

The hash-chained seam-review milestone is complete. V2.1 completed validation now loads the tracked measurement packet and exact session, verifies hashes/event chain/subject/reviewer, derives three fixture minutes, checks all four seam assertions, and rejects fixture eligibility as real evidence. RenderRecord mutation rejection increases to 18/18 under ADR-0054; real CH05 sessions/minutes/outcomes remain zero/null/zero. The suite remains 40/40.

The fail-closed repair-outcome finalizer milestone is complete. Real P036 reports nine blockers and emits no RenderRecord/candidate/review/request/cost. Two synthetic finalizations have identical record/journal/ledger digests, and changing the fixture flag cannot promote them; 10/10 mutations fail under ADR-0055. Append-only production cost ledger r3 records 21 zero-cost milestones with no cap/reservations/spend, and the suite passes 42/42.

The bootstrap/runtime reproducibility milestone is complete. A separate no-download/no-network/no-credential instrumentation profile pins CPython 3.14.6, Pillow 12.3.0, numpy 2.5.1, exact interpreter/bootstrap/manifest/suite hashes, and dry-run behavior while leaving `baseline_legacy` unchanged. Ten/ten runtime mutations fail and a no-write bootstrap passes 43/43 checks in 26.524 seconds under ADR-0056.

The selected-route artifact rebuild milestone is complete. Twenty-six ignored artifacts across eight exact groups and 4,862,061 bytes rebuild twice to identical root `0a04832b…d3f3b18`; 8/8 inventory/root/exclusion mutations fail under ADR-0057. Nondeterministic timing/provider/human/external-runtime classes are excluded explicitly. The complete suite passes 44/44 in 47.620 seconds.

The active bounded milestone is G07 review-validation runtime optimization. Profile the 10.615-second fail-closed rollup check and remove repeated immutable packet/vault recomputation while preserving exact pending state, synthetic isolation, and 9/9 mutation rejection. This is local validator engineering only.

### Authority and data boundaries

The user has directed research across local, frontier, API, and managed-GPU paths. The program may prepare adapters and run fully local work autonomously. Before material paid expenditure, model download where there are multiple plausible choices, or an external upload of adult likeness/reference material, collect current primary terms and provide the smallest decision memo needed. Initial external bakeoffs contain only original fictional adult character designs and non-sensitive control assets.

Future adult prompts must use unambiguous adult role language. Legacy child-coded tags (`boy`, `girl`, `kid`, `child`, and aliases) are prohibited outside a separately reviewed fictional-child geometry-only protocol; see ADR-0017.
