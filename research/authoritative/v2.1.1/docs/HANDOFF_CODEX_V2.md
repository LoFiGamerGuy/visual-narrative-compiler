# Conflict-resolution order (canonical — v2.1.1)

*This supersedes the numbered list later in this document, which placed the v2 research package above the handoff corrections.*

1. Reproducible LOCAL_EXPERIMENT evidence and existing working code
2. Current official licence/policy/model documentation
3. `docs/CORRECTIONS_V2_1.md` and the owner's handoff corrections
4. The v2 research package and its cited evidence
5. The older Master Brief's hypotheses

**Do not silently reconcile conflicts. Record them in an ADR.**

> ⚠️ Several specifics below are corrected in `docs/CORRECTIONS_V2_1.md`: the 40-shot wording, the
> "mirrored L/R pairs" language, ToonComposer's licence, GlobalComix's monetization policy, and the
> animation gate. Where they differ, the corrections win.

---

# Fresh Codex Handoff Prompt v2
## Incorporating Visual Narrative Compiler Research v2 + independent verification

You are starting a fresh long-horizon engineering/research session for an AI-assisted serialized webcomic pipeline that may later support controlled animation/anime.

You are NOT starting from a blank slate and you are NOT being asked to implement the architecture in the older Master Brief literally.

## Inputs to read first

Read all of these before changing the repository:

1. The original **North Garden Pipeline Brief — Eight Months of Wrong Turns**.
   - Treat it as the authoritative record of local experiments, failures, constraints, and working artifacts.
   - Do not treat its proposed fixes as final architecture.

2. The earlier **Master Research & Architecture Brief: A Model-Agnostic Pipeline for Consistent Webcomics -> Storyboards -> Anime**.
   - Treat it as a hypothesis document that triggered the next research round.
   - Several recommendations have now been corrected below.

3. The original research agent's **Visual Narrative Compiler Research v2** package:
   - `RESEARCH_BRIEF_V2`
   - `ARCHITECTURE_V0_1`
   - `DECISION_LOG`
   - `EXPERIMENT_BACKLOG`
   - `NEXT_ACTIONS`
   - `CONTINUITY_GAUNTLET` + `gauntlet.json`
   - `CANDIDATE_REGISTRY` + `candidates.json`
   - `POLICY_LICENSE_REGISTRY`
   - the summary of record

4. Inspect the existing local repository/workspace completely before modifying it.
   Inventory code, ComfyUI workflows, model/checkpoint files, trained LoRAs, canon/staging/lettering/effects code, asset files, implicit state, environment assumptions, and what still reproduces.

## Authority / conflict rule

When documents disagree, use this order:

1. Reproducible LOCAL_EXPERIMENT evidence and existing working code.
2. Current official license/policy/model documentation.
3. The v2 research package and its cited evidence.
4. This handoff's architectural corrections.
5. The older Master Brief's hypotheses.

Do not silently reconcile conflicts. Record them in an ADR/decision log.

---

# Goal

Build a durable, model-agnostic production and research system whose near-term production target is:

- reliable serialized webcomic chapters of roughly 50–90 panels;
- recurring character identity and role binding;
- recurring set continuity;
- explicit canon/timeline/wardrobe/prop state;
- panel-addressable revision and reproducibility;
- targeted repair rather than blind full-panel rerolling;
- instrumentation of candidates-per-acceptance, compute/API spend, and human minutes;
- no architectural dependency on one model, one Comfy graph, one cloud vendor, or one identity technique.

Animation/anime is a future production branch, but the static architecture should preserve reusable story state, assets, spatial data, performances/poses where useful, and provenance.

## Critical correction: do NOT force one ShotIR across comics and animation

The common reusable layer should be **story/canon/assets/scene intent**, not a universal directed shot record.

Use a structure along these lines:

`Story/Canon + Asset Registry`
→ `SceneBeat / NarrativeIntent`
→ **comic branch:** `ComicPanelPlan`
→ **animation branch later:** `AnimationShotPlan / E-Conte`

A comic panel and an animation shot have different directing semantics.

`ComicPanelPlan` may contain panel framing, crop, scroll/page rhythm, balloon-safe zones, intentional perspective cheats, expression/action beat, and spatial guidance.

`AnimationShotPlan` may later contain duration/timing, camera trajectory, key poses, performance/motion, cuts, lip-sync/audio timing, and temporal continuity.

Do not put animation-only fields such as `duration_frames` into comic records as permanently-null baggage.

Accepted comic panels may later become visual references/keyframes, but do not assume comic directing itself transfers one-to-one to anime directing.

---

# Critical correction: split intent/specification from execution/provenance

Do not overload "ShotIR" or any one record with both what the artist intends and what the renderer happened to do.

At minimum separate:

