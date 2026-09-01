# DECISION_LOG.md

> ⚠️ **v2.1 — 2026-08-31.** This document has been corrected after independent
> verification by the project owner. **Read `docs/CORRECTIONS_V2_1.md` first**; it is
> the authority wherever it conflicts with anything here. Corrections are marked inline
> with ⚠️ v2.1.
**North Garden / Visual Narrative Compiler — verdicts on prior findings**
Compiled 2026-08-31 from six parallel research tracks. Status vocabulary: **KEEP** (evidence supports, carry forward) · **REPLACE** (right problem, wrong mechanism) · **RETIRE** (stop doing this) · **UNRESOLVED** (needs an experiment, not more reading).

---

## A. Verdicts on the seven hypotheses the handoff asked me to challenge

### A1. "Shot/Panel records first, before renderer work" — **REPLACE**
The intent is right; the sequencing claim is contradicted by every system cited. MangaFlow's `Story Section Memory` fields (`R_k^scene`, `R_k^char`, `R_k^obj`) and StoryBlender's four-layer Continuity Memory Graph are not a-priori designs — they are exactly what each system's *renderer* needed as conditioning. `PREPRINT` A schema authored before you know what the renderer consumes will have the wrong fields.

This does not block you, because **you already have a working renderer.** Schema work is legitimate now and would not have been six months ago. What changes is the shape:

- Split **`ShotIR`** (renderer-independent intent) from **`RenderRecord`** (one attempt to realise it). Test for membership: *would this field still mean something if the entire renderer were swapped?* If no, it is a RenderRecord input, not intent. `prompt`, `seed`, `cfg`, `lora_weights` are RenderRecord fields wearing a schema.
- Further split **`SceneRecord`** (shared across media) from **`PanelSpec`** / **`ShotSpec`** (per-medium). See A6.

### A2. "Blender is the authoritative source of spatial truth" — **KEEP, narrowed**
Survives, but must own *less* than assumed. Blender owns **camera, scale, occlusion, relative blocking**. It must not own surface detail.

The narrowing is peer-reviewed and it is cost-*reducing*: LooseControl (Bhat/Mitra/Wonka, SIGGRAPH 2024, arXiv 2312.03079) `PEER_REVIEWED` argues exact-depth ControlNet is a trap — producing realistic depth for cluttered scenes is "probably as challenging as solving the original task" — and demonstrates that **boxy scene boundaries plus bounding boxes are sufficient**. Corollary: a beautifully modelled set is *worse* conditioning than a crude one. Build deliberately cruder than instinct suggests.

Second narrowing, also evidence-backed: **do not stack controls.** arXiv 2510.21763 `PREPRINT` reports "multi-ControlNet composition causes severe artifacts; robust combined control remains difficult." Pick one primary (depth *or* normal-derived lineart) plus at most one secondary.

**The strongest argument for this hypothesis comes from our own failure log, not from any vendor:** occluder polygons currently have to be hand-authored per room (`north-garden-page-methods.md` — "Only `rm_table` and `rm_wide` have occluders. Every new room needs one authored"). In a real 3D set that authoring cost goes to zero permanently.

### A3. "Recurring sets should have canonical 3D assets" — **KEEP, strongly — and it is not novel**
This is already standard, non-AI, professional webtoon practice (Clip Studio 3D assets, SketchUp, ACON3D) `PRACTITIONER`. We are adopting, not pioneering. Break-even is roughly **chapter 2–3 of reuse of a given set**; for a one-off location it never pays.

Two sub-claims are **RETIRED**:
- **3DGS as the set representation — RETIRE.** A splat is a view-dependent radiance field with no watertight surface and **no reliable occlusion boundary** — which is precisely the failure we are trying to fix. Photogrammetry beats it on metric accuracy on opaque structured surfaces (ISPRS Archives XLVIII-2/W12-2026 p.89) `PEER_REVIEWED`; best surface accuracy in an 8-method comparison went to 2DGS at 3.15 mm Chamfer, with plain 3DGS not leading on geometry (PP-RAI 2026) `PEER_REVIEWED`.
- **World-model mesh export as canonical geometry — RETIRE.** Marble's own docs concede reconstruction artifacts on thin structures, transparency and background, and recommend splat export for fidelity — an admission the geometry is a byproduct `OFFICIAL_DOCS`. A 600k-triangle unstructured mesh cannot be renamed, re-walled, or meaningfully version-controlled.

