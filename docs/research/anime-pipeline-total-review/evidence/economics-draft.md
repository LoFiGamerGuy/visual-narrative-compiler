# Production economics, rights, and risk — evidence draft

Access date: 2026-09-06  
Role: Production Economics, Rights, and Risk Analyst  
Worktree: `C:\AgentWorkspaces\anime-pipeline-total-review-20260906-211925`  
This assignment direct paid/cloud spend: **$0** (no provider calls, uploads, model downloads, or cloud GPU).  
Industry draft `evidence/industry-research-draft.md` was not present at write time; staffing/cadence ranges below are independently cited.

This is an evidence compilation, not legal advice and not a chain-of-title opinion. Unavailable fields stay `null`. Estimates are labeled as estimates with assumptions. Direct paid spend is only recorded when a ledger proves it. Built-in ImageGen monetary cost is unavailable, not zero.

---

## 0. Method and non-inferences

Read in this worktree and, read-only, sibling ledgers/audits: production time/cost ledgers, `BUNDLE_PROVENANCE.json`, `.env.example` (not `.env`), license/budget ADRs, `GAP_ANALYSIS.md`, `GOAL.md`, `docs/research/model-license-registry.md`, reimagining audits with `provider=null`, G07 bakeoff ledger/policy, CH05 production budget policy, and official web sources for NoobAI, WEBTOON Canvas, Tapas, and OpenAI data-use. `C:\AgentWorkspaces\anime-pipeline\docs\REPOSITORY_REVIEW_2026-09-06.md` was read as a prior engineering review; numbers were checked against primary ledgers.

Do not infer:

- built-in product cost = $0 because paid API spend is $0;
- agent triage PASS = owner acceptance or commercial clearance;
- a model-family license from a filename;
- WEBTOON Originals terms from Canvas UGC silence;
- human minutes from generation seconds.

---

## 1. Direct paid spend (measured)

### 1.1 This assignment

**$0.** Coordination file and prompt require zero paid/cloud spend. No G07 budget reuse, no production cap, no uploads of protected art.

### 1.2 Historical paid API — G07 fictional bakeoff only

Primary ledger: `docs/research/evidence/g07-bakeoff-cost-ledger-r1.json` (updated 2026-09-01T15:39:15Z).

| Field | Value |
| --- | ---: |
| Approved aggregate cap | $100.000000 |
| Committed actual | **$1.057377** |
| Held reservations | $0.000000 |
| Available | $98.942623 |
| Maximum simultaneous reservation for a full 16-request run | $4.200000 |
| Production-accepted outputs | 0 |

Per-adapter committed actuals (from ledger entries):

| Adapter | Completed required candidates | Reconciliation method | Committed USD |
| --- | ---: | --- | ---: |
| OpenAI GPT Image 2 | 4/4 | documented token-rate estimate | 0.198621 |
| Gemini 3.1 Flash Image | 4/4 | documented-rate estimate | 0.268756 |
| xAI Grok Imagine Image 2.0 | 4 required + 1 paid hosted-URL failure | exact `cost_in_usd_ticks` | 0.280000 + 0.070000 |
| BFL FLUX.2 Pro | 4/4 | exact returned credits at $0.01/credit | 0.240000 |

One OpenAI attempt released at $0 after TLS handshake failure before HTTP submission (elapsed 0.332 s; no request ID). Invoice-level confirmation remains pending for the estimated OpenAI/Gemini arms. The ledger says so; this draft does not treat those two arms as invoiced.

ADR-0023: all paid bakeoff adapters share one reservation ledger. ADR-0029: unused bakeoff capacity is **not** production authority. ADR-0060: adapters have no independent cap.

### 1.3 CH05 production budget domain

`config/ch05-production-budget-policy-r1.json` and `docs/research/evidence/ch05-production-cost-ledger-r37.json`:

- state: `DISABLED_NO_PRODUCTION_SPEND_OR_UPLOAD_AUTHORITY`
- `approved_aggregate_cap_usd`: **null**
- `committed_actual_cost_usd`: `"0.000000"`
- `available_usd`: **null**
- `entries`: `[]`
- 124 local zero-external-cost milestones
- bakeoff-ledger reuse prohibited
- G07 $1.057377 is not copied into the CH05 ledger

`.env.example` keeps `NORTH_GARDEN_APPROVED_BAKEOFF_CAP_USD` and `NORTH_GARDEN_APPROVED_PRODUCTION_CAP_USD` blank until intentionally authorized. Blank values disable paid adapters. This assignment did not open `.env`.

