# Professional vertical-scroll comics production: industry research draft

Access date for all citations: **2026-09-06**.  
Review worktree: `C:\AgentWorkspaces\anime-pipeline-total-review-20260906-211925`.  
Companion machine-readable file: [industry-citations.json](industry-citations.json).  
This file is research-only. It does not score repository pipelines, does not quote or embed copyrighted comic pages, and does not download datasets or models.

## How to read this document

Every numbered topic has two explicit blocks:

- **Sourced facts.** Claims that a named source actually states. Citations use the `id` field in `industry-citations.json`.
- **Inference.** Synthesis, transferable craft notes, or implications for this forensic review. Not a sourced fact.

Time-sensitive numbers (pay, hours, panel counts, platform specs, AI policies) are dated. Where a source is older than 2024, the date is called out and current official confirmation is marked present or missing.

Currency conversions from KRW are **estimates** using a round ~1,350 KRW/USD band typical of 2025–early 2026 reporting. They are not exact costs.

---

## Method

Internet research was mandatory. Priority order:

1. Platform official help, notices, contest rules, terms, and SEC filings.
2. Korean government / KOCCA industry surveys and Yonhap / Newsis / iNews24 reporting of those surveys.
3. Software-vendor documentation from Celsys / CLIP STUDIO PAINT (the dominant professional webtoon authoring tool).
4. Reputable trade (ANN, Korea Herald, K-Comics Beat, CBR) and named executive interviews.
5. Academic process studies where they document labor split, not as market authority.

Rejected as primary authority: SEO farms, unattributed 2026 “complete guides,” and AI-comic product blogs that invent platform specs (several of these contradicted official WEBTOON and Tapas numbers).

---

## 1. Typical professional division of labor

### Sourced facts

Korean professional production is not a single-author default once a title is on weekly full-color serialization.

- Seoul Metropolitan Government’s 2024 standard contract for webtoon assistant artists states that creating a single webtoon typically involves **7 to 9 stages**, naming **script/conte, rough sketch (daesaeng), line art, coloring, and retouching**, and defines an assistant as a contractor responsible for **individual parts** of that pipeline. The city also reported that surveyed assistant contracts were **26% labor / 74% service**, and issued worker and freelancer templates including **fixed manuscript fee** and **per-cut manuscript fee** payment types. [`asiae-seoul-assistant-2024`]
- A 2024 *Journal of Digital Contents Society* study of webtoon production process and workforce describes **personal creation** (main author does every stage) versus **team creation** of at least **three people** for weekly serials; typical splits include writer vs illustrator, or writing / illustration / color assistant; line cleanup is often done by the picture author plus assistants who imitate the author’s style; coloring is split into **flats (밑색)** then **value/lighting (명암)**. [`dcs-webtoon-process-2024`]
- CLIP STUDIO TIPS production tutorials used by working English WEBTOON creators treat the pipeline as **thumbnailing, storyboarding, sketching, inking, coloring, effects, typography, formatting**. Coloring in print comics may be further split into **flatting, toning, rendering**. [`clip-mannygart-2023`]
- Walter Ostlie (WEBTOON Original *HAXOR*) treats **lettering as a distinct professional craft** equal in importance to story and art, with reusable balloon assets, tail aiming, and mobile-size checks. [`clip-ostlie-lettering-2020`]
- Japanese studio SORAJIMA, in a 2025 Comikey process article, describes a **6–7 artist studio** on one series because full-color weekly webtoon is too heavy for traditional manga one-author-plus-editor methods. Stages named: planning, character design, storyboard, outlines, coloring, background, finishing; work is handed off in sequence after editorial review of the storyboard. [`sorajima-comikey-2025`]
- WEBTOON’s 2024 IPO prospectus (424B4) says the company **matches writers with illustrators** and offers **varying degrees of editorial support and translation** to professional and amateur creators. [`webtoon-424b4-2024`]
- KOCCA’s 2024 survey, as reported by iNews24, found that compared with 2022, the share of authors who **create every process alone fell**, while shares who **hire assistants** or work **inside a CP/studio** rose. [`inews24-kocca-2025`]

Named roles that actually appear in these sources: writer, picture author / illustrator, storyboard / conte artist, rough/daesaeng, line/inker, flatten/color assistant, lighting/shading, background artist, retoucher/finisher, letterer (more explicit in English/WEBTOON-Original practice than in Korean studio credit lists), editor, production/CP manager, assistant (보조작가).

### Inference

A “writer, storyboard, line, flatten, color, effects, letterer, editor, production manager” roster is a **reasonable professional map**, not a universal org chart. Korean weekly studios often collapse lettering into the picture team and collapse effects into color/finish. English Originals more often treat lettering as a late specialist pass. Solo Canvas authors still exist at volume, but KOCCA data says they are a shrinking share of serialized professionals. For this review, any pipeline that asks one generative pass to replace that roster is competing against a **specialized weekly factory**, not against a hobbyist.

---

## 2. Creator and studio production stages

### Sourced facts

Recurring stage order across CLIP STUDIO, Seoul’s contract, SORAJIMA, and the DCS paper:

1. **Planning / synopsis / logline / character sheets.** Kakao Webtoon Studio submissions require a planning document with URL, logline, plot, and character settings. [`kakao-joinus-2026`] Manta requires a one-page synopsis plus character sheets for at least two leads. [`manta-apply-2026`]
2. **Script and visual conte (글 콘티 → 그림 콘티).** Kakao Original submissions require **episode 1 finished manuscript plus episodes 2–3 conte**, each **≥50 cuts**, JPG. [`kakao-joinus-2026`]
3. **Thumbnail / storyboard on the final vertical canvas**, including balloon placement. [`clip-mannygart-2023`] [`clip-ostlie-lettering-2020`]
4. **Sketch / daesaeng.**
5. **Line / cleanup.**
6. **Flats then shading / lighting.** [`dcs-webtoon-process-2024`]
7. **Backgrounds**, often as a parallel track using 3D or asset libraries (see §5).
8. **Effects / finishing / retouch.**
9. **Lettering.**
10. **Export, slice, mobile preview, upload.** WEBTOON CANVAS explicitly offers **preview** and **schedule** before publish. [`webtoon-how-to-publish-2025`] Tapas likewise requires desktop/mobile preview and says many readers use the app. [`tapas-creating-episode`]

