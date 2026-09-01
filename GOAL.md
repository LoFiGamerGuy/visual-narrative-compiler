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

Execute the initial fictional G07 renderer bakeoff under the shared ADR-0023 aggregate reservation ledger. The aggregate-control and current-primary-documentation milestones are complete: all 16 requests reserve at most $4.20 against the approved $100 cap. Eight required candidates are complete (OpenAI 4/4, Gemini 4/4); one additional xAI request is a paid candidate-download failure. The ledger has $0.537377 committed, $0 held, and no accepted candidate before review. For each authorized arm, preserve two independent two-role renders, one target-change edit, and one paired no-change control, with immutable inputs/outputs and full request/cost/timing/review evidence. Exit only after the cross-arm comparison, ADR, registry updates, and next ranked experiment are complete. In parallel, advance the provenance-limited frontier-art narrative branch only through explicit review/revision records; it cannot substitute for the controlled bakeoff or commercial production path.

### Authority and data boundaries

The user has directed research across local, frontier, API, and managed-GPU paths. The program may prepare adapters and run fully local work autonomously. Before material paid expenditure, model download where there are multiple plausible choices, or an external upload of adult likeness/reference material, collect current primary terms and provide the smallest decision memo needed. Initial external bakeoffs contain only original fictional adult character designs and non-sensitive control assets.

Future adult prompts must use unambiguous adult role language. Legacy child-coded tags (`boy`, `girl`, `kid`, `child`, and aliases) are prohibited outside a separately reviewed fictional-child geometry-only protocol; see ADR-0017.
