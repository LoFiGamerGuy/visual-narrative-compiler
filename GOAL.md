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

The active bounded milestone is a 50-panel chapter run-manifest compiler. Construct every initial hash-chained ledger from the approved `ComicPanelPlan` collection, bind applicable assertions and stage denominators, pin a deterministic chapter root, and measure local compile/validation behavior. The manifest must report all 50 panels base-pending, zero executable/accepted, and no provider/cost activity while retaining the six-panel demonstration subset.

### Authority and data boundaries

The user has directed research across local, frontier, API, and managed-GPU paths. The program may prepare adapters and run fully local work autonomously. Before material paid expenditure, model download where there are multiple plausible choices, or an external upload of adult likeness/reference material, collect current primary terms and provide the smallest decision memo needed. Initial external bakeoffs contain only original fictional adult character designs and non-sensitive control assets.

Future adult prompts must use unambiguous adult role language. Legacy child-coded tags (`boy`, `girl`, `kid`, `child`, and aliases) are prohibited outside a separately reviewed fictional-child geometry-only protocol; see ADR-0017.
