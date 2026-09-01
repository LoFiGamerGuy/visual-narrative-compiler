# POLICY_LICENSE_REGISTRY.md

> ⚠️ **v2.1 — 2026-08-31.** This document has been corrected after independent
> verification by the project owner. **Read `docs/CORRECTIONS_V2_1.md` first**; it is
> the authority wherever it conflicts with anything here. Corrections are marked inline
> with ⚠️ v2.1.
Re-audited from primary sources, 2026-08-30/31. **Read the two red boxes before spending anything.**

---

## 🔴 BOX 1 — Act this week

**Specific InsightFace-distributed pretrained weight packages are non-commercial-research-only.** Code is MIT; **those weight files are not**. ⚠️ The restriction attaches to the **exact file** (`buffalo_l`, `antelopev2`, inswapper, InspireFace) — **not** to the architectures *SCRFD* or *RetinaFace*, which may exist under other licences from other sources. `OFFICIAL_DOCS` As of a 2025-11-24 repo update, face-swap models, the **buffalo_l** pack and InspireFace require explicit licensing contact.

`antelopev2` and `buffalo_l` are **downloaded silently on first run** by InstantID, IP-Adapter-FaceID, ReActor, most ComfyUI "face consistency" nodes, and many identity-scoring scripts. The detector checkpoints InsightFace ships **for** SCRFD and RetinaFace carry these terms — the most commonly missed instance. Judge the file, never the model-family name.

```
ls ComfyUI/models/insightface/     # if antelopev2 or buffalo_l is here, something uses it
```
**Action: inventory and quarantine — do NOT delete.** Record path, sha256, source, licence state and dependent nodes; then have production render profiles *refuse* restricted weights. Deleting destroys the evidence needed to identify which prior metrics were computed with them, and a **commercial InsightFace licence remains a live option** if it materially outperforms alternatives. Substitute **AuraFace** (commercial-safe; CFP-FP 95.18 vs 98.87) or drop identity-embedding conditioning entirely in favour of LoRA consistency. The obvious YOLO-face alternative carries **AGPL** — a different trap.

## 🔴 BOX 2 — Never send likeness photos to these

| Destination | Why |
|---|---|
| **FLUX API** | API Service Terms: "The Company may use Inputs and Outputs to train and improve its artificial intelligence models." Consumer ToS has an email opt-out; **the API terms do not offer one on their face**, and the opt-out is prospective only. **Use local FLUX weights instead.** |
| **Gemini free tier** | "human reviewers may read, annotate, and process your API input and output," used to "provide, improve, and develop Google products." **Paid tier: "Google doesn't use your prompts… to improve our products."** Enforce paid-tier in config, not convention. |
| **RunPod Community Cloud / Vast.ai** | Third-party-hosted machines. If you cloud-train a likeness LoRA, use a first-party/Secure tier and delete the volume. |
| **Any hosted 3D generator or mocap** | Marble claims a training licence on uploads. Rokoko Vision uploads to cloud. |
| **Anything, if the image contains the child** | Absolute. |

---

## 1. Real-person likeness — vendor by vendor

**No vendor offers a consent-attestation mechanism for a private adult.** Every one puts the warranty on you in the terms, then enforces with a filter that has never seen your paperwork. **Terms and deployed filters diverge in both directions.**