- `SceneBeat` / `NarrativeIntent`
- `ComicPanelPlan`
- `HardAssertionManifest`
- `SpatialStageSpec` / `StageManifest`
- `RenderProfile`
- `RenderRequest`
- `RenderRecord` / `RenderAttempt`
- `QAMeasurement`
- `FailureTag`
- `RepairRecord`
- `AcceptedPanelAsset`
- `Revision`

Derive v0 schemas empirically from:
1. the existing working renderer;
2. the original failure log;
3. the v2 40-shot gauntlet.

Keep the initial schemas narrow and versioned. Do not invent a giant studio ontology before it is required.

---

# Blender / 3D role

Keep canonical 3D strongly, but narrow its authority.

Blender is the **spatial reference authority** for shots that need it. It should own or provide:

- canonical room/set geometry;
- camera pose / lens / framing reference;
- major object locations;
- character height and scale;
- blocking;
- depth ordering;
- occlusion;
- contact points;
- optional pose/skeleton guides;
- depth / normals / segmentation / silhouette / line guides.

Blender should NOT be assumed to own final surface appearance or final art detail.

Support explicit spatial modes such as:

- `grounded` — generated image should substantially respect the canonical 3D scene;
- `cheated` — comic-directed intentional violation/foreshortening/impossible eyeline is allowed and recorded;
- `2d_only` — 3D is unnecessary for this panel.

Do not mistake a comic's intentional spatial cheat for a QA failure.

For recurring sets, prefer clean curated/rebuilt canonical geometry. World-model/3DGS/AI-generated meshes may help bootstrap or reference a set, but should not automatically become the production source of truth without cleanup/validation.

---

# Immediate compliance and provenance audit

Before adding more identity tooling, inventory the machine/repository for model weights and licenses.

## InsightFace

The InsightFace source code is MIT, but InsightFace-provided public pretrained model weights such as `buffalo_l` and `antelopev2` are restricted to non-commercial research unless separately licensed.

Inspect likely locations, including ComfyUI model directories.

Do NOT destructively delete discovered weights. Instead:
- identify file/hash/source;
- mark license state;
- quarantine/block them from the commercial production profile;
- note which nodes depend on them;
- evaluate AuraFace/DINO-family or another commercially usable replacement;
- optionally record the path for obtaining a commercial InsightFace license if it materially outperforms alternatives.

Do not say "SCRFD" or "RetinaFace" as architectures are categorically noncommercial; license status belongs to the exact weight/package.

Official source:
https://github.com/deepinsight/insightface

## NoobAI

Treat the current NoobAI checkpoints as **BLOCKED_FROM_COMMERCIAL_PIPELINE** unless a specific checkpoint's license is independently proven otherwise.

The currently surfaced NoobAI model cards contain an explicit commercial prohibition covering model, derivatives, and model-generated products. This is a simpler and stronger reason than relying only on a subtle FAIPL derivative-model argument.

Do not train production character LoRAs from those checkpoints.

Example source:
https://huggingface.co/Laxhar/noobai-XL-1.0

## Illustrious XL v2

Illustrious XL v2.0 currently identifies its license as CreativeML Open RAIL-M. Keep it as a serious commercial-pipeline candidate subject to normal license-record review.

Source:
https://huggingface.co/OnomaAIResearch/Illustrious-XL-v2.0

## External real-person source photos

Treat consenting adult likeness source photos as sensitive.

Default rule: keep them local unless the exact provider + product + plan + endpoint has been reviewed and approved.

Do not record vendor-level statements such as "FLUX trains on inputs" without plan/endpoint scope:
- Black Forest Labs' current general Website/Playground terms grant broad input/output training rights by default with a prospective opt-out, while separate Developer Terms/order forms may govern specific endpoints.
- Gemini unpaid services/AI Studio/unpaid API quota may use content for product improvement and human reviewers may process it; do not submit personal/sensitive information there.

Registry policy fields should include:
- provider
- product
- plan/tier
- endpoint
- effective date
- source URL
- training default
- opt-out
- human review
- retention
- likeness/consent rules
- commercial output rights
- allowed_for_sensitive_adult_reference: yes/no/conditional
- reviewer notes

---

# ComfyUI role

Keep ComfyUI as an execution adapter, not the source of truth.

- Pin the exact ComfyUI commit/hash for benchmark runs.
- Keep one stable programmatic adapter surface.
- Workflows/configs are versioned artifacts.
- Domain state must not live only in node-graph JSON.

Important correction: ComfyUI core has supported **native masked LoRA/model weights via hooks since 2024-12-02**. Do not assume Impact Pack is required for per-region LoRA.

Official source:
https://blog.comfy.org/p/masking-and-scheduling-lora-and-model-weights

This establishes mechanism availability, not production quality. It still must pass the gauntlet.

---

# Benchmark: adopt the v2 40-shot continuity gauntlet

