# Archivist inventory — anime / manhwa / webtoon pipeline generations

Access date: 2026-09-06. Isolated review worktree: `C:\AgentWorkspaces\anime-pipeline-total-review-20260906-211925` on branch `autonomous/anime-pipeline-total-review-20260906-211925`, HEAD `99cb5e9e37c211965a01213a6f7af7103aee8cf3`.

This file is an evidence inventory, not a visual scorecard. Aesthetics are not scored. Every factual claim is labeled **observation**, **sourced fact**, **measured result**, **hypothesis**, or **recommendation**. Paths are absolute. Unknown values are written `null`. Prior-attempt tree `C:\AgentWorkspaces\anime-pipeline-total-review-20260905-092558` was used as a path index only; its conclusions were not copied.

---

## 1. Method

- **Sourced fact:** text copied from a tracked or local file (quote, schema field, ADR, owner-approval JSON).
- **Measured result:** a count, hash, byte size, elapsed-seconds sum, or git object observed in place on 2026-09-06.
- **Observation:** a structural fact visible in the tree (directory layout, file kinds, gitignore policy) without a second-source quote.
- **Hypothesis:** a causal or inheritance inference the lead may test; not proven by this inventory.
- **Recommendation:** out of scope for the archivist except as a pointer that a later role should inspect a path.

Raster PNGs/JPGs were counted and sized in place. They were not copied into git.

---

## 2. Worktree and commit coordinates

**Sourced fact** from `docs/research/anime-pipeline-total-review/evidence/protected-state-initial.json` and **measured result** from `git log -1` in each tree.

| ID | Path | Branch | HEAD | Date (ISO) | Subject | Untracked |
|---|---|---|---|---|---|---|
| `root-main` | `C:\AgentWorkspaces\anime-pipeline` | `main` | `40e7940016ea3c3966752b61f55a931f91a13ac7` | 2026-09-03 17:07:10 -0400 | Build sparse lettered editions for eight chapters | 165 (coordination snapshot) |
| `reimagining-empty` | `C:\AgentWorkspaces\anime-pipeline-reimagining` | `autonomous/ten-chapter-reimagining` | `40e79400…` (same as main) | 2026-09-03 17:07:10 -0400 | same as main; no reimagining story artifacts | 0 |
| `borrowed-down` | `C:\AgentWorkspaces\anime-pipeline-reimagining-20260903` | `autonomous/ten-chapter-reimagining-20260903` | `fa6650a4f8e51e7d1138ea2c207fd560411f023a` | 2026-09-03 20:10:51 -0400 | record post-build isolation audit | 0 |
| `city-keeps-oaths` | `C:\AgentWorkspaces\anime-pipeline-reimagining-clean-webtoon-20260903-213010` | `autonomous/ten-chapter-clean-webtoon-20260903-213010` | `d1cfa464be3508809b2a6c7150ef0b29262772ca` | 2026-09-03 23:53:11 -0400 | feat: add navigable chapter viewer | 0 |
| `ember-volume` | `C:\AgentWorkspaces\anime-pipeline-litrpg-manhwa-20260904-001211` | `autonomous/ten-chapter-litrpg-manhwa-20260904-001211` | `023330e8b62335d27fee4d7369e2a0201a0e22d6` | 2026-09-04 10:12:21 -0400 | Close Ember Lattice delivery integrity | 0 |
| `ember-premium` | `C:\AgentWorkspaces\anime-pipeline-ember-lattice-premium-rd-20260904-150943` | `autonomous/ember-lattice-premium-rd-20260904-150943` | `fb10c87f974db4e02d8166b80b9489ef47af8f40` | 2026-09-04 21:37:08 -0400 | Complete unique 52-panel premium CH01 | 0 |
| `ember-editorial` | `C:\AgentWorkspaces\anime-pipeline-ember-lattice-editorial-gear-20260904` | `autonomous/ember-lattice-editorial-gear-20260904` | `99cb5e9e37c211965a01213a6f7af7103aee8cf3` | 2026-09-04 23:30:36 -0400 | Complete Ember Lattice editorial and gear pass | 0 |
| `prior-review` | `C:\AgentWorkspaces\anime-pipeline-total-review-20260905-092558` | `autonomous/anime-pipeline-total-review-20260905-092558` | `99cb5e9e…` | same editorial HEAD | uncommitted prior total-review attempt; **not authority** | 44 |
| `this-review` | `C:\AgentWorkspaces\anime-pipeline-total-review-20260906-211925` | `autonomous/anime-pipeline-total-review-20260906-211925` | `99cb5e9e…` | same | isolated review; only `docs/research/anime-pipeline-total-review/` is new | review evidence only |

**Measured result:** git history on the isolated worktree contains **221 commits** (`2026-09-01`: 81, `2026-09-02`: 89, `2026-09-03`: 44, `2026-09-04`: 7). First commit: `481c1e1` 2026-09-01 "Initialize North Garden research system". Remote: `https://github.com/LoFiGamerGuy/visual-narrative-compiler.git` (**sourced fact**, coordination snapshot).

**Observation:** `C:\AgentWorkspaces\anime-pipeline-reimagining` is a worktree parked on the same commit as `main` and contains no Borrowed Down / City / Ember story tree. It is not a distinct generation.

---

## 3. Generated-vs-tracked asset policy

**Sourced fact** from `C:\AgentWorkspaces\anime-pipeline-total-review-20260906-211925\.gitignore` and `docs/architecture/source-control-scope-r1.md`:

- Git tracks architecture, ADRs, research docs, manifests, validators, adapters, ComicPanelPlans, SVG lettering overlays, HTML readers, and two public G07 control PNGs.
- Git ignores `experiments/`, `ComfyUI/`, `loras/`, `garden-work/`, `pagecomp*/`, stage folders, models, datasets, and generated rasters. Hashes of ignored files may appear in tracked JSON.
- **Measured result** on this review HEAD: tracked media is **91 HTML**, **1368 SVG**, **2 PNG** (`public-controls/g07a-no-change-r1.png`, `public-controls/g07a-role-id-r1.png`). Zero story rasters are tracked.

---

## 4. Counts of HTML readers, SVG overlays, and gitignored PNG sources

### 4.1 Tracked HTML (this review worktree = editorial HEAD)

**Measured result:** 91 HTML files under `docs/reimaginings/ember-lattice/`.

| Bucket | Count | Paths |
|---|---:|---|
| Ember volume chapter surfaces | 50 | 10 chapters × `{index,full,compact,action,diagnostics}.html` |
| Ember volume hubs | 4 | `volume/index.html`, `read-all.html`, `progression.html`, `repair-comparison.html` |
| Ember Phase A pilot | 3 | `pilot/index.html`, `reader.html`, `safe-zones.html` |
| Premium CH01 site | 17 | `premium-rd/index.html`, 4 readers, 6 diagnostics, comparison/benchmark/evidence/failures/future-cast/gear |
| Premium benchmark-suite copy | 17 | `premium-rd/benchmark-suite/` mirror of the same reader/diagnostic set |

### 4.2 Other HTML readers (not in the 91)

**Measured result:**

