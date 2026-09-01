# Experiment log

## 2026-09-01 - CH05 approval, comic-intent promotion, and lettering-field review

- The project owner approved the clean CH05 Mill Signal development script, four-panel contact sheet, and narrative-development promotion template. The immutable promotion decision is `production/decisions/ng-decision-ch05-mill-signal-promotion-r1.json`; it creates current story state, asset registry, scene beat, 50 comic-only panel plans, comic style direction, and a 53-assertion manifest without reclassifying the original smoke renders as accepted.
- The production record validator and frozen v2.1.1 research validator both return `0 failures, 0 warnings`. All CH05 plans remain explicitly `2d_only`; this is not a claim of canonical-stage grounding and contains no animation-shot record.
- A non-destructive lettering-field overlay was built at `experiments/review-packets/ch05-mill-signal-imagegen-smoke-r1/lettering-safe-zone-overlay-r1.png` (SHA-256 `bc8d68e4d0fa988bfe740d5860d7d537ac75fbba05d5595c73965d894d9dfd23`). It identifies P050 as promising, P001 as test-layout-required, and P029/P036 as likely needing a quieter rerender or intentional balloon treatment.
- Visual direction is now recorded in `docs/research/ch05-visual-direction-assessment-20260901.md`: preserve the atmospheric illustrated style for anchors, but alternate it with lower-density dialogue/orientation panels, deliberate text fields, and local causal movement cues. This is a design hypothesis to test, not a production or commercial acceptance result.

## 2026-08-31 - `baseline_legacy` adapter preflight

- Status: completed, operational preflight; excluded from Stage-A scoring.
- Case/seed: `G01` / `101`.
- Result: one candidate rendered in 45.114 seconds through the unchanged `garden/gen3.py` graph.
- Record: `experiments/records/baseline_legacy/baseline_legacy-G01-101.json`.
- Environment: ComfyUI `82f839f5e737d8bfce480872ba05e5a430f2526f`, ComfyUI 0.33.0, Python 3.14.6, PyTorch `2.12.0.dev20260408+cu128`, CUDA 12.8, RTX 5090 Laptop GPU.
- Caveat: the semantic case is `grounded`; the legacy adapter has no canonical stage/control bundle and records this explicitly. It is a renderer failure-profile baseline, not comparable grounded-stage evidence.

## 2026-08-31 - Stage-A restart

- The first batch launch was stopped after two completed `G07a` attempts when adapter inspection found a hard-coded left-region assignment that would miscompile `G07b`.
- Those attempts are retained as operational non-scoring evidence. Stage A is restarted only after the compiler derives left/right region assignment from each frozen case manifest.

## 2026-08-31 - `baseline_legacy` Stage A completed

- 24 frozen requests completed with trace records; total renderer time was 903.79 seconds (37.66 seconds mean).
- Result: rejected without tuning. No candidate passed all declared assertions. Recurrent failures were photoreal regression, identity/role failures, unstable set semantics, and failed interaction/blocking.
- Both `G11a` seeds generated an extra child, a zero-tolerance failure.
- Results: `experiments/results/baseline_legacy_stage_a_20260831.json`.
- BenchmarkCaseBundle v1 is explicitly `DRAFT_LEGACY_LIMITED_NOT_FROZEN`; it records the absent canonical stage/control bundle instead of pretending equivalence.

## 2026-08-31 - CH01 kitchen argument sequence accepted for internal research

- Four calibrated composited panels (`p006`, `p007`, `p008`, `p010`) were reviewed as a meaningful existing legacy narrative sequence.
- The acceptance is internal only and archival: its historical source-generation and human-review timings were not captured, and model/license review blocks commercial release.
- Immutable panel IDs, source hashes, output hashes, assertions, and limitations are in `production/accepted/ch01-kitchen-sequence-v1.json`.

## 2026-08-31 - `sequential_inpaint_per_character` P07 mechanical smoke

- Status: completed as a local-only, non-scoring preflight. This is a new repair arm; `baseline_legacy` was not tuned or modified.
- Two seeds ran two isolated adult passes each (four renderer generations, 108.42 seconds total). Seed 101 retained Soren on the left and added Sigrid on the right; seed 202 failed to add Sigrid on its second pass and changed surrounding kitchen geometry.
- Target-region mean absolute change was 0.223–0.276, while non-target change was 0.0032–0.0039. These are simple pixel-change diagnostics, not semantic correctness scores.
- Seed 101 is accepted only as a mechanics smoke candidate; neither output is accepted as a production-panel replacement. No VLM, cloud/API, external upload, child reference, or timed human review was used.
- Raw records: `experiments/records/sequential_inpaint_v1/p07-seed-101.json` and `p07-seed-202.json`. Decisions and hashes: `experiments/results/sequential_inpaint_p07_smoke_20260831.json`.
- The first raw records reveal a provenance omission (runtime/workflow/source hashes). The v1.1 harness now records those fields for subsequent runs; the omission is retained rather than rewritten.
- A v1.1 replay at the same seed preserved the original raw record and reproduced both output hashes exactly. `p07-seed-101-r2.json` supplies the complete runtime, custom-node, model/LoRA, workflow, input/mask, output, timing, and source-code provenance for that deterministic confirmation.

## 2026-08-31 - `sequential_inpaint_per_character` G07 role-swap controls

- Status: completed as a non-scoring legacy preflight. G07a/G07b semantics and their `grounded` declaration were read from, but never modified in, the frozen gauntlet.
- Versioned legacy table plates, broad left/right masks, zero-mask no-change controls, and resolved HardAssertionManifests are in `manifests/experiments/sequential-inpaint-g07-controls-v1.json`.
- Initial denoise-zero controls with active inpaint masks blanked the masked region (target MAE 0.3283), proving them invalid. The records are retained. Corrected zero-mask reconstruction controls established a 0.0084 MAE VAE/workflow baseline.
- Four two-pass smoke attempts (`G07a/G07b` × seeds 101/202) took 216.70 seconds total. Agent visual triage saw requested left/right identities in all four; G07b had one failed and one indeterminate seated/blocking assertion. All outputs are rejected for production.
- Primary finding: broad masks redraw kitchen material within their target region. Low non-target change does not establish set continuity. This is a mask/control limitation, not evidence of a solved sequential-inpaint renderer.
- Full decisions, hashes, timings, and limitations: `experiments/results/sequential_inpaint_g07_controls_20260831.json`.

## 2026-08-31 - `actor_matte_legacy_composite_control` G07 control

- Status: completed local deterministic control. It reused existing adult actor plates and calibrated 2D stage code; it made no diffusion call, model download, external upload, or baseline change.
- Both role swaps retained the kitchen plate outside the actor/shadow influence region (91.60% and 91.31% unchanged pixels). This establishes set preservation for the compositor only.
- Both outputs were rejected for the semantic smoke: the existing actor plates carry their own tables/props and their poses do not satisfy “both seated at table.” Identity label alone is not an adequate reusable actor-asset record.
- Output hashes, source hashes, assertion decisions, and limitations: `experiments/results/actor_matte_g07_controls_20260831.json`.

## 2026-08-31 - minimal CH01 shared production records

- Status: completed local foundation. Existing CH01 evidence is now linked through StoryState, AssetRegistry, SceneBeat, ComicPanelPlan, and immutable EditionManifest records.
- The narrow validator checks stable panel IDs, plan/edition linkage, asset references, declared spatial modes, comic-versus-animation separation, and selected output hashes. It returns `0 failures, 0 warnings`.
- The records preserve the calibrated 2D and embedded-prop limitations of legacy assets; they do not upgrade those assets to canonical 3D or production-commercial status.

## 2026-08-31 - controlled local actor-asset inventory

- Four existing adult plate families and their two revisions were catalogued from local outputs and source references. No new image was generated or uploaded.
- No plate is verified pose-, prop-, and camera-separable for a generic G07 seated-table assertion. The result explains the actor-matte control failure and blocks treating legacy full-frame plates as reusable actor assets.

## 2026-09-01 - FLUX.2 klein 4B fictional proxy smoke

- Official FP8 transformer, Qwen3 4B text encoder, and Flux2 VAE were downloaded locally with pinned revisions and verified hashes. The transformer license artifact is Apache-2.0.
- Two proxy role-order runs completed locally in 18.613 and 16.509 seconds. Both visibly met proxy count, left/right role, common-table, non-touching, and kitchen assertions.
- This is only an operational proxy result: no adult reference input, no identity conclusion, no grounded benchmark score, and no production acceptance.

## 2026-09-01 - FLUX.2 klein 4B reference-conditioned proxy edit

- Status: completed non-scoring repair-mechanics smoke using only the generated fictional proxy panel as input. The graph is captured at `experiments/workflows/flux2_klein_proxy_reference_edit_v1.json` and derives its reference-conditioning structure from ComfyUI's installed FLUX.2 Klein blueprint.
- The first submitted graph was rejected before rendering because its image-size links incorrectly referenced `LoadImage` outputs rather than `GetImageSize`; the corrected graph executed successfully, and this integration mistake is retained as operational evidence.
- The corrected run took 35.307 seconds and visibly retained the two-token shared-table kitchen composition while changing the requested right-side token from orange to green. Its output hash is `56dcaf9e746a3794f386cf1a349df8bb0b280a01e2f8c30ec2540167d6023be2`.
- Pixel diagnostics show 83.58% of pixels changed, with a full-frame changed bounding box. Thus the method is semantic reference editing, not demonstrated targeted repair or a valid no-change control. No adult likeness/reference input, child asset, external service, or timed human review was used.

## 2026-09-01 - FLUX.2 klein 4B proxy no-change control

- Status: completed, non-scoring and fictional/proxy-only. Two reference-conditioned runs asked to preserve the proxy panel exactly (seeds 7402/7403) in 35.302 and 35.253 seconds.
- Both retained proxy-level count, color order, shared-table/non-contact, and kitchen-framing semantics in agent triage. Pixel diagnostics rejected both as no-change controls: 84.26% and 86.19% of pixels differed, each with a full-frame difference box (MAE 10.925 / 26.079).
- Decision: retain this FLUX path as an operational semantic reference-edit capability, but reject it as targeted repair evidence. Complete graph, pinned component hashes, output hashes, times, assertions, and failure decision: `experiments/results/flux2_klein_proxy_reference_controls_20260901.json`.

## 2026-09-01 - controlled Sigrid actor-plate narrow retry

- Status: completed local-only, non-scoring retry. Two explicitly invisible-support seated Sigrid plates rendered in 28.220 and 39.148 seconds; both were rejected: the first embeds a black tabletop and the second a handheld tray.
- The first renderer request completed but the harness raised a `NameError` while writing its record. The source was corrected, and the exact candidate/hash, Comfy-history timing, and incident are preserved rather than rerendering it as if nothing occurred.
- Outcome: furniture/prop leakage is now 4/4 across reviewed Sigrid attempts. No alpha/matte or G07 compositor test proceeded, because the required actor-only asset is absent. Full decisions: `experiments/results/controlled_actor_capture_v2_review.json`; ADR: `ADR-0008-legacy-seated-actor-capture-is-not-a-reliable-separable-asset-route.md`.

## 2026-09-01 - FLUX.2 Klein geometry-proxy G07 stage-conditioning smoke

- A new `DRAFT_FICTIONAL_PROXY_STAGE_NOT_FROZEN` bundle maps G07a/G07b semantics to the existing deterministic geometry proxy assets without modifying the gauntlet. It explicitly records that these are abstract roles and not canonical grounded-stage evidence.
- Three local reference-conditioned runs took 103.829 seconds. G07a seed 7501 and G07b seed 7503 passed proxy count/order/table triage; G07b seed 7502 duplicated the orange-circle token, failing the exact-count assertion. Proxy hard-assertion pass rate is therefore 2/3, with one extra-token failure.
- Decision: retain geometry-stage conditioning as a promising spatial interface, but reject the smoke as sufficient role-count reliability, targeted repair, or any frozen benchmark result. Output/provenance record: `experiments/results/flux2_klein_geometry_proxy_g07_smoke_20260901.json`.

