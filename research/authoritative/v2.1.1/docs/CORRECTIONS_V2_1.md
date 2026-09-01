# CORRECTIONS_V2_1.md
**Applied 2026-08-31, after independent verification by the project owner.**
Codex: this file is the authority where it conflicts with anything else in the package. Every correction below has been applied to the source documents; this record exists so the *reasoning* is not lost.

---

## Verification status of each correction

| # | Correction | Verified by | Status |
|---|---|---|---|
| 1 | GlobalComix permits monetization of qualifying AI-assisted work | **Owner**, live policy page (last updated 2026-03-20) | ✅ Applied. **I could not independently re-fetch** — globalcomix.com/ai-policy is JS-rendered and returns 403 to my fetcher and to r.jina.ai. Recorded on the owner's reading, attributed |
| 2 | ToonComposer is MIT | **Me**, this session — fetched `raw.githubusercontent.com/TencentARC/ToonComposer/main/LICENSE` | ✅ **Confirmed verbatim.** My researcher never fetched the LICENSE file |
| 3 | M³-Verse 12.32-point figure was mis-framed | Owner | ✅ Applied |
| 4 | SCRFD/RetinaFace architectures are not themselves non-commercial | Owner | ✅ Applied |
| 5 | InsightFace: quarantine, don't delete | Owner | ✅ Applied |
| 6 | NoobAI: explicit commercial prohibition is the simpler reason | Owner | ✅ Applied |
| 7 | Animation: reject the ≤24GB and 12-month gates | Owner | ✅ Applied |
| 8 | VLM optional/non-gating, benchmarked earlier | Owner | ✅ Applied |
| 9 | Two-stage bake-off (smoke → full) | Owner | ✅ Applied |
| 10 | Blender spatial modes | Owner | ✅ Applied |
| 11 | Vendor registry needs endpoint granularity | Owner | ✅ Applied |
| 12 | Drop the ~70%/~0% reuse figures | Owner | ✅ Applied |

---

## 1. GlobalComix — my error, corrected

**What v2 said:** "permits AI but bars it from monetization entirely."

**What is actually the case**, per the current AI policy (last updated **2026-03-20**): fully AI-generated works are removed, but **AI used as part of a broader workflow involving human artistry is permitted and qualifying work CAN be monetized**, subject to disclosure and appropriate rights. GlobalComix retains discretion over what constitutes sufficient human artistry.

**Where my researcher went wrong:** it read the general support/FAQ page, not the dedicated AI policy page, and did not notice the FAQ was stale relative to a policy revised in March 2026. A stale secondary page beat a current primary one — the exact failure the evidence rules were supposed to prevent.

**New classification: 🟡 CONDITIONAL — SEEK WRITTEN PRE-CLEARANCE.** Not "allowed," not "barred." This project sits near the boundary because generative models may render a large share of the visible final art, and the discretion clause is real. Approach them with representative pages and an honest workflow description once pages exist.

## 2. ToonComposer — my error, corrected and independently confirmed

**What v2 said:** "licence unverified."

**Verbatim from the LICENSE file, fetched this session:**
> "ToonComposer is licensed under the MIT License except for the third-party components listed below, which is licensed under different terms."
> "ToonComposer refers to the inference code, parameters and weights made publicly available by Tencent in accordance with the MIT License."

Third-party components (e.g. Wan2.1, Apache-2.0) retain their own terms. **The ~57 GB VRAM figure for 61 frames at 480p stands.** Only the licence claim was wrong. Still audit base-model and third-party terms before production use.

## 3. M³-Verse — overstated, corrected

**What v2 said:** "a −12.32 point drop on hallucination-eliciting prompts — and 'find the inconsistency' is a leading question by construction."

**What the paper reports:** a ~12.32-point gap between **hallucination-centric and factual question performance**. That is not a general "leading questions cost you 12 points" penalty, and I conflated a measured result with a design inference.