### 1.4 Local Comfy/RTX research (no API)

`experiments/results/research-time-cost-ledger-20260901.json` (dirty-root copy; summarized in this worktree’s `docs/research/production-time-cost-ledger.md`): as of 2026-09-01, **79** completed local renderer generations, **2,568.448 s (0.713 h)**, `external_api_usd` 0, accepted production outputs 0. Local electricity and depreciation: **unmeasured**.

### 1.5 Built-in ImageGen chapters and reimaginings

Paid API/cloud GPU spend recorded as `$0` on every chapter and reimagining ledger inspected. Built-in **monetary cost remains null**.

| Body of work | Paid API/cloud USD | Built-in monetary cost | Cloud GPU ops |
| --- | ---: | --- | ---: |
| CH05 six-route / complete-chapter activity (reconciled) | 0.000000 | null | 0 |
| CH06–CH13 default-house route | 0.000000 | null | 0 |
| Ember Lattice Phase A pilot | 0 | null | 0 |
| Ember Lattice Phase B volume | 0 | null | 0 |
| Borrowed Down 10-chapter volume | 0 | null | 0 |
| The City Keeps Oaths 10-chapter volume | 0 | null | 0 |

---

## 2. Unmeasurable product cost (the live route)

The route that actually produced post-G07 North Garden art and the reimaginings is **OpenAI built-in ImageGen in Codex**, not the metered GPT Image 2 API used in G07.

Every CH05 RenderRecord and chapter time-cost record keeps `model`, `endpoint`, `provider_request_id`, `usage`, `monetary_cost_usd`, and `deterministic_seed` as **null** with an unavailable-not-zero contract. CH06 client wrapper also failed to capture per-request elapsed time (`individual_elapsed_seconds`: null).

Implication: the elaborate reservation machinery (ADR-0023 / ADR-0029) is proven on G07 (~$1.06) and synthetic fixtures, and is **not** observing the production path. If the built-in product becomes priced, rate-limited, entitlement-capped, or withdrawn, there is no ledger of what the existing corpus “cost,” and no executed paid-API fallback for chapter-scale narrative panels. That is a first-class economic and continuity risk, not a rounding error.

OpenAI’s public data-use page (updated 2026-03-13; accessed 2026-09-06) states: API / ChatGPT Team / Enterprise are **not** trained on by default; **individual** ChatGPT/Sora/Operator content **may** be used to train unless the user opts out. An OpenAI EU AI Act training-content summary for ChatGPT Images 2.0 (PDF, 2026-08-07) states that, subject to privacy settings and opt-outs, interactions with products such as ChatGPT **and Codex** may be used to train Images 2.0. The in-product ImageGen tool used here **did not expose** which entitlement, opt-out state, or training default applied to these calls. Treat Codex ImageGen training-on-inputs as **unverified for this project**, not as the API default.

---

## 3. Hardware dependence

Measured local GPU (GAP_ANALYSIS 2026-08-31; Qwen feasibility 2026-09-01):

- NVIDIA GeForce **RTX 5090 Laptop**, **24,463 MiB** VRAM, driver 616.56
- Historical legacy Anima/Comfy generations: about **20–37 s** at 42 steps (GAP_ANALYSIS; Comfy was stopped at that writing)
- Stage A mean generation time: **37.66 s** over 24 local candidates (903.79 s total)
- Official Qwen-Image-Edit-2511 BF16 artifact set: **53.75 GiB** LFS; **deferred** because it does not fit 24 GiB before working memory (ADR-0015)
- `AGENT_FIRST_PROMPT.md`: local 24 GB VRAM is **not** an architectural ceiling
- `.env.example` lists unused `RUNPOD_API_KEY`, `VAST_API_KEY`, `LAMBDA_API_KEY`; ledgers record **zero** cloud GPU operations

Local ComfyUI is pinned in GAP_ANALYSIS at commit `82f839f5e737d8bfce480872ba05e5a430f2526f`. After 2026-09-01, executed chapter/reimagining rasters used built-in ImageGen, not this GPU. There is **no ADR formally retiring** Comfy/LoRA/ai-toolkit. A prior untracked engineering review called that arm dormant; this draft records the evidence gap rather than inventing a retirement.

Electricity/depreciation for this programme: **unmeasured / null**. A 2026-08-31 internal research estimate (`research/authoritative/v2.1.1/registry/POLICY_LICENSE_REGISTRY.md`) of ~$0.25 electricity per hypothetical 70-panel chapter (5.6 GPU-h × 0.22 kW × 18.44¢/kWh, EIA May 2026) is **not** a measured North Garden figure and is not entered as programme cost.

