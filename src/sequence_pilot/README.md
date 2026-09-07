# Sequence pilot ledger

This isolated, standard-library CLI preserves a small frozen-plan experiment. It records attempts, exact prompts and original reference hashes, retains failed generations, and exports a local review reader. It does not generate images, judge their semantics, verify reviewer identities, clear commercial rights, or approve production.

Run from the checkout root with Python 3.10 or newer:

```sh
PYTHONPATH=src python -m sequence_pilot --workspace production/sequence-pilot status
PYTHONPATH=src python -m sequence_pilot --workspace production/sequence-pilot reserve P01 A prompts/p01-a.txt
PYTHONPATH=src python -m sequence_pilot --workspace production/sequence-pilot register A00001 incoming/p01-a.png
PYTHONPATH=src python -m sequence_pilot --workspace production/sequence-pilot observe C00001 observations/p01-a.json
PYTHONPATH=src python -m sequence_pilot --workspace production/sequence-pilot select P01 C00001
PYTHONPATH=src python -m sequence_pilot --workspace production/sequence-pilot import-draft drafts/sequence-review-draft.json
PYTHONPATH=src python -m sequence_pilot --workspace production/sequence-pilot export production/sequence-pilot/exports/review-001
```

Inputs resolve relative to the workspace. Copy returned artwork into an `incoming/` directory before registration. Inputs must stay inside the workspace and cannot traverse parents or use symlinks. Exports use a new directory inside the current checkout and refuse to overwrite an existing review. Reserve and register receipts expose their identifier as `id`.

`plan.json` must use `NeutralPilotPlan/2`, with integer panel numbers and named route IDs. Its exact bytes are SHA-256 bound to every ledger event; changing whitespace also changes the plan. If `plan.sha256` exists, it must match even before the first attempt. Existing evidence cannot migrate silently to an edited plan. Use a separately named workspace for a newly approved experiment, retaining the previous one and its spent attempts; this is not permission to reset the same experiment's retry budget.

Each panel and route permits one primary and one targeted retry. Reserve before calling an external generation tool. A no-output generation must still be recorded with `fail`. A returned image should be registered before logging its hard failure, so the rejected candidate remains inspectable:

```sh
PYTHONPATH=src python -m sequence_pilot --workspace production/sequence-pilot fail A00001 'Wrong event: staff does not contact the forefoot'
PYTHONPATH=src python -m sequence_pilot --workspace production/sequence-pilot reserve P01 A prompts/p01-a-retry.txt --retry-of A00001 --hard-failure 'Correct the missing staff-to-forefoot contact'
```

`fail` records an operator-declared hard failure; the CLI cannot determine whether a reason is a genuine hard failure. It does enforce the budget and requires the failed primary before a retry. Failed reservations cannot later register outputs; register any returned raster before rejecting it. Prompt text is preserved exactly in the ledger, so editing a prompt file for the targeted retry does not rewrite the original prompt. Provider, model, request ID, seed, usage, and cost remain `null` when unknown; this CLI makes no claim about hidden provider behavior or actual spend.

## Original references

An optional `refs/manifest.json` supplies original pilot references. With no `--ref`, reserve binds all manifest entries. Repeat `--ref ID` to select entries. Imported franchise artwork is outside this pilot's reference contract. An original-work declaration is provenance supplied by the operator, not automatic legal clearance.

```json
{"schema":"OriginalReferences/1","references":[{"id":"cast","path":"refs/cast.png","sha256":"EXACT_FILE_SHA256","original":true,"rights_status":"original-created-for-pilot"}]}
```

Changing or deleting any bound reference or candidate blocks mutation and export. PNG files receive chunk CRC, format, compressed-stream, and non-interlaced scanline checks; JPEG files receive frame/segment structure checks. Pillow verification runs additionally if installed. The standard-library checks are not a full JPEG or interlaced PNG decoder; actual browser/phone decoding remains a delivery gate. Neither structural checks nor file hashes establish that an image depicts the correct event.

