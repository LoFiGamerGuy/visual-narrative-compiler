# CANDIDATE_REGISTRY.md

> ⚠️ **v2.1 — 2026-08-31.** This document has been corrected after independent
> verification by the project owner. **Read `docs/CORRECTIONS_V2_1.md` first**; it is
> the authority wherever it conflicts with anything here. Corrections are marked inline
> with ⚠️ v2.1.
Every candidate with: licence · commercial use · data treatment · API/automation · hardware · maintenance (with dates) · role.
2026-08-31. 🟢 adopt / 🟡 conditional / 🔴 blocked / ⬜ watch. Machine-readable: `candidates.json`.

## A. Base image models

| Candidate | Version / date | Licence | Commercial | Data | API | Hardware | Maintained | Role |
|---|---|---|---|---|---|---|---|---|
| 🟢 **Qwen-Image-Edit-2511** | 20B, Nov–Dec 2025 (sources conflict) | **Apache 2.0** | **Yes, unrestricted** | Self-host, none | ComfyUI native | 24GB w/ fp8 or GGUF; exact VRAM undocumented | Active | **Strongest single candidate.** Vendor claims two-person fusion; supports LoRA; primary repair engine |
| 🟢 **Illustrious-XL v2.0** | relicensed 2025-04-21 | **CreativeML Open RAIL (SDXL)** | Yes, w/ Attachment A downstream | Local | ComfyUI | 24GB comfortable | Onoma AI active | Current base. SDXL family ⇒ mature ControlNet + Impact Pack work |
| 🟢 **FLUX.2 [klein] 4B** | 2025-11-25 | **Apache 2.0** | **Yes, model + outputs + LoRAs** | Local | ComfyUI | ~13GB | BFL active | Cheap-iteration arm; the clean escape from FLUX licensing |
| 🔴 **FLUX.2 [klein] 9B** | 2025-11-25 | **Ambiguous** | **Unresolved** | — | — | — | Issue #32 open since 2026-01-21, no BFL response | **Treat as non-permissive until BFL answers** |
| 🟡 **FLUX.2 [dev]** | 32B | FLUX Non-Commercial v2.1 | **Model: no. Outputs: yes** | Local | — | 24GB w/ aggressive quant, slow | Active | Outputs are commercially usable; **LoRA must stay private/undistributed**. ⚠️ Verbatim "Non-Commercial Purpose" definition is gated (401) — **read before monetizing** |
| 🔴 **NoobAI-XL** | — | **Explicit commercial prohibition on the model card**, covering model, derivative models and model-generated products | **No** | — | — | — | — | **`BLOCKED_FROM_COMMERCIAL_PIPELINE`.** v2.1: the model card's plain text is the primary reason; the FAIPL training-is-modification share-alike argument is secondary. Do not train production LoRAs from these |
| 🟡 **Anima v1.1** | 2026-05-15, 2B | CircleStone NC | Model no; **selling generated images explicitly permitted** | Local | ComfyUI | Light | — | Retired from this project (0.6B encoder), but outputs already made are fine |
| 🟡 **Cosmos-Predict2** | NVIDIA OML | Commercially usable | Yes | Local | — | — | NVIDIA | Two live conditions: **no guardrail circumvention** (auto-terminates licence) and **"Built on NVIDIA Cosmos" attribution reaching your about page** |

## B. Multi-subject identity methods

| Candidate | Date | Licence | Commercial | Multi-ID? | Role-binding? | Hardware | Role |
|---|---|---|---|---|---|---|---|
| 🟢 **ComfyUI native LoRA hooks** | **2024-12-02** | GPL-3.0 (core) | Yes | Yes | Via masks | Base + N LoRAs; slower than single patch | **Test first.** Attaches the weight patch to masked conditioning — the mechanism `ConditioningSetMask` lacked |
| 🟡 **Impact Pack RegionalSampler** | v8.28, 2025-11-18 | GPL-3.0 | Yes | Yes, per-region LoRA | Via masks + ControlNet | SDXL-class | Viable **on Illustrious only**. Docs concede harmony loss; no evidence of Qwen/FLUX.2 support |
| 🟢 **Sequential inpaint (Impact Detailers)** | — | GPL-3.0 | Yes | Yes, serially | By construction | Modest | **Identity finisher.** Per-node model input ⇒ two Detailers, one LoRA each. Feathering + crop-factor solve lighting integration |
| 🟡 **Nano Banana Pro** | 2025-11-20 | Proprietary API | Yes | Claims **5 people** | Named slots, practitioner-documented confusion | API | Staging arm. **Paid tier only** — free tier trains + human review |
| 🔴 **XVerse** | NeurIPS 2025 | Apache code / FLUX-dev + InsightFace weights | **No** | 2–3 | Modulation, not spatial | 24GB (2 refs) | Blocked by weight licensing |
| 🔴 **WithAnyone** | ICLR 2026 | FLUX.1[dev] NC v1.1.1 | **No** | Yes | **Explicit face bboxes — best UX found** | — | Blocked. **Steal the bbox-conditioning idea** |
| ⬜ **MultiCrafter** | CVPR 2026 | Unknown | Unknown | 2 validated | **Yes — trained positional supervision** | — | Best published multi-human Face-Sim **0.5284**. Watch for code release |
| 🔴 **DiffSensei** | last news 2025-02-05 | Unstated | Unclear | Manga-specific | Unclear | 24GB | Stale, SDXL-era, licence unclear. Deprioritize |
| 🔴 **StoryDiffusion** | NeurIPS 2024 | Apache 2.0 | Yes | **No — single character across frames** | No | — | Wrong problem |

