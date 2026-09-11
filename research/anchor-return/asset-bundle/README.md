# Anchor Return portable delivery

The archive contains only the three anchor-return namespaces, root AGENTS instructions and the saved textual texture guide. It includes every actual candidate and support-sheet attempt, nine original anchor copies, editable SVG and rendered PNG controls, prompts, calls, copied prior choices, reader source and new reports. Runtime, scratch and local directories are excluded.

Thirty compositions remain distinct from three supplemental sheets. Budget validation fixes30 primary compositions +3 primary sheets +up to6 structural retries +30 source-only finishes =69 native artworks maximum; two unchanged no-art retries allow at most71 invocations. Counts in the final receipt report composition and sheet primaries separately.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/anchor-return/asset-bundle/bundle_assets.py inspect
PYTHONDONTWRITEBYTECODE=1 python3 research/anchor-return/asset-bundle/bundle_assets.py self-test
# After final source freeze; 69 includes every returned native attempt and sheet.
PYTHONDONTWRITEBYTECODE=1 python3 research/anchor-return/asset-bundle/bundle_assets.py create --expected-art 69 --output research/anchor-return/asset-bundle/local/final-v1
```

Creation refuses an existing output directory. It verifies ZIP CRC, member byte counts and SHA256, safe paths, case collisions and limits, then performs fresh extraction and exact reader rebuild parity. Restoration preflights all clashes: different existing bytes are rejected before writes; identical bytes are skipped. Delivery also verifies the entire exact committed Git tree before and after additive ZIP restoration and rebuilding. Final receipts remain ignored under local/. No paid APIs are required.

The read-only preservation checker expands the two hash-bound baseline source definitions, checks738 original file hashes and their ordered aggregate,23 prior worktree HEAD/status hashes, old refs and topology. Its status digest includes ignored paths but does not hash all cache contents. Only the new active branch and its origin tracking ref are exempt. Root owns final invocation after commit/push.

[Pipeline notes](../PIPELINE.md) and the final results remain part of the portable report set. The final archive count and SHA are issued only after generation, selection, review and source freeze; the budget above is a ceiling, not a delivered count. Portable-extraction and full-commit browser checks use separate ignored receipt directories after freeze.

Final art registration is closed at69 native attempts:30 composition primaries,3 sheet primaries,6 repairs and30 finishes. The final display uses29 composition finishes plus CE01-P, and three repaired sheets. Strict source preflight and696 local reader URLs pass; see [final reader QA](../reader/final-qa.json) for the166 browser checks and exact source bindings. Archive/extraction/commit-restoration receipts are created separately after the source commit, so no archive hash is asserted here.
