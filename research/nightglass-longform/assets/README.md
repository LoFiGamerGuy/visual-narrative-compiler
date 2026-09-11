# Baseline assets and portable delivery

The new worktree now contains the complete five-pilot native library and historical phone captures. All 656 relative dependencies in the baseline `docs/pilot-chapters/data.json` exist locally. A separate check of 731 recorded file/hash bindings found no missing files or hash mismatches. These checks establish file integrity and availability; they are not visual approval or a final package test.

## Imported material

| Material | Files inventoried | Bytes |
| --- | ---: | ---: |
| Entire `production/pilot-chapters` baseline, including tracked metadata | 1,136 | 546,154,147 |
| Historical `research/pilot-chapters/reader/phone-captures/final-v1` | 161 | 81,312,756 |
| Original inputs named by archived anchor-return calls | 72 | 128,322,244 |

The first two rows required copying 381 missing files (620,559,534 bytes); existing files already matched the source. The third row required 72 further native copies. Total added bytes: 748,881,778 (about 714 MiB). Every copy is an independent regular file, with source and destination hashes checked; there are no hardlinks or symlinks.

`production/pilot-chapters` preserves all 135 native pilot attempts, including repairs and unselected finishes; nine original drawing anchors; 69 earlier anchor-return attempts; exact prompts and call records; selected and candidate manifests; reference qualifications; editable controls and lettering; and previous preference exports. The historical final phone captures remain separate from the new reading edition.

The completed pilot source lacks ignored images at the original `production/anchor-return` locations. Its reader correctly uses its own `production/pilot-chapters/library/anchor-return` copies. However, the unchanged archived call records name 72 input files at the original relative paths. Those exact dependencies were recovered from `/mnt/c/AgentWorkspaces/anime-pipeline-anchor-return-20260909-1030` and checked against the recorded input SHA-256 values. The rest of the legacy image framework was not copied.

## Evidence and reruns

- `baseline-import.json`: source and destination paths, 1,297 inventoried files, actual hashes, copy actions, and 656 reader dependencies.
- `baseline-bindings.json`: 731 recorded hash bindings checked, zero missing, zero mismatched.
- `archive-inputs.json`: the 72 original relative call inputs, actual verified hashes, byte counts, and source root.
- `import_baseline.py SOURCE TARGET`: copies only missing pilot/capture files; refuses shared directory trees and links. Existing files are recorded, never overwritten. Do not rerun just to refresh current metadata after editorial changes: the initial report intentionally records the unmodified baseline.
- `restore_archive_inputs.py SOURCE TARGET`: restores only inputs explicitly named by the preserved library calls and refuses conflicting hashes.

## Package assembly guidance

Preserve repository-relative directory layout. Include the new comic reader and its complete generated data, all `production/pilot-chapters` material, the recovered `production/anchor-return` inputs and their existing tracked provenance, relevant `research/pilot-chapters` reports/scripts/lettering/captures, new `production/nightglass-longform` assets, and the new longform scripts/reviews/controls/lettering. Use the new reader's final dependencies to extend this list once production is complete. The five-pilot runtime HTML loads only local CSS and JavaScript, and its CSS uses no remote fonts.

The reader already loads data through `data.js`, so its preserved baseline works without `fetch()` or a server. A Windows entry point can open the new local `index.html` in the default browser. Keep diagnostic libraries and provenance accessible from the reader without putting production labels into the default story presentation.

Verify the assembled package itself after copying: open its Windows/local entry point, read each chapter at about 390 pixels, exercise native/history/library links, check every relative data and HTML/CSS dependency, and hash package-native images against their source records. Do not use these baseline checks as proof that a later package is portable. Absolute paths inside unchanged historical call records are original execution provenance, not runtime reader dependencies; the matching native inputs are preserved at their relative paths.

No owner preference, selected-image manifest, or original source file was changed by this asset task. One early command briefly created an empty `research/nightglass-longform/assets` directory chain in the pilot source and immediately removed only those new empty directories with `rmdir`; no source file was written or changed.
