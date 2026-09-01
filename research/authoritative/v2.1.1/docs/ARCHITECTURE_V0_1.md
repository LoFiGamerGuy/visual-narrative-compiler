# ARCHITECTURE_V0_1.md

> ⚠️ **v2.1 — 2026-08-31.** This document has been corrected after independent
> verification by the project owner. **Read `docs/CORRECTIONS_V2_1.md` first**; it is
> the authority wherever it conflicts with anything here. Corrections are marked inline
> with ⚠️ v2.1.
**North Garden Visual Narrative Compiler — v0.1**
2026-08-31. Status: proposed, partially evidence-backed, explicitly incomplete. Sections marked ⚠️ are the parts I believe are wrong or unproven.

---

## 0. The one-paragraph version

Canon, identity, geometry, shot intent, provenance and QA live in plain files outside every model. A **SceneRecord** holds what is true about a moment in the story and is shared across media. A **PanelSpec** or **ShotSpec** holds how one medium stages it. A **RenderRecord** holds one attempt to realise it and is disposable. Blender supplies camera, scale and occlusion — deliberately crudely. Models are asked for pixels and nothing else. Nothing that must survive a model change is stored inside a model, a prompt, or a workflow JSON.

---

## 1. Principles, and what each one costs

| # | Principle | Evidence | Honest cost |
|---|---|---|---|
| P1 | Canon lives outside models | Converged on independently by MangaFlow and StoryBlender `PREPRINT` | Authoring discipline; nothing is free-form any more |
| P2 | Geometry has one authority, and it is coarse | LooseControl `PEER_REVIEWED` — exact depth is a trap | 3D set build time; break-even at chapter 2–3 of reuse |
| P3 | Model outputs are candidates, never truth | Universal | Storage; a selection step that cannot be skipped |
| P4 | Everything addressable by stable ID | "Fix panel 34 without touching 33" | IDs are forever; renumbering is forbidden |
| P5 | Every output carries provenance | Reproducibility; ComfyUI issue #11833 makes this mandatory `OFFICIAL_REPO` | A few fields per render |
| P6 | Repair is first-class, and gated two-sided | GEditBench v2 under-editing trap `PREPRINT` | Two thresholds instead of one |
| P7 | Manual art tools are a stage, not a failure | Every professional-looking AI comic had hand finishing on ~10% | You must own a drawing tool and some skill |
| P8 | Declared state, not detected state | The **only** mechanism that distinguishes intentional change from drift | ~15 min authoring per chapter |
| P9 | Benchmark before belief | 40 render cases, semantically frozen | 120 renderer generations per finalist arm (Stage B); Stage A smoke is 24 |

---

## 2. Data model

Three records, and the boundaries between them are the whole design.

```
SceneRecord ──1:N── PanelSpec ──1:N── RenderRecord
     └────────1:N── ShotSpec  ──1:N── RenderRecord
```

### 2.1 SceneRecord — shared across comic and animation

```python
SceneRecord = {
  "id":          str,     # OPAQUE stable id (ULID/UUIDv7). NOT derived from chapter or order.
  "alias":       str,     # human handle, e.g. "ch01.kitchen-argument" - may be renamed freely
  "chapter":     str,
  "order":       int,     # ordering key ONLY. May be recalculated at will;
                          # stable ids make renumbering harmless. (v2.1: float-gap
                          # trick withdrawn as a long-term invariant.)
  "beat":        str,     # one sentence of what happens — human source of truth
  "dialogue":   [ {"speaker": str, "text": str, "voice_id": str|None,
                   "kind": "speech"|"thought"|"narration"|"sfx"} ],
  "location_id": str,     # -> Set asset (a .blend / .glb, later a USD stage)
  "cast":       [ {"character_id": str,          # -> identity assets
                   "wardrobe_state": str,        # "day0" | "post_integration" | ...
                   "placement": str} ],    # NAMED SEMANTIC MARK only, e.g. "at_table" | "in_doorway".
                          # v2.1: an explicit Transform is FORBIDDEN here - a world
                          # transform is a directing decision and belongs in
                          # SpatialStageSpec (comic) or AnimationShotPlan.
  "props_required":  [str],
  "props_forbidden": [str],
  "time_of_day": str|None,     # only if sets are parametrically lit — otherwise a lie
  "published_revision": str|None, # id of the immutable published revision, if any.
                          # v2.1: publication does NOT forbid re-rendering. A published
                          # revision is immutable and its bytes stay addressable forever;
                          # any new render or repair creates a NEW revision, and an
                          # edition manifest selects which revision is current. This
                          # preserves reproducibility while still allowing typo fixes,
                          # legal corrections, remasters and platform-specific exports.
}
```

