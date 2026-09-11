# Visual B notes — sequential-art critic (independent)

Reviewer: visual-b  
Rubric: `anime-pipeline-total-review-common-rubric-v1`  
Date: 2026-09-06  
Scope: actual PNG/JPG rasters, overlay SVGs, and HTML phone/chapter readers. Visual-A files were not read. Prior-attempt worktree was not copied.

## Sampling (independent of A)

- **Borrowed Down:** CH01 lettered panels s01-p01–p05, s02-p04, s04-p04, s06-p05; CH01 contact, phone preview, compact-lettered, safe-zone; CH05 lettered s01-p01, s03-p03, s06-p05 + contact + phone preview; CH10 lettered s01-p01, s04-p04, s06-p05 + contact; diagnostics `ch08-s01-r1-spent-knot-fail` and `ch10-s04-r1-creature-fail`; repair `ch10-s04-r2-imagegen-edit`; character anchor; strongest `ch01-s04-p04`.
- **The City Keeps Oaths:** CH01 p01–p03, s02-p03, s03-p03, s04-p06; CH01 contact, compact-lettered, safe-zone, phone preview; CH07 action (s02-p05, s03-p03) + contact, compact-lettered, phone preview; CH05 contact; strongest-panels; sola progression sheet; CH03 lettering before/after; `viewer.html`.
- **Ember Lattice volume:** pilot p001, p002, p007, p015, p016; p016 outdoor fail vs r2/source; volume CH01 p017, p024; CH04 p009, p013, p017, p022; CH08 p013, p018, p024; CH01/CH04/CH08 contact sheets; CH03 landscape diagnostic; Elian reference; volume phone/full HTML + CH01/CH04/CH08 overlay SVGs.
- **Premium unique CH01 + bakeoff:** unique contact; p002, p007 vs pre-repair, p008 vs pre-repair, p011, p019, p026, p034, p036, p046; editorial-clean p019, p044; baseline / openai-raw / targeted-edit contacts; bm01 and bm08 raw vs targeted-edit; baseline bm007; Elian premium sheet; `phone.html`, hybrid/original/raw SVGs, collision and safe-zone overlays, failures gallery.
- **North Garden:** `production/accepted` (JSON only); `garden/` (code, no rasters); `garden-work/northgarden/out` strips, sheets, character rounds, action stills; `public-controls` geometry proxy. `ComfyUI/` and `models/` were not walked.

Phone-size judgment uses 390px (`premium.css` `.reader.phone{max-width:390px}`) and volume `.scroll{width:min(100%,430px)}`, plus overlay font sizes scaled to those widths.

## Required findings

### Inter-panel continuity failures (with paths)

**Borrowed Down**

- Mae’s face and braid length drift inside CH01: `...\borrowed-down\chapters\ch01\lettered-panels\ch01-s01-p02.png` vs `ch01-s01-p04.png` vs `ch01-s04-p04.png`.
- Dax carries a handheld clock *and* a wrist clock in `ch01-s02-p04.png`; the character anchor (`references\mae-dax-character-anchor.png`) specifies one gauntlet clock.
- CH10 costume/prop inflation: Mae gains a teal cape in `ch10-s06-p05.png` that is not in the CH01/CH05 workwear.
- Creature identity break: `diagnostics\ch10-s04-r1-creature-fail\ch10-s04-r1.png` is a generic kaiju head; the accepted lettered panel `ch10-s04-p04.png` still shows that kaiju-like head; the repair strip `repairs\ch10-s04-p05-r2\ch10-s04-r2-imagegen-edit.png` replaces the roar beat with a curved tentacle mass. The chapter contact (`ch10\review\ch10-contact-sheet.png`) still contains the kaiju-like read.

**The City Keeps Oaths**

- Sola’s white streak changes size and placement between `ch01-s01-p01.png` (temple ribbon), `ch01-s01-p03.png` (large top lock), and `ch01-s02-p03.png` (broad forelock). The progression sheet (`references\sola-progression-sheet-v1.png`) locks a temple streak; production does not hold it.
- Hand/finger mush on the same beat: `ch01-s01-p03.png` (grounded left hand), `ch01-s03-p03.png` (adult’s crystal-hand), `ch01-s04-p06.png` (rail hand).
- CH01–CH07 costume progression is intended (coat → sleeveless), but CH07 still recycles the same sky-bridge stage with construct armor that does not persist as a designed enemy (`ch07-s03-p03.png` vs CH01 bridge stills).
- Landscape-to-landscape stacking: CH01 contact (`ch01\review\ch01-contact-sheet.png`) is almost one camera family for the first six panels.

