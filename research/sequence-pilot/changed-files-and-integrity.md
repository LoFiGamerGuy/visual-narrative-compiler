# Verification and isolated handoff

The implementation checkout is `/mnt/c/AgentWorkspaces/anime-pipeline-sequence-pilot-20260907-035400`, branch `autonomous/sequence-pilot-20260907-035400`, based on delivered audit `9a911fd8025080c06399b7acc8e89fdac5a698a2`. All task writes are confined to this new checkout and new in-product generated-image output paths. No old branch was merged or cleaned.

The full [protected-file comparison](evidence/protected-comparison.json) passes across 10 pre-existing worktrees and 204,596 files. It compares size, modification/change timestamps and mode for all included files, symlink targets, and selected small text/code content hashes. It is not a full content rehash of every large art/model file. Existing review runtime `.scratch` directories, access times and shared Git object/log updates are excluded. A checker mismatch initially omitted nine linked-worktree `.git` pointer files; targeted metadata/content checks proved all nine unchanged, and the checker was corrected. The original diagnostic failure is retained in protected-comparison-initial-check.json.

The later [head/status/ref recheck](evidence/final-protected-status.json) also passes: every protected worktree head/status and every pre-existing local/remote branch head, including main and origin/main, is unchanged. The [initial snapshot](evidence/protected-initial.json.gz) uses opaque path keys for the all-file inventory. See [isolation details](isolation.json) for the unused task-created checkout that was safely removed after its snapshot was copied.

Implementation verification: 21 backend failure-path tests pass; 49 earlier browser functional checks pass at their recorded source hashes. Final actual-art integration passes for the report, reader and correction gallery at 390×844, 1024×768 and 1440×1000. All 14 selected reader images and 18 comparison images decode, no horizontal document overflow or runtime warning/error is observed, and original copy has zero measured geometry failures. The reader scene is 5,802 CSS px high. Whole-word expanded-copy stress deliberately produces 14 flags across the two settings per viewport; these are disclosed layout limitations, not hidden passes.

The lead additionally inspected the phone reader through the close-up, handoff, vertical reveal, counter, reversal, vault, break and aftermath. Faces, active contacts, flask and damaged wood remain visible under the original lettering. The art remains restrained and textured, with clearer quiet acting than sustained action. Its rendering and dramatic force are not established at the owner's target bar. Independent review retains definite failures in P09/P11/P13/P14 and uncertainties in P07/P08. No human or owner approval is recorded.

Tracked additions contain code, original SVG boards, plans, prompts, manifests, observations, local HTML/CSS/JS and research/evidence. Generated PNGs, browser screenshots/profiles, caches, models, datasets and credentials are excluded. The illustrated local artifact requires the ignored local art bundle; hashes and exact instructions alone cannot reproduce an unknown raster provider snapshot.

## Git receipt

The payload and final receipt commit will be recorded here after push verification. The final delivery head is also reported directly to the owner; a commit cannot contain its own hash.

## Exact added-file inventory

131 new tracked files; no pre-existing tracked file is edited.

