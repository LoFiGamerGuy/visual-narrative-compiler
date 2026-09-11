# A credible path to premium action webtoons

**Decision brief · 7 September 2026 · Sources checked 6–7 September in New York**

Keep Ember provisionally, rebuild the production method around directed sequences, and test a small number of renderers against the same original boards. Do not restart the story or invest in another large output run yet. The strongest route toward the owner's *Tower of God* / *Solo Leveling* craft bar combines deliberate staging, appealing character acting, controlled drawing and a correction process that preserves those decisions.

Astra is a useful upgrade for editorial reasoning, implementation and image-grounded review. It does not eliminate the need to test the drawing tools or to obtain real reader preference. The immediate implementation therefore makes the story contract, source provenance, correction budget and editable lettering explicit.

This report compares production mechanisms, not franchise imitation. No published comic pages were supplied to a generator. Features below are documented capabilities; “best next test” is our inference. None of the unrun alternatives is a demonstrated winner.

## What the implemented pilot found

The directed baseline has now produced 14 primary panels and nine permitted hard-failure corrections. Some edits fixed local mistakes, including an extra staff and missing room separation. Independent review still finds failures in the continuing sweep, exit direction and injury laterality. The route has not earned production, and exhausted panels receive no further generation. This result strengthens the case for a small structural-control or skilled drawing test; it does not establish an unrun renderer as the winner.

The [illustrated reader](reader/index.html), [nine correction pairs](corrections/index.html) and [implementation handoff](../../../research/sequence-pilot/START_HERE.md) preserve the actual result and final verification. Generated art remains local, ignored and unaccepted. Human comprehension and owner preference have not been measured.

## What the target actually requires

The prior completed repository audit found valid, distinct files that depicted the wrong cast, event or phase of combat. Those are failures of story-to-image selection and acceptance, even when the image is attractive. It also found stronger individual contact panels, so the existing renderer deserves a fair controlled baseline. See the [delivered audit](../anime-pipeline-total-review/reports/executive-decision.html) for that evidence; this research does not independently rescore it.

Premium craft is an interacting set of choices: adult character appeal, motivated expressions, clear staging, readable force, changing shot scale, quiet beats after spectacle, controlled values, persistent damage and props, and comfortable vertical reading. A different model can help some of these while weakening others.