WEBTOON’s IPO letter from founder Junkoo Kim describes the format itself: continuous vertical scroll; white space for isolation; crowded panels for chaos; long blank panels for suspense; SFX that can burst out of panel corners. [`webtoon-424b4-2024`]

Pre-production buffer: CLIP STUDIO TIPS (Manny Guevarra, Canvas creator) recommends a **buffer of three or more finished episodes** before launch, because WEBTOON’s UI prompts subscribe after episode 3 and editors treat the first three as a pitch. [`clip-mannygart-2023`] WEBTOON’s 2025 contest FAQ independently confirms the subscribe prompt after the third episode. [`webtoon-contest-faq-2024`]

WEBTOON Entertainment told ANN that for works proceeding to official serialization it **requests three manuscript episodes**, and that even if serialization does not proceed it compensates that work (company position; union disputes unpaid revision periods). [`ann-webtoon-union-2025`]

### Inference

Professional stages are **gateable**. Conte is reviewed before line; line before color; lettering is planned in thumbnails so balloons are not an afterthought. A generative pipeline that emits finished color plus baked text in one raster skips the cheap correction layer. That is a process mismatch, not a style mismatch.

---

## 3. Vertical-scroll storyboard and thumbnail practice

### Sourced facts

CLIP STUDIO official Korean tutorial (2019, still the vendor’s public webtoon explainer):

- Phone-width composition; height is long.
- Dialogue is placed using **vertical space**, not only panel boxes; a few lines of dialogue then a figure can read as thought.
- **Gutter height** is a directing tool for scene change and psychology.
- CSP has a **webtoon on-screen area** preview matching phone aspect, to be used at rough *and* finish. [`clip-official-webtoon-2019`]

CLIP STUDIO TIPS (Manny, 2023), citing WEBTOON Academy practice:

- Aim for a **cinematic one-panel-at-a-time** read.
- On an 800 px-wide canvas, WEBTOON recommends **≥200 px vertical space between panels**.
- Location/scene changes: **600–1,000 px** of gutter.
- Gutters can hold weather, motifs, or standalone impact dialogue.
- Vary panel height, width, shape, and position; use size for importance.
- **Impact / borderless panels** for character introductions and critical beats.
- Place balloons in storyboard; WEBTOON recommends **≤3 balloons per panel**.
- Balloons and narration may live in the gutter to pace the reader. [`clip-mannygart-2023`]

Ostlie: first-read balloons sit **higher**; tails aim at the mouth; tails should not cross; balloons should not form a wall between characters; this is solved in **thumbnails**. [`clip-ostlie-lettering-2020`]

WEBTOON 2025 contest FAQ defines a panel as “a frame or a single drawing” of varying size (establishing, close-up, high angle, long shot). Title cards, end statements, and non-story extras **do not count**. Multi-part uploads labeled as one episode **count as separate episodes**, each needing the minimum panel count. [`webtoon-contest-faq-2024`]

### Inference

Vertical directing is **scroll-time directing**. The professional unit is not “a pretty 9:16 illustration.” It is a planned sequence of phone-viewport beats, gutters, and balloon order. Generative full-bleed paintings with no gutter plan will fail this even if character appeal is high.

---

## 4. Episode cadence and sustainable staffing

### Sourced facts

**Cadence.** WEBTOON’s 424B4: most content is **weekly serialized bite-sized episodes**; web-novels may release **three to five times a week**. In Q4 2023 the platform published **124,000 episodes daily** (comics + novels, all offerings). [`webtoon-424b4-2024`]

**Hours (Korea, KOCCA 2024 survey of 800 authors, 2023 work year), from KOCCA press release and Yonhap:**

- Average **5.9 creative days per week**.
- **26.9%** work all seven days (down 6.2 pp year-on-year).
- **10.1 hours** on a creative day (up 0.6 hours).
- **6.3 days to produce one episode** (down 1.9 days year-on-year). [`kocca-press-2025`] [`yna-kocca-2025`]

**Hiatus and cut floors (policy, not productivity magic):**

- Kakao Entertainment (2023 contract revision, implementing the Ministry of Culture webtoon coexistence pact): **2 hiatus episodes guaranteed per 40 episodes** (~one year of weekly serials); “do not demand excessive volume”; if a contract states a minimum cut count, that floor moved from **60 to 50 cuts**. [`kakao-sedaily-2023`] [`kakao-goodkyung-2023`]
- Korean Ministry of Culture **2024 standard contract** (Yonhap): authors may take **2 hiatus episodes per 50**, and parties may agree **upper and lower volume bounds per episode**. [`yna-standard-contract-2024`]

**Staffing pressure.** Seoul City: assistants historically worked from verbal contracts with unclear scope and unpaid dates. [`asiae-seoul-assistant-2024`] Union/ANN: contest-to-serialization revision can last **months to three years** with unpaid redesign, per union sources; WEBTOON disputes unpaid-labor characterization. [`ann-webtoon-union-2025`]

**Panel floors used as professional bar:**

- Kakao Studio Original: **≥50 cuts** per submitted episode. [`kakao-joinus-2026`]
- Manta creator program: **≥50 panels**, vertical-scroll. [`manta-apply-2026`]
- WEBTOON 2025 contest: **≥40 panels** for action/fantasy, romance/drama, thriller; comedy/slice-of-life **≥15 panels** but **≥6 episodes**. Full color, English, **no generative AI**. [`webtoon-contest-faq-2024`]

### Inference