## 2026-09-01 - FLUX.2 Klein paired geometry-proxy stability control

- Status: completed local-only, fictional-proxy control. A reproducible harness hash-checks the frozen gauntlet and captures an immutable `RenderRecord` for each request. It ran G07a/G07b at the same two seeds (7511/7512): four generations, 220.220 seconds total, no external cost.
- All four outputs retained the declared side position, shared table/non-contact blocking, and kitchen proxy. All four failed exact count: the orange circle became a stacked orange head/body-like pair. This is 0/4 exact-count passes and 4/4 side-position/blocking passes.
- Decision: do not keep sampling the same circle/triangle proxy. Geometry remains spatial authority, while renderer-facing role encoding needs redesign. Full review: `experiments/results/flux2_klein_geometry_proxy_g07_paired_control_20260901.json`; ADR-0009 records the boundary.

## 2026-09-01 - FLUX.2 Klein non-figurative tile representation control

- The same paired G07 protocol replaced circle/triangle tokens with fixed orange/teal rectangular tiles. Across four local requests (two paired seeds), exact marker count, left/right color order, and table/stage layout all passed in agent triage: 4/4 each, 243.738 seconds total.
- Marker appearance drifted into chair-like forms in 3/4 outputs. Thus the representation change isolates and avoids the circle-as-head/body count failure, but does not produce final-art or identity-preserving controls.
- Decision: keep tiles only as a renderer-facing spatial/role-order diagnostic. Full record: `experiments/results/flux2_klein_geometry_tile_proxy_g07_paired_control_20260901.json`.

## 2026-09-01 - Soren actor-plate alpha separability control

- The only previously provisional Soren plate was tested using a deterministic fixed color-distance key. It achieved 0 sampled-corner background false positives and a 21.75% foreground fraction; the mechanical alpha assertion passes.
- The checkerboard matte preview retains a long dark attached foreground artifact near the hands. Therefore alpha separability does not establish actor-only separability. The plate is not eligible for a G07 composite, and the current legacy actor-plate route has no verified reusable Soren or Sigrid plate.
- Record: `experiments/results/actor_alpha_control_soren_20260901.json`; design boundary: ADR-0010.

## 2026-09-01 - kitchen table spatial-stage contract

- Added a renderer-agnostic, versioned kitchen-table spatial contract from the existing calibrated legacy plate: comic camera/horizon/floor calibration, foreground-table occluder, seated anchors, and non-contact rule.
- The contract explicitly declares `CALIBRATED_2D_LEGACY_REFERENCE_NOT_CANONICAL_3D`; it is a spatial authority bridge for adapters, not visible final art, character identity, or an animation camera/e-conte record.
- The production-record validator now checks the authority boundary, occluder geometry, and comic-versus-animation separation. It and the frozen-package validator remain at 0 failures / 0 warnings.

## 2026-09-01 - portable canonical-geometry bootstrap

- Blender was not detected on PATH or in the standard local install location, and no existing `.blend`/interchange stage asset was found. A portable OBJ bootstrap now records floor, wall, table, legs, seated anchors, and a seated reference-camera line in metres.
- The OBJ and its manifest are locally syntax/invariant validated, with pinned hash `20904fc8ddcaf561227a227a95eac3f2181744196da0f8e70da98df81c69effa`. It is explicitly `GEOMETRY_BOOTSTRAP_NEEDS_BLENDER_OPEN_VALIDATION`, not a production canonical-stage claim.
- A local package-manager metadata query timed out before resolving an official Blender package/version, so no installation was attempted or assumed. The next Blender-dependent step remains a controlled import/open calibration with recorded version/provenance.

## 2026-09-01 - resolved comic spatial inputs

- Grounded CH01 ComicPanelPlans now carry an explicit kitchen-stage contract ID and per-role anchor/world assignments. A deterministic resolver emits camera, table occluder, and placement inputs into a comic-only intent artifact.
- The resolver output is explicitly `INTENT_DERIVED_NOT_RENDER_PROVENANCE` and contains no animation shot plan. The production validator now checks stage linkage, resolved-input source hash, and this media boundary.

## 2026-09-01 - deterministic tile-proxy QA sensor

- A local color/component QA harness now evaluates only fixed stage-declared marker regions, avoiding a false global teal detection from the kitchen window. All four paired tile outputs pass one-orange, one-teal, and declared left/right order under this adapter-specific sensor.
- This is a `NON_GATING_PROXY_SENSOR_ONLY` measurement: it validates color markers in a fixed control stage, not character identity, final-art marker morphology, pose, set continuity, or production quality. It is retained as a foundation for later no-change/control/injection calibration rather than being promoted to general VLM QA.
- Result/provenance: `experiments/results/flux2_klein_geometry_tile_proxy_qa_20260901.json`.

## 2026-09-01 - deterministic tile-proxy QA error injections

- Four derived local fixtures calibrated the stage-scoped tile sensor: one valid reference passed, while duplicate-orange, missing-teal, and left/right role-swap injections were each rejected (1/1 valid pass, 3/3 injected-error rejections).
- The first fixture assessment exposed a relative-path normalization bug in the harness before any judgment; it was corrected and the same fixtures were rerun. This is calibration evidence for a fictional control sensor only, not a benchmark result or real-panel QA authority.
- Record: `experiments/results/proxy_tile_qa_injections_20260901.json`; fixture generator: `src/north_garden/make_proxy_tile_qa_injections.py`.

## 2026-09-01 - reusable FLUX.2 Klein local render profile

- Consolidated pinned component hashes, ComfyUI commit, local-only input boundary, evidence records, and known limitations into `experiments/render-profiles/flux2-klein-local-r1.json`.
- Primary-artifact follow-up resolved the dependency states: the Qwen 3 4B encoder source declares Apache-2.0, while the exact `flux2-vae` source declares `flux-1-dev-non-commercial-license`. The profile is therefore explicitly non-commercial because of the pinned VAE, not an unresolved inference.

## 2026-09-01 - consolidated time/cost ledger

- Consolidated 58 measured local renderer generations across baseline, repair, actor-capture, and FLUX controls: 2,113.602 seconds / 0.587 renderer-hours, $0 external spend, and zero production-accepted experimental outputs.
- Timed human review and local electricity/depreciation remain unmeasured. Historical CH01 acceptance is excluded rather than turned into a false throughput metric because its source timings were not captured.

## 2026-09-01 - Blender kitchen-stage import

- Downloaded the official portable Blender 5.2.1 Windows x64 archive, verified its SHA-256 against Blender's published checksum, and imported the pinned kitchen OBJ in Blender background mode.
- All required named geometry/anchor/camera-line objects imported and a pinned `.blend` artifact was saved. The stage is now `GEOMETRY_BOOTSTRAP_BLENDER_IMPORTED_NOT_CALIBRATED_FINAL_ART`: import is verified, but camera/occlusion calibration and final set build remain work.
- Complete tool, source, script, and output hashes: `experiments/results/blender_kitchen_stage_import_20260901.json`.

## 2026-09-01 - Blender kitchen-stage visual calibration proxy

- A raw-geometry Workbench attempt could not expose the zero-thickness OBJ planes/anchors, so a separate solid cuboid inspection proxy was deterministically derived at the same pinned coordinates. This distinction is deliberate and is captured by ADR-0011.
- The final wide diagnostic visibly contains the common table and both physically separated, colored seating anchors. It verifies Blender coordinate execution only; it does not match the legacy comic framing, establish final materials/occlusion, or constitute character/role-binding evidence.
- Attempt history, output hashes, local tool provenance, and unmeasured human-review field: `experiments/results/blender_kitchen_stage_calibration_20260901.json`.

## 2026-09-01 - Blender-derived kitchen control bundle v1

- Produced a base stage plus G07a/G07b neutral role-position controls from the pinned Blender geometry. A repeat G07a construction was byte-identical (0.204 seconds across four local renders), establishing deterministic construction only.
- Inspection exposed a real coordinate ambiguity: world X-negative projects to screen-right under the diagnostic camera, while the bootstrap object names embed character and left/right labels. ADR-0012 blocks use of the bundle as a frozen G07 renderer case rather than silently inverting semantics.
- The asset bundle is now `DRAFT_DIAGNOSTIC_ONLY_NOT_STAGE_A_COMPATIBLE_NOT_FROZEN`. A neutral-anchor world-to-panel mapping is required before any image renderer can demonstrate ingestion, no-change, and injection controls. Bundle/protocol: `production/stages/controls/kitchen-table-blender-control-bundle-v1.json`.

## 2026-09-01 - neutral-anchor kitchen control bundle v2 and FLUX adapter smoke

- A non-destructive r2 stage revision replaces character-named anchor objects with neutral world X-negative/X-positive anchors. Its separate comic-panel projection map documents that the declared control camera projects world X-positive to screen-left; ADR-0012 records why this cannot be implicit.
- The local FLUX reference adapter then ran G07a/G07b at paired seed 7601 against this bundle. Both outputs visually pass two neutral tokens, declared screen order, common table, and non-contact: 2/2 proxy-control passes in 102.026 seconds.
- This is not a benchmark score or production result: one seed, no identity, no artist-time measurement, and no renderer no-change/injection control. The exact pinned VAE remains non-commercial. Records: `experiments/results/flux2_klein_blender_kitchen_control_g07_paired_20260901.json` and `production/stages/controls/kitchen-table-blender-control-bundle-v2.json`.

## 2026-09-01 - FLUX Blender-kitchen renderer no-change control

- Seed 7602 asked the same local FLUX adapter to preserve the G07a Blender control exactly. It retained the coarse two-token/table layout but globally restyled the image: 99.986% decoded pixels changed, with a full-frame difference bounding box.
- Decision: reject this route as targeted-repair/no-change evidence and do not continue same-method sampling. It may remain a non-commercial composition-control diagnostic. Complete result: `experiments/results/flux2_klein_blender_kitchen_control_nochange_20260901.json`.

## 2026-09-01 - Illustrious XL v2 fixed base-checkpoint control smoke

- Downloaded the exact official revision `69459c1fe6f46db41ab31e6114f05acc0e06bcaa`; upstream LFS and local SHA-256 agree at `c2a1…a331`. ComfyUI recognizes the checkpoint. Its declared OpenRAIL-M license remains review-pending, so this is fictional local research only.
- Untuned r1 img2img carried the two neutral tokens, paired screen swap, table, and non-contact in both outputs, but both failed the recurring-kitchen assertion. Its normal-denoise no-change control globally changed 99.954% of pixels.
- Result: partial composition evidence only, no repair/production/benchmark claim. Full records: `experiments/results/illustrious_xl_v2_blender_kitchen_g07_smoke_20260901.json` and `experiments/render-profiles/illustrious-xl-v2-local-r1.json`.

## 2026-09-01 - Illustrious XL v2 mask-limited fictional repair control

- A versioned right-token context mask composited one raw local edit over the original control. Exterior preservation passes exactly: 0 changed decoded pixels outside the mask.
- The raw model did not execute the requested teal-to-green change and introduced target-region artifacts, so the semantic repair assertion fails. This distinguishes deterministic exterior continuity from target correctness rather than claiming a repair success.
- Result: keep the compositor concept, reject the r1 bare img2img semantic-edit route. Record: `experiments/results/illustrious_xl_v2_masked_proxy_edit_20260901.json`.

## 2026-09-01 - Illustrious XL v2 + Xinsir native repaint controls