| Vendor | Consenting adult permitted? | Trains on your uploads? | Watermark | Verdict |
|---|---|---|---|---|
| **Black Forest Labs** | Yes by implication — prohibits depicting a real person abusively "without their verified, documented, and informed consent" (Usage Policy, 2026-08-04) | **API: yes, by default.** Consumer: opt-out by email, prospective only | Bars *you* from removing AI markings | 🟡 **Local weights only** |
| **OpenAI** | Yes — prohibits likeness use "without their consent" (policies eff. 2025-10-29) | API not by default | — | 🟡 Terms permit; **deployed filter reportedly refuses real-person uploads** `COMMUNITY`. Only vendor with real consent plumbing (Sora cameos — identity-verified, revocable) but it is per-account, not a licensing tool |
| **Google** | No explicit carve-out; runs a likeness **complaint** flow (selfie + liveness, 18+) | **Free: yes + human review. Paid: no** | **Visible watermark optional since 2026-08-14**; SynthID + C2PA persist — do not strip | 🟡 **Paid tier only** |
| **Adobe Firefly** | **Terms silent on likeness entirely** (guidelines eff. 2026-05-15) | **"We don't train on any Creative Cloud subscribers' personal content"** | Content Credentials auto-applied | 🟡 Best data hygiene, worst capability — filter is the most restrictive of the majors on real faces |
| **Midjourney** | No explicit rule (ToS 2026-05-27) | **Not stated — assume it may** | — | 🟡 **Stealth (Pro/Mega) is mandatory** — assets are public by default |
| **Runway** | Prohibits use of a person's image "without their permission"; **explicitly bans characters based on the face or voice of anyone under 18** | Not stated | Not stated | 🟡 Usable; the under-18 ban independently vindicates our child rule |
| **Kling** | Warranty pushed to you, incl. "personality rights" | Yes (§4.7.3(f)), revocable by email | **Mandates Kling AI branding** (§4.5) | 🔴 **§4.6 forbids commercial use of outputs without written permission** |
| **Luma** | Not covered | **Free/Lite: yes, and trains AI models** | Free watermark **persists after upgrading** | 🔴 free / 🟢 paid. Rights vest permanently once earned |
| **ByteDance** | **Unverified** — "Copyright and Portrait Feature Usage Rules" is a separate doc I could not render | Unknown | — | 🔴 **Do not commit likeness work until that doc is read** |
| **Stability** | Not audited | Not audited | — | 🟢 Community Licence free commercially under **$1M revenue**; you own outputs; **fine-tunes explicitly are not "foundational models"** |

**Your only real protection is your own paperwork.** A signed, dated, revocable likeness release covering AI training, generation, derivative works, commercial publication and merchandising, listing the vendors her images touch — plus an inventory of the training set. It costs nothing and no vendor supplies a substitute.

---

## 2. Does a LoRA inherit the base restriction?

**Yes in every family here — but the restriction lands on the *artifact*, not on the *pictures*.**

| Base | LoRA status | Outputs | Practical rule |
|---|---|---|---|
| FLUX.1/2 [dev] | "Derivative" ⇒ **non-commercial** | **Commercial** | Keep the LoRA private. Never sell, publish for sale, or host it |
| **FAIPL 1.0-SD** (old Illustrious and other FAIPL bases) | "to modify" **includes training** ⇒ **must be released under FAIPL** | Commercial | 🔴 **Share-alike on your character LoRA.** Disqualifying for a proprietary bible |
| **NoobAI-XL** | n/a — excluded before the question arises | n/a | 🔴 **v2.1: the model card carries an explicit commercial prohibition** covering model, derivatives and model-generated products. `BLOCKED_FROM_COMMERCIAL_PIPELINE`. Simpler and stronger than the FAIPL argument |
| CreativeML Open RAIL (Illustrious v2.0) | Must carry Attachment A downstream | Commercial | 🟢 Fine |
| **Apache 2.0** (Qwen, FLUX.2 klein 4B) | **No inheritance problem** | Commercial | 🟢 **Train distributable LoRAs here** |
| NVIDIA OML (Cosmos) | Allowed | Commercial | Attribution "Built on NVIDIA Cosmos" reaches your about page; guardrail circumvention auto-terminates |
| Stability Community | Fine-tunes are not foundational models | You own them | Free under $1M revenue |
| Anima (CircleStone NC) | Non-commercial | **"Selling generated images" explicitly permitted** | Keep LoRAs internal |