Sustainable weekly color at 50–70 cuts is a **team sport or a burnout machine**. KOCCA’s drop from ~8.2 days/episode in the prior-year Japanese summary of the 2023 survey to **6.3 days** in the 2024 survey is consistent with more assistants and CP employment, not with easier art. A research pipeline that cannot absorb 50-panel weekly human review will not match licensed serial operations.

---

## 5. Character sheets, 3D assets, reusable backgrounds, asset libraries

### Sourced facts

- Manta **requires** character sheets for **at least two lead characters** at submission. [`manta-apply-2026`]
- Kakao planning packets include **character settings**. [`kakao-joinus-2026`]
- WEBTOON contest materials: character-design uploads are **not counted as episodes**. [`webtoon-contest-faq-2024`]
- CLIP STUDIO official feature list: **40,000+ bundled manga materials**; 3D backgrounds and 3D characters with clothes, hair, expressions; pose libraries; LT conversion of 3D/photos to line+tone; a **Webtoon** new-document mode that concatenates pages for vertical preview and export. [`clip-functions`]
- CLIP STUDIO TIPS (O_kids, 2025): character sheets need **front, side, back, full body**; CSP 3D body models are used to lock proportions; poses can be saved and reused from Assets / PoseManiacs. [`clip-okids-sheets-2025`]
- CLIP STUDIO TIPS (SIENNAMI): convert eyebrows, eyes, lashes, hair chunks, scars, accessories, expression sets into **reusable CSP assets**. [`clip-siennami-studio`]
- SORAJIMA’s Tatelab (2026): Korean webtoons in particular use **SketchUp** for weekly full-color backgrounds of ~**70 cuts/week**; 3D is treated as mandatory because hand-painting that volume is not viable. A companion Tatelab guide walks CLIP STUDIO + ASSETS 3D → LT conversion → color match, recommending large canvases (example **8000×8000 px**). [`sorajima-sketchup-2026`] [`sorajima-3d-bg-2026`]
- WEBTOON 424B4: internal tools in testing, **Shaper** (2D sketch → 3D character so poses/clothes can change without resketching) and **Constella** (3D pose → 2D in the creator’s drawing style). Pain point named: **repetitive pose/clothing resketch** in serialization. **AI Painter** already rolled to creators. [`webtoon-424b4-2024`] [`cbr-shaper-constella-2024`]

### Inference

Professional identity control is **asset-first**: model sheets, 3D blocking, saved hair/eye parts, reusable rooms. Generative image models are being aimed by the platforms themselves at **pose reuse and coloring assistance**, not at inventing a new protagonist every panel. A pipeline without a locked character/set library is below the Korean studio floor.

---

## 6. Line-art, flats, shading, effects, finishing

### Sourced facts

- DCS 2024: after sketch, **line cleanup**; color is **flats with no holes**, then structural light/shadow. [`dcs-webtoon-process-2024`]
- CLIP STUDIO TIPS: ink on **vector layers** for resize-safe lines; close shapes for fill; then raster for paint. Flat character color plus a tight palette is explicitly recommended so weekly volume is survivable; full illustration rendering per panel is called unsustainable. Cel shade often uses **desaturated blue/purple Multiply**; hair highlights **Screen**; hard light **Glow Dodge**. Effects: speed lines, saturated lines, radial/motion/Gaussian blur. [`clip-mannygart-2023`]
- CLIP official tutorial: register character colors in a **color set**; use **correction layers / gradient maps** (e.g. sepia) for flashbacks instead of redrawing. [`clip-official-webtoon-2019`]
- Seoul contract lists **retouching** as its own stage. [`asiae-seoul-assistant-2024`]
- WEBTOON contest and Canvas upload rules: **full color** for contest; JPG/JPEG/PNG. [`webtoon-contest-faq-2024`]

### Inference

The professional look of licensed manhwa is **layered and editable**: line, flat, shade, FX, letters on separate passes. Flattened generative painting is expensive to correct because a continuity error in a hand or a costume is not a layer, it is a new image.

---

## 7. Action choreography and continuity review

### Sourced facts

- WEBTOON contest judging weights: **Artwork 20%**, **Storytelling & Hooks 20%**, **Impact & Satisfaction 20%**, **Audience Appeal & Engagement 40%**. Artwork criterion is “quality and clarity of the visual images.” Storytelling is “flow and readability” and a hook that builds anticipation. [`webtoon-contest-faq-2024`]
- CLIP TIPS: impact panels, gutter time, and camera-style shot variety (CU / ECU rendered more; wides flatter) are the action grammar. [`clip-mannygart-2023`]
- WEBTOON 424B4 founder letter: crowded panels = chaos; long blanks = suspense; SFX can exit the panel. [`webtoon-424b4-2024`]
- Shaper/Constella are justified in the S-1 as solving **pose continuity**, not spectacle generation. [`webtoon-424b4-2024`]
- CLIP official: check phone viewport at **rough and finish**. [`clip-official-webtoon-2019`]

No official public “action choreography checklist” from Naver or Kakao was found. Continuity is enforced in practice by model sheets, 3D blocking, editorial conte review, and assistant style-matching (DCS paper).

### Inference

Action readability on a phone is **cause → contact → result** across successive viewports, with locked body design. A single spectacular key image is not choreography. Human review of role binding, handedness, weapon side, and aftermath is a core professional cost, which is why platforms invested in pose-transfer tools rather than full-scene generators.

---

## 8. Editorial development

### Sourced facts

