# Lettering, system-UI, and mobile-reading audit (draft)

Access date: 2026-09-06  
Role: Lettering, System-UI, and Mobile-Reading Specialist  
Worktree: `C:\AgentWorkspaces\anime-pipeline-total-review-20260906-211925`  
Machine-readable companion: `docs/research/anime-pipeline-total-review/evidence/lettering-measurements.json`  
No images were altered. Phone type sizes are **estimates** from `svg font-size × display_width / viewBox_width` unless a diagnostic overlay already stamped a phone-px label.

## Direct answers

**Does lettering rescue unclear art?**  
Not as a general rule on the premium hybrid page, and not as the declared contract. ADR-EL002 says every chapter must still work if lettering is hidden; lettering is supposed to supply voice, causality, and exact system state. The 52-panel premium hybrid overlay has 15 empty/silent SVGs. Action beats mostly stay silent or take a single vector SFX (`GONNNG`, `KRAK`, `THOOM`, `KLANG`). System plates *do* carry numbers the drawing cannot show (XP fractions, HP/Qi, class path). That is genre machinery, not a balloon explaining a muddled pose. The ten-chapter volume is closer to rescue: CH01 P003/P005 put 9-line rounded-rect speeches over the art that restate geography and stakes the panel is already tagged as showing. Borrowed Down’s empty on-art beige boxes hide drawing without delivering copy on the panel. City’s raw panel PNGs are unlettered and often readable; lettering is a later white-card overlay.

**Did v2 actually improve the page?**  
On the premium 52-panel slice, **yes for obstruction, tails, collisions, and phone size; no for “smaller type” or “deeper wording.”** Hybrid/baseline/raw overlays are byte-identical to each other (52/52). They differ from `original-lettering` on 37/52 panels (the other 15 are shared silent SVGs). Hybrid shrinks occupied lettering (plan area 221.48% panel-equivalents vs original bbox-sum estimate 342.1%; editorial report 367.7% → 221.5%). P033 stops stacking open outlined copy on top of balloons. P049 stops three overlapping original balloons in one corner. Type gets *larger* (dialogue 29.7 → 41.0 SVG px), copy gets *shorter* (SVG spoken/open 200 → 175 words; plan spoken 161; 8 panels lose words, 0 gain). The volume “lettering v2” page is a different object: 24-panel chapters with 300–520 authored dialogue words, 84% ivory cards, and a 430 px phone column rather than 390.

**Localization resilience (expanding text)?**  
Weak on every Ember surface. Copy is hardcoded `<tspan>` lines inside fixed path geometry. There is no reflow, no overflow node, no extra-width budget. Hybrid’s larger type inside more compact balloons has *less* room for German/French expansion than original’s smaller type inside larger cards. Volume CH01 already wraps 9 lines into ~34% width rounded rects. City balloons are short English in tight white rounds. Borrowed Down is the only design that can grow: speaker/caption bands live *below* the art. Its on-art beige rectangles still do not resize with language.

**SFX integration vs stickers?**  
Premium hybrid SFX are not boxed. They are italic Arial Black, fill `#ff7447`, charcoal stroke, `paint-order="stroke"`, rotated in a `<g>`, placed on chain/impact corners (`P002 GONNNG`, `P007 KRAK`, `P017 THOOM`, `P026 KRAK`, `P044 KLANG`, `P052 GONNNG`), font-size 71.7 → **estimate 27.3 CSS px at 390**. That is closer to a vector sound effect than a dialogue sticker, but it is still a generic outlined word, not a drawn onomatopoeia integrated into the line art. City uses small black SFX labels (`THUM`, `KRAK`, `TIK...TIK`, `SSSSK`) that sit in the scene; still stickers, better scale. Borrowed Down has no on-art SFX in the sampled lettered panels.

**Did the editorial pass satisfy ADR-EL002 on the page?**  
**Partial. Not fully.** Owner required deeper wording, smaller less obstructive dialogue, transparency/overlays, and more visible system menus. Hybrid is less obstructive and more phone-legible. It is not smaller, not deeper, and not 84% transparent. System type is more visible and the copy is more abbreviated. Details below.

---

## What was measured

