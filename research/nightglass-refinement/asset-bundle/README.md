# Portable Nightglass refinement

Portable delivery helpers for NR-20260908-01. The final-v3 receipts record the verified archive, extraction and source parity; generation is closed at24 primary images plus six single repairs.

The archive contains all three current experiment namespaces (`production/nightglass-refinement`, `research/nightglass-refinement`, `docs/nightglass-refinement`) plus `ACTIVE_PIPELINE.md` and a root Windows `START_HERE.cmd`. It preserves all 24 primary images (four matched studies and twenty new images), every registered R1 (maximum six), nine original anchor copies, eighteen exact previous CE sources and their owner export, twenty-four previous WC selected image copies with manifest/data, global owner feedback, native gallery copies, prompts, call provenance, reviews, reader code and reproducing helpers. Original tool-return files and earlier namespaces stay in their existing workspaces; only their exact local copies are packaged.

From the repository root, replace `N` with the final registered attempt count, 24–30:

```bash
python3 research/nightglass-refinement/asset-bundle/check_bundle_coverage.py --expected-art N
python3 research/nightglass-refinement/asset-bundle/bundle_assets.py create --expected-art N --out research/nightglass-refinement/asset-bundle/local/final-v3
```

`create` requires a passing coverage preflight, writes a deterministic stored ZIP, verifies archive and member hashes, additively restores into its new `fresh-restoration` directory, and runs the extracted `research/nightglass-refinement/reader/build_reader.py --require-complete`. Rebuilt `docs/nightglass-refinement/data.json` and `data.js` must be byte-identical. The archive, exact member/byte manifest, archive receipt and verification receipt remain under ignored `local/`. Existing version directories are refused; preserve failures and choose a new version name only after fixing a real issue. A separate exact-Git export plus bundle restoration remains the lead’s final integration check.

Open a fully extracted share through `START_HERE.cmd` on Windows or `docs/nightglass-refinement/index.html` on any platform. The packaged gallery is offline; no server is needed. `ACTIVE_PIPELINE.md` is a preserved repository pointer and may mention earlier workspaces, which are intentionally outside this self-contained gallery package. Owner choices are preserved as prior read-only context; new preference state is not inferred from them.

For verified restoration, retain `archive-receipt.json` beside the ZIP and run:

```bash
python3 research/nightglass-refinement/asset-bundle/bundle_assets.py verify --archive PATH/nightglass-refinement-portable.zip --receipt PATH/archive-receipt.json
python3 research/nightglass-refinement/asset-bundle/bundle_assets.py restore --archive PATH/nightglass-refinement-portable.zip --receipt PATH/archive-receipt.json --target NEW_ROOT
python3 research/nightglass-refinement/asset-bundle/bundle_assets.py rebuild-check --target NEW_ROOT
```

Every archive member is verified before destination preflight. Restore allows missing files or exact identical hashes only; differing existing files, symlinks, file/directory clashes and case-colliding destinations are rejected before extraction. No existing file is overwritten. It rejects absolute/traversal/out-of-prefix paths, Windows-unsafe names, duplicate/case-colliding members, encrypted/nonregular entries, unregistered ZIP entries and hash/size mismatch. Limits: 3,000 files, 256 MiB per member, 6 GiB total declared payload and an 8 MiB manifest. These are additive local restoration safeguards, not a promise of isolation against another process changing the destination concurrently.

Runtime, `.scratch`, `local`, browser profiles, caches, virtual environments and `__pycache__` are excluded. Final `archive-receipt.json`, `verification.json` and `asset-manifest.json` at this helper directory are explicit external receipt exceptions to avoid recursively packaging an archive’s own receipt. The package includes `.mjs`, `.gitignore` and `.gitattributes`; the coverage preflight fails on omitted trackable source files instead of silently discarding them. `START_HERE.cmd` is intentionally relocated from this helper directory to archive root.

Run the small synthetic safety fixtures without making a production package:

```bash
python3 research/nightglass-refinement/asset-bundle/bundle_assets.py self-test
```

Each fixture run keeps a new ignored directory and emits `security-test-receipt.json` here. These helper tests do not claim final-art completeness, real gallery rebuild success or reproducible image regeneration. The real final create/restore/rebuild checks are recorded separately in final-v3 receipts.