Use the research agent's frozen 40-shot gauntlet as the main benchmark, preserving its IDs and assertions.

Important properties to keep:
- 30 character-facing shots;
- 6 set-continuity shots;
- 4 VFX/expression shots;
- Neutral / Occlusion / Interaction strata;
- 12 mirrored left/right pairs;
- Correct / Blend / Swap mutually exclusive identity-binding classification;
- candidate acceptance count;
- human minutes;
- 3 seeds for full finalist evaluation.

Do not immediately spend 120 generations on every discovered candidate.

Implement a two-stage evaluation protocol:

**Stage A — smoke elimination**
- representative 8–12-shot subset;
- include Interaction, Occlusion, and mirrored L/R examples;
- 1–2 seeds;
- reject obviously noncompetitive or operationally impractical methods.

**Stage B — full gauntlet**
- only serious finalists;
- all 40 shots;
- 3 seeds = 120 generations/arm;
- complete human-time and cost instrumentation.

Do not change the frozen benchmark to make a candidate look better. Add new benchmark versions instead.

---

# First renderer experiment order

Do not spend a month on renderer engineering before instrumentation exists, but also do not wait for a huge abstract schema before generating useful pages.

Start from a working measured baseline and proceed approximately in this order:

1. `baseline_legacy`
   - wrap the existing current pipeline without improving it;
   - make it reproducible;
   - run the smoke subset;
   - use it to ship at least one instrumented production page/panel sequence.

2. `illustrious_v2_masked_lora_core`
   - Illustrious XL v2;
   - existing character LoRAs retrained only if required for the correct base;
   - ComfyUI core masked LoRA/hooks;
   - same prompts/stage inputs where possible.

3. `qwen_image_edit_2511_multi_reference`
   - Apache-2.0 model;
   - explicitly benchmark the two-person/group-fusion capability;
   - judge role binding, identity blending, interaction, editability, and style economics rather than marketing examples.

Official source:
https://huggingface.co/Qwen/Qwen-Image-Edit-2511

4. `sequential_inpaint_per_character`
   - generate/stage shared scene;
   - add/repair one character at a time with only the relevant identity conditioning;
   - measure accumulated collateral damage.

5. `blender_grounded_renderer_variant`
   - use depth/pose/segmentation/camera guides from one canonical set;
   - compare against the same scene without 3D grounding.

Additional XVerse/USO/DiffSensei/etc. candidates belong in the registry and can enter the smoke funnel when reproducible and license-compatible; do not turn discovery into indiscriminate model downloading.

---

# QA and drift detection: manifest first, VLM optional

The v2 research is correct that **declared state before generation** is foundational.

Every `ComicPanelPlan` should resolve a machine-readable `HardAssertionManifest` before rendering, e.g.:
- exact characters present;
- identity-to-role assignment;
- wardrobe version;
- required/forbidden props;
- important object ownership/contact;
- left/right/foreground/background relationships when materially required;
- set and era;
- state-changing story facts;
- required power/VFX state.

QA should compare outputs against explicit assertions rather than ask a model open-endedly to "find inconsistencies."

Build the QA interface early, but do not make a VLM a gate.

Preferred order:
1. deterministic/state checks;
2. geometry/segmentation/pose checks where ground truth exists;
3. commercially licensed embedding/feature checks where empirically useful;
4. narrow closed-form VLM checks against declared assertions;
5. human acceptance.

For VLM experiments:
- include no-change/control cases;
- use neutral wording;
- measure recall AND false-alarm rate;
- test illustrated/comic data, not only photographic thresholds;
- never let a VLM alone approve/reject production until this project's own benchmark justifies it.

External evidence shows VLMs remain weak at fine-grained open-ended difference detection, but this does NOT prove they are useless for constrained semantic checks:
- DiffSpot: best model detected only ~40.7% of true web-UI changes and explicitly uses no-diff controls.
  https://arxiv.org/abs/2605.29615
- M^3-Verse reports a large human-model gap on state/difference understanding.

Do not repeat the claim that models "lose 12 points when asked leading questions" as established fact. The reported ~12.32-point result in M^3-Verse concerns hallucination-centric vs factual question performance; it is not a generic leading-question penalty. DiffSpot separately supports the qualitative concern that wording which asserts a difference can prime hallucinations.

---

# Publication / monetization policy correction

Do not copy the v2 summary's statement that GlobalComix bars all AI-assisted work from monetization.

Current GlobalComix policy (last updated 2026-03-20):
- removes fully AI-generated works;
- allows AI as part of a broader workflow with human artistry, rights, and disclosure;
- explicitly states qualifying AI-assisted human-artistry content **can be monetized**;
- GlobalComix retains discretion over whether a work has sufficient original human artistry.

Source:
https://globalcomix.com/ai-policy