- `ACTIVE_PIPELINE.md`
- `docs/research/sequence-pilot/.gitignore`
- `docs/research/sequence-pilot/corrections/.gitignore`
- `docs/research/sequence-pilot/corrections/index.html`
- `docs/research/sequence-pilot/corrections/style.css`
- `docs/research/sequence-pilot/index.html`
- `docs/research/sequence-pilot/reader/app.js`
- `docs/research/sequence-pilot/reader/index.html`
- `docs/research/sequence-pilot/reader/review-data.js`
- `docs/research/sequence-pilot/reader/review-data.json`
- `docs/research/sequence-pilot/reader/style.css`
- `docs/research/sequence-pilot/report.css`
- `production/sequence-pilot/.gitignore`
- `production/sequence-pilot/RUNBOOK.md`
- `production/sequence-pilot/boards/.gitignore`
- `production/sequence-pilot/boards/build_boards.py`
- `production/sequence-pilot/boards/index.html`
- `production/sequence-pilot/boards/layouts.json`
- `production/sequence-pilot/boards/p01.svg`
- `production/sequence-pilot/boards/p02.svg`
- `production/sequence-pilot/boards/p03.svg`
- `production/sequence-pilot/boards/p04.svg`
- `production/sequence-pilot/boards/p05.svg`
- `production/sequence-pilot/boards/p06.svg`
- `production/sequence-pilot/boards/p07.svg`
- `production/sequence-pilot/boards/p08.svg`
- `production/sequence-pilot/boards/p09.svg`
- `production/sequence-pilot/boards/p10.svg`
- `production/sequence-pilot/boards/p11.svg`
- `production/sequence-pilot/boards/p12.svg`
- `production/sequence-pilot/boards/p13.svg`
- `production/sequence-pilot/boards/p14.svg`
- `production/sequence-pilot/boards/render-qa.json`
- `production/sequence-pilot/boards/render_boards.mjs`
- `production/sequence-pilot/events.jsonl`
- `production/sequence-pilot/generation-calls.json`
- `production/sequence-pilot/layout-draft.json`
- `production/sequence-pilot/observations/corrected/P02.json`
- `production/sequence-pilot/observations/corrected/P03.json`
- `production/sequence-pilot/observations/corrected/P06.json`
- `production/sequence-pilot/observations/corrected/P07.json`
- `production/sequence-pilot/observations/corrected/P08.json`
- `production/sequence-pilot/observations/corrected/P09.json`
- `production/sequence-pilot/observations/corrected/P11.json`
- `production/sequence-pilot/observations/corrected/P13.json`
- `production/sequence-pilot/observations/corrected/P14.json`
- `production/sequence-pilot/observations/primary/P01.json`
- `production/sequence-pilot/observations/primary/P02.json`
- `production/sequence-pilot/observations/primary/P03.json`
- `production/sequence-pilot/observations/primary/P04.json`
- `production/sequence-pilot/observations/primary/P05.json`
- `production/sequence-pilot/observations/primary/P06.json`
- `production/sequence-pilot/observations/primary/P07.json`
- `production/sequence-pilot/observations/primary/P08.json`
- `production/sequence-pilot/observations/primary/P09.json`
- `production/sequence-pilot/observations/primary/P10.json`
- `production/sequence-pilot/observations/primary/P11.json`
- `production/sequence-pilot/observations/primary/P12.json`
- `production/sequence-pilot/observations/primary/P13.json`
- `production/sequence-pilot/observations/primary/P14.json`
- `production/sequence-pilot/plan.json`
- `production/sequence-pilot/plan.sha256`
- `production/sequence-pilot/prepare_prompts.py`
- `production/sequence-pilot/prompts/P01-A-primary.txt`
- `production/sequence-pilot/prompts/P02-A-hard-retry.txt`
- `production/sequence-pilot/prompts/P02-A-primary.txt`
- `production/sequence-pilot/prompts/P03-A-hard-retry.txt`
- `production/sequence-pilot/prompts/P03-A-primary.txt`
- `production/sequence-pilot/prompts/P04-A-primary.txt`
- `production/sequence-pilot/prompts/P05-A-primary.txt`
- `production/sequence-pilot/prompts/P06-A-hard-retry.txt`
- `production/sequence-pilot/prompts/P06-A-primary.txt`
- `production/sequence-pilot/prompts/P07-A-hard-retry.txt`
- `production/sequence-pilot/prompts/P07-A-primary.txt`
- `production/sequence-pilot/prompts/P08-A-hard-retry.txt`
- `production/sequence-pilot/prompts/P08-A-primary.txt`
- `production/sequence-pilot/prompts/P09-A-hard-retry.txt`
- `production/sequence-pilot/prompts/P09-A-primary.txt`
- `production/sequence-pilot/prompts/P10-A-primary.txt`
- `production/sequence-pilot/prompts/P11-A-hard-retry.txt`
- `production/sequence-pilot/prompts/P11-A-primary.txt`
- `production/sequence-pilot/prompts/P12-A-primary.txt`
- `production/sequence-pilot/prompts/P13-A-hard-retry.txt`
- `production/sequence-pilot/prompts/P13-A-primary.txt`
- `production/sequence-pilot/prompts/P14-A-hard-retry.txt`
- `production/sequence-pilot/prompts/P14-A-primary.txt`
- `production/sequence-pilot/refs/manifest.json`
- `production/sequence-pilot/register_returned.py`
- `production/sequence-pilot/retry-generation-calls.json`
- `production/sequence-pilot/retry-specs.json`
- `production/sequence-pilot/returned-calls.json`
- `research/sequence-pilot/.gitignore`
- `research/sequence-pilot/PLAN.md`
- `research/sequence-pilot/START_HERE.md`
- `research/sequence-pilot/asset-attempts.json`
- `research/sequence-pilot/board-notes.md`
- `research/sequence-pilot/build_corrections.py`
- `research/sequence-pilot/build_report.py`
- `research/sequence-pilot/changed-files-and-integrity.md`
- `research/sequence-pilot/citation-ledger.json`
- `research/sequence-pilot/corrected-visual-review.json`
- `research/sequence-pilot/corrected-visual-review.md`
- `research/sequence-pilot/evidence/backend-tests.json`
- `research/sequence-pilot/evidence/final-browser-qa.json`
- `research/sequence-pilot/evidence/final-protected-status.json`
- `research/sequence-pilot/evidence/frontend-functional-qa.json`
- `research/sequence-pilot/evidence/package-validation.json`
- `research/sequence-pilot/evidence/protected-comparison-initial-check.json`
- `research/sequence-pilot/evidence/protected-comparison.json`
- `research/sequence-pilot/evidence/protected-initial.json.gz`
- `research/sequence-pilot/implementation-results.json`
- `research/sequence-pilot/independent-visual-review.json`
- `research/sequence-pilot/independent-visual-review.md`
- `research/sequence-pilot/isolation.json`
- `research/sequence-pilot/lettering-observations.md`
- `research/sequence-pilot/qa/cdp.mjs`
- `research/sequence-pilot/qa/check_preservation.py`
- `research/sequence-pilot/qa/final_browser.mjs`
- `research/sequence-pilot/qa/final_preservation.py`
- `research/sequence-pilot/qa/package_links.py`
- `research/sequence-pilot/red-team-disposition.md`
- `research/sequence-pilot/report-source.md`
- `research/sequence-pilot/research-gap-matrix.json`
- `src/sequence_pilot/README.md`
- `src/sequence_pilot/__init__.py`
- `src/sequence_pilot/__main__.py`
- `src/sequence_pilot/cli.py`
- `src/sequence_pilot/web/app.js`
- `src/sequence_pilot/web/index.html`
- `src/sequence_pilot/web/style.css`
- `tests/sequence_pilot/test_cli.py`
