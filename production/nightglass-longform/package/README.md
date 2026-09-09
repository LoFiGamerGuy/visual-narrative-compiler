# Portable development delivery

`pack.py` copies an explicit filesystem scope and closes repository-relative dependencies. Git tracking is irrelevant: native image files and full image-bearing tool-return JSON are included even when ignored. Source images and records are copied byte for byte. The package carries editable reader HTML/CSS/JS/SVG lettering, scripts, all current-edition attempts and reference images, revised pilots, historical pilot reader/library, and relevant research records.

Use the standard-library packager from the repository root:

```bash
python production/nightglass-longform/package/pack.py plan --plan-report research/nightglass-longform/assets/package/dependency-plan.json
python production/nightglass-longform/package/pack.py build --version Nightglass-Chapter1-v1 --milestone chapter1
```

Build after the integrator marks Chapter 1 complete in the reviewed reader snapshot. Use `--milestone threechapters` and a new version for the later delivery. Existing versions are never overwritten. `trial` explicitly labels an incomplete snapshot and is not needed for the planned checkpoints. The default ignored destination is `production/nightglass-longform/package/output/`.

Each build checks free space, copies regular files, hashes both sides, rechecks the entire included source set against changes during staging, writes an exact manifest, and creates a ZIP with sorted entries and fixed timestamps. An interrupted or invalid build remains marked failed; use another version. SHA-256 and CRC establish byte preservation, not visual approval. Never change selected art or reader state from the packager.

The owner extracts the ZIP and opens `START-HERE.html` or `OPEN-COMIC.cmd` on Windows. Reading requires no Python, server, installed tool, account, font download, or network access. Reproduction of the source build uses the documented development tools separately.

Verify the **actual ZIP** using a fresh extraction, outside the delivery artifact:

```bash
LD_LIBRARY_PATH=/tmp/nightglass-pilot-browser-libs/usr/lib/x86_64-linux-gnu \
/tmp/nightglass-pilot-reader-env/bin/python production/nightglass-longform/package/verify_package.py \
 production/nightglass-longform/package/output/Nightglass-Chapter1-v1.zip \
 --output research/nightglass-longform/assets/package/Nightglass-Chapter1-v1-verification
```

The verifier checks CRC, safe paths, every manifest hash and file count, then opens the extracted start page, available Nightglass chapters, all five revised pilots, all three comparison sequences, review pages, historical reader, and its library/reference modals through `file://` at 390×844. It checks actual image loads, local links, page exceptions, horizontal overflow, and unexpected network requests; it saves phone captures and a receipt bound to the exact ZIP hash. Review those captures before reporting the delivery verified. The installed browser/environment is used for QA and excluded from the package.

Historical research can cite older intermediate captures and legacy duplicate locations that were never copied into this isolated edition. These are listed as `archival_missing` in the manifest, distinct from `required_missing`, which must be empty. Required historical reader links and preserved native attempts remain included. Absolute paths in exact historical tool records document their original execution; those strings are not rewritten into false current execution records.

Explicit exclusions: package outputs and verification extractions, credentials, dotfiles, caches, virtual environments, installed tools, neighboring worktrees, and unrelated legacy production roots. Earlier packages remain untouched. A build may be complete development work without claiming owner acceptance or publication.
