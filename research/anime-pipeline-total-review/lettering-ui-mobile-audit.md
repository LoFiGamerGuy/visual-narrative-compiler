# Lettering, system UI and mobile audit

**The editorial pass makes text larger and some exchanges much easier to recover, but it does not establish finished lettering.** Same-art comparison is essential: original P033 has overlapping utterances; the revision separates them, yet text still crosses curved balloon boundaries. Both improvement and remaining failure are visible. [Independent matched review](evidence/visual-review-b.md#b09-premium52-and-b10-editorial52-matched-comparison), [actual comparison reader](/mnt/c/AgentWorkspaces/anime-pipeline-ember-lattice-editorial-gear-20260904/docs/reimaginings/ember-lattice/premium-rd/comparison/index.html).

## Measured change on the same52 narrative sources

| Measurement | Premium before | Editorial after | Limit |
|---|---:|---:|---|
| Source positions / distinct selected images |52/52|52/52|12 after-images filtered;52 distinct is not52 correct story beats |
| Text/SFX/UI units |57|59|Units are not all balloons |
| Actual SVG word-token total |349|308|Includes SFX/UI and explicit tokenizer; not the volume’s3,821 authored dialogue count |
| Median / maximum words per panel |4/35|4/27|Words alone do not measure reading difficulty |
| Median summed authored lettering rectangle area |5.44%|3.66%|Sum can double-count overlaps; not actual balloon/glyph pixels |
| Maximum authored rectangle area |34.83%|20.35%|Smaller declared area can still overlap faces or spill copy |
| Minimum rendered type at identical362px image width |9.40px|12.30px|This isolates SVG change; prior actual mobile image width358px gives about9.30px minimum |
| Median rendered type at362px |10.50px|14.49px|Typeface/weight, contrast and containment still need visible review |
| Silent panels / action-labelled panels |15/24|15/24|Labels are authored; no inference all actions occur |

Computed from shipped overlays and manifests in [structural-measurements.json](evidence/structural-measurements.json). Current true390×844 mobile art width is362px after shell padding. Initial desktop-scrollbar stress width347px gave11.79px minimum UI; this is a narrower-browser stress result, not a claim the final true390px mobile minimum fails its12px floor.

## Direct visible findings

- **P005:** larger, shorter dialogue and smaller containers improve glance reading. First-line glyphs cross the sloping/curved upper contour. A rectangular fit test misses the actual balloon interior.
- **P033:** old overlapping exchanges are substantially repaired. Four separated utterances still have contour crossings and weak/long tail paths. The selected seated art also contradicts the active threat state; a letterer cannot solve that source error.
- **P048:** more readable reward strips with less empty space. The design remains primarily a report; value comes when the surrounding action makes the gain desirable.
- **P004/P051:** UI occupies visible facial-performance space. Calling its declared box “negative space” does not make the source pixels empty.
- **P012/P049:** upper lines visibly sit outside intended balloon boundaries. P034 UI text extends below its small dark rectangle.
- **Volume CH07/P016 and CH10 ending:** large explanations/status summaries clip or compete with movement and faces. Repeated orange italic `SHINK` makes different material/action events sound and feel interchangeable.

An image `naturalWidth>0`, no console error and a12px font pass do not establish these visible facts. The pilot reader demonstrates an even stronger false pass: its SVG images load, yet nested source art is absent in the opened browser surface, leaving overlays against black. Source art still exists and is evaluated separately. [Visual B pilot inspection](evidence/visual-review-b.md#b06-ember-pilot-delivery-versus-source).

## Reading order, tails, gutters and scale

The older Borrowed bands identify speakers clearly but consume blank in-art parchment plus separate caption space. City’s short white speaker cards are more quickly readable, yet their geometry still hides faces and lacks expressive tail attribution. CH05 cadence has a valuable varied footprint and clear clues; external speech strips remain an unfinished lettering solution. These differences matter more than a branch label saying “clean” or “premium.”

For editorial52, every source is1024×1536, rendered543px high. Most figure starts are610.72px apart, with34px inter-figure gap; the longer106px gaps provide a few pauses. Total32,639px is38.67 viewport heights including review chrome. This is continuous layout evidence, not a reading-time estimate. Detailed portrait canvases still give many inserts, conversations and impacts similar weight. Change the storyboard footprint and image hierarchy, not only the space between rectangles.

The volume’s review navigation and end-state badges are useful for audit, but its opening reveals outcomes before the reader reaches the scene. Keep diagnostics and end-state summaries in an optional review surface; a production reader should allow the reveal to occur in sequence. Preserve navigation and source access for editors without making bookkeeping the opening experience.

## Lean lettering repair specification

1. Fix source-to-beat fidelity first; independently annotate actual faces, hands, contact, gear and speaker mouths before drawing balloons. Do not regenerate annotations to avoid text.
2. Shape containers around readable line breaks and actual glyph bounds, including curved shoulders, not just normalized boxes. Use sufficient interior padding; avoid tails crossing copy or the wrong speaker.
3. Render the **same art** with original/revised overlays at actual390px phone width and full size. A screenshot containing source pixels and lettering is the acceptance artifact.
4. Preserve readable14px dialogue/12px UI project floors. When text does not fit, shorten/split or revise composition; do not use emergency shrinking. These floors are proposed project constraints, not universal platform standards.
5. Give UI its own information hierarchy and distinctive original grammar: current choice/cost, then physical effect, then payoff. Full arithmetic stays in records. More menus remain possible when they serve a scene.
6. Use SFX scale, placement and shape to describe force/material, not one default angled word stamped above a pose. Preserve separate editable SFX for localization.
7. Add ordered transcript/speaker/SFX/action descriptions, keyboard navigation and focus. Raster/embedded-SVG text is not automatically accessible because the HTML shell validates.

The frozen next-pilot proof includes+30/+50% copy expansion as artificial stress cases. Real localization remains untested and requires language review. Contrast must be measured against the actually composited balloon/backdrop; global palette values alone do not certify it. [Industry lettering/accessibility sources](industry-research.md#lettering-localization-and-accessibility), [next pilot](next-pilot-specification.md).
