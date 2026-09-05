# Premium browser QA

- Date: 2026-09-04 (America/New_York)
- Browser path: in-app Chromium session against `http://127.0.0.1:8877/`
- Desktop viewports: 1920 × 1080 (initial full pass); 1440 × 1000 (final unique-art pass)
- Mobile viewport: 390 × 844
- Result: PASS

## Surfaces exercised

| Surface | Logical panels/outputs | Loaded DOM images | Result |
|---|---:|---:|---|
| Phone reader | 52 | 104 art/overlay layers | PASS |
| Full reader | 52 | 104 art/overlay layers | PASS |
| Compact reader | 52 | 104 art/overlay layers | PASS |
| Action-only reader | 24 | 48 art/overlay layers | PASS |
| Grayscale diagnostic | 52 | 104 art/overlay layers | PASS |
| Safe-zone diagnostic | 52 | 104 art/overlay layers | PASS |
| UI-density diagnostic | 52 | 104 art/overlay layers | PASS |
| CH01 three-route comparison | 156 | 312 art/overlay layers | PASS |
| 24-panel three-route bakeoff | 72 | 144 art/overlay layers | PASS |
| Benchmark failure/repair gallery | 8 | 8 raster outputs | PASS |
| CH01 failure/repair gallery | 4 | 4 raster outputs | PASS |

Every lazy-loaded image in the phone reader was scrolled into view and allowed to decode before the final missing-image assertion. It reported 104 healthy image elements, 52 distinct hybrid-art URLs, 52 distinct overlay URLs, zero broken images, a 390 px viewport, and a 375 px document width. The navigation remains horizontally scrollable at that breakpoint but its native scrollbar is hidden. Desktop pages used 1920 × 1080 and 1440 × 1000 viewports without document overflow beyond the normal scrollbar gutter. The 312-image CH01 comparison, 144-image benchmark comparison, and both failure galleries reported zero broken loaded images.

## Defect found and corrected

The first pass used a final SVG that referenced an intermediate SVG wrapper, which in turn referenced the raster plate. Chromium loaded the outer SVG but suppressed the nested image resource in image mode, producing blank art. The renderer now emits the deterministic lettering/UI as a transparent SVG overlay and places it over a direct raster `<img>` in HTML. This preserves separate art and lettering sources, avoids base64 duplication, keeps generated raster files ignored, and renders consistently in browser image mode.

Screenshots were visually inspected at mobile reader scale and in the desktop failure/repair gallery. Text remained readable, the art layer remained visible, repaired outputs were present beside preserved failures, and no browser console errors or warnings were observed on the tested hub/reader surfaces. The final unique-art pass also verified that all 52 Chapter 1 panels resolve to distinct art paths and hashes. Panels 7 and 8 were rechecked after targeted edits removed the premature Belljaw reveal while preserving Elian, the cages, lighting, palette, and layout.