`props_required` / `props_forbidden` / `wardrobe_state` **are the declared-state manifest** (P8). They are not documentation. They are the assertion targets for QA, and they are what turns "is this a continuity error?" — which VLMs answer at ~45% accuracy — into "is the coat present: yes/no?", which they answer well.

### 2.2 PanelSpec — comic only

```python
PanelSpec = {
  "id": str, "scene_id": str, "order": float,
  "aspect": str,               # locked by the page grid, not chosen per panel
  "panel_slot": str,           # position in the grid
  "camera": {"mode":"named"|"explicit", "named":str|None,
             "position":[f,f,f]|None, "target":[f,f,f]|None,
             "focal_mm":float|None},
  "staging_notes": str,        # the 2D cheat, which is legitimate here
  "balloons": [ {"line_idx":int, "anchor":[f,f], "tail_to":[f,f]} ],
  "status": "draft"|"staged"|"rendered"|"approved"|"locked",
}
```

### 2.3 ShotSpec — animation only ⚠️

```python
ShotSpec = {
  "id": str, "scene_id": str, "order": float,
  "camera": {...},             # same union as PanelSpec — this is the shared half
  "duration_frames": int,      # DOES NOT EXIST IN THE COMIC. Authored fresh.
  "motion": str|None,          # "push_in" | "hold" | "whip_pan"
  "keyframes": [ {"frame":int, "pose_ref":str|None, "art":str|None} ],
}
```

⚠️ **This record is speculative.** It holds the shape of the boundary; it is not designed. Do not build against it yet.

**v2.1 — the earlier reuse percentages are withdrawn.** They were intuition presented with unearned confidence and are **not measured project data**. The qualitative claim stands: canon, assets, sets, designs, wardrobe, props and story beats transfer; directing decisions do not.

### 2.4 RenderRecord — one attempt, disposable

```python
RenderRecord = {
  "id": str, "spec_id": str, "created_at": str,
  "adapter": str,                 # "comfy_http"
  "adapter_version": str,         # ComfyUI COMMIT HASH — mandatory, see below
  "workflow_hash": str,           # sha256 of the API-format workflow JSON
  "inputs": dict,                 # prompt, seed, cfg, steps, lora refs+weights,
                                  # control maps as content hashes
  "environment_fingerprint": {    # v2.1: commit + workflow hash are necessary, NOT sufficient
     "comfyui_commit": str, "custom_node_commits": dict,
     "base_model_hash": str, "vae_hash": str, "text_encoder_hashes": list,
     "lora_hashes": list, "control_model_hashes": list,
     "sampler_impl": str, "scheduler_impl": str,
     "python": str, "torch": str, "cuda": str, "accel_quant_pkgs": dict,
     "gpu_class": str,            # determinism can differ across devices
     "input_asset_hashes": list,
     "prompt_compiler_version": str, "benchmark_adapter_version": str },
  "artifact_hash": str,           # sha256 of output bytes -> CAS path
  "colorspace": str,              # "sRGB" | "ACEScg"  (the whole of OCIO adoption)
  "chosen": bool,
  "qa": dict|None,
}
```

**`adapter_version` is not hygiene, it is load-bearing.** ComfyUI has no public interface contract by its maintainers' own admission, and issue #11833 (open since 2026-01-13) shows that adding a defaulted input to a node breaks previously-working API workflows. **A saved workflow JSON is a snapshot valid against one commit.** Without the hash, renders are not reproducible and the adapter boundary is decorative.

### The membership test
> Would this field still mean something if the entire renderer were swapped?

If no, it belongs in `RenderRecord.inputs`. `prompt`, `seed`, `cfg`, `lora_weights` all fail the test. This is what makes model-agnosticism real rather than aspirational.

---

## 3. Storage

