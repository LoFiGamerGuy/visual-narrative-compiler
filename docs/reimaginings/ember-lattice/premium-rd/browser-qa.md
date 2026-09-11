# Ember Lattice premium editorial browser QA

- Date: 2026-09-04 (America/New_York)
- Browser: connected Chromium/Chrome session
- Local origin: `http://127.0.0.1:8878/`
- Viewports: 390 × 844 phone, 1024 × 768 compact desktop, 1440 × 1000 wide desktop
- Result: **PASS**

## Exercised surfaces

| Surface | Browser evidence | Result |
|---|---:|---|
| Phone reader | 52 figures; 104/104 decoded art and overlay images | PASS |
| Full reader | 52 figures; 104/104 decoded art and overlay images | PASS |
| Compact reader | 52 figures; 104/104 decoded art and overlay images | PASS |
| Action reader | 24 figures; 48/48 decoded art and overlay images | PASS |
| Grayscale diagnostic | 52 panels; 104/104 decoded images | PASS |
| Safe-zone / protected-region diagnostic | 52 panels; no broken decoded images | PASS |
| Lettering-collision / reading-order diagnostic | 52 panels; 104/104 decoded images | PASS |
| Dialogue-density / phone-type diagnostic | 52 panels; no broken decoded images | PASS |
| Clean-art / noise diagnostic | 52 panels; no broken decoded images | PASS |
| Prior-versus-revised comparison | 52 matched cases; 208 image references | PASS |
| Failure / repair gallery | 14 preserved failure cases; 28 image references | PASS |
| Gear, item, and upgrade hub | 6/6 text-free family concepts decoded | PASS |
| Future-cast hub | 12/12 text-free character concepts decoded | PASS |
| Main hub, benchmark hub, evidence hub | navigation and responsive layout | PASS |

The phone reader was traversed from beginning to end after the final lettering corrections. Every lazy image decoded: 104 healthy, zero incomplete, zero broken, 52 distinct art sources, and 52 distinct overlay sources. The compact-desktop full reader also decoded all 104 images. Browser traversal found no horizontal document overflow: phone `scrollWidth/clientWidth` was 375/375, and every desktop surface reported `scrollWidth <= clientWidth`. The complete deterministic build audit separately resolved every local HTML, SVG, image, and navigation reference.

## Visual findings corrected during QA

- P033: redirected all four balloon tails to the correct member of the Elian/Mira two-shot.
- P034: moved the Spark Talisman Ledger block out of Elian's face and into the dark upper-left architectural margin.
- P049: split a shared-speaker line into five unambiguous turns; Elian's absent responses now use a dashed off-panel contour, while one compact tail anchors Mira's solid response family without crossing adjacent balloons.
- P052: moved Mira's closing line into the upper-right margin beside her silhouette and redirected Elian's response toward his lower-left figure.

Phone screenshots were visually inspected at the first page, the P033–P038 editorial cluster, the P048–P052 closing cluster, and the final panel. Desktop screenshots were inspected in the full reader, lettering-collision diagnostic, gear hub, and future-cast hub. Type remained legible, the art stayed visible beneath separate editable SVG overlays, and navigation remained usable. The accumulated browser warning/error log was empty.

## Honest scope note

The browser confirms rendering, layering, responsiveness, asset decoding, navigation, and console cleanliness. It does not make the provider-generated source rasters seed-reproducible or commercially licensed; those limitations remain recorded in the manifest and evidence pages.
