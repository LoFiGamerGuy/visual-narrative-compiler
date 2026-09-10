# Chapter8 portable-package preflight and bounded guard fix

Ready for the eventual completion freeze, not for building the incomplete edition. The only missing support was three milestone declarations in pack.py: CLI choice, required reviewed chapter list1–8, and the Eight-chapter starter label. Those three lines are now extended. No collector, strict verifier, reader or prior artifact changed.

Focused checks passed: CLI help accepts eightchapters; an actual CLI attempt against current16/45/incomplete8 exits1 with “Chapter 8 is not a complete reviewed reader snapshot” before collect/copy/output creation. All four unique EightChapters-v1 paths remain absent. The starter emits the correct label. Exact invocation/result and unchanged verifier hash are in PACKAGE8-PREFLIGHT-GUARD-CHECK.json. No source freeze, ZIP, extraction or browser was run. Existing collector regression tests were read but not rerun because its behavior did not change.

The canonical spelling collector remains byte-for-byte the proven Seven-v2 implementation: enumerate actual source spellings, require samefile for aliases, record aliases explicitly, reject distinct case collisions, and recheck source inventory/aliases before the frozen event. It includes native PNGs and image-bearing raw JSON independently of Git tracking. The package/builds and package/output trees and external package reports are pruned. Existing absolute execution paths remain provenance, not portable reader links.

Current bounded Chapter8 inspection found175 eligible files/136,672,101 bytes,62 metadata JSONs and90 unique allowed relative dependencies with zero missing at that moment. This is a moving subset check, not the final package closure. The production/script/reader/documentation seed roots already cover Chapter8 and its copied references; final collection must again require zero missing reader/production dependencies and preserve explicit archival limitations. Reader chapters and verifier routes are dynamic. At completion expect351 Nightglass panels,80 revised pilots and18 comparison panels across22 verifier routes (20 regular plus two dialogs). Expected sample split is24 chapter views,34 other regular views and6 internally scrolled dialog views if page heights remain comparable; actual capture inventory governs. Options78/anchors9 and close/scroll/load checks stay enforced.

At preflight, C: had294,183,698,432 free bytes (about274GiB), comfortably above the prior package footprint. This is not a final reserve calculation: the packager recomputes its full source closure and requires four times source bytes plus512MiB for staging/ZIP/fresh extraction. All old successful packages and failed/interrupted stages remain untouched.

After all45 Chapter8 panels have full actual reading approval, final completion-header/end proof, reviewed_complete1–8 and an explicit root source-freeze checkpoint, use the following exact commands from the isolated worktree. They are prepared commands, not instructions to bypass that gate:

```sh
python -u production/nightglass-longform/package/pack.py build --source /mnt/c/AgentWorkspaces/anime-pipeline-nightglass-longform-20260909-2110 --version Nightglass-EightChapters-v1 --milestone eightchapters --output /mnt/c/AgentWorkspaces/anime-pipeline-nightglass-longform-20260909-2110/production/nightglass-longform/package/output
```

Only after genuine build exit0 and its ZIP/build receipt:

```sh
LD_LIBRARY_PATH=/tmp/nightglass-pilot-browser-libs/usr/lib/x86_64-linux-gnu /tmp/nightglass-pilot-reader-env/bin/python -u production/nightglass-longform/package/verify_package.py /mnt/c/AgentWorkspaces/anime-pipeline-nightglass-longform-20260909-2110/production/nightglass-longform/package/output/Nightglass-EightChapters-v1.zip --output /mnt/c/AgentWorkspaces/anime-pipeline-nightglass-longform-20260909-2110/production/nightglass-longform/package/output/Nightglass-EightChapters-v1-verification --chromium /home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome
```

Use the proven sevenchapter-v2 durable subprocess/exit-receipt pattern with NEW excluded builds/eightchapter-v1-* runners and logs, exclusive creation, no duplicate jobs. Bind the verifier hash again before launch. Python/browser/library paths currently exist. Report the genuine source-snapshot-frozen event promptly; preserve included-source write hold until that event. The archive, staging directory, build receipt and verification directory are all unique Nightglass-EightChapters-v1 paths under package/output. Fresh extracted entry is verification/extracted/Nightglass-EightChapters-v1/START-HERE.html; capture directory is verification/phone-390. Final ZIP SHA, manifest SHA, exact inventory,22 actual route results and actual sample inspections remain required before a portable-delivery claim.