- The local Xinsir ProMax ControlNet was source-verified by exact SHA-256 against its official Apache-2.0 file. Two integration failures were preserved: grayscale masks yield zero ComfyUI masks, and generic masked-pixel preprocessing yields black output.
- With alpha-inverted mask encoding and Xinsir's documented black-pixel setting, the r3 edit changed the target teal tile to green and the deterministic composite held the exterior at 0 changed pixels. The r4 unchanged-prompt control recolored the target to pale gray, failing target no-change despite its exact exterior.
- Decision: this is the highest-potential local repair-mechanics route, but still not reliable repair, identity, recurring-set, commercial, or benchmark evidence. Full result: `experiments/results/illustrious_xl_v2_xinsir_repaint_proxy_controls_20260901.json`; boundary: ADR-0013.
- A first-harness composite filename collision was detected during provenance review. Raw candidates were intact; immutable r3/r4 composites were reconstructed with hashes matching their records, and the original records were not altered. Correction: `experiments/results/illustrious_xl_v2_xinsir_repaint_artifact_correction_20260901.json`.

## 2026-09-01 - Xinsir repaint low-denoise target/no-change matrix

- At strength 0.8, both denoise 0.35 and 0.65 produced a pale-gray target in both the teal-to-green edit and unchanged-target control. Thus neither configuration executes the requested change or preserves the original target color.
- All four composites preserve the exterior exactly (0 changed pixels outside the mask). This validates the compositor boundary but rejects low denoise as the semantic/no-change solution; no more seeds are justified at these variants.
- Full result: `experiments/results/illustrious_xl_v2_xinsir_repaint_target_nochange_matrix_20260901.json`.

## 2026-09-01 - Xinsir repaint strength target/no-change matrix

- At denoise 1.0, strength 0.4 and 1.0 each yielded the same pale-gray target in both the teal-to-green edit and unchanged-target control. Neither strength performed the requested edit or preserved teal.
- All four final composites still changed exactly 0 pixels outside the declared mask. This keeps the deterministic exterior boundary, but rejects both tested strengths as semantic repair/no-change settings; no further samples at these variants are justified.
- Full result: `experiments/results/illustrious_xl_v2_xinsir_repaint_strength_matrix_20260901.json`.

## 2026-09-01 - Xinsir repaint d1.0/s0.8 paired replication

- The sole prior green edit did not replicate: at a new paired seed, the edit target remained teal and the no-change target drifted blue. Exact exterior preservation remains 0 changed pixels outside the mask in both renders.
- Observed fictional target-edit mechanics are now 1/2, while observed target no-change is 0/2. ADR-0014 therefore blocks mask-boundary tuning and rejects this adapter configuration as a reliable repair route.
- Full result: `experiments/results/illustrious_xl_v2_xinsir_repaint_replication_20260901.json`.

## 2026-09-01 - hard-assertion manifest and separated review record v1

- Added an adapter-neutral comic `HardAssertionManifest` for fictional G07 proxy controls, explicitly separating pre-render intent from execution records and review outcomes. The manifest contains no animation-shot plan and cannot freeze a benchmark bundle.
- The paired Xinsir replication now has a hash-linked assertion review: spatial proxy assertions pass, while target edit and target no-change fail. Human minutes remain explicitly unmeasured and the result is rejected rather than represented as production acceptance.

## 2026-09-01 - Qwen-Image-Edit-2511 pre-acquisition feasibility

- Pinned current official source revision, README hash/license declaration, artifact inventory, and local runtime evidence without downloading model weights. The 53.75 GiB BF16 artifact set cannot fit in the installed 24 GiB GPU before working memory; the local environment also lacks the official quick-start's Diffusers/Accelerate dependencies.
- Acquisition is deferred pending a deliberate capacity/profile decision. The future protocol is fictional geometry controls first, with paired role-order, no-change, and error-injection controls; no adult reference upload is permitted.

## 2026-09-01 - BenchmarkCaseBundle v1 draft

- Versioned the neutral Blender G07a/G07b control assets, manifest, no-change requirement, injection-calibration boundary, stage limits, and freeze gate in one adapter-specific draft bundle.
- The bundle deliberately covers only the selected interaction pair, remains `DRAFT_ADAPTER_SPECIFIC_G07_CONTROLS_NOT_FROZEN`, and does not change the frozen semantic gauntlet or report a benchmark score.

## 2026-09-01 - native repaint provenance validator v1

- Added a narrow validator for the ten immutable local native-repaint execution records and their separate G07 assertion review. It verifies candidate hashes, frozen semantic-source hash, workflow mode, timing, cost, pending human-minute state, rejection state, and exact-exterior measurement.
- The validator deliberately does not validate comic intent from `RenderRecord`; it checks the separately linked review/manifest boundary instead.

## 2026-09-01 - renderer decision gate

- ADR-0015 closes further same-route native repaint tuning: current evidence requires a distinct renderer mechanism rather than additional parameter/mask samples.
- The decision memo ranks Qwen-Image-Edit-2511 as the next high-information fictional-control arm, but defers acquisition/execution until a suitable local, validated offload/quantization, or approved paid/cloud capacity route is chosen.

## 2026-09-01 - official Comfy Qwen-2511 INT8 option assessed

- The current official Comfy template identifies a 28.07 GiB local-download profile (INT8 diffusion, FP8 text encoder, VAE), materially smaller than the original 53.75 GiB BF16 package. It was not downloaded because it is one of multiple plausible large profiles.
- The exact prescribed encoder source repository currently carries a `tencent-hunyuan-community` label while the Comfy diffusion/VAE repositories declare Apache-2.0. The profile is therefore local-research only and commercially unresolved; this is recorded as an exact-component gate rather than assumed compatible.
- Primary-license review confirmed the underlying Tencent Hunyuan license is territory-limited (excluding EU/UK/South Korea) and has downstream conditions; the profile cannot silently become the long-term commercial default.

## 2026-09-01 - Qwen INT8 acquisition preflight

- Added a no-download profile/validator that pins the official INT8 artifact hashes, exact dependency license states, installed Comfy blueprint hash, fictional-only G07 smoke protocol, and required acceptance/provenance fields.
- The preflight explicitly asserts that the two large artifacts are absent and that the already-local VAE hash matches its current official source. It does not select or acquire the profile.

## 2026-09-01 - cross-arm failure taxonomy and profile

- Added a governed, non-gating taxonomy and validated evidence synthesis across baseline, adult capture, geometry proxy, sequential inpaint, FLUX, and native repaint arms.
- The profile identifies the same unsolved production constraints across arms: role/identity binding, target no-change, recurring final-set continuity, and measured human acceptance time. It preserves the distinction between positive geometry/exterior mechanisms and production acceptance.

## 2026-09-01 - `geometry_proxy_g07_control` local spatial-control route

- Status: completed non-scoring control using generated abstract role tokens only; no image renderer, network request, adult likeness asset, or child asset was used.
- G07a and G07b role swaps each passed two-token count, declared left/right token, common-table seating/occlusion, non-touching separation (356 px), and a bit-identical no-change control. The base stage was unchanged outside the explicit proxy/table layers (80.845%).
- This validates an interface for grounded geometry staging, not SOREN/SIGRID identity, final art, or renderer robustness. It remains distinct from the frozen renderer benchmark.
- Complete provenance and decisions: `experiments/results/geometry_proxy_g07_controls_20260901.json`; decision boundary: `docs/adr/ADR-0006-geometry-proxies-are-spatial-controls-not-identity-evidence.md`.

## 2026-09-01 - frontier/managed renderer bakeoff plan r1

- Established `experiments/renderer-bakeoffs/g07-fictional-bakeoff-r1.json` and a validator for the same four-request fictional G07 protocol across Gemini, Grok Imagine, GPT Image, BFL FLUX.2, and managed-GPU Qwen. The plan pins the frozen semantic source and local input hashes, requires provider request/response/cost/review provenance, and explicitly forbids child data, real-person likeness, and adult-likeness output as external input.
- The plan validates with 0 failures / 0 warnings. The current environment exposes no relevant provider credential variable names, so it remains `PLANNED_NO_PROVIDER_CREDENTIALS_PRESENT`; no account, API call, model download, or spend occurred.

## 2026-09-01 - CH01 deterministic chapter-lint foundation

- Added `src/north_garden/chapter_lint.py` and a hash-linked CH01 lint record. It verifies selected asset hashes, stable panel IDs, reading order, and DCT perceptual-hash near-duplicates without treating execution provenance as story intent.
- The archival CH01 sequence passes immutable hash, known-panel, and display-order checks. Its P007/P008 pair has a DCT pHash distance of 4 despite distinct visible blocking/actions on human review, so the provisional duplicate threshold is recorded as one **advisory**, not a failure. It cannot be calibrated from one short archive.
- Balloon/read-order geometry is explicitly `not_assessable`: the archive contains no lettering geometry manifest. The lint is non-gating until it is calibrated on at least two approved, lettered chapter drafts. Result: `experiments/results/chapter_lint_ch01_research_edition_001.json`.

## 2026-09-01 - stable panel identity and revision migration

- ADR-0016 preserves all CH01 v1 archival records while correcting the production identity boundary. `production/comic/ch01-sc01-panel-plans-v2.json` uses stable panel IDs independent of both display order and plan revision; `PanelRevisionCollection` records immutable raster revisions separately; edition 002 selects revision IDs.
- No raster was regenerated, replaced, or claimed newly reproducible/commercially clear. The successor edition therefore demonstrates panel-addressable immutable revision selection without rewriting historical evidence. CH01 lint runs equivalently through both edition shapes (0 failures, 1 provisional duplicate advisory, 1 unavailable lettering check).

## 2026-09-01 - CH02 treeline-return archival research sequence

- Located an existing adult-only `legacy_duo2` three-panel sequence: movement through wet undergrowth, exhausted return from the treeline, and a held farmhouse-threshold beat. Each selected PNG contains the original ComfyUI workflow graph; `import_historical_comfy_png.py` extracts it as immutable provenance rather than manufacturing missing timing/runtime data.
- CH02 now links StoryState → AssetRegistry → SceneBeat → 2D-only ComicPanelPlans → reconstructed archival review assertions → immutable PanelRevisions → edition selection. It is explicitly a meaningful three-panel research sequence, not a complete chapter, canonical 3D-set result, benchmark score, commercial release, or proof of reproducibility.
- The sibling `duo2_split` output is excluded: it rendered the declared non-humanoid fictional creature as a bull. The selected CH02 edition passes deterministic lint with 0 failures, 0 duplicate advisories, and one honest `not_assessable` lettering check.

## 2026-09-01 - legacy prompt age-token safety correction

- CH02's embedded historical workflow describes adult characters but contains legacy `1boy`/`1girl` tags. There is no child image, likeness, reference, or training data in the selected sequence; nevertheless the terminology is prohibited for future adult production because it is avoidably ambiguous.
- ADR-0017 preserves the historical graph unchanged while requiring explicit adult role language in all future prompt compilers. The imported CH02 images remain local-only archival evidence, not reusable clean-prompt templates.

## 2026-09-01 - `legacy_duo3` fresh local CH03 production demonstration

- Ran three newly authored, adult-only, local candidates through a separate global-LoRA `legacy_duo3` adapter. Every request recorded seed, full graph, model hashes, Comfy prompt ID, candidate hash, timing, and local/no-upload safety state. Total measured generation time: 117.312 seconds; external cost: $0; timed human review: unavailable.
- All three candidates are rejected in visual triage. P001 produced a sexualized wardrobe contrary to the declared costume, P002 created an unrequested split layout and failed distinct action/prop roles, and P003 failed threshold blocking/wardrobe/prop assertions. No same-route prompt tuning follows; the result reinforces the need for a distinct renderer mechanism.
- This is not a `baseline_legacy` score or modification. It is a local production-demo failure profile now linked by the immutable reconstructed r2 review at `experiments/reviews/legacy-duo3-ch03-ridge-signal-review-r2-reconstructed.json`; the preserved r1 linkage is documented as an incident below.

## 2026-09-01 - cross-provider execution gate and adult-prompt correction