| Surface | What | Path |
| --- | --- | --- |
| Premium overlays | 52 SVGs × 4 folders | `docs/reimaginings/ember-lattice/premium-rd/panels/{original-lettering,hybrid,baseline,raw}/` |
| Premium readers | phone / full / compact / action | `docs/reimaginings/ember-lattice/premium-rd/readers/` + `assets/premium.css` |
| Premium diagnostics | collisions, density, UI density, safe zones | `docs/reimaginings/ember-lattice/premium-rd/diagnostics/` |
| Lettering plan | 59 units, areas, phone_font_px | `production/reimaginings/ember-lattice/premium-rd/ch01-lettering-plan.json` |
| Editorial report | before/after panel index | `reimaginings/ember-lattice/premium-rd/lettering-editorial-report.md` |
| Volume overlays | 10 × 24 SVGs | `docs/reimaginings/ember-lattice/volume/chapters/ch0N/panels/` + `volume/assets/volume.css` |
| Volume metrics | authored words / density | `production/reimaginings/ember-lattice/volume/dialogue-and-density-metrics.json` |
| ADR / bible / research | owner + craft rules | `docs/reimaginings/ember-lattice/adr/ADR-EL002-owner-approval-and-lettering-v2.md`, `reimaginings/ember-lattice/lettering-and-ui-bible.md`, `docs/reimaginings/ember-lattice/research/lettering-and-dialogue-research.md` |
| Borrowed Down | lettered PNGs + phone/compact | `C:\AgentWorkspaces\anime-pipeline-reimagining-20260903\experiments\reimaginings\borrowed-down\` (raster, inspect in place) |
| City | unlettered panels + phone/compact + lettering-wave | `C:\AgentWorkspaces\anime-pipeline-reimagining-clean-webtoon-20260903-213010\experiments\reimaginings\the-city-keeps-oaths\` |

Word counts use the editorial regex `[A-Za-z0-9+−→/]+`. Balloon/UI area from SVG path bounding boxes is an **estimate**, not filled-path area. The lettering plan’s `total_lettering_area_pct` (normalized boxes) is the locked editorial number.

---

## 1. Premium-rd: original vs hybrid vs baseline vs raw (identical overlay art)

**Identity.** `hybrid`, `baseline`, and `raw` overlay SVGs are the same bytes on all 52 stems. Readers (`phone.html`, `full.html`, `compact.html`) all point at `../panels/hybrid/`. The three workflow folders do **not** test three lettering systems; they reuse one editorial overlay on three art pipelines. The only prior/revised lettering pair is `original-lettering` vs `hybrid`.

| | original-lettering | hybrid = baseline = raw |
| --- | --- | --- |
| Panels | 52 | 52 |
| Silent/empty overlays | 15 | 15 |
| Spoken/open words (SVG parse) | 200 | 175 |
| Plan spoken words | — | 161 (59 units; 57 baseline units) |
| UI words (SVG parse) | 166 | 116 |
| SFX words | 6 | 6 |
| Ivory balloon shapes (estimate) | 35 | 39 |
| UI plates (estimate) | 11 | 11 |
| Q-path tails | 35 | 34 |
| Dialogue SVG `font-size` | 29.7 | 41.0 |
| UI SVG `font-size` | 26.6 | 34.8 |
| SFX SVG `font-size` | 71.7 | 71.7 |
| **Estimate** CSS px at 390 | dialogue **11.31**, UI **10.13**, SFX 27.31 | dialogue **15.62**, UI **13.25**, SFX 27.31 |
| Diagnostic phone stamps | — | 15.6 / 13.3 / 27.3 |
| Balloon fill-opacity | 0.94 | 0.94 (thought units 0.88 dashed) |
| UI fill-opacity | 0.90 | 0.90 |
| Plan area sum | editorial “before” 367.7% | **221.48%** |
| Bbox-sum estimate | 342.1% | 204.6% |
| Balloons >38% width (bbox estimate) | 5 | 0 |
| Balloons >44% width | 0 | 0 |

Hybrid never *adds* spoken words vs original. Eight panels lose words (P005 11→9, P008 10→9, P012 16→15, P033 22→21, P036 8→6, P038 14→9, P045 9→4, P049 20→12). Geometry is rewritten even when word count is unchanged (P030 bbox-area estimate 14.9%→6.5%).

### Balloons, tails, reading order

Original balloons are taller, with quadratic tails that often aim at canvas center `Q512.0,844.8` (P005, P033, P049). That is a compositor default, not a mouth. Hybrid balloons are compact irregular paths with short local tails.

**P033 (explicit dialogue composition).**  
Original: two huge ivory balloons plus two open outlined speeches (`font-weight="900"`, `paint-order="stroke"`) sitting on the same coordinates as balloon copy — a real overlay collision inside the SVG. Hybrid: four separate balloons, last unit dashed (`stroke-dasharray="8 6"`, opacity 0.88, “I know.”). Collision diagnostic stamps reading order 1–4 and `AREA 12.0% · SPOKEN 20 WORDS` (plan: 21 words / 12.00% area; word-regex difference on `didn't`).

