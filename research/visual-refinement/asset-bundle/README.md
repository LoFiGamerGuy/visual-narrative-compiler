# Portable refinement delivery

Status: artwork, UI and reports are frozen at50 native returns (40 primaries plus10 retries). Delivery uses final-v3. The v2 viewer-valid archive is preserved but superseded because its whitelist omitted .mjs reproduction scripts; coverage-failure-v2.json records the correction and the complete source-coverage preflight. The first archive/restoration is preserved in local/final-v1 after a relative-path rebuild-launch failure; integration-failure-v1.json records the correction. External archive-receipt.json and verification.json are written after successful creation and supply the completion evidence. The final package is a self-contained snapshot of this experiment’s two offline galleries, exact prompts/provenance, code/text, all40 native primary PNG returns, every registered retry,13 copied prior reference PNGs, and any native gallery copies. It does not read or change original tool-return paths or protected worktrees. Runtime directories, caches, scratch data and virtual environments are excluded.

The archive keeps exact current-experiment paths. Repeated images at different required paths are intentionally preserved, allowing offline readers and provenance links to work without rewriting metadata. Code/text are tracked; large ZIPs, restorations and rasters stay local and ignored. The root START_HERE.cmd opens both galleries on Windows after extracting the whole ZIP into a new directory; opening either HTML file directly also works. Python is needed only to verify, restore or rebuild, not to read the galleries.

From the repository root, after the lead declares all art/QA settled, create, verify every archive member, restore into a new directory, and rebuild both galleries with one command (the frozen generated-return count is50):

```sh
python3 research/visual-refinement/asset-bundle/bundle_assets.py create --expected-art 50 --out research/visual-refinement/asset-bundle/local/final-v3
```

The output directory must not exist. It contains visual-refinement-portable.zip, its exact SHA256/byte receipt, an exact member SHA256/byte manifest, verification.json, and fresh-restoration/. The rebuild must reproduce comparison-data and sequence-data JSON/JS byte-for-byte; the builder also checks selected source SHA/dimensions. Creation requires all40 primaries,13 references and the declared retry count. It refuses incomplete registries or a missing/incomplete gallery.

To restore into a fresh clone or another new directory:

```sh
python3 research/visual-refinement/asset-bundle/bundle_assets.py restore --archive research/visual-refinement/asset-bundle/local/final-v3/visual-refinement-portable.zip --receipt research/visual-refinement/asset-bundle/local/final-v3/archive-receipt.json --target /path/to/fresh-folder
```

On Windows replace python3 with py and use Windows paths. Share the archive receipt alongside the ZIP. The restorer verifies the ZIP hash and manifest/member hashes, rejects unsafe/out-of-experiment paths, case-colliding or duplicate members, symlinks, nonregular files, file/directory collisions and declared-size limits before writing. It preflights every destination: different existing files abort the entire restore before any asset write; exact identical files are skipped. Restore into an otherwise idle directory so no other process can change its paths during the operation. A fresh clone with later divergent text should use a separate empty target rather than overwrite it.

Small security fixtures can be run independently before the production freeze:

```sh
python3 research/visual-refinement/asset-bundle/bundle_assets.py self-test
```

Fixtures and their receipt remain under ignored local/security-fixtures-*/. This tests archive/path/clash rejection and exact/idempotent restoration. Final native sources, gallery bindings and a later committed-code integration still require verification after the lead freezes the completed experiment. Hashes establish file identity, not artistic or owner acceptance.