**Ember Lattice volume**

- Setting break, then repaired: `pilot\diagnostics\p016-r1-outdoor-continuity-fail.png` places the aftermath on an outdoor plaza with hills after a sealed vertical vault (`pilot\source\p001.png`, `p015.png`). Accepted `pilot\source\p016.png` matches the r2 indoor-bridge candidate.
- Graphic-style break: `pilot\source\p007.png` / volume contact CH01 P007 is a cream-ground cutout after dark vault plates.
- Format break: `volume\ch03\diagnostics\p007-r1-landscape.png` is a landscape plate in a portrait chapter.
- Anatomy stop: `volume\ch04\source\p017.png` — Elian’s planted left hand reads six fingers.
- Boss language changes without a design handoff: CH01 Belljaw (ceramic bell-body, tube snout) vs CH04 white knight-mecha (`volume\ch04\source\p009.png`) vs CH08 rotating cylinder/jaw (`volume\ch08\source\p013.png`, `p018.png`).
- Mira shield pattern and Elian coat-tear / vial count jitter across CH01/CH04/CH08 contacts.

**Premium unique / 52-panel**

- Premature boss, then patched: `ch01-unique\raw-failures\p007-pre-repair.png` and `p008-pre-repair.png` place Belljaw before the scan/hold beats; accepted `p007.png` / `p008.png` remove the creature but keep Elian’s extra-finger left hand in p007.
- Mira hair/undercut flips inside one chapter: undercut in `p008.png` and `editorial-clean\p044.png`; longer uncut hair in `p019.png` and `p046.png`.
- Creature scale and joint count wander: small background warden in `p011.png` vs fused mega-limb in `p026.png` vs ceramic bell in `p044.png`.
- 52-panel reader (`docs\reimaginings\ember-lattice\premium-rd\readers\phone.html`) interleaves unique plates with benchmark targeted-edit stills (`bm07`, `bm20`, `bm09`, `bm08`, etc.). Those stills do not share one geography: vault-bridge unique plates vs cathedral-nave bm08 vs outdoor-plaza bm03.

**North Garden**