**The qualitative concern survives on separate evidence.** DiffSpot (arXiv 2605.29615) finds its best model detects only **~40.7%** of true fine-grained changes and deliberately includes **no-change controls** because fabricated differences are a real failure mode. So: wording that asserts a difference exists can prime hallucination — supported — but the 12.32 number does not measure that.

**Consequence for the design:** unchanged in direction (neutral wording, closed-form questions, controls), but the claim must not be repeated as established fact.

## 4. InsightFace — right finding, wrong action and wrong scope

**Scope correction.** The restriction belongs to **specific pretrained weight packages** InsightFace distributes (`buffalo_l`, `antelopev2`, inswapper, InspireFace), **not** to the *architectures* SCRFD or RetinaFace. v2 said the detectors "inherit the same terms," which over-generalises: an independently-trained SCRFD checkpoint under a permissive licence is fine. **Licence status attaches to the exact file, never to the model-family name.**

**Action correction: inventory and quarantine, do not delete.** Deleting destroys the evidence you need. Record path, hash, source, licence state, and which nodes depend on each file. Then have production render profiles *refuse* restricted weights. Two reasons this is better: any metric already computed with those weights needs to be identified and re-run, and **buying a commercial InsightFace licence remains a live option** if it materially outperforms AuraFace.

## 5. NoobAI — simpler and stronger reason

v2 argued from FAIPL's definition of "modify" (training counts) implying share-alike on a downstream LoRA. That argument is sound but subtle, and subtle licence arguments are bad foundations.

**The current NoobAI model cards contain an explicit commercial prohibition covering the model, derivative models, and model-generated products.** That alone excludes these checkpoints. Keep the FAIPL analysis as secondary reasoning for other FAIPL-licensed bases.

**Status: `BLOCKED_FROM_COMMERCIAL_PIPELINE`** unless a specific checkpoint is independently proven otherwise.

## 6. Animation — my gate was wrong in kind, not just in value

**What v2 said:** defer ~12 months; gate on ≤24 GB VRAM.

**Both are wrong.** A calendar date is not a gate — it is a guess wearing a gate's clothes. And **≤24 GB bakes in exactly the constraint the owner deliberately removed** when cloud GPUs and paid tooling were authorised. I carried forward a local-hardware assumption from the era before the budget changed.

**Replacement rule:**
> **Defer animation *productionization* until the first instrumented static chapter ships. Do not defer animation *research*.**

Allocate ~5–10% of research effort to a standing horizon lane, run occasionally on cloud 48/80 GB GPUs, aimed only at **upstream architectural questions**: will these rigs, pose representations, keyframes, cameras and set assets be usable later? The failure to avoid is discovering at chapter 20 that the canonical character/set system discarded something animation needed.

Sora's discontinuation (**2026-09-24**) is unchanged and reinforces adapter-based design rather than any deferral argument.

## 7. VLM QA — "last" was too strong

**What v2 said:** build the VLM auditor last and smallest.

**Corrected:** the VLM should be **optional and non-gating**, but **benchmarked earlier** for *narrow, closed-form* assertion checks against the declared manifest. Those are a different task from open-ended difference detection, and the poor benchmark numbers do not transfer to them automatically — an inference I made without evidence.

**Order:** deterministic/state checks → geometry/CV where ground truth exists → commercially-licensed embedding checks → **narrow closed-form VLM assertions** → human acceptance.

**The VLM is a sensor, not the judge.** It never approves or rejects production output until this project's own benchmark justifies it.

## 8. The gauntlet needs no-change controls

Added, following DiffSpot's design. Without controls you measure only missed errors and are blind to **fabricated** ones — and a QA system that invents problems wastes more human time than one that misses them.

New control block `G35`–`G38`: re-renders at a fixed seed of shots that already passed. **Ground truth: nothing changed.** Any check that flags one has produced a false alarm. Report **recall AND false-alarm rate**, always as a pair.

## 9. Two-stage evaluation

