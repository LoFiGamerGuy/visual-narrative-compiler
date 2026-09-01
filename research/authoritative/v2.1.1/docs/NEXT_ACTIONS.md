# NEXT_ACTIONS.md

> ⚠️ **v2.1 — 2026-08-31.** This document has been corrected after independent
> verification by the project owner. **Read `docs/CORRECTIONS_V2_1.md` first**; it is
> the authority wherever it conflicts with anything here. Corrections are marked inline
> with ⚠️ v2.1.
Prioritized. Ordered by *evidence gained per hour*, with compliance first. 2026-08-31.

**Governing rule: every cycle ships pages.** The documented failure mode for solo pipeline projects is not technical failure — it is infrastructure that works and goes unused. If a cycle produces only tooling, the cycle failed.

**Second rule: do not build the new renderer stack until the benchmark and the data records exist.** That is the handoff's instruction and the research supports it — every prior system derived its schema from a working renderer, and you have one.

---

## This week — compliance and cheap wins (≈10 hours)

| # | Action | Hours | Why now |
|---|---|---|---|
| 1 | **InsightFace inventory + quarantine** (v2.1 — *not* delete). `ls ComfyUI/models/insightface/`; record path, sha256, source, licence state and dependent nodes; make production profiles refuse restricted weights; evaluate AuraFace | 1.5 | 🔴 Restricted weight files, silently auto-downloaded. Quarantine preserves the evidence of which prior metrics used them, and keeps a commercial licence open as an option |
| 2 | **Pin SAM 2. Pin the ComfyUI commit** and start writing the hash into every render record | 1 | SAM 3 changed licence 2025-11-19. ComfyUI has no interface contract — issue #11833 shows a saved workflow JSON is a snapshot, not an artifact |
| 3 | **Read the FLUX.2 [dev] "Non-Commercial Purpose" definition** | 0.5 | Gated (401). Load-bearing for whether dev is usable in production at all |
| 4 | **Likeness release + training-set inventory** | 1 | No vendor supplies a consent mechanism. Your paperwork is the only protection |
| 5 | **Ratify the benchmark's SEMANTIC freeze** (40 render cases; G01–G30 intent immutable) and author the declared-state manifests. Note it is **not yet an executable frozen harness** — the `BenchmarkCaseBundle` cannot be authored until arm 1 exists | 3 | Everything downstream is measured against it |
| 6 | **Script-side continuity check on chapter one** | 3 | ⭐ Best value-per-hour in the programme: P=0.884 vs human experts' R=0.171. Prevents rather than detects |

**Do not** start the Illustrious LoRA retrain yet — item 8 may change which base you train on.

---

## Next two weeks — decide the stack (≈2 weeks)

| # | Action | Days | Stop/go |
|---|---|---|---|
| 7 | **X1.0 single-character baseline** on the frozen gauntlet | 0.5 | Correct Rate ≥ 0.90, or nothing downstream is meaningful |
| 8 | **Two-stage bake-off** (v2.1). **Stage A smoke** — 12-case subset × 2 seeds, across: `baseline_legacy` · Illustrious-v2 + **core masked-LoRA hooks** · Qwen-Image-Edit-2511 · sequential per-character inpaint · Blender-grounded variant. **Stage B full** for finalists only (40 render cases × 3 seeds). ⚠️ The Illustrious arm **requires retraining both character LoRAs on the chosen Illustrious v2 base** — the existing ones came from the Anima-family path and are not interchangeable across architectures | 5 | Winner on Correct/Blend/Swap **and** human minutes |
| 9 | **X2.1 one-day 3D bake-off** on the single hardest panel, before any set building | 1 | If reference conditioning matches 3D blockout, the 3D layer's value collapses and you save weeks |
| 10 | **X2.2 boxy vs detailed conditioning** | 0.5 | Counter-intuitive and cost-*reducing* if crude wins |
| 11 | **Write SceneRecord / PanelSpec / RenderRecord** and migrate the existing chapter-one panels into them | 2 | Legitimate now that a renderer exists; would not have been six months ago |
| 12 | **X4.2 reproduce one panel from its RenderRecord alone** | 0.5 | The test that proves the architecture is real rather than decorative |

---

## Weeks 3–6 — QA, then ship