- The `legacy_duo3` source profile no longer emits child-coded negative tokens for future adult-only work. Completed records and their embedded execution graphs are immutable evidence and were not altered. This applies ADR-0017 to the forward-facing adapter without treating past terminology as child data.
- The next evidence-supported milestone is the provider-neutral fictional G07 comparison, not another same-route local retune. Gemini 3.1 Flash Image, Grok Imagine Image 2.0, OpenAI GPT Image 2, BFL FLUX.2, and capacity-gated Qwen retain the identical four-request protocol.
- This workspace contains no configured provider credential or managed-GPU account, so no remote call or spend has occurred. `renderer-decision-memo-20260901.md` requests a $20 initial spend cap and locally configured credentials only for the services to be evaluated; all initial inputs remain original fictional adults plus geometry controls.

## 2026-09-01 - legacy_duo3 dry-run provenance correction

- A validation dry run incorrectly overwrote the three completed r1 JSON RenderRecords with planned records. This was diagnosed immediately; original output PNGs, their hashes, and local ComfyUI history remained intact.
- The corrupt r1 records are preserved as incident artifacts. Immutable r2 reconstructed records and a linked r2 review were created from local history, output bytes, and the pre-existing review; no image was regenerated or rejudged. The correction report is `experiments/incidents/legacy-duo3-dry-run-overwrite-correction-20260901.json`.
- `legacy_duo3.py --dry-run` now writes no records. The validator checks the incident boundary and r2 provenance rather than pretending the original r1 record files were unchanged.

## 2026-09-01 - executable fictional API bakeoff adapters

- Added no-dependency, source-pinned OpenAI GPT Image 2 and Gemini 3.1 Flash Image adapters for the existing four-request G07 protocol. Their dry runs validate frozen semantic and control-asset hashes without network traffic or file writes.
- Each `--execute` path requires a locally configured provider key and a positive `NORTH_GARDEN_APPROVED_BAKEOFF_CAP_USD` not exceeding the preflighted $20 cap. The request construction accepts only the plan's original geometry-control assets, not adult likeness or personal reference material.
- Both adapters retain redacted request metadata, input/output hashes, request ID, API endpoint/model, timing, returned usage when available, cost reconciliation state, and mandatory human-review placeholders. No API call, account creation, or spend occurred in this milestone.

## 2026-09-01 - executable Grok Imagine comparator adapter

- Added a no-dependency Grok Imagine Image 2 adapter for the same fictional G07 protocol. It uses xAI's documented JSON image-edit endpoint with an in-memory data URI of the hash-pinned control asset; no public source URL, consumer product, likeness, or personal input is involved.
- On authorized execution it retrieves the returned image URL immediately, stores only its SHA-256 in the render record, and preserves returned provider usage ticks without inventing a dollar conversion. The no-network preflight and plan validator pass; no key, API call, account creation, or spend occurred.

## 2026-09-01 - BFL FLUX.2 terms decision and preflight adapter

- Current BFL API terms explicitly allow use of developer Inputs and Outputs to improve/train services. ADR-0019 therefore sets a hard fictional-control-only boundary: BFL cannot receive adult likeness/reference material, LoRA output, real-person data, child data, or other sensitive content.
- Added a pinned `flux-2-pro` adapter that uses the documented asynchronous edit/poll/retrieve flow. Because BFL's documented edit endpoint takes an input URL, it refuses execution until a configured HTTPS URL is fetched locally and byte-hash-verified against the frozen fictional control asset. No public hosting, BFL call, or spend occurred.

## 2026-09-01 - bakeoff human-review scaffolding

- Added a provider-neutral review builder that discovers completed adapter RenderRecords, rehashes their candidate raster, and creates a separate review artifact only once all four prescribed requests exist. It does not alter the intent manifest, accept a panel, freeze the bundle, or score the benchmark.
- Each candidate receives the applicable hard-assertion fields, failure-tag slot, timed-human-review requirement, and pending decision. The optional VLM field remains explicitly non-gating. With no provider runs yet, all four adapter review dry runs correctly report four missing execution records and write nothing.

## 2026-09-01 - CH03 built-in frontier-art narrative draft

- Generated a new three-panel fictional-adult CH03 `ridge-signal` sequence through the available built-in image-generation service: ridge movement, distinct black-field/root-clearing action, and quiet farmhouse-threshold resolution. A fourth targeted P001 repair candidate failed preliminary prop clarity and is retained separately.
- The sequence now links StoryState → AssetRegistry → SceneBeat → three `2d_only` ComicPanelPlans → separate RenderRecords → immutable PanelRevisions → a pending human review. It contains no AnimationShotPlan, no adult-likeness input, no child data, no commercial-release claim, and no benchmark result.
- Agent visual triage finds P002/P003 promising and P001's two-axe requirement unclear. No panel is accepted: model snapshot/seed/cost are not exposed by the built-in service, and an authorized timed human review is still mandatory. ADR-0020 records a prompt-age-wording hygiene incident without mischaracterizing it as child data.

## 2026-09-01 - CH04 built-in frontier-art continuity draft

- Generated a second three-panel fictional-adult draft with the same reference designs: farmhouse preparation, boot-print investigation, and a distant-smoke hook. All new prompts use the ADR-0017/0020 clean adult-only wording (`exactly two fictional adult humans; no other people`) rather than age-category negative terminology.
- CH04 has the same intent/provenance/revision separation as CH03, with three `2d_only` plans and review-pending immutable revisions. Preliminary visual triage sees clear role/action differentiation in all three panels, but no panel is accepted, reproducible, or commercially cleared without timed human review and model/cost provenance.

## 2026-09-01 - CH03/CH04 draft-edition lint boundary

- Added non-published draft editions for the CH03 and CH04 review-pending revisions. Edition selection here means deterministic reading-order/hash lint only; it does not override the mandatory human-review acceptance boundary.

## 2026-09-01 - narrative-sequence readiness boundary

- Added an immutable-link registry and a deterministic readiness report for the two frontier-art narrative sequences. Both CH03 and CH04 have three selected panels, clean deterministic lint (0 failures; lettering geometry still not assessable), pending human review, and zero accepted panels.
- The report makes the production-scale gap explicit: each is 47 panels below the 50-panel lower target. It is intentionally non-gating and does not equate a small visual sample with chapter readiness, reproducibility, commercial eligibility, assertion success, or human acceptance. Results: `experiments/results/chapter_draft_readiness_20260901.json`.

## 2026-09-01 - CH03/CH04 human-review packet and source-control gap

- Built a labeled six-panel contact sheet and review packet from the hash-pinned draft revisions at `experiments/review-packets/narrative-sequences-20260901/`. It is a review aid only: an authorized reviewer must still create a new immutable review revision with decision, failure tags, and measured minutes.
- Verification also found no detected Git worktree at the workspace root. ADR-0021 records the resulting source-revision provenance gap and deliberately avoids silently creating a new repository/history.

## 2026-09-01 - chapter-scale historical-script discovery and quarantine

- Discovery located `garden-work/northgarden/pilot.md`, a pre-existing two-chapter, chapter-scale script. Its opening calls itself 92 panels while its numbered chapter headers/footer say 52 + 44 = 96, so no count is treated as authoritative without owner review. This is the first concrete local chapter-scale narrative source found in the workspace.
- It names the leads Dio/Thal rather than current Soren/Sigrid records and its accompanying material describes photo-derived design choices. ADR-0022 preserves it as historical evidence but blocks any silent canon/name/asset/prompt import. It does not close the gap to a current, clean, instrumented 50–90-panel production draft.
- `research/historical/inventories/gardens-anchor-pilot-r1.json` now hash-pins the source (`ef5967…2a5759`) and verifies contiguous numbered runs of 52 and 44 panels. It also proves the source's 92-vs-96 total contradiction. The inventory contains no copied panel prose or image assets and retains the quarantine boundary.

## 2026-09-01 - provider adapter freshness check

- Rechecked current official OpenAI, Gemini, xAI, and BFL API documentation/terms before a paid-route decision. The planned OpenAI snapshot, Gemini Interactions endpoint, and xAI JSON edit endpoint remain current. Gemini's paid-service terms remain compatible with fictional controls; BFL's outside-EU API terms still license Inputs/Outputs for service improvement/training, preserving ADR-0019's fictional-control-only boundary.
- The check caught and corrected a BFL preflight defect: G07's regular control and no-change reference have different hashes, so the adapter now requires two separately hash-verified HTTPS control URLs instead of one URL that could only match one request. No request, external upload, account, or spend occurred.

## 2026-09-01 - clean CH05 chapter-scale development option

- Authored a fresh 50-panel `The Mill Signal` planning option from the existing CH04 smoke-column hook, without importing the quarantined Garden's Anchor pilot. It uses only the currently recorded fictional Soren/Sigrid pair and is explicit that it is non-canon, not a ComicPanelPlan, not a render request, and not evidence of art, acceptance, commercial eligibility, or reproducibility.
- The deterministic validator confirms unique stable development IDs and display order 1–50, adult-cast constraints, no historical Dio/Thal panel content, and no AnimationShotPlan. Review source: `research/development/clean-ch05-mill-signal-r1.json`.

## 2026-09-01 - CH05 Mill Signal frontier-art visual smoke

- Generated four separate, original fictional-adult visual probes from non-canon CH05 development panels: departure toward mill (P001), mill entry split roles (P029), practical two-person plank/tin action (P036), and urgent uphill return (P050). All assets, service execution IDs, byte hashes, observed elapsed time (194.1 seconds total), safety classifications, and pending-human-review status are recorded.
- Agent routing triage finds clear two-person roles and intended geography/blocking in all four. This is non-gating only: no model snapshot, seed, or price is exposed, so no candidate is accepted, reproducible, commercially cleared, benchmark-scored, or promoted into current canon/ComicPanelPlan work. Review record: `experiments/reviews/ch05-mill-signal-imagegen-smoke-review-r1.json`.

## 2026-09-01 - CH05 coverage and promotion boundary

- Measured the new development script honestly: 50 planned panels, 4 generated candidates (8%), 0 accepted, 4 awaiting human review, and 46 unrendered. The observed 48.525 seconds/candidate mean is retained only as an observation; no 50-panel forecast is claimed from this small, provenance-limited sample.
- Added an owner-decision template that separates development-script approval from creation of current canon/panel plans, renderer execution, panel acceptance, commercial clearance, and animation-shot direction. This keeps the future promotion path auditable without prematurely creating production records.

## 2026-09-01 - local provider-configuration handoff

- Added root `.env` (blank, local-only, Git-ignored) and `.env.example` (shareable) covering the four executable G07 API adapters, BFL's two separately hash-verified fictional-control URLs, and prospective managed-GPU/frontier candidates. The adapter entrypoints now load the local file without third-party dependencies, never override existing process variables, never print values, and still require `--execute` plus the explicit cap before a paid call.
- Added `.gitignore` before remote setup; no Git repository was initialized or remote contacted. The recommended repository name is `north-garden-visual-narrative-compiler`.

## 2026-09-01 - aggregate bakeoff reservation milestone

- Added a single OS-locked, atomic reserve/hold/reconcile/release ledger used by all four paid adapters. Concurrent validation against a reduced $10 approved cap allowed one competing $6 reservation and denied the other; the successful reservation reconciled to $1.25 and a separate proven-unsubmitted reservation released correctly. Temporary test state ended with $8.75 available. No provider request or real-ledger spend occurred.
- ADR-0023 requires possibly billable failures and unknown costs to remain fully held. Duplicate active/committed adapter-request keys are refused. The frozen gauntlet and `baseline_legacy` were not opened or changed.

## 2026-09-01 - current provider documentation and live readiness gate

- Retrieved current official model, endpoint, pricing, and terms/data-use pages for OpenAI GPT Image 2, Gemini 3.1 Flash Image, Grok Imagine Image 2.0, and BFL FLUX.2 Pro before spend. Hashable HTTP responses and dated source facts are recorded in `provider-primary-documentation-20260901.md`.
- The xAI release changed omitted quality to `auto`; its adapter now pins 1K/medium and converts exact response cost ticks at 10^10 ticks/USD. Other provider costs remain fully reserved until usage/billing reconciliation.
- Conservative ceilings are $0.50 OpenAI, $0.20 Gemini, $0.10 xAI, and $0.25 BFL per request: $4.20 maximum held for all 16 calls against the approved aggregate $100 cap.
- Live preflight found all four credentials without exposing values, revalidated frozen local inputs, enforced the data boundary and empty ledger, and downloaded both configured BFL public controls with exact expected SHA-256 values. State: `READY_NO_PROVIDER_API_REQUEST_NO_LEDGER_WRITE`; external spend remains $0.

