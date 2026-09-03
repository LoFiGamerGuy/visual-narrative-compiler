# Model and license registry: initial local inventory

Date: 2026-08-31. This is an inventory and gate, not a claim that an unreviewed artifact is commercially usable. Hashes are SHA-256 of local files. Detailed baseline hashes are also attached to every `experiments/records/baseline_legacy` record.

| Local artifact | SHA-256 | Pipeline status | License/provenance state |
| --- | --- | --- | --- |
| `ComfyUI/models/checkpoints/JANKUTrainedChenkinNoobai_v777.safetensors` | `88177d224ce97f60cf3e908f87902f913ed4562bd79d237f84238a4354601efb` | `BLOCKED_FROM_COMMERCIAL_PIPELINE` | Exact upstream provenance is unrecorded. The official NoobAI-XL 1.0 card prohibits commercialization of the model, derivatives, and model-generated products; do not infer an exception for this file. |
| `ComfyUI/models/controlnet/noobaiXLControlnet_epsBlur.safetensors` | `bb6217e8bce3d29df43a846e97f2a3baa3e7524b8436695dd3286bd9e7ba53bd` | `BLOCKED_FROM_COMMERCIAL_PIPELINE` | File name indicates NoobAI lineage; exact provenance/license remains to be independently established. |
| `ComfyUI/models/diffusion_models/anima-aesthetic-v1.1.safetensors` | `3c1868387a3a1ff504bbb87c33678321965ead381fcf87afbd0264daa600c082` | `INTERNAL_BASELINE_ONLY` | Existing legacy base; source/license must be recorded before commercial/profile use. |
| `ComfyUI/models/text_encoders/qwen_3_06b_base.safetensors` | `cd2a512003e2f9f3cd3c32a9c3573f820bb28c940f73c57b1ddaa983d9223eba` | `INTERNAL_BASELINE_ONLY` | Existing legacy dependency; exact source/license unrecorded. |
| `ComfyUI/models/vae/qwen_image_vae.safetensors` | `a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f` | `LOCAL_RESEARCH_DEPENDENCY_PROVENANCE_PINNED` | Exact local SHA matches current official `Comfy-Org/Qwen-Image_ComfyUI` artifact at revision `7beb7b647f04469fbe64ba8adc2bb0d7e5e9f73f`; the repository card declares Apache-2.0. This only proves this VAE's current source artifact, not the licenses of a complete Qwen profile. |
| `ComfyUI/models/loras/soren_v1.safetensors` | `8e8cafaf663a02a6c7477f10be60285a8484b90f4e19278dbdf43c7263e83277` | `SENSITIVE_ADULT_LIKENESS_LOCAL_ONLY` | Adult-likeness LoRA; base-license and signed-consent/provenance record required before any commercial profile. |
| `ComfyUI/models/loras/sigrid_v1.safetensors` | `015216b8c40c2b3a1d78fd9791842061e3f3a79178bcef12eaa20606194634d9` | `SENSITIVE_ADULT_LIKENESS_LOCAL_ONLY` | Adult-likeness LoRA; base-license and signed-consent/provenance record required before any commercial profile. |
| `ComfyUI/models/checkpoints/hyphoria_v002.safetensors` | `d463b3a7deb92181fc4c5afd3a3e0aa82c08b8ed18312109c618aa94af51dbb4` | `QUARANTINED_UNVERIFIED` | Embedded metadata labels it SDXL and references several `illustrious/*` merge inputs, but no source revision or license artifact. Metadata is not sufficient provenance. |
| `ComfyUI/models/checkpoints/novaAnimeXL_ilV190.safetensors` | `fa486caafc330f133605d3c18b418d183812f14946631c6544bfb28730db6d6f` | `QUARANTINED_UNVERIFIED` | Legacy Lion Cub workflow asset. Embedded `sd_merge_models` metadata shows a multi-level merge with placeholder hashes and unnamed temporary inputs; exact upstream source/license cannot be reconstructed from it. |
| `ComfyUI/models/ipadapter/ip-adapter-plus_sdxl_vit-h.safetensors` | `3f5062b8400c94b7159665b21ba5c62acdcd7682262743d7f2aefedef00e6581` | `QUARANTINED_UNVERIFIED` | Not used by North Garden baseline. Installed IPAdapter package includes FaceID example workflows, so any future FaceID use requires a separate InsightFace-weight check. |
| `ComfyUI/models/controlnet/xinsir_controlnet_union_sdxl_promax.safetensors` and duplicate `controlnet-union-sdxl-promax.safetensors` | `9fae2e50cb431bfcbe05822b59ec2228df545ef27f711dea8949e9f4ed9f7cdc` | `LOCAL_RESEARCH_CONTROL_CANDIDATE` | Exact upstream SHA-256 match: `xinsir/controlnet-union-sdxl-1.0`, revision `801a4a3fa3d4c936f4feea95b98607bc6726f80c`, `diffusion_pytorch_model_promax.safetensors`; current official card declares Apache-2.0 and documents ProMax inpainting. Main-checkpoint OpenRAIL-M review remains a separate commercial gate. |
| `ComfyUI/models/diffusion_models/flux2-klein-4b-fp8/flux-2-klein-4b-fp8.safetensors` | `97ed34fe0567e436200f2faee3939b88f2b5d99f8af2a4dc16532c4245c0ccb6` | `LOCAL_RESEARCH_RENDERER_CANDIDATE` | Retrieved locally from official BFL revision `5b4408e59397a4a37ccb46afe426d8ed86379441`; the bundled `LICENSE.md` hashes to `ca02bc51900ab07789d1b70283329e7137f5af98f5161c23a1c81fc38a4af1fe` and is Apache-2.0. Tested only with fictional proxy inputs; no adult reference may be uploaded. |
| `ComfyUI/models/text_encoders/qwen_3_4b.safetensors` | `6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a` | `LOCAL_RESEARCH_RENDERER_DEPENDENCY` | Retrieved locally from official `Comfy-Org/z_image_turbo` revision `08d04455279082882deaabc8d0d09fc914c071e1`. Current primary API check on 2026-08-31 and retained README (`3be81b…57473`) declare Apache-2.0. |
| `ComfyUI/models/vae/flux2-vae.safetensors` | `d64f3a68e1cc4f9f4e29b6e0da38a0204fe9a49f2d4053f0ec1fa1ca02f9c4b5` | `NON_COMMERCIAL_DEPENDENCY_LOCAL_RESEARCH_ONLY` | Retrieved locally from official `Comfy-Org/flux2-dev` revision `ab9055628ea245000e610f2aa2c96f4746093546`. Current primary API check on 2026-08-31 and retained README (`06e6a5…c0f6620`) declare `flux-1-dev-non-commercial-license`; this blocks a commercial FLUX profile using this exact VAE. |
| `ComfyUI/models/checkpoints/illustrious-xl-v2.0/Illustrious-XL-v2.0.safetensors` | `c2a1a3eaa13d4c107dc7e00c3fe830cab427aa026362740ea094745b3422a331` | `LOCAL_FICTIONAL_RESEARCH_RENDERER_CANDIDATE_LICENSE_REVIEW_PENDING` | Retrieved from official `OnomaAIResearch/Illustrious-XL-v2.0`, revision `69459c1fe6f46db41ab31e6114f05acc0e06bcaa`; exact upstream LFS SHA matches. The pinned README declares CreativeML OpenRAIL-M. Use remains fictional/local research only until intended-use terms are reviewed. |

