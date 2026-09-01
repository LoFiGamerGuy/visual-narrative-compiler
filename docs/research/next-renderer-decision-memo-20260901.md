# Next renderer decision memo — 2026-09-01

## Measured position

The local FLUX.2 Klein reference adapter passes the latest neutral-token, shared-table paired smoke (2/2 at one paired seed) but fails its Blender-control no-change test: 99.986% of decoded pixels change across the frame. Its exact pinned VAE is non-commercial. The legacy stack has no reusable two-adult actor-asset route, and `baseline_legacy` remains frozen.

Existing 6.9 GB SDXL checkpoints cannot substitute for a new arm: NoobAI is blocked from the commercial pipeline, and `hyphoria`/`novaAnimeXL` have no reconstructable upstream license provenance. They remain quarantined.

## Ranked decision

| Rank | Option | Information gained | Effort/risk | Recommendation |
| --- | --- | --- | --- | --- |
| 1 | Download Illustrious XL v2.0 from its official repository | Tests a comic-native SDXL arm with the already present SDXL-style spatial controls; creates a clean baseline for masked locality and fictional-design role binding | Requires checkpoint download and a new pinned profile; CreativeML OpenRAIL-M constraints must be recorded | Approve first |
| 2 | Download Qwen Image Edit 2511 from its official repository | Direct multi-image and editability test for group role binding/repair | Official card identifies a 20B BF16 model; local 24 GB feasibility is unproven and integration is materially larger | Defer until after Illustrious failure profile, or approve as a separate feasibility track |
| 3 | Continue FLUX.2 Klein samples | More composition-diagnostic variance data | Repeats known full-frame no-change drift; exact profile is non-commercial | Do not prioritize |

## Acquisition provenance already pinned

Illustrious's official API revision is `69459c1fe6f46db41ab31e6114f05acc0e06bcaa`; its revision-pinned README SHA-256 is `f06d16269c0f09e5d8cca9ff406f48c0ac484d0884f458e37f73f0fc9995092f` and declares `creativeml-openrail-m`. Qwen's corresponding revision is `6f3ccc0b56e431dc6a0c2b2039706d7d26f22cb9`, README SHA-256 `9724c194bef2a6d821090f0cd65774962e8f77e3acbfb2a7cbbdd58c92049902`, and declared license Apache-2.0. These were read-only primary-source checks; no weights were fetched.

## Proposed first Illustrious experiment

Fictional/neutral controls only: one G07a/G07b paired seed plus one renderer no-change control, using the r2 Blender stage bundle. No adult image, adult LoRA, child data, cloud service, or commercial claim. Record file and license hashes, Comfy node versions, candidate hashes, timing, reviewer status/minutes, and all assertion decisions.

## Authority needed

Authorize the Illustrious XL v2.0 checkpoint download from the official source. Qwen remains a separately gated option; no provider upload or paid service is proposed.