## 2026-09-01 - OpenAI pre-submission TLS trust-store incident

- The first OpenAI execution attempt reserved $0.50, then Python's bundled CA validation rejected the locally trusted inspection chain during the TLS handshake (`Basic Constraints of CA cert not marked critical`). No HTTP request, input upload, provider request ID, or charge occurred. The complete local failed RenderRecord preserves adapter/input hashes, elapsed 0.332 seconds, error class, source commit `26a1f5d`, and reservation ID.
- The reservation was explicitly released as proven unsubmitted and reconciled to $0; the real ledger returned to committed $0, held $0, available $100. No evidence was deleted or overwritten.
- Certificate verification remains mandatory. OpenAI, Gemini, and xAI adapters now use the native OS trust store, matching the already validated BFL approach. No TLS check or hostname verification was disabled.

## 2026-09-01 - OpenAI G07 bakeoff execution and cost reconciliation

- OpenAI GPT Image 2 completed all four authorized fictional-control requests in 128.347 seconds total (31.534–32.401 seconds/request). Every RenderRecord preserves the snapshot, endpoint, provider request ID, exact input/output hashes, token usage, source commit/adapter hash, pending-review state, and decision=false.
- Documented token-rate reconciliation is $0.049644, $0.049644, $0.049669, and $0.049664, totaling $0.198621. These are explicitly formula-derived usage estimates pending invoice-level confirmation; no reservation remains held.
- Output hashes are `321b4013…6bc0`, `7e7b29c…1ac0`, `3f9f05b…2906`, and `45b9e858…73c6`. None has been visually accepted or scored.

## 2026-09-01 - Gemini Interactions recovery and first G07 result

- The first Gemini POST completed at the provider in 11.006 seconds, but the adapter initially expected SDK-only `output_image` sugar instead of the REST `steps` schema. The failure RenderRecord retained the interaction ID and full $0.20 reservation; no retry generation was issued.
- The adapter now pins `Api-Revision: 2026-05-20`, parses image blocks from model-output steps, hashes a redacted response summary, and supports official `GET /interactions/{id}` recovery. A fixture test passes. The existing interaction was recovered in 0.863 seconds as JPEG `523d0255…e5e` with 375 input tokens and one 1K image output.
- Documented-rate reconciliation is $0.067188 (375 input tokens at $0.50/M plus $0.067 for the 1K output), explicitly an estimate pending invoice-level confirmation. Aggregate state after five completed generations is $0.265809 committed, $0 held, $99.734191 available; review and acceptance remain pending.

## 2026-09-01 - Gemini G07 completion and xAI hosted-URL failure

- Gemini completed the remaining three requests in 14.067, 11.152, and 9.948 seconds. The arm is now 4/4 with exact candidate hashes and request IDs, 46.173 seconds total provider-generation time, and a $0.268756 documented-rate estimate. Review remains pending.
- xAI's first POST completed in 8.899 seconds and reported an exact billed cost of 700,000,000 ticks ($0.07), but immediate retrieval of the temporary hosted candidate URL returned HTTP 403/code 1010. The paid failure record retains request ID, source/input provenance, exact cost, data-control header, error, and no candidate claim.
- Current official xAI guidance documents `b64_json` as the direct, non-hosted response format and describes URL output as temporary. The adapter now requests validated base64 bytes, hashes the raw provider response, records MIME, and requires an explicit retry ledger suffix for replacement of a paid failed request. No duplicate was issued before that repair passed validation.

## 2026-09-01 - xAI G07 direct-base64 completion

- The explicit replacement for the failed first case and the remaining three planned cases completed with direct base64 output. Required-candidate latency was 9.177, 13.588, 12.491, and 14.769 seconds (50.025 seconds total); exact provider usage was 700,000,000 ticks ($0.07) per request, $0.28 total.
- All four required candidate hashes, raw response hashes, request IDs, pinned 1K/medium parameters, and data-control headers are recorded. The prior $0.07 hosted-URL failure remains separate, bringing xAI experiment spend to $0.35 while renderer review still covers only the four complete candidates.
- Before BFL spend, its adapter was tightened to capture returned credit cost/input/output megapixels, reconcile 1 credit=$0.01 directly, explicitly request PNG, hash submission/poll responses, and run one request ID at a time. This does not alter ADR-0019's public fictional-control-only boundary.

## 2026-09-01 - completed four-provider G07 bakeoff and measured selection

- BFL completed 4/4 in 74.587 seconds at exactly 6 returned credits ($0.06) per request. All four public-control URLs were byte-hash verified immediately before submission; no input beyond the two approved fictional controls was sent.
- The required 16-candidate bakeoff cost is $0.987377; the preserved xAI hosted-URL failure adds $0.07, making aggregate experiment cost $1.057377. The ledger has $0 held and $98.942623 available. Required-candidate operational time is 299.995 seconds; including the paid failure it is 308.894 seconds.
- Deterministic instrumentation verifies all candidate hashes and records independent-repeat, target-change, and no-change full-frame drift. Four review packets remain `PENDING_HUMAN_REVIEW`; human minutes are null and accepted count is zero.
- Non-gating agent triage observes core proxy role/count/order/table/non-contact and target-state success across all 16, while recording xAI's extra central object in 3/4 and BFL/xAI labels. ADR-0025 selects OpenAI for bounded hardening based on cost, structural cleanliness, target/no-change measurements, and provenance—not visual appeal.

## 2026-09-01 - selected-route local targeted-repair hardening r1

- The already-returned OpenAI target candidate was locally resized and composited through a deterministic color-derived rectangular target mask. The mask covers 7.923% of the source; 99.939% of masked pixels change, 71.993% become green-dominant, and exactly 0% outside the mask changes.
- A no-change compiler short circuit returns the input bytes exactly, with identical SHA-256 and no provider request/cost. The rectangular composite has a visible boundary/style seam and is rejected as art; it proves only exterior-preservation mechanics.
- Narrative applicability is linked to approved `ng-ch05-sc01-p036-plan-r1` in the CH05 `ComicPanelPlanCollection`. It records the two-adult practical-action intent and lettering safe zone but performs no CH05 render/upload. `animation_shot_plan` remains null; the missing high-information input is an approved panel-specific base raster and causal hand/plank repair mask.

## 2026-09-01 - CH05 P036 layout conflict and abstract repair control

- The unaccepted P036 smoke raster places the reaching hand/tin within the approved top-right lettering safe zone. A local overlay measures 64.7059% overlap of the non-gating annotated causal region; mask authoring is blocked and no repair mask was emitted.
- A deterministic abstract ComicPanelPlan layout control moves the causal hand/tin/plank relationship outside that zone. It uses exactly two neutral role proxies, a 5.288% target-context mask, and 0% mask/safe-zone overlap. It is not art, accepted, or provider input; external requests/cost remain zero.

## 2026-09-01 - CH05 50-panel production preflight and fail-closed inputs

- Compiled all 50 approved ComicPanelPlans: 18 environment/zero-adult, 15 one-adult, 17 two-adult; motion modes 26 observation, 10 directional, 10 sensory, 4 practical action. Approved base rasters, CH05 production RenderRecords, accepted panels, and human minutes remain 0/0/0/null.
- Selected existing contiguous P033–P038 as a six-panel no-render demonstration slice spanning all four motion modes and the P036 repair contract. Arithmetic-only selected-arm scenarios are $0.297932/192.521 seconds for six and $2.482762/1604.338 seconds for 50; they are not forecasts.
- Added separate base-raster and mask-review templates plus a fail-closed compiler gate. Empty templates produce 11 and 14 rejection reasons. ADR-0026 prohibits local approval from implying external upload; exact provider/model/endpoint authority remains separate.

## 2026-09-01 - CH05 six-panel no-network packet and adversarial input gate

- Compiled P033–P038 into a local packet with 0/6 executable panels, 0 approved bases/masks, 0 RenderRecords/acceptances, 0 uploads/requests, and $0 new external cost. Thirty-six review task instances are declared while all human-minute fields remain null; task counts are not time estimates.
- Verified three source-derived continuity contracts: held two-adult blocking from P033 to P034, sealed-tin acquisition through P035–P037, and creek-map detail from P037 to P038. Source-term checks are compiler evidence, not visual continuity evidence.
- Hardened raster inputs beyond file hashes: supported decodable raster formats, exact declared dimensions, grayscale-PNG masks, and valid nonzero mask fractions are now mandatory. Ten of ten adversarial partial/malformed mutations are rejected.
- Hardened external scope against self-authorization: record provider/model/endpoint fields do not pass unless a separate caller-supplied authority scope matches exactly. Empty templates now fail for 12 base and 16 mask reasons.

## 2026-09-01 - CH05 deterministic sequence layout control

- Built six local abstract layout controls and six story-occupancy masks for P033–P038. Two consecutive builds reproduce all 13 pinned output hashes (six controls, six masks, one contact sheet).
- Planned role-proxy counts match 2/2/0/2/0/0; total role proxies are six. Story geometry occupies exactly zero pixels inside every compiled lettering safe zone.
- Color-token recurrence verifies bell P033–P034, tin P035–P037, and map P037–P038 dependency plumbing. This is not character, acting, style, or visual-continuity evidence; all human minutes remain null and accepted panels remain zero under ADR-0027.
- Provider requests/uploads/cost are 0/0/$0. The controls are not approved bases or authorized provider inputs.

## 2026-09-01 - CH05 hash-chained panel run ledgers

- Added append-only SHA-256 lifecycle ledgers for P033–P038; all six stop at `BASE_APPROVAL_PENDING` because no approved base raster exists. Executable panels, provider requests/uploads, accepted panels, and external cost remain 0/0/0/0/$0; human minutes remain null.
- A synthetic full lifecycle validates base and mask approval, exact external scope, aggregate reservation, submission, RenderRecord plus cost reconciliation, timed hard-assertion review, and acceptance without invoking a provider.
- Eighteen of eighteen adversarial transition, chain-tamper, and aggregate-binding mutations fail. Missing/released/mismatched reservations, adapter/request/cost mismatches, skipped gates, absent RenderRecords, untimed decisions, and failed-assertion acceptance cannot advance.
- ADR-0028 keeps `ComicPanelPlan`, lifecycle ledger, `RenderRecord`, and future `AnimationShotPlan / E-Conte` as distinct records.

## 2026-09-01 - CH05 production-budget domain and local candidate intake

- Added a distinct, disabled `NORTH_GARDEN_CH05_PRODUCTION` policy and ledger. The G07 cap environment alone, a production-cap environment value alone, and substitution of the G07 ledger all fail production preflight. No production cap, adapter, upload, reservation, or spend is authorized.
- A synthetic isolated policy validates aggregate reserve, hold, cost reconciliation, and proven-unsubmitted release. Actual cost above the reservation ceiling fails for incident review; no provider was contacted.
- Local candidate intake decodes and hashes all six deterministic sequence controls against their stable panel revisions. All 6/6 hashes match, while classification remains pending/null, human minutes null, permissions false, and the separate base-approval gate rejects every candidate.
- `.gitignore` now excludes runtime `experiments/` records, candidates, controls, and reviews from accidental staging. Tracked source/evidence remains constrained by the existing scope preflight.

## 2026-09-01 - CH05 candidate review and non-promotion controls

