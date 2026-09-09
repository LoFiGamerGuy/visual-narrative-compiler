# Pilot chapters reader

Five independent sixteen-panel chapters share one offline reader. New panels, supplemental cast sheets, nine original style paths and all sixty-nine earlier Anchor Return attempts remain distinct. Nothing in a display choice fills the owner’s responses or establishes canon.

The default chapter view combines original native art with editable HTML balloons and SVG speaker tails. Frozen text and normalized layout zones come from each plan entry’s `lettering` list; `position: "below"` supports a short outside-art caption. Phone lettering stays at least16px. The native-art toggle and source viewer retain unmodified image pixels. Scene briefs and provenance remain optional details.

Candidate-specific repositioning is read from `production/pilot-chapters/lettering-overrides.json`, with `entries[id]` containing `attempt_id`, exact `sha256`, and `lettering`. Overrides may change placement but must preserve each frozen text, speaker, kind and lettering ID. A changed layout changes the reader dataset binding. Actual browser fit and image-overlay inspection remain necessary; valid coordinates alone do not establish legible lettering.

Panel and chapter responses start blank. Exact experiment, plan, selected-image and lettering bindings protect atomic export/import. Earlier choices remain read-only. The saved options library groups all nine style paths and separates original anchors from earlier attempts, including native/prompt/call links.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/pilot-chapters/reader/build_reader.py
node research/pilot-chapters/reader/test_preferences.mjs
node research/pilot-chapters/reader/browser_qa.mjs --root /absolute/root --out /absolute/ignored/qa --port 9387
```

The builder writes only docs/pilot-chapters/data.json and data.js. Native-aspect phone captures, complete chapter strips and exact attempt comparisons are written to versioned phone-captures directories. Captures bind their source dataset and code bytes; technical verification and independent story/art review are separate.
