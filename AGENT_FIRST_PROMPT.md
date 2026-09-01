# Long-Horizon Goal — Consistent Webcomic → Future Animation Production System

You are beginning a long-horizon engineering and research project for an AI-assisted serialized webcomic production pipeline that may later support controlled anime/animation production.

This is not a one-shot implementation task. Treat the repository as a persistent multi-month/multi-year research program.

## Read before changing anything

First inspect the entire local repository/workspace.

Then read, in this authority order:

1. Existing reproducible local experiments and working code.
2. Current official model/license/policy documentation when a decision depends on it.
3. `research/authoritative/v2.1.1/README.md`, `research/authoritative/v2.1.1/docs/CORRECTIONS_V2_1.md`, and `research/authoritative/v2.1.1/docs/HANDOFF_CODEX_V2.md`.
4. The rest of the v2.1.1 research package.
5. `research/authoritative/north-garden-pipeline-brief.pdf` as the authoritative historical record of experiments/failures.
6. `research/historical/master-research-architecture-brief.md` only as historical hypotheses; it has been superseded on several architectural points.

Do not silently reconcile contradictions. Record important disagreements or supersessions in an ADR/decision log.

## Long-term objective

Build a durable, model-agnostic production/research system capable of reliably producing serialized **50–90 panel webcomic chapters** with:

- recurring character identity;
- correct multi-character role binding;
- recurring-set continuity;
- explicit canon, timeline, wardrobe, prop and story state;
- deliberate comic composition rather than generic posed images;
- reproducible panel generation;
- panel-addressable revision history;
- targeted repair rather than mandatory full rerolls;
- instrumentation of generation count, compute/API cost and human time;
- systematic benchmark-driven evaluation of new rendering methods;
- no dependency on one image model, one ComfyUI graph, one cloud provider or one identity technique.

Animation is a future production branch. Preserve reusable canon, assets, sets, poses/cameras where useful and provenance, but **do not force comic panels and animation shots into one directing schema**.

Shared layer:

`Canon / Story State → Asset Registry → SceneBeat / NarrativeIntent`

Then branch:

`ComicPanelPlan`

versus eventually:

`AnimationShotPlan / E-Conte`

## Architectural rules already adopted

Treat the following as the present working decisions unless new reproducible evidence overturns them:

- Shared story/canon/assets are cross-media; comic and animation directing records are separate.
- Intent/specification is separate from execution/provenance.
- `RenderRecord` records what actually happened; it is not the same thing as a `ComicPanelPlan`.
- Blender/canonical 3D is a **spatial reference authority**, not necessarily visible final art.
- Every comic panel uses an explicit spatial mode:
  - `grounded`
  - `cheated`
  - `2d_only`
- Comic cheats are legitimate direction and must not automatically be treated as QA failures.
- Recurring sets should ultimately have canonical controllable assets.
- ComfyUI is an execution adapter, not the database or domain architecture.
- Every important render records traceable environment/model/workflow provenance.
- A declared `HardAssertionManifest` exists before rendering and drives QA.
- VLM QA is optional/non-gating until our own measurements justify more authority.
- Published revisions are immutable; corrections create new revisions selected through an edition/publication manifest.
- Stable internal IDs are independent from chapter/display ordering.

## Benchmark

Import the v2.1.1 benchmark **without modifying its frozen semantic intent**.

Current validated values are computed by the package validator:

- 40 renderer cases:
  - 10 Neutral
  - 10 Occlusion
  - 10 Interaction
  - 6 Set
  - 4 VFX
- 10 paired-variant relations.
- Stage A: 12 cases × 2 seeds = 24 renderer generations.
- Stage B: 40 × 3 = 120 renderer generations per finalist.
- 4 derived no-change QA control templates × 3 seeds = 12 control comparisons.
- 8 derived QA error-injection cases.

The semantic benchmark is frozen.

The executable `BenchmarkCaseBundle` is **NOT_YET_FROZEN** because its stage/camera/control assets depend on the first renderer adapter. Follow the package's bootstrapping order:

`semantic freeze → build baseline arm → construct/version BenchmarkCaseBundle v1 → freeze executable harness`

The current `research/authoritative/v2.1.1/bench/gauntlet.json` is the source of truth for benchmark structure and counts.

## Safety / policy constraints

Preserve all project child-safety rules.

No child likeness model, face training, digital double, voice clone, or hosted service receiving child imagery.

