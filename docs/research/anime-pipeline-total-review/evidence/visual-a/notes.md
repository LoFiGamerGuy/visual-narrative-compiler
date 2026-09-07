# Visual A independent notes

Reviewer: visual-a  
Rubric: `anime-pipeline-total-review-common-rubric-v1`  
Method: inspected rasters with the image reader (pages rendered, not filenames). Inspected matching SVG lettering overlays and HTML readers as text for scroll structure, type sizes, and phone widths. Did not read visual-b files. Did not upload art.

Observation vs inference is labeled. Scores live in `scorecard.json`. This file records what the pages actually show.

## Inspection log (what was actually looked at)

### Ember Lattice ten-chapter volume
- Pilot rasters `p001.png`–`p016.png` in the litrpg worktree (opening, portraits, Belljaw, action, talisman, combo, aftermath).
- Remaining CH01 rasters `p017`, `p019`, `p020`, `p024`.
- CH01 / CH03 / CH05 / CH10 contact sheets (all 24 frames each).
- CH03 action/aftermath: `p011` Glassback, `p013` resonance, `p014` shield intercept, `p022` kill, `p023` loot, `p024` well.
- CH05 system/progression: `p003` Orin, `p004` inventory tray, `p015` failed channel, `p022` chest/UI glow.
- CH10 ending: `p018` Channel II pose, `p022` Regentbreaker spectacle, `p024` party walk-off.
- Lettering SVGs: `ch01/panels/p001.svg`, `p002.svg`, `p003.svg`, `p007.svg`, `p013.svg`, `p015.svg`, `p019.svg`; `ch05/p002.svg`, `p022.svg`; `ch10/p022.svg`.
- HTML: `volume/chapters/ch01/index.html` (phone), `full.html`, `volume/index.html`, `read-all.html`.
- CSS: `volume/assets/volume.css` (phone column is **430px**, not 390).

### Premium 52-panel unique CH01
- Contact sheet `ch01-unique-contact.png`.
- Unique rasters: `p002`, `p007`, `p008`, `p026`, `p043`, `p044`.
- Preserved failures: `raw-failures/p007-pre-repair.png`, `p008-pre-repair.png`.
- Editorial-clean: `p014`, `p034`, `p044`.
- Hybrid lettering SVGs: `el-pr-ch01-s01-p001` (empty), `p002` (SFX), `p004` (HUD), `p005` (dialogue).
- HTML: `premium-rd/readers/phone.html` (max-width **390px**), `full.html` structure via CSS, `failures/index.html`, `diagnostics/clean-art.html`, `gear/index.html`, `future-cast/index.html`.
- Gear/future-cast concept SVGs: `family-01.svg`, `future-01.svg`, `future-02.svg`.

### Borrowed Down (lighter sample)
- Lettered CH01: `s01-p01` through `s01-p05`, `s02-p01` through `s02-p03`, `s03-p01`.
- Phone strip `ch01-phone-preview.png`.
- CH03 contact sheet and action panel `ch03-s04-p04`.
- Strongest still `strongest/ch01-s04-p04.png`.
- Creature-fail strip `diagnostics/ch10-s04-r1-creature-fail/ch10-s04-r1.png`.

### The City Keeps Oaths
- CH01 rasters `s01-p01`–`p06`, `s02-p01`–`p03`, `s03-p03`.
- CH01 contact sheet, compact lettered review, phone preview strip.
- CH04 contact sheet and `ch04-s03-p03`.
- CH08 contact sheet (later quiet chapter).
- `viewer.html` (desktop 960px frame; phone mode loads prebaked 390px strips).

### North Garden legacy-local
- Accepted kitchen: `pagecomp3/page03_p06.png`, `p07`, `p08`, `p10`.
- Earlier compose: `pagecomp/page01_p06.png`, `p08`.
- Style tests: `actstage/act_1_webtoon_00001_.jpg`, `act_1_painted_00001_.jpg`.
- Visible sample is a kitchen two-shot plus style-probe stills. No monster, no action chain, no lettered reader, no system UI on the inspected pages.

---

## Key questions

### 1. Are strongest individual panels competitive while sequences fail, or are panels themselves below bar?

**Both, with the split depending on pipeline. Observation first.**

