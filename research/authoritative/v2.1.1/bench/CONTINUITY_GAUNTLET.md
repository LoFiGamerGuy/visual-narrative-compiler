# CONTINUITY_GAUNTLET.md

> ⚠️ **v2.1 — 2026-08-31.** This document has been corrected after independent
> verification by the project owner. **Read `docs/CORRECTIONS_V2_1.md` first**; it is
> the authority wherever it conflicts with anything here. Corrections are marked inline
> with ⚠️ v2.1.
**The permanent benchmark. Counts are computed from `gauntlet.json` and reported in the generated `PACKAGE_STATUS.md` — this document never hand-states them. Semantically frozen; see `executable_bundle_status` for what is not yet frozen.**
v1.0 — 2026-08-31

---

## Rules

1. **Freeze the inputs.** Once ratified, shot text, reference images, seeds and masks never change. If a shot must change, it becomes a new ID (`G07b`) and the old one is retired, never edited. A benchmark you tune is not a benchmark.
2. **Fixed seeds, 3 seeds per render case** for Stage B. Stage A smoke uses a 12-case subset at 2 seeds. Role-swap is stochastic; a single-seed point estimate has error bars wide enough to rank candidates wrongly.
3. **The paired-variant rule.** Twenty cases exist as ten **paired variants** in which exactly one role relationship is exchanged and nothing else changes. ⚠️ v2.1: these are **not all left/right mirrors**, and calling them that was wrong. Each pair declares a `variant_axis` and a `variant_discriminator` — the manifest key that must differ — so the pair is machine-checkable rather than prose:

   | axis | meaning |
   |---|---|
   | `left_right_swap` | screen positions exchanged |
   | `near_far_swap` | which character is nearer camera |
   | `depth_role_swap` | which character is occluded by the other |
   | `focus_role_swap` | which character carries focus |
   | `interaction_role_swap` | who gives / who receives / who carries |

   **A method correct only on the `a` variant has learned prompt order, not role binding.** This is the cheapest possible test for fake success and the one most likely to be skipped. For a true *geometric* mirror, the stage/camera transform or asset hash must be frozen so "mirror" is executable.
4. **Difficulty is stratified, not incidental.** Tiers follow arXiv 2603.26078 (`PREPRINT`): Neutral / Occlusion / Interaction. The Interaction tier is where multi-subject methods collapse — and for a two-hander domestic drama it is also the *most common* real panel type. Do not let the benchmark over-sample the easy case.
5. **Blind review.** Candidate arm identities are stripped before human scoring. Score sheets are filled before the arm is revealed.
6. **Every shot carries a declared-state manifest** (see `gauntlet.json`). Scoring asserts against the manifest, never against "does this look inconsistent" — that judgment is what VLMs are demonstrably bad at.

---

## Coverage matrix

| # | Requirement from the handoff | Shots |
|---|---|---|
| 1 | Single-character identity | G01, G02, G03 |
| 2 | Multi-character identity | G07–G18 (twelve cases, six of the ten paired-variant relations) |
| 3 | Occlusion | G09a/b, G10a/b, G21 |
| 4 | Foreground/background role binding | G11a/b, G12a/b |
| 5 | Prop handoff / contact | G13a/b, G14a/b |
| 6 | Reverse angles | G19, G20 |
| 7 | Recurring-room views | G19–G23 (same room, five cameras) |
| 8 | Wardrobe variants | G04, G05, G24 |
| 9 | Expression | G02, G25, G26 |
| 10 | Action | G15a/b, G16a/b, G27 |
| 11 | Additive VFX (Sigrid) | G28 |
| 12 | Subtractive VFX (Soren) | G29 |
| 13 | Quiet domestic acting | G06, G22, G23, G30 |

---

## The shots

