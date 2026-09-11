# Workspace consolidation — execution result, 2026-09-11

**Phases 1–2 are complete and verified. Phase 3 is waiting for an archive destination outside C:.**

Removed **53,084,406,809 bytes (53.08 GB)** across **111,608 files**: eight older build directories, nine verification extraction directories, one partial Six-v1 build and two exact duplicate ZIP filenames. Phase 1 removed 46.49 GB; phase 2 removed 6.60 GB. Every deletion path and its retained archive or preserved unique file is listed in the [execution ledger](WORKSPACE-CONSOLIDATION-EXECUTION-20260911.json).

C: free space was 359,540,002,816 bytes immediately before removal and 412,892,811,264 immediately afterward: **53.35 GB observed increase**. This is a volume measurement; background activity and allocation can affect it. The logical removal total is the exact sum of the checked files. Small cleanup receipts and retained manifests remain on disk.

## Preserved and checked

- All nine distinct Nightglass ZIPs remain at their original paths. Their full-file SHA256 hashes were freshly matched to the original build receipts before deletion.
- The current **Nightglass-NineChapters-v1** unpacked reader stays in place. Its manifest and **all 8,953 listed files** were freshly checked by SHA256 after cleanup; all 8,954 files including the manifest match the expected inventory. All nine chapters / 393 panels remain present. Prior 23-route offline browser evidence is reused because the reader's exact bytes and location remain unchanged.
- All **67 original final delivery screenshots**, their three review records and the original verification receipt still match their recorded hashes. Verification parent directories, screenshots, small reports, failures and retries remain; only their `extracted` copies were removed.
- All nine release manifests were retained separately in [cleanup-20260911/manifests](cleanup-20260911/manifests), as well as inside their ZIPs.
- The only unique file found in the partial Six-v1 build was a **15,435-byte historical `pack.py`**. Its exact bytes were preserved at [the retained historical script](cleanup-20260911/unique-files/fbaa6e9dc91fa00dd562ed3aaac6dec429fea627a00a3c3e30223e3e2f4ac9db.py). The ledger retains its original path and hash. No unique artwork was found in the removed copies.
- Live source, original/rejected artwork, raw generation records, scripts/lettering, references, trained LoRAs, models, environments and independent worktrees remain. No new art or story revisions were made.

Current reader: [START-HERE.html](../../production/nightglass-longform/package/output/Nightglass-NineChapters-v1/START-HERE.html).

Current archive: [Nightglass-NineChapters-v1.zip](../../production/nightglass-longform/package/output/Nightglass-NineChapters-v1.zip), SHA256 `948d2571f5f5d193c61c41223679a41fdbd6a9dc8408a23eb7c691ea67969b5d`.

## Retired duplicate filenames

- Main workspace `loras-trained_2026-08-30_2022.zip` now resolves historically to retained `loras-trained_2026-08-31_0048.zip`; both had SHA256 `b88812a63aab1ff7216ec575093687c991f5f187222805bc1c1da15e09d686cd`.
- Structural asset bundle `local/rebuilt-assets.zip` now resolves historically to retained `local/SC-20260907-01-preserved-assets.zip`; both had SHA256 `14caa4b1b284c83e9406e1f74825122df929657bacd26da4e24825a420e7382e`.

Old receipts and validation reports retain their original execution paths; this ledger explains retired paths instead of rewriting historical evidence. To revisit an old release, extract its retained ZIP when needed. Do not recreate all removed copies preemptively.

## Phase 3 pending

The eight older Nightglass ZIPs still occupy **20.94 GB** on C:. Windows currently exposes only C:, and the WSL virtual disk also resides on C:. Moving the ZIPs into WSL would not achieve the planned physical-space recovery.

The owner has been asked for an external-drive or network-folder destination. Once supplied, copy the eight exact ZIPs there, verify their SHA256 hashes at the destination, record the archive locations and then remove the C: copies. Keep Nine-v1 locally. No cloud upload, paid storage, compact-history substitution or distinct-ZIP deletion has been performed.

The phase-3 source paths and expected hashes are ready in the execution ledger. Phases 4–5 of the original plan were not part of the user's authorization and were not executed.

## Execution evidence

[Preflight](cleanup-20260911/preflight.json), [explicit removal binding](cleanup-20260911/removal-binding.json), [removal results](cleanup-20260911/removal-result.json), and [final exact-byte check](cleanup-20260911/postcheck.json) document the work. The one-off scripts and per-directory inventories remain in `cleanup-20260911` as historical execution records; do not rerun them against the already-cleaned paths.