- WEBTOON 424B4: multilayered assistance including **writer–illustrator matching, editorial support, translation, marketing, and IP-adaptation agency**; promotion of titles identified as high-potential, including **cross-border**. [`webtoon-424b4-2024`]
- WEBTOON 2025 contest: judges are **WEBTOON editorial staff plus named Originals creators**; winners join Originals with a **separate publishing contract** in addition to prize money. [`webtoon-contest-faq-2024`]
- Kakao Studio: ongoing open call; results by mid-next month; Original track wants **20+ episode serialization experience**; adaptation track wants web-novel/drama adaptation samples; art track wants **≥50-cut color dramatic manuscript**. [`kakao-joinus-2026`]
- Manta 2026 creator program: Google Form → internal review → email only if accepted → **contract negotiation** → content delivery → schedule → launch. Original work only; adaptations ineligible; English; 18+; full ownership required. [`manta-apply-2026`] ANN and K-Comics Beat reported the same program, including PPE vs hybrid subscription+PPE matching per title. [`ann-manta-2026`]
- WEBTOON told ANN: contest winners contract immediately; serialization candidates submit **three manuscript episodes**; company says it pays even if serialization fails. Union: unpaid revision of story and designs for **3–8 episodes**, sometimes **up to three years**. [`ann-webtoon-union-2025`]
- Canvas publishing is **self-serve** with community policy, age-rating questionnaire, and creator-support appeals—not Originals editorial. [`webtoon-how-to-publish-2025`] [`webtoon-community-policy-2025`]

### Inference

Editorial is a **paid, multi-pass taste and market filter**, not a linter. Originals/Kakao/Manta gates expect a finished episode plus conte, not a style demo. Canvas is not a substitute for that gate.

---

## 9. Lettering and localization workflows

### Sourced facts

**Lettering craft (English WEBTOON Original practice).** Ostlie: rounded-rectangle balloons; diamond-shaped rag; tail to mouth; higher balloon reads first; no crossed tails; never cover important art; Crossbar-I only for the pronoun in all-caps lettering; consistency of stroke and typeface; design balloons in thumbnails. He draws at **1900×3040 px** so it scales to WEBTOON **800×1280** and can print at US comic size; **300 dpi** “so the printer doesn’t get confused”; font size chosen by zooming the canvas to **phone width**. [`clip-ostlie-lettering-2020`]

Manny: WEBTOON recommends **12–30 px** for standard dialogue depending on canvas; he uses **14 pt on 1600 px-wide / 300 dpi** and checks CSP on-screen area; balloons about **1/4–1/3 of canvas width**. [`clip-mannygart-2023`]

**Localization.** WEBTOON Canvas Translation Program (official FAQ, 26 Mar 2026):

- Opt-in, not default.
- Languages: English, Spanish, French, Indonesian, Thai, Traditional Chinese, German. **Not Korean or Japanese** in this unification.
- **Text only; does not alter art; does not train on artwork.**
- Eligibility: **≥10 published episodes** and **>2,000 global page views in 365 days**.
- Creator supplies a **glossary** (names, key terms).
- **No preview** before live; translations publish with the episode.
- Opt-out removes translations immediately; 60-day rejoin wait; per-series off has a 30-day wait.
- Human moderators exist (K-Comics Beat background interview with WEBTOON: **no in-house translators/localizers replaced**). [`webtoon-canvas-translation-faq-2026`] [`kcb-translation-2026`]

Totus (Voithru) English webtoon translation guidelines: translate **all in-image text** including signs and SFX; one text box per balloon/SFX unit; keep translation length/shape that **typesetters can paste into existing balloons**; Korean-to-English SFX glossary provided as reference. Pipeline stated: **translation → typesetting**. [`totus-en-guidelines`]

Professional localization vendors (GTE, GloZ, Translexi) describe the same constraint: **text expansion**, balloon redraw, SFX redraw vs overlay vs retain, and the need for **layered source files**. Treat as trade practice, not platform law.

**Canvas license (rights relevant to localization).** Canvas Terms (6 Jan 2026): WEI will **not sell** the digital comic to unaffiliated third parties; derivative-work rights limited to **marketing/promotion**; license lasts while content is on Canvas; **50% of Net Ad Revenue** to the uploading member; Super Like **70% of Super Like Net Revenue** after a 30% store-fee deduction. [`webtoon-canvas-tos-2026`]

### Inference

Localization resilience is **separate lettering layers + balloon slack + glossary**, not OCR of baked raster text. AI translation is being productized for **Canvas text**, with explicit “no art training / no art rewrite” promises. That is a different object than generative redraw of panels.

---

## 10. Mobile preview and QC

### Sourced facts

- WEBTOON How to Publish (updated 24 Nov 2025): before publish, **preview episodes** or **schedule**. Publishing is **website-only**, not in the app. [`webtoon-how-to-publish-2025`]
- CLIP official and TIPS: **On-screen area (webtoon)** preview during drawing; Manny: catch continuity errors and typos in WEBTOON’s **PC and mobile preview** after CSP export. [`clip-official-webtoon-2019`] [`clip-mannygart-2023`]
- Tapas Creating a Comic Episode: **preview on desktop and mobile**; “recommended to ensure that your comic’s font is legible on both”; many readers use the app. Upload from **desktop**; mobile upload can lower image quality. [`tapas-creating-episode`] [`tapas-how-to-publish`]
- Tapas feature guidance: vertical-scroll is **mobile-friendly** and more likely to be featured; episodes readable in **~5 minutes or less** while still delivering story. [`tapas-get-featured`]
- WEBTOON auto-slices images over **800×1280** and may drop quality, resize, or reformat. Creators who do not want that must stay inside those dimensions and the 2 MB / 20 MB caps. [`webtoon-contest-faq-2024`] [`webtoon-notice-1766-2021`]

### Inference

QC is **phone-first visual QA**: type size, balloon order, accidental slice through a face, color banding after JPEG, file-size crushing of gradients. Professional teams preview the actual viewer, not only the working PSD/CLIP file.

---

## 11. Platform dimensions, slicing, file size, color, upload constraints

Official or first-party specs located on 2026-09-06. Color mode is generally **RGB JPEG/PNG** by implication of mobile web; none of the official pages below state a required ICC profile.

### WEBTOON CANVAS (English, official)