**Cast.** `SOREN` — man, 40s, dark wavy hair, short dark beard. `SIGRID` — woman, 40s, thick curly red-auburn hair, freckled. `LINNEA` — child, **original design only, no real-person referent, geometry-proxy staging only**. `BEAST` — eyeless quadruped predator, shoulders at a man's chest height, no hands.

**Sets.** `KITCHEN` — farmhouse kitchen, night, woodstove + one lamp. `RIDGE` — low forested Appalachian ridgeline, dusk. `PORCH` — farmhouse porch steps, evening.

### Tier N — Neutral (10)

| ID | Set | Content | Primary probe |
|---|---|---|---|
| G01 | KITCHEN | SOREN alone, seated at table, three-quarter, mid shot | Baseline single identity. **Ceiling check** — if this fails, nothing downstream is meaningful |
| G02 | KITCHEN | SIGRID alone, close, expression: tired, not looking at viewer | Single identity at close range + expression |
| G03 | RIDGE | SOREN alone, full figure, wide, small in frame | Identity survival at small scale |
| G04 | KITCHEN | SIGRID, **day-zero wardrobe** — wool coat over pyjamas, no axes, no tattoos | Wardrobe-variant binding. Catches the canon-timeline bug |
| G05 | RIDGE | SIGRID, **post-integration wardrobe** — plaid wrap, leather harness, two axes, woad forearms | Same person, different era. Compare identity against G04 |
| G06 | PORCH | SOREN alone, sitting on steps, hands on knees, quiet | Quiet domestic acting, single |
| G07a | KITCHEN | SOREN **left**, SIGRID **right**, both seated at table, not touching | Two-identity baseline |
| G07b | KITCHEN | SIGRID **left**, SOREN **right**, otherwise identical to G07a | **Mirror. Detects learned prompt order** |
| G08a | RIDGE | SOREN **left**, SIGRID **right**, standing apart, wide | Two identities, wide, separated |
| G08b | RIDGE | Mirror of G08a | Mirror |

### Tier O — Occlusion (10)

| ID | Set | Content | Primary probe |
|---|---|---|---|
| G09a | KITCHEN | SIGRID seated **behind the table**, SOREN standing **nearer camera**, partially overlapping her | Depth ordering + occlusion. **The historical failure: figures composited over the table read as sitting on it** |
| G09b | KITCHEN | Mirror of G09a | Mirror |
| G10a | KITCHEN | SOREN in **foreground, back to camera, out of focus**; SIGRID in **midground, facing, in focus** | Foreground/background role binding under defocus |
| G10b | KITCHEN | Mirror of G10a | Mirror |
| G11a | RIDGE | SOREN **near, large**; SIGRID **far, small**, both standing | Scale-by-depth. **A standing far figure must be smaller than a seated near one** |
| G11b | RIDGE | Mirror of G11a | Mirror |
| G12a | KITCHEN | SIGRID **doorway, far**, entering; SOREN **seated near**, turned to look back | Role binding across a large depth gap |
| G12b | KITCHEN | Mirror of G12a | Mirror |
| G21 | KITCHEN | SOREN seated, **BEAST looming behind him**, partly cut by frame edge | Non-humanoid occluder. **Also checks the beast does not become a bull, a deer, or Soren** |
| G24 | PORCH | SOREN and SIGRID, **SIGRID wearing SOREN's coat** | Wardrobe cross-binding — the adversarial wardrobe case |

### Tier I — Interaction (10)

