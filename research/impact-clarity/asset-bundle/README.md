# Impact-clarity portable delivery

Final art is closed at29 retained natives (16P,4R1,9F1),29 invocations and16 selected displays. Strict metadata preflight and34 scoped contracts pass. Create the archive only after final reader QA and the lead’s source commit.

Expanded by the explicit user authorization in scope-amendment-01.json: the original12 studies remain unchanged, with Y01–Y04 added. Current limits are16 primaries, at most4 R1 repairs and16 F1 source-only finishes:36 natives, two unchanged no-art retries and38 total invocations. Exact archived V1 retains its12/4/12/28/2/30 budget for historical calls. No other scope/budget amendment or changed-input retry exception is permitted. The helper pins the authorized amendment and original plan hashes, checks all original entries/references remain unchanged, and requires every study to exist in its own call-bound plan version. F1 requires an exact sole source and a recorded reason; artistic necessity remains a separate review.

From this experiment root:

```sh
python3 research/impact-clarity/asset-bundle/bundle_assets.py self-test
python3 research/impact-clarity/asset-bundle/test_ic_contracts.py
python3 research/impact-clarity/asset-bundle/bundle_assets.py inspect
# Only after final artwork/reviews/reader QA, source freeze and lead commit:
python3 research/impact-clarity/asset-bundle/bundle_assets.py create --expected-art 29 --output research/impact-clarity/asset-bundle/local/final-v1
```

Inspect permits missing planned primaries, while validating registered natives, exact prompts, calls, actual references, selections and prior-choice sources. Every job/request allows one to five references. Copied prior-choice JSON is hash-bound as an intact historical export; its embedded CE plan/dataset identifiers are recorded separately and are not IC call plan hashes. All new call plan hashes must resolve to current or preserved full plan-vN.json bytes with matching SHA sidecars, experiment identity and that version’s exact authorized IDs/numerical budget. Unrun job specifications are preserved but never counted as invocations. At most one R1 and one F1 per ID; retained source and reason are mandatory. A no-art service failure is a counted invocation; its one permitted retry must keep the same creative request and source hashes. Final creation rejects pending calls and requires the explicit actual native count.

The ZIP includes the complete three new impact-clarity namespaces: native attempts, local reference copies, prompts, provenance, prior choices, reader assets/code, reports and QA. Root AGENTS.md and the saved textual texture skill/guide are the only inherited instruction exceptions; older galleries and original external tool-return locations are excluded. Helper START_HERE.cmd/START_HERE.md map to the package root. Runtime, local, .scratch, caches, browser profiles, virtualenvs and self archives are excluded. Unknown file types fail classification. Raster artwork and ZIPs remain local/ignored; scripts and metadata are tracked.

Create writes a new version only, verifies archive SHA/bytes, member hashes/bytes and ZIP CRC, then restores into a fresh directory and rebuilds the copied offline reader. Both data.json and data.js must remain byte-identical. Exact file inventory is checked before/after rebuild, and local HTML/CSS/data paths resolve with URL queries/fragments respected. Relative Markdown links require a separate final report check. A failed creation retains its evidence; do not automatically rerun or overwrite.

```sh
python3 research/impact-clarity/asset-bundle/bundle_assets.py verify --archive PATH/impact-clarity-portable.zip --receipt PATH/archive-receipt.json
python3 research/impact-clarity/asset-bundle/bundle_assets.py restore --archive PATH/impact-clarity-portable.zip --receipt PATH/archive-receipt.json --target NEW_OR_MATCHING_CHECKOUT
python3 research/impact-clarity/asset-bundle/bundle_assets.py rebuild-check --target NEW_OR_MATCHING_CHECKOUT
python3 research/impact-clarity/asset-bundle/check_preservation.py --output research/impact-clarity/asset-bundle/local/preservation-post-push-v1.json
```

After the lead commits frozen sources, export the full exact Git commit into a new ignored local directory, without a subtree path filter. Verify every tracked blob, restore the ZIP additively and rebuild, then recheck all original tracked bytes. Existing identical files are skipped. Any differing file, symlink, case collision or file/directory conflict rejects the entire restoration preflight before writing. New files use exclusive creation; use a quiescent target, not a concurrently modified directory. Never rebuild the original source root. All post-freeze receipts stay ignored under asset-bundle/local.

Archive limits: 5000 members, 256 MiB each, 8 GiB total, 8 MiB manifest. Absolute/traversal/Windows-reserved paths, duplicate/case-colliding files, encryption, symlinks and unexpected members fail. Hash receipts provide integrity, not signatures. Viewing needs no server, account or paid API; optional verification and rebuilding use Python standard library. Browser behavior and art acceptance are separately reviewed.

The preservation checker verifies 21 prior worktree HEAD/status hashes, 130 saved original content hashes, saved local refs and precreation topology using the exact recorded status argv: git status --porcelain=v1 --untracked-files=all --ignored=matching. Only the new active worktree and its branch/origin-tracking refs may be added. Windows Git pointers are normalized; optional locks and fsmonitor are disabled. Ignored-path inventory is checked at Git reporting granularity, not by hashing all cache contents. Only saved originals have content-hash coverage. Remote parity is a separate lead check; the filesystem audit spans an interval, not an atomic snapshot.

The additional combat-reference research and offline reference gallery are included under the same new research/docs namespaces. External research thumbnails are classified research assets, not generated-native attempts or automatic generation inputs; only exact actual call reference records establish what the generator received.

The reference board freeze binds45 exact files and16 attributed excerpt JPEGs, plus data.json/data.js consistency. Their nested image URLs are checked from the reference board directory. Both main and research data pairs must remain byte-identical through the main reader rebuild. The research crop builder is not invoked during offline verification: its full publisher source cache is intentionally excluded. Only frozen limited excerpts are transported. Actual generation-reference hashes are checked to exclude these research images and their recorded full-source hashes.
