# Combat-depth offline reader

Only new combat-depth namespaces are writable. The lead owns production sources and managed builder invocation.

```sh
python3 research/combat-depth/reader/build_reader.py
python3 research/combat-depth/reader/build_reader.py --require-complete
python3 research/combat-depth/reader/test_builder.py
node research/combat-depth/reader/test_preferences.mjs
node research/combat-depth/reader/browser_qa.mjs --require-complete --port 9382
node research/combat-depth/reader/capture_phone.mjs
node research/combat-depth/reader/capture_sequence.mjs
node research/combat-depth/reader/capture_history.mjs D01-P D01-F1
```

Browser QA also accepts `--root PATH --out PATH --smoke --port 9382` for restored deliveries. Postfreeze outputs must stay in designated ignored locations.

Input: `production/combat-depth/plan.json` (`CombatDepthPlan/1`, experimentCD-20260908-01), exact D01–D12 duel/G01–G06 squad/W01–W06 war entries with standard source/description/subject fields. Numeric IDs define reading order. References come from `reference_library` or new `reference-library.json`; `@D01` links identify related generated panels. `prior_choices` binds exact copied CE export with path/SHA. Missing plan or art stays explicitly pending; final build requires all24 actual selected images.

Candidate/selected/call/review-notes formats follow the previous reader, renamed CombatDepth. R1 structural repairs and F1 source-preserving finishes require retained source attempt and reason. Separate failed service requests validate prompt, refs, plan and raw-error sidecar and do not create artwork or preferences.

The reading view has quiet adjustable gutters and optional captions. Responses are in the gallery. `CombatDepthChoices/1` binds every selected attempt/hash, experiment, plan and dataset; all nine ratings and comfort begin null, notes blank, shortlist false. N/A is explicit. Prior choices never populate this round.

Call plan hashes resolve to the current plan or exact preserved `production/combat-depth/plan-history/plan-*.json` bytes. Unknown hashes reject the build. Each retained image links its frozen call plan; no-artwork service failures accept the same validated plan-history set. The active plan still binds the new choice dataset, so revisions cannot silently migrate responses. Blocking guides validate independently against `research/combat-depth/controls/manifest.json`, including original SVG hashes, and stay separate from drawing anchors.

The W06 six-reference input validation failure is distinct from transport failures. Its original request, six source hashes, unchanged original prompt, raw error sidecar and preserved plan remain linked. The revised primary deliberately drops only the redundant W01 source and uses its own prompt/plan bindings; it is labeled changed input, never an unchanged retry. Failure-only panels expose request history while artwork remains pending and cannot receive responses.

Final handoff metadata check: `node research/combat-depth/reader/final_metadata_qa.mjs` checks the frozen selected dataset, all 24 observation bindings, both report links, blank preserved choices, and the W06 no-art history distinction at all three viewport sizes. It does not rebuild the reader or alter production inputs.