---

## 4. Provider dependence

| Route | Status in this programme | Data-use / rights gate | Economic exposure |
| --- | --- | --- | --- |
| Local Comfy + RTX 5090 | Last measured research 2026-09-01; not used for later chapter rasters | License/provenance blocks on NoobAI, FLUX.2-dev VAE, adult LoRAs, unverified merges | Capex/electricity unmeasured; no API invoice |
| Built-in Codex ImageGen | **Live path** for CH03–CH13 and reimaginings | Model/terms/cost/seed **null**; training-on-inputs unverified vs API default | Cost unmeasurable; single-product outage risk |
| OpenAI GPT Image 2 **API** | G07 4/4; ADR-0025 selected for bounded repair hardening; **not** the chapter executor | API not trained on by default (provider doc 2026-09-01 / OpenAI data-use page 2026-03-13) | $0.198621 estimated / 4 G07 edits; invoice pending |
| Gemini 3.1 Flash Image API | G07 4/4; paid-tier only for bakeoff | Paid: Google says it does not use paid-service prompts to improve products | $0.268756 estimated |
| xAI Grok Imagine Image 2.0 API | G07 4/4 + 1 paid transport failure | API not trained on without permission (provider doc) | $0.35 exact ticks |
| BFL FLUX.2 API | G07 4/4; **boundary closed** | API terms 2026-08-04: BFL may use Inputs/Outputs to train; ADR-0019 fictional-geometry only | $0.24 exact; **no adult refs ever** |
| Managed GPU (RunPod/Vast/Lambda) | Keys named in `.env.example`; no adapter wired | N/A until a profile exists | $0 recorded |

BFL remains ineligible for adult-likeness or character-reference production under current terms. Expanding BFL inputs would be a rights incident, not a cost optimization.

Provider-null pattern (reimaginings and CH05 reduced-palette / ablation manifests): `provider: null`, `model: null`, `endpoint: null`, `provider_request_id: null`. Ember Lattice Phase A validation-report records the same unavailable metadata block.

---

## 5. Throughput (generation only)

Generation seconds are **not** human minutes and are **not** chapter wall-clock unless a record says so. Mixed-scope sums are prohibited by the CH05 reconciliation package.

### 5.1 Local RTX / Comfy

- Stage A: 24 candidates, 903.79 s, mean 37.66 s, 0 accepted
- Full local research ledger: 79 generations, 2,568.448 s, 0 production-accepted
- Sequential inpaint / FLUX / Illustrious arms: see ledger; all 0 production-accepted

### 5.2 G07 paid APIs

From `docs/research/g07-provider-bakeoff-comparison-20260901.md`:

| Arm | Mean elapsed | Required-arm cost |
| --- | ---: | ---: |
| OpenAI GPT Image 2 | 32.087 s | $0.198621 est. |
| Gemini 3.1 Flash Image | 11.759 s | $0.268756 est. |
| xAI Grok Imagine Image 2 | 12.506 s | $0.280000 exact |
| BFL FLUX.2 Pro | 18.647 s | $0.240000 exact |

Human review of the blinded packet: **0/20 decisions**, minutes **null**. No arm is accepted art.

### 5.3 Built-in ImageGen — CH05

`docs/research/evidence/ch05-active-goal-art-output-reconciliation-r1.json`:

- 76 service rasters, 312 panel-level candidates/crops, 132 authorized reference uses
- Six-route aligned subset: 300 (50 r6 selected + 250 five-arm crops)
- Aggregate end-to-end seconds: **null** (incomparable timing scopes)
- Example overlap-adjusted batch walls (not additive): alt-graphic 954.3 s (11 calls), clear-line-watercolor 1,090.0 s, premium-cel 1,234.0 s; flat gouache non-overlap arithmetic 1,290.989 s with actual E2E null

CH05 overnight 20-candidate run: 919.389 s observed tool elapsed; cadence-hardening 6 candidates / 310.669 s; combined overnight+hardening 26 candidates / 1,230.058 s (GOAL.md / production-time-cost-ledger.md). p10/median/p90 on that 26-candidate basis: 30.531 / 51.227 / 56.524 s generation-only.

Nonexecuted remaining-plan envelope (36 initials + 13 bounded repairs): median **2,510.123 s** generation-only; human minutes **null**; monetary cost **null**. Fresh-consistency fallback (50+18): median **3,483.436 s**. These are scenarios, not runs.