- **Source of truth: JSON on disk, in git.** Free diffs, free history, human-readable review — which matters enormously when the versioned thing is a creative decision.
- **SQLite is a derived index**, rebuildable from the JSON at any time by a `reindex()` function. Gives you "all panels where Sigrid appears in the kitchen at dusk with status != approved". A corrupted index is never an emergency. SQLite's own guidance puts a single-writer, sub-terabyte, device-local workload squarely in its territory `OFFICIAL_DOCS`.
- **Binaries: content-addressed plain filesystem.** `renders/<sha[:2]>/<sha>.png`. Renders are immutable once written — the ideal CAS case. ⚠️ v2.1: a render is **not** a pure function of its inputs. GPU kernels, backend versions and non-deterministic reductions mean byte-identical reproduction on arbitrary hardware is not guaranteed. **The target is traceable reproduction** — enough recorded state to explain any difference — not a false promise of bit-exactness. Free dedup, trivial rsync backup, and a hash that *proves* which bytes a record refers to. Cost: a `checkout_chapter(n)` helper that hardlinks hashes into readable names. Half a day.
- **Not adopted:** git-lfs (pointers pollute history forever), DVC (a second version-control mental model).

**Not adopted: Kitsu, AYON, ftrack, Flow.** All four coordinate *people*; you have one person and therefore no approval loop. The decisive evidence is a documented solo natural experiment — a Blender Artists thread where one artist stood up Kitsu successfully in Aug 2021, reported by Dec 2021 "I've just not been using it all that much," found the Blender addon hard-coded to Blender Studio's folder layout in Jan 2022, and had abandoned it by Sept 2022 `PRACTITIONER`. Note the failure shape: **the system worked; it went unused.** Assume you are not exempt. Trigger condition for revisiting: a second human joins. Steal one idea for free — AYON's **"Project Anatomy"**, a declarative project-level definition of folder structure and naming templates that everything derives from.

---

## 4. The renderer boundary

One interface, one method, one adapter:

```python
class RendererAdapter(Protocol):
    def render(self, spec: PanelSpec, scene: SceneRecord) -> RenderResult: ...
```

`ComfyHTTPAdapter` drives `/prompt` plus the WebSocket progress channel. **Do not write a second adapter now** — an interface with one implementation is a guess about the second, and it will be shaped by ComfyUI's idiosyncrasies regardless. Write the second when a second renderer earns its place, and let the first bend to fit.

**Not adopted:** porting to diffusers (weeks of re-tuning sampler/scheduler/weighting differences against no documented quality gain `OFFICIAL_REPO`); ComfyUI-to-Python-Extension for batch (its own README: no result caching across calls, i.e. model reload per panel).

---

## 5. The generation stack

Four stages. Stages 2 and 3 are the ones under test.

```
1. STAGE      Blender: camera, proxies, occluders  ->  depth (+ ONE secondary), per-character masks
2. BASE       ControlNet-conditioned panel, NO character LoRAs      [arm under test]
3. IDENTITY   per-region or sequential-inpaint pass, ONE LoRA active per region   [arm under test]
4. UNIFY      whole-panel low-denoise pass, style only, ~0.15-0.25
5. LETTER     strip/kit.py, unchanged
```

**Spatial mode is mandatory on every panel** (v2.1). `SpatialStageSpec.mode` ∈ `grounded` | `cheated` | `2d_only`.

- `grounded` — the render should substantially respect canonical 3D.
- `cheated` — start from canonical 3D and **intentionally violate it** for composition or readability. **Record the cheat.**
- `2d_only` — 3D adds nothing here.

This exists to prevent a specific future failure: **a sufficiently good QA system will begin rejecting good comic art.** Impossible eyelines, exaggerated foreshortening, a wall quietly moved so two figures fit, a hand enlarged for readability — all correct direction, all geometry violations. QA reads the mode and does not score geometry against `cheated` or `2d_only` panels.

**Stage 1 is deliberately crude.** Boxy proxies, boxy sets. LooseControl's finding is cost-*reducing*: a beautifully modelled set is worse conditioning than a blocky one. And **do not stack controls** — one primary plus at most one secondary; multi-ControlNet composition is documented to cause severe artifacts `PREPRINT`.

**Stage 3 is the bake-off.** Five arms, defined in `EXPERIMENT_BACKLOG.md`. The prior favourite (Impact Pack `RegionalSampler`) is demoted: ComfyUI has had **native masked LoRA via the hooks system since 2024-12-02** `OFFICIAL_DOCS`, which attaches the weight patch itself to a masked conditioning — the exact mechanism the earlier attempt lacked.

⚠️ **Unproven:** that any of these produce production-quality two-character panels. Best published multi-subject Face-Sim is 0.5284. Assume the answer is "adequate with a finisher pass," not "solved."

---

## 6. Animation boundary ⚠️