**P049.**  
Original: three balloons sharing the top-left origin, long center tails, one speech packing “Can you feel both hands? Any blood when you breathe?” Hybrid: five stacked right-edge units — `Both hands?` / `Yes.` / `Blood when you breathe?` / `No.` / `Good. No third answer.` Plan area 8.91%. This is the editorial “split/decompressed” beat. It is more playable, not deeper.

**P005 on identical art.**  
Original: “Tell me the bright edge is old.” / “It was opened clean.” font 29.7, long tails. Hybrid: “Tell me that bright edge is old.” / “Opened clean.” font 41.0, short tails. Opacity stays 0.94, not bible 0.84.

### Type hierarchy

Hybrid has a real three-tier scale: dialogue 41.0 / Ledger 34.8 / SFX 71.7. Original has the same hierarchy at a smaller, phone-illegal size. Face is Arial everywhere. Emphasis is weight (720/750/900), not a lettering font. Bible asked 30–36 px at 1024 for dialogue; hybrid **exceeds** that (41) in order to clear the 15 CSS px phone floor. Original sits in the bible 30–36 band and **fails** the phone floor.

### System UI vs dialogue

Distinction is clear on the page:

- Dialogue: ivory `#f6f0e4`, charcoal stroke, dark fill `#12151a`, centered tspans, tails.  
- Ledger: dark `#10151c` at 90% opacity, ember `#ff7447` outline, brass rule, ivory caps, `letter-spacing=".4"`, no tails.  
- SFX: ember italic outlined, no box.

Hybrid menus are **more visible** (34.8 vs 26.6; **estimate 13.25 vs 10.13 CSS px at 390**) and **more abbreviated**. P004 original: `ELIAN VOSS · LV 3 · XP 60 / 100 · SALVAGER · BREATH SEED I · HP 44 / 52 · QI 31 / 40` on four lines. Hybrid: seven short lines (`ELIAN VOSS ·` / `LV 3` / `SALVAGER ·` / `SEED I` / …). P048 original coverage stamp in the stale UI-density overlay is **34.8%**; hybrid plan area is **20.35%** with three stacked plates. P051 original UI plate runs y≈154–968 (most of the panel). Hybrid shrinks it and keeps two bottom balloons.

P048 is the one panel where lettering *is* the beat (boss defeat / XP / Cinder-Key). Hide it and the drawing does not report 85 XP or LV 3→4. That matches ADR “exact system state,” not “rescue unclear art,” as long as the loot object remains drawn.

### Negative space, gutters, rhythm

Safe-zone diagnostics draw `NEGATIVE SPACE` dashed orange rects plus protected labels (`PRIMARY_ACTION_SILHOUETTE`, `FACE_EYES`, `EXPRESSIVE_HANDS_WEAPON_CONTACT`, `EQUIPMENT_INJURY_EVIDENCE`). Lettering plan `protected_overlap_types` is empty on every unit. That is a box-vs-box check against **synthetic** protected rectangles, not a pixel test against faces in the PNG.

Phone reader gutters: `.reader` gap `clamp(26px,6vw,84px)`; six `deep-gutter` panels (`P001, P029, P037, P044, P046, P052`) at `clamp(72px,14vw,180px)`; under 600 px the phone gap becomes 34 px. Full reader uses the same overlay at `max-width:1024px` (1:1 with viewBox). Compact reader is a `minmax(150px,1fr)` grid: hybrid 41 px type → **estimate 6.0 CSS px**. Unreadable. Action reader is 720 px (**estimate 28.8 CSS px**) and only the 24 action-tagged panels.