**Do not scan 70 acres.** Build terrain from the plat to survey dimensions, with landmark proxies; photogrammetry (RealityScan 2.0, free below Epic's revenue threshold) for the 5–10 hero objects the camera gets close to; splats only as a look reference that never ships.

### A4. "Run a multi-person identity bake-off rather than assuming regional LoRA" — **KEEP the bake-off; the assumed mechanism was wrong**
The instruction to bake off was correct, and it caught a real error. Three corrections:

1. **ComfyUI has had native masked LoRA since 2024-12-02** — the LoRA *hooks* system (`Create Hook LoRA`, `Set CLIP Hooks`, `Cond Pair Set Props`, `Cond Pair Combine`, `Set Default Combine`) `OFFICIAL_DOCS`. Hooks attach the *weight patch itself* to a masked conditioning, which is exactly the mechanism the earlier `ConditioningSetMask` attempt lacked. It is core, first-party, stated compatible with all models. **This, not Impact Pack, is the thing to test first.** Documented gotchas: all conditioning must be masked or use `Set Default Combine`; overlapping masks reintroduce blending; identity trigger tokens left in the base prompt leak globally.
2. **Impact Pack `RegionalSampler` is probably the wrong vehicle anyway.** Its own official tutorial concedes it "is easier to lose harmony compared to other regional methods" and that without proper ControlNet alignment it yields "blurry image" results `OFFICIAL_DOCS`. More decisively, I found **no documentation of RegionalSampler support for Qwen-Image, Qwen-Image-Edit, or FLUX.2** — only FLUX.1 for Impact KSampler/Detailers. It is an SD1.5/SDXL-era design. It remains viable *on Illustrious specifically*, which is SDXL-family.
3. **Reference encoders do not beat a LoRA on likeness.** Best published multi-subject Face-Sim is **0.5284** (MultiCrafter, arXiv 2509.21953, CVPR 2026), vs XVerse 0.4117 and UNO 0.1474 `PEER_REVIEWED`. A rank-16 LoRA on 30 curated photos beats all of those. Keep the LoRAs.

**Reframed architecture:** reference-conditioning for *staging and composition*; LoRA-patched region refinement for *identity*. Not either/or.

### A5. "ComfyUI demoted to one adapter behind an interface" — **KEEP, scoped down hard**
The evidence for demotion is stronger than expected, and it comes from ComfyUI's own maintainers: there is **no public interface contract**, "every change made to ComfyUI has the potential to break custom nodes," and custom nodes "can 'brick' a ComfyUI installation" `OFFICIAL_DOCS` (Nodes v3 post, 2025-06-07). Concrete breakage: Comfy-Org issue #11833, open since 2026-01-13 — adding a defaulted input to an existing node breaks previously-working API workflows `OFFICIAL_REPO`.

**Therefore a saved workflow JSON is not a stable artifact.** It is a snapshot valid against one commit.

But scope the abstraction to one method — `render(shot_ir) -> RenderResult` — and write exactly **one** adapter. An interface with one implementation designed in advance is premature abstraction, and it will be shaped by ComfyUI's idiosyncrasies anyway. **Mandatory, non-optional:** record the ComfyUI **commit hash** and the workflow **content hash** in every RenderRecord. Without those the adapter boundary is decorative and renders are not reproducible.

**RETIRE:** porting to diffusers for maintainability. No evidence of an inherent quality deficit, but clear evidence that reproducing a tuned ComfyUI result in diffusers means chasing sampler/scheduler/prompt-weighting/aspect-ratio differences one at a time `OFFICIAL_REPO` (diffusers discussion #9265). Weeks of unpaid re-tuning against no gain.

**RETIRE:** ComfyUI-to-Python-Extension for batch work — its own README states exported scripts "do not implement Web UI prompt/result caching across repeated service calls," i.e. model reload per panel.

### A6. "One ShotIR serves comic panels and animation shots" — **REPLACE**
This is the most important correction in the programme, and the reason is structural rather than technical.

**An anime e-conte carries timing; a comic panel does not.** The e-conte consists of "scene illustrations, timing information, and textual descriptions" and is the production blueprint (Griffith, CHI 2024, DOI 10.1145/3613904.3642121) `PEER_REVIEWED`. A comic panel encodes composition, reading order, and *implied* duration via panel size and gutter. The map from gutter width to seconds is not a function; it is a directorial decision made fresh. A `duration_frames` field on a panel record stays permanently null.

Second, independent objection: **comic staging is built on cheating.** 3D layout artists rebuild boarded shots with proxies precisely because "2D animatic is often cheatable in terms of character scale, perspective or distance. But cheating these properties in a 3D layout is not that easy" `PRACTITIONER`. Good comic panels contain foreshortening and eyelines that will not resolve into a consistent 3D camera.

**What actually transfers:** story beats and dialogue (fully) · character identity assets (fully) · 3D environments (fully) · voice ID per line (fully) · camera position/lens (mostly — layout cameras do survive to final). **What does not:** panel composition → shot composition · timing · cut count.

**Revised:** `SceneRecord` shared; `PanelSpec` and `ShotSpec` separate, each referencing it. Assets, canon and story state are reused; directing decisions are re-made per medium. *(v2.1: earlier percentage estimates withdrawn — intuition, not measurement.)* That is still a large win and it is the one worth designing for. Claiming shot-level reuse buys a rewrite at chapter 40.

**No verified case** of anyone shipping animation from reused comic panel records was found — only vendor marketing. Absence of evidence in a marketing-dense space.

### A7. "QA/repair matters more than first-pass beauty" — **UNRESOLVED, and reframed**
Directionally plausible, **not verified by anything**. I found no published cost accounting comparing generate-cost against QA-and-repair-cost for a serialized production, and — more tellingly — **no production account of image-side automated continuity QA at chapter scale exists at all.** Two targeted searches returned only SEO content. Either it is not valuable enough to have been built, or it is harder than it looks; the evidence below suggests the latter.

**REPLACE the mechanism.** "An automated VLM+CV drift audit is the highest-value custom tooling" is half right, and the wrong half is the expensive half:

- **VLMs are bad detectors.** On inter-state visual difference detection: human 89.75%, Gemini-2.5-Pro 47.58%, GPT-5 45.14% (M³-Verse, arXiv 2512.18735) `PREPRINT`. On difference captioning, GPT-4o scores ~1/5 of a task-specific model (OmniDiff, arXiv 2503.11093v2) `PREPRINT`. ⚠️ v2.1: M³-Verse's ~12.32-point figure is the gap between **hallucination-centric and factual questions**, *not* a generic leading-question penalty — I previously conflated a measured result with a design inference. The qualitative concern survives on separate evidence: DiffSpot's best model detects only ~40.7% of true fine-grained changes and deliberately includes **no-change controls**, because fabricated differences are a real failure mode `PREPRINT`.
- **The human ceiling is itself low.** Inter-annotator ρ ≈ 0.41–0.54 on visual narrative coherence (VCMS, ACL 2026) `PEER_REVIEWED`. Continuity error is partly taste, which caps any detector.
- **Judge reliability ≠ validity.** κ 0.376–0.511 with humans across 21 judge models and ~541k judgments; exact-match agreement overstates chance-corrected agreement by 33.8–41.3 points (arXiv 2606.19544) `PREPRINT`. **Self-consistency voting will not save you** — it reproduces the same bias three times.
- **Audit & Repair's code was never released** — "Coming soon," no repo, ~14 months post-submission `OFFICIAL_DOCS`. The flagship paper for this hypothesis is not adoptable, and it reports **no precision or recall for its own detection step**. Neither does CANVAS. Neither does ViStoryBench.

**What replaces it — and this is the actionable finding:** the highest-value tooling is the **declared-state panel manifest**, authored before generation. It converts every question from *"detect drift"* (which VLMs are demonstrably bad at) to *"assert declared state"* (a lookup), and it is **the only mechanism in the literature that can distinguish intentional change from error**. The VLM's job shrinks to single-image binary VQA, which it does well.

**Two further corrections:**
- **Run the continuity check on the script, before any pixels.** ConStory-Checker reports **precision 0.884 / recall 0.550** on 1,000 injected errors, versus human experts at P 0.891 / R 0.171 — a 3.2× error-discovery rate (arXiv 2603.05890) `PREPRINT`. Highest precision, lowest cost, and it prevents rather than detects. **This is the single best-value check available and it was not in the plan.**
- **Repair gates must be two-sided.** GEditBench v2 documents an **"under-editing trap"**: models post inflated consistency scores by *not performing the edit*, e.g. GLM-Image consistency 1,109 with instruction-following collapsed to 787 `PREPRINT`. A gate that only checks "did the rest of the frame survive" selects for silent no-ops. Require the target region to change *and* the remainder not to.

---

## B. Verdicts on findings carried from the original brief

| # | Original finding | Verdict | Note |
|---|---|---|---|
| 1 | Hard problem is volume-with-consistency, not single-image quality | **KEEP** | Corroborated by every system surveyed |
| 2 | Prompt-only character design insufficient | **KEEP** | Uncontested |
| 3 | Character LoRAs strongly assert identity | **KEEP — strengthened** | Reference encoders top out at Face-Sim 0.53; LoRAs beat them |
| 4 | Two global LoRAs bleed/merge | **KEEP** | Mechanism now understood: additive global weight updates + partial cross-attention → stable *average* |
| 5 | Text regionalization ≠ regional LoRA weights | **KEEP** | Correct diagnosis. The fix (native hooks) existed one node family over |
| 6 | Compositing has perspective/lighting/edge ceilings | **KEEP — now has theory** | Linear latent blending is off-manifold by construction (arXiv 2512.05198); VAE round-trips accumulate drift |
| 7 | Hand-derived perspective is the wrong source of truth | **KEEP** | Superseded by 3D, but see A2 — cruder than instinct |
| 8 | Canon strings need stable IDs + timeline variants | **KEEP — strengthened** | Text encoders are order-sensitive; fixed slot order moved consistency 84 → 87.5% over 600 panels `PRACTITIONER`. Freeze as constants |
| 9 | Programmatic lettering is an architectural strength | **KEEP** | Balloon-placement literature is small and static (canonical ref is 2013). A hand-rolled compositor is competitive with the state of the art. Do not rewrite |
| 10 | Panel-level repair + drift detection essential | **UNRESOLVED** | See A7 — necessary, but the mechanism assumed was wrong |
| 11 | Art style not frozen; don't prematurely lock training | **KEEP** | Reinforced: a *simpler*, flatter style has a higher ceiling because it hides model artefacts |
| 12 | Economics must be measured, not assumed | **KEEP — urgent** | Still **zero** measured hours-per-chapter figures from any named practitioner. Instrument your own first three chapters; your numbers will beat the literature |

### Reinterpretations from the master brief

- **"0.6B text encoder is the root cause" — KEEP as a local diagnosis, REJECT as system-level root cause.** Correct for the Anima branch. But no generative model should be the authority for exact camera, role binding, set topology, wardrobe state or prop persistence, however good its encoder gets.
- **"Per-region LoRA may be the single unlock" — REPLACE.** See A4.
- **"Set continuity might need an environment LoRA" — RETIRE as primary.** No first-hand account of anyone training one for a comic was found in either research pass. Canonical 3D is far better evidenced.

---

## C. New findings that change decisions already taken

### C1. The Illustrious switch (decided 2026-08-31) — **KEEP, with one correction**
Illustrious-XL v2.0 was **relicensed to CreativeML Open RAIL (SDXL)** on 2025-04-21, away from FAIPL `OFFICIAL_REPO`. Commercial use permitted subject to passing Attachment A restrictions downstream. The switch stands.

**But do not train on the NoobAI checkpoints already on disk.** ⚠️ **v2.1 — simpler primary reason:** the current NoobAI model cards carry an **explicit commercial prohibition covering the model, derivative models and model-generated products**. That alone excludes them; status `BLOCKED_FROM_COMMERCIAL_PIPELINE`.

Secondary reasoning, retained for other FAIPL bases: FAIPL 1.0-SD defines "to modify" to include "perform any training on a model" and requires modifications be released under FAIPL or compatible — a **share-alike obligation on the character LoRA itself**. A community analysis argues the layered NC claim is unenforceable `COMMUNITY`; that is exactly the kind of argument not to bet a project on, which is why the model card's plain text is now the operative reason.

### C2. 🔴 InsightFace is a silent non-commercial contaminant — **act now**
InsightFace code is MIT; **the pretrained weights are "available for non-commercial research purposes only."** `OFFICIAL_DOCS` As of a 2025-11-24 repo update, face-swap models, the **buffalo_l** recognition pack, and InspireFace all require explicit licensing contact.

**antelopev2 / buffalo_l are pulled automatically and silently** by InstantID, IP-Adapter-FaceID, ReActor, most ComfyUI "face consistency" nodes, and many identity-scoring scripts. The same contamination reaches **XVerse, PuLID, WithAnyone**. ⚠️ v2.1 scope correction: the restriction attaches to the **exact distributed weight files**, not to model-family names. InsightFace's *own distributed detector checkpoints* carry these terms; an independently trained checkpoint of the same architecture from another source does not. **Judge the file and its hash, never the architecture name.**

**Action: `ls ComfyUI/models/insightface/`. If `antelopev2` or `buffalo_l` is present, something in the graph uses it.** Substitute **AuraFace** (built specifically for commercial use; accuracy genuinely lower — CFP-FP 95.18 vs 98.87) or drop identity-embedding conditioning entirely in favour of LoRA-based consistency. Note the Ultralytics/YOLO-face alternative carries **AGPL**, a different trap.

### C3. Other licence/policy changes worth knowing
- **SAM 3** (2025-11-19) moved off Apache 2.0 to a bespoke "SAM License" `OFFICIAL_REPO`. **Pin SAM 2.** A silent auto-upgrade changes your terms.
- **DINOv3** is commercially usable but under a bespoke licence with acknowledgement and use restrictions. **DINOv2 is Apache 2.0** and is the safer default if it suffices.
- **FLUX.2 [dev]** is non-commercial for model and derivatives; **outputs are explicitly commercial**. So a LoRA on it must stay private and undistributed. **FLUX.2 [klein] 4B is Apache 2.0.** klein 9B's status is an *open, unanswered* GitHub issue (#32, since 2026-01-21) — treat as non-permissive.
- **Qwen-Image / Qwen-Image-Edit are Apache 2.0** — the least encumbered high-capability editing models available.

### C4. Vendor policy corrections — several prior assumptions were wrong
- **Kling forbids commercial use of outputs without written permission** (§4.6) while simultaneously granting IP ownership (§4.4) `OFFICIAL_DOCS`. Internally awkward — **disqualified for a monetized comic.**
- **BFL's FLUX *API* trains on inputs and outputs by default.** Consumer ToS has an email opt-out; API Service Terms do not offer one on their face. **Never send likeness photos to the FLUX API.** Local weights only.
- **Gemini free tier: human reviewers may read and annotate your inputs**, and content is used to improve products. **Paid tier: not used for training.** `OFFICIAL_DOCS` Free tier is disqualifying for reference photos of a real person; enforce in config, not convention.
- **Google made the *visible* watermark optional on 2026-08-14**; SynthID and C2PA metadata persist and must not be stripped.
- **Tapas still bans AI-generated content outright** (guidelines live; originating announcement 2023-01-23). **GlobalComix permits AI within a workflow involving human artistry and qualifying work CAN be monetized**, subject to disclosure and its discretion (policy updated 2026-03-20) — status **CONDITIONAL, seek written pre-clearance**. **WEBTOON Canvas terms are silent** on AI as of 2026-01-06 — silence is not safety. **Patreon** has no AI-art rule and is currently the best monetization surface. **Kickstarter** requires disclosure including consent for source works — a question answerable in your favour.
- A widely-ranking 2026 blog contradicts the primary sources on three of these platforms. It is wrong.
- **Runway's usage policy independently bans "characters based on the face or voice of a person under the age of 18."** The project's child-safety rule matches where the industry's hard lines actually are.

### C5. 🔴 Child-safety: one tool must be named and forbidden
**Reallusion Headshot 3 for CC5** (announced 2026-04-27) is marketed explicitly as *digital double creation* — photo to rigged 3D head, cloud-processed `OFFICIAL_DOCS`. It is precisely a child-likeness pipeline. **Forbidden.**

Also forbidden: any TTS voice clone from a child's recording (XTTS v2, Chatterbox both do ~5s zero-shot); Wan Animate / SCAIL-2 "Move" mode driven by home video of a child; any hosted mocap (Rokoko Vision) fed child footage; any LoRA trained on photos of a real child.

**Safe and fully adequate alternatives:** build the child as an **original design, not a likeness** — generate until it is right, declare that the character, train on the generated design. There is then no real-person referent to protect. For voice, **Kokoro-82M** (Apache 2.0, 54 fixed voices, **cannot clone by design** — its incapacity is the safety feature) or a hired adult voice actor, which is the anime industry norm anyway.

**And a genuine argument *for* the 3D layer:** a child proxy can be pure geometry — a scaled, non-photographic low-poly body emitting depth, pose and a segmentation mask, carrying no likeness, no reference photos, no trained model, no face. The face comes from the drawn style pass. This lets a child character occupy space correctly with **no identity data existing anywhere in the pipeline.**

### C6. Animation is gated, and the gate is specific
**Defer animation productionization, not animation research.** The one tool built for the intended workflow — ToonComposer (ICLR 2026), keyframes + sketches → inbetweens + colour — needs **~57 GB VRAM for 61 frames at 480p**, which is a routine cloud rental. Its released inference code, parameters and weights are **MIT** (verified 2026-08-31 from the LICENSE file); listed third-party components retain their own terms `OFFICIAL_REPO`. The field is also moving *away* from the needed interface: Wan Animate-2 (2026-08-07) and SCAIL-2 both **removed explicit pose conditioning** in favour of end-to-end driving-video conditioning, which suits VTuber/replacement work and not "I have a rig and want exact staging."

**Corrected rule (v2.1):** defer animation *productionization* until the first instrumented static chapter ships; do **not** defer animation *research*. A VRAM ceiling is not a strategic gate now that cloud GPUs are authorised, and a calendar date never was. Keep a ~5–10% horizon lane, cloud 48/80 GB, answering upstream architectural questions only. Re-evaluate quarterly.

**Time-critical:** the **Sora API is removed 2026-09-24**. Any doc still referencing Sora should be marked dead.

---

## D. Standing UNRESOLVED items (experiments, not reading)

| ID | Question | Why it can't be settled by research |
|---|---|---|
| U1 | Does native LoRA-hook masking actually hold two identities at production quality? | No published benchmark of the ComfyUI hooks system exists |
| U2 | Does Impact `RegionalSampler` work on Illustrious at acceptable harmony cost? | Docs concede harmony loss; no numbers |
| U3 | Generate-in-scene (sequential inpaint) vs composite vs regional — which wins on the same shots? | No study compares them |
| U4 | Does depth-conditioning flatten our specific style? | Style-dependent; unanswerable in the abstract |
| U5 | Real per-panel human minutes for the 3D route | Zero published figures; estimates only |
| U6 | Does the declared-state manifest actually cut review time? | Nobody has run it |
| U7 | Is identity preserved through an instruction edit? | **No benchmark isolates this.** Must build our own eval set |
| U8 | Does CANVAS's ContinuityEval assert against its global plan, or only measure pairwise similarity? | Could not determine from the paper — the most consequential gap found |
| U9 | Verbatim definition of "Non-Commercial Purpose" in the FLUX.2 [dev] licence | Gated repo, 401. **Read before monetizing** |
| U10 | ByteDance "Copyright and Portrait Feature Usage Rules" | Index page only; Seedream/Seedance likeness rules unknown |
