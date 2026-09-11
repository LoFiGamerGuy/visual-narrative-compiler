# Anchor Return reader

The gallery contains thirty compositions: three separate eight-beat sequences plus six standalone studies. Sequence order and titles come from the frozen plan. Three supplemental cast/equipment sheets, nine original anchor references and24 editable controls are shown separately and never counted as final compositions or preference rows.

Panel ratings, comfort, notes and shortlist start blank. Sequence comprehension/continuity responses also start blank and unlock only when all eight sources exist. Exact experiment/plan/dataset and source bindings protect atomic import/export. Existing character-choice exports remain read-only.

The builder reads production sources and emits only docs/anchor-return/data.json and data.js. It validates each selected image, native history, prompt, call/reference hash, support sheet and editable SVG/PNG control pair. Original edit-provenance aliases normalize only when they agree. Evidence hashed after a call is labeled inspection-time evidence.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/anchor-return/reader/build_reader.py
node research/anchor-return/reader/test_preferences.mjs
node research/anchor-return/reader/browser_qa.mjs --root /absolute/root --out /absolute/ignored/qa --port 9385
```

Actual browser QA covers390×844,1024×768 and1440×1000, ordered continuous reading, full image aspect, caption/gap controls, native zoom, all available main/support histories and unchanged preferences. Source-bound phone and sequence captures provide evidence for actual visual review; technical checks do not establish art acceptance or canon.

The regular art flow uses short titles and current state. Long scene briefs, planned camera framing and provenance stay in collapsed details. Compare image versions opens original, repair and finish in that order, with exact native/call links; supplemental sheets remain in the separate process view. [Pipeline notes](../PIPELINE.md) describe the study workflow when published.

Capture helpers accept an isolated output path. `capture_phone.mjs --ids NG01,NG02` captures displayed cards with an8px top margin; `capture_history.mjs --ids NG01` captures every retained attempt at390px; `capture_comparisons.mjs --ids NG01` captures source/repair/finish together at1440px; `capture_sequences.mjs --ids NG` captures a complete uncaptioned strip. Each receipt binds image/call hashes and reader source bytes. Preserve the six reader files alongside a capture snapshot: the dataset identity tracks selected sources, while data.json/data.js hashes also distinguish added history or changed notes.

[Final reader verification](final-qa.json) records166 passing browser checks, all30 displayed phone cards, all69 source-matched phone histories and three complete uncaptioned strips. These are presentation/integrity results; artwork limitations remain in [Results](../RESULTS.md).
