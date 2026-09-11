# Ember Lattice premium R&D: research, route audit, and citations

**Audit date:** 2026-09-04
**Scope:** premium, commercially intended, original vertical-scroll action-manhwa production for *Ember Lattice*.
**Method:** official/primary technical documentation plus read-only inspection of the current machine and repository. No package or model was installed or downloaded, no paid endpoint was called, no credentials were requested or exposed, no generation was queued in the protected worktree, and direct external spend was **$0**.

This is a technical and production audit, not legal advice. A model card or repository license is evidence about a publisher's stated terms; it is not a chain-of-title opinion for every training input, dependency, adapter, font, reference image, or generated output.

## Determination

The strongest available architecture is **hybrid and layered**, not one monolithic generator:

1. Use the session's built-in OpenAI image-generation/edit route for fresh, isolated character/environment references and the strongest text-free source-art candidates. It is callable now and does not require a user-supplied API key, local install, or local VRAM. It supports image-conditioned edits, but its actual backend identity, snapshot, seed, request ID, metered price, and product-entitlement accounting are not exposed by the tool contract. Therefore its reproducibility is provenance-and-reference based, not bit-exact.
2. Keep characters, equipment, camera intent, action vectors, negative space, and lighting encoded in structured panel records. Use fresh Ember Lattice references only. Never reuse the two existing unrelated LoRAs or any prior-worktree image as a character reference.
3. Use localized image editing/inpainting for defects rather than repeatedly regenerating an otherwise good panel. Preserve an untouched source and log every edited region and edit instruction.
4. Add dialogue, captions, SFX, system cards, borders, accessibility metadata, and publication slicing as deterministic SVG/HTML/Pillow layers. This route is installed, auditable, cheap, and reversible.
5. Treat the detected local ComfyUI routes as **research candidates**, not as cleared production routes yet. They are technically strong and fit the available RTX 5090 Laptop GPU, but the live runtime and outputs are rooted in the protected original checkout. In addition, the exact local FLUX VAE has conflicting/non-commercial provenance metadata, and the full SDXL checkpoint/adapter/LoRA chain has not been commercially cleared. No protected-runtime job was queued.
6. Do not block the premium chapter on Blender, direct Diffusers, automatic pose/depth/line-art extractors, or LoRA training. Blender and Diffusers are not installed; the custom preprocessor nodes are registered but their annotator weights are absent; and there is no fresh, consented Ember Lattice training set. These are future controlled experiments, not present-tense production dependencies.

This recommendation is a pre-bakeoff route decision. The 24-case benchmark must still choose the winning **art route** empirically. A candidate does not pass merely because its median score is high: the weakest cases and the hard failures (identity, anatomy, action geography/contact, safe composition) control.

## Route decision matrix

| Route | Current state | Best use | Reproducibility | Direct marginal cost observed | Production disposition |
|---|---|---|---|---:|---|
| Built-in OpenAI image generation/editing | Callable in this session | Fresh references, text-free panels, targeted edits, multi-reference attempts | Low-to-medium: prompts, inputs, hashes, and lineage can be pinned; backend/snapshot/seed are not exposed | $0 during this audit; entitlement accounting unknown | **Primary candidate; benchmark now** |
| OpenAI GPT-Image-2 API | SDK present; no API credential found in environment-name audit; no call made | Automatable generations/edits, pinned API snapshot | Medium: a dated snapshot exists; no documented image seed was found | Current list prices apply; free tier unsupported | **Blocked by credential and spend authority** |
| BFL hosted FLUX.2 API | No BFL credential found; no call made | Fast paid FLUX.2 Klein, Pro/Max/Flex editing and multi-reference | Medium: use non-preview endpoint, save endpoint/model/input/output metadata; stochastic | From $0.014/image for Klein 4B | **Blocked by credential and spend authority** |
| Local ComfyUI + FLUX.2 Klein 4B FP8 | Installed and live only under protected original checkout | Fast local plates, up to four-reference experiments, seed-controlled iteration | High if runtime/model/workflow/seed are frozen; not guaranteed cross-version/hardware | $0 endpoint cost; local compute/time | **Technically viable, legally and operationally gated** |
| Local ComfyUI + Illustrious XL v2 + union ControlNet/IP-Adapter | Installed and live only under protected original checkout | Anime-styled controlled plates, Canny guidance, reference conditioning, repair | High with frozen graph/models/seed; adapter/preprocessor variation matters | $0 endpoint cost; local compute/time | **Internal R&D only pending full chain audit and isolation** |
| Direct Python Diffusers | Package absent globally and in Comfy venv | Scriptable FLUX/ControlNet/IP-Adapter experiments | Potentially high with pinned stack/generators | $0 endpoint cost; local compute/time | **Unavailable without install** |
| Pose/depth/line-art preprocessing | Node definitions present; required annotator weights absent | Structural control maps | Deterministic-to-high once model/version/input pinned | Would require download/install | **Unavailable offline under this task**; Canny is ready |
| Blender 2D/3D staging | Blender executable absent | Perspective/layout proxy, depth/normal/object passes | High with pinned `.blend`, Blender version, camera, render settings | $0 license fee; labor/compute | **Unavailable without install** |
| Character/style LoRA training | Experimental trainer node exists; fresh dataset/base route absent | Later identity/style adapter from owned material | Medium-to-high if data/order/config/seed/runtime pinned | Local compute; data/QA labor | **Not ready; defer** |
| Local inpainting/masked repair | Crop/stitch, masking, and model nodes detected | Hands, props, seam/contact, face, background cleanup | Medium-to-high with saved mask/workflow/seed | $0 endpoint cost; local compute/time | **Candidate after isolated runtime and model-chain clearance** |
| Deterministic SVG/HTML/Pillow compositing | Ready in repository and global environment | Lettering, UI, balloons, captions, SFX, safe zones, proof sheets | High for SVG/source hashes; raster pixels require renderer pin | $0 | **Production-ready** |
| Automated visual evaluation | Pillow/numpy ready; CV/identity/pose weights absent; scikit-image only in protected venv | Mechanical triage and regression checks | High for explicit metrics; semantic accuracy limited | $0 | **Use for triage, never as anatomy/identity approval** |
| Story/episode development and ledgers | Ready as structured local authoring | season spine, hooks, reveal/economy/injury/location ledgers | High | $0 | **Production-ready** |

