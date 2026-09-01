# RESEARCH_BRIEF_V2.md

> ⚠️ **v2.1 — 2026-08-31.** This document has been corrected after independent
> verification by the project owner. **Read `docs/CORRECTIONS_V2_1.md` first**; it is
> the authority wherever it conflicts with anything here. Corrections are marked inline
> with ⚠️ v2.1.
**North Garden Visual Narrative Compiler — research findings, v2**
2026-08-31 · Six parallel research tracks · Supersedes the v1 failure log, which remains valid as evidence

Evidence tags: `OFFICIAL_DOCS` `OFFICIAL_REPO` `PEER_REVIEWED` `PREPRINT` `PRACTITIONER` `COMMUNITY` `ANECDOTAL`

---

## 1. Executive summary

The proposed architecture — canon, geometry, shot state and QA outside the models; models as replaceable renderers — **is substantially correct, and three of its seven load-bearing hypotheses are wrong in ways that matter.**

**Survives:** Blender as spatial truth (narrowed); canonical 3D for recurring sets (strongly, and it is standard non-AI webtoon practice already); ComfyUI behind an adapter (with stronger justification than expected — its maintainers admit there is no interface contract).

**Wrong, and correctable:**
1. **One ShotIR cannot serve both comic and animation.** An anime e-conte carries timing; a comic panel does not. The field stays permanently null. Split `SceneRecord` (shared) from `PanelSpec` / `ShotSpec` (separate).
2. **Per-region LoRA was the right instinct pointed at the wrong tool.** ComfyUI has shipped native masked LoRA since 2024-12-02 in core. Impact Pack's `RegionalSampler` probably does not even work on the 2026 models.
3. **The VLM drift auditor is the *last* thing to build, not the first.** VLMs detect visual differences at ~45–48% against an 89.75% human baseline, and confabulate when asked leading questions. The valuable artifact is a **declared-state manifest**, which contains no machine learning at all.

**Three findings that change decisions already taken:**
- 🔴 **InsightFace pretrained weights are non-commercial-research-only** and are auto-downloaded by common face-consistency nodes. This silently contaminates commercial pipelines.
- 🔴 **The FLUX API trains on your inputs by default**, and Gemini's free tier exposes them to human reviewers. Neither may receive photographs of a real person.
- 🔴 **Tapas still bans AI art; Kling forbids commercial use of outputs.** GlobalComix permits AI within a workflow involving human artistry and **qualifying work can be monetized**, subject to disclosure and its discretion — status **CONDITIONAL, seek written pre-clearance**.

**The most important unresolved question is economic, not technical**: there are **zero** published measured hours-per-chapter figures for AI-assisted comics, and **no production account anywhere** of image-side automated continuity QA at chapter scale. One instrumented chapter will produce better data than the entire literature.

---

## 2. What the evidence actually says

### 2.1 The strongest single finding: cruder is better

LooseControl (Bhat/Mitra/Wonka, **SIGGRAPH 2024**, arXiv 2312.03079) `PEER_REVIEWED` argues that exact-depth ControlNet is a trap — producing realistic depth for cluttered scenes is *"probably as challenging as solving the original task"* — and demonstrates that **boxy scene boundaries plus bounding boxes suffice**.

This inverts the natural instinct and it is **cost-reducing**: a beautifully modelled set is *worse* conditioning than a blocky one. Combined with arXiv 2510.21763 `PREPRINT` (*"multi-ControlNet composition causes severe artifacts"*), the operating point is: **crude geometry, one primary control, at most one secondary.**

The strongest argument for the 3D layer, though, comes from this project's own failure log rather than any paper: occluder polygons are currently hand-authored per room. In a real 3D set that cost goes to **zero, permanently**.

### 2.2 Reference encoders have not surpassed LoRAs

Best published multi-subject face similarity: **MultiCrafter 0.5284**, XVerse 0.4117, OmniGen2 0.2453, UNO 0.1474 (CVPR 2026) `PEER_REVIEWED`. A rank-16 LoRA on 30 curated photos beats all of them for a recurring lead.