| Asset | Spec | Source |
| --- | --- | --- |
| Episode image max (to avoid auto-optimize) | **800×1280 px**; auto-slice/optimize if larger | Contest FAQ 20 Nov 2024; Notice 1766 (18 May 2021) |
| Per sliced image | **≤2 MB** | Contest FAQ |
| Episode total | **≤20 MB, ≤100 images**; JPG/JPEG/PNG | Contest FAQ |
| Square series thumb | **1080×1080, <500 KB**, JPG/JPEG/PNG | [`webtoon-thumbs-zendesk-2026`] |
| Vertical series thumb | **1080×1920, <700 KB**, JPG/JPEG/PNG | [`webtoon-thumbs-zendesk-2026`] |
| Episode thumb | **202×142 px recommended, <500 KB**; pre-2025 **160×151** still shown at 202×142 | [`webtoon-thumbs-zendesk-2026`] |
| Preview / schedule | Yes, on website | How to Publish 24 Nov 2025 |
| Color | Contest requires **full color** | Contest FAQ |
| Gen AI | **Banned for 2025 contest**; Canvas community policy retrieved 2026-09-06 does **not** contain a general Canvas gen-AI ban | Contest FAQ; Community Policy 25 Nov 2025 |

Older WEBTOON “Before you publish” PDF still listed episode thumbs at 160×151; Zendesk 2026 is the current thumb spec.

### Naver Webtoon Challenge (Korean UGC)

**Not independently confirmed on a currently dated Naver help article in this pass.** Celsys’ official CLIP STUDIO tutorial (11 Dec 2019) documents Naver upload as **width 690 px only, height unlimited, 5 MB per file, 50 MB total, JPG/GIF**. Korean production-school writeups in 2024 still tell students to export 690 px and cite 5 MB / 50 MB. Treat **690 px** as long-standing Challenge practice, **not** as a 2026 Naver-official page we opened. [`clip-official-webtoon-2019`]

### Kakao Webtoon / Kakao Page

**No current public pixel upload sheet was retrieved from Kakao.** What *is* official:

- Kakao Webtoon Studio submission: **JPG, ≥50 cuts**, episode 1 finished + 2–3 conte. [`kakao-joinus-2026`]
- Kakao Entertainment 2023: contractual minimum cut count **50** if a floor is written (was 60). [`kakao-sedaily-2023`]

Industry training (Y Lab Academy, CLIP tutorials, studio tweets) commonly cite **Kakao Page ~720 px width** as *upload* width, with working files **1500–2500 px** at **≥300 dpi**. That is **practitioner consensus, not a Kakao help URL from this pass**.

CLIP official 2019 also documented then-Daum Webtoon as **760×7000 split, 4 MB/image, JPG preferred**. Daum Webtoon has since been absorbed into Kakao; do not treat 760 px as current Kakao Webtoon law.

### Tapas (official creator site)

| Asset | Spec | Source |
| --- | --- | --- |
| Episode page | **940 px wide, no height limit** (GIF height max **1000 px**) | File Size Guide; Creating a Comic Episode |
| Formats | PNG, JPG, GIF | File Size Guide |
| Individual file | File Size Guide: **<2 MB**; Creating a Comic Episode page also prints **10 MB** next to page size — **internal Tapas docs disagree**; do not flatten | [`tapas-file-size-guide`] [`tapas-creating-episode`] |
| Episode total | **<20 MB** | [`tapas-file-size-guide`] |
| Episode thumb | **300×300**, PNG/JPG/GIF, **<2 MB**, all-ages art | Creating a Comic Episode |
| Series thumb | **300×300** | File Size Guide |
| Book cover | **960×1440** | File Size Guide; 2024 cover guidelines |
| Banner | **1280×460** | File Size Guide |
| Preview | Desktop and mobile | Creating a Comic Episode |

### Tappytoon

Tappytoon Terms (effective **26 May 2026**): Contents First, Inc.; reader license for professional Content; **does not accept unsolicited materials, pitches, stories or ideas for Tappytoon Content**. User Content is a separate feature; no public episode dimension sheet for licensed manhwa delivery. [`tappytoon-tos-2026`] **Official creator upload specs: not published.**

### Manta (official apply page, live 2026)

Submission (English only): contact, title, one-page synopsis, character sheets (≥2 leads), **≥1 sample episode**, **vertical-scroll**, **≥50 panels**, **JPG, minimum 1500 px width**. Creators keep ownership; PPE or hybrid subscription+PPE chosen per title. [`manta-apply-2026`]

Note: 1500 px is a **submission working-width floor**, not a reader-slice width.

### Comparison (upload / submission, not working files)

| Platform | Width | Height / slice | Per file | Episode cap | Notes |
| --- | --- | --- | --- | --- | --- |
| WEBTOON Canvas | 800 px | 1280 px/slice | 2 MB | 20 MB / 100 images | Auto-slice if larger |
| Naver Challenge (2019 CSP doc) | 690 px | unlimited | 5 MB | 50 MB | Confirm before use |
| Kakao Studio | unspecified | n/a | n/a | ≥50 cuts JPG | Editorial intake |
| Tapas | 940 px | unlimited (GIF 1000) | 2 MB guide / 10 MB episode page | 20 MB | Docs conflict on per-file |
| Tappytoon | unpublished | unpublished | unpublished | unpublished | No unsolicited pitches |
| Manta apply | ≥1500 px | vertical-scroll | JPG | ≥50 panels | Intake, not viewer spec |

### Inference

Professionals **draw larger than upload** (Ostlie 1900 px, Manny 1600 px, Korean studios 1500–2500 px, Manta intake 1500 px) and downsample. Working at native 800 px is amateur practice. File-size caps punish heavy gradients, dense screentone, and uncompressed PNG.

---

## 12. Accessibility and localization resilience

### Sourced facts

