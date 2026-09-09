# Nightglass longform reader interface

Entry: `docs/nightglass-longform/index.html`; comparison: `comparison.html`; review: `review.html`. Offline `file:` loading needs no server, external font, fetch, CDN or build tool on the reader's machine.

Build snapshot with a Python environment containing Pillow:

```
/tmp/nightglass-pilot-reader-env/bin/python production/nightglass-longform/reader/build.py
```

Inputs:

- Lead-owned `production/nightglass-longform/scripts/chapter-N.json` with `chapter`, `title`, `panels[{id,action,copy,reuse}]`. `reading_premise` optionally supplies a spoiler-free introduction.
- Lead-owned `production/nightglass-longform/selected.json` with `selected: {panelID: {path,sha256,attempt_id}}`. Paths are repository-relative. Optional `reviewed_complete: [1,2,3]` identifies chapters the integrator has approved as complete development readings; owner acceptance remains separate.
- Existing pilot v2 source/lettering for a script's `reuse` id only when no explicit lead selection overrides it.
- Reader-owned `lettering-overrides.json` source-bound geometry. Main text always comes from current chapter script. `reviewed:true` requires actual visual checking; a changed source hash invalidates that lettering review.

A chapter is shown as complete only when every script panel has a valid available image, every lettered source is reviewed, and the integrator's chapter flag is set. Otherwise the reading page explicitly says incomplete and marks unavailable stretches. No placeholder art is substituted.

Comparison uses frozen `comparison-script.json` and reader-owned explicit `comparison-sources.json`. Default A/B primaries can be discovered; repairs require an explicit selection entry. C page crops are made by `prepare_comparison.py`, preserving native tool-return bytes elsewhere. The source records include exact crop rectangles and both crop/native SHA-256 values. The renderer consumes actual derivative paths, not independent inferred art.

Reusable `docs/nightglass-longform/comic.js` exposes `ComicReading.renderPanel(panel, prefix='../../')`. Its paragraph balloons stay editable, SVG tails remain separate from native raster images, and named margin treatments support explicitly ambiguous/offscreen speakers. No shared manifests, calls, candidates or accounting records are mutated by the reader.

Reviewed custom lettering also stores `reviewed_copy_sha256`, computed from the actual script copy with `json.dumps(copy, ensure_ascii=False, sort_keys=True, separators=(',', ':'))`. A changed line invalidates review while preserving editable geometry and displaying the latest authoritative text. This prevents a late copy revision from silently inheriting approval of a different lettered reading.
