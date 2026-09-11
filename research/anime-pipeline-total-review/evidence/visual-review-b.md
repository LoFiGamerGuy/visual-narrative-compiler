# Independent visual and lettering review B

This is an independent **AI task pass**, not independent human validation. I read the complete owner prompt and frozen rubric before scoring. I did not read the lead's scores, recommendation, or previous aesthetic ratings. I used pipeline inventory identifiers only to map observations. Scores reflect selective direct inspection, not a professional-market percentile or owner preference prediction.

Individual 0–5 dimension judgments, confidence, evidence and non-assessed fields are in [subjective-scores-b.json](subjective-scores-b.json). All six rubric categories appear for every inventory identifier. Category means follow individual dimensions in that file; no weighted total is calculated. Architecture/control experiments with insufficient finished-reader evidence receive nulls, not flattering proxy scores or punitive art scores.

## Inspection and coverage

Protected roots used below:

- `R`: `/mnt/c/AgentWorkspaces/anime-pipeline`
- `B`: `/mnt/c/AgentWorkspaces/anime-pipeline-reimagining-20260903`
- `C`: `/mnt/c/AgentWorkspaces/anime-pipeline-reimagining-clean-webtoon-20260903-213010`
- `E`: `/mnt/c/AgentWorkspaces/anime-pipeline-litrpg-manhwa-20260904-001211`
- `P`: `/mnt/c/AgentWorkspaces/anime-pipeline-ember-lattice-premium-rd-20260904-150943`
- `G`: `/mnt/c/AgentWorkspaces/anime-pipeline-ember-lattice-editorial-gear-20260904`

Continuous reader captures live in isolated `.scratch/screenshots/`; my additional direct CDP9335 captures and scripts live in `.scratch/visual-b/`. These are internal ignored QA files, not redistributed art. [reader-browser-plan.json](reader-browser-plan.json) resolves source-reader paths. Synthetic local wrappers display the **existing complete phone raster strips**; they do not create replacement lettering or art. They establish mobile reading of those strips, not the behavior of an undiscovered original HTML reader.

Initial captures used a 390×844 CSS viewport with a visible desktop scrollbar; they are narrow-browser stress evidence. Subsequent own browser checks used mobile emulation and reported both `innerWidth` and `documentElement.clientWidth` as 390. Own final comparison/editorial captures followed `decode()` of existing local images to avoid lazy-loading position shifts. I did not use initial volume captures that repeatedly showed the page top: those were a capture-selector error, not repeated comic panels. The lead replaced them using `article.panel`. My volume CH01 scroll independently verified the actual sequence. Header occlusion in screenshots scrolled to an element's absolute top is not treated as panel-internal clipping.

