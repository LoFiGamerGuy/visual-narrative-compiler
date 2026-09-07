# Per-shot conditioning controls

The selected six original SVG/PNG controls are in `production/visual-refinement/sequence-design/shot-controls/v4/`; manifest.json binds each editable source and rendered PNG, the unchanged frozen story/state sources, and key normalized hand/prop anchors. Earlier versions remain preserved. No dialogue, labels or arrows appear in the six control canvases.

These flat blocking drawings condition composition and contact, not final character design or rendering style. They are not candidate artwork. The actual native/392px review and its limitations are recorded in actual-visual-check-v4.json. The phone-review SVG references local source PNGs without embedding raster bytes.

The helper build_controls.py uses exclusive writes into its selected version directory. Preserve existing versions when revising. render_svg.mjs renders through task-owned Chromium CDP port9369 and an isolated profile under the shot-controls .scratch directory. The six PNGs were created by Chromium from editable SVG; no image-generation calls or Python raster editing were used.