| ID | Set | Content | Primary probe |
|---|---|---|---|
| G13a | KITCHEN | SIGRID **hands a mug to** SOREN, hands touching, both seated | Prop handoff + contact. Hardest documented tier |
| G13b | KITCHEN | Mirror of G13a | Mirror |
| G14a | PORCH | SOREN **takes an axe from** SIGRID; the axe is in both their hands | Prop contact with a canonical object |
| G14b | PORCH | Mirror of G14a | Mirror |
| G15a | RIDGE | Back to back mid-fight, **both heads turned toward camera**, motion | Action + contact + two faces visible |
| G15b | RIDGE | Mirror of G15a | Mirror |
| G16a | RIDGE | SOREN **half-carrying** SIGRID out of a treeline, her arm over his shoulders | Sustained physical contact, exhaustion, no camera-facing |
| G16b | RIDGE | Mirror of G16a | Mirror |
| G27 | RIDGE | SIGRID **charging the BEAST**, extreme foreshortening, low angle | Action against a non-humanoid, extreme perspective |
| G30 | KITCHEN | SOREN and SIGRID **arguing across the table without raising their voices** — maximum space between them, neither facing camera | Quiet domestic acting, two-hander. **The panel type this project fails at most and needs most** |

### Set-continuity block (5, embedded above where noted)

| ID | Camera on KITCHEN | Probe |
|---|---|---|
| G19 | Wide, from the doorway | Establishing reference |
| G20 | **Reverse of G19** — from the stove looking back at the door | **Reverse angle. Is it the same room?** |
| G22 | Medium, across the table toward the stove | Recurring view |
| G23 | Close on the stove corner, firelight on floorboards | Recurring detail view |
| G17/G18 | Two-character shots reusing G19 and G20 cameras | Set + identity simultaneously |

### VFX block

| ID | Content | Probe |
|---|---|---|
| G28 | SIGRID, **additive** power — storm light, roots, growth; things appear | Additive VFX legibility |
| G29 | SOREN, **subtractive** power — a clean circle of absolute black; the world bends toward it | **Subtractive VFX. "Nothing" is not a picture; the world's reaction must carry it.** Wardrobe must be light — the void is black and cannot read against black clothing |
| G25 | SIGRID, close, **expression: fear** | Expression range |
| G26 | SOREN, close, **expression: cold anger** | Expression range |

---

## Metrics

### Hard gates — a candidate arm that fails any of these is eliminated regardless of beauty

| Gate | Threshold |
|---|---|
| Correct person count | ≥ 95% of shots |
| **Role-Swap Rate** | ≤ 5% |
| No extra child | 100% — **zero tolerance** |
| Beast is non-humanoid and species-neutral | 100% |
| No photoreal output where a drawn style was specified | ≥ 95% |

### Identity — three mutually exclusive outcomes that sum to 1

Per detected face, compute similarity against a frozen reference bank (20–40 approved crops per lead), assign via **Hungarian matching** (2×2 with two leads), then:

- **Identity Margin** = `sim(correct) − sim(incorrect)`
- **Correct Rate** — margin strongly positive
- **Blend Rate** — `|margin|` below threshold (the two identities averaged)
- **Role-Swap Rate** — optimal assignment disagrees with the scripted role

Report all three. A single similarity number cannot separate blending from swapping, and they have different fixes.

**Also report ID-Conf** (from UMO, arXiv 2509.06818): for each reference, `1 − (second_best / best)`, clipped to [0,1], averaged. Higher = less confusion. Note the UMO paper **does not name its face embedding model** — so pin your own and report it.

**Embedding model — licence-critical.** Use **AuraFace** (commercial-safe) or **DINOv3 crops**, *not* InsightFace, whose pretrained weights are non-commercial-research-only and which is pulled silently by many face-consistency nodes. Do **not** use photographic ArcFace thresholds (0.30–0.45 cosine at FMR 1e-4) on illustrated faces — that calibration does not transfer. Calibrate on your own approved chapters: validation split → freeze → test.

**Ensemble, don't trust one model.** ViStoryBench (CVPR 2026, code Apache-2.0, dataset MIT) ensembles ArcFace + AdaFace + FaceNet *and* backstops with CLIP image embeddings on the crop — strong evidence that single-model face similarity is unreliable on stylised art. Add **DINOv3 crop similarity** for *structural* identity (hair, build, costume, silhouette), which catches costume and hair swaps that face embeddings miss.

### Geometry, set, style, repair, production

