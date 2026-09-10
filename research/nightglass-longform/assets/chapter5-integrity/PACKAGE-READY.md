# Five-chapter portable package — prepared, not built

Proposed new version: `Nightglass-FiveChapters-v1`, milestone `fivechapters`. No build, source freeze, new ZIP, extraction or portability claim was made by this audit. Wait for root's actual full42 reading completion, `reviewed_complete=[1,2,3,4,5]`, and explicit build release. The existing packager enforces that milestone gate, free-space reserve, source hash stability and refusal to overwrite versioned artifacts.

Run from `/mnt/c/AgentWorkspaces/anime-pipeline-nightglass-longform-20260909-2110` only after release:

```bash
python production/nightglass-longform/package/pack.py build --version Nightglass-FiveChapters-v1 --milestone fivechapters
```

Default new staging directory: `production/nightglass-longform/package/output/Nightglass-FiveChapters-v1/`. New ZIP: `production/nightglass-longform/package/output/Nightglass-FiveChapters-v1.zip`. Both paths were absent during preparation. Logs, if retained during the freeze, belong under the packager's excluded `production/nightglass-longform/package/builds/`, not an included moving source. Notify root immediately on the actual `source-snapshot-frozen` event after copy/hash/inventory checks; do not infer it from a started copy or completed first pass.

Then freshly extract and verify the actual new ZIP into the currently unused output path:

```bash
LD_LIBRARY_PATH=/tmp/nightglass-pilot-browser-libs/usr/lib/x86_64-linux-gnu /tmp/nightglass-pilot-reader-env/bin/python production/nightglass-longform/package/verify_package.py production/nightglass-longform/package/output/Nightglass-FiveChapters-v1.zip --output research/nightglass-longform/assets/package/Nightglass-FiveChapters-v1-verification --chromium /home/gosnerp/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome
```

Expected complete edition:19 dynamic routes,219 Nightglass panels across five chapters,80 revised pilot panels and18 comparison panels. Updated verifier captures actual open-dialog interior offsets and checks78 options images/nine anchors/Close controls; its UI-only regression on the old fourchapter extraction passed, but does not prove a future fivechapter ZIP. New extracted captures must still be actually viewed.

Free space observed during preparation:341836091392 bytes; packager must recheck at build time using its four-times-source-size plus512MiB reserve. Preserve the existing Chapter1, ThreeChapters and FourChapters ZIPs unchanged. If the proposed version or verification path exists at actual release, use a new version/sibling output rather than overwrite. No publication or human acceptance is implied.