## C. 3D / spatial

| Candidate | Version / date | Licence | Commercial | Hardware | Maintained | Role |
|---|---|---|---|---|---|---|
| 🟢 **Blender** | **5.2 LTS, 2026-07-14** (5.2.1, 2026-08-25); LTS to Jul 2028 | GPLv2+ | Yes | — | Active | Spatial truth: camera, scale, occlusion, blocking |
| 🟢 **bpy (headless)** | 5.2.1 on PyPI, 2026-08-25, **Python 3.13 only** | GPLv2+ | Yes | — | Active | Scripted staging |
| 🟡 **toyxyz character-bones rig** | v101, Gumroad, $0 PWYW, needs Blender 3.5+ | **No licence text published anywhere** | **Unverified** | — | Bus factor 1, no issue tracker | Emits OpenPose+depth+normal+canny+**per-character seg masks** in one pass. **Use but do not redistribute; keep a scripted fallback** |
| 🟢 **RealityScan 2.0** | 2025-06-17 | Free below Epic revenue threshold | Yes | — | Epic | Photogrammetry for 5–10 hero objects only |
| 🔴 **3DGS as set geometry** | — | — | — | — | — | **Retired.** No occlusion boundary; photogrammetry beats it on metric accuracy `PEER_REVIEWED` |
| 🟡 **KIRI 3DGS Render for Blender** | v5.0.0, 2026-06-05 | **Apache 2.0** | Yes | — | Active | The one splat tool with a clean licence. Tracing reference only |
| 🟡 **World Labs Marble** | launched 2025-11-12 | Proprietary | **Pro $35/mo minimum** — free & Standard have **no commercial rights** | — | Active | Look-dev / establishing only. ⚠️ **Claims a training licence on your uploads** (irrevocable free, revocable+opt-out paid). **Never upload photos containing the child** |
| 🟡 **TRELLIS.2-4B** | arXiv 2512.14692 | **MIT** | Yes | **≥24GB — no headroom** | Microsoft | Props only, never leads or sets |
| 🟡 **Hunyuan3D / HY-World** | HY-World 2.1, Jul 2026 | Tencent Community | Yes in US; **excludes EU/UK/South Korea** | — | Active | Props / look-dev. Territory exclusion bars EU distribution partners |
| 🟡 **Meshy** | — | Proprietary | **Free tier = CC BY 4.0 (attribution)**; paid = you own | API on paid | Hosted | Props. States no training without consent (vendor claim) |
| 🟡 **Tripo** | Pro $20/mo | Proprietary | **Paid only** — free is public/non-commercial | Yes | Hosted | Props |
| 🟡 **Character Creator 5** | 2025-08-27; $299 perpetual | Reallusion | **Standard License covers comic/film output royalty-free** | — | Active | **Defer to the animation transition** |
| 🔴 **Reallusion Headshot 3** | 2026-04-27 | — | — | Cloud (Nano Banana) | — | **FORBIDDEN — explicitly a digital-double / likeness pipeline** |

## D. QA / repair / review

| Candidate | Version / date | Licence | Commercial | Role |
|---|---|---|---|---|
| 🟢 **FiftyOne** | v1.15.0 docs, Python 3.10–3.14 | **Apache 2.0** | Yes | **Adopt, don't build.** Local; tagging; embeddings panel shows drift as a visible smear |
| 🟢 **DINOv2** | — | **Apache 2.0** | Yes | Structural identity embedding. Safer default than v3 |
| 🟡 **DINOv3** | 2025-08-19 | Bespoke "DINOv3 License" | Yes, w/ conditions | Better embeddings; **read LICENSE.md before shipping** |
| 🟢 **AuraFace** | 2024-08-26 | Commercial-safe by design | Yes | **Face embedding replacement for InsightFace.** Lower accuracy (CFP-FP 95.18 vs 98.87) |
| 🔴 **InsightFace-distributed weight files** — `antelopev2`, `buffalo_l`, `inswapper`, InspireFace packs, **and InsightFace's own detector checkpoints** | repo update 2025-11-24 | Code MIT; **these weight files are non-commercial research only** | **No** | 🔴 **SILENT CONTAMINANT.** Auto-pulled by InstantID, IP-Adapter-FaceID, ReActor, most face-consistency nodes. ⚠️ v2.1: the restriction attaches to **the exact file and hash**, never to an architecture family — an independently trained checkpoint of the same architecture from another source is a separate licence question. **Action: inventory and quarantine, do not delete** |
| 🟢 **SAM 2** | — | **Apache 2.0** | Yes | Segmentation. **Pin it** |
| 🔴 **SAM 3** | LICENSE 2025-11-19 | Bespoke "SAM License" | Conditions | **Licence regression.** Do not auto-upgrade |
| 🟢 **GroundingDINO** | — | Apache 2.0 | Yes | Open-vocab prop/character detection |
| 🟢 **ViStoryBench** | CVPR 2026; code 2025-08-19 | **Code Apache 2.0 / data MIT** | Yes | Metric implementations to reuse. Ensembles 3 face models + CLIP — take the design |
| 🔴 **Audit & Repair** | arXiv 2506.18900, Jun 2025 | — | — | **Code never released** ("coming soon", ~14 mo). Architectural reference only |
| 🟡 **manga-image-translator / BallonsTranslator** | GPL-3.0 | GPL-3.0 | **Copyleft** | **Harvest ideas or run as a separate process — do not link.** Useful for *read-back QA* of your own pages |
| 🔴 **Magi** | v3 Mar 2025 | **Academic research only** | **No** | Excluded, though it is the ideal comic-CV stack |