**Ember Lattice volume:** strongest stills are competent *illustration* key art, not competitive *comic panels*.  
- `pilot/source/p001.png` is a real establishing image: tiny figures on a chain bridge over an ember shaft. As a poster it works. As panel one of a serial it spends the entire frame on architecture and gives the reader two unreadable silhouettes.  
- `p004.png` Belljaw from behind the party is the best monster intro in the corpus: scale, ceramic bell-head, cracked platform.  
- `p015.png` combo and `ch10/p022.png` “Regentbreaker” are spectacle stills — glowing line into a tower, debris, two posed figures.  
- `p013.png` is below bar as a panel: sausage hands, two square coins that do not read as the “Spark Talisman vs Iron Seals” the caption claims, face in the generic-pretty-boy register.

Sequences fail *and* many panels are already below a licensed serial bar. The failure mode is not “great comics drawing ruined by bad cutting.” It is “attractive generative stills, each composed as a complete illustration, then stacked.”

**Premium unique / editorial-clean:** stills go higher. `ch01-unique/p026.png` (Belljaw backhand) and editorial-clean `p044.png` (ankle split) would not embarrass a mid-tier key-art pass. They still read as posed illustrations. `p043.png` is the tell: Elian levitates in a jump-pose with no launch surface, Mira runs in a separate plane, Belljaw stands on a broken ledge that does not match the prior bridge. Competitive still, failed sequence.

**Borrowed Down:** panels themselves are closer to a real comic language (print texture, black borders, tool-specific acting). `ch01-s01-p02` Mae on the pin, `ch03-s04-p04` the slab rescue, and the CH03 contact sheet show sequential intent. The panels are not below bar as drawings. What fails the serial is empty lettering boxes and caption-under-art, not the drawing.

**City Keeps Oaths:** individual paintings are the most “pretty.” `ch01-s01-p01` Sola on the cloud road, `ch01-s01-p05` headache close-up, `ch01-s03-p03` two-character key-and-staff. They are below a professional *webtoon panel* bar because they are landscape illustration plates with almost no panel grammar (no gutters inside the frame, no speed, no crop for phone). Sequences are a slideshow of similar beauty.

**North Garden:** `pagecomp3/page03_p08.png` and `p10.png` are the most comic-like drawings in the whole review: graphic-novel ink, lamp/fire light, two adults in a real room. The panels are not generic AI prestige-fantasy. The sequence is a four-frame kitchen argument with mutating architecture. Not enough pages to call it a serial, but the drawing language is closer to comics than Ember Lattice’s stills.

**Inference:** if the owner’s bar is Tower of God / Solo Leveling transferable *craft* (staging, acting, causality, phone rhythm), no pipeline’s strongest still is that craft. If the bar is “would this pass as a fantasy illustration,” premium Ember and City stills sometimes would.

### 2. Generic prestige-fantasy convergence: yes/no with examples.

**Yes for Ember Lattice (volume, premium unique, editorial-clean) and The City Keeps Oaths. No for Borrowed Down. No for North Garden kitchen.**

Ember Lattice examples (observation):
- Elian is a fair, sharp-jawed blonde in a tattered long coat, open shirt, brass vials, hooked shortblade. That costume repeats from `p002` through `ch10/p024` with almost no silhouette evolution.
- Mira is the redhead-with-undercut spear-and-kite-shield girl. Hair shifts orange (`volume p003`) to darker red (`premium p007`). The T-pose with split ivory shield is the only strongly designed shape, and it is reused as a stamp.
- Environments converge on cracked ashlar, hanging chains, orange lava-cracks, teal glass catwalks. CH01 pit, CH03 gallery, CH05 kiln, CH10 shaft are the same material language at different zoom levels.
- Faces share one rendering: smooth skin, identical eye highlight, same three-quarter scowl. Orin (`ch05/p003`) is a second handsome-bearded stock. Sable (`ch04/p018`) is a third stock (black-plum pathcutter).
- Premium unique `p002` (macro glowing chain) is a Midjourney-house object hero. Editorial-clean does not change the design; it reduces grit.

City Keeps Oaths examples:
- Sky-bridge over clouds, glowing lantern-pylons, teal crystal, dusk palette, ornate white-gold coats. `ch01-s01-p01` through `p06` could be any “floating capital” webtoon opener.
- Sola’s white hair-streak and copper witness-cuff are the only identity locks. The city behind her is generic luminous gothic.
- CH08 contact sheet is twenty-four conversation stills in the same blue-gold night.

