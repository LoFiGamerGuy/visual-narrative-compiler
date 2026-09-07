# Visual-direction artwork bundle

The final bundle is frozen with **23 PNG assets: 21 native candidates (20 primaries plus the preserved direction-19 retry) and two approved gallery overview sheets**. The gallery selects 20 options. Prior artwork, prompts, metadata, gallery code, caches and runtime profiles are excluded.

All commands run from the repository root with Python 3 and require no third-party packages. The ZIP stays in this directory's ignored `local/` folder. Transfer that ZIP separately from the repository.

The completed archive was created with this exact final selection:

```sh
python3 research/visual-directions/asset-bundle/bundle_assets.py create --expected-candidates 21 \
  --overview docs/research/visual-directions/overview-01-10.png \
  --overview docs/research/visual-directions/overview-11-20.png
```

If a final overview PNG exists, append `--overview path/from/repository/root.png`. This option can be repeated. The command refuses an unexpected candidate count, existing bundle/manifest/receipt files, symlinks or images outside this experiment. It records dimensions, byte counts and SHA-256 for each PNG in tracked `asset-manifest.json`, then verifies the full ZIP and every member before writing tracked `archive-receipt.json`.

For a fresh clone of the final gallery commit, put `visual-directions-artwork.zip` in `research/visual-directions/asset-bundle/local/`, then run:

```sh
python3 research/visual-directions/asset-bundle/bundle_assets.py verify
python3 research/visual-directions/asset-bundle/bundle_assets.py restore --dry-run
python3 research/visual-directions/asset-bundle/bundle_assets.py restore
```

You may instead pass `--archive /path/to/artwork.zip` and `--target /path/to/fresh-clone`. The script verifies archive and member hashes, then checks **every destination before writing any asset**. Identical existing files are skipped. A different existing file, symlink or non-directory parent rejects the restoration. Missing files use exclusive creation and are verified after writing; no existing file is replaced. If interrupted after some new files are restored, rerunning verifies and skips those identical files.

To reproduce the exact ZIP from restored images and the frozen manifest:

```sh
python3 research/visual-directions/asset-bundle/bundle_assets.py rebuild --archive research/visual-directions/asset-bundle/local/rebuilt-artwork.zip
```

Sorted entries, fixed timestamps and stored ZIP members make this byte-reproducible. Rebuild verification checks the result against the original archive hash. Existing archive files are never overwritten.

`self-test` uses tiny temporary fixtures inside ignored `local/` to check collision rejection before writes, identical-file skipping, missing-file restoration, repeat restoration, unsafe paths, non-directory parents and incorrect archive hashes.

After restoration, rebuild the gallery with:

```sh
python3 research/visual-directions/build_gallery.py --require-complete
```

Serve the repository root locally and open `docs/research/visual-directions/index.html`. Fresh-Git integration against the lead’s final commit is the only pending validation; it will export that exact commit into ignored `local/`, restore the ZIP, run the committed command above, and verify the twenty image bindings. Its receipt will remain local/ignored so the validated commit stays unchanged.

Verified archive: **74,347,502 bytes** (about 70.9 MiB). SHA-256: `58864aadb390d43cd853b45b572e3ad7f7c29f45db3818f4f32e0235b99de8af`. An independent rebuild produced identical ZIP bytes. Full empty-target restoration wrote all 23 assets; repeat preflight found all 23 identical. Every native candidate matches `results.json`, and all twenty selected gallery bindings are covered. The overview images have native dimensions **1280×2437**, with exactly the approved hashes. See `validation.json` and `archive-receipt.json`.
