# Encounter Lab portable delivery

The helper packages only the three encounter-lab namespaces, the root AGENTS instructions, and the saved textual texture guide. Every native attempt, prompt, source reference, prior choice export and new report stays bound by SHA256. Runtime and local caches are excluded.

Run from the new workspace root with Python 3 (standard library only):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/encounter-lab/asset-bundle/bundle_assets.py inspect
PYTHONDONTWRITEBYTECODE=1 python3 research/encounter-lab/asset-bundle/bundle_assets.py self-test
# Only after final art, notes and source commit are frozen; substitute actual native count.
PYTHONDONTWRITEBYTECODE=1 python3 research/encounter-lab/asset-bundle/bundle_assets.py create --expected-art COUNT --output research/encounter-lab/asset-bundle/local/final-v1
```

Creation refuses an existing output directory. It verifies archive CRC, every member hash and byte count, safe paths, case collisions and size limits, then fresh-restores and rebuilds the reader with exact data parity. Restore is additive: existing different bytes are rejected before writes; identical bytes are skipped. Final delivery also exports the entire exact committed Git source tree and verifies tracked bytes before and after additive restoration and rebuilding. All final receipts stay under ignored local/.

The fixed budget is 24 primary images, at most six structural retries and 24 source-only texture finishes, with at most two identical no-art transport retries: 54 native artworks and 56 total invocations maximum. No changed-input retry exception or amendment is assumed.
