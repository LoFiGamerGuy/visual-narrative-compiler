# Phase 1 gap analysis

Date: 2026-08-31. Evidence is local code/logs unless marked otherwise.

## What exists

- A working legacy Anima/ComfyUI renderer is represented by `garden/gen.py`, `gen2.py`, and `gen3.py`; logged generations complete in about 20-37 seconds at 42 steps on the local RTX 5090 Laptop GPU. ComfyUI is currently stopped, so this is historical reproducibility evidence, not a live green check.
- `garden/canon.py` centralizes prompt strings and timeline wardrobe variants; `garden/rooms_def.py` plus `stage.py` provide calibrated 2D plate geometry and foreground-occluder compositing.
- The legacy renderer has two explicit two-person approaches: regional text conditioning (`gen3.py`) and plate compositing (`panelcomp.py`, `make_page01.py` through `make_page03.py`). Its own source correctly notes that regional conditioning does not regionally mask global LoRA weights.
- Deterministic Pillow-based lettering/page-previz code exists in `garden-work/northgarden/strip/`; code-driven VFX exists in `garden/voidfx.py`.
- Two adult identity LoRAs exist and their train configs/checkpoints are local. Training/reference images are sensitive and remain unmodified.
- ComfyUI is pinned locally at `82f839f5e737d8bfce480872ba05e5a430f2526f`; custom nodes are installed. There are no discovered InsightFace weight directories, although IPAdapter's installed examples include FaceID workflows.
- The v2.1.1 research package validates locally: 40 renderer cases, 24 Stage-A generations, 120 Stage-B generations per finalist, 12 QA controls, 8 injected QA cases, `0 failures, 0 warnings`.

## Missing or not yet evidenced

| Target capability | Gap | Phase 1 response |
| --- | --- | --- |
| Source-of-truth production state | Canon is Python prose/prompt state, not versioned domain records | Add narrow versioned static-path records; do not rewrite legacy canon. |
| Intent/provenance split | Current job JSON mixes prompts, seeds, and execution inputs; no RenderRecord | Wrap legacy execution and emit immutable attempt records. |
| Benchmark harness | Frozen semantics exist, but no adapter-specific control/stage bundle | Build `BenchmarkCaseBundle v1` only after baseline adapter mapping is explicit. |
| Stage A | No baseline benchmark result history | Run the frozen 12-case/two-seed subset without tuning. |
| QA | No HardAssertionManifest resolution or measured QA history | Deterministic assertion/review records first; VLM remains non-gating. |
| Revisions/publication | Output folders and filenames are mutable/implicit | Add edition and revision manifests before publishing new material. |
| License/policy registry | Local files lack source/license/hash records | Inventory weights and block uncertain/restricted artifacts from commercial profiles. |
| Canonical 3D | Current calibrated plates are useful 2D staging but not canonical 3D sets | Preserve them as a legacy stage adapter; do not call them Blender authority. |
| Instrumented production | Existing outputs/logs lack acceptance, human-minutes, or complete provenance | Record the next real narrative sequence through `baseline_legacy`. |
| Chapter-scale current script | A historical 52+44-panel Garden's Anchor pilot exists, but its stated total is inconsistent and its Dio/Thal/photo-derived design history conflicts with current Soren/Sigrid records | ADR-0022 quarantines it; require an owner-approved adaptation/mapping and clean fictional-design basis, or a newly authored current chapter script, before import. |

## Known risks and blocked assumptions

- The active legacy Anima base and adult LoRAs have not yet been given primary-source commercial license records. They may be used only as an internal baseline until reviewed.
- `JANKUTrainedChenkinNoobai_v777.safetensors` and the similarly named NoobAI ControlNet are blocked from commercial pipeline profiles pending independent provenance; the official NoobAI model card explicitly prohibits commercialization of the model, derivatives, and generated products.
- The local Comfy API is down. Starting the existing local service is a normal reproducibility step; no model download or external upload is needed.
- The semantic gauntlet is frozen, but treating it as a fully comparable grounded benchmark before stage/control assets are versioned would be invalid. Baseline attempts must state their legacy-stage limitations.