| Pipeline/sample | Direct continuous inspection | Required sequence coverage and boundaries |
|---|---|---|
| North Garden boards | CH01 offsets 0,.2,.4,.6,.8,1; CH02 middle and end | Opening, dialogue, two-character exchange, quiet kitchen, system notices, exterior threat and both ending samples. Simplified previs; no complete choreographed combat or finished showcase art in these boards. |
| CH05 cadence | Full phone strip offsets 0,.2,.4,.6,.8,1; full P036 premium-cel image | Opening, tracking/dialogue, two-character brace, quiet inserts, dense interior, running ending; no monster boss or game UI in inspected sequence. Does not establish every CH03/04 output. |
| CH06–13 house-route | CH06 offsets 0,.2,.4,.6,.8,1; CH13 0,.4,.8,1; direct CH06 P004/CH13 P003 crops | Opening, clues, two-character emotion and physical work, quiet inserts, dense greenhouse and ending. CH07–12 **not independently visually sampled** in this pass. Full attack/counter/reversal and progression system unavailable from inspected spans. |
| Borrowed Down | CH01 all six offsets; CH04/08 middle and end; CH10 opening/middle/end; full CH01 S01 P05 | Opening, work/action, dialogue, two-person continuity, creature reveal CH04 end, quiet relationships and CH10 kiss, dense mass action, endings. No numeric LitRPG progression assessed. Complete combat reversal cannot be inferred from spaced chapter samples. |
| City | CH01 all six offsets; CH04/08/10 opening/middle/end; full CH01 S01 P01 | Opening, dialogue/emotion, two-person continuity, rescue/structural action, magical entity threat, low-density and dense exchanges, chapter endings. No numeric system/gear-choice progression assessed. |
| Ember pilot | Opened actual reader through opening/action/UI/ending/review sections; direct source P003 and CH01 volume reuse | Delivered reader showed overlays over empty art areas. Source art exists. Complete finished pilot sequence and experience scores are not inferred from source files. |
| Ember volume | CH01 direct own scrolling P001,003–014,016,018,020,022,024; CH04/07/10 corrected samples 1,3,5,8,12,16,20,24 | Opening, dialogue, cast continuity, action/counter/injury/aftermath, boss, resource/skill choices, quiet and dense scenes, four chapter endings. CH02/03/05/06/08/09 not independently sampled here. |
| Premium24 | P001,003,006,009,012,015,018,021,024, direct BM01/03/13/15 | Character, wounded exchange, environment, creature, fight/aftermath and UI benchmark coverage. Sampler order is not scored as an episode opening/ending. |
| Premium52 | P001,005,009,017,026,029,033,037,044,048,052; shared full art and P044 original | Opening, dialogue, contact/injury/aftermath, reveal/UI, quiet portrait, dense exchange and ending. Uses same narrative/art family as editorial; the stronger coverage there is not falsely counted as separate new images here. |
| Editorial52 | P001,004–009,012,017–024,026,029–034,037,039,043,044,046,048–052; direct BM01/03/13/15 and cleaned P044 | All required sequence types sampled. Matched original/revised lettering on identical selected art P005/P033/P048 in actual comparison page; P044 original/cleaned full images directly compared. |
| Kitchen control/matte | Full G07A Blender proxy, independent rendering, targeted change, actor matte composite | Control and preservation/repair illustrations only; no completed continuous sequence. Other LoRA/local control experiment families are not individually visually scored by this pass. |

## B01 North Garden storyboards

**Observation:** CH01 contains simplified geometric people, kitchen table, paper/map inserts, house exteriors and system notices. The ordinary argument over food and the unexplained system arrival are intelligible; the repeated kitchen camera and minimally differentiated figures do not supply expressive performance. CH02's final “safe/visible” reversal provides a clean story question. The drawings clearly function as previs. Calling them failed finished art would confuse production stages.

**Phone observation:** Small serif dialogue and extremely small monospaced notices require concentrated reading. The kitchen layout preserves a usable left/right speaker model; this is the best counterexample to a claim that the early work contains no useful sequencing. The board's controlled empty space also demonstrates that detail is not necessary for narrative structure.

Source: `R/docs` material displayed by `.scratch/north-garden-ch01.html` and `north-garden-ch02.html`; exact wrapper image URLs are retained in those files and reader plan. Evidence: `north-garden-ch01-390x844-{0,0_2,0_4,0_6,0_8,1}.png`, CH02 middle/end equivalents.

## B02 CH05 cadence and premium-cel route

**Observation:** The tracking sequence has an effective visual chain: map, footprints, crossed ground, thread, warmed vessel, bell, water, brace, return to a smoking home. It frequently varies panel width and height. A map insert asks a different reading action than an exterior or face. This is more purposeful cadence than a uniform succession of full-height fantasy illustrations.

**Limits:** The painterly mud, weathered wood and fabric remain visually busy. Dialogue mostly lives in rectangular caption strips without balloon performance. The final “Run.” box crosses the foreground woman's head. This produces a readable subdued investigation, not a strong action/progression contract. The full `P036` beam-bracing image has clear adult figures and a readable diagonal task; it is a counterexample to “the pipeline cannot stage physical interaction.” The larger question is sustained action under changing force, not whether two people can hold one object convincingly.

Source: `R/experiments/review-packets/ch05-sequence-cadence-review-r1/lettered/ch05-sequence-cadence-lettered-r1-phone-390px.png`; full `R/experiments/review-packets/ch05-complete-chapter-premium-cel-r1/panels/p036-premium-cel-r1.png`.

