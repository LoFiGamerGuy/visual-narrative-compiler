# Image-observed lettering placement — final draft

Status: complete lettering draft bound to the final selected candidates; **all artwork remains unaccepted**. This is agent-authored placement and geometry evidence, not human/owner acceptance or a semantic quality verdict. The coordinator separately recorded failed corrected artwork for P09/P11/P13/P14; readable lettering does not resolve those failures.

Canonical handoff: `production/sequence-pilot/layout-draft.json`, SHA-256 `93a153929b23fe85fe5580e9b354855b97ce9d7b5372ea8651605a0fb9b0d5db`. Frozen plan SHA-256: `b31533e87ee23fbf8739fda72a65d1fe9d78c98956ae1c95385bec1ed05f05b6`. The draft contains 14 panel bindings, 15 exact copy units, and 98 image-observed protected rectangles.

## Observation and placement method

All 14 primary rasters and all nine final corrective rasters were viewed directly. Every protected rectangle was located from the actual selected local raster; storyboard zones were not reused as observations. Coordinates use the fixed planned canvas with the exact `object-fit: contain` image-to-canvas transform. Tiny observed features use a conservative minimum 2% rectangle to satisfy the shared geometry schema. These are selected face, hand, flask, staff/contact/break, mechanism and sentinel annotations, not comprehensive segmentation. A label such as “visible staff forelimb crossing” identifies a drawn feature without asserting that the required persistent contact is correct.

Full source art is preserved. The checker reports visible letterboxing for P07 and P11 because their contained heights differ from the frozen canvas by more than one pixel. Other subpixel aspect differences are also handled by containment. No art was cropped or painted to conceal a story failure.

The frozen copy is preserved exactly. Visible NERA:/ODO: prefixes are stored in the speaker field; SFX: is represented by kind=sfx. Reconstructing those prefixes yields every frozen copy entry in the original order. P03/P05/P09/P13 are intentionally silent. Dialogue tails end beside the visible speaker face; P02 and P10 retain the scripted order through top-to-bottom placement.

Dialogue uses canonical 16 CSS px; UI uses 13.5. At a 390 CSS px viewport, the editor SVG measures 358 px and displays dialogue at 14.687 px and UI at 12.392 px, above the 14/12 project floors. The reader SVG measures 390 px and displays 16/13.5 px. SFX use 27–29 px, with a cream outline behind dark glyphs. Fonts do not shrink under stress.

## Final selected bindings

| Panel | Candidate | Copy units | Observed regions | Placement evidence |
|---|---|---:|---:|---|
| P01 | C00001 | 1 | 1 | Nera speech in right daylight, clear of face. |
| P02 | C00015 | 2 | 6 | West handoff preserved; Odo bubble above Nera response, flask and pulley clear. |
| P03 | C00016 | 0 | 8 | Silent; faces, release, flask, staff, east shutter and overhead recess marked. |
| P04 | C00004 | 2 | 4 | Two UI blocks in upper open space; fist, blank wrist and flask clear. |
| P05 | C00005 | 0 | 6 | Silent tall reveal; faces, flask, release and unfolding limbs marked. |
| P06 | C00017 | 1 | 8 | Speech above Nera; waiting staff tip and nearest foot remain visible. |
| P07 | C00018 | 1 | 8 | TAK over lower-right water; staff/forefoot splash clear. |
| P08 | C00019 | 2 | 6 | Two UI blocks in upper-center space; face and staff contact clear. |
| P09 | C00020 | 0 | 9 | Silent; sweeping limb and visible crossing marked without certifying contact. |
| P10 | C00010 | 2 | 8 | Catch above Go; throwing/receiving hands and flask remain visible. |
| P11 | C00021 | 1 | 9 | UI in upper daylight; airborne face, continuous staff, grips and cyan trail clear. |
| P12 | C00012 | 1 | 7 | KRAK below the impact between legs; scraped hand and wood break clear. |
| P13 | C00022 | 0 | 10 | Silent; faces, shutter edge/limb, broken wood, injured hand and flask marked. |
| P14 | C00023 | 2 | 8 | Odo above Nera response; both faces, scraped raised hand and flask clear. |

## Measured checks

Read-only `Workspace.validate_draft` passed for all 14 current candidate IDs and hashes. An independent reconstruction of visible text plus speaker/kind prefixes matched all frozen copy arrays exactly. `node --check src/sequence_pilot/web/app.js` passed. The public reader data and event ledger were not changed by this lettering task.

A private offline bundle was tested in isolated Chromium CDP 9338. All 14 selected images decoded successfully. Original copy produced zero measured geometry failures across all panels at the 390 px viewport: rounded-balloon glyph-contour bounds, art bounds, project font floors, conservative marked-region collisions and lettering overlap. Desktop/phone review and reader views at 390/1024/1440 showed no horizontal page overflow or observed runtime exceptions. Phone composites for every panel containing copy were visually inspected; the four silent panels were inspected as source art. An early clipped screenshot of P11 included the preceding panel due to the CDP clip capture; a full viewport capture confirmed the complete P11 art and UI. This was a capture limitation, not an image crop.

The coordinator subsequently tested the exported report/reader/correction pages across all three viewports, with evidence in `evidence/final-browser-qa.json`. That integration evidence is tied to the final layout hash above. The earlier `evidence/frontend-functional-qa.json` remains the historical 49-check interaction baseline at its original frontend hashes; it was not relabeled as final artwork validation.

## Synthetic copy stress

The two settings repeat whole words until reaching at least +30% or +50%; these are diagnostic copy-growth tests, not translation tests or exact-length expansions. Actual character growth ranges from +38.5% to +133.3% for the first setting and +57.7% to +133.3% for the second on this short script. Very short words can therefore produce identical stress strings at both settings. The UI labels and note disclose this rounding. Canonical copy and font sizes remain unchanged.

Both settings flag the same six copy units, producing seven flags per setting:

| Copy unit | Failure at both stress settings |
|---|---|
| P02-L01 — One dose. Keep it upright. | Glyph bounds cross rounded balloon contour. |
| P02-L02 — Then hold the door. | Glyph bounds cross rounded balloon contour. |
| P04-L01 — PULSE · 3 | Glyph bounds cross balloon contour and extend beyond art. |
| P04-L02 — AIR BRAKE · COUNTERS 1/2 | Glyph bounds cross rounded balloon contour. |
| P08-L02 — COUNTERS 2/2 · AIR BRAKE READY | Glyph bounds cross rounded balloon contour. |
| P10-L02 — Go. | Glyph bounds cross rounded balloon contour. |

The other nine copy units produce no measured stress geometry flags. This does not establish publishable alternate copy: longer text requires deliberate resizing, relocation or rewriting followed by another visual review. Protected-region checks use conservative authored rectangles, including tail bounds; they do not locate faces automatically or prove correct reading order, impact, anatomy, topology or continuity.

## Frontend fixes prompted by actual art

The first dark KRAK composite had weak contrast against dark art. SFX now receive a 1.8 px cream stroke behind the existing dark fill; KRAK was positioned in clear space below the impact. No raster art was edited. Stress labels were changed to “At least +30%/+50%” with a whole-word rounding explanation. These are the only late frontend changes; the coordinator’s final export includes them.

The next decision is editorial/art correction or rejection using the independent review, followed by real owner/human phone review. This draft contains no production promotion, invented score, verified-human claim, or acceptance.