Our exact workflow may sit near a policy boundary because generative models can produce substantial visible art. Record GlobalComix as **CONDITIONAL / SEEK WRITTEN PRECLEARANCE**, not as automatically allowed or automatically barred.

Tapas' current official guidelines say AI-generated content is not allowed:
https://help.tapas.io/hc/en-us/articles/115005323707-Content-and-Community-Guidelines

Patreon currently permits AI-generated works subject to its content-category rules and is a viable owned-audience/monetization option, but "best platform" is a business recommendation, not a factual license conclusion.

Do not make the production architecture depend on any single distribution platform.

---

# Child-safety boundary

Preserve the existing non-negotiable rule:
- no child reference-photo training;
- no child identity/likeness LoRA;
- no digital-double workflow based on a child's face;
- no child voice cloning;
- no hosted mocap/3D/animation service receiving child imagery by default.

For the child character, use an original fictional design rather than a real-person likeness.

A geometry-only child proxy for blocking is allowed within this project rule because it carries body position/scale but no identity reference.

Runway's current policy adds a product-specific corroboration: its Characters & Game Worlds products prohibit characters based on the face or voice of a person under 18. Do not overgeneralize that exact clause to every Runway product, but keep our stricter project rule regardless.

Source:
https://runway.com/safety/usage-policy

---

# Animation strategy correction

Do NOT hard-code "animation deferred for 12 months."

Also do NOT use "must fit in <=24 GB" as a strategic gate. Cloud 48/80+ GB GPUs and paid tooling are allowed when useful.

Instead:

- **Defer animation productionization** until the static pipeline ships an instrumented full chapter.
- Keep a small parallel **animation research/horizon lane** so static decisions do not accidentally block future rigs, pose data, cameras, or asset reuse.
- Run occasional cloud experiments when they answer an upstream architectural question.
- Revisit current candidates quarterly.

ToonComposer is especially relevant to sparse-keyframe/post-keyframing research:
- official README: ~57 GB VRAM for a 61-frame 480p generation;
- its official LICENSE states the publicly released inference code, parameters, and weights are MIT, with listed third-party components under their own licenses.

Sources:
https://github.com/TencentARC/ToonComposer
https://github.com/TencentARC/ToonComposer/blob/main/LICENSE

Therefore "ToonComposer license unverified" is outdated as a blanket statement. Still audit all third-party dependencies/base-model terms before production use.

The Sora API is being discontinued on 2026-09-24 and should not be an architectural dependency.

---

# Governance: every cycle ships pages

Adopt the v2 rule:

> A research/engineering cycle that produces only infrastructure has failed.

Interpret this pragmatically:
- foundational work is allowed;
- but every cycle must also push the current pipeline through real narrative material and produce at least one accepted/instrumented page or meaningful panel sequence;
- those outputs become the production dataset and expose real bottlenecks.

Do not wait for a "perfect pipeline" before making the story.

Instrumentation must capture:
- generation count;
- candidates rejected/accepted;
- GPU/API time and cost;
- human intervention;
- repair attempts;
- human minutes;
- failure tags;
- exact model/workflow/config/seed/asset hashes;
- accepted artifact and revision lineage.

The first complete instrumented chapter is a research deliverable, not merely a content milestone.

---

# First-session deliverables

After repository discovery, create or update only the minimum scaffolding needed to run the first measured cycle:

- `GAP_ANALYSIS.md`
- `GOAL.md`
- `docs/architecture/overview.md`
- ADR recording the **common SceneBeat + separate ComicPanelPlan / AnimationShotPlan** decision
- versioned schemas for the comic/static path and RenderRecord split
- exact import of v2 `gauntlet.json` without changing its IDs
- smoke-test subset manifest
- compliance/model-weight inventory
- candidate registry with license/status gates
- renderer adapter for `baseline_legacy`
- minimal Blender stage adapter/scaffold
- instrumentation/provenance store
- one instrumented real production panel sequence/page produced using the baseline

Do not build:
- a full studio asset-management platform;
- a generalized animation pipeline;
- a VLM autonomous continuity gate;
- dozens of renderer adapters;
- a polished UI before the experiment loop works.

---

# End-of-session report

Return:

1. what exists in the repository and what actually reproduces;
2. files/weights with license or policy risk;
3. files changed/created and commits;
4. the exact v0 static data flow;
5. any disagreement with the v2 research package or this handoff;
6. results of the baseline smoke run / page-producing cycle;
7. the next three experiments with expected information gain;
8. any user approval needed for:
   - large downloads,
   - cloud GPU spend,
   - subscriptions/assets,
   - external upload of sensitive adult reference material.

The governing objective is not to crown a model. It is to build a production/research loop that keeps shipping pages while systematically reducing the human time and failure rate required to obtain consistent accepted panels.