- None of WEBTOON, Tapas, Kakao, Manta, or Tappytoon official creator specs retrieved here require WCAG conformance, alt text for panels, or reflowable lettering.
- WCAG 2.2 (W3C Recommendation **12 Dec 2024**) still applies to **web content generally**: text contrast **4.5:1** (AA) / **3:1** for large text; **images of text** should be real text unless presentation is essential; non-text contrast **3:1**; content must not rely on color alone; meaningful sequence must be programmatically determinable. Comics as **images of text** fail 1.4.5 unless lettering is essential to the art. [`wcag22-2024`]
- WEBTOON Community Policy (25 Nov 2025, effective ~6 Jan 2026): age ratings; no instructional self-harm; hate-speech limits; IP ownership required; **no full/partial nudity** and no mosaic/box censoring of nudity on Canvas. [`webtoon-community-policy-2025`] [`webtoon-notice-community-update-2025`] [`webtoon-age-rating-2026`]
- Canvas Translation Program: glossary-driven, text-only, no art rewrite. [`webtoon-canvas-translation-faq-2026`]
- Totus: plan translation length to fit existing balloons. [`totus-en-guidelines`]
- Ostlie/Manny: phone-width type tests. [`clip-ostlie-lettering-2020`] [`clip-mannygart-2023`]

### Inference

Licensed vertical comics are **inherently image-of-text**. Accessibility that platforms actually enforce is **age rating, contrast-enough-to-read-on-a-phone, and not covering faces**. Localization resilience is balloon slack and layered type. Decorative SFX welded into line art is the expensive failure mode.

---

## 13. Performance and reader-loading

### Sourced facts

- WEBTOON auto-optimize exists **because** oversize files hurt load; quality may be dropped. [`webtoon-notice-1766-2021`] [`webtoon-contest-faq-2024`]
- CLIP official: upload height often capped around **1280 px per file**, with files stacked to reconstruct the scroll. [`clip-official-webtoon-2019`]
- Tapas forum staff/community (older, 2018): shorter images load faster than one 940×4000 image. Not current official docs.
- WEBTOON 424B4 user metrics (Q1 2024 / Dec 2023): **~170 million MAU**; average **26–57 minutes/day** depending on offering; users read **5–10 episodes/day** in the founder letter. That is engagement, not bytes-per-slice. [`webtoon-424b4-2024`]
- No official Canvas/Naver public CDN budget (KB per slice, lazy-load window) was found.

### Inference

The operational rule is: **slice near 1280 px, JPEG, stay under 2 MB**, keep gradients from exploding entropy, and never let the platform recompress a carefully graded episode. Long PNG stacks are a loading defect.

---

## 14. Rights, model/output provenance, AI disclosure, commercial-use, platform AI policies

### Sourced facts

**Canvas / UGC**

- You must **own the IP** you upload. [`webtoon-community-policy-2025`]
- Canvas Terms 6 Jan 2026: nonexclusive license to WEI to host, display, monetize (ads / paid access), and use for **marketing** while listed; **no sale to unaffiliated third parties**; derivative rights **limited to marketing**. [`webtoon-canvas-tos-2026`]
- Translation Program: **does not train on artwork**. [`webtoon-canvas-translation-faq-2026`]

**Originals / Korea contracts (disputed)**

- WEBTOON Global Comms (Kiel Hume, ANN 6 Nov 2025): “Creators maintain full rights to their underlying IP, and **we do not train AI on creators' content**.”
- WEBTOON Creators Union provided ANN a Korean contract clause granting NAVER WEBTOON use of content **for research** (internal researchers, university joint research, affiliate research). Union head Shin-a Ha: this can mean **AI training without limitation**. Company: research-use ≠ AI training, “factually untrue.” [`ann-webtoon-union-2025`]

**Contests**

- WEBTOON 2025 Webcomic Legends: submissions **must not be created using any form of generative artificial intelligence**; discovered use is **disqualification**. [`webtoon-contest-faq-2024`]

**Platform AI products (company-described)**

- 424B4 / CBR: **AI Painter**, **Shaper**, **Constella**; training data for those products is **not disclosed** in the filing excerpts CBR quotes. [`webtoon-424b4-2024`] [`cbr-shaper-constella-2024`]
- Chosun Biz (13 Dec 2024): Webtoon AI Painter trained on **1,500+ works / 300,000 images from Naver Webtoon** (industry sources, not a Naver legal memo). [`chosunbiz-ai-painter-2024`]
- JoongAng Daily (6 Mar 2025): AI Painter launched **Oct 2021**; platforms also use AI for **recommendation** and **piracy detection (ToonRadar since 2017)**. [`joongang-ai-2025`]
- ScreenRant interview at Anime Expo 2025 with Yongsoo Kim and LINE Digital Frontier’s Sinbae Kim: company uses AI for **anti-piracy, user ML, and title recommendation**, not as a replacement for artists/writers. This is an **executive interview**, and it is narrower than the S-1’s creator-tool discussion. [`screenrant-ax-2025`]
- KOCCA 2024: **63.8% of companies** willing to use AI in production vs **36.1% of authors**. [`kocca-press-2025`]

**Tappytoon:** no unsolicited submissions; User Content license is broad if you use those features. [`tappytoon-tos-2026`]

**Manta:** submitter must fully own and control rights; no exclusive third-party lock. [`manta-apply-2026`]

**Generative-vendor commercial terms** (OpenAI, Adobe Firefly, Midjourney, BFL, etc.) were **not re-verified line-by-line in this pass**. They change and are output-route-specific. Do not infer commercial clearance from architecture family.

### Inference

There is **no single “WEBTOON AI policy.”** Contest: gen-AI ban. Canvas translation: text AI, no art training (company). Korea Originals contracts: **research-use clause vs company denial** — unresolved in public sources. Creator tools: style-transfer / pose / color AI whose training provenance is **not transparent**. For a commercial pipeline, provenance is a **dated registry decision**, matching this repo’s own standing rule.

---

## 15. Where generative AI is useful, unreliable, disallowed, or reputationally risky