## B03 CH06–13 house-route sample

**Observation:** CH06's smoking house, window hand, ropes and close exchange develop a tangible rural mystery. The intimate face-to-face image is a stronger emotional counterexample than the later stock heroic lineup. CH13's greenhouse integrates overgrowth, water and machinery with the characters; the environment is worth retaining as craft evidence.

**Limits:** Long full-height object/texture inserts can assign an ordinary footprint or mechanism as much scroll time as a reveal. The sampled lettered strips have long stretches of art without visible dialogue; I cannot determine from the image alone whether omitted copy is intentional. The ending CH06 `GGRRRM` visibly extends beyond its dark rectangle. I do not infer a missing combat system or boss sequence where none is visible. CH07–12 require the other audit passes for coverage.

Source: `R/experiments/review-packets/ch06-ch13-local-lettering-review-r1/ch06/ch06-lettered-phone-preview-r1.png`, analogous CH13 strip, `ch06-default-house-route-r1/crops/ng-ch06-sc01-p004-default-r1.png`, `ch13-default-house-route-r1/crops/ng-ch13-sc01-p003-default-r1.png`.

## B04 Borrowed Down

**Observation:** This sample has a distinct palette and cast: Mae's yellow work coat, long braid and broad physical presence contrast with Dax's orange scarf and silver curls. Rope, winch and floating tools make the gravity premise visible. CH04's creature and CH10's broad struggle provide threat and scale. The CH10 kiss gives a concrete emotional event instead of a prose claim that the relationship matters.

**Limits:** Heavy black marks, scratches, water flecks and mechanical detail compete across almost every region. The character gesture is often understandable but seldom isolated by a quiet value field. Blank paper rectangles remain inside the art while dialogue is placed in labelled bands beneath it. The reader repeatedly consumes both a blank reserved area and a separate caption area. SFX such as THRUM/WHAM/tik become transcript labels; they do not shape the event spatially. Wide crowd/mechanism frames are particularly dense at phone size.

**Counterexample:** CH01's floating tools against a flat orange field makes the impossible motion immediately legible. Therefore “the visual identity is generic” is too broad for this project. It is an original and memorable identity with insufficient emphasis control, not merely an interchangeable dark fantasy look.

Source: `B/experiments/reimaginings/borrowed-down/chapters/ch{01,04,08,10}/chNN-phone-preview.png`; full `ch01/lettered-panels/ch01-s01-p05.png`.

## B05 The City Keeps Oaths

**Observation:** The curved luminous road, sky city and braid create a clear visual proposition. CH01's refusal to repair, rescue and speaking road establish curiosity. CH08's seated exchange and “Will you still walk with me?” show human vulnerability and visual relationship pressure. The supporting figures retain distinct broad clothing/hair cues.

**Limits:** Blue/gold atmosphere, glowing hand effects and repeated medium views make successive revelations similar in visual weight. Even CH10's conflict often looks like people discussing magic while standing in formation. Speaker-labelled white boxes are readable but repeatedly occupy faces: CH01 opening, the ending close-up, CH08 final promise and CH10 exchanges. This is a composition/lettering coordination failure; the full unlettered CH01 S01 P01 has a readable face that assembly subsequently hides.

**Counterexample:** The road cut and rescue produce understandable scene-level causality. The short readable copy and lighter separators are real advantages over the longest Ember dialogue blocks. Replacing the whole production because it is painterly would discard these strengths without proving a better result.

Source: `C/experiments/reimaginings/the-city-keeps-oaths/chapters/ch{01,04,08,10}/chNN-phone-preview.png`; full `ch01/panels/ch01-s01-p01.png`.

## B06 Ember pilot delivery versus source

**Observation, high confidence:** Opening the existing `E/docs/reimaginings/ember-lattice/pilot/reader.html` displayed lettering/UI/SFX on empty black art areas, including its embedded phone and review sections. This is a delivery observation for the opened file surface; it is not evidence that the source drawing is blank or unattractive. The source P003 exists and is attractive: a slight Elian smile and Mira's concerned backward look give more expression than several later portraits. The source lettering uses diagonal tails that pass through text in the review examples, and some UI content clips horizontally.