| Family | Metric | Notes |
|---|---|---|
| Blocking | Pose/keypoint IoU vs the ShotIR's intended blocking | Requires the 3D layer to have a ground truth |
| Depth/occlusion | Correct depth ordering of overlapping figures | Binary per shot, human-scored |
| Masks | Per-character segmentation IoU vs proxy render | Only meaningful on the 3D arms |
| Set landmarks | Presence + relative position of 5 named landmarks per set, across all 5 cameras | Open-vocab detection against the manifest |
| Set identity | SSIM + LPIPS on a **fixed crop** of a recurring surface, same-scene only | Collapses across large camera moves — use for same-camera drift only |
| Wardrobe/props | Declared-state assertion from the manifest | Lookup, not judgment |
| Style/palette | CIELAB histogram EMD vs scene reference; median L\* delta | **Scene-scoped, never chapter-scoped** — a night scene must not be compared to a day scene |
| Repair success | Two-sided: target region LPIPS > 0.15 **AND** non-target SSIM > 0.95, LPIPS < 0.10 | **Two-sided is mandatory.** A one-sided gate selects for silent no-ops — the documented "under-editing trap" |
| Collateral edits | Count of changes outside the mask | |
| Candidates per acceptance | Generations ÷ keepers | The real cost driver |
| Compute / API cost | Per accepted shot | |
| **Human minutes** | Per accepted shot, measured with a timer | **The number that decides everything. Nobody has published it. Ours will be worth more than the literature** |

### Initial targets — deliberately provisional

These are hypotheses to calibrate against, not standards. Revise after the first ratified run.

| Metric | Target |
|---|---|
| Correct Rate (identity) | ≥ 0.85 |
| Blend Rate | ≤ 0.10 |
| Role-Swap Rate | ≤ 0.05 |
| Depth ordering correct | ≥ 0.90 |
| Candidates per acceptance | ≤ 4 |
| Human minutes per accepted shot | ≤ 8 |

**Known ceiling for context:** best published multi-subject Face-Sim is **0.5284** (MultiCrafter). If an arm scores near that, it is at the research frontier, not failing.

---

## QA sensor benchmark (derived — NOT renderer cases)

Renderer quality and QA-sensor quality are different measurements and must never share a
denominator. Both derived families below are computed from `gauntlet.json`.

### No-change controls — `qa_controls`, C01–C04
Re-renders of an approved parent case at the same seeds. **Ground truth: nothing changed.**
Any QA flag here is a **fabricated error**. Without these you measure only missed errors and
are blind to invented ones — and a checker that invents problems wastes more human time than
one that misses them.

### Error injection — `qa_error_injection`, E01–E08
Mutations of *approved* outputs with known ground truth, one per error class: identity/role
swap · wardrobe mismatch · required prop missing · forbidden prop present · set landmark moved ·
character count wrong · left/right role altered · expression altered.

⚠️ **Stated limitation, and it is not small.** Injected errors are *synthetic*. They are clean,
localised and deliberate; real model failures are diffuse, correlated and weird. **Recall measured
on injections will almost certainly overstate recall on real drift.** Two rules follow:

1. Report the metric as **"recall on synthetic injections"**, never as "detection recall".
2. **Derive the injection classes from this project's own observed failure log**, not from
   imagination. Every class above corresponds to a failure actually seen in production here.
   As new real failure modes appear, add them; do not invent plausible-sounding ones.

The honest reading: injections give you a **lower bound on blindness** — a class you miss on a
clean synthetic example you will certainly miss in the wild.

### Reporting

- true-positive recall **by error class** (synthetic)
- false-alarm rate on no-change controls
- `cannot_determine` rate
- human review minutes caused *and* saved

### Compute budgeting caveat

QA controls and injections are excluded from the **benchmark** count — they are not independent
narrative generations. They are **not** free: the 12 control comparisons are real re-renders and
cost real GPU time. Exclude them from the benchmark denominator; include them in the compute budget.