## Independent observations

Write observations from actual image inspection. Do not fill them by copying expected beats. Every observation must bind the exact candidate, image, and plan, with all five checks explicitly supplied:

```json
{
  "candidate_id":"C00001",
  "image_sha256":"EXACT_IMAGE_SHA256",
  "plan_sha256":"EXACT_PLAN_SHA256",
  "reviewer":"Attributed observer",
  "method":"Direct visual inspection",
  "checks":{
    "actors":{"verdict":"not_assessed","observation":"Identity has not been checked."},
    "event":{"verdict":"fail","observation":"The figures stand apart; the planned contact is absent."},
    "contact":{"verdict":"fail","observation":"The staff tip is visibly separated from the foot."},
    "props":{"verdict":"not_assessed","observation":"Prop continuity has not been checked."},
    "state":{"verdict":"not_assessed","observation":"Charge state has not been checked."}
  }
}
```

Verdicts are `pass`, `fail`, or `not_assessed`, each with a nonempty observation. Hash validity cannot turn an observed wrong event into a pass. Multiple observations remain visible; later passes do not erase earlier failures. A draft selection can include a rejected candidate for comparison, but status continues to expose its failure.

## Reader and integrity limits

Export copies the frontend, selected art, `review-data.json`, and `review-data.js`; open `index.html` locally. Missing panels remain missing. Exact canonical copy travels with the plan, separate from art. Geometry is normalized to the frozen planned canvas, 390 px wide by `target_css_height_at390`; a candidate fits inside that canvas without cropping and may have letterboxing. Protected regions include those canvas margins. Font size is CSS pixels at the canonical 390 px canvas width.

To retain browser edits, export its `SequenceReviewDraft/1` JSON, place it inside the workspace, and run `import-draft`. Every panel must be present exactly once, including missing panels with both candidate fields explicitly null. Candidate IDs and SHA-256 values must match the current selections, and the plan SHA must match. The import validates every panel before appending one `draft_imported` event. Shape rectangles must remain within normalized coordinates 0–1, have width/height at least .02, and use unique IDs; fonts are 6–96 px, lettering text at most 4000 characters, and each panel has at most 100 lettering items and 100 regions. Nonfinite numbers, oversized strings, acceptance claims, and verified-identity assertions are rejected.

Exports apply the latest imported layouts matching each current candidate. Changing a candidate invalidates its previous layout and exposes a status blocker; returning to the exact same candidate can recover its matching draft. Browser observations remain unverified notes and never become backend semantic checks or authenticated human reviews. Use `observe` separately for independently supplied image-grounded checks. Imported lettering may change draft copy, but `copy_drift` flags a differing, missing, or reordered transcript; it never rewrites canonical plan copy. The transcript combines an explicit speaker prefix or `SFX: ` with lettering text for comparison.

Optional `lettering.json` must also contain the full hash-bound `SequenceReviewDraft/1` schema. An old unbound panel-keyed file, stale bindings, or invalid geometry are ignored with a visible `draft_layout_issues` blocker. Prefer `import-draft` because it preserves append-only provenance. Prepared lettering and SVG remain draft data requiring visual review; they cannot approve production.

All candidates are `draft-unaccepted`, owner review is pending, and commercial clearance is unresolved. Status separates integrity errors, semantic failures, unknown checks, and pending external human/owner/delivery gates. `production_eligible` always remains false in this pilot implementation, including when all supplied semantic checks pass.

`events.jsonl` is append-only with SHA-256 chaining. This detects ordinary local corruption; it is not externally signed, cannot prevent a user rewriting an entire history, and cannot prove reviewer independence. CLI mutation uses an exclusive workspace lock. Investigate abandoned lock files before removing them. Keep external backups/versioned receipts if stronger audit evidence is needed. Raster inputs and export copies should remain ignored by Git.

Validation:

```sh
PYTHONPATH=src python -m unittest discover -s tests/sequence_pilot -v
```