Borrowed Down counterexamples:
- Coral/teal print, rope, pins, bells, stained yellow work coat, teal harness, dock cranes. `ch01-s01-p01` “In Veyr, down arrives by schedule” is a specific world, not a dungeon template.
- Mae’s braids, gold hoop, dirty coat, and working hands do not resemble Elian/Sola.

North Garden counterexamples:
- Cabin kitchen, laptop, wood stove/fireplace, snow window, lantern, plaid trousers. Graphic black ink, not cel-dungeon.

### 3. Character magnetism vs mere consistency.

**Ember Lattice: consistency without magnetism. Observation.**

Elian is *recognizable* across 240 volume frames and the 52-panel slice: blonde undercut, green eyes, grey-green coat, brass belt. That is consistency. Magnetism would be a face or body language a reader could pick out of a lineup of LitRPG protagonists. He does not have it. The expression range on inspected pages is: profile stoic (`p002`), three-quarter smirk (`p003`), combat grimace (`p010`–`p011`), injured stoic (`p016`, `p017`). Premium `p026` pain-face is the most acted, and it still looks like a stock “hit reaction.”

Mira is more magnetic than Elian because of the undercut-plus-shield silhouette, not because of acting. Her face is the same determined frown in `p007`, `p008`, `p014` (CH03), `p022` (CH03). The CH01 `p017` bind-the-ribs kneel is the only tender beat, and even there her face is the combat frown.

Orin has more face-as-character (`ch05/p003` monocle, apron, vial). Sable has a costume (`ch04/p018`) but the “wrong victory” is a pose, not a look.

**Borrowed Down: magnetism present.** Mae’s body reads as a person who works: squat on the pin, brace on the stairs, lift the slab. Dax’s red scarf and clock-gauntlet separate him in every two-shot. Consistency of coat/harness is high across CH01 and CH03.

**City: moderate magnetism, good consistency.** Sola’s braid + white streak + copper cuff survive CH01, CH04, CH08. The white-coat staff man is a stable second lead. Magnetism is illustration-pretty, not comic-acting. `ch01-s01-p05` (hand to temple) is the best acted face in that pipeline; most other frames are the same alert three-quarter.

**North Garden: magnetism in a small sample.** Soren’s back-and-lamp compositions (`pagecomp3 p08`, `pagecomp p08`) and Sigrid’s lantern-and-plaid are more specific than Ember’s heroes. Hair/face of Sigrid is consistent enough to recognize. Not tested across action.

**Inference:** Ember optimized for “same character every time” and got a mannequin. Borrowed Down optimized for a worker’s body and got a protagonist.

### 4. Action assembled from poses vs choreographed motion.

**Assembled from poses, almost everywhere. Observation.**

A choreographed sequence would keep a stage, a camera side, and a body that arrives in the next panel from the previous one.

Ember volume CH01 action:
- `p005` side-on geography (good intent: Belljaw right, Mira center, Elian left, pit below).
- `p006` charge on the same bridge language.
- `p007`–`p008` dump the dungeon for a cream studio cyclorama. Mira and Belljaw become cut-out figures. That is not a cut; it is a new illustration.
- `p009` ankle scan, no bridge.
- `p010` Elian slides under the jaw — but the background is outdoor ruins and sky, not the pit.
- `p011` backhand into a hanging chain (readable impact, new floor).
- `p012` hanging in the pit (returns to dungeon, body not obviously the result of `p011`’s trajectory).
- `p015` combo: Mira and Elian in the air together, no ground, Belljaw as a hanging object.

Intended beat list (attack / clamp / scan / slide / counter / hang / spend / finish) is written into alt-text and overlays. The drawings do not keep the stage.

Premium unique tries harder and still poses:
- `p007` (repaired) hanging on a chain over a hole is a good single action drawing.
- Pre-repair `p007` inserts Belljaw on the far ledge — a premature boss, i.e. the generator adding the monster because “this is the dungeon story.”
- `p026` impact is a strong still (forelimb, body arc, Mira planted).
- `p043` midair jump with no contact.
- `p044` / editorial `p044` is the best contact drawing in Ember: blade into ankle plate, Mira loading the spear, shards. It is still one illustration of “the hit,” not a chain of attack-counter-reversal.