120 generations per candidate is right for a finalist and wrong for a half-promising repo.

- **Stage A — smoke elimination.** 8–12 high-information shots, biased toward Interaction, Occlusion and mirrored L/R pairs. 1–2 seeds. Rejects the obviously non-competitive and the operationally impractical.
- **Stage B — full gauntlet.** Finalists only. All 40 shots, 3 seeds, full cost and human-time instrumentation.

**The frozen benchmark is never edited to make a candidate look better.** New versions only.

## 10. Blender spatial modes

The correction that most improves the architecture, because it prevents a future failure that would have been hard to diagnose: **a sufficiently good QA system will start rejecting good comic art.**

Comics cheat deliberately — impossible eyelines, exaggerated foreshortening, a wall quietly moved so two characters fit, a hand enlarged for readability. Every one of those is correct direction and would read as a geometry violation.

```
grounded   respect canonical 3D closely
cheated    start from canonical 3D, intentionally violate it, RECORD THE CHEAT
2d_only    3D adds nothing to this panel
```

`SpatialStageSpec.mode` is mandatory. QA reads it and does not score geometry violations against `cheated` or `2d_only` panels.

## 11. Vendor policy registry granularity

"FLUX trains on inputs" is too coarse to act on. BFL's general Website/Playground terms grant broad training rights with a prospective opt-out, **while separate Developer Terms and order forms may govern specific endpoints.** One row per vendor hides that.

Required fields per row: `provider · product · plan_tier · endpoint · effective_date · source_url · training_default · opt_out · human_review · retention · likeness_consent_rules · commercial_output_rights · allowed_for_sensitive_adult_reference (yes/no/conditional) · reviewer_notes`.

The Gemini finding is unchanged and remains clear: **unpaid services may use content for product improvement and human reviewers may process it — no adult photographic identity sources there.**

## 12. Reuse figures dropped

The "~70% asset/story, ~0% directing" split was my intuition presented with more confidence than it earned. It is not measured project data and must not be designed against. The *qualitative* claim stands: assets, canon and story state transfer; directing decisions do not.

---

## Architecture, as corrected

```
Canon / Story State
        ↓
Asset Registry
        ↓
SceneBeat / NarrativeIntent
        ├──────────────────────────────┐
        ↓                              ↓
ComicPanelPlan                 AnimationShotPlan / E-Conte   [future]
        ↓                              ↓
SpatialStageSpec (optional)     timing / motion / camera trajectory
  mode: grounded|cheated|2d_only
        ↓
HardAssertionManifest
        ↓
RenderProfile → RenderRequest → RenderRecord
        ↓
QAMeasurement → FailureTag → RepairRecord
        ↓
AcceptedPanelAsset → Revision
        └────────── reusable assets / state ──────────┘
```

## Conflict-resolution order (canonical — identical to README)

1. Reproducible LOCAL_EXPERIMENT evidence and existing working code
2. Current official licence/policy/model documentation
3. `docs/CORRECTIONS_V2_1.md` and the owner's handoff corrections
4. The v2 research package and its cited evidence
5. The older Master Brief's hypotheses

**Do not silently reconcile conflicts. Record them in an ADR.**

*`scripts/validate_research_package.py` fails the package if any document states a different order.*

---

## What this episode says about the research method

Three of my errors share one cause: **a secondary or stale source beat a current primary one, and I did not fetch the primary.** GlobalComix (FAQ instead of the AI policy page), ToonComposer (README instead of LICENSE), NoobAI (a licence-theory argument instead of the model card's plain text).

The evidence-tagging discipline caught none of them, because each claim *was* correctly tagged — it was correctly tagged and wrong. **Tags describe provenance, not currency.** The rule that would have caught all three: for any claim that gates a spend, a platform, or a legal boundary, **fetch the primary artifact — the LICENSE file, the policy page, the model card — not a description of it.**

Codex should apply that rule to anything in this package it is about to act on.