Two further reasons to keep LoRAs: the **copy-paste artifact** — reference methods paste the reference face rather than re-rendering identity under new pose and light, which reads as collage in a medium where every panel is a new angle `PREPRINT`; and the **semantic shortcut** — models trade identity fidelity for text alignment as prompts densify `PREPRINT`, and comic prompts are dense by nature.

**But:** LoRAs are architecture-locked and worthless the moment the base changes — in a market that shipped FLUX.2, Qwen-2511 and Nano Banana Pro inside six months. **Synthesis: reference-conditioning for staging and composition, LoRA-patched refinement for identity.** Not either/or.

### 2.3 Identity collapse is real but we are on the flat part of the curve

arXiv 2603.26078 `PREPRINT` documents an *"illusion of scalability"*: methods look fine at 2–4 subjects and undergo catastrophic collapse beyond, with subject-collapse rates of 96–97% at ten subjects. **At n=2 all methods are in their competent regime.**

The relevant warning is the tier structure: **Neutral → Occlusion → Interaction**, where Interaction (physically engaged figures) is hardest. For a two-hander domestic drama, **the hardest tier is also the most common panel type.** The gauntlet stratifies accordingly.

### 2.4 VLMs are poor detectors and the human ceiling is low

| Task | Human | Best model |
|---|---|---|
| Inter-state visual difference detection (M³-Verse) | **89.75%** | Gemini-2.5-Pro 47.58% · GPT-5 45.14% |
| Difference captioning BLEU-4 (OmniDiff) | — | task-specific 14.3 vs **GPT-4o 3.1** |
| Visual narrative coherence, inter-annotator ρ (VCMS) | **0.41–0.54** | VLM reaches 95% *of that ceiling* |

`PREPRINT` / `PEER_REVIEWED`. M³-Verse also reports a ~12.32-point gap between **hallucination-centric and factual questions** — that is not a general leading-question penalty. The related qualitative concern rests on separate evidence: DiffSpot's best model detects only **~40.7%** of true fine-grained changes and deliberately uses **no-change controls**, because fabricated differences are a real failure mode. Add judge unreliability: κ 0.376–0.511 with humans across ~541k judgments; exact-match agreement overstates chance-corrected agreement by 34–41 points; **test-retest >0.95 masks severe bias, so self-consistency voting does not help** `PREPRINT`.

**Design consequence:** deterministic CV detects; the VLM only confirms, on the top-K, one binary manifest-conditioned question at a time, with `cannot_determine` as a first-class answer.

### 2.5 The one mechanism that distinguishes intent from drift

No published system can tell "she took her coat off" from "the model forgot her coat" by looking at images. ConStory-Bench states it as a limitation; Audit & Repair compares panels to each other, so every intentional wardrobe change is *by construction* a detected error `PREPRINT`.

**The fix removes the judgment from the model.** If the manifest declares `coat: on` for panels 1–22 and `coat: off` for 23–70, then "coat missing in panel 30" is a **lookup**, and the VLM's job shrinks from a question it answers at 45% to one it answers well.

**The declared-state manifest is the highest-value artifact in the QA design, and it contains no ML.**

### 2.6 The cheapest, highest-precision check is on the script

ConStory-Checker: **precision 0.884 / recall 0.550** on 1,000 injected errors, versus human experts at 0.891 / **0.171** — a **3.2× error-discovery rate** `PREPRINT`. Errors cluster at the **40–60% narrative position**.

Text-only, cents per chapter, and it **prevents** errors instead of detecting them after they are rendered. **This was not in the original plan and it is the best value-per-hour item in the programme.**

### 2.7 The under-editing trap

GEditBench v2 `PREPRINT` documents models posting *inflated* consistency scores alongside collapsed instruction-following — **they preserve the background beautifully by not performing the edit.**

**Any repair gate must be two-sided:** the target region must change **and** the remainder must not. A one-sided gate makes CI go green while the drift ships.

### 2.8 Comic and animation do not share a shot language

The e-conte consists of *"scene illustrations, timing information, and textual descriptions"* (Griffith, **CHI 2024**) `PEER_REVIEWED`. A comic panel encodes composition, reading order, and *implied* duration. The map from gutter width to seconds is a directorial decision, not a function.