---

## 2. Phone CSS actually uses 390 px — with a volume exception

| Reader | Width rule | 390 px? |
| --- | --- | --- |
| Premium `phone.html` | `.reader.phone{max-width:390px}` in `premium.css` | **Yes** |
| Premium `full.html` | `.reader.full{max-width:1024px}` | No (native) |
| Premium `compact.html` | `.compact-grid` `minmax(150px,1fr)` | No |
| Premium `action.html` | `.reader.action{max-width:720px}` | No |
| Pilot `reader.html` / `safe-zones.html` | `.phone{width:390px}` | **Yes** |
| Volume chapter `index.html` (body.phone) | `.scroll{width:min(100%,430px)}` | **No — 430 px** |
| Volume `full.html` | `.full .scroll{width:min(100%,1024px)}` | No |
| Volume compact | `.review-grid` `minmax(170px,1fr)` | No |

Volume CSS never contains `390px`. ADR-EL002, the bible, the lettering plan viewport, and premium phone CSS all say 390. The ten-chapter owner phone reader is 430. At 430, volume 36.8 px type is **estimate 15.45 CSS px** (clears bible 15). At 390 the same type is **estimate 14.02 CSS px** (clears ADR 14, fails bible 15).

Hybrid dialogue at 390 is **estimate 15.615 CSS px** (bible 15 pass; ADR 14 pass). Hybrid UI at 390 is **estimate 13.254** (ADR wrapped system 13 pass; editorial system floor 12 pass; bible dialogue floor N/A). Original dialogue/UI at 390 are **11.31 / 10.13** — fail every phone floor in ADR, bible, and editorial report.

---

## 3. Diagnostics vs published hybrid

There is **no** diagnostics JSON in this tree that lists collision FAIL rows. `ch01-lettering-plan.json` stores `protected_overlap_types: []` on all 59 units. `lettering-collisions.html` is a visual stamp layer (reading-order indices + `Npx PHONE` + `AREA % · SPOKEN N WORDS`), not a fail list. Stamped phone sizes on that layer: **13.3, 15.6, 27.3** — hybrid, not original. Stamped area sum: **206.9%**. Stamped spoken sum: **154** (plan 161; regex/contraction drift).

`dialogue-density.html` embeds hybrid-like 41.0/34.8 type on 32 plates.

`ui-density.html` is **stale**. 32 plates still carry original-like 26.6/29.7 type. P048 stamp: `UI/LETTERING COVERAGE 34.8%` matching original, not hybrid 20.35%. Anyone reviewing only UI-density will overstate coverage.

Safe-zone HTML uses the compact grid, so the diagnostic itself is not a 390 px reading test.

Volume chapter safe-zones are a different language: green focal rect + orange lettering rect + banner `GREEN FOCAL PROTECTION · ORANGE LETTERING`. CH01 P005 orange lettering box is 399×323 over a balloon that is already 348×391 — the diagnostic restates the large card rather than proving clearance.

---

## 4. Volume chapter overlays vs premium hybrid

Phase B volume is the ADR-EL002 production contract: 24 panels/chapter, 300–520 dialogue words, 14 px phone dialogue / 13 px system, 159/60/21 density, four system moments.

Authored (`dialogue-and-density-metrics.json`): CH01 **474** words, volume **3821**, 258 dialogue units, 41 system moments. Validation JSON: 299 lettering-fit checks, 100 overlap-pair checks, 0 WARN/FAIL (the only failure class recorded is `non_vertical_source`, not lettering).

SVG parse (includes captions; see JSON caveat):

| Ch | Authored spoken | SVG spoken/open | SVG UI words | Silent | Fill opacities | Area bbox-sum estimate |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | 474 | 518 | 48 | 1 | 0.76–0.84 | 176.1 |
| 02 | 397 | 402 | 55 | 6 | 0.76–0.84 | 152.2 |
| 03 | 360 | 394 | 28 | 4 | 0.76–0.84 | 205.6 |
| 04 | 343 | 366 | 34 | 6 | 0.76–0.84 | 80.8 |
| 05 | 401 | 425 | 35 | 5 | 0.76–0.84 | 208.3 |
| 06 | 343 | 373 | 33 | 2 | 0.76–0.84 | 72.0 |
| 07 | 339 | 355 | 48 | 2 | 0.76–0.84 | 77.2 |
| 08 | 357 | 379 | 40 | 2 | 0.76–0.84 | 205.5 |
| 09 | 348 | 380 | 32 | 2 | 0.76–0.84 | 212.8 |
| 10 | 459 | 487 | 61 | 0 | 0.76–0.84 | 219.5 |