A fictional child design and geometry-only staging proxy are permitted, but carry no **real-person likeness/biometric identity data**.

Adult likeness data is sensitive and local by default unless an exact provider/product/plan/endpoint has been reviewed and explicitly approved.

Before using any existing identity tooling, perform a model/license inventory.

In particular:

- inventory and quarantine restricted InsightFace-distributed pretrained weights rather than deleting them;
- mark NoobAI checkpoints `BLOCKED_FROM_COMMERCIAL_PIPELINE` unless a specific checkpoint is independently proven otherwise;
- record exact file hashes and license provenance;
- do not infer license from architecture/family names.

For anything that gates spending, distribution, commercial use, external upload of personal data, or legal/policy boundaries, fetch the **current primary artifact** when possible: LICENSE, model card, policy page, or provider terms.

Evidence tags alone are not enough; currency matters.

## First phase — do this before broad implementation

Do **not** immediately build the full proposed system.

First:

### 1. Repository discovery

Inventory:

- existing source tree;
- current Python code;
- ComfyUI installation and exact version/commit if detectable;
- workflow JSON files;
- custom nodes;
- model/checkpoint files;
- LoRAs and training data references;
- canon code;
- staging/perspective code;
- lettering;
- VFX/effects;
- generated outputs;
- environment/setup assumptions;
- what currently runs successfully;
- what is stale/broken.

Do not delete or rewrite anything during discovery.

### 2. Validate the research package

Run:

`python research/authoritative/v2.1.1/scripts/validate_research_package.py`

Confirm it still produces 0 failures / 0 warnings in the local environment.

### 3. Produce a gap analysis

Compare the current repo with v2.1.1's architecture and experiment plan.

Create:

- `GOAL.md`
- `GAP_ANALYSIS.md`
- `docs/architecture/overview.md`
- an ADR/decision log if one does not exist.

Keep these concise and tied to actual repository evidence.

### 4. Establish the baseline renderer arm

Wrap the existing working pipeline as `baseline_legacy`.

Do not improve it yet.

The objective is reproducibility and measurement.

Record at minimum:

- input state;
- workflow;
- seed;
- model hashes;
- LoRA hashes;
- relevant custom-node versions;
- Comfy commit;
- Python/PyTorch/CUDA/runtime;
- generated candidates;
- accepted output;
- generation time;
- human intervention;
- human minutes.

### 5. Run the Stage-A smoke benchmark through the baseline

Do not optimize results.

We need the baseline failure profile.

### 6. Ship real narrative material in the same cycle

Produce at least **one accepted, instrumented real page or meaningful panel sequence** using the best currently functioning legacy workflow.

This is required.

A cycle containing only architecture/tooling work is incomplete.

### 7. Only then propose the next experiment

Likely early candidates include:

- Illustrious XL v2 with newly trained adult character LoRAs and native ComfyUI masked-LoRA hooks;
- Qwen-Image-Edit-2511 multi-reference;
- sequential per-character inpainting;
- Blender-grounded variants.

But do not automatically download or install all of them.

Rank experiments by **expected information gain / effort / cost** after seeing the baseline failures.

## Long-running operating mode

Work autonomously when the next action is supported by local evidence.

Stop and ask me when:

- meaningful paid expenditure is required;
- a very large model download is required and there are multiple plausible choices;
- uploading sensitive adult identity/reference material to an external service is proposed;
- destructive repository/model changes are proposed;
- important architectural evidence conflicts;
- a legal/license/policy decision remains genuinely ambiguous.

Otherwise continue the goal.

Maintain a living:

- experiment log;
- decision log;
- model/license registry;
- benchmark result history;
- production-time/cost measurements;
- next-experiment queue.

## Research philosophy

Do not optimize for pretty one-off images.

Optimize for:

- accepted-panel rate;
- multi-character correctness;
- set/canon continuity;
- repairability;
- human minutes per accepted production-quality panel;
- the difficult long tail;
- chapter-level sustainability.

Do not rewrite solved tooling unnecessarily.

Paid tools, cloud GPUs, commercial assets, subscriptions, APIs and specialist software are allowed when they materially reduce project risk or human effort. Local 24 GB VRAM is **not** an architectural ceiling.

## First response

Before modifying files, give me a short discovery plan describing:

1. what directories/files you will inspect;
2. how you will determine what is currently reproducible;
3. what you expect to create during Phase 1;
4. anything obviously missing from the workspace that prevents beginning.

Then begin inspection unless a genuine blocker exists.