- Built an intake review packet for the six deterministic controls: 6/6 are policy-ineligible under ADR-0027, approved bases/uploads are 0/0, and human minutes remain null.
- Candidate promotion requires exact candidate/raster/panel linkage, completed positive-minute reviewer identity, explicit fictional-adult-only classification, no likeness/child/personal/LoRA material, provenance sufficiency, passing applicable hard assertions, local acceptance, and local repair permission. It categorically refuses external upload authority.
- All six controls remain blocked even with superficially complete fields. A synthetic eligible-raster fixture exercises the field-validation path but is emitted as `SYNTHETIC_VALIDATION_ONLY_NOT_APPROVAL` and fails the real base gate.
- Eight of eight review mutations fail: absent minutes, child material, likeness, hash mismatch, failed assertion, insufficient provenance, attempted external permission, and absent local permission. External requests/uploads/cost remain 0/0/$0.

## 2026-09-01 - CH05 50-panel chapter run manifest

- Compiled all 50 stable panels into initial hash-chained run ledgers with one applicable hard-assertion hash per panel. Every current state is `BASE_APPROVAL_PENDING`; stage denominators retain all 50 planned panels and the P033–P038 slice remains exactly six.
- Pinned chapter root `0498d79f…73664` over ordered panel/plan/assertion/chain-head tuples. It reproduced 30/30 local compiles; chain-head, plan revision, assertion, and panel-order mutations were detected 4/4.
- Local record compilation measured median 9.120 ms, p95 10.178 ms, maximum 11.094 ms, and 1,802,668 bytes peak Python `tracemalloc` allocation across the validation run. These are not provider or human throughput measurements.
- Review structure exposes 250 task instances without inventing duration. Executable/submitted/rendered/reviewed/accepted panels, provider requests/uploads, human minutes, and external cost remain 0/0/0/0/0, 0/0, null, and $0.

## 2026-09-01 - immutable review timing and full-denominator progress

- Added hash-chained START/PAUSE/RESUME/COMPLETE review sessions. A synthetic 25-minute wall interval with a 10-minute pause computes exactly 15 active minutes; validation fixtures remain ineligible as real review evidence. Ten/ten timer, decision, transition, chain, and derived-summary mutations fail.
- Terminal panel decisions now require an exact timed-session digest and matching reviewer, subject, decision, and calculated minutes. The combined run-ledger suite rejects 22/22 transition, tamper, aggregate-budget, and timed-review mutations.
- The real CH05 rollup retains all 50 planned panels: 50 base-pending, 0 submitted/accepted, null measured human minutes, and $0 committed production cost; current root equals the pinned baseline root.
- An isolated synthetic scenario exercises one retry: 2 submitted panels, 3 completed attempts, 1 rejected then retried, 2 current accepted panels, accepted-per-planned 0.04 versus accepted-per-submitted-panel 1.0, 15 fixture-only minutes, and $0.45 fixture-only reconciled cost. Four/four missing-panel/cost/session/plan mutations fail. None enters real evidence.

## 2026-09-01 - selected OpenAI P036 offline submission preflight

- Compiled selected-route prerequisites for exact P036 panel/revision and pinned `gpt-image-2-2026-04-21` `/v1/images/edits`. The real record stops on four independent blockers: approved base, approved repair mask, exact external authority, and distinct CH05 production reservation.
- Real input-package hash, request envelope, and request body remain null. Static inspection confirms no requests/urllib/httpx/openai/socket/aiohttp import and no API-key access; provider requests/uploads/cost are 0/0/$0.
- A complete synthetic prerequisite fixture produces metadata-only envelope state with no request body or network executor. Six/six base-hash, mask-overlap, authority-scope/package, and reservation-domain/package mutations block it.
- Added a consolidated local entry point. Twenty-one of twenty-one offline checks pass in 2.652 seconds, including frozen v2.1.1, runtime, both budgets, input/ledger/review mutations, 50-panel root/progress, selected-route stop, origin URL, and the exact two public-control hashes.

## 2026-09-01 - selected-route submission journal and crash recovery

- Added deterministic idempotency keys over adapter, panel/revision, exact input-package hash, and attempt ordinal plus an append-only submission journal. No network/client executor exists.
- Synthetic pre-submit abort releases its reservation and permits only a consecutively numbered retry that explicitly supersedes it. A synthetic crash after `SUBMISSION_STARTED` enters `OUTCOME_UNKNOWN`, keeps the aggregate reservation held, and blocks both repeat submission and retry.
- Recovery binds the original provider request ID, exact output hashes/timing, cost reconciliation, and RenderRecord reference before terminal completion. Aggregate production ledger domain/reservation/adapter/input/request/cost must match.
- Duplicate idempotency keys and 11/11 transition, chain, reservation state, request ID, and cost mutations fail. Provider requests/uploads/real production cost remain 0/0/$0.

## 2026-09-01 - production RenderRecord and unknown-incident completeness

- Added a targeted comic repair RenderRecord template with exact panel/journal/idempotency/provider/request/input/output/timing/usage/cost/failure/review/acceptance fields. Successful candidates remain pending human review and unaccepted.
- Explicit provider-failure fixtures bind the original request, reconciled cost, and failure record while requiring zero candidate files. Unknown-outcome fixtures use `ProviderSubmissionIncident`, retain the aggregate hold, and categorically require null RenderRecord and no candidates.
- Synthetic success, explicit failure, and unknown incident validate. Twelve/twelve candidate hash/count, request/journal/cost/timing/usage/review, fabricated failure candidates, missing failure, and incident fabrication/release mutations fail.
- No real CH05 RenderRecord, candidate, request, upload, human minute, acceptance, or cost was created.

## 2026-09-01 - G07 local evidence-vault integrity

- Built a tracked non-art manifest over 19/19 provider records, 16/16 candidate rasters, and the two approved public controls. Exact candidate bytes decode and hash-match; vault root is `e84b04029ca14b9a40dbdcd2e6d2937c322bf019df2191d032169e062696d3ab`.
- Reconciled $0.987377 across the 16 required candidates plus the distinct $0.07 xAI paid transport failure: $1.057377 committed, $0 held, $98.942623 available. Gemini recovery is bound to its original interaction/request ID and one charge.
- Five/five cost, record-hash, candidate-hash, review-state, and BFL-input manifest mutations fail. Git tracks zero paths below `experiments/`; generated records and pixels remain local and ignored.
- All 16 candidates remain `not_yet_performed`, null human minutes, false acceptance. Hash completeness adds no visual score, reproducibility claim, commercial clearance, or expanded upload authority.
- Consolidated offline validation now passes 24/24 checks in 3.021 seconds with zero provider calls, uploads, or new cost.

## 2026-09-01 - G07 evidence restoration rehearsal

- Constructed a deterministic local ignored ZIP from the exact vault inventory: one embedded manifest, two approved public controls, 19 provider records, and 16 candidate rasters. All 38/38 members validate directly from the archive without extraction.
- Two consecutive in-memory constructions are byte-identical. The archive is 19,879,277 bytes, SHA-256 `64bea215c1d340684046b951507018fe7d5c657d4a8d04ac99e6d24aca69cad7`.
- Five/five missing, extra, corrupt, path-escaping, and duplicate-member mutations fail. Existing differing archives are not overwritten.
- This is a same-disk restoration rehearsal, not durable off-device backup. Provider calls/uploads/cost are 0/0/$0; review remains unperformed and accepted candidates remain zero under ADR-0037.
- Consolidated offline validation now passes 25/25 checks in 3.230 seconds.

## 2026-09-01 - blinded and timed G07 review protocol

- Re-encoded all 16 candidates into provider-neutral PNG presentations while preserving each source's decoded RGB bytes exactly. Four hidden-arm repeat descriptors pair the two independent requests, giving 20 required decisions.
- The packet excludes provider/model labels, original provider paths, request IDs, and cost. Assignment root is `98a71467…35387`; packet root is `4b1e5f0c…478161`. Presentation blinding is procedural rather than secrecy against source inspection.
- Candidate assertions cover proxy role binding/order/count, shared table/blocking, contact, side effects/text, target-change preservation, and strict no-change observation. Repeat assertions cover count/order/blocking consistency and explicit uncontrolled-variation notation.
- Append-only timer events calculate minutes. Thirteen/thirteen identity leak, reorder, missing coverage, candidate hash, case/pair binding, assertion, manual-minute, and fixture mutations fail.
- No real reviewer/session/decision was created: decisions 0/20, human minutes null, accepted subjects zero. Consolidated offline validation passes 26/26 in 5.326 seconds.

## 2026-09-01 - fail-closed G07 human-review rollup

- Bound all four arms and 16 candidates to the vault plus exact measured required-candidate cost, total/mean latency, independent-repeat drift, target-change drift, and no-change drift.
- The deblinding compiler accepts only a complete eligible exact-packet session whose hidden mapping root derives from the vault. It preserves every assertion, failure tag, candidate decision, and repeat-pair decision by arm.
- Pending evidence deliberately contains no human arm result, composite score, automatic ranking, or selection change. Current state is 0/20 decisions, null human minutes, zero accepted candidates.
- Nine/nine fabricated pending results, metric/hash drift, adapter removal, fixture leakage, incomplete coverage, and mapping mutations fail. Synthetic compilation is explicitly validation-only.
- Consolidated offline validation passes 27/27 checks in 15.658 seconds; the increased local runtime is dominated by repeated neutral-presentation verification, not provider activity.

## 2026-09-01 - selected-route boundary hardening r2

- Compared hard, 2, 4, 8, 16, 24, and 32-pixel inward cosine compositor boundaries on the exact existing OpenAI G07 target candidate. All generated composites/alphas remain ignored local evidence; no provider call or upload occurred.
- The predeclared selection threshold required at least 90% artificial boundary-jump reduction, 99% hard-mask central green retention, exact exterior, and zero P036 lettering overlap. Only 16 pixels qualifies: 91.2633518% reduction, 99.461535% central green, zero exterior changed pixels, zero overlap.
- Wider variants were not assumed better: 24 and 32 pixels fell below the 90% maximum-artificial-jump threshold because the transition crossed stronger internal gradients. The narrowest passing variant is selected for one topology test under ADR-0040.
- Eight/eight input, method, metric, selection, spill, core-signal, lettering, and invented-review mutations fail. Candidate acceptance remains false and human minutes null.
- Consolidated offline validation passes 28/28 checks in 16.458 seconds with $0 additional external cost.

## 2026-09-01 - P036 current-mask topology audit

- Verified that the existing 5.288% P036 target-context mask is one fully filled axis-aligned rectangle (rectangularity 1.0), not an irregular hand/plank/tin mask.
- Applying the selected 16-pixel inward policy retains 65,736 of 83,176 support pixels as fully replaced core (79.0324089%), preserves 1/1 connected component, and produces zero exterior or lettering-zone change in a synthetic compositor check.
- Concavity, holes, multiple components, and thin-feature survival are all untested. The record therefore passes rectangle mechanics but explicitly fails evidence sufficiency for irregular narrative topology under ADR-0041.
- Eight/eight input, policy, topology metric, lettering, overclaim, and invented-review mutations fail. Provider calls/uploads/cost remain 0/0/$0; art acceptance remains false.

## 2026-09-01 - P036 causal-shape topology control r2

- Bound deterministic plank/reach/hand/tin geometry to P036's ComicPanelPlan, `p036_core_read`, repair-readiness target semantics, and sealed-tin continuity contract. The output is explicitly abstract geometry, not a base or approved mask.
- Compared 0/4/8/12/16-pixel context pads under the fixed selected 16-pixel inward boundary. The predeclared rule selects 8 pixels as the narrowest single-core pass.
- Selected measurements: 42.1067208% union fully replaced core, one support/core/nonzero-alpha component, rectangularity 0.215862894, and core retention 45.4680595% plank / 44.4704701% reach / 48.6920039% hand / 38.3841661% tin.
- Concavity and a 42-pixel thin reach are exercised; holes and disconnected support are not. Synthetic compositor exterior difference and lettering overlap are both zero.
- Ten/ten intent, variant, boundary, connectivity, feature, spill, authority, and invented-review mutations fail. Calls/uploads/cost remain 0/0/$0.

## 2026-09-01 - selected-route local repair policy and proxy non-promotion

