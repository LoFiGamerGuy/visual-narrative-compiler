# Preserved experiment asset bundle

`local/SC-20260907-01-preserved-assets.zip` is a local, ignored asset archive. Transfer it separately from the repository; it is not published by this experiment. `asset-manifest.json` records every included path, byte count and SHA-256. `archive-receipt.json` records the ZIP hash and successful member verification.

The bundle includes original experiment binary assets under the production, research and documentation structural-pilot directories, all preserved finishing SVG/JSON sources that contain inline image data, and the fourteen prior sequence candidate images needed to rebuild both readers. Ordinary JSON, reader HTML/JavaScript/CSS and other mutable metadata remain in the repository. Runtime profiles, `.scratch`, cache and dependency directories are excluded. The preserved inline source files belong in the ignored local archive; portable external-image sources remain suitable for tracking.

From a fresh clone at the experiment commit, place the ZIP in this directory's `local/` folder. Run from the repository root using Python 3; no third-party packages are required:

```sh
python3 research/structural-pilot/asset-bundle/bundle_assets.py verify
python3 research/structural-pilot/asset-bundle/bundle_assets.py restore --dry-run
python3 research/structural-pilot/asset-bundle/bundle_assets.py restore
```

You can instead pass `--archive /path/to/the.zip` and `--target /path/to/fresh-clone`. The script verifies the archive hash, exact member list and every file hash before examining destinations. It then validates **all** existing destination files before creating any file. Identical existing assets are skipped; a differing file or symlink rejects restoration without writing any assets. Missing files use exclusive creation and are verified after writing. Restoration never replaces an existing file. A concurrent failure can leave newly restored, valid files, and rerunning safely skips those files.

The tracked reader code and current reader input metadata complete the restored workspace. Rebuild reader copies if needed:

```sh
python3 research/structural-pilot/build_reader.py
python3 research/structural-pilot/build_reader.py --correction --input production/structural-pilot/reader-patches/CF-reader-input.json
```

Serve the repository root with a local static server and open `docs/research/structural-pilot/reader/index.html` or `docs/research/structural-pilot/correction-reader/index.html`. The asset-only ZIP deliberately does not freeze reader metadata or code while the reader author is still editing them.

To recreate the exact ZIP from restored assets and the tracked manifest:

```sh
python3 research/structural-pilot/asset-bundle/bundle_assets.py rebuild --archive research/structural-pilot/asset-bundle/local/rebuilt-assets.zip
```

The rebuild verifies every local source against the frozen manifest, uses sorted members, fixed timestamps and uncompressed ZIP entries, then checks the resulting archive against the original archive hash. An existing archive is only accepted when its bytes already match. `create` is for the initial snapshot and refuses existing manifest/receipt/output paths.

`self-test` exercises collision rejection before any writes, identical-file skipping, missing-file restoration, repeat restoration, unsafe paths and incorrect archive hashes. Its tiny temporary fixtures remain inside the ignored `local/` directory and are removed after the test.

Validated bundle: **613 files, 525,081,219 archive bytes** (about 501 MiB). SHA-256: `14caa4b1b284c83e9406e1f74825122df929657bacd26da4e24825a420e7382e`. Full restoration into an empty ignored proof directory wrote 613 files; a second preflight found all 613 identical. A separate rebuild produced the exact same archive hash. Both current readers' source and display binary bindings were covered without missing assets or hash mismatches. See `validation.json`.