## E. Animation ⬜ — **research lane open, productionization deferred** (v2.1)

*Corrected: the the local card gate is withdrawn — it re-imposed a local-hardware constraint the owner deliberately removed. Cloud 48/80GB GPUs are authorised. ~5–10% of research effort runs here to answer upstream architectural questions only.*

| Candidate | Version / date | Licence | Hardware | Note |
|---|---|---|---|---|
| ⬜ **ToonComposer** | ICLR 2026; weights 2025-08-15 | ✅ **MIT — verified 2026-08-31 from the LICENSE file.** Third-party components (e.g. Wan2.1, Apache-2.0) retain their own terms | ~57 GB for 61 frames @480p — cloud 80 GB class | Exactly the right tool for sparse-keyframe research. **Cloud is authorised, so VRAM is not a strategic gate** |
| ⬜ **Wan 2.2 Animate-14B** | 2025-09-19 | **Apache 2.0** | 14–16GB fp8+offload; 8–10GB GGUF | Needs a **driving video**. Never drive from child footage |
| ⬜ **Wan2.2-Animate-2-14B** | 2026-08-07 | Apache 2.0 | **8× A800 documented** | Removed pose conditioning — field moving away from our interface |
| ⬜ **SCAIL-2-14B** | arXiv 2606.10804 | Apache 2.0 | Undocumented | Accepts Blender-rendered mesh as driver — relevant |
| ⬜ **LTX-2.5** | 2026-08-11 | Free commercial <$10M ARR | 16 GB min | Lightest local option. Licence claim officially unverified |
| 🟢 **Cascadeur** | 2026.2, 2026-08-06 | Indie **$96/yr**, perpetual after 1yr | — | Best value in this report. Quadruped-aware; **MCP server for LLM control** |
| 🔴 **Sora API** | — | — | — | **Removed 2026-09-24.** Do not build on it |
| 🔴 **Kling** | ToS 2026-04-21 | Proprietary | — | **§4.6 forbids commercial use of outputs without written permission** |
| 🟡 **Luma** | — | Proprietary | — | **Free/Lite output is permanently non-commercial and permanently watermarked.** Never prototype on free |
| 🟢 **Kokoro-82M** | — | **Apache 2.0** | CPU, faster than realtime | **Cannot clone by design — the safety feature.** Recommended default for the child voice |
| 🔴 **XTTS v2** | — | CPML **non-commercial** | — | Coqui closed Jan 2024. Unmaintained + unusable |

## F. Standards & infrastructure

| Candidate | Version / date | Verdict |
|---|---|---|
| 🟢 **SQLite** | — | Derived index. Single-writer, sub-TB, device-local is squarely its territory |
| 🟢 **Content-addressed filesystem** | — | Immutable renders are the ideal CAS case |
| 🟡 **OpenColorIO** | 2.5.0; CY2026 platform | **Adopt the discipline, not the library.** One field: `colorspace` |
| ⬜ **OpenUSD** | **v26.03, 2026-03-26**; Core Spec 1.0 | **Later.** Design toward it — stable object/camera names in .blend so export is mechanical. Sparse array-edit overrides make "revise ch3's set without touching ch1" cheap |
| ⬜ **OpenTimelineIO** | v0.18.1, 2025-11-09; **0.19 unreleased ~21 months** | Adopt when you cut video. Pre-1.0 after nine years — flagged |
| 🔴 **MaterialX** | 1.39.5, 2026-05-22 | **Never for this project.** One renderer; solves a problem you don't have |
| 🔴 **Kitsu / AYON / ftrack / Flow** | — | All coordinate people. Documented solo abandonment case. Steal AYON's "Project Anatomy" idea only |
| ⬜ **C2PA** | Spec **2.4, Apr 2026**; c2patool v0.26.67, 2026-06-11 | Record provenance in RenderRecord now; defer signing until asked |