CH03 volume: `p013` orange beam, `p014` spark on shield, `p022` kill arc. The Glassback exists, then Mira is on a flat floor that is not the glass catwalk, then the dead bug is on another floor. Aftermath `p023` (bloody palm + loot) is a product shot.

City: `ch01-s02-p03` pylon exploding is a reaction still (kneel, reach, debris). `ch04-s03-p03` is a leap-pose with two witnesses. CH08 has no fight; it is sitting and glowing.

Borrowed Down is the exception that still is not fully choreographed, but it is *physical*: rope directions on the CH03 contact sheet, Mae pushing a slab while Dax hauls, people under the stone. Weight is visible. That is closer to comics action than Ember’s air-jumps.

North Garden inspected pages are blocking/acting, not combat.

### 5. Phone-size (390×844) readability of the HTML/SVG stack.

**Observation from CSS, SVG type sizes, and phone-preview strips. Inference about actual 390×844 rendering is labeled.**

**Ember volume**
- Phone reader CSS: `.scroll{width:min(100%,430px)}`. That is **not** 390. Full reader is 1024.
- Each “panel” is a full 2:3 illustration stacked with a 12px gutter. No in-page panel grid. Sticky chapter menu + panel-nav eat vertical space.
- Lettering is a second `<img>` overlay on top of the raster. The SVG *also* embeds `<image href="...png">`. In this review worktree `experiments/` does not exist, so a local open of the HTML cannot show art. **Inference:** the stack is not portable without the gitignored raster worktree.
- Type: Arial 36.8px in a 1024×1536 viewBox. At 390 CSS pixels that is ~14px; at 430px ~15.5px. Readable for 2–3 lines. `p003.svg` puts **nine** tspans in one balloon and another nine in a second balloon over the two-shot. That will brick a phone.
- `p001` caption is a dark 7-line block over the upper-left of the establishing shot.
- `p013` mixes a huge ivory balloon (8 lines) with open stroked caption at the bottom.
- `p007` action uses open stroked dialogue on the cream field — contrast is fine; it is still a paragraph on a fight.
- `p019.svg` and `ch05/p022.svg` are empty of lettering. The “class terminal” and “60 XP / party-trust” beats are not on the page. System information is in the HTML header chips (`LV 4 · XP 45/140`), not in the art.
- `read-all.html` is 240 stacked full-bleed images in a 430px column. **Inference:** scroll rhythm is a brick of equal-height posters; loading 240 lazy images plus 240 SVG overlays is heavy.

**Premium 52**
- `.reader.phone{max-width:390px}` — this is the only Ember surface that actually targets 390.
- Deep-gutter class on selected panels (`p001`, `p029`, `p037`, `p044`, `p046`, `p052`) is real vertical-pacing intent.
- Hybrid balloons are organic blobs, not 8-line rectangles. `p005` “Tell me that bright edge is old.” / “Opened clean.” is the right length for phone.
- HUD cards (`p004` Elian LV3, `p010` Belljaw LV6) use ember-orange strokes and 34.8px type (~13px at 390). Tight but designed.
- SFX exists: `p002` “GONNNG” at 71.7px italic. That will read.
- `p001` hybrid SVG is empty (title only). Opening panel has no lettering in the overlay.
- Rasters are a mix of `ch01-unique`, `benchmark/targeted-edit`, and `editorial-clean`. **Observation:** the 52-panel “chapter” is not one drawing pass; phone scroll will show style/lighting pops.

**Borrowed Down**
- Phone preview is a precomposed vertical strip of square panels with a cream caption band under each.
- Balloons in the art are **blank paper rectangles**. Dialogue lives under the panel as `MAE / Pin four is singing.` At 390px the art balloons are empty holes. That is a lettering failure, not a size failure.
- Square panels on a 390×844 viewport letterbox or crop. The strip shows many small squares, readable as thumbnails, weak as immersion.

**City Keeps Oaths**
- Viewer phone mode loads `{chapter}-phone-preview.png`, described as “Complete chapter at 390-pixel reading width.”
- Inspected `ch01-phone-preview.png`: landscape paintings stacked, white rounded balloons with speaker names, some SFX (`KRAK`, `TIK...TIK`, `SSSSK`). Balloons are actually on the art in the strip (unlike Borrowed Down).
- Landscape 3:2 paintings in a 390-wide phone means each panel is short; the strip is a long film of wide images. A lot of sky/road, little face size except the dedicated close-ups.
- Desktop viewer is a 960px frame with sidebar — not a native 390 reader.