## Read-only environment audit

### Hardware and base runtime

- Windows workspace target: `C:\AgentWorkspaces\anime-pipeline-ember-lattice-premium-rd-20260904-150943`.
- GPU: NVIDIA GeForce RTX 5090 Laptop GPU; driver `616.56`; compute capability `12.0`; `24,463 MiB` reported VRAM (`22,654 MiB` free at the observation).
- Global Python: `3.14.6`; Node: `24.19.0`; npm: `11.17.0`.
- Global image-related Python packages observed: Pillow `12.3.0`, NumPy `2.5.1`, OpenAI Python SDK `1.109.1`, ONNX Runtime `1.28.0`.
- Not observed in the global Python environment: PyTorch, Diffusers, OpenCV, MediaPipe, or scikit-image.
- Installed browsers: Microsoft Edge `152.0.4191.62` and Google Chrome `151.0.7922.174`.
- No repository `.ttf` or `.otf` was found. Current SVG output requests Arial without embedding it; this is a portability and exact-render reproducibility risk.
- No `blender`, `comfyui`, `ffmpeg`, or ImageMagick command was found on `PATH`. No Blender installation was found in the common program directory or uninstall registry inspected.
- No relevant credential variable name was returned by a read-only environment-name search. That observation is deliberately narrow: it does not prove that a credential could not exist in an external secret store, signed-in product session, or uninspected profile.

### Protected local ComfyUI installation

A GET-only inspection found a live service at `http://127.0.0.1:8188` in the protected original checkout, `C:\AgentWorkspaces\anime-pipeline\ComfyUI`. The audit queried `/system_stats` and `/object_info`; it did not submit a prompt, upload a file, mutate the queue, or write an output.

- ComfyUI `0.33.0`, git commit `82f839f5e737d8bfce480872ba05e5a430f2526f`.
- Frontend `1.49.6`; workflow templates `0.11.44`.
- Python `3.14.6`; PyTorch `2.12.0.dev20260408+cu128`; local-git deployment.
- Reported device is the RTX 5090 Laptop GPU with approximately 25.6 GB physical VRAM.
- The protected Comfy venv includes NumPy `2.5.2`, OpenCV headless `5.0.0.93`, Pillow `12.3.0`, safetensors `0.8.0`, scikit-image `0.26.0`, segment-anything `1.0`, nightly PyTorch/torchvision, and Transformers `5.15.1`; Diffusers, MediaPipe, Ultralytics, and InsightFace packages were not observed in the inspected package list.
- Registered workflows/nodes include standard and advanced ControlNet, OpenPose, several depth preprocessors, line-art/anime-line-art preprocessors, native Canny, IP-Adapter variants, masking, Inpaint Crop & Stitch, KSampler, FLUX helpers, an experimental FLUX multi-reference latent method, and an experimental LoRA trainer.
- No local annotator weight was found for the registered pose/depth/line-art preprocessors. Those nodes are present but are not offline-ready; invoking them would be expected to fetch a model. No such invocation was made. Native Canny requires no learned annotator and is the one verified ready structural preprocessor.
- No GroundingDINO, DINO similarity, OCR, or calibrated identity-scoring route was found. An InsightFace loader node exists, but no corresponding local model was found. SAM/Impact nodes are registered, but no required detector/segmenter model weight was found in the inspected model paths.