- Added a versioned `ComicTargetedRepairPolicy` binding P036/`p036_core_read`, the selected OpenAI snapshot/endpoint, 16-pixel inward boundary, 8-pixel causal context, exact-exterior requirement, and byte-identical no-change short circuit.
- The abstract layout base, causal support mask, and inward alpha are all explicitly false for production-base eligibility, production-mask eligibility, and external upload authority.
- Offline preflight binds the policy hash while retaining exactly four real blockers: approved base, approved mask, exact external authority, and distinct CH05 production reservation. It still has no request envelope/body/client/executor.
- A non-fixture attempt to wrap proxy controls as approved inputs is blocked. Synthetic fixture mode remains metadata-only. Eleven/eleven input, policy state/route/proxy/executor, authority, and reservation mutations fail.
- Provider requests/uploads/cost remain 0/0/$0; production policy/cap remains disabled/absent.

## 2026-09-01 - immutable P036 repair readiness r2

- Created `ng-ch05-p036-openai-repair-readiness-r2` as a new record and pinned r1's unchanged SHA-256 `6ea50b94…19ac6`; r1 was not edited.
- R2 binds the exact ComicPanelPlan, selected route, local mechanics policy, boundary/causal evidence, disabled production budget policy, zero production ledger, and current offline preflight.
- Real state remains four blockers with zero eligible proxy bases/masks/uploads and null approved base, mask, authority, reservation, input package, request envelope/body, journal, RenderRecord, candidate, review minutes, and acceptance.
- `ComicPanelPlan` remains the directing record; `AnimationShotPlan` and E-Conte are explicitly null. Eleven/eleven immutability, policy, blocker, input, execution, medium, and invented-review mutations fail.
- Added five zero-cost CH05 hardening milestones to the production cost ledger. It remains disabled with no cap, $0 committed, and $0 held.

## 2026-09-01 - CH05 full-denominator repair-policy coverage

- Classified all 50 approved ComicPanelPlans without inferring any mask. The explicit rule finds four practical-action panels with the exact causal hand/object direction: P019, P026, P036, and P044.
- Only P036 has an exact panel/revision mechanics policy. Three explicit candidates are policy-absent; 46 panels have no explicit plan-level targeted-repair applicability. Absence is not treated as proof that repair can never be needed.
- P036 policy inheritance is prohibited. Motion mode alone neither selects another policy target nor makes a panel executable.
- Approved bases/masks/executable panels/requests/uploads/accepted panels are 0/0/0/0/0/0, human minutes null, and production cost $0 across the 50-panel denominator.
- Ten/ten missing/reordered panel, policy leak, execution, invented input, denominator, target-selection, generalization, and AnimationShotPlan mutations fail.

## 2026-09-01 - next local repair-control information gain

- Compared only the three policy-absent explicit causal panels: P019 hand-signal/bridge blocking, P026 hand/ember/smoke, and P044 hands/blade/taut-twine contact.
- P044 uniquely meets the bounded rule for one local control: explicit sharp geometry, an uncovered sub-32-pixel boundary scale, direct tool contact, and no new renderer/effect mechanism.
- P026 is deferred because smoke separating fingers is a diffuse/translucent boundary question outside the current opaque inward compositor. P019 is deferred because it does not directly test the uncovered boundary scale. Neither is rejected as a panel.
- Selection authorizes only deterministic abstract P044 geometry. Production policy/mask/provider changes and external activity remain false/false/false/zero.
- Eight/eight candidate inventory/order, wrong selection, diffuse-mechanism erasure, missing thin dimension, policy/mask, and external-authority mutations fail.

## 2026-09-01 - P044 fixed 16-pixel boundary stress

- Built one deterministic abstract support from an 18-pixel blade crossing a 12-pixel taut-twine line, clipped away from two protected hand ellipses and bound to P044/`p044_core_read`.
- Applied the selected P036 16-pixel inward boundary unchanged and performed no tuning. The support is one connected component, but both blade and twine retain zero fully replaced core pixels; the union core is empty.
- Positive separation mechanics remain exact: protected-hand overlap 0 pixels, lettering overlap 0 pixels, synthetic compositor exterior difference 0.
- The fixed absolute width is rejected for this fine-feature control under ADR-0047. No P044 production policy/mask or renderer change follows.
- Nine/nine intent, policy, no-tuning, geometry, core, protected separation, overclaim, policy-authoring, and invented-review mutations fail. Calls/uploads/cost remain 0/0/$0.

## 2026-09-01 - P044 adaptive inward-boundary width

- Compared 1/2/3/4/5/6/8/10/12/16 pixels on the exact unchanged stress support. Geometry and support hash were fixed; no widening/redrawing occurred.
- The rule selects the widest width with one core/nonzero-alpha component, at least 15% union/blade/twine core, zero protected-hand/lettering overlap, and exact exterior.
- Five pixels is the widest pass: 18.4960036% union core, 22.9446164% blade core, 18.1701855% twine core. Six pixels is the first larger failure because twine core falls below the threshold.
- Nine/nine support hash, series completeness, geometry, selection, core, exterior, policy/authority, and invented-review mutations fail.
- This is a P044 abstract-control result only. No seam-quality observation, P044 policy, approved mask, provider call, upload, or cost follows.

## 2026-09-01 - scale-aware boundary selector contract

- Encoded six separate gates: exact panel/support binding, topology width ceiling, exact-base visual discontinuity, exterior/no-change, timed human seam review, and production authority.
- P036 remains a 16-pixel local mechanics profile; P044 remains a 5-pixel local topology control. Width inheritance, motion-mode inference, and a universal default are all prohibited.
- Both topology controls pass, but exact approved-panel-base visual-boundary passes are 0, timed seam reviews 0, production-ready profiles 0, and approved production masks 0.
- P036 retains its four production blockers. P044 additionally lacks a panel-specific policy and exact-base boundary evidence.
- Ten/ten missing gate, width swap, fake visual pass, fake production readiness/review, universal width, and generalization mutations fail. Calls/uploads/cost remain 0/0/$0.

## 2026-09-01 - append-only repair boundary evidence contract

- Preserved the existing v2.0 RenderRecord and v1.0 incident validators unchanged. Added v2.1 `comic_targeted_repair_v2` and v1.1 incident templates plus a layered validator.
- A completed fixture binds the exact selector contract, P036/plan revision/16px profile, exact support and inward alpha, topology source, base/candidate visual measurement, zero exterior change, explicit no-change result, and a three-minute identified synthetic seam decision. The ordinary candidate review remains pending.
- An explicit failure binds the known selector/profile/support/alpha/topology inputs but cannot carry visual, exterior, no-change, or seam outcomes. An outcome-unknown incident rejects every such field.
- Fifteen/fifteen selector, cross-panel width, support/alpha/topology hash, visual-base, exterior, no-change, seam timing, failure-fabrication, and unknown-fabrication mutations fail under ADR-0050.
- Consolidated offline validation passes 37/37 checks in 24.757 seconds. The accepted seam is validation-only; real requests/uploads/candidates/RenderRecords/seam reviews/human minutes/production cost remain 0/0/0/0/0/null/$0.

## 2026-09-01 - append-only CH05 cost ledger r2

- A validation run caught that later local milestones had changed the r1 ledger hash pinned by P036 readiness r2. R1 was restored byte-for-byte; the readiness validator passes again.
- New ledger r2 pins r1 and appends three unique zero-cost milestones rather than rewriting prior evidence. The combined ledger has 18 local milestones, zero reservation entries, no cap, zero requests/uploads, $0 committed, and $0 held.
- Eight/eight supersession, rewrite, authority, cap, cost, reservation, request, and summary mutations fail under ADR-0051.

## 2026-09-01 - CH05 repair-evidence readiness matrix

- Compiled all 50 ComicPanelPlans in order against exact applicability, selector, topology, panel policy, approved input, authority, production budget, visual-boundary, exterior/no-change, seam-review, and v2.1 outcome gates.
- Measured coverage is four explicit repair candidates, two local selector/topology profiles, and one panel-specific policy. P036 is the strongest local row but still lacks every production and outcome gate; P044 lacks a policy; P019/P026 lack profiles and policies.
- Approved bases/masks/authorities/reservations/visual results/seam reviews/RenderRecords/candidates/accepted panels are all zero, human minutes null, and production activity 0 requests/0 uploads/$0.
- Thirteen/thirteen denominator, reorder, cross-panel profile, policy leak, width leak, fabricated input/result/review/outcome, invented minutes/selection, and AnimationShotPlan mutations fail under ADR-0052.
- Consolidated offline validation passes 39/39 checks in 25.734 seconds.

## 2026-09-01 - exact-base boundary measurement packet

- Built a deterministic synthetic candidate from the exact P036 abstract base through the exact 16px inward alpha; recorded exact base/candidate/support/alpha/profile/topology hashes and dimensions.
- Measured 64,992 support pixels, 35,150 transition pixels, 27,366 fully replaced core pixels, and exact zero exterior changed pixels/max difference. The candidate reduces mean directed support-to-exterior RGB distance 98.838% relative to the in-memory binary hard reference on this fixture.
- The separate no-change short circuit returns the exact input bytes without provider invocation. A three-view base/candidate/3x-difference crop packet is bound to the exact sources, but review session/decision/minutes remain null and acceptance false.
- Fourteen/fourteen binding, metric, no-change, review, fixture-label, and invented-activity mutations fail under ADR-0053. Provider requests/uploads/cost remain 0/0/$0.
- Consolidated offline validation passes 40/40 checks in 25.418 seconds.

## 2026-09-01 - hash-chained seam-review binding

- Replaced the loose synthetic session summary with the existing immutable `TimedHumanReviewSession` state machine and made the exact tracked measurement packet its sole subject.
- Completed v2.1 validation now loads and hash-checks both the measurement packet and session, validates the event chain, recomputes three active minutes, and requires the same reviewer, subject, accepted decision, and boundary/causality/protected-semantics/lettering-clearance assertions.
- The synthetic session is explicitly a validation fixture and derives `review_evidence_eligible=false`; a real RenderRecord must use a non-fixture eligible session. The ordinary full-candidate review remains separately pending.
- RenderRecord contradiction coverage increases from 15/15 to 18/18 with exact session/evidence hash and reviewer mutations. Real seam sessions/minutes/accepted outcomes remain 0/null/0 under ADR-0054.
- Consolidated offline validation remains 40/40 in 25.977 seconds.

## 2026-09-01 - fail-closed repair outcome finalizer and cost ledger r3

- Added a no-network finalizer that consumes only complete journal/ledger/RenderRecord evidence. Current real P036 reports nine blockers: the four production preflight gates plus real exact-base measurement, eligible seam review, completed journal, candidate, and cost reconciliation.
- Real output fields remain null. Two synthetic validation finalizations produce identical record/journal/ledger digests; changing the fixture flag fails instead of promoting the record.
- Ten/ten missing-blocker, fabricated record/candidate/minutes, fixture promotion, network, invented activity, and AnimationShotPlan mutations fail under ADR-0055.
- Append-only cost ledger r3 pins r2 and records measurement, session binding, and finalizer milestones. It now totals 21 unique zero-cost milestones with no cap, empty reservations, $0 committed, and $0 held; 8/8 ledger mutations fail.
- Consolidated offline validation passes 42/42 in 25.569 seconds; real requests/uploads/cost remain 0/0/$0.

## 2026-09-01 - no-download instrumentation runtime and bootstrap dry run

- Added a separate instrumentation profile to the tracked runtime manifest without changing the frozen `baseline_legacy` profile. It pins Python 3.14.6, Pillow 12.3.0, numpy 2.5.1, the suite entrypoint, and false download/network/credential flags.
- Exact local inventory records CPython/cpython-314 on Windows 11 AMD64, interpreter SHA-256 `03168c01…a0c38`, and exact manifest/bootstrap/suite hashes. Ten/ten runtime/source/dependency/activity mutations fail.
- Bootstrap `-Profile instrumentation -DryRun` creates neither `.env` nor a local manifest and performs no install/download/provider operation. It preserves the existing ignored legacy local manifest and reports four warnings rather than overwriting it.
- The complete dry run passes frozen v2.1.1 and 43/43 offline checks in 26.524 seconds. Provider requests/uploads/cost remain 0/0/$0 under ADR-0056.
- The inventory is a measured local snapshot, not a cross-platform resolver or wheel lock; changes require a new reviewed revision.