There is direct professional support for treating this as a production discipline. REDICE director Jeong A-gyul describes adapting line weight for color and researching eye movement and choreography for vertical reading, alongside distinct planning, direction, drawing and editing responsibilities. This is a first-person account in a promotional interview, not a staffing or productivity benchmark. It supports purposeful direction and specialized work; it does not establish that a particular software stack guarantees comparable results. [Animate Times interview, January 2024](https://www.animatetimes.com/news/details.php?id=1703820882)

## The choices worth testing

| Route | Useful contribution | Principal unresolved problem | Recommendation |
|---|---|---|---|
| Current in-product generator, newly directed | Existing access; original references; instruction edits | Exact contact, state and spatial continuity; fused art repair | Keep as baseline A |
| Qwen Image Layered + conventional editing | RGBA decomposition and independent component changes | Useful semantic layers, reconstruction drift, hidden anatomy | Conditional component experiment |
| Blender layout + Krita or Clip Studio finishing | Repeatable room geometry, camera and editable correction | Drawing skill, acting, hand/face cleanup and setup effort | First structural alternative |
| NovelAI V5 Full | Anime-oriented composition, character positioning, native alpha | V5 identity-reference gap and exact interactions | First specialized renderer challenger |
| FLUX.2 | Multiple references and instruction-based structural guidance | Semantic guidance is not exact pose/contact constraint | General-purpose challenger |
| Qwen Image Edit / Qwen Image 3 APIs | Multi-reference edits or current managed generation | Different model families and access; exact sequence behavior | Alternative to FLUX, not another simultaneous full pilot |
| Skilled sequential artist + Clip Studio EX | Direct control of drawing, acting, corrections and lettering | Actual available skill, time and money | Strongest staffed conventional control |
| Krita + explicit SVG lettering | Editable local baseline without software license fees | More manual production coordination | Implementable finishing foundation |
| Niji 7 / Midjourney | Potentially useful anime design language and acting exploration | Version-specific controls, manual access, public-by-default terms | Manual concept trial first |
| Local fine-tuning / DiffSensei research | Reusable identity or explicit multi-character layout mechanisms | Training data, setup, overfitting and action flexibility | Defer until a measured bottleneck remains |

These ranks prioritize information gained per bounded experiment. They are not numerical quality rankings. The rest of the report explains which features actually coexist.

## Astra's role

Official OpenAI documentation describes GPT-6 Astra as a reasoning and tool-using model for complex work. It accepts image input and produces text; image generation is a supported tool capability. That distinction lets us use it to inspect art and drive a workflow without claiming it is the underlying raster model. The local model cache exposes `gpt-6-astra` with text/image inputs, and the session's agent tools expose the same option. [GPT-6 Astra model documentation](https://developers.openai.com/api/docs/models/gpt-6-astra)

Use Astra to challenge the script, plan action, translate boards into constrained prompts, compare observed images with required beats, and maintain the implementation. Keep its reviews labeled as AI observations. Two AI passes are not two independent human readers. An authoring model may also miss its own staging assumptions.

The official guide supports long, multistep tool workflows and explicitly discusses auditing skill instructions that can influence behavior. This makes a compact task contract and isolated review inputs sensible. The engineering change here is to make mistakes visible and reviewable, not to assume that a stronger model makes a semantic check infallible. [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model)

No paid Astra API migration is needed for this pilot. Published API rates are not a measure of this in-product session's incremental cost, and no API billing estimate is substituted for observed usage.

## Rendering and correction alternatives

### Keep the current route as a fair control

Keep the same story, boards, character specification, copy and attempt ceiling across challengers, while declaring each tool’s supported inputs and prompt translation. NovelAI V5 lacks the identity-reference mechanism available in other routes, so this is a comparison of supported production configurations rather than a pure renderer ablation. Historical audit outputs are context; their inputs, selection process and hidden model snapshot differ.

OpenAI's current image documentation offers generation and editing, while acknowledging continuing limitations in precise composition, recurring-character consistency and text. GPT Image 2 has its own documented model identity and API configuration; the built-in image tool used here does not expose a provider snapshot or seed in its response. Those fields remain null. [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation), [GPT Image 2 model](https://developers.openai.com/api/docs/models/gpt-image-2)

The falsifiable question is whether a newly directed version can depict the exact counter, reversal and consequence within one primary and one hard-failure correction. If it clears all hard gates, earns owner appeal and offers acceptable correction effort, retain it unless a challenger demonstrates worthwhile improvement. If it repeatedly cannot, more flattering style adjectives are unlikely to solve the missing control.

### Qwen Image Layered: test editability before adopting a drawing stack

Qwen Image Layered decomposes an image into RGBA layers and allows different layer counts. Its public repository uses Apache 2.0 and demonstrates image decomposition; it explicitly says prompts are not designed to control the semantic content of individual layers. Its recommended 640 resolution bucket makes full-size edge and recomposition checks material. A layer count alone is insufficient evidence of useful editability. [Official repository](https://github.com/QwenLM/Qwen-Image-Layered/blob/main/README.md), [research paper](https://arxiv.org/html/2512.15603v1)

Run this test only if the underlying art is appealing and the measured failure is local repair. If overall acting, faces or drawing appeal fail, obtain a three-panel drawing assessment first. Compare decomposition against direct masking/manual repair on the same tasks and total effort. Start with three original panels: overlapping hand and weapon, crossing actors, and a translucent effect. Compare the original with the initial recomposite before editing anything. Then move one actor, repair one hand and adjust the effect. Record which intended objects can be edited independently, whether previously hidden regions are plausible, whether untouched layers remain identical, and the actual correction time.

A consequential dependency trap appears in the repository's RGBA editing helper. It converts to a green-backed RGB image, edits through Qwen Image Edit and removes the background with BRIA RMBG-2.0. That is not a native lossless alpha-preserving operation. The BRIA weights have noncommercial terms unless separately licensed, despite the surrounding Qwen repository's Apache license. Begin with decomposition plus ordinary manual compositing; do not silently adopt that helper as a commercially unrestricted pipeline. [Helper source](https://github.com/QwenLM/Qwen-Image-Layered/blob/main/src/tool/edit_rgba_image.py), [BRIA model card](https://huggingface.co/briaai/RMBG-2.0)

This experiment tests correction locality, not whether Qwen draws a better comic. No model was downloaded or run during the research.

### NovelAI: separate V5 composition from V4.5 references

NovelAI V5 Full and Curated launched on August 21, 2026. The launch describes native transparency, freely positioned character prompts and multi-panel generation. Full has V5 inpainting; Curated's inpainting uses V4.5 Curated until its own implementation arrives. Native alpha can make an isolated character useful for compositing, but does not imply independently editable objects in a complete scene. [V5 launch](https://journal.novelai.net/image-generation-novelai-diffusion-v5-is-here-c2df7c6b8d2d/)

The important limitation is compatibility. Current Precise Reference documentation restricts it to V4.5 and says multiple character references blend together. Strong references can also preserve unwanted pose or expression. We must not combine V5's newer positioning and V4.5's reference feature in a fictional “best of both” configuration. [Precise Reference documentation](https://docs.novelai.net/en/image/precisereference/)

V5's free positioning is worth trying on the four action beats because separate character prompts can improve composition. Position controls still do not specify full skeletons or exact staff-to-foot contact. Test those relationships visually. [Multi-character prompting](https://docs.novelai.net/en/image/multiplecharacters/)

The FAQ lists $10/$15/$25 monthly plans and a registered image trial, but exact V5/control eligibility for that trial was not established. Existing account access is unknown. Save through the product's download function to preserve settings metadata; clipboard saves omit it. No purchase or account creation occurred, and no supported image API contract was established for an automated adapter. [NovelAI FAQ](https://docs.novelai.net/en/faq/)

### FLUX.2: useful references, qualified structural control

FLUX.2 documents multi-reference editing and image-based pose, depth or edge guidance. Its own structural-control guide says the model interprets those guides semantically rather than behaving like a dedicated pixel-exact ControlNet. This matters when a hand must grip a particular staff segment or a foot must meet a precise contact point. [FLUX.2 editing](https://docs.bfl.ai/flux_2/flux2_image_editing), [structural guidance](https://docs.bfl.ai/guides/usecases_editing_controlnets)

A fair comparison would use the same boards and character specification as route A, recording the supported conditioning inputs and renderer-specific prompt translation. Freeze an available model version rather than a mutable preview where possible. Preserve the actual input references, returned dimensions and correction attempts.

For local adaptation, the official Klein training guide distinguishes a 4B Apache-licensed base from a 9B base with noncommercial terms. Its hardware guidance lists 12 GB VRAM / 32 GB RAM for 4B training and 22 GB / 64 GB for 9B. The local GPU reports 24,463 MiB; this makes some small-model work plausible, not measured feasible performance. Available system RAM, training time and output quality were not tested. [Klein training guide](https://docs.bfl.ai/flux_2/flux2_klein_training)

Do not start a new integration around old FLUX.1 Depth/Canny simply because earlier tutorials recommend it: the current vendor page marks those tools deprecated for new integrations. Likewise, the FLUX.3 page describes image/open-weight availability as forthcoming; a promise is not an available still-image tool. [FLUX.1 tools notice](https://bfl.ai/blog/24-11-21-tools), [FLUX.3 page](https://bfl.ai/models/flux-3)

### Qwen editing and managed APIs: keep family and region explicit

Qwen Image Edit 2511 is an Apache-licensed open model with documented multi-image editing and examples of improved identity and geometry. Those demonstrations warrant a controlled comparison, not a sustained-sequence claim. [Official model card](https://huggingface.co/Qwen/Qwen-Image-Edit-2511)

Alibaba's updated September 2, 2026 API documentation also covers Qwen Image 3.0 / 3.0 Pro. It specifies model-dependent reference limits, output constraints and region-matched endpoints/credentials; returned image URLs expire. This managed generation route is distinct from running the older editing weights locally. Preserve downloaded originals and request metadata if a future paid experiment is authorized. [Current API reference](https://www.alibabacloud.com/help/en/model-studio/qwen-image-generation-and-editing-api-reference)

The pricing page has region-specific tables. Singapore international prices include standard 3.0 output at $0.03 and Pro at $0.04 for 1K / $0.075 for 2K, with reference-input charges where applicable. Those are listed component prices, not all-in panel costs or a guaranteed free quota. Account entitlement and eventual correction yield remain unknown. [Model pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing)

Choose either this route or FLUX for the first general-purpose challenger. Running many loosely controlled full sequences would obscure the causal comparison and recreate the abandoned experiment sprawl.

### Niji and Midjourney: useful manual exploration, no invented integration

Niji 7 is the anime-focused line; general Midjourney's current default is V8.2. The four-reference Edit Model documentation applies to V8.1/V8.2, and did not establish Niji 7 compatibility. An image made in Niji and edited in V8 is a mixed-model route that should be recorded explicitly. [Version documentation](https://docs.midjourney.com/hc/en-us/articles/32199405667853-Version), [Edit Model](https://docs.midjourney.com/hc/en-us/articles/48495453462797-Edit-Model)

The May 27, 2026 terms prohibit automated service access/generation and make content public/remixable by default. Consequently, do not build an unofficial generation bot. A manually operated style or acting trial could still be useful if the owner accepts the applicable terms. [Midjourney terms](https://docs.midjourney.com/hc/en-us/articles/32083055291277-Terms-of-Service)

Monthly plans are listed at $10/$30/$60/$120; Stealth is limited to Pro/Mega. A $10 subscription is therefore not a private production workflow. Existing subscription status is unknown and no purchase occurred. [Plan comparison](https://docs.midjourney.com/hc/en-us/articles/27870484040333-Comparing-Midjourney-Plans)

## Conventional production routes

### A skilled artist with Clip Studio is the strongest staffed control

Clip Studio offers panels, balloons, perspective rulers, 3D support and comic page management. Its webtoon tools provide smartphone-area preview and vertical export slicing, while EX adds relevant multi-page operations. These are practical production capabilities, not automatic artistic judgment. [Comic features](https://www.clipstudio.net/en/comics-manga/), [Webtoon manual](https://help.clip-studio.com/en-us/manual_en/540_comic/Webtoons.htm)

The most credible conventional test is a skilled sequential artist finishing the same anticipation/contact/aftermath boards, with one requested correction and delivery of editable sources. Measure whether the acting, force and continuity become better, and what the intervention actually costs. No skilled human labor is currently booked; the optional human route remains unrun.

Clip Studio's LT conversion can turn 3D or photographic material into line/tone components, but still requires cleanup and style integration. Asset formats can transfer geometry into the application; they do not guarantee preservation of Blender rigs, cameras or shader meaning. [LT conversion guide](https://tips.clip-studio.com/en-us/articles/1261), [3D import manual](https://help.clip-studio.com/en-us/manual_en/660_3d/Importing_3D_Files.htm)

Before buying assets, read the actual asset license. The August 19, 2026 terms allow commercial creative use subject to applicable conditions and restrict extractable-source redistribution; limited licenses can override the general terms. The marketplace's prohibition on submitting AI-generated assets is a separate policy, not a blanket ban on editing generated work in Clip Studio. [Asset terms](https://assets.clip-studio.com/en-us/information/terms/detail), [Asset policy](https://assets.clip-studio.com/en-us/information/policy)

### Start Blender with a room and three cameras

Blender's Grease Pencil supports editable 2D strokes in a 3D scene. That is valuable for repeatable space and camera choices. It does not supply expressive anatomy or good action poses by itself. [Blender Story Artist](https://www.blender.org/features/story-artist/)

Build only the pilot gallery, ridge, shutter and cable, then frame the establishing view, contact and escape. Use these as layout guides for drawn or generated finishing. Compare preparation time and geography errors against the current board-only route. A full toon-character rig is a later investment if this small test earns its complexity.

Interoperability needs a version-pinned round trip. Grease Pencil and SVG export behavior changes across releases; toon shader techniques also have render-engine limitations. Do not promise editable equivalence across Blender, SVG and a painting application. Blender itself permits commercial artwork, while imported assets retain their own licenses. [Grease Pencil release notes](https://developer.blender.org/docs/release_notes/5.0/grease_pencil/), [Shader to RGB manual](https://docs.blender.org/manual/en/dev/render/shader_nodes/color/shader_to_rgb.html), [Blender license](https://www.blender.org/about/license/)

### Krita plus SVG is a credible finishing baseline

Krita supplies raster layers and vector shapes/text without a software license fee. Its manual warns that PSD interoperability is incomplete. Prefer native KRA working files, explicit image exports and a separately editable SVG lettering layer, then test the actual receiving application. [Vector layers](https://docs.krita.org/en/reference_manual/layers_and_masks/vector_layers.html), [PSD limitations](https://docs.krita.org/en/general_concepts/file_formats/file_psd.html), [Krita license](https://krita.org/en/about/license/)

The implementation starts with live browser/SVG lettering because the existing failure was visible at the reading surface. Explicit text lines, measured glyph bounds, correctly attributed tails and image-observed exclusion regions are more useful than a wrapper around a fused raster. Synthetic copy expansion is a layout diagnostic; it is not qualified translation review.

No local Blender, Krita or Inkscape executable was found on the current shell path. Windows installations and human proficiency were not established. “Free software” must not be confused with free skilled finishing.

## Research architectures and misleading benchmarks

DiffSensei is useful architectural evidence for combining character conditioning with explicit layout and dialogue-region controls. Its paper also reports problems with unclear references and character fusion. The research is not a demonstrated premium full-color production stack; repository/model licensing does not establish clearance for all training material. [DiffSensei paper](https://arxiv.org/html/2412.07589v2), [official repository](https://github.com/jianzongwu/DiffSensei)

ViStoryBench separates character identity, prompt compliance, style and other sequence dimensions. Its copy-paste counterexample is relevant: repeating a recognizable character can improve some metrics while failing the requested action. Its model results concern its evaluated 2025 configurations, not a 2026 ranking of every tool discussed here. [ViStoryBench paper](https://arxiv.org/html/2505.24862v2)

Fine-tuning should wait until approved original assets demonstrate the identity range we actually want: profile, strong expression, occlusion, shared action and injury. Training too early may stabilize a stiff or unwanted design. The right question is whether it reduces accepted-panel correction effort without suppressing pose and acting flexibility.

## Experiments that will change the decision

| Test | Frozen inputs | Evidence to retain | Decision |
|---|---|---|---|
| Directed baseline A | All 14 original beats, boards, copy and references | Every attempt, actual source, semantic observations, phone lettering | Determine whether the newly directed current route meets the predeclared gates |
| One renderer challenger | P06 anticipation, P08 counter, P09 reversal, P12 impact; same references and copy | Exact version/controls, wrong actors/contact/state, correction minutes | Expand to 14 only if it fixes the baseline's bottleneck |
| Layer correction | Three original overlap/effect panels | Initial recomposite, editable components, unchanged-layer hashes, correction time | Adopt only where it reduces repair burden without visible drift |
| Room/camera control | One gallery and three views | Geometry, camera files, finished comparisons, setup time | Keep only if reuse or geography improvement earns setup |
| Human finishing | Same three action boards and one correction | Native layers, actual labor, blinded reader reasons | Staff this route only when measured gain justifies capacity |

The four generated action panels are a screening test, not proof of sequence quality: they omit the attack, skill application and aftermath. Show them inside identical unchanged contextual boards, and score generated-panel fidelity separately from comprehension. A promising configuration must still complete the frozen 14-panel sequence. Register future NovelAI/FLUX trials as new predeclared follow-up experiments; do not relabel the existing A/B/C routes or reset their spent budgets.

Use one primary and one targeted hard-failure retry per panel, no beauty-variant search. Freeze grouping before calls so a failed group cannot be split into a fresh budget. Apply the same absolute actor, event, contact, state and readability gates to every route.

The full pilot still requires two independent human readers and an owner decision. The prior specification's score margins are conservative project rules, not market-calibrated statistical thresholds. Passing an AI review or compiling the reader does not authorize a serial. If A is compelling and ties a more complicated route, keep the simpler route.

## Cleanup and the next production decision

The practical cleanup is to establish one active pilot workspace and a clear registry of preserved experiments. Keep story/world records, source provenance, useful export infrastructure and the forensic audit. Stop using preset “quality” scores as evidence of a panel's event, and stop selecting inherited plates merely because their tags resemble the script.

Keep the old branches and art caches intact. Archive their status in the navigation rather than deleting them. Do not merge a large experimental branch wholesale. Once the pilot's implementation is reviewed, integrate only the small reusable package and the chosen workflow. A fresh story should be tested only after competent execution of a bounded Ember opening still fails to create interest.

The remaining uncertainties are empirical: owner appeal, actual sustained drawing quality, correction labor, available artists and destination requirements. More vendor pages will not resolve those. The next useful work is the bounded sequence, one focused challenger and honest reader response.

## Evidence and limits

Two independent research lanes covered rendering/control and conventional production; the lead reconciled version mismatches and re-opened consequential primary sources, including Astra modality, NovelAI reference compatibility, Midjourney automation terms, Qwen layered-helper dependencies and Clip Studio asset terms. Sources were accessed September 7, 2026 UTC. Undated live documentation has no invented publication date.

The comparison includes official documentation, model cards, public source code, research papers and a first-person studio interview. Vendor examples are feature evidence, not independent quality validation. No public comic art was redistributed, no paid API or subscription was used, no model/dataset was downloaded and no human labor was hired for this research.

The [implementation reader](reader/index.html) and [pilot handoff](../../../research/sequence-pilot/START_HERE.md) report what was actually built and observed. Alternative-route tests described in this report remain unrun unless explicitly identified there.
