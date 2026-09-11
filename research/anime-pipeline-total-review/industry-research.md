# Industry, platform and delivery research

Research cutoff and access date: **2026-09-06**. Scope: professional production, self-publishing delivery, localization, accessibility and quality control. This is external evidence; it does not itself score the repository's artwork. Source dates, authority and access qualifications are in [the industry citation ledger](evidence/industry-citations.json). Dates marked `null` were not discoverable; a crawl date or a date in a URL is not treated as a publication date.

**Finding:** professional practice provides a strong reason to test a storyboard and revision gate before rendering. It does not establish that any particular AI model, cel finish, staffing count or new story will beat the current pipeline. Those are comparative-pilot questions.

## What production evidence actually establishes

**Sourced fact — IND-02 (2022).** Ko and colleagues' We-toon study describes storyline development, character design, writing/storyboarding, draft revision, inking/coloring/shading and finishing. Storyboards include balloons, dialogue and composition; revision resolves poses and expressions before final art. Its formative workflow came from nine interviews with four professionals; the evaluation involved 24 professionals. The work identifies difficulty communicating visual revisions between writers and artists. This is a small, historical collaboration study, not a representative census or evidence that its GAN technique solves premium sequential art. [We-toon paper](https://hyungkwonko.info/data/wetoon.pdf)

