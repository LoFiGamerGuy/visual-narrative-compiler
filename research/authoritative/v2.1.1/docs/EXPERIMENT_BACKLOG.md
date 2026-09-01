# EXPERIMENT_BACKLOG.md

> ⚠️ **v2.1 — 2026-08-31.** This document has been corrected after independent
> verification by the project owner. **Read `docs/CORRECTIONS_V2_1.md` first**; it is
> the authority wherever it conflicts with anything here. Corrections are marked inline
> with ⚠️ v2.1.
Prioritized by expected value ÷ cost. **Every experiment has an explicit stop/go criterion written before it runs.** An experiment without a falsifiable stop condition is not an experiment, it is a hobby.

**Standing rule: every cycle must ship pages.** A cycle that produces only tooling has failed, regardless of how good the tooling is. The documented failure mode for solo pipeline projects is infrastructure that works and goes unused.

---

## Tier 0 — Do this week. Cheap, and two of them are compliance.

### X0.1 — InsightFace contamination sweep 🔴
**Do:** `ls ComfyUI/models/insightface/`; grep the graph library for `antelopev2`, `buffalo_l`, InstantID, IP-Adapter-FaceID, ReActor. Replace any identity-embedding conditioning with AuraFace or remove it.
**Cost:** 1 hour. **Go:** no non-commercial weights in any production path. **Stop:** n/a — this is not optional.

### X0.2 — Pin SAM 2, pin the ComfyUI commit
**Do:** freeze SAM 2 (Apache 2.0); record the ComfyUI commit hash; start writing it into every render record.
**Cost:** 1 hour. **Go:** two identical re-runs of one panel produce byte-identical output, or the difference is explained.

### X0.3 — Read the FLUX.2 [dev] "Non-Commercial Purpose" definition
**Cost:** 30 min. **Go:** definition is scoped to model distribution ⇒ dev is usable for production. **Stop:** definition sweeps in revenue-generating use ⇒ move production to klein 4B or buy the Builder licence.

### X0.4 — Likeness release + training-set inventory
**Do:** signed, dated, revocable release covering training, generation, derivatives, commercial publication, merchandising; list the vendors her images touch. Inventory every image in `datasets/`.
**Cost:** 1 hour. **Go:** signed and filed. No vendor supplies a substitute for this.

### X0.5 — Ratify and freeze the gauntlet
**Do:** review `bench/gauntlet.json`, cut or add shots, then **freeze**. Author the declared-state manifest for all 40.
**Cost:** 3 hours. **Go:** frozen, committed, and the freeze is respected thereafter.

### X0.6 — Script-side continuity check 🟢 **highest value-per-hour in the programme**
**Do:** LLM pass over the chapter-one script — span extraction, pairwise contradiction classification, evidence chains, JSON with character offsets.
**Why:** precision **0.884** / recall 0.550 vs human experts at 0.891 / **0.171** — a 3.2× error-discovery rate `PREPRINT`. Text-only, cents per chapter, and it **prevents** errors rather than detecting them.
**Cost:** 3 hours. **Go:** finds ≥1 real continuity bug in an existing script. **Stop:** three chapters, zero real findings ⇒ retire.

---

## Tier 1 — The identity bake-off. This decides the renderer stack.

**Protocol (v2.1, two-stage).** **Stage A smoke:** the 12-case subset named in `gauntlet.json`, 2 seeds (24 generations) — eliminates non-competitive or operationally impractical candidates cheaply. **Stage B full, finalists only:** all 40 render cases × 3 seeds = **120 renderer generations per arm**. QA controls (12 comparisons) and QA injections (8 cases) are **derived** and are not renderer generations. Never edit a case to flatter a candidate. Blind-scored. Report **Correct / Blend / Swap** rates (mutually exclusive, sum to 1), ID-Conf, candidates-per-acceptance, and **human minutes**. Embeddings via AuraFace or DINOv3 — never InsightFace. Calibrate thresholds on your own approved art; photographic ArcFace thresholds do not transfer to illustrated faces.

### X1.0 — Baseline: single-character ceiling
Run G01–G06 on the current stack. **Go:** Correct Rate ≥ 0.90. **Stop:** below that, the base model or LoRAs are the problem and no multi-character work is meaningful yet. **Run this before anything else in Tier 1.**

### X1.1 — Arm A: Illustrious v2 + ComfyUI **native LoRA hooks**, masked 🟢 *test first*

**Prerequisite, not optional:** both character LoRAs must be **retrained on the chosen Illustrious v2 base** from the existing adult source datasets, subject to the licence/provenance audit. The current LoRAs came from the Anima-family path and are **not interchangeable across architectures**. Budget ~90 min per character plus a validation sweep.
Masked LoRA via the hooks system (core since **2024-12-02**), not Impact Pack. Non-overlapping masks; identity trigger tokens **out of the base prompt**; `Set Default Combine` for uncovered area.
**Cost:** 1 day. **Go:** Swap ≤ 0.05 and Blend ≤ 0.10 across mirrored pairs. **Stop:** Blend > 0.25 ⇒ masked-weight patching is insufficient on this base.