### Sourced facts (useful / deployed)

- Pose/clothing reuse (Shaper) and style-consistent 2D from 3D (Constella), per WEBTOON S-1. [`webtoon-424b4-2024`]
- Coloring assistance (AI Painter). [`chosunbiz-ai-painter-2024`] [`cbr-shaper-constella-2024`]
- Recommendation, personalization, piracy detection. [`screenrant-ax-2025`] [`joongang-ai-2025`]
- Canvas **text** translation with glossary, explicit no-art-training. [`webtoon-canvas-translation-faq-2026`]
- 3D/SketchUp/CSP assets as **non-generative** automation already standard for backgrounds. [`sorajima-sketchup-2026`]

### Sourced facts (disallowed)

- WEBTOON 2025 contest: **any generative AI** in the submission. [`webtoon-contest-faq-2024`]

### Sourced facts (unreliable / contested)

- CBR: creators **do not know** how Shaper/Constella were trained. [`cbr-shaper-constella-2024`]
- ANN: union vs company on training-on-works. [`ann-webtoon-union-2025`]
- KOCCA: authors much less willing than companies to adopt production AI. [`kocca-press-2025`]
- ScreenRant AX 2025 quotes executives emphasizing recs/piracy, which **does not erase** the S-1 creator-tool program.

### Inference (risk map for this review)

| Use | Professional status | Risk |
| --- | --- | --- |
| 3D blocking, CSP assets, LT conversion | Standard | Low if licenses of 3D packs are clean |
| Flats / coloring assist on **author-owned** line, human-checked | Deployed by Naver tool | Medium: style leakage, muddy light, holey flats |
| Pose transfer from a locked 3D/character rig | Stated WEBTOON R&D goal | Medium until provenance is contractual |
| Machine translation of **layered text** with glossary + human letterer | Canvas product 2026 | Medium quality; low art-rights if promises hold |
| Full-scene generative color as final panels | Not how weekly studios ship | High: identity drift, extra limbs, uneditable paint, contest/Originals ineligibility, reader “AI slop” reputation |
| Baked-in generative lettering/SFX | Opposite of localization practice | High |
| Training on in-copyright comics without license | Public dispute; legally and reputationally toxic | High |

---

## 16. Realistic human review and correction burden

### Sourced facts

- KOCCA: **10.1 h × 5.9 d ≈ 60 hours/week** of author-reported creative time; **6.3 days/episode**. [`kocca-press-2025`]
- Seoul: 7–9 stages, often **per-cut pay** for assistants. [`asiae-seoul-assistant-2024`]
- DCS: weekly color needs **≥3 specialists**. [`dcs-webtoon-process-2024`]
- SORAJIMA: **6–7 artists** per series. [`sorajima-comikey-2025`]
- CLIP TIPS: balloon placement in storyboard specifically to **avoid covering art later**; mobile preview to catch typos/continuity. [`clip-mannygart-2023`]
- ANN union anecdote: “dozens of revisions,” new supervisor forcing a restart after a year. Single-source, not a survey. [`ann-webtoon-union-2025`]
- WEBTOON contest: **no individual editorial feedback** at volume. [`webtoon-contest-faq-2024`]

No public study gives “minutes per panel of QC” for AI-assisted vs hand pipelines.

### Inference

For a 50-panel color episode, professional burden is **days of specialist labor**, not minutes of prompt review. The expensive human minutes are: conte rhythm, acting, hands, identity, balloon/art conflict, color script, and phone read. Generative pipelines that dump 50 unique rasters **move almost all of that cost after generation**. Unless correction is layer-local (line, flat, mask), review time exceeds generation time. That is the central production-fitness issue for this repository.

---

## 17. Production economics (trade reporting; estimates labeled)

All figures below are **survey or filing statistics**, not a quote for a specific title. Do not treat them as this project’s budget.

### Sourced facts — industry scale

- KOCCA 2024 survey (2023 year): webtoon industry revenue **KRW 2.189 trillion** (+19.7% YoY); platforms **KRW 1.4094 trillion** (64.4%). Export mix: Japan 40.3%, North America 19.7%, Greater China 15.6%, Southeast Asia 12.3%, Europe 8.2%. Sample: **160 firms, 800 authors, 1,031 users**. [`kocca-press-2025`] [`yna-kocca-2025`]

### Sourced facts — author income (Korea, 2023 work)

From KOCCA via KOCCA PR, Yonhap, Newsis, iNews24 (they report overlapping slices; keep them distinct):

| Metric | Value | Who |
| --- | --- | --- |
| Median annual income, authors who serialized **all year** | **KRW 38 million** | KOCCA PR / Yonhap |
| Mean annual income, any serialization in 2023 | **KRW 42.68 million** (down 22.08 million YoY) | Newsis / iNews24 |
| Mean, all-year serializers | **KRW 47.69 million** | iNews24 |
| Largest income band | **KRW 30–50 million (50.4%)** of all-year serializers | KOCCA PR |
| Share earning ≥ KRW 50 million | **24.7%** (down 9.5 pp) | Newsis |
| Mean per-episode manuscript fee / MG | **KRW 868,000** (median **780,000**) | Newsis / iNews24 |
| Main income source | Manuscript fee **64.3%**; MG also **60%** (multiple-response) | iNews24 |
| Employment-style contracts | **25.9%** (up 15.1 pp) | KOCCA PR |
| Overseas income share | mean **6.8%** | KOCCA PR |

**USD estimates (not exact):** KRW 38 million ≈ **$28k**; KRW 868,000/episode ≈ **$640**; KRW 780,000 median ≈ **$580**.

Newsis also converted WEBTOON’s SEC professional average **$48,000** as about **KRW 70.5 million**, illustrating FX sensitivity—keep USD and KRW in their native units. [`newsis-kocca-2025`]

### Sourced facts — WEBTOON Entertainment (SEC 424B4, year 2023)