Independently: 3D layout artists rebuild boarded shots because *"2D animatic is often cheatable in terms of character scale, perspective or distance. But cheating these properties in a 3D layout is not that easy"* `PRACTITIONER`. **Good comic panels are built on cheats that will not resolve into a consistent 3D camera.**

**Transfers:** story, dialogue, voice IDs, identity assets, 3D environments, camera position/lens. **Does not:** composition, timing, cut count. Assets, canon and story state transfer; directing decisions do not. *(Earlier percentage estimates are withdrawn — they were intuition, not measured project data.)*

### 2.9 Animation is gated, specifically

ToonComposer (**ICLR 2026**) — keyframes + sketches → inbetweens + colour — is exactly the right tool and needs **~57 GB for 61 frames at 480p**, with an unverified licence `OFFICIAL_REPO`. Worse, the field is moving away from the needed interface: Wan Animate-2 (2026-08-07) and SCAIL-2 both **removed explicit pose conditioning**.

**Corrected rule:** defer animation *productionization* until the first instrumented static chapter ships; do **not** defer animation *research*. Keep a ~5–10% horizon lane on cloud 48/80 GB GPUs, answering upstream architectural questions only. A VRAM ceiling is not a strategic gate now that cloud is authorised, and a calendar date never was one. ToonComposer's released code, parameters and weights are **MIT** (verified from the LICENSE file); third-party components retain their own terms. **The Sora API is removed 2026-09-24** — mark any doc referencing it dead.

---

## 3. Contrary evidence, collected

The handoff asked for evidence *against*. Here it is in one place.

1. **No verified precedent.** Not one solo creator shipping a substantial AI-assisted comic on an IR-first pipeline could be found, in either research pass. The positive case rests on academic systems evaluated on benchmarks, not on shipping 40 chapters.
2. **The abandonment base rate.** A documented solo natural experiment: an artist stood up Kitsu successfully (Aug 2021), reported by Dec 2021 *"I've just not been using it all that much,"* found the Blender addon hard-coded to Blender Studio's layout (Jan 2022), and had abandoned it by Sept 2022 `PRACTITIONER`. **Note the shape: the system worked; it went unused.**
3. **Every cited system derived its schema from a working renderer**, not before one. MangaFlow's memory fields are exactly what its renderer needed as conditioning. Schema-before-renderer will produce the wrong fields.
4. **The IR does not fix what is broken.** MangaFlow, with full agentic decomposition, still reports *"character rendering failures persist"* and that quality *"depends on the underlying image generation backbone."*
5. **Nobody runs image-side continuity QA in production.** Two targeted searches returned only SEO content. Either it is not valuable enough to have been built, or it is harder than it looks.
6. **Audit & Repair's code was never released** — "coming soon," ~14 months on — and it reports **no precision or recall for its own detection step**. Neither does CANVAS. Neither does ViStoryBench. The only precision/recall numbers in the field are text-side.
7. **Genre skew.** A survey of 19 AI comics found the medium clusters in sci-fi/horror because those tolerate atmospheric, single-character, face-obscured imagery, and struggles with *"quieter slice-of-life stories."* **This project is the documented hard case.**
8. **3DGS is not geometric truth.** Photogrammetry beats it on metric accuracy on opaque structured surfaces `PEER_REVIEWED`; splats have no reliable occlusion boundary — the exact failure being solved.
9. **World-model mesh is a byproduct.** Marble's own docs concede reconstruction artifacts and recommend splat export for fidelity `OFFICIAL_DOCS`.
10. **Reader backlash exceeds policy risk.** Subscription cancellations across RIDI/Manta/Kakao/LEZHIN over AI localization (2025-11) `COMMUNITY` — the only empirical revenue-side signal found, and it points down.

---

## 4. Where the research was weak

Stated so the next pass targets it rather than repeating it.