The reusable local FLUX adapter profile is `experiments/render-profiles/flux2-klein-local-r1.json`. It records the pinned ComfyUI commit and treats the exact VAE's documented non-commercial declaration as a commercial gate rather than inferring permission from the transformer license.

## InsightFace audit

No `ComfyUI/models/insightface` directory or other local InsightFace pretrained-weight directory was found. No restricted InsightFace-distributed weight was deleted. `ComfyUI_IPAdapter_plus` contains FaceID examples, therefore its future use must trigger a fresh dependency/weight inventory before a commercial render profile may invoke it.

## Primary-source checks performed

- [NoobAI-XL 1.0 model card](https://huggingface.co/Laxhar/noobai-XL-1.0) currently identifies the Fair AI Public License and expressly prohibits commercialization of the model, derivative models, and model-generated products.
- [Illustrious XL v2.0 model card](https://huggingface.co/OnomaAIResearch/Illustrious-XL-v2.0), refreshed 2026-09-01: official API revision `69459c1fe6f46db41ab31e6114f05acc0e06bcaa`; its revision-pinned README is 1,404 bytes, SHA-256 `f06d16269c0f09e5d8cca9ff406f48c0ac484d0884f458e37f73f0fc9995092f`, and declares `creativeml-openrail-m`. Its exact local checkpoint is now inventoried above; it remains a fictional research candidate only.
- [Qwen Image Edit 2511 model card](https://huggingface.co/Qwen/Qwen-Image-Edit-2511), refreshed 2026-09-01: official API revision `6f3ccc0b56e431dc6a0c2b2039706d7d26f22cb9`; its revision-pinned README is 7,179 bytes, SHA-256 `9724c194bef2a6d821090f0cd65774962e8f77e3acbfb2a7cbbdd58c92049902`, and declares Apache-2.0. The card documents multi-image inputs and a 20B BF16 base; local feasibility is separately assessed in `docs/research/qwen-image-edit-2511-feasibility-20260901.md`.
- [Comfy's Qwen-Image-Edit-2511 INT8 workflow template](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_edit_2511_int8.json), refreshed 2026-09-01, identifies an official 19.09 GiB INT8 diffusion artifact, FP8 text encoder, and VAE. The prescribed encoder's source repository is currently labeled `tencent-hunyuan-community`, whereas the diffusion/VAE repositories declare Apache-2.0; `docs/research/qwen-image-edit-2511-comfy-int8-assessment-20260901.md` records this exact-component gate.
- [Tencent HunyuanVideo-1.5 LICENSE](https://huggingface.co/tencent/HunyuanVideo-1.5/raw/main/LICENSE), refreshed 2026-09-01, applies only in its defined Territory (excluding EU, UK, and South Korea), includes downstream distribution/notice conditions, prohibits using outputs/results to improve other AI models, and requires a separate license above 100M MAU. This is recorded for the prescribed Comfy INT8 text-encoder source; it is neither inferred Apache permission nor an automatic ban on local research in an eligible territory.
- [InsightFace repository](https://github.com/deepinsight/insightface) is the authority to consult for exact weight-package terms; source-code licensing must not be conflated with a pretrained-weight license.

## External renderer candidates — not acquired or approved

These are service routes, not local artifacts.  They have no local model-file hash to record.  Their exact API model/version, current primary terms, data configuration, request/response hashes, and cost become mandatory `RenderRecord` fields if an experiment is authorized.  They remain fictional-control-only candidates until then.

| Provider path | Status | Current primary-source provenance / gate |
| --- | --- | --- |
| Google Gemini 3.1 Flash Image / Gemini 3 Pro Image API | `EXTERNAL_FICTIONAL_CONTROL_EXECUTED_PENDING_REVIEW` | [Official image guide](https://ai.google.dev/gemini-api/docs/image-generation), refreshed 2026-09-01, documents reference capacity and image editing. Stable `gemini-3.1-flash-image` completed 4/4 G07 requests with request IDs, hashes, usage, timing, and $0.268756 documented-rate reconciliation. One output was recovered from its existing interaction after a local REST parser mismatch, without repeat generation. No output is reviewed, selected, or commercially cleared. |
| xAI Grok Imagine Image API | `EXTERNAL_FICTIONAL_CONTROL_EXECUTED_PENDING_REVIEW` | [Official Imagine guide](https://docs.x.ai/developers/model-capabilities/images/generation), refreshed 2026-09-01, documents direct `b64_json` output and temporary hosted URLs. Four required G07 candidates completed with exact request IDs, hashes, timings, and $0.28 provider-tick cost. A separate first-attempt $0.07 hosted-URL failure remains preserved. No output is reviewed, selected, or commercially cleared. |
| OpenAI GPT Image 2 API | `SELECTED_FOR_BOUNDED_LOCAL_HARDENING_PENDING_HUMAN_REVIEW` | [Official model page](https://developers.openai.com/api/docs/models/gpt-image-2), refreshed 2026-09-01, documents image-generation/edit endpoints and snapshot `gpt-image-2-2026-04-21`. All 4/4 G07 requests completed with request IDs, hashes, usage, timing, and $0.198621 documented-rate reconciliation. ADR-0025 selects the mechanism for local repair hardening; no result is accepted or commercially cleared and no expanded upload is authorized. |
| BFL FLUX.2 API | `EXTERNAL_FICTIONAL_CONTROL_EXECUTED_BOUNDARY_CLOSED` | [Official FLUX.2 image-editing guide](https://docs.bfl.ai/flux_2/flux2_image_editing), refreshed 2026-09-01, documents pinned `flux-2-pro`, polling, and URL-based reference inputs. BFL completed 4/4 at exact $0.24 returned cost. [Current FLUX API Service Terms](https://bfl.ai/legal/flux-api-service-terms), last revised 2026-08-04 and reviewed 2026-09-01, grant BFL rights to use Inputs/Outputs to improve/train services. ADR-0019 remains absolute: no further input class or commercial-release conclusion follows. |
| Built-in image-generation service | `FICTIONAL_FRONTIER_ART_RESEARCH_ONLY_PROVENANCE_LIMITED` | Built-in service generated CH03 fictional adult-design candidates on 2026-09-01. The service did not expose a model snapshot, seed, billable cost, or a project-reviewable commercial terms artifact in the execution result. It may support visual research only; do not represent output as commercially cleared, reproducible, or a provider-comparison score. |

The owner-directed CH05 style/density/scale exploration used the same built-in route for four new text-only fictional-adult candidates and supplied no input images or existing art. The result again exposed no model snapshot, endpoint, request ID, usage, or billable cost. Hash-pinned local candidates may be reviewed as visual research, but cannot be represented as paid-provider RenderRecords, reproducible model evidence, commercially cleared assets, exact production bases, or authority to upload later input packages.

## External-provider pre-execution refresh — 2026-09-01T15:07Z

Current official model, endpoint, pricing, terms/data-use, and content hashes are recorded in `docs/research/provider-primary-documentation-20260901.md` before spend. The four executable candidates are now `EXTERNAL_FICTIONAL_CONTROL_BAKEOFF_READY`, not selected or commercially approved.

- OpenAI remains pinned to `gpt-image-2-2026-04-21` at `/v1/images/edits`; API business data is not used for training by default.
- Gemini remains stable `gemini-3.1-flash-image` at `/v1beta/interactions`; only the paid-service credential context is permitted for this run.
- xAI remains `grok-imagine-image-2.0` at `/v1/images/edits`; the adapter now pins 1K/medium and reconciles exact `cost_in_usd_ticks`.
- BFL remains pinned `flux-2-pro`; current API terms preserve ADR-0019's absolute fictional-control-only boundary.

No service result is accepted, selected, or cleared by this documentation state.

## CH05 post-selection compiler boundary — 2026-09-01

The selected OpenAI mechanism's registry status is unchanged by CH05 compiler hardening. P033–P038 packet, layout-control, and run-ledger milestones made zero provider requests/uploads and incurred $0 external cost. They create no new service terms, commercial-clearance, model-selection, or external data-use conclusion; exact expanded upload authority remains absent.

Pre-spend chronology evidence now binds the dated primary-document record to all 19 exact G07 provider records. The record contains 19 official model/endpoint/pricing/terms links across four sections and predates the earliest attempt/positive-cost request by 490/695 seconds. This confirms G07 chronology only; any future CH05 request still requires a fresh then-current primary review and separate exact authority.

## G07 local evidence integrity boundary — 2026-09-01

The hash-only evidence manifest validates all 19 provider records and 16 candidates without changing any provider/model/license status above. Its vault root is `e84b0402…6d3ab`; generated pixels and runtime records remain ignored local evidence. Exact-byte retention is neither commercial clearance nor output acceptance, and BFL remains closed to every input beyond the two published hash-pinned fictional controls.

## Selected-route local repair policy boundary — 2026-09-01

The P036 local mechanics policy does not change OpenAI's registry status or commercial-clearance state. It binds the already selected snapshot/endpoint and local compositor evidence only; it contains no request executor, production input approval, upload authority, or production budget. Abstract proxy controls are explicitly ineligible for external submission.

## Selected-route boundary evidence schema — 2026-09-01

The v2.1 RenderRecord profile changes no provider, model, endpoint, terms, data-use, license, or commercial-use conclusion. It is an append-only local provenance requirement for any future authorized repair outcome. Its completed fixture is synthetic; it grants no upload, spend, production-input, output-acceptance, or expanded BFL authority.

## Selected-route hardening-state handoff — 2026-09-01

The consolidated hardening state does not change any registry status. OpenAI GPT Image 2 remains an engineering hardening route selected from measured G07 operations/diagnostics, with human review pending and no accepted or commercially cleared output. BFL remains closed beyond its two public fictional controls; all other expanded upload and CH05 production authority remains absent.

## Built-in ImageGen CH05 overnight boundary — 2026-09-01

The Codex built-in ImageGen product received only the three owner-authorized, hash-pinned fictional-adult project images. It disclosed no model name, endpoint, provider request ID, usage, cost, deterministic seed, license grant, or commercial-use decision; those fields remain unavailable rather than inferred. Twenty outputs are ignored local research evidence and none is accepted, commercially cleared, reproducible, or an exact production base. No direct paid API, BFL upload, alternate provider, real likeness, private reference, LoRA, dataset, or child-related material was used.

The six-candidate cadence-hardening continuation uses the same exact product/reference boundary and changes no license or commercial-use conclusion. Total new CH05 evidence is 26 ignored candidates; zero are accepted or commercially cleared.

The three future LitRPG concepts use only the same exact built-in/reference boundary. The new concept outputs were not re-uploaded as continuity references. They remain non-canon, ignored, unaccepted, and commercially uncleared; no provider/model/license status changes.

The offline owner-decision worksheet performs no model or provider operation and changes no registry conclusion. It links ignored local pixels, contains no remote assets or network calls, and exports only an uningested local draft; all output acceptance and commercial-clearance fields remain pending.

## Built-in ImageGen CH05 final provenance reconciliation — 2026-09-01

The final exact RenderRecord index contains 29 candidates: 26 CH05 ComicPanelPlan candidates and three explicitly non-canon future-LitRPG concepts. It records 29 exact prompts, 29 exact outputs, 39 authorized reference uses across exactly three hashes, and 1,385.036 elapsed seconds. Every record keeps model, endpoint, provider request ID, usage, monetary cost, and deterministic seed `null` with `unavailable_not_zero: true`; no unavailable monetary field is reinterpreted as `$0`.

All 29 remain pending human review, unaccepted, commercially uncleared, and non-reproducible. The only permitted reference hashes are `cb1e7b…b83d`, `c0a2be…b4a`, and `50f641…eb`; P036 remains composition-only and non-authoritative for hair identity. The three LitRPG candidates remain non-canon and were not re-uploaded as references. Final release, source, closeout, and review-link milestones perform no provider operation and do not change the built-in product's provenance-limited research status or create a commercial-use conclusion.

## Built-in ImageGen complete-chapter continuation — 2026-09-02

The complete-chapter run used the same OpenAI built-in ImageGen product and only the three previously authorized hash-pinned fictional-adult references. Eleven sequence outputs plus two targeted-repair outputs create 54 panel-level candidates through deterministic local cropping. There were 27 reference uses across the same three unique hashes. No new upload class, direct paid API, BFL call, alternate provider, cloud GPU, real likeness, private reference, LoRA, dataset, or child-related material was used.

The product again exposed no model snapshot, endpoint, provider request ID, usage, monetary cost, or deterministic seed. These values remain `null`/unavailable rather than inferred as zero. All art remains ignored, pending owner review, unaccepted, commercially uncleared, and non-reproducible. ADR-0171 and ComicStyleDirection r11 change the engineering workflow only; they do not create a license or commercial-use conclusion.

The P036 r4 continuation adds one built-in output and three authorized reference uses, including the P036 image solely for composition. Current totals are 14 outputs, 55 panel-level candidates, 30 uses of the same three unique hashes, and no new provider or upload class. ComicStyleDirection r12 and ADR-0172 make no license, rights, or commercial-use determination.

The P039/P043 r5 continuation adds one built-in strip, two deterministic panel crops, and two authorized reference uses. Current totals are 15 outputs, 57 panel-level candidates, and 32 uses of the same three unique hashes. The product metadata and commercial-use boundary are unchanged; ADR-0173 is a canon/provenance correction, not a rights decision.

The P029/P032 r6 continuation adds one built-in strip, two panel-level candidates, and two reference uses. Only P029 is assembled; P032 is diagnostic-only. Current totals are 16 outputs, 59 panel-level candidates, and 34 uses of the same three unique hashes. Freezing CH05 under ADR-0174 changes no provider, model, license, or commercial-use status.

The r6 release and chapter inventory add no service operation and change no license conclusion. All eight release images remain ignored local review evidence; model, endpoint, request IDs, usage, monetary cost, seed, reproducibility, commercial clearance, and exact-production-base status remain unavailable or pending exactly as recorded. ADR-0175 is a planning/provenance boundary, not a rights determination.

The cross-chapter regression reuses existing local pixels only. Its two derivatives do not alter the source images' mixed renderer provenance, review states, licenses, or commercial conclusions. ADR-0176 is a future-generation continuity rule and does not retroactively normalize historical provider metadata or rights.

The complete-chapter authoring contract/template is provider-neutral metadata with zero prompts, calls, uploads, or candidates. It grants no new model, license, commercial-use, or data-upload authority.

The semantic graph validator is local provider-neutral code. Its rejection of pre-promotion model/service/reference fields reinforces the existing license/upload boundary and creates no new authority.

Post-CH05 integrated release r1 performs no network-capable command and changes no provider, model, license, upload, or commercial-use conclusion.

The r6 owner pointer links existing ignored pixels only and changes no provider/model/license/commercial-use conclusion. Its explicit rights group remains unfilled.

The alternate-graphic preflight authorizes no new provider or data class. If executed, it is restricted to OpenAI built-in ImageGen and the same three exact fictional-adult reference hashes; model/endpoint/request ID/usage/cost/seed and commercial-use status remain unavailable or pending unless the product exposes them.
## Built-in ImageGen alternate-graphic and clear-line-watercolor continuation — 2026-09-02

The alternate-graphic run used only the OpenAI built-in ImageGen product and the three already-authorized exact fictional-adult reference hashes. It adds 11 outputs, 50 deterministic crops, and 23 reference uses. No BFL, direct paid API, alternate provider, real-person material, child-related material, private reference, LoRA, dataset, or new upload class was used. Model, endpoint, provider request ID, usage, monetary cost, deterministic seed, license grant, and commercial-use decision remain unavailable/open.

The next clear-line-watercolor full-chapter arm has the same exact product and reference boundary. Its preflight creates no execution or new rights conclusion. All outputs remain pending human review, unaccepted, commercially uncleared, non-reproducible, and not an exact production base.

The clear-line-watercolor arm was executed entirely through the same OpenAI built-in ImageGen product. It adds 11 outputs, 50 local deterministic crops, and 23 uses of only the three authorized hash-pinned fictional-adult references. No BFL, direct API, alternate provider, real-person or child-related material, private reference, training data, LoRA, model download, cloud GPU, or new upload class was used. The product still exposed no model snapshot, endpoint, provider request ID, usage, monetary cost, or deterministic seed. Those fields remain explicitly unavailable/null, and no license grant, commercial-use conclusion, acceptance, or exact-production-base status is inferred.