Volume **does** implement bible opacity (0.84 ivory, 0.76–0.82 captions/UI) and deeper wording. Volume **does not** implement premium’s compact organic balloons. CH01 P003/P005 are `rect rx="54"` cards ~348×391 (width **estimate 34%**, inside 26–38% bible band) with 9 lines of 36.8 px type. Tails are triangular `L` paths, not the original’s center-seeking `Q`. Gutters are `border-bottom:12px` — much tighter than premium phone `clamp(26px,6vw,84px)` plus six deep gutters. Compact volume type at 170 px is **estimate 6.1 CSS px**.

Premium hybrid CH01 (52 panels) is a fight-expanded slice with **161** plan spoken words — below the 300–520 chapter contract because it is not the 24-panel volume chapter. Comparing “v2 improved the page” across these two objects without that denominator is a category error.

Volume overlays also embed `<image href="...source.png">` inside the SVG. Premium overlays are lettering-only, stacked in HTML. Volume SVGs are therefore not a clean “hide lettering” toggle; the art is inside the same file.

---

## 5. ADR-EL002 / bible / editorial report vs the page

Owner text (ADR-EL002): deeper wording; smaller less obstructive dialogue; experiment with transparency or contrasting overlays; more visible system menus, leveling, XP, skills. Lettering v2 “therefore” uses compact 84%-opaque soft balloons, outlined open dialogue on validated quiet backgrounds, border-butted or linked balloons, narrower high-information Ledger menus. Phone: 14 px dialogue, 13 px wrapped system.

| Requirement | Volume CH01–CH10 | Premium hybrid 52 | Original-lettering 52 |
| --- | --- | --- | --- |
| Deeper wording (300–520 / ch) | Yes (339–474 authored) | No (161 spoken in 52 panels) | Slightly more than hybrid (200 SVG words) still not deep |
| Smaller dialogue type | 36.8 at 1024 (**est. 14.0 at 390 / 15.5 at 430**) | **Larger** 41.0 (**est. 15.6 at 390**) | 29.7 (**est. 11.3 at 390**) — smaller and unreadable |
| Less obstructive | Large 84% rounded cards | Yes: compact paths, area 221% vs 368% | No: long center tails, overlaps |
| 84% soft balloon | Yes 0.84 | **No, 0.94** (0.88 only on dashed thought) | 0.94 |
| Open dialogue on quiet BG | Used (outlined ivory) | Rare; P033 converted to dashed balloon | Used and collides with balloons on P033 |
| More visible menus | Brass plates, 31–36 px | Yes, 34.8 px, more line-breaks, less copy | Smaller 26.6 px, denser copy |
| Art works if lettering hidden | Contract yes; long cards still cover a lot | 15 silent panels; UI-only beats remain | Same silents; worse occlusion |

Editorial fail-closed rules (`lettering-editorial-report.md` / plan `rules`): normal balloon ≤15% area, total ≤25% unless exception, ≤2 speech balloons unless exception, ≤28 spoken words, speech ≥14 px at 390, system ≥12 px. Hybrid P033 (4 balloons, 12% area) and P049 (5 balloons, 8.91%) are documented exceptions. P048 (20.35%) is under 25% with a written UI-as-beat note. Original P048/P051 (~35%/33% bbox) would fail that total-treatment cap. Original phone type would fail the 14 px speech / 12 px system gates.

Bible “never below 15 CSS px at 390”: hybrid dialogue passes; volume dialogue **fails at 390 and passes at the 430 px reader it actually ships**. That is an unpublished width split, not a measurement error.

---

## 6. Borrowed Down lettered panels vs City viewer

Neither title stores SVG lettering in this worktree. Observations are from the gitignored rasters named in `coordination.md`.

**Borrowed Down** (`lettered-panels/`, `ch01-phone-preview.png`, `ch01-compact-lettered-review.png`):