**North Garden:** no phone reader on the inspected accepted pages. Actstage stills are landscape 16:9-ish.

---

## Per-pipeline visual facts

### north-garden-legacy-local

Drawing language: graphic-novel ink, hard blacks, limited palettes (fire orange vs cold window blue). This is the only pipeline that looks like someone chose a print comic method rather than a generative “anime” default.

Kitchen sequence (`pagecomp3`):
- `p06`: Soren seated at table with laptop, Sigrid at stove with lantern, open dark door.
- `p07`: same two people, but the room is a different kitchen (wood stove left, orange door-light right, laptop on the near table).
- `p08`: Soren on a stool by the stove, Sigrid at the table. Best acting: two people not looking at each other.
- `p10`: brick *fireplace* instead of stove, different shelf wall, Sigrid at the hearth. Spatial continuity of “the kitchen” fails even while character IDs hold.

`pagecomp/page01_p08` is a tighter two-shot (Soren’s back, Sigrid chin-on-hand, newspaper, mug). More comic than the later wide rooms.

Actstage: same man in a forest, webtoon-flat vs painted-grey. Style probes, not a sequence. Webtoon version is generic “man in coat in woods with geometric overlay.”

No lettering, no HUD, no monster, no fight on inspected pages. Quiet staging is the strength. Architecture mutation is the sequential failure.

### borrowed-down

Print/linocut/pressure-print: coral sky, teal water, dirty yellow coat. Opening `s01-p01` is a harbor crane city that does not look like Ember’s dungeon.

Lettering system is broken as comics: every inspected lettered panel has a reserved blank rectangle in the art and a typeset caption *below* the border. `s01-p03` SFX is `KONNNG` under the panel while a blank box sits on the splash. `s02-p03` diegetic `EAST LEAN: SEVERE` is the most original “system” graphic in any pipeline — and it is still a caption, not in-world type.

CH03 contact sheet is the best sequential page in the review: rope arrows, weight transfer, market, wave, rescue slab, aftercare. `ch03-s04-p04` has actual overlapping bodies and a problem (stone, water, trapped people).

CH10 creature-fail strip: a generic kaiju head appears in a dock winch story. The fail is labeled and preserved. That is honest. The kaiju is also generic prestige-monster, unlike Mae.

### the-city-keeps-oaths

Clean painted webtoon stills, landscape. CH01 is a road-seam opener: Sola finds a crack, talks to her cuff, crowd runs, pylon breaks, key ritual. Continuity of braid/cuff/staff-man is above Ember. Hands are better than Ember `p013` but still soft.

Lettering on the compact review and phone strip is real balloons with names (`SOLA`, `HAMN`, `WITNESS`). Placement is often top-center or floating, not tail-locked to mouths. SFX is sparse and typeset.

CH04 is mostly table/map/glow. `ch04-s03-p03` leap is a single action still. CH08 is almost all sit-and-talk in blue night — pretty, low density, no fight.

Viewer is a productized HTML shell (modes: full / phone / review). Phone is a screenshot of the chapter, not a live SVG stack.

### ember-lattice-ten-chapter-volume

240 tall illustrations, Candidate B charcoal-cel, teal/ivory/brass/ember. Monster design (Belljaw, Glassback) is the art-direction win. Character design is the loss.

Lettering v2 (owner-noted 84% ivory, 4px stroke, Arial) is a production overlay, not drawn lettering. Balloons are rectangles or butted shapes. UI is a dark brass card. Many “system moments” have no overlay (`p019`, `ch05/p022`). Dialogue is essay-length.

CH04 `p018` Sable lifting a dripping seal while the Bailiff stands idle is the best *story* still in the volume: someone else won. It is still a key-art pose in ankle-deep water.

CH05 `p004` item tray is a good inventory graphic (ampoule, lens, seal, chain, glands). Progression is shown as objects more clearly than as numbers.

CH10 `p024` four adults walking into an orange slit is a poster ending, not a cliffhanger panel.

### ember-lattice-premium-rd-52-panel

