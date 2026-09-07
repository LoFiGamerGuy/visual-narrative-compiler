# Original storyboard layout implementation

The fourteen SVG diagrams in `production/sequence-pilot/boards/` were authored from the frozen pilot plan. No prior audit drawings, protected worktree artwork, generated reference sheets or published comic panels were read or copied for this task. They are code-native composition controls, not finished illustration or proof of a production route's drawing quality.

Each panel uses the frozen width-to-height ratio: a 390-unit viewBox and its specified height. Background, threat, actors, props and effects are separate editable SVG groups. Nera uses a yellow cape, Odo a broad blue jacket and silver hair. Figures use adult body proportions; the sentinel is a slate kite body with three articulated legs and a violet gill. Blank pale outlined rectangles reserve lettering space without baking any story copy into the artwork.

`layouts.json` records the source plan hash, each SVG hash, expected actor positions, face/contact exclusion rectangles, lettering margins and explicit cropped/offscreen objects. These are **expected layout annotations**, not observations of generated art. They must not be copied into a semantic review as if an independent reviewer had inspected a candidate.

The original continuity choices are explicit: west-left release cable to east-right shutter; one sealed flask transferred in P02 and P10; P07 approach separated from P08 contact; P09 side-leg reversal; one Nera body following P11's continuous braking arc; P12 exposed joint contact with two staff pieces; P13 adults east of the lowered shutter and living threat west; P14 retained hand scrape and short staff piece. Charge transactions and earned unlock are supplied by editable UI from the frozen plan, never invented as image-observed state. Close crops list intentionally offscreen props.

Browser inspection of the contact sheet and action sheet led to hand/prop alignment corrections in P02, P08, P12, P13 and P14. This is author self-check of a diagram, not independent semantic approval. Small faces and gesture economy remain thumbnail-level; this artifact does not demonstrate final acting, anatomy, character appeal or mobile lettering acceptance.

Rebuild with `python3 production/sequence-pilot/boards/build_boards.py`. With an already running isolated Chromium CDP browser, `node production/sequence-pilot/boards/render_boards.mjs 9337` renders all panels at 780 px width and exactly twice the frozen height to ignored `boards/png/P01.png` through `P14.png`. The renderer opens and closes its own target. `render-qa.json` records dimensions, five editable groups, zero external image dependencies, zero baked SVG story-text nodes and no XML parse error for each panel. These checks establish render integrity only.

No human approval, renderer comparison win, final-art quality result or paid spend is asserted.