### X1.2 — Arm B: Impact Pack `RegionalSampler` on Illustrious
Only meaningful on SDXL-family. `base_only_steps` to settle composition; `overlap_factor` for boundaries.
**Cost:** 1 day. **Go:** beats Arm A on identity **without** the harmony loss its own docs concede. **Stop:** requires per-panel ControlNet to avoid blur ⇒ fold into the 3D track rather than treating as standalone.

### X1.3 — Arm C: sequential inpaint / two Detailers, one LoRA each 🟢 *predicted winner on identity*
Stage the panel with no character LoRAs, then two Impact Detailers off person-SEGS, each fed a pipe carrying one LoRA. `bbox_crop_factor` is the lighting-integration knob; `feather` the blend.
**Cost:** 1.5 days. **Go:** highest Correct Rate of any arm. **Stop:** unmasked regions degrade measurably per pass (a known issue) beyond the two-sided repair thresholds.

### X1.4 — Arm D: Qwen-Image-Edit-2511 multi-reference
Apache 2.0, local, vendor claims "high-fidelity fusion of two separate person images into a coherent group shot" — **exactly this case**, and unbenchmarked by anyone.
**Cost:** 1 day. **Go:** matches Arm A/C identity with fewer candidates per acceptance. **Stop:** documented image drift (subject shifts position/size) exceeds thresholds — mitigate with pad-to-square + `Frequency Detail Restore` before abandoning.

### X1.5 — Arm E: Nano Banana Pro staging, local identity finish
API for composition (claims 5-person consistency), then a local low-denoise LoRA pass to re-assert identity. **Paid tier only.**
**Cost:** 0.5 day + ~$15. **Go:** best staging score. **Stop:** filter refusals on the two leads make it unreliable.

### X1.6 — Do LoRAs still beat reference conditioning? ⭐
Cross-cut: Arm C (LoRA) vs Arm D/E (reference) on identical shots.
**Prior:** LoRAs win. Best published multi-subject Face-Sim is **0.5284**; a rank-16 LoRA on 30 photos should exceed it. Also watch for the **copy-paste artifact** — reference methods pasting the face rather than re-rendering it under new pose and light, which reads as collage in a comic.
**Go:** LoRA advantage ≥ 0.1 similarity ⇒ keep LoRAs as identity authority. **Stop:** reference matches LoRA ⇒ drop LoRA maintenance entirely and gain model portability.

---

## Tier 2 — The 3D question. Run the cheap version before the expensive one.

### X2.1 — One-day bake-off: 3D blockout vs reference conditioning ⭐ **do before any set building**
One hard panel — two figures, one seated behind a table (G09a) — three ways: (a) current composite, (b) Blender proxies → depth → ControlNet, (c) Qwen-Image-Edit reference conditioning from three plates.
**Why first:** this single test produces better evidence than anything published, and it gates a 40+ hour set-building commitment.
**Cost:** 1 day. **Go:** (b) fixes occlusion and scale that (a) and (c) cannot ⇒ proceed to X2.2. **Stop:** (c) matches (b) ⇒ the 3D layer's marginal value collapses; stay 2D and save weeks.

### X2.2 — Boxy vs detailed conditioning ⭐ *counter-intuitive, cost-reducing*
Same shot, deliberately crude proxies vs a detailed set.
**Prior:** LooseControl `PEER_REVIEWED` — exact depth is a trap; boxy is better *and* cheaper.
**Go:** crude ≥ detailed ⇒ **build all sets crude**, saving most of the modelling budget. **Stop:** detailed wins clearly ⇒ accept the cost and re-estimate the set budget upward.

### X2.3 — Control stacking limit
Depth alone vs depth+pose vs depth+pose+lineart+seg.
**Prior:** multi-ControlNet composition causes severe artifacts `PREPRINT`.
**Go:** identify the maximum stack before artifacts. **Stop:** anything beyond one primary + one secondary degrades ⇒ hard-cap it in the workflow.

### X2.4 — Build the kitchen set, crude, with occluders
Only after X2.1/X2.2 pass. **Cost:** 8–20 hours.
**Go:** occluder authoring cost for new cameras in that room drops to **zero** — the specific pain from `north-garden-page-methods.md`. **Stop:** >30 hours without a usable set ⇒ the 3D route is too expensive for a solo operator.

### X2.5 — Reverse-angle set identity (G19 vs G20)
The least-served problem in the entire literature. Compare: canonical 3D · establishing-plate reference conditioning · per-location LoRA.
**Go:** ≥4 of 5 named landmarks present and correctly placed across both cameras. **Stop:** none reach it ⇒ **write the story around it** — avoid reverse angles in recurring rooms, which is a legitimate directorial answer.

### X2.6 — Child geometry proxy 🔴 safety-relevant
Scaled non-photographic low-poly body on the rig; emits depth, pose, seg mask; face from the style pass only.
**Go:** the character stages correctly with **zero identity data anywhere in the pipeline**. This is both a safety win and an argument for the 3D layer.