### 5.4 Built-in ImageGen — CH06–CH13

`docs/research/evidence/ch06-ch13-production-time-cost-summary-r1.json`:

- 8 complete chapters, 64 sequence requests/outputs, 320 panel candidates, 166 authorized reference uses
- Triage (agent, not owner): PASS 296 / WARN 5 / FAIL 19
- Reported overlapping-interval sum CH07–CH13: **15,060.448 s** — **not** elapsed wall-clock; intervals overlap inside parallel groups
- CH06 per-request timing: **unavailable** (null, not zero)
- Accepted / commercially cleared / exact production base: **0 / 0 / 0**
- Human review minutes: **null**

Per-chapter parallel-group walls (last request in each of two overlapping groups; chapter wall is not their sum):

| Chapter | Sequence requests | Panel candidates | Parallel-group walls (s) | Overlapping interval sum (s) |
| --- | ---: | ---: | --- | ---: |
| CH06 | 8 | 40 | unavailable | unavailable |
| CH07 | 8 | 40 | 497.196, 460.672 | 2,370.565 |
| CH08 | 8 | 40 | 430.624, 437.107 | 2,158.140 |
| CH09 | 8 | 40 | 437.501, 417.841 | 2,177.960 |
| CH10 | 8 | 40 | 403.285, 414.710 | 2,045.824 |
| CH11 | 8 | 40 | 442.406, 429.358 | 2,214.860 |
| CH12 | 8 | 40 | 420.731, 427.911 | 2,113.601 combined overlapping |
| CH13 | 8 | 40 | 421.512, 399.711 | 1,979.498 exact wrapper |

If the two groups truly ran concurrently, generation wall per 40-panel chapter is on the order of **~400–500 s (~7–8 min)** of caller-visible ImageGen time, **excluding** review, lettering, repair, and owner decisions. That figure is generation-only and must not be compared to a professional episode’s labor hours.

### 5.5 Reimaginings (sibling worktrees; $0 paid)

| Work | Generation requests (as recorded) | Direct paid USD | Provider metadata | Acceptance / commercial |
| --- | --- | ---: | --- | --- |
| Ember Lattice Phase A | 24 | 0 | model/endpoint/request/usage/cost/seed null | pending / uncleared |
| Ember Lattice Phase B volume | 224 new requests; 16 pilot sources reused; validation also lists 225 new generated sources | 0 | same null pattern in pilot records | unaccepted / uncleared |
| Borrowed Down | 67 total (62 sequence/repair, 4 style, 1 character-ref); 15,939.808 s summed overlapping | 0 | null | unaccepted / uncleared |
| The City Keeps Oaths | 91 total (80 production, 9 style/topology, 2 refs); 28,172.185 s summed overlapping | 0 | null | unaccepted / uncleared |

Do not add those latency sums across works or treat them as wall-clock.

---

## 6. Labor

### 6.1 Measured human minutes: null

Every live ledger inspected records `human_review_minutes: null` (or `unmeasured`). The instrumentation exists; the clock has not been started on real owner review.

| Instrument | Subjects | Decisions taken | Minutes |
| --- | ---: | ---: | --- |
| G07 blinded packet (`config/g07-blinded-human-review-protocol-r1.json`, packet SHA `4b1e5f0c…478161`) | 20 timed decisions / 16 candidates | 0 | null |
| CH05 live review-time contract | 39 subjects | 0 events | null |
| CH01 kitchen sequence (only `production/accepted/` artifact) | 4 panels | Codex visual review; `human_review_status`: not yet performed | null |
| CH02 archival research edition | 3 panels | INTERNAL_RESEARCH_ACCEPTED; non-commercial | null |
| CH03–CH13 generated candidates | hundreds of rasters/crops | 0 owner accepted | null |

CH01 `commercial_release_allowed`: **false**. CH02 import boundary: adult-likeness legacy path **not commercially cleared**. Post-CH01 production-accepted panels: **0**.

GOAL.md success measures include accepted-panel rate and human minutes. Those two measures are still empty. Engineering output (ADRs, validators, zero-external-cost milestones) is large; that is not a substitute labor metric.

### 6.2 Estimate — owner review of *existing* unaccepted inventory

**Estimate, not measured.** Assumptions:

1. Reviewer is the owner (the missing gate), not a second agent.
2. G07: 20 decisions × 1–3 minutes including written tags = **20–60 minutes**.
3. One 50-panel chapter first-pass accept / reject / one-class-repair at 1–4 minutes per panel = **50–200 minutes**, excluding generation of repairs and excluding lettering QC.
4. A 320-panel CH06–CH13 pass at the same 1–4 min/panel = **5–21 hours**, still excluding repairs.
5. No estimate is offered for “make it as good as Tower of God,” because that is art-direction labor with no measured baseline in this repo.

If those sessions do not happen, downstream cost, yield, and route-comparison numbers remain unfalsifiable.

### 6.3 Estimate — industry conventional webtoon staffing and cadence

**Industry ranges, not this programme.** Sources accessed 2026-09-06:

- Korea Institute of Labor Safety and Health English summary of 2022 webtoon-writer conditions: most serials **one episode per week**; mean **68 cuts/episode** (median 70); writers judged **52 cuts** more appropriate; mean **51 hours/week**, 5.7 days, 9.9 hours/day.
- KBS *추적60분* (2025-08 broadcast; English transcript in search snippet): one storyboard artist described **65–70 panels** taking about **32–36 hours**, with much higher weekly hours when pay is low.
- Kim, *Platformisation and precarity…* (ResearchGate record dated 2026-02-22): factory-style webtoon production split into writing, adaptation, storyboard, character, line, background, colour, post; **typically five to six people including producers**. One studio example of “three episodes per week” at 2 million KRW/month is cited as **precarity**, not a quality benchmark.
- Honeytoon production blog (2026-08-06): solo or 6–10 specialists; **~2 weeks/episode** and often **bi-weekly** release. Vendor blog; lower confidence than KILSH/academic sources.

GOAL.md targets **50–90 panel** chapter-scale drafts. That is in the same panel-count band as a Korean weekly episode (~65–70 cuts), not a 4-panel research strip.

### 6.4 Estimate — AI-assisted chapter once templates exist

The project’s own 2026-08-31 registry (`POLICY_LICENSE_REGISTRY.md` §5) states **there are no published measured hours-per-chapter** for AI-assisted serialized webcomics, then offers an estimate of **12–25 hours per chapter** once LoRAs and templates are stable (~20% script/thumbs, ~35% generation and culling, ~30% compositing/cleanup, ~15% lettering/QC), with culling/cleanup as the bottleneck. That remains an **estimate**. This programme has not instrumented those buckets. Treating 12–25 h as a forecast would launder an unmeasured guess into a plan.

### 6.5 Labor diagnosis (evidence, not a wage model)

Compute is cheap relative to a weekly 50–70 panel professional episode. The scarce unmeasured input is **owner (or hired art-director) minutes**. The pipeline currently converts agent time into unaccepted candidates and evidence about evidence. Yield in accepted, rights-cleared panels per human hour is **undefined** because the denominator and the accepted-panel numerator are both empty after CH01’s four internal-research panels.

---

## 7. Licensing and commercial clearance

**No generated candidate in the live ImageGen corpus is commercially cleared.** Registry and chapter records state this repeatedly; it is not a style opinion.

### 7.1 Acceptance vs clearance (do not collapse)

| Class | What exists | Commercial release |
| --- | --- | --- |
| CH01 four kitchen composites | `INTERNAL_RESEARCH_ACCEPTED_NOT_PUBLISHED`; Codex visual review; human minutes null | `commercial_release_allowed: false`; LoRA/base provenance incomplete |
| CH02 three archival panels | INTERNAL_RESEARCH_ACCEPTED; non-commercial archival review | not commercially cleared |
| G07 16 candidates | pending blinded human review | not cleared |
| CH03–CH13 ImageGen | 0 accepted | 0 commercially cleared; 0 exact production bases |
| Reimaginings | owner-review pending | commercially uncleared; non-reproducible unless proven |

ADR-0016: a new edition must not claim an archival render became reproducible or commercially cleared.

### 7.2 NoobAI — commercial prohibition (primary source)

