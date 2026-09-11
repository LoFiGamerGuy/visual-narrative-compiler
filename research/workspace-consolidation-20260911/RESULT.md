# Workspace consolidation completed — 2026-09-11

All **26 sibling worktrees** have been consolidated into `C:\AgentWorkspaces\anime-pipeline`. Only this checkout remains registered. Every original branch still points to its original commit, and all those commits are ancestors of the consolidation branch.

Open [the library](../../START-HERE.html), or double-click `start-library.cmd` from the main folder. The [workspace guide](../../WORKSPACE-INDEX.md) maps the source, readers, experiments and historical views.

## Space recovered

Removed **123,783 verified duplicate files: 5,324,530,498 bytes (5.32 GB)**. This is additional to the previous cleanup's 53.08 GB and does not count it again.

Moved 99,978 files/links into their current project paths (58,758,966,583 bytes). Preserved 297 distinct conflicting versions in `archive/workspace-variants/` (4,677,108 bytes), with duplicate historical versions pointing to an existing retained copy. Different paths required by current readers and distinct release ZIPs remain available.

Observed C: free space increased from 407,460,651,008 to 412,119,478,272 bytes: **4.66 GB net gain** during execution. That volume measurement includes new audit metadata and other concurrent disk activity; it is distinct from the exact duplicate-removal total above.

The older distinct Nightglass milestone ZIPs remain locally under `production/nightglass-longform/package/output/`. Offloading their previously identified 20.94 GB still requires a separate storage destination. Main models, trained LoRAs and environments were preserved.

## Preservation and validation

- **224,058 original file/link entries** resolve to **111,940 verified destinations**, with zero remaining actions and zero content failures. Twelve directory symlinks from WSL runtime caches were found during retirement and separately preserved with their exact targets.
- The original main folder's local files remain; the source checkout now includes the cumulative Nightglass work plus Borrowed Down, The City Keeps Oaths, AWS editorial work and the earlier independent review. One package-description conflict was resolved; both conflicting historical review entry pages were retained.
- **59 browser routes passed** at a phone viewport: the library, 23 current entries, all 26 historical entries and all nine Nightglass chapters. All **393 chapter images** were explicitly loaded. No tested route had missing images, HTTP failures or JavaScript exceptions.
- Borrowed Down and The City Keeps Oaths both pass their read-only source validators. The seven library routing tests pass on Windows Python and WSL Python.
- Worktree removal followed content verification and empty-directory checks. Windows/WSL registrations were repaired explicitly before retirement; no branch or commit was pruned.
- The loose parent-directory session prompt was moved into `prompts/historical/` and hash-verified separately.

## Evidence and use

[Verification](verification.json), [action totals](plan-summary.json), [original branches](workspaces.json), [retired worktrees](retired-worktrees.json), [browser checks](browser-check.json), [source validation](source-validation.json), and [directory-link receipt](supplemental-directory-links.json) document the result.

The complete local `inventory.sqlite3` and independently exported `preservation-map.jsonl.gz` map every old workspace/path to its retained path and SHA256. `execution.jsonl.gz` preserves the execution events losslessly; supplemental links have their separate receipt. Completed actions are tracked individually, so resumed event records are not added again to the removal totals.

Large local assets, archive variants and the complete local inventory remain excluded from public Git. The PR contains integrated source, navigation, tools and summary receipts. Preserve the entire main workspace when backing up artwork; cloning Git alone does not restore ignored assets.

Historical execution records and one-off scripts retain their original absolute paths. The library server remaps browser links and serves the exact historical file versions without recreating old checkouts. Historical scripts that assume the old folder layout may need their paths adapted before reuse. Production scripts that use the repository root and the tested readers work from the consolidated location.

The one-off consolidation tools are execution records, not a request to rerun cleanup. Keep future necessary temporary worktrees under `.worktrees/` and retire them after preserving unique outputs.
