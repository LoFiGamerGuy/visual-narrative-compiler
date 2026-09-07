# Handoff browser observations

Fresh-tab CDP9351 QA passed for `index.html` and `comparison.html` at 390×844, 1024×768 and 1440×1000. Actual screenshots were inspected. All 12 comparison images decoded at each size, all 18 local links exist (including START_HERE), and the pages have no horizontal overflow or runtime/console errors.

On the phone, readable headings and buttons wrap without collision. Before/after cards stack at 362px image width and tall panels use normal vertical scrolling; image canvases do not crop the source. Both desktop sizes retain paired 390px images with clear labels. The reader link opens the CF proof by default; the original-route link opens comparison mode.

One objective label fix was made in `build_comparison.py` and regenerated `comparison.html`: P14’s collapsed generated source is explicitly an unchanged reference, with no local art correction claimed. The other source disclosures now describe their own preserved sources. No artwork, CF selection, layout, or semantic verdict changed.

Evidence: `handoff-browser-qa.json` binds the final pages and builder by SHA-256; actual screenshots are in `.scratch/handoff-browser/`. The initial reused-tab result remains in `handoff-browser-qa-prior-state-transition.json`: its single failure was a browser beforeunload intervention inherited from prior dirty reader state. The final dedicated-tab run had no errors. These checks establish display/navigation integrity, not artistic acceptance.