**Sourced fact — IND-01 (2025-10-02; updated 2025-12-11).** Creator Obliviousquill's CELSYS tutorial documents episode scripting, character sheets with angles/colors/outfit details, thumbnails with dialogue, 3D assistance, line art, flats, rendering and finishing. It places scroll spacing and balloon planning in the sketch stage and uses phone preview. Its exact panel-density preferences are an individual's working rules, not platform requirements. [Creator's documented process](https://www.clipstudio.net/how-to-draw/archives/172579)

**Sourced fact — IND-04 (publication date unknown).** WEBTOON's live resource page links character sheets, character-design sheets, publishing checks and mental-health resources. Their existence supports treating preproduction and sustainable production as explicit activities; it does not prove every studio uses the same template. [WEBTOON Academy resources](https://www.webtoons.com/en/creators101/webtoon-academy/resource-list?resourceType=DOWNLOAD_RESOURCE)

**Inference for this repository.** The owner's difficulty naming a holistic gap is compatible with a missing shared visual decision surface. A longer prose contract cannot demonstrate a readable facial performance or a counterattack's geography. A rough, editable sequence allows rejection before expensive finished images become the basis of later decisions. This is a testable production hypothesis, not proof that generated art is intrinsically unsuitable.

## Recommended handoffs and review responsibilities

The following is a proposed lean production design derived from the evidence above; role names are responsibilities, not a claim that seven separate employees are required.

| Stage and responsible function | Reviewable handoff | Gate before proceeding | Failure prevented |
|---|---|---|---|
| Story/editorial | One episode promise, conflict, turn, payoff and unresolved next question; exact dialogue | Editor can explain why each beat belongs and what the reader wants next | Coherent lore with weak propulsion |
| Character/art direction | Original adult-cast turnarounds, expressions, costume/prop sheets and value studies | Recognizable silhouette and readable emotion at phone scale | Identity reduced to hair color and prompt attributes |
| Storyboard/action direction | Continuous rough strip, balloon shapes, positions, action vectors and a simple location map | Two independent readers can reconstruct who moved, why the counter works and what changed | Spectacular isolated poses with missing causality |
| Layout/assets | Approved cameras and staging; reusable prop/background geometry with provenance | Perspective and scale fit the action; repeated assets serve geography | Reference plates dictating the story |
| Drawing and color | Separable character, background, line, flat, shadow and effect information where practical | Faces/hands/weapon paths and value hierarchy reviewed before polish | Expensive correction of fused raster mistakes |
| Lettering/localization | Editable copy, speaker IDs, balloon geometry, separate SFX/UI and terminology list | Reading order, tail attribution, expansion and phone preview pass | Safe-zone compliance with poor reading rhythm |
| Finishing/delivery | Continuous export, slices, file manifest, transcript and browser preview | Visual sequence approval plus technical delivery checks | Correct files mistaken for a finished comic |

For action, freeze the start/end positions of both combatants, contact points, weapon hand, obstacle and escape direction. Show an anticipation/commitment, response, reversal, impact and resulting state where the beat requires them. These are proposed acceptance questions for the controlled benchmark; no source found establishes a universal mandatory six-panel action formula.

A modular route should prove **editability**, not merely produce layers with plausible names. Test changing one expression, reversing a weapon grip, reducing background detail and expanding a balloon without collateral changes to neighboring panels. A repeatable correction is more valuable than an attractive first candidate if the series must absorb editorial notes.

## Cadence, staffing and sustainable output

**Sourced fact — IND-24 (date unknown).** WEBTOON's service description characterizes ongoing ORIGINALS as weekly. Individual series may be on hiatus or have different live status; the label is not proof of their current delivery rate. [Official service description](https://help.line.me/LINE_WEBTOON/web/categoryId/20006001/3/pc?lang=en)

**Sourced fact — IND-25 (2022, historical).** KILSH's investigation included 15 interviews and 320 survey participants. The summary reports weekly publication for 63% of respondents and median required episode cuts of 70 versus a median of 50 respondents considered appropriate. It describes specialist studio work and deadline pressure. The translated summary contains anomalies in other numeric fields, so this review does not use its hours or income wording as a rate estimate. These are sampled historical experiences, not a 2026 universal quota. [KILSH primary report](https://kilsh.or.kr/en/webtoon-writers-working-conditions2022/)

**Recommendation.** Do not copy a 50–70-panel target or weekly calendar as a quality goal. Measure accepted panels per **total human hour**, including thumbnails, rejection, cleanup, lettering, QA and revisions. After a pilot wins, time at least two additional episodes before choosing a release cadence. Maintain explicit capacity for sickness, revision and buffer work. The proposed next pilot is intentionally too short to demonstrate sustainable serialization.

There is no defensible universal staffing count, current wage or full-episode production-hour range in the sources verified here. Costs and capacity assumptions are therefore separated in [economics, rights and risk](economics-rights-risk.md).

## Platform specifications: keep the export contract separate from panel design

**Sourced requirements as documented on access date.** WEBTOON's current resource index links the updated handbook. Its PDF page 8 (printed pages 9–10), plus PDF pages 28 and 31, provides the limits below. The web reader rejected its size, so the official PDF was fetched into memory and passed through `pdftotext` stdin/stdout; no PDF or artwork was saved. Its publication date is unknown. The live authenticated uploader was not tested. [Current-linked WEBTOON handbook](https://webtoons-static.pstatic.net/creator101/en/pdf/Creators-Resource-Handbook-Updated.pdf?dt=2024011001)

| Target | Documented content dimensions/format | Documented size limits | Delivery implication |
|---|---|---|---|
| WEBTOON CANVAS | Images within 800×1280 px; JPG/JPEG/PNG; larger images automatically reduced/sliced | 2 MB per processed image; 20 MB and 100 images total per episode | Keep a continuous master; make ordered delivery slices and inspect seams after recompression |
| Tapas comics | 940 px wide; PNG/JPG/GIF; no ordinary height limit; GIF maximum height 1000 px | 10 MB listed with page specification | Make a separate 940 px export; confirm size interpretation in uploader before publication |
| Tapas episode thumbnail | 300×300 px; PNG/JPG/GIF | Under 2 MB | Thumbnail is a separate deliverable, not a miniature readable comic |
| Kakao/Naver domestic, Manta, Tappytoon contracted delivery | `null` | `null` | Obtain the actual publisher/territory delivery contract before claiming readiness |

The Tapas guide also recommends desktop/mobile preview and checking font legibility. Its publication date is unavailable. [Tapas publishing guide](https://help.tapas.io/hc/en-us/articles/1260802028970-Series-Basics-How-to-publish-a-comic-episode-on-Tapas)

**Important distinction:** an 800×1280 file slice is not a requirement that every narrative panel be 800×1280. Slice count is not panel count. Neither a compliant width nor a low file size proves pacing, readability or editorial acceptance.

No verified universal color-profile requirement was found for all destinations. **Proposed local delivery contract:** retain a high-resolution editable master; export color-managed sRGB for browser QA, compare gradients/skin/black levels after export, and record the profile. Label this as the project's engineering choice until the destination confirms its own requirement. Do not equate DPI metadata with displayed screen detail.

## Lettering, localization and accessibility

**Sourced practice — IND-06 (date unknown; Korean interview).** Tappytoon describes separate language QA, graphic teams and coordination/PM responsibilities. Language reviewers check translation, flow, spelling and expression; graphic teams adapt visible Korean material for local readers. This is evidence that localization includes image work and scheduling, not just replacing dialogue strings. The report's English summary is a paraphrase of the Korean interview, not a certified translation. [Tappytoon division interview](https://about.tappytoon.com/25c8d914-9fdf-4560-a87a-b1d9238cc423)

**Sourced craft guidance — IND-07/08 (dates unknown).** Piekos recommends aiming tails toward the mouth and distinguishes lettering conventions from editorial preference. Ostlie advises evaluating type at phone width, planning balloon order during thumbnailing and preserving important art. Typeface-specific example settings are not a universal displayed-pixel minimum. [Blambot](https://blambot.com/pages/comic-book-grammar-tradition), [Walter Ostlie](https://tips.clip-studio.com/en-us/articles/3751)

**Proposed project checks.** Preserve speaker IDs, terminology, intentional emphases and line-break alternatives in editable records. Keep original text, balloons, SFX and system UI distinct. Test copy expansion on the same art (for example +30% and +50%, explicitly stress-test parameters rather than language statistics). A bilingual reviewer must review any eventual translation; machine consistency cannot establish idiom, voice or cultural accuracy. UI needs room for names and numeric changes without a smaller emergency font.

**Sourced standard — IND-09 (2024-12-12).** WCAG 2.2 includes non-text alternatives, meaningful sequence, color-independent communication, keyboard operation and text contrast (normally 4.5:1; 3:1 for defined large text). Its images-of-text and reflow criteria have scoped exceptions. A raster comic should not be pronounced conformant merely because its surrounding HTML passes automated checks. [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/)

**Proposed accessible local reader.** Add a useful panel-ordered transcript with speaker names, salient action and SFX, rather than only “panel 14” alt text. Use accessible navigation and visible focus; provide magnification without losing place; do not use color alone for system states. Preserve dramatic reveal order in descriptions. The current review's 390×844 QA is a usability sample, not an accessibility certification.

## Reader performance and actual attention

**Sourced engineering practice — IND-10 (date unknown).** Google's browser-loading guidance recommends explicit image dimensions, deferring offscreen images, and keeping initial-viewport/LCP images eager. Lazy loading still needs an end-to-end scroll test. [Browser image loading guidance](https://web.dev/articles/browser-level-image-lazy-loading)

**Proposed checks.** Record total bytes, first useful image load, layout shifts, image decode failures and scroll stalls under a stated viewport/network profile. Validate every lazy image after scrolling it into view. Test long reveals across file boundaries. A zero-broken-link test proves addressability, not timely reading or correct art selection.

**Sourced research — IND-23 (2026-01-29).** Chen and colleagues surveyed 84 people, tested 24 readers and interviewed five artists. Their interface comparison found different recall, engagement and preference effects by visual-language fluency; single-frame presentation simplified some comprehension but reduced perceived aesthetic satisfaction. The study used limited content/participants and is not a test of this original vertical-scroll pipeline. [Sage Open study](https://journals.sagepub.com/doi/10.1177/21582440261416099)

**Inference.** Freeze the evaluation interface and ask readers to explain action and emotional change, then separately score appeal and desire to continue. Passing comprehension does not imply premium art; passing an attractiveness vote does not imply clear causality. Avoid importing universal gutter widths or panel-height formulas from small studies.

## AI in professional production: bounded conclusions

WEBTOON's March 26, 2026 announcement describes opt-in AI text translation and a staged beta rollout. It does not establish that generated illustration is editorially accepted or commercially cleared, and an announcement is not proof that the owner's account has the feature. [Official localized program FAQ](https://webtooncanvas.zendesk.com/hc/zh-tw/articles/47592439172884-WEBTOON-Entertainment-%E5%AE%A3%E5%B8%83%E6%95%B4%E5%90%88%E5%85%A8%E7%90%83-CANVAS-%E5%B9%B3%E5%8F%B0-%E5%8A%A9%E5%8A%9B%E5%89%B5%E4%BD%9C%E8%80%85%E6%8B%93%E5%B1%95%E8%AE%80%E8%80%85%E4%B8%A6%E6%8F%90%E5%8D%87%E6%94%B6%E7%9B%8A-%E5%92%8C-FAQ)

Candidate uses worth testing are layout exploration, owned background assets, color variants, cleanup assistance and draft localization. Their utility must be measured against manual correction time and policy constraints. This is a proposed experiment list; this research did not observe production-grade results from those uses in this repository.

Platform permission, output authorship, asset licenses and provenance remain separate decisions. Tapas's live AI-generated-content prohibition makes it a material distribution constraint. Detailed scope and uncertainty appear in [economics, rights and risk](economics-rights-risk.md).

## Research limits that affect the decision

- The evidence combines current platform pages with older documented craft studies. It does not assert that every premium Korean studio shares one staffing topology.
- Current authenticated uploader behavior, private publisher contracts, actual asset licenses and destination-specific AI exceptions are unverified.
- Handbook publication date and several tutorial dates are unknown. Version strings were preserved without inventing dates.
- Korean KOCCA 2025 survey pages were discoverable but reliable full retrieval was unsuccessful; market-size snippets and their conflicting export percentages are excluded.
- The research establishes reasons for a fair production test, not a predetermined winner. The actual repository visual audit and owner response decide what to retain.