- **Reddit was inaccessible** to the research agents (403), removing r/StableDiffusion, r/comfyui and r/webtoons — almost certainly where the best practitioner detail lives. **Worth a direct human look.**
- **Civitai articles are gated**; two directly relevant titles were visible but unreadable.
- **CHI 2026, "AI in Webtoon Creation: Challenges, Perceptions, and Design Implications"** (DOI 10.1145/3772318.3790343) is paywalled. **The single most relevant academic source to this project. Obtain it.**
- **Runway is a blind spot** — the developer portal is JS-only; no model list, pricing, or duration data could be retrieved.
- **Consistency percentages** widely quoted (84% / 87.5%) come from one author with no published methodology.
- **Much 2026 pricing** came from SEO aggregators rather than vendor docs, and is tagged `COMMUNITY`. Re-verify before committing spend.
- **Practitioner failure cases for 3D-blockout-to-diffusion** are in Discords and deleted threads, not indexed pages. No clean documented abandonment was found — this is a weak-evidence area in *both* directions.

---

## 5. The ten open questions, re-ranked

| Rank | Question | Was | Why it moved |
|---|---|---|---|
| 1 | **What does a chapter actually cost in human minutes?** | Q10 | Zero published figures. Settles the QA-vs-beauty hypothesis. One chapter beats the literature |
| 2 | **Does masked-LoRA (native hooks) hold two identities?** | Q1 | Mechanism corrected — hooks, not RegionalSampler |
| 3 | **Generate-in-scene vs composite vs regional, same shots** | Q2 | Unchanged. No study compares them |
| 4 | **Does 3D blockout beat reference conditioning on the hardest panel?** | Q3 | Now a *one-day* test that gates a 40-hour commitment |
| 5 | **Does the declared-state manifest cut review time?** | new | Replaces "build a VLM auditor" as the QA thesis |
| 6 | **Set continuity from new angles** | Q4 | Least-served problem in the literature. Unchanged |
| 7 | **Does identity survive an instruction edit?** | new | **No benchmark isolates this.** Must build our own |
| 8 | **Automated drift audit** | Q5 | **Reframed** — deterministic CV detects; the VLM is a non-gating sensor for narrow closed-form assertion checks, benchmarked with no-change controls |
| 9 | **Style LoRA and the simplicity ceiling** | Q7 | Unchanged. A *simpler* style has a higher ceiling |
| 10 | **The subtractive-power problem** | Q8 | Art direction, not engineering. Still open |

*Q6 (instruction-edit as the correction loop) is now folded into #7 and the two-sided repair gate. Q9 (panel-record architecture) is answered in `ARCHITECTURE_V0_1.md`.*

---

## 6. What I would bet on, stated so it can be falsified

1. **Sequential inpainting with one LoRA active per region wins on identity**, and Nano Banana Pro or Qwen-Image-Edit wins on staging. The production stack is staging by one, identity by the other.
2. **Crude 3D beats detailed 3D**, and the set-building budget is roughly half what it looks like.
3. **The declared-state manifest plus deterministic lint catches most of what matters**, and the VLM contributes less than 20% of real findings.
4. **Chapter one takes 25–40 hours**, not the 15–30 estimated — and chapter two takes materially less, confirming the reuse thesis.
5. **The biggest risk is not technical.** It is that this system gets built and then not used. Every cycle must ship pages.

---

## Deliverables in this set

| File | Contents |
|---|---|
| `docs/RESEARCH_BRIEF_V2.md` | This document |
| `docs/ARCHITECTURE_V0_1.md` | Data model, storage, renderer boundary, generation stack, QA architecture, and what it does not solve |
| `docs/DECISION_LOG.md` | KEEP / REPLACE / RETIRE / UNRESOLVED on every prior finding and all seven challenged hypotheses |
| `docs/EXPERIMENT_BACKLOG.md` | Prioritized experiments with explicit stop/go criteria |
| `docs/NEXT_ACTIONS.md` | Sequenced plan, purchases, publishing posture, and what not to do |
| `bench/CONTINUITY_GAUNTLET.md` + `bench/gauntlet.json` | The frozen 40-shot benchmark, metrics and targets |
| `registry/CANDIDATE_REGISTRY.md` + `candidates.json` | 53 candidates with licence, commercial use, data treatment, API, hardware, maintenance, role |
| `registry/POLICY_LICENSE_REGISTRY.md` | Re-audited vendor policy, model licensing, platform policy, compute economics, child-safety register |
