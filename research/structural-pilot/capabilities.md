# Capabilities used for SC-20260907-01

Measured September 7, 2026 UTC. Direct paid API, cloud GPU, subscription, asset-store and hired-labor spending is $0. In-product billing allocation remains unknown.

- Existing Windows Blender executable runs through WSL: `tools/blender/blender-5.2.1/blender-5.2.1-windows-x64/blender.exe` in the protected root. Read-only version probe returned Blender 5.2.1 LTS, build `9e2066aef7ef`. New scenes, settings, renders and temporary files belong to this isolated worktree.
- The session exposes built-in image generation with text instructions and local reference images. Actual provider snapshot, seed and usage are not exposed. The reasoning agents use GPT-6 Astra; that is not a claim about the raster model.
- A task-owned Python environment at `research/structural-pilot/.scratch/venv` has Pillow 12.3.0, installed from an existing cached 6.9MB wheel. It is used for authorized deterministic compositing and measurements, not a substitute image-generation API.
- Existing cached Chromium runs with the prior review's read-only shared-library directory. A new browser profile lives in this worktree, CDP port 9347 for lead inspection. Prior browser processes and profiles are preserved.
- No NovelAI tool is exposed in this session. Existing account/subscription access is unknown; no account creation, credentials search, subscription purchase or unsupported adapter was attempted. A full-frame finishing call through the available in-product tool is the focused challenger to fixed scene layers.
- Read-only probes of `127.0.0.1:8188/system_stats` and `:8189/system_stats` did not connect. This establishes only that those two local ComfyUI endpoints were unavailable; it does not prove absence of other local installations.

Only consequential compatibility documentation was rechecked; the prior broad research was reused. [NovelAI Precise Reference documentation](https://docs.novelai.net/en/image/precisereference/) still restricts that feature to V4.5 and warns that multiple character references blend. [Multi-character prompting](https://docs.novelai.net/en/image/multiplecharacters/) separately documents V5 character positioning. Neither establishes an available authenticated V5 configuration here. Both accessed September 7, 2026 UTC; live documentation has no invented publication date.

The attempted current Blender API documentation URL returned an internal error through web access. Implementation uses the installed Blender API and actual render probes; no API compatibility is inferred from the failed fetch. No models or datasets were downloaded.