| # | Action | Days |
|---|---|---|
| 13 | Gate 1 lint (deterministic, zero ML) | 1 |
| 14 | Gate 2 drift (numpy, **scene-scoped** thresholds, calibrated on approved chapters) | 1.5 |
| 15 | FiftyOne review loop — adopt, don't build | 0.5 |
| 16 | Two-sided repair gate (target must change **and** remainder must not) | 1 |
| 17 | Build the kitchen set crude with occluders — **only if #9 and #10 passed** | 2–3 |
| 18 | ⭐ **Ship chapter one, instrumented with a real timer** | 5–8 |

**#18 is the most valuable single item on this list.** There are zero published measured hours-per-chapter figures for AI-assisted comics. One instrumented chapter gives you better data than the entire literature, and it settles the one hypothesis research could not: whether QA and repair really do dominate first-pass beauty.

---

## Purchases — recommended now

| Item | Cost | Justification |
|---|---|---|
| Cloud GPU account (RunPod or Lambda), **first-party/Secure tier** | pay-as-you-go, ~$3–6 per LoRA run | Train on an 80GB card, generate locally. **Never put likeness data on Community Cloud or Vast** |
| Gemini API **paid tier** | ~$34–134/chapter, half with batch | Free tier has human review and trains on your inputs — disqualifying for reference photos of a real person |

## Purchases — deliberately deferred

| Item | Cost | Gate |
|---|---|---|
| Marble Pro | $35/mo | Only if X2.5 shows world-model plates beat canonical 3D for set continuity. Never upload child images |
| Cascadeur Indie | $96/yr | When the animation gate opens. Best value in the report when it does |
| Character Creator 5 | $299 perpetual | Animation transition only |
| DaVinci Resolve Studio | $295 | Start Free; buy when you hit a named wall |
| Toon Boom Harmony | $1,128/yr | **Skip.** Studio tool for trained 2D staff; worse scripting than Blender |
| Rokoko suit | $$$$ | **Skip.** Cannot drive a quadruped without heavy retargeting; Cascadeur addresses the same need |

---

## Publishing posture — decide before chapter one ships

- **Patreon** = monetization. **WEBTOON Canvas** = audience (terms silent on AI; silence is not safety). **GlobalComix** = distribution only, disclosed, **cannot be monetized**. **Tapas** = closed, still bans AI. **Kickstarter** = viable with full disclosure.
- **Disclose proactively, early, in your own voice**: which models, what is human, that both depicted adults consented in writing, and that no child likeness model exists. In this market that statement is an asset; disclosure extracted by an accusation thread is a liability. Reader backlash currently exceeds policy risk.

---

## What NOT to do next

1. **Do not tune prompts.** The gauntlet does not exist yet; you would be optimizing against an unmeasured target — which is exactly how the last eight months went.
2. **Do not build a second renderer adapter.** One implementation behind an interface is a guess about the second.
3. **Do not adopt OpenUSD, OTIO, Kitsu, AYON, or MaterialX.** Design toward USD by keeping stable object and camera names; adopt nothing else until a named trigger fires.
4. **Do not make a VLM a gate.** It is a non-gating sensor for narrow closed-form assertion checks, benchmarked with no-change controls and reported as recall *and* false-alarm rate. VLMs score ~45% against a ~90% human baseline on **open-ended** difference detection; that number does not automatically transfer to constrained checks, which is why they must be measured separately rather than assumed useless.
5. **Do not scan 70 acres.** Terrain from the plat; photogrammetry for 5–10 hero objects; splats never in the truth path.
6. **Do not build the animation production system.** But do **not** freeze animation research either (v2.1) — keep a ~5–10% horizon lane on cloud GPUs, answering only upstream architectural questions about rigs, poses, cameras and asset reuse.
7. **Do not train LoRAs on NoobAI checkpoints.** Their model cards carry an explicit commercial prohibition covering the model, derivatives and generated products. (FAIPL share-alike is a secondary reason.)
8. **Do not build on Sora.** The API is removed **2026-09-24**.

---

## The three things most likely to be wrong in all of this

Stated so they get attacked rather than inherited:

1. **That the pipeline gets built and then used.** The single documented solo natural experiment in adopting production tooling ended in quiet abandonment after a year — and the system *worked*. This is the highest-probability failure mode in the programme and no amount of architecture prevents it. Only shipping pages does.
2. **That QA and repair dominate first-pass beauty.** Plausible, unverified, and **no production account of image-side continuity QA at chapter scale exists anywhere.** Either it isn't valuable enough to have been built, or it's harder than it looks. #18 settles it.
3. **That any of this beats a locked 6-panel grid, an aggressively simple style, and hand-finishing the 10% of panels that matter.** That combination is what every professional-looking AI comic actually did. Three of those four are taste, and one is a grid — and none of them are in the schema.
