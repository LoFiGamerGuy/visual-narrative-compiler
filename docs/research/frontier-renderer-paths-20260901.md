# Frontier and managed renderer paths: initial evidence review

Date: 2026-09-01.  This is an evidence review, not authorization to open an account, spend funds, upload any personal data, or call an API.  Every external candidate would be an execution adapter; canon, `ComicPanelPlan`, assertions, and `RenderRecord` remain local source-of-truth artifacts.

## Decision

Run a small, fictional-only, adapter-normalized bakeoff before selecting a production renderer.  The first recommended cloud candidate is **Gemini 3.1 Flash Image** for the measured smoke arm, with **Grok Imagine Image 2.0** as the parallel visual/editing comparator.  Keep original Apache-2.0 Qwen Image Edit 2511 as the local/managed-GPU reproducibility arm.  Do not use consumer chat/playground products for personal references.

This is not an assertion that any candidate is commercial-release ready.  Rights, current service terms, output restrictions, and the intended distribution need a separate dated gate before production release.

## What each path can answer

| Path | Current primary evidence | Best uncertainty resolved | Important limitation |
| --- | --- | --- | --- |
| Gemini 3.1 Flash Image API | Official guide supports image editing, multi-turn iteration, and up to four character-consistency references / ten object references; paid Gemini API inputs and outputs are not used to improve Google products. | Can a reference-heavy frontier model bind two fictional adult roles while retaining a staged set and accepting a no-change control? | API behavior is not seed-reproducible in the local-renderer sense; outputs carry SynthID. Paid-service safety logging remains documented. |
| Gemini 3 Pro Image API | Official guide supports up to five character references, three style references, and 4K output; positioned by Google for complex professional asset production. | Whether higher-capability reference composition materially improves difficult multi-character comic panels. | Higher anticipated cost/latency; use only after the Flash smoke has a measured failure reason. |
| Grok Imagine Image 2.0 API | Official API docs support natural-language image editing and multi-image editing with up to five source images. xAI's current docs state generated media is not used for training and describe regional processing. | Whether its edit/compositing mechanism produces a visibly stronger, repairable illustrated panel from the same controls. | The public current page does not establish deterministic seed control; retain request IDs, all inputs, prompts, response metadata, and returned bytes instead. Consumer Grok is not an adult-reference route. |
| OpenAI GPT Image 2 API | Official model page exposes image generation/edit endpoints, high-fidelity image inputs, and a dated snapshot. API inputs/outputs are not used to train models by default. | An API renderer with a snapshot-pinnable model and output usage in the response; useful as a separate controlled edit arm. | Reference-count/role-binding limits require direct smoke evidence; API billing and data-retention configuration are separate gates. |
| BFL FLUX.2 API | BFL's current docs recommend FLUX.2 for multi-reference editing (up to ten images), with up to 4MP output. | Whether commercial hosted FLUX.2 solves the local FLUX non-change drift without changing spatial assets. | Current commercial terms/data handling and exact model/version pinning must be fetched before any call; do not infer them from local FLUX artifact licenses. |
| Qwen Image Edit 2511, managed GPU | Original model card/license is Apache-2.0 and its multi-image edit capability is source-pinned in the registry. | Whether a self-controlled, reproducible multi-reference renderer can outperform the legacy sequential repair arm. | Requires a chosen paid GPU provider and 53.75 GiB BF16 artifact acquisition, or a separately reviewed quantized profile. |

## Common first bakeoff: fictional G07 only

Use the existing draft adapter-specific G07a/G07b control assets and `HardAssertionManifest`; do not alter the semantic gauntlet or claim grounded-stage evidence where the input is a legacy 2D plate.

For each remote adapter, make exactly these initial requests, if/when a funded account and service gate are approved:

1. two independent P07-compatible two-fictional-adult renders from the same staged controls;
2. one target-change edit; and
3. one paired no-change edit using the same source/control image and an explicit preservation prompt.

The record must retain the immutable local source bytes/hashes, declared input order and role map, full request body excluding secret, provider/model/version/region, request ID, timestamps, response bytes/hash, cost/usage, and human-review minutes.  A provider's internal request ID is provenance, not reproducibility.  The reviewer applies the same hard assertions and failure-tag taxonomy already used locally.

Exit condition: one compact cross-adapter table shows role binding, identity/wardrobe behavior, set continuity, target change, non-target change, failure tags, elapsed time, recorded cost, and reviewer decision.  A visually appealing result that fails the no-change or role assertion is a rejected benchmark result, not a selected pipeline.

## Data and safety gate

Initial remote requests may contain only fictional adult character designs, original neutral set proxies, and non-sensitive prompts.  They must contain no child imagery or child-like character references, no real-person/biometric image, and no adult-likeness LoRA output used as an identity reference.  The consumer Grok website/apps are excluded for sensitive material; their own FAQ says generated media includes a watermark and consumer data terms differ from API/enterprise controls.

Before any eventual adult-reference use, record the exact product/plan/endpoint, current primary privacy/terms artifacts, retention/data-residency configuration, consent provenance, and a specific approval.  A paid API's no-training statement alone is not approval to upload a likeness.

## Ranked next actions

1. **Gemini 3.1 Flash Image fictional G07 bakeoff** — highest expected information gain for role binding/reference conditioning; low integration effort.  Requires a paid Gemini API Cloud project and a deliberately small spend cap.
2. **Grok Imagine Image 2.0 fictional G07 bakeoff** — parallel creative/editing comparator; official image pricing currently lists $0.04 at 1K low output plus $0.01/image input, so the four-request protocol has a transparent small direct media cost before taxes/other account charges.
3. **Qwen Image Edit 2511 managed-GPU profile selection** — strongest reproducibility and model-agnostic-adapter evidence, but larger setup/download effort.  Compare a 48–80 GiB short-lived GPU rental against the prepared local offload profile only after pricing, retention, and region are recorded.

## Primary sources checked 2026-09-01

- [Google Gemini image-generation guide](https://ai.google.dev/gemini-api/docs/image-generation): editing, reference capacity, sequential-art guidance, model selection, and SynthID.
- [Google Gemini API additional terms](https://ai.google.dev/gemini-api/terms): paid-service data handling; unpaid quota/AI Studio must not receive sensitive data.
- [xAI Grok Imagine API](https://x.ai/api/imagine), [Imagine capability guide](https://docs.x.ai/developers/model-capabilities/imagine), and [xAI pricing](https://docs.x.ai/developers/pricing): API modalities, multi-image edits, pricing, and stated security posture.
- [OpenAI GPT Image 2 model page](https://developers.openai.com/api/docs/models/gpt-image-2) and [OpenAI business-data privacy](https://openai.com/business-data/): image endpoints/snapshot and API data-use default.
- [BFL FLUX image-editing guide](https://docs.bfl.ai/kontext/kontext_image_editing): FLUX.2 multi-reference and output-capability claim.

The documents above are live policy/documentation pages, not frozen model artifacts.  Re-fetch and archive current primary terms before a commercial or personal-data decision.
