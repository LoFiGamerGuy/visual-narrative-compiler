# Pilot chapters portable package

The package contains only the three pilot-chapters namespaces plus root AGENTS and the saved textual texture guide. It retains all new native attempts, all 78 earlier option images, their exact prompts and calls, previous choice files, frozen scripts, editable lettering, reader code, reviews and actual phone evidence. Copied historical calls retain their original paths and plan identities as provenance; the reader uses copied local assets. Runtime, caches, scratch and local output directories are excluded.

The frozen budget is 80 panel primaries, up to5 supplemental primaries, 10 structural repairs and 40 source-only finishes: at most 135 natives and 137 invocations including two unchanged no-art retries. Per-image repair and finish caps are one each; every actual generation request has at most five references. Budgets are ceilings, not delivery counts. Final counts and ZIP hashes are issued only after art, selection, lettering and report freeze.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/pilot-chapters/asset-bundle/bundle_assets.py inspect
PYTHONDONTWRITEBYTECODE=1 python3 research/pilot-chapters/asset-bundle/bundle_assets.py self-test
# After final source commit; COUNT includes every new returned native and sheet.
PYTHONDONTWRITEBYTECODE=1 python3 research/pilot-chapters/asset-bundle/bundle_assets.py create --expected-art COUNT --output research/pilot-chapters/asset-bundle/local/final-v1
```

Creation refuses an existing output directory. Verification checks CRC, every member SHA and byte count, path/prefix/case/size constraints and exact fresh extraction inventory. Additive restoration preflights every destination and rejects differing existing bytes before writes; exact matches are skipped. Fresh extraction and the entire exact committed Git tree are both rebuilt and browser-tested, preserving all original tracked bytes. All post-freeze receipts remain ignored under local/. No paid APIs are used. Root owns the separate prior-worktree preservation audit.

The full committed source proof has a separate runner. After the ZIP is verified and the source commit exists, run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/pilot-chapters/asset-bundle/verify_full_commit.py --commit EXACT_40_CHARACTER_COMMIT --delivery research/pilot-chapters/asset-bundle/local/final-v1
```

It exports the entire commit without a subtree filter, validates regular-file paths and archive inventory, checks every materialized file against its Git blob, restores only missing identical-bound assets, rebuilds the reader, and checks every original tracked byte again. It refuses existing snapshot outputs. Actual browser QA then runs against both restoration roots, with evidence stored outside them under the original ignored delivery directory.