| Location | Count | Notes |
|---|---:|---|
| `C:\AgentWorkspaces\anime-pipeline-reimagining-20260903\experiments\reimaginings\borrowed-down\` | 4 | `START-HERE.html`, `strongest-panels.html`, `targeted-repair-decisions.html`, `ten-chapter-progression.html` (gitignored with `experiments/`) |
| `C:\AgentWorkspaces\anime-pipeline-reimagining-clean-webtoon-20260903-213010\docs\reimaginings\the-city-keeps-oaths\viewer.html` | 1 | tracked on the City branch |
| `C:\AgentWorkspaces\anime-pipeline\experiments\review-packets\ch05-owner-review-index-r1` … `r9` plus worksheet | 11 | gitignored North Garden owner hubs |
| `C:\AgentWorkspaces\anime-pipeline\garden-work\northgarden\{bible,ch01-02,pitches}.html` | 3 | gitignored historical Garden's Anchor HTML |

**Measured result — HTML reader total across inspected trees, excluding vendor/Blender/torch:** 91 + 4 + 1 + 11 + 3 = **110**.

### 4.3 Tracked SVG overlays (this review HEAD)

**Measured result:** 1368 SVG = 1272 under `docs/reimaginings/ember-lattice/` + 94 under `production/reimaginings/ember-lattice/premium-rd/assets/` + 2 fixtures under `src/reimaginings/ember_lattice/premium_rd/fixtures/`.

| Overlay class | Count | How counted |
|---|---:|---|
| Ember volume panel lettering overlays | 240 | 10 × 24 `volume/chapters/chXX/panels/*.svg` |
| Ember volume safe-zone overlays | 240 | 10 × 24 `…/safe-zones/*.svg` |
| Ember pilot panels + safe-zones | 32 | 16 + 16 |
| Premium CH01 panel layers | 208 | 52 × `{baseline,hybrid,original-lettering,raw}` |
| Premium CH01 diagnostics | 312 | 52 × `{dialogue-density,grayscale,lettering-collision,noise,safe-zone,ui-density}` |
| Premium 24-panel benchmark-suite copy | 240 | 24 × 4 panel layers + 24 × 6 diagnostics |
| Production hybrid/concept SVGs | 94 | 52 CH01 hybrid + 24 benchmark hybrid + 12 future-cast + 6 gear |
| Test fixtures | 2 | `source.svg`, `premium-source.svg` |

**Observation:** Borrowed Down and The City Keeps Oaths letter onto PNG (Pillow), not SVG. North Garden CH05/CH06–CH13 lettering review sheets are PNG overlays under gitignored `experiments/review-packets/`. Garden's Anchor strip lettering is Pillow in `garden-work/northgarden/strip/kit.py`.

### 4.4 Gitignored PNG/JPG sources (inspect in place; never copied)

| Corpus | Path | Raster count | Bytes | Notes |
|---|---|---:|---:|---|
| Ember ten-chapter volume | `C:\AgentWorkspaces\anime-pipeline-litrpg-manhwa-20260904-001211\experiments\reimaginings\ember-lattice\` | 254 PNG + 10 JPG = **264** | 586,744,434 | `volume/` 235; `pilot/` 18; `references/` 8; `style-candidates/` 3 |
| Ember premium originals | `C:\AgentWorkspaces\anime-pipeline-ember-lattice-premium-rd-20260904-150943\experiments\reimaginings\ember-lattice\` | **109 PNG** | 277,012,412 | `premium-rd/benchmark` 75; `ch01-unique` 30; `references` 3; plus contact |
| Ember premium + editorial | `C:\AgentWorkspaces\anime-pipeline-ember-lattice-editorial-gear-20260904\experiments\reimaginings\ember-lattice\premium-rd\` | **121 PNG** | 304,972,909 | originals + 12 `editorial-clean/` repairs |
| Borrowed Down | `C:\AgentWorkspaces\anime-pipeline-reimagining-20260903\experiments\reimaginings\borrowed-down\` | **809 PNG** (+ 4 HTML) | 1,876,337,935 | 10 × 71 chapter files + diagnostics/incoming/repairs/style-probes/strongest |
| The City Keeps Oaths | `C:\AgentWorkspaces\anime-pipeline-reimagining-clean-webtoon-20260903-213010\experiments\reimaginings\the-city-keeps-oaths\` | **421 PNG** | 875,736,103 | 10 × 39 chapter files + pilot 6 + repairs 18 + refs/style/volume-review |
| North Garden `experiments/` | `C:\AgentWorkspaces\anime-pipeline\experiments\` | 2254 PNG + 13 JPG among 2587 files | 4,789,991,302 | review-packets ~2132 PNG; outputs ~150; records JSON |
| ComfyUI output | `C:\AgentWorkspaces\anime-pipeline\ComfyUI\output\` | **516 PNG** | 714,894,530 | garden batches + later adapter runs |
| ComfyUI input | `C:\AgentWorkspaces\anime-pipeline\ComfyUI\input\` | 129 PNG + 3 JPG | 35,661,475 | local inputs |
| pagecomp / pagecomp2 / pagecomp3 | `C:\AgentWorkspaces\anime-pipeline\pagecomp*` | 4+4+4 = **12 PNG** | ~13.5 MB | CH01 kitchen composites |
| calib plates | `C:\AgentWorkspaces\anime-pipeline\calib\` | **4 PNG** | 5,132,266 | door/stove/table/wide |
| actstage style tests | `C:\AgentWorkspaces\anime-pipeline\actstage\` | **36 JPG** | 3,163,440 | 6 acts × 6 styles |
| lorastage | `C:\AgentWorkspaces\anime-pipeline\lorastage\` | **72 PNG** | 104,108,217 | LoRA test renders |
| garden-work out sheets | `C:\AgentWorkspaces\anime-pipeline\garden-work\northgarden\out\` | contact/option JPGs (listed, not re-hashed here) | null | historical cast sheets |

**Measured result — named raster roots from coordination.md:** Ember volume 264 rasters; premium/editorial 121; premium originals 109; Borrowed Down 809 PNG; City 421 PNG.

---

## 5. Chronological experiment genealogy

Dates are file mtimes / commit dates. Parallel arms are indented.

```
~pre-2026-08-29  Lion Cub historical (pose zips, novaAnimeXL, garden-work "Lion Cub lesson")
2026-08-29..31   Garden's Anchor local Anima/Comfy batches (garden/gen.py → gen3.py)
                 ├─ style/cast rounds (style.py, cast.py … cast5.py, actstage)
                 ├─ Soren/Sigrid LoRA train (ai-toolkit YAML; loras/soren_v1, sigrid_v1)
                 ├─ regional-conditioning two-shot (gen3.py ConditioningSetMask)
                 ├─ plate cutout composite (panelcomp.py, make_page01..03)
                 ├─ calibrated 2D stage + occluder (stage.py, rooms_def.py, calib/)
                 └─ Pillow strip lettering/previz (garden-work/northgarden/strip/)
2026-08-31       GAP_ANALYSIS.md + git init of North Garden v2 records (481c1e1 on 2026-09-01)
2026-08-31       baseline_legacy Stage A (wraps garden/gen3.py; 24 gens; 0 accepted)
2026-08-31       sequential_inpaint + actor_matte G07 controls
2026-09-01       FLUX.2 Klein proxy / geometry / tile / Blender OBJ+blend / Illustrious+Xinsir
2026-09-01       G07 fictional provider bakeoff (Gemini, xAI, OpenAI, BFL); ADR-0025 selects OpenAI
2026-09-01       Owner visual-direction decision r2; CH05 Mill Signal promotion (50 plans)
2026-09-01       CH01 kitchen sequence internally accepted (pagecomp3 composites)
2026-09-01–02    CH03/CH04 3-panel imagegen drafts; CH05 compiler/repair/ledger hardening (no CH05 art yet)
2026-09-02       CH05 complete-chapter six style routes + sequence-cadence hybrid assembly
2026-09-03       CH06–CH13 40-plan chapters + default house-route 5-panel strips; sparse lettering editions (40e79400 = main)
2026-09-03 20:10 Borrowed Down 10ch / 300 panels (f77663a8, envelope fa6650a4)
2026-09-03 23:39 The City Keeps Oaths 10ch / 240 panels (562b2295, viewer d1cfa464)
2026-09-04 01:15 Ember Lattice Phase A 16-panel pilot (6a239225)
2026-09-04       Owner approval JSON; Phase B authorized
2026-09-04 10:09 Ember Lattice 10ch / 240 panels (6f135579); integrity close (023330e8)
2026-09-04 18:42 Premium R&D 24-panel benchmark slice (9d191cbc)
2026-09-04 21:37 Unique 52-panel premium CH01 (fb10c87f)
2026-09-04 23:30 Editorial / lettering / clean-art / gear / faction / future-cast (99cb5e9e)
2026-09-05       Uncommitted prior total-review attempt (path index only)
2026-09-06       This isolated review branch
```

**Hypothesis:** each reimagining inherits North Garden *records* (ComicPanelPlan, RenderRecord, ignore-rasters, adult-only language, $0-cloud default) more than it inherits Garden *pixels* or LoRAs. **Observation:** Ember volume code explicitly cites Borrowed Down / City audits as negative lessons (`docs/reimaginings/ember-lattice/cumulative-experiment-ledger.md`).

---

## 6. Stage-by-stage map: narrative intent → phone reader

This is the intended production chain, not a claim that every generation implemented every box.

| Stage | What it is | Authority records | Typical execution | Reader surface |
|---|---|---|---|---|
| 0 Premise / bible | story, visual, progression | `reimaginings/*/story-bible.md`, ADRs | owner prompt + agent authoring | START_HERE / index HTML |
| 1 Canon / StoryState | named adults, wardrobe, irreversible flags | `production/canon/`, `production/reimaginings/*/continuity-*.json` | JSON compile | progression hub |
| 2 Asset registry / refs | identity sheets, style anchors | `reference-registry.json`, hash-pinned PNGs in `experiments/` | built-in ImageGen or LoRA plates | character-sheet PNG |
| 3 SceneBeat | chapter objective / closing turn | `production/scene-beats/` or volume source JSON | authoring scripts | chapter index |
| 4 ComicPanelPlan | one panel: cast, density, safe zone, beat | `production/comic/*panel-plans*` or reimagining `comic-panel-plans.json` | compile_all() | diagnostics overlay |
| 5 HardAssertionManifest | pass/fail checks | `production/comic/hard-assertion-manifests/` | validators | triage sheets |
| 6 Spatial stage | camera / occluder / 3D | `production/stages/`, `garden/stage.py`, `assets/stages/*.obj|.blend` | Blender or 2D plate | calibration PNG |
| 7 Prompt compile | exact prompt + refs + negative | `prompt-manifest.json`, RenderRequest | text only until authorized | evidence JSON |
| 8 Raster generation | diffusion / ImageGen / composite | RenderRecord; ignored PNG | Anima/Comfy, built-in ImageGen, OpenAI, Gemini, xAI, BFL | source PNG |
| 9 Selection / rejection | candidate vs diagnostic | reviews JSON, failure-tags | agent triage then owner | contact sheets |
| 10 Repair | inpaint, mask, SVG clean-art, lettering move | repair-snapshots, ch01-clean-art-audit | localized only | before/after PNG |
| 11 Lettering / SFX / UI | code, not baked glyphs | SVG overlays or Pillow | `strip/kit.py`, `build_volume.py`, City/Borrowed pipeline | lettered PNG or SVG-over-PNG |
| 12 Build / assemble | vertical scroll, phone 390 px | assembly manifests | Pillow crop + HTML | `full.html` / `phone.html` / `viewer.html` |
| 13 Validation | hard gates, density, integrity | validation-report, volume-validation | unittest + JSON validators | diagnostics HTML |
| 14 Owner review | qualitative, timed, or pending | owner-approval JSON, ADR-0084, G07 packet | human | owner-review-index HTML |
| 15 Edition / acceptance | immutable revision | `production/accepted/`, EditionManifest | almost never fired | null commercial |

**Observation:** Garden's Anchor implemented 6–8–11–12 with Python jobs and almost no RenderRecords. North Garden v2 implemented 1–5 and 13–15 first, then filled 7–12 for CH05–CH13. Reimaginings implement 0–14 in one isolated branch and leave 15 at `unaccepted`.

---

## 7. Owner-feedback ledger (quotes and paths only)

No quote below is invented. Agent paraphrases are marked and not treated as owner speech.

| Date | Path | Exact recorded wording | Status |
|---|---|---|---|
| 2026-08-30 | `C:\AgentWorkspaces\anime-pipeline\garden\stage.py` L3–5 | `Ryan: "where the people are in the scene doesn't always make sense... they are sitting on tables... looking tinier than the table. I wonder if we need to create backgrounds, scale everything, and adjust based on that."` | **sourced fact** |
| 2026-08-30 | `C:\AgentWorkspaces\anime-pipeline\garden\cast4.py` L3–8 | `Direction from Ryan:` / `- Tower of God / Solo Leveling quality bar. More action.` / `- Soren's power must read HARDER: void, darkness, mushin.` / `- Sigrid is a celtic / scottish NATURE WITCH crossed with a DUAL-WIELDING BERSERKER. Not a woman in a coat.` / `- Both early forties but should LOOK younger and cooler.` | **sourced fact** |
| 2026-09-01 | `production/decisions/ng-decision-owner-visual-direction-r2.json` | `owner_report`: `"reviewed everything; all great; approved"` (G07 packet); `"characters look great; art is potentially eligible as an exact production base"` (CH05 smoke contact sheet). Lettering direction: `"Lettering is approved when it does not block people or faces. Conditional overlap may be acceptable when transparency preserves the character and read."` Requested exploration: other styles, lower density / phone clarity, higher-quality causal action, smaller and larger panel formats. | **sourced fact** |
| 2026-09-01 | `docs/adr/ADR-0084-owner-visual-approval-advances-direction-not-invented-timing-or-exact-authority.md` | Records the same qualitative approval; forbids synthesizing G07 timings, exact CH05 base hashes, upload authority, or budget. | **sourced fact** |
| 2026-09-01 | `production/decisions/ng-decision-ch05-mill-signal-promotion-r1.json` | `"Owner approved the clean CH05 Mill Signal script, its visual smoke contact sheet, and the promotion template."` | **sourced fact** (decision_rationale; not a first-person quote) |
| 2026-09-04 | `production/reimaginings/ember-lattice/owner-approval.json` | `"pilot": "APPROVED"`; `"selected_style_owner_assessment": "great selection; art and candidate B are amazing"`; required Phase B changes: `"improve wording and dialogue substance"`, `"reduce speech-balloon art occlusion"`, `"test translucency and high-contrast text overlays"`, `"make dialogue containers smaller while allowing more text"`, `"show substantially more system menus, leveling, XP, and skills"`. | **sourced fact** |
| 2026-09-04 | `docs/reimaginings/ember-lattice/adr/ADR-EL002-owner-approval-and-lettering-v2.md` | `"The owner explicitly approved the pilot and praised Candidate B."` plus the required lettering/system changes. | **sourced fact** (ADR restatement of the JSON) |
| 2026-09-04 | `docs/reimaginings/ember-lattice/research/lettering-and-dialogue-research.md` | `"This research answers the owner's concrete pilot feedback: the balloon shapes cover too much art, the copy is too short, and the system layer is too sparse."` | **sourced fact** (research restatement) |
| 2026-09-04 | `C:\AgentWorkspaces\anime-pipeline\FRESH_SESSION_LITRPG_MANHWA_PRODUCTION_PROMPT.txt` L5 | Owner-authored binding diagnosis of earlier attempts: `"they were too visually busy; they converged on the same generic painterly fantasy look; they did not meaningfully evoke the readable, cinematic, action-forward qualities the owner values in The Beginning After the End, Solo Leveling, and Tower of God; their balloons, text blocks, and lettering were unattractive; they lacked forceful action and memorable spectacle; two unrelated casts drifted toward nearly uniform dark complexions despite the owner's preference; and the supposedly progression-fantasy work showed almost none of the concrete LitRPG machinery expected from the genre."` | **sourced fact** (owner prompt text) |
| 2026-09-06 | `C:\AgentWorkspaces\anime-pipeline\FRESH_SESSION_TOTAL_ANIME_PIPELINE_INDUSTRY_REVIEW_PROMPT.txt` L40 | `> "It is still not like Tower of God or Solo Leveling in the way I want. The pipeline may need improvement, a substantially different approach, or a complete restart."` | **sourced fact** (quoted in the owner’s authoritative prompt) |

**Not owner quotes (do not treat as such):**

- `docs/reimaginings/ember-lattice/cumulative-experiment-ledger.md` L21 `"the owner's binding diagnosis rejects its visual result"` — **observation:** agent paraphrase of the LitRPG prompt, not a separate owner utterance.
- CH01 kitchen `production/accepted/ch01-kitchen-sequence-v1.json` `"reviewer": "Codex visual review"` — agent, not owner.
- City/Borrowed `FINAL_AUDIT.md` “owner-review-pending” — status flag, not a quote.

**Measured result:** G07 formal timed decisions remain `0/20` with `human_minutes: null` (`ng-decision-owner-visual-direction-r2.json`). Commercial clearance is `false` on every owner-approval / volume-manifest inspected.

---

## 8. Pipeline generations

Each record uses the same field set. `model/tool/generation route` is `null` when the provider did not expose it.

### G00 — Lion Cub historical (discovered, not North Garden)

- **identifier:** `lion-cub-historical`
- **story:** Lion Cub (plush-toy likeness problem). **Sourced fact:** `garden-work/northgarden/pipeline.md` “Lion Cub lesson”.
- **branch / commit / worktree:** untracked local; not on `main`. Worktree `C:\AgentWorkspaces\anime-pipeline`.
- **date:** pre-Garden batches; `LionCub_PoseLibrary_v3.zip` / `v4.zip` present at repo root. **Observation.**
- **status:** abandoned relative to North Garden; assets remain as local cache.
- **intended hypothesis:** diffusion+LoRA could match a real toy. **Sourced fact:** pipeline.md says that was circular.
- **source inputs:** real plush / pose library (not opened in this inventory).
- **model/tool/generation route:** ComfyUI + `novaAnimeXL_ilV190.safetensors` listed in `docs/research/model-license-registry.md` as `QUARANTINED_UNVERIFIED` “Legacy Lion Cub workflow asset”.
- **prompt architecture / identity / spatial / panel-planning / selection / repair / lettering / build / validation:** null as a documented production loop; Comfy output contains `LionCub_anime_00001_.png` … `00006_.png`.
- **panel/chapter/output counts:** 6 named LionCub PNGs in Comfy output (**measured result**); pose zips not unpacked.
- **generated-vs-tracked:** ignored binaries/zips.
- **known owner response:** pipeline.md treats Lion Cub as the failure that motivated splitting lettering/backgrounds/characters.
- **strongest evidence paths:** `C:\AgentWorkspaces\anime-pipeline\garden-work\northgarden\pipeline.md`; `docs/research/model-license-registry.md`; `C:\AgentWorkspaces\anime-pipeline\ComfyUI\output\LionCub_anime_00001_.png`.
- **visible strengths:** explicit four-layer split after the failure (**sourced fact**).
- **visible failures:** circular identity training against a real toy (**sourced fact**).
- **reproducibility/licensing:** novaAnimeXL merge metadata cannot reconstruct license (**sourced fact**).
- **what next inherited:** four-layer split (Pillow lettering, Blender sets, character LoRA, code assembly).
- **whether inheritance improved the page:** **hypothesis** — the split is the Garden architecture; page quality of Lion Cub itself was not re-scored here.

### G01 — Garden's Anchor / North Garden legacy local Anima pipeline

- **identifier:** `gardens-anchor-legacy-anima`
- **story:** Garden's Anchor / North Garden farmhouse; adult leads originally Dio/Thal, later Soren/Sigrid. Child Linnea strings exist in `garden/canon.py` (**sourced fact**); later ADR-0017 / ADR-0022 forbid child-coded production use.
- **branch / commit:** **untracked**. `git -C C:\AgentWorkspaces\anime-pipeline ls-files garden` count = 0. `git status --porcelain -- garden` untracked count = **115** (**measured result**). Worktree: `C:\AgentWorkspaces\anime-pipeline\garden\`.
- **date:** scripts 2026-08-29 through 2026-08-31 (mtime).
- **status:** operational historical renderer; wrapped later as `baseline_legacy`; not a git edition.
- **intended hypothesis:** local Anima on RTX 5090 can produce serialized farmhouse pages if prompts, LoRAs, and compositing are iterated in-place.
- **source inputs:** prompt JSON batches `garden/batch.json` … `batch14.json`, `page01.json`, `duo.json`, `close.json`, `rooms.json`; Comfy checkpoints.
- **model/tool/generation route:** ComfyUI REST `http://127.0.0.1:8188`; UNET `anima-aesthetic-v1.1.safetensors`; CLIP `qwen_3_06b_base.safetensors`; VAE `qwen_image_vae.safetensors`; sampler `er_sde` / `simple`; 42 steps typical in gen3, 34 in gen.py. ComfyUI commit pinned later as `82f839f5e737d8bfce480872ba05e5a430f2526f` (**sourced fact**, experiment-log / GAP_ANALYSIS).
- **prompt architecture:** `garden/canon.py` frozen identity strings + per-job JSON; negatives for anatomy, duplicates, photoreal, day-zero wardrobe.
- **character identity method:** prompt strings first (`canon.py` documents drift); then dual LoRAs `s0rn` / `sgrd` on the **whole model** (`gen3.py` docstring: LoRA is not regional).
- **environment/spatial-continuity method:** none in gen.py (full-frame text2img); later rooms/plates.
- **panel-planning method:** named jobs in batch JSON, not ComicPanelPlan.
- **selection/rejection:** operator looking at `ComfyUI/output/` prefixes (`c_dio_`, `pg_pl_`, `r4_`, `act_*`).
- **repair:** reroll batches; later regional masks.
- **lettering/SFX/UI:** not in gen.py.
- **build/reader:** `make_page*.py` writes `pagecomp*/page01_pXX.png`; garden-work HTML bible.
- **validation:** run logs `garden/run*.log`; no HardAssertionManifest.
- **panel/chapter/output counts:** **measured result** — `garden/` 56 `.py` + 25 `.json`; Comfy output 516 PNG including garden prefixes; GAP_ANALYSIS says logged gens ~20–37 s at 42 steps.
- **generated-vs-tracked:** entire `garden/` untracked; rasters ignored.
- **known owner response:** stage.py / cast4.py quotes above.
- **strongest evidence paths:** `C:\AgentWorkspaces\anime-pipeline\garden\gen.py`, `gen2.py`, `gen3.py`, `canon.py`; `C:\AgentWorkspaces\anime-pipeline\GAP_ANALYSIS.md`; `C:\AgentWorkspaces\anime-pipeline\ComfyUI\output\`.
- **visible strengths:** working local loop; explicit limitation comments in gen3; canon-string freeze.
- **visible failures:** photoreal/identity/set/blocking later measured as 0/24 Stage A; extra child on G11a; duo shots described as posed/blended in `panelcomp.py` docstring.
- **reproducibility/licensing:** Anima + Qwen CLIP/VAE + adult LoRAs = `INTERNAL_BASELINE_ONLY` / `SENSITIVE_ADULT_LIKENESS_LOCAL_ONLY` (`model-license-registry.md`). No seed/model snapshot in garden job JSON beyond the file’s seed field.
- **what next inherited:** graph reused verbatim by `src/north_garden/baseline_legacy.py`; compositing and canon strings inform CH01 acceptance.
- **whether inheritance improved the page:** **hypothesis** — wrapping added provenance, not better pixels (Stage A still 0 accepted).

### G02 — Garden-work historical script + Pillow lettering / previz

- **identifier:** `gardens-anchor-script-lettering`
- **story:** Garden's Anchor CH01 52 + CH02 44 panels, leads Dio/Thal. **Sourced fact:** ADR-0022.
- **branch / commit:** untracked `garden-work/` (gitignore). Path `C:\AgentWorkspaces\anime-pipeline\garden-work\northgarden\`.
- **date:** present locally; ADR-0022 dated 2026-09-01.
- **status:** `HISTORICAL_NARRATIVE_AND_DESIGN_EVIDENCE_NOT_IMPORTED` (**sourced fact**, ADR-0022). Internal count contradiction: header 92 vs 52+44=96.
- **intended hypothesis:** lettering/UI as code under art rectangles; Blender for land; LoRA for characters (`pipeline.md`).
- **source inputs:** `pilot.md`, `bible.md`, `canon.md`.
- **model/tool/generation route:** previz is procedural (`strip/previz.py`); real art optional via `art=` PNG.
- **prompt architecture:** null for previz.
- **character identity method:** written design brief → curate 15–25 → LoRA (`pipeline.md`).
- **environment/spatial-continuity method:** intended Blender 3D set + ControlNet; **observation:** no `.blend` in garden-work; later kitchen OBJ lives under `assets/stages/` in the git tree.
- **panel-planning method:** `pilot.md` numbered panels; `strip/ch01.py`, `ch02.py`.
- **selection/rejection:** null automated.
- **repair:** null.
- **lettering/SFX/UI:** **deterministic Pillow** `strip/kit.py` — balloons, captions, System UI; canvas width 900; fonts Archivo / Newsreader / JetBrainsMono. Docstring: “lettering … are CODE, not art.”
- **build/reader:** `Strip.render()`; `bible.html`, `ch01-02.html`, `pitches.html`; `out/*.jpg` sheets.
- **validation:** ADR-0022 count mismatch blocks import.
- **panel/chapter/output counts:** asserted 52+44; inconsistent total. **Observation:** kit.py 7040 bytes; ch01.py 9954; ch02.py 7629; previz.py 11415.
- **generated-vs-tracked:** gitignored.
- **known owner response:** none in these files beyond the pipeline design.
- **strongest evidence paths:** `C:\AgentWorkspaces\anime-pipeline\garden-work\northgarden\pipeline.md`; `strip/kit.py`; `docs/adr/ADR-0022-quarantine-gardens-anchor-script-and-design-conflict.md`; `pilot.md`.
- **visible strengths:** lettering-as-code is the ancestor of Ember SVG overlays; 900 px webtoon canvas already specified.
- **visible failures:** name conflict Dio/Thal vs Soren/Sigrid; photo-derived design history flagged; panel-count contradiction.
- **reproducibility/licensing:** fonts under `garden-work/northgarden/fonts` (not inventoried for license here) = **unknown/null** for redistribution.
- **what next inherited:** Pillow lettering idea; 52-panel chapter as a *scale* memory (premium CH01 later uses 52 for a different story).
- **whether inheritance improved the page:** **hypothesis** — Ember SVG lettering is a descendant; Garden's Anchor script itself was not promoted, so the page did not ship from this generation.

### G03 — Soren / Sigrid LoRA + regional conditioning

- **identifier:** `soren-sigrid-lora-regional`
- **story:** same Garden adults; trigger words `s0rn`, `sgrd`.
- **branch / commit:** untracked `loras/`, `garden/train_soren.yaml`, `train_sigrid.yaml`.
- **date:** YAML 2026-08-30; sample JPGs in `loras/*/samples/`.
- **status:** local identity mechanism; commercial profile blocked.
- **intended hypothesis:** low-rank LoRA on Anima can hold identity without dragging photos into photoreal (`train_soren.yaml` comments).
- **source inputs:** `C:\AgentWorkspaces\anime-pipeline\datasets\soren` (27 images noted in YAML); Sigrid counterpart. **Not opened** (sensitive adult likeness).
- **model/tool/generation route:** ai-toolkit `sd_trainer`; LoRA linear 16; 1500 steps Soren; flowmatch / adamw8bit / lr 1e-4. Checkpoints `loras/soren_v1/soren_v1.safetensors` (69,389,496 bytes) and `loras/sigrid_v1/sigrid_v1.safetensors` (69,389,504) plus step snapshots. **Measured result.**
- **prompt architecture:** trigger + `canon.py` strings; gen3 regional text boxes.
- **character identity method:** LoRA on MODEL (global) + ConditioningSetMask on TEXT (regional). gen3 documents Anima Cosmos-Predict2 extra latent axis breaking `ConditioningSetAreaPercentage`, hence mask path.
- **environment/spatial-continuity method:** none (identity only).
- **panel-planning method:** loratest JSON / duo jobs.
- **selection/rejection:** sample grids every 250 steps.
- **repair:** regional two-shot instead of joint generation (`panelcomp.py` explains LoRA fight).
- **lettering:** none.
- **build/reader:** lorastage 72 PNG; Comfy `LoRA_train/` 42 PNG.
- **validation:** later actor-plate capture failed prop separability (ADR-0005, ADR-0008, ADR-0010).
- **panel/chapter/output counts:** 2 final LoRAs + backups in `lora-backup/`; Soren samples 24 jpg + thumbs; Sigrid similar.
- **generated-vs-tracked:** ignored; hashes recorded in license registry.
- **known owner response:** cast4 redesign direction (younger/cooler/ToG bar) sits in the same identity loop.
- **strongest evidence paths:** `C:\AgentWorkspaces\anime-pipeline\garden\gen3.py`; `train_soren.yaml`; `docs/research/model-license-registry.md` LoRA rows; `docs/research/actor-asset-inventory.md`.
- **visible strengths:** trigger-word regional text is a cheap separator; hashes pinned.
- **visible failures:** LoRA still influences every pixel; seated plates embed tables/trays; alpha key ≠ actor-only asset.
- **reproducibility/licensing:** adult-likeness local-only; Anima license unrecorded; dataset not in git.
- **what next inherited:** CH01 composites use `pg_pl_dio_*` / `pg_pl_thal_*` plates (names not yet renamed on disk). North Garden later **abandons** LoRA for built-in ImageGen + text identity contracts.
- **whether inheritance improved the page:** **observation** — CH01 kitchen four-panel sequence is the only internally accepted narrative art and it uses these plates. Later chapter-scale work does not load these LoRAs.

### G04 — Stage, calibration, Blender/OBJ, plates, compositing

- **identifier:** `stage-calib-plate-composite-blender`
- **story:** kitchen / farmhouse interiors for Garden CH01 argument.
- **branch / commit:** mix of untracked (`calib/`, `pagecomp*`, Comfy `rm_*` / `pg_bg_*`) and tracked (`production/stages/`, `assets/stages/`).
- **date:** garden stage.py 2026-08-31; Blender import 2026-09-01 (experiment-log).
- **status:** legacy 2D stage `CALIBRATED_2D_LEGACY_REFERENCE_NOT_CANONICAL_3D`; OBJ `GEOMETRY_BOOTSTRAP_BLENDER_IMPORTED_NOT_CALIBRATED_FINAL_ART`.
- **intended hypothesis:** size people from room geometry (horizon / camera height) and occlude with foreground furniture so they do not sit on tables (**sourced fact**, stage.py).
- **source inputs:** generated room plates `rm_wide`, `rm_table`, `rm_door`, `rm_stove`; figure plates `pg_pl_*`.
- **model/tool/generation route:** plates via Anima; composite via Pillow (`panelcomp.py` cutout/grade/ink_edge/contact_shadow); later Blender 5.2.1 portable, kitchen OBJ hash `20904fc8ddcaf561227a227a95eac3f2181744196da0f8e70da98df81c69effa` (**sourced fact**, experiment-log). Tracked files: `C:\AgentWorkspaces\anime-pipeline\assets\stages\kitchen-table-stage-v1.obj|.blend` and `…-v2-neutral-anchors.obj|.blend`.
- **prompt architecture:** room prompts in `rooms.json` / `build_rooms.py`.
- **character identity method:** cut out LoRA plates, grade to stove-warm or door-cool.
- **environment/spatial-continuity method:** `Room(horizon, cam_height, floor_near, floor_far, occluder polygons)`; table 0.75 m used to solve E ≈ 1.09 m seated (**sourced fact**, rooms_def.py). ADR-0011/0012: structural geometry ≠ renderable proxy; world-X vs screen-left must be explicit.
- **panel-planning method:** four CH01 two-shots p006/p007/p008/p010 in `make_page01.py` then calibrated `make_page03.py`.
- **selection/rejection:** skip if plate missing; later production acceptance of pagecomp3 hashes.
- **repair:** pagecomp → pagecomp2 → pagecomp3 recalibration.
- **lettering:** none on these four art panels (**sourced fact**, accepted record limitations).
- **build/reader:** PNG files in `pagecomp3/`.
- **validation:** `src/north_garden/validate_production_records.py`; accepted record hashes.
- **panel/chapter/output counts:** 4 accepted panels; 4 calib PNG; 4 pagecomp versions × 4 panels; Blender control bundles v1/v2 several diagnostic PNG under `experiments/outputs/blender_*`.
- **generated-vs-tracked:** composites gitignored; JSON hashes tracked in `production/accepted/ch01-kitchen-sequence-v1.json`.
- **known owner response:** the Ryan quote that caused this generation.
- **strongest evidence paths:** `garden/stage.py`; `garden/rooms_def.py`; `garden/panelcomp.py`; `garden/make_page03.py`; `production/accepted/ch01-kitchen-sequence-v1.json`; `production/stages/kitchen-table-spatial-contract-v1.json`; `experiments/results/blender_kitchen_stage_import_20260901.json`.
- **visible strengths:** occlusion + contact shadow + grade; only internally accepted narrative sequence.
- **visible failures:** actor plates still carry furniture; Blender diagnostic camera inverts X (ADR-0012); FLUX/Illustrious no-change controls restyle ~99.9% of pixels (not targeted repair).
- **reproducibility/licensing:** historical gens uninstrumented; adult LoRA plates; Blender output ownership OK, inputs not commercially cleared.
- **what next inherited:** spatial-contract fields on ComicPanelPlans; compositor idea reused in actor_matte and Ember SVG stacking.
- **whether inheritance improved the page:** **observation** — for the four kitchen panels, yes relative to uncomposited duos (that is why they were accepted). It did not scale to 50-panel chapters.

### G05 — North Garden v2 production-record system (git)

- **identifier:** `north-garden-v2-records-and-harness`
- **story:** North Garden Soren/Sigrid fictional-adult continuity (CH01–CH13 plans).
- **branch / commit / worktree:** `main` `40e79400…` and all later isolated branches. Source lives in this review tree.
- **date:** 2026-09-01 initialize (`481c1e1`) through 2026-09-03 lettered editions.
- **status:** durable compiler/ledger; art mostly unaccepted.
- **intended hypothesis:** model-agnostic loop with addressable panels, assertions, and replaceable renderers (`GOAL.md`).
- **source inputs:** `research/authoritative/v2.1.1/` gauntlet; development scripts; owner promotion decisions.
- **model/tool/generation route:** none required for the record layer.
- **prompt architecture:** hashed prompt blueprints (ADR-0131); ComicPanelPlan lettering-safe zones.
- **character identity method:** `production/comic/continuity/ch05-fictional-adult-visual-profile-r1.json`; ADR-0017 no child-coded tags; ADR-0101 cast membership ≠ role order.
- **environment/spatial-continuity method:** `spatial_mode` `grounded` | `cheated` | `2d_only`; kitchen contract ID on grounded CH01 plans.
- **panel-planning method:** ComicPanelPlan collections; CH05 50; CH06–CH13 40 each.
- **selection/rejection:** append-only run ledgers; illegal transitions fail closed (ADR-0028).
- **repair:** panel-specific policies; P036/P044 mask mechanics; OpenAI selected for bounded hardening (ADR-0025) **without** CH05 uploads (ADR-0026).
- **lettering/SFX/UI:** proposed safe zones on plans; Pillow overlays for review; CH06–CH13 local lettering review packet (25 PNG).
- **build/reader:** `experiments/review-packets/ch05-owner-review-index-r1`…`r9` HTML; CH06–CH13 progression hubs.
- **validation:** `src/north_garden/validate_production_records.py`; frozen v2.1.1 research validator; 217 ADRs under `docs/adr/`; 603 Python files under `src/north_garden/` (**measured result**).
- **panel/chapter/output counts:** **measured result** — CH01 v1/v2: 4 plans; CH02: 3; CH03: 3; CH04: 3; CH05: 50; CH06–CH13: 40×8 = 320; total current plans **423** (CH01 counted once from v2). Inventory doc `docs/research/comic-panel-plan-chapter-inventory-r1.md` still describes CH01–CH04 as fragments and CH05 as the only full chapter (written before CH06–CH13 authoring).
- **generated-vs-tracked:** records tracked; rasters ignored.
- **known owner response:** CH05 script + visual-direction approvals.
- **strongest evidence paths:** `docs/architecture/overview.md`; `GOAL.md`; `src/north_garden/`; `production/comic/`; `docs/adr/`.
- **visible strengths:** immutable IDs, fail-closed gates, license registry, cost ledgers, no child likeness.
- **visible failures:** Goodhart risk — validators pass while owner bar is unmet (owner prompt 2026-09-06). Human minutes mostly null.
- **reproducibility/licensing:** source is reproducible; generated art is not, by policy.
- **what next inherited:** every reimagining copies ComicPanelPlan / RenderRecord / ignore-rasters / adult-only / $0 default.
- **whether inheritance improved the page:** **hypothesis** — improved auditability more than visible serial quality.

### G06 — `baseline_legacy` Stage A benchmark

- **identifier:** `baseline-legacy-stage-a`
- **story:** frozen gauntlet cases (G01, G07a/b, G11a, …), not a chapter.
- **branch / commit:** tracked manifests + ignored `experiments/records/baseline_legacy/` (24 JSON).
- **date:** 2026-08-31.
- **status:** completed; **rejected without tuning**.
- **intended hypothesis:** wrap `garden/gen3.py` unchanged and score the frozen 12-case × 2-seed subset.
- **source inputs:** `research/authoritative/v2.1.1/bench/gauntlet.json` SHA-256 `f826b0f1d06ed5a999667bde23ba0d04f8ebb22f516095034dab62c7541ae9ae`.
- **model/tool/generation route:** same Anima graph; RTX 5090 Laptop; 903.79 s total / 37.66 s mean (**sourced fact**, `docs/research/benchmark-history.md`).
- **prompt architecture:** adapter mapping from gauntlet; `DRAFT_LEGACY_LIMITED_NOT_FROZEN` because no canonical stage bundle.
- **character identity method:** LoRA + regional text.
- **environment/spatial-continuity method:** legacy 2D, declared not comparable grounded evidence.
- **panel-planning method:** BenchmarkCaseBundle v1.
- **selection/rejection:** no candidate passed all assertions; G11a both seeds extra child (zero-tolerance).
- **repair:** none (ADR-0002: do not tune baseline).
- **lettering:** none.
- **build/reader:** records JSON + Comfy `baseline_legacy/` 28 PNG.
- **validation:** HardAssertionManifest; agent visual triage only; human minutes unmeasured.
- **panel/chapter/output counts:** 24 renderer generations, 0 accepted.
- **generated-vs-tracked:** records ignored; summaries tracked in `experiments/results/baseline_legacy_stage_a_20260831.json` if present locally (gitignore `experiments/` — **observation:** result JSON is local-only).
- **known owner response:** null for this arm.
- **strongest evidence paths:** `src/north_garden/baseline_legacy.py`; `docs/research/benchmark-history.md`; `docs/adr/ADR-0002-baseline-legacy-is-a-failure-profile-arm.md`; `manifests/benchmark/stage-a-v1.json`.
- **visible strengths:** honest failure profile; extra-child catch.
- **visible failures:** photoreal regression, identity/role, unstable set, interaction/blocking.
- **reproducibility/licensing:** same as G01; Comfy must be running.
- **what next inherited:** all later arms compare against this failure profile rather than retuning it.
- **whether inheritance improved the page:** N/A (not a page). It improved measurement.

### G07 — Sequential inpaint, actor-matte, FLUX Klein, Illustrious/Xinsir

- **identifier:** `ng-repair-and-proxy-renderer-arms`
- **story:** G07 seated-table role-swap; fictional orange/teal tokens; kitchen stage.
- **branch / commit:** tracked ADRs/results pointers; ignored outputs under `experiments/outputs/` and `ComfyUI/output/`.
- **date:** 2026-08-31 to 2026-09-01.
- **status:** multiple completed smokes; **no production-accepted experimental outputs** (experiment-log ledger: 58 local gens, 2113.602 s, $0).
- **intended hypothesis:** per-character inpaint, separable actor plates, geometry proxies, or a different checkpoint can fix baseline failures.
- **source inputs:** kitchen plates; Blender controls; fictional proxies (no adult refs on FLUX).
- **model/tool/generation route:**
  - sequential inpaint: Anima inpaint, 4+8 gens; target MAE 0.223–0.276 vs non-target 0.0032–0.0039; broad masks redraw set (ADR-0004).
  - actor_matte: 0 diffusion; 91.60%/91.31% pixels unchanged outside actor/shadow; seated-at-table 0/2.
  - FLUX.2 Klein 4B local: Apache transformer + **non-commercial VAE** `flux2-vae`; reference-edit ~84–86% pixels changed (not no-change).
  - geometry tiles: 4/4 count/order under stage-scoped sensor; markers become chair-like 3/4.
  - Illustrious XL v2 OpenRAIL-M pending; Xinsir ControlNet Union ProMax Apache-2.0; mask-limited composite 0 exterior change, rectangular seam not art.
- **prompt architecture:** adapter-specific graphs in `experiments/workflows/`.
- **character identity method:** none on FLUX (proxy tokens); LoRA plates on actor_matte.
- **environment/spatial-continuity method:** geometry proxy / Blender bundle v2 with explicit world-to-panel map.
- **panel-planning method:** G07a/G07b frozen semantics, draft bundles.
- **selection/rejection:** agent triage + pixel MAE; all production-rejected.
- **repair:** this cluster *is* the repair research.
- **lettering:** none.
- **build/reader:** diagnostic PNGs.
- **validation:** proxy tile QA injections 1/1 pass + 3/3 error rejections; ADR-0006..0015, 0040–0055.
- **panel/chapter/output counts:** see experiment-log; Comfy subdirs listed in §4.
- **generated-vs-tracked:** ignored rasters; ADR + some `docs/research/evidence/*.json` tracked (237 JSON under `docs/research/evidence/` in this tree — **measured result** from list_dir).
- **known owner response:** null per-arm; G07 packet later “all great” is qualitative on bakeoff presentations, not these local smokes.
- **strongest evidence paths:** `docs/research/experiment-log.md`; `docs/research/benchmark-history.md`; `experiments/results/*` locally; ADRs 0003–0015.
- **visible strengths:** fail-closed no-change tests; geometry as spatial interface; exterior-preserving composite.
- **visible failures:** inpaint set drift; non-separable actors; FLUX restyle; count bugs on circle tokens.
- **reproducibility/licensing:** FLUX VAE NCL blocks commercial profile; Illustrious OpenRAIL-M review-pending.
- **what next inherited:** OpenAI selected instead for repair hardening; Ember later uses “localized repair + hash proof” as a lesson, not these graphs.
- **whether inheritance improved the page:** **observation** — no accepted page emerged from these arms.

### G08 — G07 fictional provider bakeoff

- **identifier:** `g07-provider-bakeoff`
- **story:** fictional two-adult kitchen role-swap controls (public-controls PNGs).
- **branch / commit:** tracked provider records (hash-only vault); ignored candidates in `experiments/outputs/{bfl,gemini,openai,xai}_*_g07_bakeoff_r1/`.
- **date:** 2026-09-01.
- **status:** 16/16 required candidates + one paid xAI transport failure; $1.057377 aggregate; **0 accepted**; G07 human review 0/20.
- **intended hypothesis:** compare Gemini 3.1 Flash Image, Grok Imagine Image 2.0, OpenAI GPT Image 2, BFL FLUX.2 on the same fictional controls before picking a production arm.
- **source inputs:** exactly two approved public controls (`public-controls/g07a-no-change-r1.png`, `g07a-role-id-r1.png`). BFL closed to any other input (ADR-0019).
- **model/tool/generation route:** **sourced fact** (`model-license-registry.md`): Gemini 4/4 $0.268756; xAI 4/4 $0.28 + $0.07 failure; OpenAI 4/4 $0.198621 snapshot `gpt-image-2-2026-04-21`; BFL 4/4 $0.24. ADR-0025 selects OpenAI for bounded targeted-repair hardening.
- **prompt architecture:** bakeoff protocol in `docs/research/frontier-renderer-paths-20260901.md`.
- **character identity method:** fictional adults on the control images; no Soren LoRA upload.
- **environment/spatial-continuity method:** control image + edit instructions.
- **panel-planning method:** G07 assertions, not chapter plans.
- **selection/rejection:** blinded packet `experiments/review-packets/g07-blinded-human-review-r1/` (16 PNG). Owner qualitative “all great”; formal timed session never run.
- **repair:** OpenAI hardening later (16 px cosine feather, P036 causal shape) on **abstract** controls, not CH05 art.
- **lettering:** none.
- **build/reader:** blinded packet JSON + owner hub.
- **validation:** vault root `e84b0402…6d3ab`; restoration archive 19,879,277 bytes hash `64bea215…69cad7` (GOAL.md).
- **panel/chapter/output counts:** 16 candidates + controls; 19 provider records.
- **generated-vs-tracked:** 2 control PNGs tracked; candidates ignored and hash-pinned.
- **known owner response:** “reviewed everything; all great; approved” — qualitative only.
- **strongest evidence paths:** `docs/research/g07-provider-bakeoff-comparison-20260901.md`; `production/decisions/ng-decision-owner-visual-direction-r2.json`; `docs/adr/ADR-0025-select-openai-gpt-image-2-for-bounded-targeted-repair-hardening.md`.
- **visible strengths:** exact cost/request IDs; BFL data-use boundary recorded; no likeness upload.
- **visible failures:** owner approval ≠ 20 timed decisions; CH05 still had 0 executable provider panels after selection.
- **reproducibility/licensing:** BFL terms grant training rights on inputs/outputs; OpenAI business data not used for training by default (registry). Outputs uncleared.
- **what next inherited:** OpenAI as *selected mechanism*, unused for CH05 production; CH05/reimaginings instead used **built-in ImageGen** (no snapshot).
- **whether inheritance improved the page:** **observation** — CH05/reimagining pages were not generated on the selected OpenAI API.

### G09 — CH01–CH04 North Garden fragments

- **identifier:** `ng-ch01-ch04-fragments`
- **story:** CH01 kitchen argument; CH02 treeline return; CH03 ridge signal; CH04 dawn trail.
- **branch / commit:** `main` and descendants. Editions: `production/editions/north-garden-research-edition-001.json` / `002`; ch02 research; ch03/ch04 imagegen drafts.
- **date:** CH01 acceptance 2026-08-31; CH03/CH04 imagegen 2026-09-01.
- **status:** CH01 `INTERNAL_RESEARCH_ACCEPTED_NOT_PUBLISHED`; CH02 archival; CH03/CH04 draft unaccepted. Below 50-panel lower bound (`GOAL.md`).
- **intended hypothesis:** instrument a real sequence; then smoke frontier imagegen on 3-panel chapters.
- **source inputs:** G04 composites; later built-in ImageGen text-only fictional adults.
- **model/tool/generation route:** CH01 `baseline_legacy_composite_stage` + `make_page03.py`; CH03/CH04 `built-in-image_gen` with **null** model/seed/cost (`model-license-registry.md`). ADR-0020: age-wording hygiene incident in built-in CH03.
- **prompt architecture:** 3 ComicPanelPlans per CH03/CH04; CH01 v2 separates panel_id from plan_revision_id (ADR-0016).
- **character identity method:** LoRA plates (CH01); fictional design assets (CH03/CH04).
- **environment/spatial-continuity method:** CH01 grounded kitchen contract; CH03/CH04 `2d_only`.
- **panel-planning method:** 4 / 3 / 3 / 3 plans.
- **selection/rejection:** Codex visual review on CH01; CH03/CH04 review JSON pending human.
- **repair:** CH03 two-axes repair PNG exists under `experiments/outputs/built_in_imagegen_ch03_ridge_signal/`.
- **lettering:** none on accepted CH01; smoke overlay later on CH05 not these.
- **build/reader:** `experiments/review-packets/narrative-sequences-20260901/`.
- **validation:** chapter_lint JSON under experiments/results.
- **panel/chapter/output counts:** 4 accepted kitchen PNG; CH03 4 output PNG; CH04 3; CH02 historical duo records.
- **generated-vs-tracked:** hashes in editions; pixels ignored.
- **known owner response:** CH05 smoke (not these fragments) plus G07.
- **strongest evidence paths:** `production/accepted/ch01-kitchen-sequence-v1.json`; `production/editions/`; `docs/research/comic-panel-plan-chapter-inventory-r1.md`.
- **visible strengths:** only accepted sequence; ID/revision split.
- **visible failures:** not chapter-scale; CH03/CH04 unreproducible imagegen; ADR-0020 incident.
- **reproducibility/licensing:** CH01 historical uninstrumented; imagegen provenance-limited.
- **what next inherited:** CH05 50-plan promotion after owner liked the *style* of smoke art, not these 3-panel drafts as chapters.
- **whether inheritance improved the page:** CH01 page exists; CH03/CH04 remain probes.

### G10 — CH05 Mill Signal six-route complete chapter

- **identifier:** `ng-ch05-six-route-complete-chapter`
- **story:** CH05 “Mill Signal” — pair leave farmhouse, follow mill smoke, return to unexpected house smoke. 50 comic-only `2d_only` plans.
- **branch / commit:** assembled on 2026-09-02 (`b122aa1` premium/semantic-pass, `ff1a8c4` six-route release, etc.) and present on `40e79400` / later heads.
- **date:** plans promoted 2026-09-01; complete-chapter routes 2026-09-02; overnight closeout 2026-09-03.
- **status:** `FROZEN_REVIEW_CANDIDATE_UNACCEPTED`. 0 commercially cleared. Sequence-cadence hybrid: 47 PASS / 3 WARN / 0 FAIL agent triage (**sourced fact**, `docs/research/ch05-complete-chapter-review-handoff-r7.md`).
- **intended hypothesis:** a role-aware hybrid (clear-line watercolor travel, graphic anchors, premium-cel faces, limited-ink inserts) can complete a 50-panel phone scroll without waiting for OpenAI upload authority.
- **source inputs:** 50 ComicPanelPlans `production/comic/ch05-sc01-panel-plans-v1.json`; fictional-adult profile; some earlier smoke/style candidates reused as layout assets (production map: 14 reuse / 36 new at map time).
- **model/tool/generation route:** **built-in ImageGen** (`imagegen-default` / `built-in-image_gen` in later Ember records; CH05 same family). Model snapshot **null**. Six full 50-panel style arms plus a cadence assembly:
  1. r6 complete-chapter draft
  2. alternate graphic
  3. clear-line watercolor
  4. premium cel
  5. flat graphic-gouache
  6. reduced-palette text control  
  Assembly: reduced-palette S01 (5) + r6 S02–S08 (34) + premium cel S09–S11 (11).
- **prompt architecture:** per-route prompt manifests under `production/comic/run-manifests/ch05-complete-chapter-*-prompt-manifest-r1.json`; text-free art; reserved safe zones top-left/right/center.
- **character identity method:** prompt contracts (Soren light-brown/dark-blond oatmeal coat; Sigrid dark bun + plaid wrap) + optional reference images from prior CH05 candidates. S01/S11 reference-ablation exists.
- **environment/spatial-continuity method:** `2d_only`; object-state chain (map → twine → cloth → tin → farmhouse smoke) in production map; continuity atlas ADR-0102.
- **panel-planning method:** 50 plans, 11 sequences, variable cadence (ADR-0089, ADR-0103).
- **selection/rejection:** agent triage sheets per route; six-route comparison PNGs; strongest-candidate worksheet. Owner exact-base still null.
- **repair:** targeted-repair crops r1–r5; premium-cel trio; P036 plank-reach-brace (ADR-0087) never provider-executed on real art.
- **lettering/SFX/UI:** Pillow review lettering (provisional copy); transparent rehearsal; outside-art bands (ADR-0092); width/copy sensitivity 31 PNG; lettering-safe overlays on long scrolls (1200×26776).
- **build/reader:** phone 390×8702 cadence lettered scroll; owner-review-index r1–r9 HTML; long-scroll PNG.
- **validation:** semantic-graph validator; density metrics (entropy/edge/bytes); sequence-boundary audit; overnight integrity gates. Semantic PASS/WARN/FAIL from handoff r7:

| Route | Semantic P/W/F | Overall P/W/F | Entropy | Edge density | PNG B/px |
|---|---|---|---|---|---|
| r6 | 47/1/2 | 49/1/0 | 6.889241 | 0.220004 | 1.623124 |
| alternate graphic | 36/7/7 | 36/7/7 | 6.837860 | 0.215718 | 1.608028 |
| clear-line watercolor | 45/2/3 | 45/2/3 | 7.025710 | 0.244026 | 1.698281 |
| premium cel | 40/5/5 | 40/5/5 | 6.934245 | 0.227841 | 1.656707 |
| flat graphic-gouache | 41/6/3 | 16/7/27 | 6.897733 | 0.211280 | 1.581633 |
| reduced-palette text | 43/4/3 | 6/6/38 | 6.572611 | 0.149995 | 1.397747 |

- **panel/chapter/output counts:** 50 plans × 6 routes ≈ 300 chapter rasters plus comparisons. **Measured result** review-packet rasters (PNG): r6 drafts r1–r6 ~70–129 each; alt-graphic 130; watercolor 130; premium-cel 130; gouache 130; reduced-palette 130; semantic-pass-hybrid 134; sequence-cadence 71; overnight 69; lettering packs 25–31.
- **generated-vs-tracked:** ignored rasters; tracked handoff markdown + production JSON.
- **known owner response:** approved *direction* and smoke contact sheet; no recorded per-route acceptance after six-route build.
- **strongest evidence paths:** `docs/research/ch05-complete-chapter-review-handoff-r7.md`; `docs/research/ch05-complete-chapter-production-map-r1.md`; `production/comic/recommendations/ch05-pipeline-route-recommendation-r1.json`; `C:\AgentWorkspaces\anime-pipeline\experiments\review-packets\ch05-six-route-comparison-r1\`.
- **visible strengths:** first complete 50-panel scroll; measured density; role-aware hybrid; phone assembly.
- **visible failures:** reduced-palette density win with 27 lettering failures; P003/P032/P045 WARNs; route-boundary P005→P006 visual concern not isolated; no exact production base; built-in ImageGen non-reproducible.
- **reproducibility/licensing:** provenance-limited; $0 direct API; adult fictional only.
- **what next inherited:** CH06–CH13 default house route uses CH05 style refs (`P050-wide-action-clean-graphic-r1.png`, `P040-medium-close-cel-painted-r1.png`). Reimaginings inherit phone 390, safe zones, density classes, and “don’t trust style labels” (ADR-0094).
- **whether inheritance improved the page:** **hypothesis** — first time a full chapter can be read as a scroll, which is a page-level improvement over 3–4 panel fragments; owner 2026-09-06 quote still says the bar is unmet.

### G11 — CH06–CH13 default house-route chapters

- **identifier:** `ng-ch06-ch13-house-route`
- **story:** Bell Road progression — farmhouse node → Mireback combat → northward mission → Brackenwake factions → North Garden climax. Titles **measured** from plan JSON: CH06 The House That Answered; CH07 Mireback at the Gate; CH08 The Root Road; CH09 Below the Black Weir; CH10 Iron for a Name; CH11 The Orchard Siege; CH12 The Map That Lied; CH13 The North Garden.
- **branch / commit:** commits 2026-09-03 `80fee7d` … `40e79400`. Worktree root-main and all later clones.
- **date:** 2026-09-03.
- **status:** `AUTHORING_COMPLETE_NOT_PROMOTED_PROVISIONAL_CANON` on plan collections; execution `EXECUTED_AGENT_TRIAGED_OWNER_REVIEW_PENDING` (`ch06-default-house-route-execution-r1.json`).
- **intended hypothesis:** chronological 40-panel chapters with visible class/injury/wardrobe persistence beat “more hero panels” (ADR-0096, ADR-0088 LitRPG silhouette without retcon).
- **source inputs:** CH05 selected style rasters as Image 1/2 references; 40 ComicPanelPlans per chapter.
- **model/tool/generation route:** built-in ImageGen **five-panel chronological strips** (see CH06 exact_prompt in execution manifest). Same null snapshot.
- **prompt architecture:** `ch06-ch07-default-house-route-prompt-manifest-r1.json` and CH08–09, CH10–11, CH12–13 pairs; 5 panels per request, numbered order, gutters, scale roles.
- **character identity method:** long invariant paragraphs (hair never black/bright-blond / never blond-red-curls); Tamsin distinct; Garden Ledger as frost-green inscription on real surfaces, not HUD.
- **environment/spatial-continuity method:** carried object/injury state in plans; CH12–CH13 shoulder persistence hardening (8 PNG packet).
- **panel-planning method:** 40 plans × 8 = 320; declared_target_panel_count 40.
- **selection/rejection:** default-house-route review packets 53 rasters × 8 chapters (**measured result**).
- **repair:** shoulder-persistence hardening prompts; sparse lettering editions (`40e79400`).
- **lettering/SFX/UI:** `production/comic/ch06-ch13-lettering-copy-r1.json`; local lettering review 25 PNG; still provisional.
- **build/reader:** progression hubs CH06–CH09 / CH06–CH11 / CH06–CH13 (3 PNG each packet).
- **validation:** semantic graphs; cross-chapter continuity review doc.
- **panel/chapter/output counts:** 320 plans; 8 × 53 = 424 review-packet rasters plus hardening 8.
- **generated-vs-tracked:** plans tracked; rasters ignored.
- **known owner response:** null recorded after CH05 direction (no CH06–13 owner-approval JSON found).
- **strongest evidence paths:** `docs/research/north-garden-ch06-ch13-progression-plan-r1.md`; `production/comic/ch06-sc01-panel-plans-r1.json` … `ch13-…`; `production/comic/run-manifests/ch06-default-house-route-execution-r1.json`; `C:\AgentWorkspaces\anime-pipeline\experiments\review-packets\ch06-default-house-route-r1\`.
- **visible strengths:** chapter-scale continuity flags; injury persistence; 5-panel strip is the topology Borrowed Down also uses.
- **visible failures:** still ImageGen-null provenance; 5-panel sheets bake multi-moment risk later diagnosed in Borrowed Down; owner review pending.
- **reproducibility/licensing:** same built-in ImageGen limits.
- **what next inherited:** Borrowed Down 5-cell sheets; City rejected 3×2 in favor of 3-panel vertical strips; Ember rejected multi-moment sheets for individual critical panels.
- **whether inheritance improved the page:** **hypothesis** — more story breadth; visual identity still CH05 house style, so owner-bar gap likely persists.

### G12 — Borrowed Down

- **identifier:** `borrowed-down-ten-chapter`
- **story:** Veyr, gravity-rationed city beside a vertical ocean; Mae Nox & Dax Pell. Pressure-print / woodcut-risograph style.
- **branch / commit / worktree:** `autonomous/ten-chapter-reimagining-20260903` `fa6650a4…` (content `f77663a8` 2026-09-03 20:10:37). `C:\AgentWorkspaces\anime-pipeline-reimagining-20260903`.
- **date:** 2026-09-03.
- **status:** complete owner-review volume; unaccepted; commercially uncleared.
- **intended hypothesis:** a new original story + extreme graphic style avoids Garden likeness and tests 10-chapter production in isolation from `main`.
- **source inputs:** `production/reimaginings/borrowed-down/source/ch*-sequences.json`; style probes (4 treatments, no image refs).
- **model/tool/generation route:** built-in ImageGen; model/endpoint/usage/cost **null**; $0 (`cost-and-timing-summary.json`). 67 generation requests; 15939.808 s summed latency.
- **prompt architecture:** one 3×2 sheet per sequence; first five cells story, sixth environment motif; lettering clearance rectangles in prompt (`src/reimaginings/borrowed_down/pipeline.py`).
- **character identity method:** frozen CHARACTERS strings + `mae-dax-character-anchor.png` (61 recorded uses) + `pressure_print_style_anchor` (60).
- **environment/spatial-continuity method:** irreversible_state list accumulated across 60 sequences; continuity-graph JSON.
- **panel-planning method:** 10 × 6 sequences × 5 panels = **300** ComicPanelPlans (`volume-manifest.json`).
- **selection/rejection:** sequence PASS/WARN/FAIL 34/26/0; 2 preserved failed diagnostics (`ch08-s01` spent-knot, `ch10-s04` creature); replacement isolated (ADR-R004, ADR-R005).
- **repair:** localized; CH10-S04-P05 r2; non-target hash proof claimed in FINAL_AUDIT.
- **lettering/SFX/UI:** local Pillow on 300 entries; speaker metadata review-only; **observation:** FINAL_AUDIT says generated safe-area rectangles remain in unlettered candidates (blank baked regions).
- **build/reader:** per chapter `chXX-reading-draft.png`, `chXX-phone-preview.png`, compact lettered, contact, safe-zone; 4 HTML hubs in experiments/.
- **validation:** pipeline tests; integrity; protected refs unchanged True (`START_HERE.md`).
- **panel/chapter/output counts:** **measured result** — 300 selected panels; 809 PNG on disk; 71 files/chapter (6 sequence sheets + 30 crops + 30 lettered crops + 5 review PNGs).
- **generated-vs-tracked:** 147 production JSON tracked; rasters ignored.
- **known owner response:** none in-repo after delivery; later LitRPG prompt lists this generation among failures (busy, generic, weak lettering/action, complexion homogenization, missing LitRPG UI — City/Borrowed both in scope of that sentence).
- **strongest evidence paths:** `C:\AgentWorkspaces\anime-pipeline-reimagining-20260903\docs\reimaginings\borrowed-down\START_HERE.md`; `FINAL_AUDIT.md`; `src/reimaginings/borrowed_down/pipeline.py`; experiments raster root.
- **visible strengths:** isolation; localized repair with preserved failures; 300-panel complete volume; distinct graphic thesis.
- **visible failures:** baked blank lettering holes; 26 WARN sequences; 3×2 density; owner later rejects the family of looks.
- **reproducibility/licensing:** ImageGen null fields; $0; uncleared.
- **what next inherited:** City keeps isolation + RenderRecords + localized lettering repair **without** 3×2 sheets. Ember ledger explicitly retains “localized defects get localized repair”.
- **whether inheritance improved the page:** **hypothesis** — first full original volume is a production improvement; owner binding diagnosis says the *look* did not clear the bar.

### G13 — The City Keeps Oaths

- **identifier:** `the-city-keeps-oaths-ten-chapter`
- **story:** Caelune; Sola Merrow, Tarin Kest; Covenant Lattice (diegetic promises, **no numeric LitRPG HUD**). Clean cinematic fantasy-webtoon.
- **branch / commit / worktree:** `autonomous/ten-chapter-clean-webtoon-20260903-213010` `d1cfa464…` (content `562b2295` 2026-09-03 23:39:31). `C:\AgentWorkspaces\anime-pipeline-reimagining-clean-webtoon-20260903-213010`.
- **date:** 2026-09-03.
- **status:** delivered; validation PASS; owner-review-pending; unaccepted.
- **intended hypothesis:** clean cel + 3-panel vertical strips + Covenant progression will read more like licensed webtoon than Borrowed Down’s woodcut sheets.
- **source inputs:** `production/reimaginings/the-city-keeps-oaths/source/volume.json`; style candidate A (93/100) locked; topology pilot 94/100 vs 3×2 (**sourced fact**, START_HERE.md).
- **model/tool/generation route:** built-in ImageGen; 91 requests (80 production + 9 style/topology + 2 refs); 28172.185 s summed; $0; model/seed null (`FINAL_AUDIT.md`).
- **prompt architecture:** two text-free 3-panel portrait strips per 6-panel sequence; Image 1 style anchor, Image 2 Sola sheet, Image 3 supporting adults (`the_city_keeps_oaths/pipeline.py`).
- **character identity method:** CHARACTERS dict + hash-pinned sheets `references/sola-progression-sheet-v1.png`, `supporting-adults-sheet-v1.png`.
- **environment/spatial-continuity method:** state_adds per sequence; LETTERING_OVERRIDES for specific panels.
- **panel-planning method:** 10 × 4 sequences × 6 panels = **240**.
- **selection/rejection:** manual sequence PASS 29 / WARN 11; metric proxy PASS 54 / WARN 186 (edge 144, high-frequency 160, entropy 98, focal 54).
- **repair:** 7 lettering-clearance defects by **moving safe zones only**; 0 source regen; CH03/CH04 before-after PNG.
- **lettering/SFX/UI:** Pillow; 240 entries; remaining WARNs include lettering/SFX encroaching heads (3+1).
- **build/reader:** tracked `docs/reimaginings/the-city-keeps-oaths/viewer.html`; per-chapter reading-draft / phone / compact / contact / grayscale / density / safe-zone / source-strips.
- **validation:** closeout-report PASS; integrity PASS vs protected trees.
- **panel/chapter/output counts:** **measured result** — 240 panels; 421 PNG; 39 files/chapter (8 source strips + 24 panel crops + 7 review PNGs).
- **generated-vs-tracked:** 183 production JSON + viewer HTML tracked; rasters ignored.
- **known owner response:** no City-specific approval JSON. Owner LitRPG prompt (2026-09-04) treats prior attempts including this look as binding failures (busy, generic painterly, weak ToG/SL translation, lettering, action, complexion, missing LitRPG machinery). Ember ledger’s “rejects its visual result” is that prompt, not a second quote.
- **strongest evidence paths:** `…\docs\reimaginings\the-city-keeps-oaths\START_HERE.md`; `FINAL_AUDIT.md`; `viewer.html`; `src/reimaginings/the_city_keeps_oaths/pipeline.py`; raster root.
- **visible strengths:** navigable viewer; 3-panel phone crops; lettering repair without regen; Covenant is a real progression *fiction* even without HUD.
- **visible failures:** 186/240 metric WARN; generic cinematic convergence named by owner; no numeric system UI (later treated as a genre miss, not a City bug relative to its own bible).
- **reproducibility/licensing:** same ImageGen nulls; $0; uncleared.
- **what next inherited:** Ember keeps individual-panel generation, phone 390, SVG-not-Pillow lettering, **and** numeric Ledger UI that City deliberately omitted.
- **whether inheritance improved the page:** **hypothesis** — cleaner than Borrowed Down on City’s own topology pilot (94/100); owner still placed it below the named bar.

### G14 — Ember Lattice Phase A owner-review pilot

- **identifier:** `ember-lattice-phase-a-pilot`
- **story:** Ember Lattice; Elian Voss & Mira Vale; Hollow Meridian / Ledger LitRPG. Candidate B locked.
- **branch / commit / worktree:** `6a239225` 2026-09-04 01:15:09 on the litrpg-manhwa branch; still present at `023330e8` and `99cb5e9e`.
- **date:** 2026-09-04.
- **status:** owner **APPROVED** (`owner-approval.json`); Phase B authorized.
- **intended hypothesis:** individual critical panels + Candidate B cel line + visible XP/class UI + 16-panel density contract will not repeat City/Borrowed failures (`failure-correction-contract.md`).
- **source inputs:** three style sheets, identical narrative evidence; Candidate B 96/100, A 91, C 85 (**sourced fact**, cumulative ledger).
- **model/tool/generation route:** only built-in ImageGen authorized; local Comfy/LoRA caches **not used** (isolation). Route-audit: 1 available route.
- **prompt architecture:** one panel per request for critical beats; Candidate B style paragraph; reserved negative space.
- **character identity method:** hash-pinned fair/light Elian + distinct Mira; fresh refs only.
- **environment/spatial-continuity method:** system-state JSON; density 11 low / 3 moderate / 2 high precommitted.
- **panel-planning method:** 16 ComicPanelPlans (`docs/reimaginings/ember-lattice/pilot/`).
- **selection/rejection:** validation `PASS_WITH_WARN`; P005 planned-low reads moderate (1/11 = 9.1% < 25% fail-closed).
- **repair:** none required for hard gates.
- **lettering/SFX/UI:** organic SVG v1 then v2 after owner balloon complaints; 16 safe-zone SVGs.
- **build/reader:** `pilot/index.html`, `reader.html`, `safe-zones.html`.
- **validation:** `pilot/validation-report.json`; integrity before/after.
- **panel/chapter/output counts:** 16 panels; 18 raster files in experiments/pilot (16 source + 2 diagnostics); 16 SVG panels + 16 safe-zones tracked.
- **generated-vs-tracked:** SVG/HTML tracked; PNG ignored.
- **known owner response:** “great selection; art and candidate B are amazing” + five required Phase B lettering/system changes.
- **strongest evidence paths:** `production/reimaginings/ember-lattice/owner-approval.json`; `docs/reimaginings/ember-lattice/phase-a-pilot-audit.md`; `docs/reimaginings/ember-lattice/pilot/`.
- **visible strengths:** mandatory gate respected; style lock; density fail-closed.
- **visible failures:** owner still required smaller balloons, more copy, more system UI — lettering v1 failed the owner even when art was praised.
- **reproducibility/licensing:** ImageGen null; $0; uncleared.
- **what next inherited:** Candidate B + lettering v2 + 24-panel chapter contract.
- **whether inheritance improved the page:** **observation** — first recorded owner praise of a *style candidate* since CH05 smoke; balloon occlusion still failed.

### G15 — Ember Lattice ten-chapter volume (Phase B)

- **identifier:** `ember-lattice-ten-chapter-volume`
- **story:** CH01 The Bridge That Bites … CH10 Strike the Silence. 24 panels/chapter.
- **branch / commit / worktree:** `6f135579` complete volume; `023330e8` integrity close. `C:\AgentWorkspaces\anime-pipeline-litrpg-manhwa-20260904-001211`. Also present (SVG/HTML) on editorial HEAD.
- **date:** 2026-09-04 10:09–10:12.
- **status:** volume-validation **PASS**; art unaccepted; commercially uncleared; `direct_paid_cloud_spend_usd`: 0.
- **intended hypothesis:** Phase B contract (24×10, 35–45% action, 159/60/21 density, 300–520 dialogue words/chapter, 4 system moments/chapter) plus Candidate B yields a LitRPG manhwa volume the owner can read on a phone.
- **source inputs:** 16 approved pilot rasters reused; 224 new panel requests.
- **model/tool/generation route:** built-in ImageGen; `provider_metadata_availability.model = "imagegen-default"`; endpoint `built-in-image_gen`; usage/seed null (`generation-reconciliation.json`).
- **prompt architecture:** one finished source-art panel per request; Candidate B paragraph; subject contracts; creature contracts; reserved br/tl/etc. negative space (`volume/render-records.json` samples).
- **character identity method:** per-prompt subject contracts + reference registry; fair/light Elian enforced by failure-correction contract.
- **environment/spatial-continuity method:** `system-state-ledger.json`; volume-master zone/opening/closing per chapter.
- **panel-planning method:** 240 ComicPanelPlans; 108 action (45.0%).
- **selection/rejection:** selected_and_reviewed_pass 224; 1 preserved hard-fail diagnostic class `non_vertical_source`; 0 missing; 0 unresolved.
- **repair:** 1 localized repair request; `repair-snapshots/ch03-p007-before.json`; repair-comparison.html.
- **lettering/SFX/UI:** SVG v2 — 84% opaque soft balloons, open outlined dialogue, butted/distress shapes, Ledger menus (`src/reimaginings/ember_lattice/build_volume.py`). Phone width 390. Dialogue words 3821; system moments 41; lettering_fit_checks 299; overlap_pair_checks 100 (**sourced fact**, volume-validation.json).
- **build/reader:** 50 chapter HTML + 4 hubs; 240 panel SVG + 240 safe-zone SVG.
- **validation:** volume-validation PASS; system-state-validation PASS; local_review_link_checks 5136.
- **panel/chapter/output counts:** **measured result** — 240 panels; 225 new generated sources + 16 pilot reused; experiments volume rasters 235 (ch01 only 8 on disk because 16 reused from pilot; ch03 25 = 24 + diagnostic). Summed chapter elapsed seconds from reconciliation (partial list): ch01 3460.561; ch02 14246.259; ch03 12122.077; ch04 9672.523; ch05 23949.206; ch06 30649.524; ch07 23945.018; remaining chapters in same JSON.
- **generated-vs-tracked:** SVG/HTML/JSON tracked; PNG ignored.
- **known owner response:** Phase B was authorized from the pilot; **no post-volume owner-approval JSON** was found. 2026-09-06 owner prompt still says the work is not like ToG/SL.
- **strongest evidence paths:** `production/reimaginings/ember-lattice/volume/volume-master.json`; `generation-reconciliation.json`; `volume-validation.json`; `docs/reimaginings/ember-lattice/volume/`; raster root.
- **visible strengths:** complete 10-chapter LitRPG with numeric Ledger; SVG lettering; integrity PASS; 45% action vs City’s quieter covenant story.
- **visible failures:** ImageGen non-reproducibility; CH01 on-disk sources only 8 (rest reused — **observation** reuse can freeze early look); owner bar still open.
- **reproducibility/licensing:** same as G14.
- **what next inherited:** premium R&D uses volume CH01 as **baseline** plates vs new raw/hybrid routes.
- **whether inheritance improved the page:** **hypothesis** — genre machinery and lettering v2 are on-page improvements vs City; whether that meets ToG/SL is out of archivist scope.

### G16 — Ember Lattice premium R&D vertical slice

- **identifier:** `ember-lattice-premium-rd-24-benchmark`
- **story:** same Ember Lattice; 24-panel benchmark covering required scenarios.
- **branch / commit / worktree:** `9d191cbc` 2026-09-04 18:42:11. `C:\AgentWorkspaces\anime-pipeline-ember-lattice-premium-rd-20260904-150943`. Editorial tree contains the built site.
- **date:** 2026-09-04.
- **status:** benchmark site built; hybrid recommended; candidates uncleared.
- **intended hypothesis:** compare baseline (volume plates) vs raw ImageGen vs hybrid (raster + SVG) on a locked 21-criterion rubric; selected non-baseline must win median **and** weakest-panel.
- **source inputs:** volume CH01 rasters as baseline; new openai-raw / targeted-edit folders (75 PNG = 24×3 + extras).
- **model/tool/generation route:** built-in ImageGen again; timing `benchmark_generation_calls: 24`, `benchmark_targeted_edit_calls: 4`; parallel batch walls 251–296 s (`generation-session-timing.json`). Local FLUX.2 Klein present but **not approved** (VAE NCL) — **sourced fact**, ch01-manifest recommendation.
- **prompt architecture:** PremiumBenchmarkManifest/1.0; clean-art instruction + negative-space regions (`ch01-generation-spec.json` later 52-panel file shows the pattern).
- **character identity method:** “fresh isolated reference sheets” in prompts; 3 reference PNGs.
- **environment/spatial-continuity method:** predeclared negative-space geometry.
- **panel-planning method:** ≥24 panels required; suite uses 24.
- **selection/rejection:** rubric 0–5 × 21 criteria; hard failure ineligible; `selected_workflow_id: hybrid`.
- **repair:** 4 targeted edits on benchmark.
- **lettering/SFX/UI:** SVG overlays; diagnostics (collision, density, grayscale, noise, safe-zone, UI).
- **build/reader:** `docs/reimaginings/ember-lattice/premium-rd/` + `benchmark-suite/` copy.
- **validation:** `python -m reimaginings.ember_lattice.premium_rd` author/validate/build/audit; unittest.
- **panel/chapter/output counts:** 24 benchmark panels × 3 raster workflows + SVG hybrid; 75 benchmark rasters.
- **generated-vs-tracked:** SVG/HTML tracked; PNG ignored.
- **known owner response:** null specific to the 24-slice (owner prompt of 2026-09-06 post-dates it but does not cite the slice).
- **strongest evidence paths:** `src/reimaginings/ember_lattice/premium_rd/README.md`; `production/reimaginings/ember-lattice/premium-rd/benchmark-manifest.json`; `docs/reimaginings/ember-lattice/premium-rd/index.html`.
- **visible strengths:** explicit baseline-vs-premium; diagnostics; fail-closed hybrid recommendation.
- **visible failures:** raw “too brittle at equipment contact, negative-space, and sequential geography” (**sourced fact**, ch01-manifest recommendation).
- **reproducibility/licensing:** SVG compositor reproducible; rasters not; $0.
- **what next inherited:** unique 52-panel CH01 uses the same hybrid architecture.
- **whether inheritance improved the page:** **hypothesis** — hybrid overlays can improve lettering/UI without changing pixels; art brittleness remains a raster problem.

### G17 — Unique 52-panel premium CH01

- **identifier:** `ember-lattice-unique-52-ch01`
- **story:** Ember Lattice CH01 expanded to 52 unique story panels (not 24 reused).
- **branch / commit / worktree:** `fb10c87f` 2026-09-04 21:37:08. Premium-rd worktree HEAD; editorial tree includes rasters + editorial extras.
- **date:** 2026-09-04.
- **status:** 52 panels with distinct art-file hashes (**sourced fact**, generation-session-timing note). Deliverable `premium_ch01`.
- **intended hypothesis:** unique per-panel generation (40–60 allowed; 52 chosen) plus clean-art repair beats repeating one baseline plate across many overlay slots (ch01-manifest maps some early hybrid panels to reused `bm001.png` baseline — the unique route exists to stop that).
- **source inputs:** 3 reference PNGs; Candidate B; generation spec 52 cases (`ch01-generation-spec.json`).
- **model/tool/generation route:** built-in ImageGen; `ch01_unique_generation_calls: 28`; `ch01_targeted_edit_calls: 2`; unique batch walls 493–971 s. **Measured result:** `ch01-unique/` 28 PNG + 2 `raw-failures/`. Remaining 52 hashes filled from benchmark openai-raw/targeted-edit reuse **plus** unique files — timing note says all 52 resolve to distinct hashes.
- **prompt architecture:** per-panel scene + reserved regions + clean-art instruction + “No words, letters…” (`ch01-generation-spec.json`).
- **character identity method:** reference sheets + subject contracts.
- **environment/spatial-continuity method:** negative-space regions per panel; 5 scenes s01–s05 in SVG filenames.
- **panel-planning method:** 52 ComicPanelPlans in `ch01-comic-panel-plan.json` / manifest `panels=52`.
- **selection/rejection:** clean-art audit 52 audited / 12 failures / 12 repaired / 0 unresolved (`ch01-clean-art-audit.json`).
- **repair:** high-frequency classified failures; blend_strength recorded; 12 `editorial-clean/*.png` on editorial tree (p014, p019, p022, p025, p034, p036, p039, p041, p042, p044, p045, p046).
- **lettering/SFX/UI:** LetteringPlan/2.0 (`editorial_schema` in manifest project block).
- **build/reader:** premium-rd readers (phone/full/compact/action) now bound to 52-panel hybrid SVGs `production/…/assets/ch01-hybrid/p001.svg`–`p052.svg`.
- **validation:** premium_rd audit; integrity JSON.
- **panel/chapter/output counts:** 52 panels; 30 unique-folder rasters + 12 editorial-clean + benchmark reuse.
- **generated-vs-tracked:** 52 hybrid SVG tracked; rasters ignored.
- **known owner response:** null after this commit besides the later total-review prompt.
- **strongest evidence paths:** `production/reimaginings/ember-lattice/premium-rd/ch01-manifest.json` (recommendation + 52 panels); `generation-session-timing.json`; `ch01-clean-art-audit.json`; `C:\AgentWorkspaces\anime-pipeline-ember-lattice-editorial-gear-20260904\experiments\reimaginings\ember-lattice\premium-rd\ch01-unique\`.
- **visible strengths:** unique hashes; classified clean-art repair; 52-panel chapter matches Garden's Anchor *scale* without importing Dio/Thal.
- **visible failures:** 12/52 needed noise/texture repair; provider seed still null so pixel regen is unavailable (**sourced fact**, remaining_gaps).
- **reproducibility/licensing:** same.
- **what next inherited:** editorial pass consumes the 12 repaired plates and adds gear/cast bibles.
- **whether inheritance improved the page:** **hypothesis** — unique plates should reduce “same splash reused” vs 24-panel overlay; not scored here.

### G18 — Editorial / lettering / clean-art / gear / faction / future-cast pass

- **identifier:** `ember-lattice-editorial-gear-pass`
- **story:** same premium CH01 + future-facing item/cast bibles.
- **branch / commit / worktree:** `99cb5e9e` 2026-09-04 23:30:36. `C:\AgentWorkspaces\anime-pipeline-ember-lattice-editorial-gear-20260904`. **This isolated review is branched from that commit.**
- **date:** 2026-09-04.
- **status:** complete on isolated branch; owner review of editorial pass **null** (no new owner-approval JSON).
- **intended hypothesis:** cleaner art, rewritten lettering, visible gear upgrades, faction families, and future-cast sheets make the hybrid page read more like a serial bible + chapter, not a one-off generate.
- **source inputs:** G17 rasters; `src/reimaginings/ember_lattice/premium_rd/editorial_data.py` (LOADOUTS, FACTION_FAMILIES, FUTURE_CAST_ROWS, CLEAN_ART_PANELS, ACQUISITION_SCHEDULE, BOSS_REWARD_FAMILIES).
- **model/tool/generation route:** mostly deterministic Python (`editorial.py`) on existing rasters; optional ImageGen only if already in cache. GPU observed in premium route-audit: RTX 5090 Laptop 24463 MiB (**sourced fact**, not necessarily used for this pass).
- **prompt architecture:** lettering_units() / protected focal zones in editorial.py; not new full-chapter prompts.
- **character identity method:** future-cast SVG `production/…/concepts/characters/future-01.svg`–`future-12.svg`.
- **environment/spatial-continuity method:** gear families `concepts/gear/family-01.svg`–`family-06.svg`; `gear-item-bible.json`; `future-cast-bible.json`.
- **panel-planning method:** still 52 CH01 plans; LetteringPlan/2.0.
- **selection/rejection:** clean-art 12/12 repaired; unresolved 0.
- **repair:** editorial-clean rasters (12 PNG, ~2.2–2.5 MB each).
- **lettering/SFX/UI:** editorial rewrite of SVG overlays; diagnostics regenerated.
- **build/reader:** `docs/reimaginings/ember-lattice/premium-rd/{gear,future-cast,failures,evidence}/index.html` and benchmark-suite copies.
- **validation:** `production/reimaginings/ember-lattice/premium-rd/integrity/editorial-protected-state-*.json`; `src/reimaginings/ember_lattice/premium_rd/tests/test_premium_rd.py`.
- **panel/chapter/output counts:** 52 CH01 + 12 future-cast SVG + 6 gear SVG; editorial rasters 12; HTML gear/future-cast pages 2 (+ suite copies).
- **generated-vs-tracked:** SVG/JSON/HTML tracked; editorial-clean PNG ignored.
- **known owner response:** none dated after 23:30 on 2026-09-04 except the 2026-09-06 total-review prompt, which still states the ToG/SL gap.
- **strongest evidence paths:** `src/reimaginings/ember_lattice/premium_rd/editorial.py`; `production/reimaginings/ember-lattice/premium-rd/ch01-lettering-plan.json`; `gear-item-bible.json`; `future-cast-bible.json`; `docs/reimaginings/ember-lattice/premium-rd/gear/index.html`.
- **visible strengths:** item/cast continuity artifacts; lettering plan version bump; protected-state snapshots.
- **visible failures:** still no owner acceptance; still no commercial clearance; still non-reproducible rasters.
- **reproducibility/licensing:** deterministic overlays yes; rasters no; Arial requested in SVG (`build_volume.py`) with later note to replace after license approval (`premium-rd/research-and-citations.md`).
- **what next inherited:** this review branch (inventory only).
- **whether inheritance improved the page:** **hypothesis** — gear/cast bibles improve *serial infrastructure*; page pixels change only on 12 cleaned panels plus lettering SVG. Owner 2026-09-06 quote implies the remaining gap is still visible.

---

## 9. Supporting infrastructure (not a story generation, but required)

| System | Path | Role | Counts |
|---|---|---|---|
| Hard assertions / gauntlet | `research/authoritative/v2.1.1/`; `production/comic/hard-assertion-manifests/` | frozen semantics | 40 renderer cases described in GAP_ANALYSIS |
| RenderRecords | `experiments/records/` (local); Ember `volume/render-records.json`; City `production/…/render-records/`; Borrowed chapter records | provenance | City 80 production JSON files under render-records/; Ember volume JSON list |
| System ledgers | Ember `system-state-ledger.json`; NG `comic_run_ledger.py`; bakeoff budget | numeric / reservation state | Ember volume-validation system_state PASS |
| Continuity tools | `compile_ch05_cross_panel_semantic_gates.py`; Ember `author_system_state.py`; City `continuity-graph.json` | carry-forward flags | NG CH05 object chain; Ember 10 chapter states |
| Diagnostics HTML/PNG | listed in §4 | grayscale, density, collision, safe-zone | Ember 312+144 diagnostic SVG |
| HTML review surfaces | §4.1–4.2 | owner navigation | 110 HTML |
| Cost ledgers | `docs/research/production-time-cost-ledger.md`; G07 $1.057377; all reimaginings $0 | spend | **sourced fact** |
| License registry | `docs/research/model-license-registry.md` | commercial gates | Anima internal; LoRA sensitive; FLUX VAE NCL; NoobAI blocked |
| Record templates | `config/record-templates/` | RenderRecord v1/v2, incidents, timers | 11 JSON templates |

---

## 10. Inheritance vs page improvement (summary)

| From → To | What was inherited | Did the *page* improve? |
|---|---|---|
| Lion Cub → Garden | four-layer split | **hypothesis:** architecture improved; different story |
| Garden gen → baseline_legacy | exact graph | measurement only; 0 accepted |
| Garden plates → CH01 accepted | composite + occluder | **observation:** yes, only accepted sequence |
| Garden lettering → Ember SVG | lettering-as-code | **hypothesis:** SVG v2 is more serial-capable than baked ImageGen glyphs; owner still complained about balloons on the pilot |
| NG records → all reimaginings | ComicPanelPlan, ignore rasters, adult-only | auditability yes; pixels are new |
| CH05 house style → CH06–13 | refs + 5-panel strips | more chapters, same renderer family |
| CH05/CH06 strips → Borrowed Down | 5-cell sheets | **hypothesis:** Borrowed Down FINAL_AUDIT baked blanks — topology inheritance hurt lettering |
| Borrowed → City | isolation, records, localized lettering repair; **rejected** 3×2 | City topology pilot 94/100 vs sheets; owner still rejected the look later |
| City → Ember | negative lessons (busy, generic, HUD-less “progression”) | Ember adds numeric Ledger + Candidate B; owner approved **pilot style**, then 2026-09-06 still below ToG/SL |
| Ember volume → premium 24 → unique 52 → editorial | hybrid SVG, unique plates, clean-art, gear/cast | each step adds tools and some repaired pixels; **no owner acceptance after the Phase A JSON** |

**Recommendation (pointer only):** visual scoring belongs to Visual A/B; this inventory does not declare a winner.

---

## 11. Unknowns (`null`)

- Exact ImageGen backend snapshot, seed, and per-image provider milliseconds for CH03–CH13 and all reimaginings.
- Timed owner minutes for G07 (required 20, completed 0) and for every reimagining volume.
- Commercial license of Anima aesthetic v1.1 and adult LoRA consent packets.
- Whether garden `datasets/soren|sigrid` contain photo likeness (not opened).
- Lion Cub generation counts inside zip archives.
- Owner utterance specifically naming *The City Keeps Oaths* or *Borrowed Down* titles (the LitRPG prompt refers to “earlier attempts” without those titles in the quoted sentence; worktree names in the same prompt file do identify the experiments).
- Whether CH06–CH13 default-house rasters were ever seen by the owner.
- Electricity / GPU depreciation (explicitly unmeasured in experiment-log).

---

## 12. File index the lead should open first (no extra tree walk required)

1. This file and `archivist-inventory.json`
2. `docs/research/anime-pipeline-total-review/evidence/coordination.md`
3. `docs/research/experiment-log.md` + `docs/research/benchmark-history.md` + `docs/research/model-license-registry.md`
4. `production/decisions/ng-decision-owner-visual-direction-r2.json` + `production/reimaginings/ember-lattice/owner-approval.json`
5. `C:\AgentWorkspaces\anime-pipeline\FRESH_SESSION_TOTAL_ANIME_PIPELINE_INDUSTRY_REVIEW_PROMPT.txt` L38–40 and `FRESH_SESSION_LITRPG_MANHWA_PRODUCTION_PROMPT.txt` L5–120
6. Raster roots listed in coordination.md (inspect only)
7. Generation code: `garden/gen3.py`, `garden/stage.py`, `garden-work/northgarden/strip/kit.py`, `src/north_garden/baseline_legacy.py`, `src/reimaginings/borrowed_down/pipeline.py`, `src/reimaginings/the_city_keeps_oaths/pipeline.py`, `src/reimaginings/ember_lattice/build_volume.py`, `src/reimaginings/ember_lattice/premium_rd/`