Installed custom-node commits are recorded so a future isolated clone can be reproduced:

| Component | Commit |
|---|---|
| comfyui_controlnet_aux | `e8b689a513c3e6b63edc44066560ca5919c0576e` |
| ComfyUI_IPAdapter_plus | `a0f451a5113cf9becb0847b92884cb10cbdec0ef` |
| ComfyUI-Frame-Interpolation | `26545cc2dd95bc3d27f056016300673bdeee78f5` |
| ComfyUI-GGUF | `6ea2651e7df66d7585f6ffee804b20e92fb38b8a` |
| ComfyUI-Impact-Pack | `429d0159ad429e64d2b3916e6e7be9c22d025c3c` |
| ComfyUI-Impact-Subpack | `50c7b71a6a224734cc9b21963c6d1926816a97f1` |
| ComfyUI-Inpaint-CropAndStitch | `606e2b4fd83fc44e1f0b403e1f076501db8c3749` |
| ComfyUI-Manager | `f39cbd56fecae0b27a446c0cd450cd591f3a8bea` |
| ComfyUI-VideoHelperSuite | `4ee72c065db22c9d96c2427954dc69e7b908444b` |

### Material local model files

| Artifact | Bytes | SHA-256 | Publisher-stated license/provenance finding |
|---|---:|---|---|
| FLUX.2 Klein 4B FP8 checkpoint | 4,070,624,520 | `97ed34fe0567e436200f2faee3939b88f2b5d99f8af2a4dc16532c4245c0ccb6` | Local checkpoint directory includes Apache-2.0 license; official BFL material says Klein 4B is Apache-2.0 [R7-R9] |
| Qwen 3 0.6B base encoder | 1,192,135,096 | `cd2a512003e2f9f3cd3c32a9c3573f820bb28c940f73c57b1ddaa983d9223eba` | Dependency terms still require separate review |
| `flux2-vae.safetensors` | 336,213,556 | `d64f3a68e1cc4f9f4e29b6e0da38a0204fe9a49f2d4053f0ec1fa1ca02f9c4b5` | Adjacent local source metadata names FLUX.2-dev and a non-commercial license: **commercial blocker until resolved** |
| Illustrious XL v2.0 | 6,938,040,674 | `c2a1a3eaa13d4c107dc7e00c3fe830cab427aa026362740ea094745b3422a331` | Exact hash matches publisher-hosted artifact; model card states CreativeML Open RAIL-M [R24-R25] |
| Xinsir union SDXL ProMax ControlNet | 2,513,342,408 | `9fae2e50cb431bfcbe05822b59ec2228df545ef27f711dea8949e9f4ed9f7cdc` | Publisher model card states Apache-2.0 and multi-control support [R26] |
| IP-Adapter Plus SDXL ViT-H | 847,517,512 | `3f5062b8400c94b7159665b21ba5c62acdcd7682262743d7f2aefedef00e6581` | Exact hash matches publisher-hosted file; repository states Apache-2.0 [R27-R28] |
| CLIP ViT-H image encoder | 2,528,373,448 | `6ca9667da1ca9e0b0f75e46bb030f7e011f44f86cbfb8d5a36590fcd7507b030` | Separate dependency/license review still required |

Other community SDXL checkpoints and style LoRAs were found, but the local audit did not find a complete license/provenance packet for them. Two character LoRAs are plainly from prior work (`sigrid_v1`, `soren_v1`) and are categorically out of scope for fresh Ember Lattice references.

## Detailed technical research

### 1. OpenAI image generation and editing

The current API model documented by OpenAI is GPT-Image-2. It supports generation and editing, flexible image sizes, and high-fidelity image inputs. OpenAI publishes a dated API snapshot, `gpt-image-2-2026-04-21`, which is preferable to a moving alias for a reproducible API bakeoff [R1]. The API guide supports multiple input images, high-input-fidelity editing, masks, and Responses-API multi-turn iteration [R2]. That makes it a strong fit for fresh reference sheets, expression/costume continuity, and localized correction.

Important constraints are production-relevant:

- OpenAI documents recurring-character consistency and precise structured composition as limitations, and notes that complex image requests can take up to two minutes [R2]. This is why the benchmark must stress group shots, equipment, fast melee, repeated geography, and high-density safe zones.
- Masks guide the edit but may not follow their literal shape exactly; preserve the source, mask, result, and a before/after crop [R2].
- Text rendering is improved but precise placement can still fail [R2]. Source art should contain **no lettering**. Typography belongs in deterministic layers.
- The API supports flexible dimensions within published bounds, but panel-source generation should use stable master aspect classes and be cropped only under a safe-zone contract [R2].
- The inspected official image guide and model page do not document a generation `seed`. Do not invent one. For API calls, record model snapshot, endpoint, size, quality, prompts, ordered input hashes, mask hash, returned usage, request identifier if exposed, and output hash.
- Current GPT-Image-2 list pricing is token-based: image input $8/M tokens, cached image input $2/M, image output $30/M; text input $5/M and cached text input $1.25/M. Batch rates are lower. Price is not predictable from “one panel” alone, so capture returned usage rather than using a fictional per-image constant [R3]. Free-tier GPT-Image-2 is not supported [R1].

The built-in tool available to this session is not the same audited surface as a user-controlled API call. It exposes reference-image selection but does not expose its backing model/snapshot, public endpoint, seed, request ID, token usage, or price. The R&D record must keep those fields explicitly `null`/`unknown`, never silently label it GPT-Image-2, and use hashes plus visual regression for traceability.

OpenAI's current Service Terms and the governing user/business agreement still control use; inputs must be owned or licensed and outputs require human review. Similarity, trademarks, publicity/personality rights, and third-party rights remain separate risks [R4-R5]. For this original work, use only fresh isolated Ember Lattice references, avoid real-person likenesses and artist-name imitation, retain prompt/input/output records, and perform a release review.

### 2. FLUX / Black Forest Labs

FLUX.2 Klein 4B is the most relevant BFL route for this machine. BFL describes the 4B model as Apache-2.0, supporting up to four reference images, around 13 GB VRAM, and compact low-step operation; that fits the observed 24 GB laptop GPU [R7-R9]. BFL's API lineup offers more capable paid Max/Pro/Flex routes and larger reference limits [R7-R8]. Current documented prices begin at $0.014/image for Klein 4B, with higher prices for hosted Pro/Max/Flex; API use requires a BFL account, prepaid credits, and a key [R10-R11]. None was used.

For a hosted BFL benchmark, use a non-preview endpoint, because BFL states preview endpoints can be updated while fixed endpoints are the reproducibility choice [R12]. Record endpoint, model/version, dimensions, safety settings, ordered references, prompt, seed when the chosen endpoint exposes one, polling identifiers, delivery URL expiry, output hash, latency, and billed credits. Avoid uploading confidential or unlicensed references until the applicable terms/data handling have been accepted by the owner.

For local execution, isolate the runtime and all cache/temp/output paths outside the protected worktree, then reproduce the exact Comfy graph and hashes listed above. Do **not** run the detected FLUX stack commercially until the VAE provenance conflict is resolved and all text encoder/VAE/checkpoint dependencies are reviewed. The checkpoint's Apache status does not automatically cure a different dependency's restriction.

### 3. ComfyUI, ControlNet, IP-Adapter, and Diffusers

ComfyUI is an appropriate graph runner for reproducible local R&D. Its official repository is GPL-3.0 and documents local/offline operation, workflow embedding in generated files, seeds, an API, and changed-node caching [R13]. Pin the Comfy commit, custom-node commits, Python/PyTorch/CUDA versions, graph JSON, all model hashes, every seed, sampler/scheduler/steps/CFG, dimensions, and input/control-map hashes. A seed is necessary but not sufficient: GPU kernels, library upgrades, quantization, and node changes can alter pixels.

ControlNet adds spatial conditioning from edges, depth, pose, or other control maps; multiple ControlNets can be composed [R14-R15]. For this production:

- **Canny**: available now and best for kiln ribs, bridges, weapon contours, and UI-safe architecture.
- **Pose**: valuable for duos/groups and explicit melee vectors, but the detected learned OpenPose/DensePose preprocessors lack local weights. Do not allow a node to lazy-download. Supply a manually authored/openly cleared map or defer.
- **Depth**: valuable for crownshaft scale and repeatable platforms, but the local learned depth extractor is not offline-ready. A Blender depth pass would be excellent once Blender is installed.
- **Line art/anime line art**: helpful for clean silhouettes and repair passes, but the registered learned extractor lacks its local weight. Manually created line art remains usable as a control input.

IP-Adapter provides image prompting with relatively small adapters, and Diffusers documents combining IP-Adapter with ControlNet for depth/edge/pose guidance [R18-R20]. The detected SDXL adapter is a plausible character/style conditioning candidate, but it must be tested for identity drift, outfit mutation, expression loss, and compositional overconstraint. Reference strength must be logged.