⚠️ **Open item U9:** the verbatim definition of "Non-Commercial Purpose" in FLUX.2 [dev] is behind a gated repo (401). If it excludes *running the model in a revenue-generating business*, it could sweep in a monetized webcomic despite the Output clause. **Read it before monetizing.** BFL sells a Self-Hosted Commercial Licence (Builder tier, 10K images/mo, klein, includes LoRA rights) — prices sales-gated.

---

## 3. Publishing platforms

A widely-ranking 2026 blog contradicts primary sources on three of these. **It is wrong.**

| Platform | Policy | Status |
|---|---|---|
| **Patreon** | No AI-art rule. Deepfake rule targets harassment / non-consensual sexualization / deceptive impersonation — none apply | 🟢 **Best monetization surface** |
| **WEBTOON Canvas** | **Terms (2026-01-06) are silent on AI** — no mention, no disclosure requirement | 🟡 **Audience.** Silence is not safety; assume retroactive disclosure may be required |
| **Kickstarter** | Disclosure required (policy eff. 2023-08-29), including **consent for source works** | 🟢 Viable — and that consent question is answerable in your favour |
| **GlobalComix** | ⚠️ **CORRECTED v2.1.** Current AI policy (updated **2026-03-20**): fully AI-generated works are removed, but **AI used within a broader workflow involving human artistry is permitted and qualifying work CAN be monetized**, subject to disclosure and rights. GlobalComix retains discretion over what counts as sufficient human artistry | 🟡 **CONDITIONAL — seek written pre-clearance** with representative pages. This project sits near the boundary |
| **Tapas** | **"AI generated content is not allowed on Tapas"** — live guidelines; announcement 2023-01-23 | 🔴 **Closed** |
| **WEBTOON Originals** | Per-contract, non-public | ⚠️ Assume disclosure obligation and human-authorship reps. Legal review required |

**Market risk exceeds policy risk.** Readers cancelled subscriptions across RIDI/Manta/Kakao/LEZHIN over AI localization (2025-11) `COMMUNITY`. **Disclose proactively, early, in your own voice** — models used, what is human, that both depicted adults consented in writing, and that no child likeness model exists. That statement is an asset; extracted disclosure is a liability.

---

## 4. Compute economics — 70-panel chapter

Assumes roughly one thousand image generations per chapter (8–15 per keeper at two-likeness consistency; range 500–1,500).

| Path | Cost | Note |
|---|---|---|
| **Local electricity** | **~$0.25** | ~5.6 GPU-h × 0.22 kW × 18.44¢/kWh (EIA, May 2026). **A rounding error — anyone claiming local power is a real cost is wrong** |
| **Local depreciation** | **$5/chapter at heavy use → $55/chapter at 2 chapters/month** | 10× spread. **Local is cheap only if you use it a lot** |
| **Rented RTX 5090** | ~$5.50 raw, **$8–12 realistic** | RunPod $0.99/hr. You pay while art-directing, not just rendering |
| **Cloud LoRA training** | **$2–6 per run** | Best argument for renting: **train on an 80GB card, generate locally** |
| **Gemini 3.1 Flash Lite 1K** | **$34** | $0.0336/image |
| **Gemini 3 Pro (NB Pro) 1K/2K** | **$134** | $0.134/image |
| **Batch mode** | **≈ half** | Nothing here is interactive. Batch should be the default |
| **H100 / H200** | Bad value | Single-image diffusion doesn't scale with the interconnect you're paying for |

**Allocation:** likeness work → local, always (privacy decides, not cost). LoRA training → rented A100 on a first-party tier, deleted after. Backgrounds/props/no-likeness → hosted API, paid tier, batch.

**Do not buy hardware on cost grounds.** Buy it for privacy and iteration freedom — those justifications are strong; the cost one is not.

---

## 5. Measured production economics

**There are none.** I could not find a single named practitioner publishing measured hours-per-chapter or cost-per-page for an AI-assisted serialized webcomic. Search returns are almost entirely vendor content marketing, which I will not launder into figures.

