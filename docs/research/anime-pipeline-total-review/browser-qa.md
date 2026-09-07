# Browser QA

Access date: 2026-09-06. Direct spend $0.

## Tooling limit

This environment has no screenshot / click-browser MCP. `open_page` cannot fetch `127.0.0.1`. QA used:

1. Static HTML/CSS inspection (skip link, `width:min(100%,…)`, `@media (max-width:500px)` stacking tables).
2. `python -m http.server` from the **worktree root** on `127.0.0.1:8767`.
3. `Invoke-WebRequest` status and byte lengths.
4. `check_hub_links.py` for in-package `href`s (except `changed-files-and-integrity.md` written at closeout).

Dedicated 390×844 / 1024×768 / 1440×1000 *viewport screenshots were not captured.* CSS is written for those widths: sticky toc scrolls horizontally rather than overflowing the document; tables become blocks under 500px; proof scroll column is `min(100%,390px)`.

## Routes exercised (HTTP 200)

| URL | Bytes |
| --- | ---: |
| `/docs/research/anime-pipeline-total-review/index.html` | 14236 |
| `/docs/research/anime-pipeline-total-review/proof/index.html` | 8682 |
| `/docs/research/anime-pipeline-total-review/START_HERE.md` | (200) |
| `/docs/research/anime-pipeline-total-review/executive-decision.md` | (200) |
| `/docs/research/anime-pipeline-total-review/next-pilot-specification.md` | (200) |
| `/docs/research/anime-pipeline-total-review/red-team-review.md` | (200) |
| `/docs/reimaginings/ember-lattice/volume/index.html` | 15595 |
| `/docs/reimaginings/ember-lattice/volume/chapters/ch01/index.html` | 21072 |
| `/docs/reimaginings/ember-lattice/premium-rd/readers/phone.html` | 27428 |
| `/docs/reimaginings/ember-lattice/pilot/reader.html` | 23237 |

## Findings

- Hub and proof have no `<img>` of protected rasters. No broken images in the package itself.
- Prior Ember readers 200-OK for HTML. Source PNGs are gitignored and **absent in this worktree**, so those readers will show missing `panel-source` images here. That is a production reproducibility finding, not a hub defect.
- Serving only the review subdirectory makes `../../reimaginings/` 404. Serve from worktree root or open the file on disk.
- Keyboard: skip link to `#verdict`; toc is a list of in-page anchors.
- Color is not the only score encoding: numbers are in the table; bars are supplementary.
- Console: not instrumented (no browser DevTools). HTML is static; no scripts on the hub.

## Phone vs desktop

- Hub: fluid `min(100%, 1100px)` page column; toc overflow-auto.
- Proof: 390px scroll column.
- Volume prior-reader CSS uses **430px** phone column — recorded as a finding, not “fixed” in this audit.