Diffusers itself is not installed. Official Diffusers supports FLUX.2 reference-image conditioning, ControlNet, IP-Adapter, adapter loading, and explicit `Generator` objects [R17-R21]. Its reproducibility guide warns that exact results are not guaranteed across releases or platforms and recommends a CPU `Generator` when reproducibility matters [R21]. If installation is later authorized, create a locked virtual environment outside protected worktrees and write a frozen dependency manifest; do not mutate the protected Comfy environment.

### 4. Multiple references

Multi-reference is useful only when every image has one job. Use a stable order and label it in metadata:

1. identity/head and apparent age;
2. full-body costume/equipment contract;
3. environment/creature contract;
4. optional pose/composition reference that contains no identity to copy.

More references are not automatically better. They can conflict and dilute identity. The benchmark should test one-, two-, and three-reference variants on the same seed/prompt where the route permits. No reference may come from prior worktrees or unrelated projects. Hash every input and document source/rights.

### 5. LoRA training

BFL's current guidance says base variants are the right starting point for fine-tuning, calls for a varied high-resolution dataset, and gives character-training ranges in the low thousands of steps [R22]. The detected local asset is a distilled/FP8 Klein inference checkpoint, while the registered Comfy LoRA trainer is marked experimental. There is also no fresh Ember Lattice dataset. Training now would be an uncontrolled experiment and would violate the fresh-reference rule if the old character LoRAs were substituted.

A future LoRA gate requires: a publisher-approved base model and license chain; 30-100+ fresh, owned, deduplicated, captioned images per subject/style goal; holdout views; dataset and caption hashes; consent/provenance log; isolated base and output paths; pinned trainer commit and dependencies; seed, shuffle order, optimizer, rank/alpha, resolution buckets, step/checkpoint schedule; contamination and overfit checks; and the same 24-case benchmark against the non-LoRA route. Do identity and style adapters separately when possible. A LoRA that improves portraits but harms hands, action geography, or outfit continuity fails.

### 6. Inpainting and local editing

Masked repair should be a surgical, auditable stage:

- freeze the accepted source and SHA-256;
- define one defect and one mask per edit;
- include a margin around the defect but protect identity-critical boundaries;
- use the original character/environment references and matching model route;
- log crop coordinates, mask hash, prompt/negative prompt, denoise strength, seed, workflow/model hashes, and result hash;
- inspect the seam at 100%, thumbnail size, grayscale, and adjacent-panel context;
- reject edits that silently alter age, face geometry, costume, grip, handedness, landmark, injury, or lighting.

The installed Inpaint Crop & Stitch nodes make this practical once the runtime is isolated and the model chain cleared. OpenAI's edits endpoint/built-in edit route is the currently authorized alternative, with the caveat that the mask is guidance rather than a guaranteed pixel boundary [R2].

### 7. Blender 2D/3D staging

Blender would materially improve repeated architecture, camera continuity, depth maps, collision/contact, and difficult perspective. Its official storyboarding workflow combines Grease Pencil, 3D layout, linked assets, and the video sequencer; View Layers can isolate objects and emit depth/normal/Cryptomatte-like passes for downstream control and compositing [R29-R30]. Blender is GPL, while the artwork produced remains the creator's work, subject to any third-party asset/add-on licenses [R31]. Blender 4.5 LTS is an appropriate future pin, and the observed machine exceeds Blender's published recommended 8 GB VRAM requirement [R32-R33].

The executable is absent, so Blender is not a current route. If installation is later authorized, build only simple original proxies: kiln-rib kit, platforms, lift cable, chain bridge with anchor states, Belljaw/Bell Regent volume proxy, and scale mannequins. Export camera matrix, object transforms, focal length, render settings, depth/normal/object masks, `.blend` hash, and Blender version. Use passes as control evidence, not as final glossy 3D art.

### 8. Layered compositing and professional lettering/system UI

The repository already supports deterministic SVG balloons, captions, system cards, SFX, safe zones, hashes, contact sheets, grayscale checks, action strips, and responsive review HTML. This is the most mature and reproducible route in the current environment.

Production rules:

- Generate source art without letters, digits, fake glyphs, balloons, or UI.
- Store dialogue/UI as text data and render it as separate named SVG groups.
- Give every balloon/card an owner, reading-order index, safe-zone box, tail target, padding rule, and collision check.
- Keep system semantics stable: separate visual tokens for Status, Skill, Quest, Item, Inventory, XP, Level, Enemy, Dungeon/Floor, Cultivation, and Faction.
- Never communicate danger/state by hue alone. Preserve shape/icon/label redundancy and check grayscale.
- For screen text, use WCAG 2.2 contrast as a conservative QA target: 4.5:1 for normal text and 3:1 for large text [R35-R36]. This does not by itself certify a raster comic as WCAG-conformant; it is a measurable readability floor.
- Preserve editable text in the review artifact. SVG 2 defines text/tspan layout, but exact glyph geometry depends on the font and renderer [R34].
- Replace the unembedded Arial request with an explicitly licensed, repository-bundled font only after owner/license approval. An OFL font is a strong candidate; include its unmodified license and honor reserved-font-name requirements [R37]. Until then, pin the browser and record that typography is not bit-identical cross-platform.
- Pin the rasterization engine/version (Edge `152.0.4191.62` or Chrome `151.0.7922.174` currently), viewport, DPR, font file hash, SVG/HTML/CSS hashes, and screenshot hash.