What is credible: traditional illustration at **$50–200/page**, $5,000–30,000 for a graphic novel, 1–3 finished pages/day, 2–18 months. **The meaningful saving is the illustration line and the calendar — not compute, which is a rounding error against either.** Optimize the pipeline for *your hours*, not cost-per-image.

Best available estimate, offered as an estimate: **12–25 hours per chapter** once LoRAs and templates are stable — ~20% script/thumbs, ~35% generation and culling, ~30% compositing/cleanup, ~15% lettering/QC. **Generation is not the bottleneck; culling and cleanup are.**

**Instrument your own first three chapters.** Your numbers will be worth more than anything published, and this is the cheapest research in the entire programme.

---

## 6. Child-safety register — non-negotiable

**Forbidden, categorically:** any LoRA or likeness model trained on photos of a real child · any voice clone from a child's recording (XTTS v2, Chatterbox, ElevenLabs — all technically capable) · **Reallusion Headshot 3** (explicitly a digital-double pipeline) · Wan Animate / SCAIL-2 "Move" driven by home video of a child · any hosted mocap fed child footage · uploading any image containing the child to any hosted service.

**Safe and adequate:** build the child as an **original design, not a likeness** — generate until right, declare that the character, train on the *generated design*. No real-person referent then exists to protect. Voice: **Kokoro-82M** (Apache 2.0, 54 fixed voices, **cannot clone by design**) or a hired adult VA — the anime industry norm anyway, for continuity reasons.

**Note the architectural bonus:** a child proxy can be pure geometry — a scaled, non-photographic low-poly body emitting depth, pose and a segmentation mask, carrying no likeness, no photos, no trained model, no face. The face comes from the drawn style pass. This lets the character occupy space correctly with **no real-person likeness or biometric identity data anywhere in the pipeline** (a fictional character still has persistent *fictional* identity assets, which is fine and desirable) — and it is one of the strongest arguments for the 3D layer.

**External corroboration:** Runway's usage policy independently bans "characters based on the face or voice of a person under the age of 18"; Google's likeness flow is 18+ only. **The rule matches where the industry's hard lines actually are. Put it on the about page.**

---

## 7. Could not verify

FLUX.2 [dev] "Non-Commercial Purpose" verbatim definition (gated, 401) · BFL Self-Hosted licence prices (sales-gated) · FLUX image API per-image pricing (not rendered) · ByteDance Portrait Feature Usage Rules (index page only) · Midjourney training practices on uploads · Runway training practices and free-tier watermarking · Stability likeness policy; licence page shows **no date** · Adobe indemnification scope · OpenAI per-image cost (calculator-gated) and whether the filter tightening corresponds to any written policy change · WEBTOON Originals terms · CHI 2026 "AI in Webtoon Creation" (paywalled — **the single most relevant academic source; obtain it**) · individual OpenCLIP checkpoint licences.

---

## 8. ⚠️ v2.1 — registry granularity is mandatory

**One row per vendor is not actionable.** "FLUX trains on inputs" hides that BFL's general Website/Playground terms differ from Developer Terms and per-endpoint order forms.

Every row must carry:

`provider · product · plan_tier · endpoint · effective_date · source_url · training_default · opt_out · human_review · retention · likeness_consent_rules · commercial_output_rights · allowed_for_sensitive_adult_reference (yes/no/conditional) · reviewer_notes`

`allowed_for_sensitive_adult_reference` is the field the pipeline actually reads. Default **no**; flip to yes only after the exact provider+product+plan+endpoint has been reviewed and dated.

**Unchanged and clear:** Gemini unpaid services may use submitted content for product improvement and human reviewers may process it — **no adult photographic identity sources there.**

**Also v2.1:** "best platform" is a business recommendation, not a licence conclusion. **Do not make the production architecture depend on any single distribution platform.** The master must export cleanly to any storefront or an owned site.
