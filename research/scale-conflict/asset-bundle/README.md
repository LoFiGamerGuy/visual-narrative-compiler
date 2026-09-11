# Portable scale-conflict delivery

Generation accounting is closed and verified:51 native artworks (24P +4R1 +23F1), one preserved no-art service failure,52 total invocations and zero pending calls. Run final creation only after the lead also freezes all selected displays, reviews, notes and reader output. The actual total must match `--expected-art`; the original plan and its explicitly bound amendment limits apply. The base remains24P/4R1/12F1,40 total; amendment01 raises only F1 to24 and total to52. The helper validates amendment schema/experiment/identity, exact base-plan hash, frozen evidence hash and its candidate bindings, then records both base and effective budgets. It does not rewrite either input.

From the experiment root:

```sh
python3 research/scale-conflict/asset-bundle/bundle_assets.py self-test
python3 research/scale-conflict/asset-bundle/bundle_assets.py inspect
python3 research/scale-conflict/asset-bundle/bundle_assets.py create --expected-art 51 --output research/scale-conflict/asset-bundle/local/final-v1
```

`inspect` is read-only and tolerates missing planned primaries; it still rejects a broken registered source. `create` requires complete24-scene source/display coverage, writes a new ZIP/manifest/receipt, verifies archive SHA/size, every member SHA/size and CRC, then restores into a new isolated folder and runs its own copied reader builder. Both `data.json` and `data.js` must rebuild byte-identically. Local HTML/CSS and gallery-data paths must resolve with query strings/fragments removed. Exact extraction inventory is checked before and after rebuilding. Failures retain the archive, receipts and extraction; use a new final-vN only after fixing a real failure.

Coverage is explicit: all supported files in the three new scale-conflict namespaces; root `AGENTS.md`; the textual texture skill subtree and `GUIDE.md`; root-mapped `START_HERE.cmd`/`START_HERE.md`. Unknown file types fail inspection rather than being silently omitted. `.scratch`, `local`, runtime/cache/browser/venv directories are excluded. Asset-bundle root final receipts are external to prevent circular hashes; launcher/instructions map to the root. Earlier galleries, original external generated-image locations and the archive itself are excluded. Sources are copied unchanged; artwork and ZIP stay local/ignored. Hashes retain provenance but do not establish visual acceptance.

Source checks cover exact24 IDs, unique attempt identities, frozen budget, registered native inventory, prompt/call hashes, actual call-reference paths versus their hashed local copies, frozen job/call plan hashes, edit source/reason, references and exact prior-choice bytes. Actual calls always require their exact submitted prompt and reference hashes. A superseded unrun job is checked against its embedded prompt digest and one byte-identical archived prompt under `production/scale-conflict/unrun/`; its old intended path is recorded separately from the executed prompt. There is no fallback for actual calls. Final calls must match registered returned attempts. Static HTML href/src, CSS url() and dynamic gallery-data dependencies (including service failure record/tool-output/prompt paths) are checked; historical `source_path` and semantic `story_path` are explicitly excluded from runtime-file resolution; arbitrary JavaScript execution is covered separately by the reader’s browser QA.

Verification and additive restoration:

```sh
python3 research/scale-conflict/asset-bundle/bundle_assets.py verify --archive PATH/scale-conflict-portable.zip --receipt PATH/archive-receipt.json
python3 research/scale-conflict/asset-bundle/bundle_assets.py restore --archive PATH/scale-conflict-portable.zip --receipt PATH/archive-receipt.json --target NEW_OR_MATCHING_CHECKOUT
python3 research/scale-conflict/asset-bundle/bundle_assets.py rebuild-check --target NEW_OR_MATCHING_CHECKOUT
```

For final committed integration, export the exact delivery Git commit into a **new task-owned ignored directory**, then run restore and rebuild-check above from the original helper against that directory. Restore checks every destination before writing: a byte-identical tracked file is skipped; any differing existing file, case collision, symlink or file/directory conflict rejects the entire preflight. It never intentionally overwrites. Run against a quiescent destination; this is not a transaction against concurrent adversarial filesystem changes. New files use exclusive creation. Do not use `rebuild-check` on the original source root.

The archive manifest supplies relative paths, SHA256 and byte counts. Limits:5000 files,256MiB per file,8GiB payload,8MiB manifest. ZIP entries must be regular unencrypted files with exact allowlisted paths; traversal, Windows reserved names, duplicate/case collisions and unexpected members are rejected. Receipts are integrity records, not cryptographic signatures; retain the trusted archive hash separately when sharing.

The Windows launcher opens the offline gallery only. No paid APIs, packages, Blender, image generation or prior-workspace writes are used.


## Preservation audit

```sh
python3 research/scale-conflict/asset-bundle/check_preservation.py --output research/scale-conflict/asset-bundle/local/preservation-post-push-v1.json
```

Each output must be new. This checker reads `research/scale-conflict/protected-initial.json`:19 prior worktree HEADs and status SHA256 values, seven original source file content hashes, all saved local refs, and registered worktree topology. It uses explicit Git-dir/work-tree normalization for Windows Git pointers, `--no-optional-locks`, `GIT_OPTIONAL_LOCKS=0` and disabled fsmonitor to avoid optional index writes or hooks. Only the active scale-conflict branch, its `origin` tracking ref and active worktree HEAD may advance. Any other changed, added or missing ref/worktree fails.

The original snapshot did not record historical status argv. The checker uses raw stdout from `git status --porcelain=v1 --untracked-files=all --ignored=matching` and requires every saved status hash to match; a full match demonstrates reproduced output equivalence, not recovered historical argv. The first `--ignored` run failed16/19 status hashes; a bounded reporting-mode probe matched one nonempty baseline exactly with `--ignored=matching`, which is now required for the complete audit. The first failure and probe receipts remain preserved. No fallback relaxes mismatches. Ignored path inventory is covered only at Git’s reporting granularity: arbitrary ignored/cache bytes are not hashed. Existing dirty files can change bytes without changing status. Only the seven explicitly saved originals have content-hash coverage. Local refs are checked without fetching; remote server parity remains a separate lead check. Run after concurrent work settles, since this is an interval audit, not an atomic snapshot.


Transport service failures are preserved under `production/scale-conflict/transport-failures/` and count toward the effective52-invocation cap even when no native artwork returns. The ledger separates returned native artworks, no-art failures and pending calls. A supporting `ScaleConflictToolFailure/1` receipt is evidence for its linked request, not another invocation. Untagged original failure records are validated against their explicit fields (status, null returned artwork, error/times, IDs and source bindings); no schema tag is invented in those originals. One unchanged transport retry is allowed: exact failed-record SHA, creative request fields, prompt and reference hashes must agree. A final archive rejects pending calls. If the retry also fails, its preserved failure and any identical call alias count once, and no native is invented. The identical retry succeeded. Final expected-art is51 and invocation count is52; the tool-output receipt and failed request remain bound evidence. The strict final accounting receipt is `final-invocation-accounting.json`.


Final delivery order: finish selected-image review and notes; rebuild and QA the final reader; freeze all packaged source files; run `create --expected-art 51` into a new `local/final-vN`; retain its verified manifest/receipt and fresh-restoration result; then let the lead commit/push. If final receipts are copied to the asset-bundle root for Git delivery, the declared external-receipt exclusions prevent circular packaging. Do not edit bundled text after freezing the ZIP. Export the exact committed code into another new ignored directory, run additive `restore`, then `rebuild-check` against that export. Finally run the preservation checker to a fresh post-push receipt. No additional image calls or automatic archive reruns are part of this sequence.