**Boundary:** I leave reader-impact, sequencing and genre experience scores null for this broken delivered pilot. Source-art direction is scored separately with medium confidence. Do not quietly substitute the volume reader and claim the pilot browser worked.

Sources: above HTML and `E/experiments/reimaginings/ember-lattice/pilot/source/p003.png`; screenshots `ember-pilot-390x844-0_15.png`, `-0_35.png`, `-0_95.png`, `-1.png`.

## B07 Ember ten-chapter volume sample

**Observation:** CH01 unmistakably promises adult action/progression fantasy. Ivory Belljaw against dark stone is a readable silhouette. P007/P008 use light empty backgrounds and clear physical engagement; this is the best counterexample to the claim that every Ember image is muddy or lacks graphic economy. CH10's enormous Bell Regent is a strong scale image. Injuries, resources, talisman spending and rescue choices make costs visible enough to follow.

**Limits:** Copy repeatedly describes the movement that art must communicate: CH01 P011 explains changed forelimb angle; CH07 P012 explains a choice between routes; CH10 P020 describes a return trajectory while showing Mira kneeling. In CH10 P016, copy says the platform is gone while an intact-looking platform remains prominent. This can represent a local timing distinction, but the image alone does not resolve it. On-page observation establishes ambiguity; it does not prove the exact upstream generation cause.

The dialogue regularly sounds like technical commentary plus dry qualification. Injury scenes still make room for lengthy polished remarks, reducing urgency. UI information covers faces or clips at the edge (CH01 P002/P009/P024; CH04 P024; CH07 P024). Long tails and boxes are placed over otherwise available performance. CH07's sampled slab redirect, floor-circle use and collapse all use the same orange `SHINK`; one treatment cannot distinguish these materials or emotional accents. This is a visible assembly choice, not a model limitation.

**Counterexamples:** CH01's bright action cards are economical; CH04 P024's crouched concern and lantern establish a believable quiet aftermath; CH10 P001 has genuinely useful monster scale. The pipeline has usable panel vocabulary. It does not sustain a deliberate sequence-level hierarchy with that vocabulary.

Sources: `E/docs/reimaginings/ember-lattice/volume/chapters/ch{01,04,07,10}/{index,full}.html`; corrected screenshots identified in coverage table. My CH01 sequence captures use the actual phone `index.html` and `article.panel`.

## B08 Premium24 benchmark

**Observation:** Strong adult close-ups, wounded exchange, architectural depth and mechanical monsters are present. Full BM01 has deliberate contours and planar face shading. Calling it purely an undirected painterly smear is inaccurate. BM03's two-person wound scene is readable, and BM15's kick shows a clear forceful contact.

**Limits:** The reader presents a benchmark sampler, not a finished episode; no opening-hook or chapter-end score is assigned. Large UI rectangles often contain only one tiny line. P004 puts that rectangle over the lead's face. P003's dialogue has weak attribution. Environmental stone, cloth tears and cracks receive a similar level of detail in quiet and action samples. Good individual illustrations do not establish sustained premium pacing.

Source: `P/docs/reimaginings/ember-lattice/premium-rd/benchmark-suite/readers/phone.html`; full art `P/experiments/reimaginings/ember-lattice/premium-rd/benchmark/targeted-edit/bm{01,03,13,15}.png` (identical source-family images also inspected in G).

## B09 Premium52 and B10 editorial52: matched comparison

**Observation:** The opening bridge is an effective sense-of-place image. The action now contains multiple contact, reversal, injury, recovery and reward moments. P018→P019 shows the jaw catching the spear and is a useful local causal chain. P031 expresses physical pain. P029's clean profile and P033's wound exchange are competent standalone images.

**Sequence limits:** P020 says to hold the jaw but shows the characters reset with the spear upright; P021 again has an upright spear and a different monster/character arrangement. The release/reset is not depicted as clearly as the initial contact. P022 lights a broad crack across head and limb while the sequence asks the reader to attend to a particular weakness. P043/P044 are strong spectacle stills, but identifying the exact trajectory and the relation between the two attackers takes more inference than recognizing the pose. P049 is an upright portrait under a medical exchange; its source-page description says she binds/checks the injury. The promised action is not visible. The existence of action-labelled panels does not establish the completeness of a choreographed action.