### 9. Automated visual evaluation

Automation can reject mechanical defects and prioritize review; it cannot approve premium sequential art. Recommended deterministic checks with the installed global Pillow/NumPy stack are:

- dimensions, aspect, file existence, alpha, corruption, and SHA-256;
- near-blank, clipping, excessive border contact, duplicate/near-duplicate panels, and palette outliers;
- safe-zone occupancy and balloon/UI overlap from source geometry;
- local contrast and grayscale readability;
- edge density/entropy as a warning for clutter, never as an aesthetic score;
- reference/output perceptual comparisons only as drift signals;
- sequence checks for left/right vectors, injury/equipment/location state when those are explicitly annotated.

SSIM, PSNR, and MSE are available from scikit-image and are useful for render regressions, not semantic identity [R40]. MediaPipe's official task outputs include 33 pose landmarks, 21 hand landmarks per hand, and face landmarks/blendshapes/transforms [R38-R39, R41], but the required package/model assets are not present here. Even when installed, stylized-anime domain failures and occlusion are expected. Use landmark confidence only to flag likely anatomy cases; a human must inspect every hand, face, grip, contact, and action transition.

There is no installed calibrated face-identity, OCR, or semantic-image scorer. Do not fabricate CLIP/DINO/InsightFace scores. If later authorized, validate any scorer against a hand-labeled Ember Lattice set before using thresholds. OCR is useful only to enforce “no accidental text” on source art and should be paired with visual review because stylized fake glyphs evade it.

### 10. Premium webtoon story and episode development

The premium visual pipeline should be driven by a serial-production story model, not by isolated image prompts. The following is a production inference from the project's requirements, not a claim from a model vendor:

- Maintain a season spine with promise, escalation, midpoint inversion, irreversible cost, climax, and renewal hook.
- Give every episode one external objective, one relationship turn, one progression/economy delta, and one final-scroll question or reversal.
- Maintain reveal, injury, equipment, inventory/economy, faction, cultivation, location, lighting/time, and unresolved-question ledgers. Panel prompts are compiled views of those records.
- Limit visible system UI to 2-4 consequential moments per episode. Reconcile values explicitly after action so progression feels earned rather than decorative.
- Write action in topology: establish positions/anchors; initiate; make contact; show consequence; update geography; pay off. If a reader cannot redraw the bridge and vectors, the sequence is not ready.
- Author for vertical rhythm: compact setup, varied panel height, intentional whitespace pause, tall reveal/action payoff, short aftermath, hook. Preserve mobile-safe type and do not solve pacing by shrinking text.
- Build a publication buffer and measure correction rate, median labor per accepted panel, weakest-case frequency, lettering overflow, late continuity repairs, and hook-to-next-episode conversion signals.

WEBTOON CANVAS currently supports creator-managed series/episode publishing through its website, previews/scheduling, and specified thumbnail assets [R42-R43]. Content rating/review and the current rating questionnaire must be completed before release [R44-R45]. Current creator-product changes include expanded analytics and translation features, but platform rollouts can change; verify the live dashboard before committing the release runbook [R46]. No publishing action was taken in this audit.

## Recommended 24-case bakeoff protocol

Use the existing 24-case benchmark specification as the narrative lock. Compare complete sets, not curated winners. For every route/case:

1. Freeze the case prompt, ordered references, target aspect/dimensions, and negative constraints.
2. Define a fixed attempt budget before generation: suggested maximum is two raw attempts plus one localized correction. Do not give a weak route unlimited retries.
3. Preserve every attempt, including failures, with immutable hashes. Record wall time, active operator time, and any usage/credit cost.
4. Apply lettering/UI only after the same text-free-art selection policy. Evaluate both source art and composed result.
5. Have at least one reviewer score blind to route. Use the full 1-5 rubric; store comments for every score below 4.
6. Report median, fifth percentile, absolute weakest case, hard-failure count, correction success, acceptance rate, cost per accepted panel, active minutes per accepted panel, and multi-panel continuity.
7. A route with any unresolved story-breaking hard failure cannot win. The final hybrid may assign different routes to different case classes only if that branching rule is explicit, reproducible, and does not create style/identity drift.

