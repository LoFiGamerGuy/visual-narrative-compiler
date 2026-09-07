# Technical pipeline audit

The current architecture can preserve files and editable lettering. It does not yet reliably preserve **what each panel is supposed to show**. The highest-value repair is to restore the contract between storyboard beat, selected source art and continuous reader before changing generation providers or extending the code framework.

This report analyzes code, exact manifests, selected-source hashes and actual generated HTML without executing protected builds. It distinguishes observed mechanisms from causal hypotheses. Visual conclusions are independently checked in the visual and story audits. [Technical evidence](evidence/technical-measurements.json) contains code excerpts/hashes, all 52 raw-prompt-to-selected-art mappings, static test inventory and measurements.

## 1. Source selection changes the story even when every hash is unique

**Observed:** the 52-panel chapter contains **24 reused premium benchmark sources and 28 newly generated chapter sources**. All 52 current selected rasters exist, match their recorded result hashes and are distinct. Yet benchmark-to-story mapping assigns source art to incompatible beats. This is an editorial selection fault before it is a model-compliance fault.

| CH01 panel | Chapter requirement | Actual benchmark source request | Consequence corroborated by lead phone inspection |
|---|---|---|---|
| P012 | Two leads, boss and intact-anchor combat geography | `bm06`: explicitly asks for Elian, Mira, **Orin and Sable**, four adults on a tense platform | Extra cast appears in a scene requiring only the leads. |
| P017 | Belljaw jaw strikes Mira's shield at one contact point | `bm12`: wide charge/geography, Mira anchoring and Elian waiting | Anticipation/positioning stands in for contact; THOOM cannot supply missing impact. |
| P029 | Injured Elian hangs above the void | `bm01`: tight mature close-up hearing the Bell Regent | Upright close-up substitutes for hanging injury silhouette. |
| P033 | Mid-threat talisman sacrifice and permission conflict | `bm03`: seated Elian and kneeling Mira in a quiet emotional exchange | Emotional content is partly relevant, but setting/body-state continuity loses pressure. This is less binary than P012/P037 and needs contextual visual judgment. |
| P037 | Breath Seed II breakthrough before decisive attack | `bm24`: **Belljaw collapses** beside intact anchor; reconciliation UI space | The source visually spends victory before the decisive chain. |

All leaf paths are under the protected editorial worktree's `experiments/reimaginings/ember-lattice/premium-rd/benchmark/targeted-edit/`. Exact source prompts, hashes and chapter beats are preserved in the [mapping evidence](evidence/technical-measurements.json). The mapping is authored in [integrate.py](/mnt/c/AgentWorkspaces/anime-pipeline-ember-lattice-editorial-gear-20260904/src/reimaginings/ember_lattice/premium_rd/integrate.py:193).

**Inference:** constraints that favored completing all 52 unique art bindings made available attractive assets easier to reuse than reshoot. No labor-time study establishes the motivation. What is established is the wrong-beat mapping. The cheapest correction is a storyboard-to-source adjudication pass, replacing incompatible plates while retaining usable ones. A different model would still fail if the selector makes this substitution.

## 2. The premium bakeoff does not isolate architecture

**Measured:** baseline has 52 panel positions but only **24 distinct baseline hashes**; raw and hybrid each have 52 unique asset hashes. Baseline sources are mapped by `ceil(panel_order * 24 / 52)`. They were not generated anew against the revised 52 story beats. The 24-case benchmark likewise contrasts historical baseline plates with freshly authored scenarios.

**Observed:** `criteria_scores()` returns fixed vectors by workflow, with a few ordinal penalties. Editorial updates assign every hybrid row `lettering_safe_composition=4.95` and `sustained_sequential_quality=4.7`. The resulting 52 hybrid panels have one unique score vector, and identical mean, median and weakest score **89.095**. The model validator requires the selected nonbaseline workflow to win and exceed baseline median/weakest scores. Code constructs that outcome; it is not an independent estimate of reader preference. [Score constructor](/mnt/c/AgentWorkspaces/anime-pipeline-ember-lattice-editorial-gear-20260904/src/reimaginings/ember_lattice/premium_rd/integrate.py:117), [editorial assignment](/mnt/c/AgentWorkspaces/anime-pipeline-ember-lattice-editorial-gear-20260904/src/reimaginings/ember_lattice/premium_rd/editorial.py:403).