- Copy lives in a **below-art band** with a red speaker/CAPTION label (`CAPTION / In Veyr, down arrives by schedule.`; `MAE / Pin four is singing.`).
- The panel still contains an **empty beige rectangle** on the drawing (dock crowd; sky beside Mae’s head). No tail, no type inside the box.
- Phone preview is a vertical stack of those lettered PNGs. Compact 30-up review makes the gutter type unreadably small; the empty boxes remain.
- This is gutter lettering plus leftover on-art **stickers with the text omitted**. Localization of the caption band is easy. The empty box still occludes art in every language.
- No HTML reader; `START-HERE.html` links PNG drafts.

**The City Keeps Oaths** (no `START-HERE.html` in the experiments folder; viewer surrogate is `ch01-phone-preview.png` and `ch01-compact-lettered-review.png`):

- `chapters/ch01/panels/*.png` are **unlettered**. P01–P03 of CH01 are silent establishing/acting shots.
- Lettering is composited only on phone/compact/reading-draft surfaces: white rounded balloons with tails, teal caption boxes, speaker chips (`SOLA`, `HARN`), small black SFX.
- CH03 `repairs/lettering-wave/ch03-before-after.png` is a real editorial pass: balloons move off faces (`CH03 BEFORE — failed lettering clearance` → `AFTER — localized safe-zone repair`). They remain opaque white cards.
- Phone scroll is the only “viewer.” There is no 390 px CSS. Type looks near-readable in the phone PNG; compact contact sheet is for placement, not reading.

**Transferable contrast.** City treats lettering as a removable overlay and will move a balloon off a face. Borrowed Down moved copy out of the art (good) and left empty boxes in the art (bad). Ember premium hybrid is closer to City’s overlay model, with a distinct Ledger language City does not have. Ember volume is closer to City’s white cards, just ivory/brass and much larger.

---

## 7. `lettering_and_mobile` dimension notes (not a full art rubric)

Scale: 0–5 anchors from `common-rubric.json`. Scores are this specialist’s lettering/mobile read only. Confidence medium: SVG/HTML measured; raster titles inspected, not pixel-counted.

### Ember premium hybrid (published 52-panel overlay)

| Dimension | Score | Evidence |
| --- | --- | --- |
| balloon_shape_and_placement | 3 | Compact irregular paths, width ≤37.5% estimate, area down to 221%. Still 94% opaque Arial cards. |
| tail_attribution | 3 | Short local Q tails vs original center-seek. SVG does not encode a mouth target. |
| type_hierarchy | 3 | 41 / 34.8 / 71.7 is a hierarchy. No lettering face. |
| sfx_integration | 3 | Unboxed vector SFX on impact vectors; still generic outlined type. |
| system_ui_distinction_and_originality | 3 | Brass Ledger vs ivory speech is unambiguous. Copy is truncated; not competitive with licensed system-page craft. |
| negative_space_planning | 3 | Declared regions + safe-zone overlays. Overlap test is synthetic. |
| phone_readability | 3 | **Est. 15.6 / 13.3 at 390** on the phone CSS that actually uses 390. Compact grid fails. |
| scroll_rhythm_and_loading_experience | 3 | Phone gap + 6 deep gutters. Overlay lazy-loads. Compact/full share the same overlay, different cadence. |
| localization_resilience | 2 | Fixed tspans, larger type, no reflow. |

Original-lettering on the same art would drop phone_readability to **1**, tail_attribution to **1**, balloon_shape_and_placement to **2**.

### Ember volume (10×24, lettering v2 contract)

| Dimension | Score | Evidence |
| --- | --- | --- |
| balloon_shape_and_placement | 2 | Large `rx=54` cards; bible opacity; still the “rounded card” failure class from `failure-correction-contract.md`. |
| tail_attribution | 2.5 | Triangle tails exist; many speeches are open/outlined. |
| type_hierarchy | 3 | 36.8 dialogue / ~31–34 UI / 68 SFX. |
| sfx_integration | 2 | Sparse (CH01 SVG parse: 1 SFX node). |
| system_ui_distinction_and_originality | 3 | Distinct brass plates; four moments/chapter in authoring metrics. |
| negative_space_planning | 2 | Orange boxes track the large cards. |
| phone_readability | 2.5 | Reader is **430 px**, not 390. **Est. 14.0 at 390 / 15.5 at 430**. 12 px gutters. |
| scroll_rhythm_and_loading_experience | 2 | 12 px panel separators. Compact 170 px grid is not a reader. |
| localization_resilience | 2 | 9-line prewrapped cards. |

