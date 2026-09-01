# Renderer decision memo — 2026-09-01

## Recommendation

Keep the current shared production foundation. Reject further tuning of the current Illustrious/Xinsir and `legacy_duo3` configurations. Execute the already-defined **fictional-only, cross-provider G07 bakeoff** before selecting the next production renderer: Gemini 3.1 Flash Image and Grok Imagine Image 2.0 first; OpenAI GPT Image 2 and BFL FLUX.2 as comparable API arms; Qwen-Image-Edit-2511 only on appropriately sized, approved compute.

## Measured evidence

| Route | Established | Blocking evidence | Decision |
| --- | --- | --- | --- |
| Deterministic Blender geometry/proxy | Exact role-swapped placement, table/occlusion proxy, bit-identical local no-change | Not characters, art, or a renderer | Retain as spatial authority and control input |
| Legacy adult assets | One mechanically usable Soren plate | Sigrid has foreign furniture/prop leakage in 4/4; no usable G07 pair | Reject current asset route |
| FLUX.2 Klein | Coarse fictional composition/reference diagnostics | Global no-change drift; exact VAE is non-commercial | Diagnostic only |
| Illustrious XL v2 + Xinsir repaint | Exact deterministic exterior composite; 1/2 fictional target edit mechanics | Target no-change 0/2; one edit seed fails | Reject as reliable repair; retain evidence only |
| Qwen-Image-Edit-2511 (original BF16) | Official Apache-2.0 card, multi-image pipeline, claims relevant to multi-person consistency and editing | 53.75 GiB artifacts; 24 GiB local VRAM; no local evaluation yet | Best distinct hypothesis, capacity-gated |
| Qwen-Image-Edit-2511 (official Comfy INT8) | 28.07 GiB required download set; existing native-Comfy direction | Prescribed exact FP8 encoder comes from a current `tencent-hunyuan-community`-labeled repository; memory behavior and commercial composition unproven | Local-research candidate only; resolve dependency/license before acquisition |

The measured ledger is **82 local generations / 2,685.760 seconds / $0 external spend / 0 production-accepted experimental outputs**. The added `legacy_duo3` CH03 production-demo candidates each failed visual assertions: unrequested split-panel layout, wrong wardrobe, sexualized wardrobe, and/or role/prop/blocking failure. Timed human review remains unmeasured, so no accepted-panel-rate or labor-rate claim is justified.

## Required next experiment, after provider access

1. Use `experiments/renderer-bakeoffs/g07-fictional-bakeoff-r1.json` unchanged: two independent two-role renders, one target-change edit, and one paired no-change control per adapter.
2. Upload only the existing original fictional adult designs and geometry controls. Do not upload adult-likeness outputs, real-person/biometric imagery, or any child imagery.
3. Pin provider model/version where the API permits it. Otherwise retain the request ID, returned bytes, input hashes, response metadata, timing, cost, and human review/minutes; nondeterministic APIs are not locally seed-reproducible.
4. For Qwen, pin every artifact at its then-current official revision, record all LFS hashes/license artifacts/runtime/GPU/cost, and first resolve its compute profile.
5. Keep `experiments/benchmark-case-bundles/benchmark-case-bundle-v1.json` draft until adapter-specific controls and stage assets are complete. Do not report a Stage-A score or freeze the harness early.

## Execution gate

The protocol, assets, review forms, and adapter-neutral provenance contract are ready. Calls cannot yet be executed because this workspace has no configured provider credentials or funded managed-GPU account. To run all five arms, configure only the provider keys/accounts you choose to fund as local environment variables (never paste keys into a prompt), and set a total bakeoff spend cap. A **$20 initial cap** is recommended: it comfortably covers the four-request fictional protocol for the four API arms plus a limited retry allowance, while managed Qwen GPU time is separately provider-dependent.

OpenAI's current GPT Image 2 documentation confirms image-generation and image-edit endpoints plus a dated snapshot, but it does not expose a simple per-image price on the model page; record actual response usage/billing in its adapter rather than inventing an estimate. The model is unavailable on the free API tier. [Official model documentation](https://developers.openai.com/api/docs/models/gpt-image-2)

No adult likeness/reference material or child data is needed for the first evaluation. The official Comfy INT8 Qwen profile remains a local-research option only: its exact encoder license composition must be resolved before acquisition and it is not silently substituted for the Apache-2.0 original package.
