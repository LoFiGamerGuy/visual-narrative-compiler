# Qwen-Image-Edit-2511 official Comfy INT8 route — 2026-09-01

## Status

`RESEARCH_PROFILE_CANDIDATE_NOT_ACQUIRED_LICENSE_COMPOSITION_UNRESOLVED`

This is a materially different execution option from the original Diffusers BF16 package. It is **not** yet selected, downloaded, or approved for commercial work.

## Current primary-source facts

ComfyUI's current official INT8 workflow template names these required files:

| Component | Official source / revision | Exact remote hash | Size | License evidence | Status |
| --- | --- | --- | ---: | --- | --- |
| INT8 diffusion model | `Comfy-Org/Qwen-Image-Edit_ComfyUI` revision `984166f60a9b1fcede5e9b9287b7a7aebc050010` | `11b5af5ac601821d73930c84846c9a158e67177356daf927ce1c8d10f3963829` | 20,499,083,824 bytes / 19.09 GiB | Repository card declares Apache-2.0 | Candidate; not acquired |
| Qwen 2.5 VL 7B FP8 text encoder | `Comfy-Org/HunyuanVideo_1.5_repackaged` revision `144e6ea259230936cdc6f140b3fe69c8529b5c47` | `cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4` | 9,384,670,680 bytes / 8.74 GiB | Repository card currently declares `tencent-hunyuan-community` | Territory-limited/conditional dependency; do not infer Apache-2.0 |
| Qwen Image VAE | `Comfy-Org/Qwen-Image_ComfyUI` revision `7beb7b647f04469fbe64ba8adc2bb0d7e5e9f73f` | `a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f` | 253,806,246 bytes / 0.24 GiB | Repository card declares Apache-2.0 | Exact local file already present |

The required download set is at least 30,137,560,750 bytes / 28.07 GiB, excluding optional Lightning LoRA. The current local ComfyUI checkout already contains the official BF16 Qwen-2511 blueprint and native Qwen support, but the newer INT8 template requires the current template/core contract to be checked at acquisition time.

## Decision

Do not acquire the INT8 profile automatically. It is the best local-footprint Qwen path found so far, but its prescribed text-encoder artifact carries a different current repository license label from the Apache-2.0 Qwen/Comfy model artifacts. Tencent's current primary Hunyuan license is limited to the defined Territory (excluding EU, UK, and South Korea), has distribution/notice conditions, restricts use of outputs to improve other AI models, and requires a separate license above 100M MAU. A commercial-profile decision must resolve that exact dependency and the intended distribution territory, or use an exact Apache-provenanced alternative. For local fictional research, any acquisition is still a large-download choice among plausible variants and requires explicit selection.

## Implications for the first smoke

If selected as local-only research, use only the existing neutral Blender G07 controls. Record all three hashes above, exact Comfy commit/template hash, the loader's memory-management behavior, peak VRAM, wall time, candidates, assertion review, and no-change/injection controls. A successful local render would not resolve commercial dependency status.
