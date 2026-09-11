# Scale-conflict offline reader

This reader writes only `docs/scale-conflict/data.{json,js}`. The lead owns production sources and managed build invocation. No prior gallery is rebuilt or included by this reader.

Commands from the new worktree root:

```sh
python3 research/scale-conflict/reader/build_reader.py
python3 research/scale-conflict/reader/build_reader.py --require-complete
python3 research/scale-conflict/reader/test_builder.py
node research/scale-conflict/reader/test_preferences.mjs
node research/scale-conflict/reader/browser_qa.mjs --require-complete --port 9381
node research/scale-conflict/reader/capture_phone.mjs
node research/scale-conflict/reader/capture_history.mjs V01-F1
```

The browser helper also accepts `--root PATH --out PATH --smoke --port 9381` for a restored delivery. Use ignored output after source freeze. Capture helpers use the active worktree and durable `phone-captures` folders. They do not modify production selection or owner choices.

Inputs: frozen `production/scale-conflict/plan.json`, optional candidates/selected/review-notes. Missing plan means an explicit empty state; missing candidate means an unavailable image. Final build requires exactly V01–V06, T01–T06, A01–A08 and Q01–Q04. Full images preserve their actual native dimensions. F1 texture passes and R1 structural repairs require `retry_of` and `retry_reason` in a source-bound call record. Reference images and exact prior choice JSON remain within the new production namespace. Prior choices are read-only and cannot populate this round.

Preferences: `ScaleConflictChoices/1`; exact experiment, plan hash, dataset hash, ordered complete source binding list, and all scene responses. Nine independent ratings use null/like/dislike/unsure/na; comfort uses null/yes/no/unsure/na. Notes and shortlist remain independent. N/A differs from unanswered. Source changes isolate browser storage; imports validate every field before applying any response.

Service failures are separate `service_failures` records, with no image or preference binding. The failed request and raw tool-error output are linked separately after validating plan, prompt, source references and unchanged transport retry. Run `node research/scale-conflict/reader/service_failure_qa.mjs` after the managed rebuild for focused actual history checks.