Most panels remain substantial portrait rectangles containing detailed ruins. The quiet profile, explanation, creature approach and impact all demand similar scroll real estate. Some longer gaps give pauses, but their effect cannot substitute for shape/shot/contrast differences inside the sequence. This is fatigue from repeated visual weight, not merely an objection to dark colors.

**Matched lettering findings, high confidence:** On the actual G comparison page, P005/P033/P048 use identical selected art for original and revised overlays.

- P005: revised copy is larger and shorter, with smaller boxes and tails. The top first line intersects the balloon contour; the tail remains weakly connected to the speaker. Original type is markedly small relative to the large balloon.
- P033: the original lays multiple exchanges on top of one another. Revision separates four utterances and substantially improves recoverability. It still places text above balloon contours, with long/ambiguous crossing paths through the shared reading space.
- P048: revised reward boxes use more readable type and less empty interior. They still resemble stacked status records; this is useful information, but visually more reporting than a felt power reward.
- P004 and P051 in the revised reader cover part or all of the protagonist's face with UI. P034 text visibly extends below the small UI box. P012 and P049 also show text sitting above balloon bounds. These are actual rendered defects; a safe-zone or font-size pass cannot override them.

**Clean-art comparison:** Original `P/.../ch01-unique/p044.png` and `G/.../editorial-clean/p044.png` retain the same composition. The edited image has subtly calmer surfaces in parts of the rubble/body, but the reader-facing event, silhouettes, camera, values and density remain broadly unchanged. I do not claim that this small repair has no value; it does not demonstrate a new visual direction or solve motion continuity.

**Best counterexamples to an overly negative account:** P029's face is clean and appealing; P018/P019 make contact clear; P031 has real pain; the small P005/P033 overlay changes demonstrably improve text; Belljaw is recognizable and setting-specific. The artwork is usable. The sequence and assembly are less controlled than its strongest stills.

Sources: `P/docs/reimaginings/ember-lattice/premium-rd/readers/phone.html`; G equivalent and `comparison/index.html`. Direct full BM01/03/13/15, plus original/cleaned P044. Own captures: `comparison-stack9/10` (P005), `comparison-stack65/66` (P033), `comparison-stack95/96` (P048); `editorial-p20` through `-p23`, `-p30` through `-p34`, `-p49`, `-p51`. These final own captures follow decoded art and verified 390-CSS-pixel viewport.

## B11 Kitchen controls and matte

**Observation:** G07A Blender proxies are clear orange/teal blocks and a table. The independent rendering retains that broad arrangement; the target-change rendering changes the right block to green while also changing surface/light treatment. This tests a narrow control task. It is not a premium character-sequence comparison.

The actor-matte composite has a readable inked kitchen but conspicuously mismatched people: the right figure is a large head/shoulder cutout with hard luminous edges and little seated-body continuity; the left figure is much smaller and sits behind a different desk-like shape. The compartmentalized actors do not establish believable shared physical space. **Counterexample:** the room itself has legible warm/cool grouping and a recognizable stove/table/window. Layer separation can preserve useful environmental work, but crude actor compositing is not a proven route to final comics.

Sources: `R/experiments/outputs/blender_kitchen_control_bundle_v2/g07a-no-change-r1.png`, `openai_gpt_image2_g07_bakeoff_r1/g07a-independent-01.png`, `.../g07a-target-change.png`, `actor_matte_g07_v1/g07a-actor-matte-composite-r1.png`. Provider names here identify existing artifact directories; I do not independently establish model identity, commercial rights or reproducibility from them.

## Causal implications and limits

**Supported diagnosis:** The strongest later stills are functional to strong illustrations; the observed failures concentrate in panel-to-panel event control, repeated visual weight, and coordination between image composition and lettering. Some earlier work has better local cadence (CH05), stronger cast/color distinction (Borrowed), or warmer visible acting (City, pilot P003) than a simple chronological improvement narrative suggests. The latest editorial pass improves recoverable dialogue without solving every balloon/UI defect.

