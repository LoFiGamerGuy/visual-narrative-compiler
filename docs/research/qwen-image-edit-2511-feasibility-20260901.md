# Qwen-Image-Edit-2511 pre-acquisition feasibility — 2026-09-01

## Decision

Defer acquisition. Qwen-Image-Edit-2511 is a high-information future renderer candidate for fictional multi-reference role binding and targeted repair, but the official BF16 artifact set is too large for the currently available 24 GiB GPU before inference working memory. No model files, cloud service, paid compute, or personal-reference upload were used in this decision.

## Primary-source pin

- Official repository: `Qwen/Qwen-Image-Edit-2511`, revision `6f3ccc0b56e431dc6a0c2b2039706d7d26f22cb9` (queried 2026-09-01).
- Revision-pinned `README.md`: SHA-256 `9724c194bef2a6d821090f0cd65774962e8f77e3acbfb2a7cbbdd58c92049902`; the model card declares Apache-2.0, BF16, 20B parameters, `QwenImageEditPlusPipeline`, and a two-image example.
- Official repository API lists 11 LFS safetensors totaling 57,710,671,694 bytes (53.75 GiB). The text encoder alone is 16.31 GiB; the transformer is 38.97 GiB; the VAE is 0.24 GiB. Exact upstream LFS hashes must be rechecked and recorded at acquisition time.

## Local evidence

- GPU: NVIDIA GeForce RTX 5090 Laptop GPU, 24,463 MiB VRAM; driver 616.56.
- ComfyUI commit: `82f839f5e737d8bfce480872ba05e5a430f2526f`; embedded environment: PyTorch `2.12.0.dev20260408+cu128`, CUDA 12.8, GPU available.
- The same environment has `transformers`, but no `diffusers` or `accelerate`. The system drive has 327.78 GiB free, so disk capacity is not the gating resource.

The official quick-start loads the pipeline in BF16 and transfers it to CUDA. It does not establish that offload, quantization, or 24 GiB execution is supported for this project configuration. Treating an unverified workaround as a baseline would reduce rather than increase information quality.

## Future fictional-control protocol

Before any acquisition, create a dedicated render profile and adapter-specific `BenchmarkCaseBundle` draft using only the existing neutral geometry controls:

1. Hash every acquired source artifact and record the exact revision, license artifact, Diffusers/Transformers/Accelerate versions, GPU, workflow, seed, and runtime.
2. Run G07a/G07b paired role-order controls at two seeds against the neutral Blender stage; preserve their declared grounded semantic intent and proxy limitations.
3. Run an unchanged-target control and the existing role-swap/duplicate/missing derived injections. Target no-change and exterior continuity must be independently measured.
4. Use `production/comic/hard-assertion-manifests/g07-fictional-proxy-v1.json` for intent and create separate RenderRecord/review records. No result becomes a Stage-A score until its executable bundle is versioned, controls are calibrated, and limitations remain explicit.

## Gate

The next action requires a deliberate execution-capacity choice: a suitably sized local GPU, an approved quantized/offload profile with primary implementation documentation, or paid/cloud compute. The project must not upload adult likeness/reference material; initial Qwen controls remain fictional geometry only.