- No sequential painted chapter exists in `production\accepted` (JSON only) or `garden\` (no rasters). Reviewable rasters in `garden-work\northgarden\out` are previz strips plus unlocked style rounds. Sigrid’s hair/body language in `sigrid_r3.jpg` (90s-anime / webtoon / watercolor) does not match `r5.jpg` (witch-berserker curls). That is not continuity inside a chapter; it is an unlocked pipeline.

### AI signature list

1. Extra digits / melted contact hands (Ember CH04 p017; premium p007; City crystal-hand and rail-hand; some Borrowed Down glove masses).
2. Extra or duplicated props (Borrowed Down double clocks in `ch01-s02-p04.png`).
3. Generic-IP bleed (CH10 kaiju-like head in creature-fail and still in `ch10-s04-p04.png`).
4. Face/age morph of a named lead inside a chapter (Mae; Sola streak; Mira hair; Elian “pretty-boy vs weathered”).
5. Cream-ground or outdoor location inserts that ignore the established set (Ember p007 cutout; p016 outdoor fail).
6. Painterly diffusion look: soft bloom, micro-grit, chromatic speckles, decorative debris (City entire CH01; premium unique — the failures gallery names these exact classes).
7. Same-pose generation: City CH01 p01–p04 are one crouch/bridge template; Borrowed Down many mid-chapter panels are “two figures + rope + spray.”
8. Constructed SFX/UI as Arial / Arial Black overlays rather than drawn lettering (all Ember overlay SVGs; City compact-lettered rounded chips).
9. Style-transfer character sheets that look like “90s anime / webtoon / watercolor” presets (`garden-work\northgarden\out\sigrid_r3.jpg`, `linnea_r3.jpg`, `soren_r3.jpg`).
10. Texture camouflage: Borrowed Down’s woodcut grain hides some mush but also reads as a global filter, not panel-by-panel craft.

### Does lettering hide art problems?

**Mostly no. Sometimes it occupies the problem instead of fixing it.**

- **Borrowed Down:** Lettering is not in the art. Lettered PNGs are empty paper rectangles baked into the painting, with speaker/SFX labels *under* the panel (`ch01-s01-p01.png` caption “In Veyr, down arrives by schedule.”). The boxes do not hide hands or faces; they waste composition and, in `ch10-s04-p04.png`, sit on the foreground like a missing title card. Compact-lettered review still shows empty boxes with microscopic captions. Lettering cannot rescue the kaiju read or extra clocks.
- **City:** Real balloons exist (`ch01-compact-lettered-review.png`). They sit in marked safe zones (`ch01-safe-zone-review.png`) and only rarely cover a face (P05, P23). They do not hide streak drift or bad hands. The CH03 before/after (`repairs\lettering-wave\ch03-before-after.png`) is balloon parking, not art repair.
- **Ember volume / premium hybrid:** SVG overlays are the honest architecture. System parallelograms (`volume\chapters\ch01\panels\p002.svg`; hybrid `el-pr-ch01-s01-p004.svg`, `el-pr-ch01-s05-p048.svg`) live in reserved corners and do not conceal six-finger hands. Hybrid tails are short blobs; original-lettering tails (`original-lettering\el-pr-ch01-s01-p006.svg`) quadratic through panel center (`Q512.0,844.8`) and *would* slice faces if used. SFX (`GONNNG`, `KRAK`) is Arial Black with a fat stroke — it advertises impact rather than hiding anatomy. Editorial-clean slightly reduces grit; it does not rebuild Mira’s hair or Elian’s extra finger.
- **North Garden previz:** Lettering *is* the comic. Faceless geometry means there is almost no drawing for balloons to hide.

### Are the strongest stills competitive?

**Yes as single images. No as a licensed serial.**

Competitive or near-competitive stills (mid-tier platform wall, not Tower of God / Solo Leveling craft as a book):

- Borrowed Down `ch01-s01-p01.png`, `ch01-s04-p04.png` / `strongest\ch01-s04-p04.png`, `ch05-s03-p03.png`, `ch10-s01-p01.png`.
- Ember volume `pilot\source\p001.png`, `p002.png`, `p015.png`, `volume\ch04\source\p022.png`, `volume\ch08\source\p013.png`.
- Premium `ch01-unique\p002.png` (chain), `p034.png`, `p036.png`; targeted-edit `benchmark\targeted-edit\bm08.png` (nave).
- City `ch01-s01-p01.png` and `volume-review\strongest-panels.png` P01/P08 — pretty, generic.
- North Garden `r4_action.jpg` and `r5.jpg` action rows — poster energy, not a chapter.

None of these pipelines would survive platform editorial as a weekly title: identity drift, extra digits, placeholder or Arial lettering, and (City / premium) generic AI painting would be caught on first pass. The stills prove a ceiling; the sequences prove the floor.

## Phone-width (390px) judgment

- **Borrowed Down:** Square plates at 390px keep faces large. The phone-preview filmstrips (`ch01-phone-preview.png`, `ch05-phone-preview.png`) make the under-panel captions unreadably small. Empty in-art boxes become beige slabs. Not a phone comic; a contact sheet of squares.
- **City:** Landscape 16:9-class plates at 390px are ~220–260px tall. Wides (CH01 p01, p24; CH07 p15) shrink acting to silhouettes. `viewer.html` is a real reader with Phone / Full / Review modes and a 760px drawer, but the source aspect ratio is wrong for vertical scroll.
- **Ember volume:** Correct webtoon aspect. Phone reader width 430px. Overlay type ~30–36px on ~850–1024 viewBoxes scales to ~14–16px at phone width. Readable for short English, tight for the long CH04 balloon (`volume\chapters\ch04\panels\p013.svg`, six lines).
- **Premium hybrid:** Collision overlay states `15.6px PHONE` (`diagnostics\lettering-collision\el-pr-ch01-s01-p005.svg`). That is the floor of adult reading, not a lettered-platform standard. Balloons are cream rounded masses, not designed balloon shapes. Deep-gutter panels in `phone.html` help scroll rhythm; recycled benchmark stills break it.
- **North Garden previz strips:** Vertical and actually designed as a phone scroll. Type is small; faces are discs. Readable as a graphic essay, not as character acting.

## Pipeline notes (critic, not strategist)

### north-garden-legacy-local

Inspectable output is a **previz comic** (`ch01_strip.jpg`, `ch02_strip.jpg`, `ch01_sheet.jpg`) plus **unlocked style boards**. The kitchen/system argument is genre-legible (rural freeze, terminal, numbered schema). Acting cannot function without faces. Action boards (`r4_action.jpg`, `action_warm.jpg`, `r5.jpg`) show poster-level void/berserker energy in three style lanes and do not lock a series look. `production/accepted` has no rasters. `artstatus.md` claims Anima/Comfy generation; those trees were not walked. Score this pipeline as an unfinished local R&D stack with a readable previz, not as a painted serial.

### borrowed-down

Highest **world and print identity** in the set. Opening hook and color script would not embarrass a mid-tier print-fantasy book *as stills*. Sequential craft is a working serial with frequent identity and extra-prop failures. Lettering is a mock. CH05/CH10 do not collapse, but they get busier and less spatially strict. Repair culture exists (creature-fail named and re-rendered) and still ships a kaiju-like head in the lettered CH10 plate.

### the-city-keeps-oaths

Cleanest “AI fantasy illustration” look, and that is the problem. Genre is readable (oath-roads, sky city). CH01 has a causal seam-failure story. CH07 action is pose-and-glow, not choreography (`ch07-s03-p03.png` is a group pinwheel). Viewer HTML is the most complete reading shell outside Ember. Hair/hand continuity would fail editorial. Strongest stills are wallpaper.

### ember-lattice-ten-chapter-volume

Best **manhwa-shaped** pipeline: portrait plates, reserved UI corners, Fault Sight → ankle as an intended combat sentence, ten-chapter contacts that still look like one book. CH01 vault and CH08 hanging beat are the closest this review gets to a licensed-floor still. Six-finger CH04, cream cutout P007, outdoor p016 fail, and Arial overlays keep it below platform standard. LitRPG machinery is present and mostly understandable when overlays are on; it is not original versus the named bar’s system windows.

### ember-lattice-premium-rd-52-panel

Higher peak stills (chain, lattice-breath, nave) and worse identity control. 52-panel CH01 is assembled from unique plates **plus** bakeoff stills, so geography and costume cannot be one place. Premature-boss repairs work as instruction-following, not as anatomy repair. Mira’s hair is not a character; it is a sample. This is a cinematic R&D chapter, not a shippable episode.

### ember-lattice-editorial-gear-hybrid

The overlay/clean-art/targeted-edit layer is the only place in-scope that treats lettering as a deterministic, localizable object. Hybrid balloons beat original-lettering (shorter tails, 41px vs 29.7px source type). Targeted-edit `bm08` vs openai-raw `bm08` proves a real art-direction lever (remove extra wardens; keep the nave). Editorial-clean is a denoise pass, not a redraw. Hands, hair, and extra-joint Belljaw remain. Production fitness is the highest of the six *as a method*; sequential-art quality remains the premium rasters.

## Uncertainty (labeled)

- Not every panel of every Borrowed Down / City / Ember chapter was opened at full resolution; contacts were used to scan, then full plates were opened on failures and peaks.
- North Garden ComfyUI output directories were not inspected by protocol. If later Anima chapter rasters exist only there, they are **not assessed**.
- Overlay SVGs in this worktree point at `experiments\reimaginings\...` rasters that live in other worktrees; phone readers were judged from HTML/CSS/SVG plus those rasters in place, not from a running local server.
- File integrity, hashes, and schema PASS were ignored for scoring, per rubric.
- Named-bar comparison is craft-transfer only (clarity of acting, identity lock, action grammar, system-window originality). No copyrighted panels were used as generation references.

Scores live in `scorecard.json`. They were not averaged with any other reviewer.
