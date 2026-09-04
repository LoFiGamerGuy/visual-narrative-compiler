# Premium browser QA

- Date: 2026-09-04 (America/New_York)
- Browser path: in-app Chromium session against `http://127.0.0.1:8877/`
- Desktop viewport: 1920 × 1080
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
| Preserved failure/repair gallery | 8 | 8 raster outputs | PASS |

Every lazy-loaded image was scrolled into view and allowed to decode before the final missing-image assertion. The mobile reader reported a 390 px viewport and 375 px document width; the navigation remains horizontally scrollable at that breakpoint but its native scrollbar is hidden. Desktop pages used the native 1920 px viewport without document overflow beyond the normal scrollbar gutter.

## Defect found and corrected

The first pass used a final SVG that referenced an intermediate SVG wrapper, which in turn referenced the raster plate. Chromium loaded the outer SVG but suppressed the nested image resource in image mode, producing blank art. The renderer now emits the deterministic lettering/UI as a transparent SVG overlay and places it over a direct raster `<img>` in HTML. This preserves separate art and lettering sources, avoids base64 duplication, keeps generated raster files ignored, and renders consistently in browser image mode.

Screenshots were visually inspected at mobile reader scale and in the desktop failure/repair gallery. Text remained readable, the art layer remained visible, repaired outputs were present beside preserved failures, and no browser console errors were observed on the tested hub/reader surfaces.