The route may in fact be better. The current score records cannot establish how much, why, or whether modular replacement would beat it. Freeze matched beats, source eligibility and review criteria before the next route comparison, then score blinded actual pages independently. Preserve existing scores as historical intent; exclude them from quality-selection arithmetic.

## 3. Negative space and protection are partly generated from the answer

**Observed:** editorial code first authors balloon boxes, appends those boxes as negative-space reservations when earlier zones do not contain them, then places generic face/hand/gear exclusion boxes within the broad focal rectangle. `_protected_zones()` selects a candidate box that avoids the reservations. It receives **no image, detected feature or independently annotated face location**. [Implementation](/mnt/c/AgentWorkspaces/anime-pipeline-ember-lattice-editorial-gear-20260904/src/reimaginings/ember_lattice/premium_rd/editorial.py:71).

A clean collision report therefore proves that selected mathematical rectangles do not overlap, not that visible eyes or weapon contacts are unobstructed. Later prompt text says to reserve these exact zones, but the existing raster was already generated. That record is a useful prospective reshoot instruction; it is not evidence the current art obeyed the instruction.

Required correction: annotate actual visible protected features independently, freeze those annotations before balloon placement and verify tails/contact/acting at rendered phone size. The visual specialist should be allowed to reject or reshape a composition despite passing rectangle arithmetic. Keep collision geometry once its inputs mean what their labels say.

## 4. The executed hybrid has fewer layers than the description suggests

The historic architecture describes controlled grade, safe-area shaping and separate layers. In actual reader HTML, `_leaf_art_path()` follows the SVG's image reference to the underlying raster. The reader then displays that raster and a separate lettering SVG. The wrapper's grade filter and negative-space rectangles are **bypassed** on these reader/comparison paths. This is confirmed in [render.py](/mnt/c/AgentWorkspaces/anime-pipeline-ember-lattice-editorial-gear-20260904/src/reimaginings/ember_lattice/premium_rd/render.py:46) and the first art `img` tags in [phone.html](/mnt/c/AgentWorkspaces/anime-pipeline-ember-lattice-editorial-gear-20260904/docs/reimaginings/ember-lattice/premium-rd/readers/phone.html).

The implemented route is therefore: selected full-frame generated plate → selected targeted edit or deterministic filtered plate → separate SVG lettering/UI → HTML reader. Character, prop and background shapes are not independently editable production layers. The SVG metadata's “layered source” claim must be interpreted narrowly. This architecture permits modular replacement; it does not prevent clean line/cel layers or conventional art correction. Those capabilities are simply not demonstrated by the current full-frame source route.

## 5. Clean-art correction reduces one signal; it is not a finishing artist

**Observed:** 12/52 selected plates receive `ImageFilter.MedianFilter(3)` blended with the original RGB. The original and result hashes, blend strength and noise metrics are recorded. The current 52 leaf hashes independently reconcile without missing files or mismatches. This is a real bounded pixel operation.

It cannot repair action geography, expressive anatomy, omitted contact, palette hierarchy or line economy. It changes pixels across the whole plate, so “frozen anatomy/material boundaries” is an intended visual constraint, not pixel immutability. Noise ratios may fall while useful fine contours soften. Independently inspect faces, hands, gear boundaries and focal effects before accepting the result. “PASS_FULL_AND_PHONE_VISUAL_REVIEW” is bulk assigned from the invocation flag; a per-panel review record should say who actually saw which art at what scale. [Repair code](/mnt/c/AgentWorkspaces/anime-pipeline-ember-lattice-editorial-gear-20260904/src/reimaginings/ember_lattice/premium_rd/editorial.py:134).

## 6. Legacy routes contain useful engineering and real negative evidence

- **Global LoRA versus regional text:** `gen3.py` chains LoRAs globally but uses `ConditioningSetMask` for text. It explicitly documents why percentage-area conditioning failed. Calling this a regional LoRA system would overstate control.
- **Matte and stage:** separate actors, contact shadows, grading and occluders solved distinct compositing problems. G07 matte controls preserved more than 91% of exterior pixels but failed both seated-at-table assertions because actor plates contained furniture. Alpha separability did not produce reusable actor/pose assets.
- **Sequential inpaint:** isolated role binding improved in small preflights, but broad masks changed the set. Preserve this failure instead of assuming stronger identity conditioning solves geography.
- **Blender/OBJ and proxy routes:** geometry import/calibration was real; colored roles were deliberately not identity or final art. Local FLUX/Illustrious/Xinsir controls had target/no-change failures. Their existence does not demonstrate a ready conventional storyboard-to-finished-panel pipeline.
- **Provider G07:** four providers produced 16 required fictional-control candidates. Drift, transport recovery and target-change mechanisms were measured. No-change drift was not semantic beauty or professional-comics scoring.
- **Deterministic repair boundaries:** outside-mask equality and byte-copy no-change are valuable compositor invariants. The local OpenAI hardening record made zero additional provider calls. It does not prove the provider itself obeys a precise edit boundary on real character art.