**Hypothesis, not proven mechanism:** Selecting attractive completed images before final dialogue/action blocking makes it easy to retain the wrong moment and then explain it in copy. P049's binding description versus portrait, P020's reset spear, and repeated report-like UI are consistent with this hypothesis. They could also arise from insufficient editorial selection or timing choices within a more flexible architecture. The visible evidence does not prove that every generative model or every raster-based method has a fixed quality ceiling.

**Recommended controlled proof:** Keep the adult cast/ivory mechanical threat and test a 10–16-panel frozen sequence with rough continuous thumbnails before rendering, explicit spear/jaw/contact state, one deliberate bright quiet or action field, and balloons planned with the pose. Compare it to the current route on identical beats. Require no face occlusion, no text outside balloons/UI, and two readers able to reconstruct attack/counter/reversal without caption explanation. One full-resolution beautiful panel is insufficient evidence to scale. Human reviewers and the owner must supply the preference gate; my pass cannot stand in for them.

**Do not overclaim:** No production economics or rights fields were scored. No translation was run. This pass did not inspect every panel of every chapter, every local LoRA candidate, or inaccessible alternate readers. Technical-stage nulls reflect that boundary. A renderer can pass integrity, arithmetic and collision assertions while the observed reading remains unsatisfying. Conversely, high texture or dark values alone do not prove weak art; the counterexamples above preserve that distinction.


## B12 Bounded follow-up: gear and future-cast catalogues

Added after the subjective scores were locked. **No score changed:** this is documentation/concept-output evidence, not new finished sequential art. I opened both protected catalogue pages in my browser at mobile 390×844 and wide 1440×1000. Samples were Free Delver Fieldwork, Ash Crown Contract-Forged, Civic Meridian Office Issue and Verdigris Communion Grownwork; the Elian leverage-blade and Orin medical-workshop upgrade ladders; and future-cast entries Orin Pell, Sable Renn and Ilyra Quoin. These are adult-cast design briefs; the geometric illustrations themselves cannot visually establish age.

**Observation, high confidence:** The four sampled equipment-family illustrations are the same flat shield/cross/ring schematic with different palette colors. They do not depict the text's asymmetric repairs and pockets, crown-notched spines, rectilinear housings, or root hinges. The upgrade ladders are prose lists. No drawn before/after blade, satchel or equipment transformation appears in those sampled cards. The three future-cast illustrations are the same circular-head/trapezoidal-body/line-arm pictogram recolored by faction. Orin's square satchel and rolled sleeves, Sable's unequal shoulder and twin heel forks, and Ilyra's three tuning arcs are described but not drawn. These are neither turnarounds nor posed/anatomical character sheets, and they cannot be used to verify costume assembly, props, expressions or silhouette differentiation across shots.

**Practical value:** The catalogues give useful constraints to an art director: named materials, tradeoffs, role conflicts, silhouettes to explore and unwanted character shortcuts. For example, the medical kit's finite uses and loss of mobility can drive a readable tactical choice. Palette-family coding is useful for planning. **Limit:** the visible catalogue does not prove that those concepts work as appealing gear or differentiated cast, much less that the existing pipeline can reproduce them in action. Counting catalogue entries or schematic SVG files as production-ready designed assets would mistake prose coverage for visual development. The next proof needs at least a drawn front/side/back design and a two-character interaction using one actual upgrade, so silhouette, attachment and material differences can be tested on the page.

Sources: `G/docs/reimaginings/ember-lattice/premium-rd/gear/index.html` and `future-cast/index.html`; linked `G/production/reimaginings/ember-lattice/premium-rd/concepts/gear/family-{01,02,03,04}.svg` and `concepts/characters/future-{01,02,03}.svg`. Own local evidence: `.scratch/visual-b/gear-card{1,2,3,7,12}.png`, `gear-full.png`, `future-card{1,2,3}.png`, `future-full.png`. The attempted nonexistent card30 screenshot is excluded; it did not navigate to a new item.