### Borrowed Down

| Dimension | Score | Evidence |
| --- | --- | --- |
| balloon_shape_and_placement | 1 | Empty beige rectangles on art. |
| tail_attribution | 0 | No tails. |
| type_hierarchy | 2 | Caption vs MAE/DAX bands only. |
| sfx_integration | 1 | Not present on sampled lettered panels. |
| system_ui_distinction_and_originality | not_assessed | Not a system-menu title. |
| negative_space_planning | 1 | Boxes cover workers/sky. |
| phone_readability | 2 | Gutter type readable in the phone stack; compact not. |
| scroll_rhythm_and_loading_experience | 2 | PNG stack, no 390 CSS. |
| localization_resilience | 3 | Best of the set for expanding caption text; on-art empties still fail. |

### The City Keeps Oaths

| Dimension | Score | Evidence |
| --- | --- | --- |
| balloon_shape_and_placement | 3 | Standard white rounds; CH03 wave moves them off faces. |
| tail_attribution | 3 | Short tails toward speakers on the compact sheet. |
| type_hierarchy | 3 | Speech vs teal caption vs SFX. |
| sfx_integration | 3 | Small in-scene labels, not boxed. |
| system_ui_distinction_and_originality | 2 | Captions, not a Ledger. |
| negative_space_planning | 3 | Repair wave exists; some CH01 balloons still sit on faces in the compact sheet (P03, P05). |
| phone_readability | 3 | Phone PNG is the viewer; no 390 CSS to verify. |
| scroll_rhythm_and_loading_experience | 3 | Vertical phone preview with silent opens. |
| localization_resilience | 2 | Short English in tight balloons. |

---

## 8. What v2 fixed, what it traded, what still fails a serial editor

**Fixed on premium hybrid vs original (same 1024×1536 overlay art):**

- Occupied area (plan 367.7% → 221.5%).
- Center-seeking tails.
- P033 open-on-balloon collision.
- P049 stacked overlap.
- P048/P051 Ledger covering a third of the panel.
- Phone dialogue/UI below 14/12 CSS px.

**Traded away:**

- Wording depth (200 → 175 SVG words; 0 panels gained copy).
- Bible 30–36 px dialogue band (now 41).
- Bible 84% balloon (still 94%).
- Dense Ledger sentences (replaced by chopped lines).

**Still below a mid-tier licensed phone serial:**

- Arial + path blobs, not a lettering face or hand-tuned shapes.
- No true mouth-targeted tails in data.
- Compact/volume-compact grids are not readers (≈6 CSS px).
- Volume owner “phone” is 430 px while the contract says 390.
- Volume still ships giant rounded cards the failure-correction contract already named.
- Localization is author-time wrap only.
- SFX are competent stickers, not drawn sound.
- UI-density diagnostics disagree with the published hybrid overlay.

**Does the editorial pass satisfy the owner on the page?**  
It satisfied “less obstructive” and “more visible menus” as **visibility of type**, not as **richer system copy**. It did not satisfy “smaller dialogue” or “deeper wording” on the 52-panel slice. Transparency remains an unused default (94% ivory) with a dashed-thought exception. The volume is where deeper wording and 84% opacity actually landed, at the cost of card size and a 430 px phone column.

---

## 9. Limits of this audit

- No raster pixel-overlap against faces except visual inspection of City/Borrowed Down PNGs and SVG path geometry.
- Balloon area estimates are bounding boxes; trust `ch01-lettering-plan.json` (221.48%) for premium hybrid totals.
- SVG word counts can differ from plan/authoring counts on contractions and captions.
- baseline/raw overlays were not a lettering experiment.
- City has no HTML viewer in the experiments tree; the phone PNG is the viewer.
- North Garden CH05 lettering (ADR-0090 88% rehearsal, 13 px bands) is out of this page’s Ember/City/Borrowed Down focus except as prior art that already proved small phone type and outside-art bands.