---

## Tier 3 — QA and repair. Cheap first, ML last.

### X3.1 — Gate 1 lint (deterministic, zero-ML)
Balloon geometry, balloon count vs script lines, reading order, webtoon slice boundaries never within 24px of a face or balloon, duplicate-panel pHash.
**Cost:** 1 day. **Go:** zero false positives on an approved chapter. These are asserts, not heuristics.

### X3.2 — Gate 2 drift (numpy, scene-scoped)
Median L\* delta, CIELAB histogram EMD, set-crop SSIM/LPIPS, character count, prop presence.
**Critical:** thresholds **scene-scoped**, never chapter-scoped — a night scene must not be compared to a day scene. Calibrate on two approved chapters: validation split → freeze → test.
**Cost:** 1.5 days. **Go:** ≤4 false positives per check family on an approved chapter.

### X3.3 — FiftyOne review loop
Adopt, don't build. Apache 2.0, local, embeddings panel shows drift as a visible smear.
**Go:** human review of a flagged chapter in ≤20 minutes. **Stop:** setup exceeds 4 hours ⇒ fall back to a 200-line Streamlit grid and lose similarity search.

### X3.4 — VLM confirmation, top-15 only
One binary question per call, manifest-conditioned, enum outputs, `cannot_determine` first-class, **never a leading question**, **no majority voting** (reliability without validity — you reproduce the same bias 3×). Flash-class + batch.
**Go:** eliminates ≥40% of Gate-2 false positives without discarding real findings. **Stop:** confirms hallucinated problems ⇒ demote to advisory and never let it gate.

### X3.5 — Two-sided repair gate ⭐
Target region **must change** (masked LPIPS > 0.15) **AND** remainder must not (SSIM > 0.95, LPIPS < 0.10). Max 2 iterations.
**Why two-sided:** the documented **under-editing trap** — models post inflated consistency scores by silently not performing the edit. A one-sided gate makes CI go green while the drift ships.
**Go:** ≥70% of repairs pass both sides. **Stop:** below 40% ⇒ regenerate rather than repair.

### X3.6 — Does identity survive an edit? ⭐ **no benchmark exists; build one**
Re-run the identity check on repaired panels.
**Go:** repaired panels still pass. **Stop:** they don't ⇒ every repair needs a LoRA re-assert pass appended.

---

## Tier 4 — Chapter qualification

### X4.1 — Ship chapter one, instrumented ⭐ **the most valuable experiment in the programme**
Full 50–90 panels through the winning stack. **Time every stage with a real timer.**
**Why:** there are **zero** published measured hours-per-chapter figures for AI-assisted comics. After one chapter you will have better data than the literature.
**Go:** ≤30 hours, ≤4 candidates per acceptance. **Stop:** >50 hours ⇒ the pipeline is not viable for a serial; cut scope or panel count.

### X4.2 — Reproduce a panel from metadata alone
Delete a render, regenerate from its RenderRecord.
**Go:** byte-identical, or the difference is fully explained by a recorded version change. **This is the test that proves the architecture is real** rather than decorative.

### X4.3 — Chapter two, same sets
**Go:** measurably faster than chapter one ⇒ the reuse thesis holds and 3D break-even (predicted at chapter 2–3) is confirmed. **Stop:** no speedup ⇒ the amortization argument is false and the 3D investment should be halted.

---

## Tier 5 — Deferred, gated, or explicitly not doing

| Item | Status | Gate / reason |
|---|---|---|
| Animation **productionization** | **Deferred until the first instrumented chapter ships** | Not a calendar date and not a VRAM ceiling (both withdrawn v2.1) |
| Animation **research** | **OPEN — ~5–10% of effort** | Cloud 48/80 GB authorised. Answers upstream architectural questions only: will these rigs, poses, cameras and set assets still be usable later? ToonComposer is **MIT** and needs ~57 GB — a routine rental. Re-check quarterly |
| Cascadeur Indie | **Buy when animation opens** | $96/yr, perpetual after 1yr, quadruped-aware, MCP-scriptable |
| OpenUSD | **Design toward, don't adopt** | Keep stable object/camera names so export is mechanical |
| OpenTimelineIO | **When you cut video** | Pre-1.0 after nine years; 0.19 unreleased ~21 months |
| C2PA signing | **When a platform asks** | RenderRecord already holds everything a manifest needs |
| Kitsu / AYON / ftrack | **Not doing** | Coordinate people; you have one. Trigger: a second human joins |
| MaterialX | **Never** | One renderer; solves a problem you don't have |
| Environment LoRA | **Retired as primary** | No first-hand account of anyone training one for a comic, in either research pass |
| Marble / world models | **Look-dev only** | Vendor concedes mesh is a byproduct. **Pro tier minimum for commercial rights; never upload child images** |
| Second renderer adapter | **Not until earned** | One implementation behind an interface is a guess about the second |