- Professional creator = monetizes Paid Content under a **formal revenue-share agreement**.
- **Average professional creator earnings $48,000**.
- **Top 100 average $1 million**.
- **483 creators ≥ $100,000**.
- Cumulative creator payouts **$2.8 billion (2017–2023)**.
- **~24 million** creators; Korea Herald, using the filing, puts professionals at about **13,000**.
- Amateur Canvas/Challenge cannot use Paid Content until promoted.
- Company 2023 revenue **$1,282.7 million**. [`webtoon-424b4-2024`] [`korea-herald-2024`]

These $48k / $1M figures are **platform-reported averages across WEBTOON’s professional contracts**, not Canvas ad-share medians, and not Korean KOCCA medians. They are different populations.

### Sourced facts — Canvas monetization mechanics (not typical income)

- Ad share: **50% of Net Ad Revenue**; payout floors **$100 Patreon / $25 PayPal**. [`webtoon-canvas-tos-2026`]
- Super Like: creator **70% of Super Like Net Revenue** after 30% store-fee bucket. [`webtoon-canvas-tos-2026`]
- Korea Herald: Canvas ad-share eligibility historically tied to **1,000 subscribers and 40,000 monthly views** (2024 reporting of a Naver pledge). Confirm in current dashboard before relying. [`korea-herald-2024`]

### Sourced facts — episode production cost

**No reputable 2024–2026 source opened here published a standard “cost per 50-cut color episode” for a Korean studio.** Informal studio quotes on the open web vary wildly and were not used.

What *can* be said without inventing a number:

- Labor is the cost: KOCCA ~**60 author-hours/week** plus assistants (Seoul: often per-cut).
- Per-episode MG/fee survey mean **KRW 868,000** is **author compensation**, not full loaded studio cost. Teams, 3D licenses, office, and CP margin sit on top.
- Kakao/Manta/WEBTOON contest all treat **~50 panels** as a professional episode quantum.

### Inference

Economics are **bimodal**. A weekly professional serial is a small firm: median Korean all-year author ~KRW 38M, WEBTOON professional mean $48k, top 100 at $1M. Canvas ad-share is a different, usually thinner, stack. Any AI pipeline whose “savings” come from deleting specialists must still fund **identity-true correction**; otherwise it is not cheaper, it is unfinished.

---

## Cross-cutting implications for this forensic review

### Inference only

Against the owner’s named bar (high-level transferable craft of titles such as *Tower of God* and *Solo Leveling*, without imitation):

1. **Unit of work** is a weekly **50+ panel** color episode with conte, not a handful of hero illustrations.
2. **Labor** is specialized and sequential; lettering is planned in thumbnails; backgrounds are asset/3D libraries.
3. **Phone viewport + gutter + balloon order** is the directing language.
4. **Generative full-panel color** is misaligned with how platforms actually use AI (pose, color assist, recs, piracy, text translation) and is **disqualifying** in WEBTOON’s own contest.
5. **Rights** are messy: Canvas license is nonexclusive hosting/marketing; Originals research-use vs “we don’t train” is a live dispute. Commercial eligibility cannot be inferred from a model family.
6. **Human minutes** dominate. A pipeline that cannot cheaply patch a hand, a hair part, or a balloon collision cannot serialize.

---

## What this pass could not verify

- A **2025–2026 Naver Challenge official upload-spec page** (690 px / 5 MB / 50 MB). Relied on Celsys 2019 + Korean school practice.
- A **current Kakao Page / Kakao Webtoon pixel-and-byte upload sheet** (720 px is practitioner lore).
- **Tappytoon** licensed-delivery technical specs (width, slice, MB). Official stance: no unsolicited submissions.
- **WEBTOON Originals** internal delivery spec (may differ from Canvas 800×1280).
- Whether Canvas has a **mandatory AI-assisted tag** as of 2026-09-06. SEO blogs asserted a Feb 2026 toggle; **official Canvas policy pages opened here do not state it**. Contest still bans gen-AI.
- **Training-data licenses** for AI Painter / Shaper / Constella.
- **Standard studio all-in cost** per episode in 2025–2026 KRW or USD.
- **Minutes of QC per AI panel** vs hand panel (no survey).
- Platform **WCAG** requirements (none found).
- Current **OpenAI / Adobe / Midjourney / Black Forest Labs** commercial-use terms (not re-read this pass).
- **Lezhin, Toomics, Ridibooks, Wattpad WEBTOON Studios** delivery specs (out of requested set except where WEBTOON 424B4 mentions Wattpad as a sister offering).
- Exact **cut-count averages** in KOCCA 2024 PDF tables (table of contents shows “average cuts per episode” and “appropriate cuts” exist in the full report; the public press release did not print those two cells; Gendai’s 2024 article on the *previous* survey cited ~**65 actual / 30–40 desired** cuts and studio median **70** — do not mix survey years).

Full KOCCA PDF landing page: [`kocca-report-page-2024`] (publicnuri type 4: attribution, non-commercial, no derivatives). Prior-year cut-count figures: [`gendai-kocca-2023-survey`].

---

## Source-quality notes

Primary/official used: WEBTOON Zendesk, notices, contest FAQ, Community Policy, Canvas Terms, SEC 424B4; Tapas creator site; Manta apply; Kakao joinus; Tappytoon ToS; KOCCA press release; W3C WCAG 2.2; CLIP STUDIO official tutorial/feature pages.

Reputable trade: Yonhap, Newsis, iNews24, Korea Herald, ANN, K-Comics Beat, Asiae, Sedaily, CBR, ScreenRant (interview), JoongAng, Chosun Biz.

Practitioner/vendor: CLIP STUDIO TIPS (named Originals/Canvas authors), SORAJIMA Tatelab, Totus/Voithru guidelines.

Weak / unused as authority: Gootaku, Patron, Comistitch, Honeytoon, LlamaGen, and other 2025–2026 roundups that contradicted official widths or invented AI-tag rules.