Minimum provenance record per generated panel:

```json
{
  "route_id": "stable route identifier",
  "model_or_tool": "exact value or unknown",
  "model_snapshot": null,
  "workflow_hash": null,
  "prompt_hash": "sha256",
  "ordered_input_hashes": [],
  "mask_or_control_hashes": [],
  "seed": null,
  "parameters": {},
  "request_id": null,
  "started_utc": "RFC3339",
  "ended_utc": "RFC3339",
  "usage": null,
  "direct_cost_usd": null,
  "output_sha256": "sha256",
  "parent_output_sha256": null,
  "operator_notes": "unknown fields remain explicit"
}
```

## Release/license/security gate

Before any route becomes final production:

- confirm the governing service terms on the actual account and date of use;
- audit the complete local component chain, not only the headline checkpoint;
- retain license/model-card snapshots and artifact hashes;
- verify every reference, font, texture, 3D asset, and training item is owned or licensed for intended distribution;
- prohibit living-artist imitation and real-person likeness references;
- strip credentials, signed URLs, machine usernames, and absolute protected paths from publishable artifacts;
- keep services loopback-only unless an owner authorizes networking;
- never embed API keys in workflow JSON, HTML, logs, or screenshots;
- run visual similarity/trademark/release review with human judgment;
- archive prompts, refs, masks, controls, raw candidates, rejects, edits, composed outputs, scores, and hashes.

## Official and primary sources

All web sources below were accessed **2026-09-04**. Pricing, model status, platform limits, and terms are time-sensitive and must be rechecked at the next production run.

