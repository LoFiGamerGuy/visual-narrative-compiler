# Encounter Lab reader

The default gallery groups the five four-beat encounters and keeps the four radical peaks separate. Read an encounter shows one ordered setup → commitment → reversal → consequence at a time, with optional captions and spacing controls. Complete images preserve native aspect ratio; native zoom and all retained source attempts remain accessible from panel details.

Each panel starts with ten unanswered ratings, unanswered comfort, empty note and no shortlist. Each four-panel encounter has its own unanswered comprehension and continuity responses, note and shortlist. Sequence responses require all four images. Reading or opening references does not fill responses. Export/import validates the complete experiment, plan, dataset and ordered source bindings before any preference mutation; prior character choices stay read-only.

The root agent runs the managed builder. It emits only docs/encounter-lab/data.json and data.js and never rewrites the independently owned reference-comparison board.

```sh
node research/encounter-lab/reader/test_preferences.mjs
node research/encounter-lab/reader/browser_qa.mjs --root /absolute/workspace --out /absolute/ignored/qa-output --port 9384
```

Browser QA uses a new target in the task-owned Chromium session and closes that target. It checks gallery/sequence order, three viewport widths, aspect ratio, captions, native zoom, every available image history and untouched preferences. Screenshots and receipts bind the actual dataset and reader source hashes. It does not declare the art or story successful; those require actual viewing and independent review.