See [complete genealogy](pipeline-inventory.md) for exact results, dormant controls and source paths. No previous runtime, model cache or build was altered during this audit.

## 7. Reproducibility, economics and provenance

A generated artifact hash proves byte identity, not reproducible generation. `imagegen-default` is a tool-route alias. `exec-…` IDs are orchestration identifiers; no verified provider request identity or backend snapshot should be inferred. Premium raw records carry empty `input_references` arrays even though the generation spec records shared references. Recoverable manifest linkage should be retained; any missing exact call input remains unknown.

The premium session ledger records **61 calls**: 3 reference, 24 benchmark, 4 benchmark edits, 28 unique chapter and 2 chapter edits. Its per-output times amortize parallel batch wall intervals. They are not provider latency, sequential wall time or human effort. The final 170 asset-bound RenderRecords include baseline bindings, local SVG outputs and preserved diagnostics; they are not a candidate-generation denominator.

Historical G07 aggregate direct cost is documented at **$1.057377**, combining exact returned credits/ticks and usage-rate estimates, including a failed transport. This audit's direct paid/cloud spend remains **$0**. In-product monetary cost/usage and human minutes per acceptable panel are unknown. Don't rank routes by a misleading `0` compositor cost or call amortization.

Deterministic assembly is reproducible conditional on original raster files, fonts, renderer and dependencies. Ignored raster caches mean a clean Git clone alone cannot reproduce art-bearing readers. Premium source requests Arial/Arial Black fallbacks; exact portable glyph appearance is not pinned by SVG source alone. Model-license and legacy likeness provenance remain unresolved local-record concerns, not a commercial clearance opinion. No private reference contents or weights were inspected or uploaded here.

## 8. Maintainability and useful test coverage

Read-only enumeration finds **603** `src/north_garden/*.py` modules, **76,613 physical lines**, **317** `validate*` files, and only **two** modules with relative/package imports. There are **506** SHA-named helper definitions under the measured name set. This is a large copied-script surface. It plausibly increases repair cost and makes authority hard to find; the audit has not measured developer hours lost to duplication.

Borrowed Down has four discovered test methods; City six; current premium eleven. Premium adds small shared model/render/core/audit modules and genuine failure-injection checks for hash/link/collision/area/type/negative-space/duplicate-art/clean-art states. Those are useful. Test count does not establish visual semantic coverage, and running tests that author/build assets inside old trees is inappropriate during preservation review. The lead may run isolated scoped tests against copies where needed; no prior builds were run for this report.

Extract common hashing/schema/link/manifest functions only when a pilot needs them. Do not spend another production cycle mechanically consolidating hundreds of validators before proving the page. Retain immutable source identifiers, auditable replacements, nullable metadata and small injection tests. Retire generated quality scores from selection and replace authoritative-but-circular zone/scenario data.

## Highest-return correction program

1. **Before generation:** thumbnail the frozen sequence; map attack/counter/reversal/contact/aftermath and equipment states; annotate real character/environment geometry and reserve copy space.
2. **Before selection:** require one-to-one beat correspondence. A spectacular source depicting the wrong event fails. No substitution by a unique hash, related emotional mood or available benchmark art.
3. **Before lettering:** independently annotate faces/hands/contact/gear on the selected pixels. Measure rendered font size at actual panel width, not the viewport constant.
4. **Before ranking:** compare matched complete sequences with frozen criteria and independent blinded reviews. Preserve minimum-quality failures; allow every route, including baseline, to lose or win.
5. **Before scale:** record attempt/retry/correction counts, actual human minutes, source/edit provenance, and owner preference. Pay for no new provider or external labor during this audit. A human-directed approach remains an unpriced hypothesis until its pilot is run.

These corrections retain the strongest infrastructure while directly addressing failure causes. They do not require abandoning Ember, and they do not establish that Ember's story or the existing generator can reach the owner's desired ceiling. The neutral next pilot must test that question through actual reading.