| ID | Source | What it supports |
|---|---|---|
| R1 | [OpenAI — GPT-Image-2 model](https://developers.openai.com/api/docs/models/gpt-image-2) | Current API model, endpoints, snapshot, rate limits |
| R2 | [OpenAI — Image generation guide](https://developers.openai.com/api/docs/guides/image-generation) | Generations/edits, multiple inputs, masks, sizes, fidelity, limitations |
| R3 | [OpenAI — API pricing](https://developers.openai.com/api/docs/pricing) | Current token prices and Batch prices |
| R4 | [OpenAI — Service Terms](https://openai.com/policies/service-terms/) | Current service-specific rights, obligations, and exceptions |
| R5 | [OpenAI — Services Agreement](https://cdn.openai.com/osa/openai-services-agreement.pdf) | Input/output and customer responsibilities under the business agreement |
| R6 | [OpenAI — API output/copyright help](https://help.openai.com/en/articles/5008634) | Official pointer to applicable terms for API outputs |
| R7 | [Black Forest Labs — FLUX.2 Klein](https://bfl.ai/models/flux-2-klein) | 4B/9B variants, licensing, hardware benchmark context |
| R8 | [BFL docs — FLUX.2 overview](https://docs.bfl.ai/flux_2/flux2_overview) | Reference counts, VRAM guidance, family capabilities and licenses |
| R9 | [BFL help — generating quickly with FLUX.2 Klein](https://help.bfl.ai/articles/7592221790-how-do-i-generate-quickly-with-flux-2-klein) | Dimensions, reference limit, operating guidance |
| R10 | [BFL docs — pricing](https://docs.bfl.ai/quick_start/pricing) | Current hosted prices and credit conversion |
| R11 | [BFL docs — getting started](https://docs.bfl.ai/quick_start/get_started) | Account, credits, API key requirements |
| R12 | [BFL docs — generating images](https://docs.bfl.ai/quick_start/generating_images) | Endpoint workflow and preview/fixed endpoint reproducibility |
| R13 | [Comfy-Org — ComfyUI](https://github.com/Comfy-Org/ComfyUI) | License, local runtime, workflows, seeds, API, caching |
| R14 | [ComfyUI docs — ControlNet](https://docs.comfy.org/tutorials/controlnet/controlnet) | Edge/depth/pose control and multiple controls |
| R15 | [ComfyUI docs — preprocessors](https://docs.comfy.org/tutorials/utility/preprocessors) | Preprocessor/model/custom-node workflow requirements |
| R16 | [ComfyUI docs — FLUX.2 dev](https://docs.comfy.org/tutorials/flux/flux-2-dev) | Official Comfy FLUX.2 workflow/component context |
| R17 | [Hugging Face Diffusers — FLUX.2 pipelines](https://huggingface.co/docs/diffusers/api/pipelines/flux2) | Reference conditioning and pipeline API |
| R18 | [Diffusers — IP-Adapter](https://huggingface.co/docs/diffusers/using-diffusers/ip_adapter) | IP-Adapter and ControlNet composition |
| R19 | [Diffusers — loading adapters](https://huggingface.co/docs/diffusers/main/using-diffusers/loading_adapters) | Adapter loading and composition |
| R20 | [Diffusers — ControlNet pipelines](https://huggingface.co/docs/diffusers/api/pipelines/controlnet) | Control inputs and inpaint/control pipeline APIs |
| R21 | [Diffusers — reproducibility](https://huggingface.co/docs/diffusers/main/using-diffusers/reusing_seeds) | Generators, seeds, cross-platform/version limits |
| R22 | [BFL docs — FLUX.2 Klein training](https://docs.bfl.ai/flux_2/flux2_klein_training) | Base-model fine-tuning, data and step guidance |
| R23 | [BFL help — self-serve developer license](https://help.bfl.ai/articles/9272590838-self-serve-dev-license-overview-pricing) | Local 4B/9B licensing and hosted commercial-use summary |
| R24 | [Onoma AI Research — Illustrious XL v2.0 model card](https://huggingface.co/OnomaAIResearch/Illustrious-XL-v2.0) | Publisher-stated license and model context |
| R25 | [Onoma AI Research — exact Illustrious artifact](https://huggingface.co/OnomaAIResearch/Illustrious-XL-v2.0/blob/main/Illustrious-XL-v2.0.safetensors) | Remote hash comparison |
| R26 | [Xinsir — ControlNet Union SDXL 1.0 model card](https://huggingface.co/xinsir/controlnet-union-sdxl-1.0) | Publisher-stated license and supported controls |
| R27 | [Tencent — IP-Adapter repository](https://huggingface.co/h94/IP-Adapter) | Publisher-stated license and adapter context |
| R28 | [Tencent — exact IP-Adapter Plus SDXL artifact](https://huggingface.co/h94/IP-Adapter/blob/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors) | Remote hash comparison |
| R29 | [Blender Manual — storyboarding](https://docs.blender.org/manual/en/latest/video_editing/storyboarding/index.html) | Grease Pencil, 3D layout, VSE, linked assets |
| R30 | [Blender Manual — View Layers and passes](https://docs.blender.org/manual/en/latest/render/layers/introduction.html) | Layer isolation and render-pass composition |
| R31 | [Blender — license](https://www.blender.org/about/license/) | GPL terms, output ownership, add-on caveat |
| R32 | [Blender — system requirements](https://www.blender.org/download/requirements/) | Recommended hardware |
| R33 | [Blender — 4.5 LTS](https://www.blender.org/releases/4-5/) | LTS status/support line |
| R34 | [W3C — SVG 2 text](https://www.w3.org/TR/SVG2/text.html) | SVG text/tspan/font layout model |
| R35 | [W3C — WCAG 2.2](https://www.w3.org/TR/WCAG22/) | Normative contrast criteria |
| R36 | [W3C WAI — Understanding contrast minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) | Practical contrast rationale and thresholds |
| R37 | [SIL — Open Font License](https://openfontlicense.org/) | Official OFL text and FAQ |
| R38 | [Google AI Edge — PoseLandmarkerResult](https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/PoseLandmarkerResult) | Pose landmark outputs |
| R39 | [Google AI Edge — HandLandmarkerResult](https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/HandLandmarkerResult) | Hand landmark/handedness outputs |
| R40 | [scikit-image — image metrics](https://scikit-image.org/docs/stable/api/skimage.metrics.html) | SSIM, PSNR, MSE APIs and parameter caveats |
| R41 | [Google AI Edge — FaceLandmarkerResult](https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/FaceLandmarkerResult) | Face landmarks, blendshapes, transforms |
| R42 | [WEBTOON CANVAS — start publishing](https://webtooncanvas.zendesk.com/hc/en-us/articles/18556588863380-How-do-I-start-publishing-on-CANVAS) | Website publishing, preview, scheduling, thumbnails |
| R43 | [WEBTOON CANVAS — file size overview](https://webtooncanvas.zendesk.com/hc/en-us/articles/32913712749588-File-Size-Overview-What-to-Know-before-Publishing-your-Comic-on-WEBTOON-CANVAS) | Current thumbnail asset sizes |
| R44 | [WEBTOON CANVAS — content review](https://webtooncanvas.zendesk.com/hc/en-us/articles/29555016331924-Content-Review) | Content ratings/review |
| R45 | [WEBTOON CANVAS — episode upload/rating requirement](https://webtooncanvas.zendesk.com/hc/en-us/articles/29275038924052-Why-can-t-I-upload-a-new-episode) | Required content-rating questionnaire |
| R46 | [WEBTOON — 2026 creator platform update](https://about.webtoon.com/press-release/238) | Analytics/translation/creator-control rollout context |