**Productionization deferred; research lane OPEN.** ⚠️ v2.1 — the previous VRAM-ceiling gate is **withdrawn**: it re-imposed a local-hardware ceiling the owner deliberately removed when cloud GPUs were authorised, and a calendar date is a guess wearing a gate's clothes.

**Rule:** defer animation *productionization* until the first instrumented static chapter ships. Do **not** defer animation *research* — run ~5–10% of effort here, on cloud 48/80 GB GPUs, aimed solely at upstream architectural questions: will these rigs, pose representations, keyframes, cameras and set assets still be usable later?

ToonComposer (ICLR 2026) needs ~57 GB for 61 frames at 480p — fine on rented hardware — and is **MIT for its released code, parameters and weights** (verified 2026-08-31 from the LICENSE file; third-party components retain their own terms). The field is also moving away from the needed interface — Wan Animate-2 and SCAIL-2 both removed explicit pose conditioning in favour of driving-video conditioning.

What to do meanwhile costs nothing and compounds: keep `voice_id` populated per dialogue line, keep environments 3D-only, keep identity assets locked. Those are the layers that genuinely transfer.

---

## 7. QA architecture — inverted from the obvious design

**Deterministic CV detects. The VLM only confirms, on the top-K.** This inverts the Audit & Repair architecture, and the inversion is the point: VLMs score 45–48% against a 89.75% human baseline on **open-ended** inter-state difference detection `PREPRINT`. Note this does **not** automatically transfer to narrow closed-form assertion checks, which are a different task and must be benchmarked separately.

| Gate | What | ML? | Expected flags / 70 panels |
|---|---|---|---|
| 0 | **Script-side continuity check, before any pixels** | LLM | 1–3 |
| 1 | Lint: balloon geometry, count vs script, reading order, slice boundaries, duplicate panels | none | 0–3, all real |
| 2 | Drift: luminance, palette EMD, set-crop SSIM/LPIPS, character count, prop presence, identity embedding | some | 12–23 |
| 3 | **Narrow closed-form VLM assertion checks** against the manifest, top-15 only, one binary question per call, enum outputs, `cannot_determine` first-class. **Optional and non-gating** | yes | reduces to ~8–10 |
| 4 | Human review in FiftyOne (Apache-2.0, local, embeddings panel) | — | ~10 seen, ~15 min |
| 5 | Repair, **two-sided gate**, max 2 iterations | yes | — |

**Gate 0 is the highest-value check in the system and was not in the original plan.** ConStory-Checker reports precision 0.884 / recall 0.550 against human experts at 0.891 / 0.171 — a 3.2× error-discovery rate `PREPRINT`. It is text-only, cheap, and it *prevents* errors rather than detecting them.

**Gates 1–4 contain almost no machine learning.** That is the finding that most directly contradicts the "build a VLM drift auditor" instinct.

⚠️ **v2.1 correction — treating the VLM as the final, minimal component was too strong a framing.** The VLM should be **optional and non-gating**, but **benchmarked earlier** on *narrow closed-form* assertion checks. Those are a different task from open-ended difference detection, and the poor benchmark numbers do not automatically transfer — that was an inference I made without evidence. **The VLM is a sensor, not the judge**; it never approves or rejects production output until this project's own benchmark justifies it. Every VLM experiment must include **no-change controls** and report **recall AND false-alarm rate** as a pair.

**Identity embedding — licence-critical.** Use AuraFace or DINOv3 crops. **Not InsightFace**: its pretrained weights are non-commercial-research-only and are pulled *silently* by many face-consistency nodes. Do not apply photographic ArcFace thresholds to illustrated faces.

---

## 8. What this architecture does not solve

- **The renderer is still the bottleneck.** MangaFlow, with a full agentic decomposition, still reports "character rendering failures persist" and that quality "depends on the underlying image generation backbone." No IR fixes a backbone that cannot draw your leads.
- **Taste is not in the schema.** What separates professional-looking from generated-looking is locked layout, aggressive style constraint, deliberate under-rendering of 80% of panels, and hand finishing on the 10% that matter. Three of those four are judgment and one is a grid.
- **The abandonment risk is the real risk.** Infrastructure that works but goes unused is the modal outcome for solo pipeline projects. **Mitigation: every cycle must ship pages.** If a cycle produces only tooling, the cycle failed.
- ⚠️ **No verified precedent.** I could not find a single solo creator who shipped a substantial AI-assisted comic on an IR-first pipeline. The positive case rests on academic systems evaluated on benchmarks, not on shipping 40 chapters. Weight accordingly.