## 2026-09-01 - selected-route exact artifact rebuild reproducibility

- Advanced the runtime inventory append-only to r2 because the suite entrypoint hash changed; r1 remains pinned. R2 adds supersession/rewrite mutations for 12/12 total runtime mutations rejected.
- Ran eight local validators twice and inventoried every file in eight bounded ignored groups: layout, boundary variants, mask topology, causal topology, P044 fixed/adaptive, RenderRecord fixture, and measurement presentation.
- Both inventories contain 26 artifacts / 4,862,061 bytes and have identical canonical root `0a04832b6826d6610b39a92fec7e9e7dd311d8d8e9e69fb017366b425d3f3b18`.
- Eight/eight command, count, rebuild-count, root, byte-identity, artifact hash, exclusion, and invented-provider mutations fail under ADR-0057.
- Timestamps, timing samples, provider records/candidates, human decisions/minutes, and external runtimes are excluded, not normalized. Requests/uploads/downloads/cost remain 0/0/0/$0.
- With the two-pass rebuild check included, consolidated validation passes 44/44 in 47.620 seconds.

## 2026-09-01 - G07 review-rollup validator runtime optimization

- Profile inspection found that `compile_rollup` regenerated all 16 neutral presentations and the mapping five times per process: once for the main packet and again for fixture/mutation compiles.
- Main now derives the validated expected mapping root once and supplies it to same-process compiles. Standalone callers without a supplied root retain the full recomputation fallback, and every supplied mapping is still root-compared.
- The pending gate bytes remain SHA-256 `927e76a3…224b78c`; 9/9 pending, fixture, incomplete-coverage, and wrong-mapping mutations still fail.
- Five optimized wall-clock samples are 1705.740/1700.703/1700.121/1708.702/1708.904 ms (median 1705.740), versus the pinned 10614.524 ms baseline: 83.930132% reduction / 6.222826x speedup under ADR-0058.
- Actual review remains 0/20 decisions, null minutes, zero accepted, and no human results/composite/ranking. Provider activity remains 0 requests/0 uploads/$0.
- The complete 44-check suite now passes in 38.687 seconds versus 47.620 seconds immediately before the optimization.

## 2026-09-01 - safe-source pushed release baseline

- Captured already-pushed commit `f5057885b9c953ba102f9b577be229fa42c64ad3` rather than creating a self-referential manifest. Its Git tree is `df2c40bb3efea38e286daf35598799e54bdc5e67`.
- Inventoried all 346 blobs / 8,184,364 bytes with path, mode, byte count, Git object ID, and SHA-256. Canonical inventory root is `2993f2d405c4404b22b93fa69fb520dcde92785ca8c2475bb02293e2a1a52cde`.
- Scope contains exactly the two approved public controls and zero tracked `experiments`, prohibited key/model extensions, or files above 10 MiB. Eight/eight commit/tree/count/root/blob/exclusion mutations fail under ADR-0059.
- `.env`/credentials, generated candidates/review artifacts/runtime records, models/LoRAs/checkpoints/runtimes, datasets/private references, local manifest, and evidence archives remain excluded.

## 2026-09-01 - post-bakeoff aggregate adapter budget audit

- Parsed all four paid adapters and reran their no-network/no-write preflights. Each imports the shared cap and reservation functions, reserves under its exact adapter ID before the paid submission, and contains no adapter-local `$100` literal.
- OpenAI/Gemini release only proven-unsubmitted TLS failures and otherwise hold for later reconciliation. xAI/BFL reconcile exact returned usage where present and hold unknown cost. Gemini interaction recovery reuses the failed record reservation and creates no new generation/reservation.
- Final aggregate ledger has 18 entries: 17 committed, one proven-unsubmitted release, zero held; $1.057377 committed and $98.942623 available. Required candidates are $0.987377 plus the $0.07 xAI failure.
- BFL remains bound to `g07a-control` and `g07a-nochange-reference` with their two approved hashes. Ten/ten cap/order/ledger/BFL/activity mutations fail under ADR-0060. Audit activity is 0 requests/0 uploads/$0.

## 2026-09-01 - provider transport/data-boundary closure and production ledger r4

- Confirmed four HTTPS API endpoints and native trust-store `PROTOCOL_TLS_CLIENT` contexts; every `urlopen` call supplies the verified context and no insecure override token exists.
- Hardened Gemini provider image-URI retrieval and BFL provider polling/sample retrieval to reject non-HTTPS schemes before I/O. Existing BFL public-control HTTPS/hash verification is unchanged.
- All 19 vault records observe only the two published fictional-control hashes. Six prohibited data classes and unapproved adult-likeness upload remain intact; 9/9 transport/input/authority/activity mutations fail under ADR-0061.
- Append-only CH05 production ledger r4 pins r3 and adds bootstrap, rebuild, review optimization, safe source, budget audit, and transport audit. It records 27 unique zero-cost milestones, empty reservations, no cap, $0 committed/held, and 8/8 mutations fail.
- No network request, provider call, upload, or spend occurred.

## 2026-09-01 - selected-route non-promotional hardening state

- Compiled hashes for selection ADR, vault/instrumentation/review/budget/transport, boundary selector/measurement/finalizer, full chapter matrix, exact rebuild, runtime, cost ledger, and safe-source release.
- Preserved the measured OpenAI arm as four candidates / $0.198621 / 128.347 seconds plus separate repeat/target/no-change raster drift dimensions. The engineering selection is not visual acceptance, commercial clearance, or universal superiority.
- Real G07 review remains 0/20 decisions, null minutes, zero accepted, and no human arm result/composite/ranking. Chapter state remains 50 plans / four explicit repair candidates / two profiles / one policy / nine P036 blockers / zero production outcomes/$0.
- Fifteen/fifteen invented acceptance/review/authority/universal width/input/outcome/minutes/budget/AnimationShotPlan and removed-limitation mutations fail under ADR-0062.

## 2026-09-01 - disconnected and protected-hole topology stress

- Fixed a 200px outer/90px inner ring and a separate 32px diagonal component before comparing 2/4/6/8/10/12/16/20px inward boundaries. Geometry is panel-neutral and was not widened or tuned per variant.
- The widest predeclared-rule pass is 8px: exactly two nonzero/core components, 62.915% ring core, and 25.936% thin-component core. Ten pixels is the first larger failure.
- Protected-hole and exterior nonzero alpha are zero, and a synthetic composite changes zero hole/exterior pixels.
- Twelve/twelve geometry, series, selection, component, hole, exterior, policy/profile, invented review, and activity mutations fail under ADR-0063. Provider requests/uploads/cost remain 0/0/$0.

## 2026-09-01 - append-only scale-aware selector r2

- Pinned selector r1 by exact SHA-256 and preserved its two panel profiles unchanged: P036 16px and P044 5px.
- Added the disconnected/hole 8px result only under a panel-neutral mechanics-control collection. Profile, production-policy, and visual-acceptance eligibility are all false.
- Aggregate topology passes are now three, while local panel profiles remain two and universal width, exact-panel visual passes, timed seam reviews, production-ready profiles, masks, requests, and uploads remain zero.
- Thirteen/thirteen supersession, prior rewrite, width leak, generic-control promotion, fake visual/review/production state, and generalization mutations fail under ADR-0064.

## 2026-09-01 - expanded artifact rebuild r2 and production ledger r5

- Pinned rebuild r1 and retained its original 26-file root. R2 appends the disconnected/hole validator and ninth group without changing prior commands, groups, or nondeterministic exclusions.
- Two expanded rebuilds each contain 28 artifacts / nine groups / 4,868,771 bytes and canonical root `18816d3cb4a60161440e8dc5fdb9b0aea628c3d0a688cc39a5eb868d6ce50d64`.
- Ten/ten supersession, rewrite, group/count/root/identity/artifact/activity mutations fail under ADR-0065. Provider calls/uploads/downloads/cost remain 0/0/0/$0.
- Append-only production cost ledger r5 pins r4 and adds hardening state, disconnected/hole stress, selector r2, and rebuild r2. It now records 31 unique zero-cost milestones, no cap, empty reservations, $0 committed/held, and rejects 8/8 mutations.

## 2026-09-01 - aggregate hardening release gate and budget audit r3

- Ran the unchanged 44-check core suite followed by nine named safe-source, budget, transport, state, topology, selector, rebuild, and cost-ledger validators. All 53/53 pass and 8/8 release-gate mutations fail under ADR-0066.
- The tracked local timing observation is 69.752 seconds. It is nondeterministic validation runtime, not provider or human throughput.
- Transport hardening changed Gemini and BFL adapter source hashes after budget audit r2. Preserved r2 and issued append-only r3; 4/4 adapters still reserve through the aggregate ledger before paid submission, 18 entries reconcile to $1.057377 actual/$98.942623 available, and 12/12 mutations fail.
- Production cost ledger r6 pins r5 and records these two local milestones for 33 unique zero-cost milestones. CH05 remains disabled/no-cap, with empty entries and $0 committed/held.
- No network request, provider call, upload, download, or external spend occurred. No human review, art acceptance, production authority, or chapter outcome follows.

## 2026-09-01 - selector r2 consumer compatibility

- Canonically compared selector r1 and r2: all six selection gates and both complete P036/P044 profile objects are byte-equivalent after canonical JSON encoding.
- Validated six direct source consumers and three immutable evidence bindings that intentionally retain exact r1 provenance. Six/six focused validators pass, including the RenderRecord v2.1 boundary-evidence checks.
- The new `disconnected_holed_support` mechanics control resolves to an empty profile, is absent from the profile map, and remains ineligible for panel profile, production policy, and visual acceptance.
- Fifteen/fifteen pipeline/profile/binding/generic-promotion/record-rewrite/activity mutations fail under ADR-0067. Production ledger r7 records 34 zero-cost milestones and remains disabled/no-cap/$0.

## 2026-09-01 - selected-route authority/dependency frontier

- Compiled a 20-node/20-edge acyclic dependency graph over G07 review and selected-route P036 readiness from nine exact source records.
- Separated five root authority items: one identified-human G07 session, exact human-reviewed P036 base and mask, exact user-authorized provider/model/endpoint/input package, and a distinct user-approved CH05 aggregate cap.
- G07 remains 0/20 decisions/null minutes. P036 remains four root preflight blockers and nine total finalization blockers; downstream candidate, cost, measurement, seam review, RenderRecord, and acceptance nodes cannot self-activate.
- Current-primary terms/pricing/data-use refresh is retained immediately before any future paid CH05 execution. G07's $98.942623 remaining capacity is explicitly non-reusable for CH05.
- Eighteen/eighteen graph/authority/activity mutations fail under ADR-0068. Ledger r8 records 35 local zero-cost milestones and remains disabled/no-cap/$0.

## 2026-09-01 - safe-source release r2

- Captured already-pushed commit `43fc787f783236c1c5dae9f4694a6e2a804e0aae`; r2 pins r1's exact manifest/hash rather than rewriting it.
- Inventoried 387 tracked paths / 8,535,516 bytes at Git tree `4e85a8c3f267b9e06dd9f83711882677e375f70b`; canonical inventory root is `53af7d04b36fd02fdff0c35b882ffac88afce72121c846f66c4cf4f84d413d6b`.
- Exactly two approved public controls and zero generated-experiment, prohibited-extension, or over-10-MiB paths are tracked. Thirteen/thirteen mutations fail under ADR-0069.
- Current tracked scope/origin parity pass. Untracked imported assets, launchers, generators, and trainer material remain untouched and excluded. Ledger r9 records 36 zero-cost milestones and remains disabled/no-cap/$0.