Same story as volume CH01, more cuts (52 vs 24), more cameras, more painterly light. Unique pass adds hanging (`p007`), two-shot release (`p008`), impact (`p026`), midair (`p043`). Failures gallery shows the generator injecting Belljaw too early; repairs remove it without restaging.

The 52-panel reader is a collage of three raster sources (unique, targeted-edit benchmark, editorial-clean). That is visible as lighting/texture changes. Hybrid lettering is the best Ember lettering (organic balloons, short lines, SFX, HUD). Opening overlay empty.

### ember-lattice-editorial-gear-hybrid

Editorial-clean rasters are denoise/sharpen/spark-reduction of the unique/benchmark poses. `p044` unique vs `p044` editorial: same staging, fewer decorative sparks. That helps `controlled_detail`. It does not create new acting or choreography.

Gear HTML is a text bible with six geometric SVG “family” icons (hex + cross + circle). Future-cast HTML is twelve circle-head / triangle-arm diagrams. These are not sequential art and not character drawings. They do not raise silhouette or appeal scores for the *pages a reader would scroll*. They do show that the pipeline can emit maintainable vector placeholders.

---

## AI artifact notes (observation)

- Repeated face template (Ember Elian; City Sola three-quarter).
- Over-smooth skin against over-cracked stone.
- Environment reset between panels (cream cyclorama; outdoor sky in a pit fight; kitchen stove vs fireplace).
- Extra or melted fingers (`volume p013`; several reaching hands).
- Decorative ember specks and edge chatter (named in editorial repairs: `edge_chatter`, `chromatic_speckles`, `excessive_micro_texture`, `indiscriminate_bloom`).
- Premature boss insertion (premium `p007`/`p008` pre-repair).
- Generic kaiju (Borrowed Down CH10 fail).
- Floating action poses with no contact shadow (`premium p043`; volume `p015`).
- Empty generator-reserved lettering boxes (Borrowed Down, systematically).

## Strongest panels (as stills)

1. Ember volume `pilot/source/p004.png` — Belljaw scale intro.
2. Ember volume `pilot/source/p001.png` — pit establishing.
3. Ember premium `ch01-unique/p026.png` — backhand impact.
4. Ember editorial-clean `p044.png` — ankle split contact.
5. Ember volume `ch04/source/p018.png` — Sable takes the seal.
6. Borrowed Down `ch03-s04-p04.png` — slab rescue.
7. Borrowed Down `ch01-s01-p02.png` — Mae on pin four.
8. City `ch01-s01-p05.png` — Sola headache close-up.
9. City `ch01-s03-p03.png` — two-character key ritual.
10. North Garden `pagecomp3/page03_p08.png` — kitchen not-looking.

## Weakest sequences

1. Ember volume CH01 `p006→p010` — dungeon / cream studio / outdoor ruins in five fights.
2. Ember volume CH01 `p013` hands/talisman as a “system spend.”
3. Ember premium `p043→p044` — levitation then contact, stages don’t match.
4. Ember volume lettering on `p003` (two 9-line balloons) and empty `p019`/`ch05/p022`.
5. Borrowed Down entire lettered CH01 — blank boxes, captions underneath.
6. City CH01 landscape stack on phone — pretty, short, low face size.
7. City CH08 — 24 conversation paintings, no visual turn.
8. North Garden kitchen — four rooms claiming to be one.
9. Ember volume CH10 `p018`+`p022`+`p024` — power pose, beam into tower, group poster; no readable fight geography.
10. Gear/future-cast SVG icons presented as if they were cast/gear design sheets.

## Production-fitness notes (inference, lower confidence)

- Volume throughput is high (240 rasters + SVG overlays + five HTML surfaces per chapter). Continuity and lettering still require panel-by-panel human rejection.
- Repairs are full re-gens with “smallest changed instruction” (premium failures gallery). That is expensive and does not restage.
- Rasters are gitignored and live in other worktrees; this worktree’s HTML cannot display them. Reproducibility of `imagegen-default` is already disclaimed on the volume hub.
- SVG lettering *is* editable and localizable in principle. Balloon geometry is fitted to English dumps, so localization will overflow.
- North Garden’s local/control approach did not actually lock the kitchen. The 3D-contract hypothesis is not proven by the accepted four.

No strategy recommendation. Visual facts and scores only.