Official model card [Laxhar/noobai-XL-1.0](https://huggingface.co/Laxhar/noobai-XL-1.0), accessed 2026-09-06, section **II. Commercial Prohibition**:

> We prohibit any form of commercialization, including but not limited to monetization or commercial use of the model, derivative models, or model-generated products.

The card also requires open-sourcing derivatives/LoRAs/products and inherits Fair AI Public License 1.0-SD from Illustrious-xl-early-release-v0. Training data named on the card includes latest Danbooru (v1.0 cutoff ~2024-10-23) and an e621 dataset.

GAP_ANALYSIS (2026-08-31) and `model-license-registry.md`: local `JANKUTrainedChenkinNoobai_v777.safetensors` and the NoobAI-named ControlNet are `BLOCKED_FROM_COMMERCIAL_PIPELINE`. Exact upstream provenance of the local files is **unrecorded**; do not infer an exception. Any commercial profile that used this lineage, or sold products generated from it, would conflict with the stated card terms.

### 7.3 Other local weights (registry 2026-08-31, refreshed 2026-09-01)

| Artifact | Status | Rights note |
| --- | --- | --- |
| Anima aesthetic v1.1 | INTERNAL_BASELINE_ONLY | source/license unrecorded; GAP: internal baseline until reviewed |
| `soren_v1` / `sigrid_v1` LoRAs | SENSITIVE_ADULT_LIKENESS_LOCAL_ONLY | base-license + signed consent/provenance required before any commercial profile |
| hyphoria / novaAnimeXL merges | QUARANTINED_UNVERIFIED | metadata ≠ provenance |
| FLUX.2 Klein 4B FP8 transformer | local research candidate | Apache-2.0 (bundled LICENSE.md) |
| `flux2-vae.safetensors` | NON_COMMERCIAL_DEPENDENCY_LOCAL_RESEARCH_ONLY | `flux-1-dev-non-commercial-license` on the Comfy-Org flux2-dev pin |
| Illustrious XL v2.0 | fictional research; license review pending | CreativeML OpenRAIL-M on pinned README; intended-use review not closed |
| Xinsir ControlNet Union ProMax | local research control | Apache-2.0 on current official card; main-checkpoint OpenRAIL-M remains a separate gate |
| Qwen Image VAE (pinned) | Apache-2.0 for that file | does not clear a complete Qwen profile |
| InsightFace weights | none found locally | FaceID examples exist; future use needs a fresh inventory |

FLUX.2 Klein + non-commercial VAE cannot be a commercial FLUX profile without replacing the VAE under a cleared license. Open item in the 2026-08-31 registry: verbatim FLUX.2 [dev] “Non-Commercial Purpose” definition was behind a gated 401 and was **not** re-fetched here.

### 7.4 External-provider output rights (G07 documentation, 2026-09-01)

Documented before spend in `docs/research/provider-primary-documentation-20260901.md`. None of the G07 outputs is accepted or commercially cleared. BFL API training-use is a hard input-class limit, not a pricing footnote.

---

## 8. Model provenance

`BUNDLE_PROVENANCE.json` only identifies the authoritative research archive zip (`ngvnc_research_v2_1_1.zip`) and its SHA-256. It is not a model-weight bill of materials.

CH05 final provenance audit (`docs/research/ch05-final-model-license-provenance-audit-r1.md`): 29 records (26 CH05 + 3 non-canon), 39 reference uses across exactly three authorized fictional-adult hashes, 29/29 model/endpoint/request/usage/cost/seed **null**, 0 accepted, 0 commercially cleared, 0 reproducible. Paid API calls/new uploads/paid spend 0/0/$0.

Authorized CH05 reference hashes (composition/identity plates, not LoRAs):

- `50f6413e…43eb` — P036 composition-only
- `c0a2be11…6b4a` — P040 Sigrid face
- `cb1e7b49…c83d` — P050 dual identity action

Later complete-chapter and CH06–CH13 arms reuse those three hashes; newly generated outputs **must not be re-uploaded**. That is both a rights control and a continuity constraint (no “use last chapter as reference” loop).

Built-in outputs cannot be represented as paid-provider RenderRecords, seed-reproducible masters, or commercially cleared assets.

---

## 9. LoRA training-data privacy

- Two adult-identity LoRAs exist locally (`soren_v1`, `sigrid_v1`). GAP_ANALYSIS: training/reference images are **sensitive and remain unmodified**.
- GOAL.md / AGENT_FIRST_PROMPT: adult likeness is **local by default**; child likeness/training/upload is forbidden.
- Registry: commercial use requires base-license **and** signed consent/provenance. No such signed packet was found in tracked docs.
- Ember Lattice premium R&D (2026-09-04): existing Soren/Sigrid LoRAs are **out of scope** for Ember; no fresh consented Ember training set exists; LoRA training deferred.
- No ledger shows these LoRAs or their datasets uploaded to OpenAI, Gemini, xAI, BFL, RunPod, Vast, or Lambda.
- If the LoRAs were trained on a NoobAI or uncleared Anima checkpoint, **the adapters inherit that commercial block** (registry §2). Exact base used for `soren_v1`/`sigrid_v1` is **not** independently proven in the files read for this draft; treat commercial use as blocked until that chain is documented.
- Hosted LoRA training on community cloud GPUs is flagged in the 2026-08-31 registry as a likeness-leak risk (third-party machines). No such training run is in the paid ledgers.

Privacy risk that **did** occur: fictional-adult **reference images** (not the LoRA datasets) were sent to **built-in ImageGen** for CH05+ and reimaginings. That is a different data class from G07’s geometry-only bakeoff. Training-on-those-uploads for the Codex product remains **unverified** (see §2).

---

## 10. Platform-policy risk

### 10.1 WEBTOON Canvas (official)

[WEBTOON Community Policy / Canvas content guidelines](https://www.webtoons.com/en/terms/canvasPolicy), last updated **2025-11-25**, implemented six weeks later (~**2026-01-06**). Accessed 2026-09-06.

A full-text search of the official page for an AI-generation or AI-disclosure rule did not find a dedicated AI clause (substring hits were unrelated, e.g. “Taiwan”). Creators must own IP rights in uploads; copyright infringement is forbidden. **Silence is not permission and is not a disclosure requirement.** The 2026-08-31 internal registry already recorded Canvas terms as silent on AI and warned not to trust ranking blogs.

A 2026-05 Comistitch blog claiming a mandatory Canvas “AI-assisted” tag since February 2026 **contradicts** the official policy page as fetched on 2026-09-06 and matches the class of secondary source the internal registry told the project to ignore. It is **not** used as a fact here.

WEBTOON Originals contracts are **non-public**. Assume disclosure and human-authorship representations until a signed contract is read. That is a limitation, not a fabricated clause.

### 10.2 Naver Webtoon (Korea) and AI law

- 2023: Naver Webtoon barred generative-AI entries from its contest after reader backlash against suspected AI art (*Chosun Biz* 2023-05-31; MIT Technology Review 2025-04-22 on *The Knight King Returns with the Gods*).
- 2025–2026: WEBTOON/Naver have publicly disputed union claims that contracts allow AI training on creator works without consent (ANN 2025-11-06). The union published a “research purposes” clause; the company said it does not train AI on creators’ content. **This draft does not resolve that dispute.**
- Korea AI Basic Act transparency: ANN 2026-01-24 and Korean coverage (Money Today 2025-12-24; Hi-Tech 2026-01-20) report **business/provider** watermark/disclosure duties, with **individual uploaders** generally not the obliged party, and machine-readable watermarks allowed for webtoon-like formats. That is **not** a platform green light, and it is **not** WEBTOON Canvas policy.

Market risk: reader campaigns against undisclosed AI webtoons are documented independently of ToS text. Internal registry: “Market risk exceeds policy risk.”

### 10.3 Tapas (official, accessed 2026-09-06)

[Tapas Content and Community Guidelines](https://help.tapas.io/hc/en-us/articles/115005323707-Content-and-Community-Guidelines): **“AI generated content is not allowed on Tapas.”** Page footer still “Last Modified : March 09th, 2022”; originating announcement 2023-01-23 remains consistent. Secondary blogs claiming Tapas now allows tagged AI are **false** relative to this official page.

### 10.4 Other surfaces (internal registry 2026-08-31, not re-litigated except Tapas/WEBTOON)

| Platform | Recorded posture | This draft |
| --- | --- | --- |
| Patreon | no AI-art rule (harassment/deepfake rules still apply) | not re-fetched; treat as 2026-08-31 snapshot |
| Kickstarter | disclosure required (policy 2023-08-29), including consent for source works | not re-fetched |
| GlobalComix | 2026-03-20: fully AI-generated removed; AI inside a human-artistry workflow may be monetized with disclosure and discretion | not re-fetched |
| WEBTOON Originals | per-contract | still unread |

Any publication plan that ships current ImageGen rasters as-is is a **rights and platform** decision, not an engineering merge.

---

## 11. Route comparison for the next dollar and the next hour

| Lens | Local RTX + Comfy | Built-in ImageGen (current) | Paid APIs (G07-class) |
| --- | --- | --- | --- |
| Direct $ so far | $0 API; electricity null | $0 paid; **product $ null** | **$1.057377** committed |
| Marginal $ / image | unmeasured kWh + depreciation | unknown entitlement | ~$0.05–$0.07 observed on G07 edits (size/quality specific; not a chapter quote) |
| Throughput | ~20–38 s/candidate historically on 24 GB | ~30–120 s/call typical; chapter groups ~7–8 min generation if parallel | Gemini/xAI ~12 s mean; OpenAI ~32 s mean on G07 |
| Provenance | hashable weights/graphs/seeds if recorded | **null model/seed** | request IDs + usage (OpenAI/Gemini) or ticks/credits (xAI/BFL) |
| Commercial path | blocked until NoobAI/VAE/LoRA/Anima chain is replaced or cleared | **uncleared**; terms not in tool result | still uncleared; BFL unusable for adult refs |
| Privacy | likeness can stay local | fictional-adult refs already uploaded to in-product tool | G07 used geometry only; adult refs not authorized |
| Hardware lock-in | 24 GB cannot host official Qwen BF16 | none local | none local |
| Single-vendor lock-in | Comfy + specific checkpoints | **high** (entire CH05–CH13 + reimaginings) | diversified in G07, then abandoned for chapters |
| Human minutes to accept | null | null | null |

Cheapest path in invoices is local or in-product. Cheapest path in **publishable panels** is unknown, because acceptance is zero. Spending more on APIs without owner review would buy more uncleared pixels.

---

## 12. Explicit nulls and unknowns

| Item | Status |
| --- | --- |
| This assignment paid spend | $0 |
| Built-in ImageGen $ / image | null |
| Built-in model snapshot, endpoint, request IDs, seeds | null |
| Codex vs API training-on-inputs for these calls | unverified |
| Invoice confirmation for OpenAI/Gemini G07 | pending |
| Local electricity and GPU depreciation | unmeasured |
| Live human review minutes | null |
| Accepted panels post-CH01 | 0 |
| Commercially cleared generated candidates | 0 |
| CH06 per-request elapsed seconds | null |
| CH05 / mixed-arm combined E2E wall | null (forbidden to invent) |
| Ember Phase B request count | 224 in `volume-master.json` vs 225 `new_generated_sources` in `volume-validation.json` — both recorded; not silently averaged |
| WEBTOON Originals contract AI clauses | unread / null |
| Signed adult-likeness consent packet | not found |
| Exact commercial license of Anima base and of `soren_v1`/`sigrid_v1` training base | unrecorded |
| Exact provenance of local NoobAI-named files vs official NoobAI-XL 1.0 | unrecorded (blocked anyway) |
| FLUX.2 [dev] Non-Commercial Purpose verbatim text | previously gated; not re-fetched |
| `.env` live key inventory | not opened; `.env.example` only |

---

## 13. Implications for continuation vs rebuild (economics/rights only)

These are constraints for the strategy matrix, not a visual-quality ranking.

1. **Do not protect sunk compute cost.** Measured paid spend is $1.06. Local GPU time is 0.713 h plus later unmetered ImageGen. That is not a reason to keep a route that cannot be rights-cleared.
2. **Do protect the scarce resource:** owner/art-director hours. Another unreviewed 50–320 panel dump has near-zero expected publishable yield.
3. **A commercial or WEBTOON Originals path cannot use** NoobAI-lineage weights, the current FLUX.2-dev VAE, uncleared adult LoRAs, or uncleared ImageGen rasters as-is.
4. **Tapas is closed** to AI-generated content on current official guidelines.
5. **Canvas UGC** has no official AI-disclosure clause as of the 2026-09-06 fetch; Originals terms are unknown; Korean reader backlash is real. Disclose in the owner’s voice before any public test, as a market-risk control, not because Canvas currently mandates a tag.
6. **If the next pilot stays on built-in ImageGen**, budget $0 cash and accept unmeasurable cost, null provenance, and a single-vendor outage risk. Record that as a conscious trade, not as “free.”
7. **If the next pilot needs commercial eligibility**, plan a **cleared-weight or paid-API** stack with a dated terms refresh, and keep adult likeness local or on a no-train-by-default paid API — not BFL, not free-tier Gemini, not an unverified Codex training default.
8. **Human-directed hybrid (layout, model sheets, targeted regen, human finish)** is the only class of strategy whose labor shape resembles the 32–36 h / 5–6 person industry ranges. Generation-only 8-minute chapters do not.
9. **Kill criterion (economic):** further chapter-scale generation before a timed owner session leaves accepted-panel rate at 0 and rights at uncleared; additional GPU/API spend cannot move those numbers.

---

## 14. Source map

Machine-readable claims: `economics-sources.json` in this folder. Primary local paths are listed there with dates. Web sources were accessed 2026-09-06.
