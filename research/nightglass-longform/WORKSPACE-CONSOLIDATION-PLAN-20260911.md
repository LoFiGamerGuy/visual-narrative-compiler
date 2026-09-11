# Workspace consolidation and space-recovery plan

Assessment dated 2026-09-11. No artwork, source file, archive, worktree or environment was moved or deleted. This is a proposed cleanup plan; Chapter 9 remains delivered and production remains stopped.

**Recommendation: begin with a 46.49 GB cleanup of redundant delivery copies and two proven duplicate ZIPs, preserving every distinct milestone ZIP and the current reader.** Check failed/partial builds separately for another 6.60 GB. Offloading the eight older Nightglass ZIPs to verified storage outside C: adds 20.94 GB of C: recovery. These three non-overlapping groups total **74.03 GB potential**, before environment or inactive-worktree cleanup.

## What is actually taking space

The inventory covers all 27 `C:\AgentWorkspaces\anime-pipeline*` folders: **212.55 GB**, 521,974 files. The 445 archive-format files total **34.45 GB**; many are small library/runtime files, not large comic deliveries. Measurements are logical file sizes in decimal GB. Actual freed disk space can differ with hardlinks, sparse allocation and files retained in the Recycle Bin. Downloads, other projects, other drives and WSL temporary storage are outside this inventory.

| Area | Size | Main contents |
| --- | ---: | --- |
| Main `anime-pipeline` | 95.55 GB | ComfyUI models 62.51 GB; Anima-Diffusers models 5.64 GB; Python environments and earlier experiments |
| Nightglass longform worktree | 86.54 GB | Package/output alone 73.29 GB; more extraction copies live under research |
| Other 25 folders | 30.47 GB | Independent experiments, pilots, unique assets, source archives and review copies |
| Nine Nightglass milestone ZIPs | 24.90 GB | Included in the longform total, not additional |

These are already worktrees of one shared Git repository. The main Git object directory is only about 0.315 GB. Reorganizing Git history is not the major space opportunity, and a large merge is unnecessary.

The nine release manifests list 26.81 GB of repeated payloads, representing about 3.78 GB of distinct content hashes. The eight older releases together contain only **3.07 MB of distinct payload content absent from Nine-v1**, mainly earlier scripts, lettering/selection state, generated reader data and status documents. Their own manifests add about 11.14 MB. This is SHA256/size comparison of existing manifests, not a claim that the older ZIPs are byte-identical or disposable. Historical exact ZIP bytes and earlier reader states still have preservation value.

## 1. Recover approximately 46.49 GB while retaining every distinct ZIP

Keep the existing `Nightglass-NineChapters-v1` directory and ZIP in their current locations. Keep the live source worktree, editable scripts/lettering, all original and rejected generation attempts, native/raw tool records, reference bindings, training data and trained LoRAs. Keep every verification report, manifest, failure explanation and actual review screenshot.

Before any removal, produce a small explicit action ledger binding each candidate to its retained source ZIP or identical surviving file, its size and its evidence. Reuse valid verification receipts; check that retained archives still match their recorded identities and that candidate folders have no later unique additions. This does not require another editorial reread or another full extraction of every archive.

### A. Eight older unpacked build directories: 22.50 GB

All are under the longform worktree's `production\nightglass-longform\package\output\`. Remove these unpacked build copies after matching their inventories to retained ZIPs; preserve the ZIPs and adjacent build receipts. Do not remove the current Nine-v1 reader directory.

| Directory | GB |
| --- | ---: |
| `Nightglass-Chapter1-v1` | 1.300 |
| `Nightglass-EightChapters-v1` | 3.962 |
| `Nightglass-FiveChapters-v1` | 2.739 |
| `Nightglass-FourChapters-v1` | 2.373 |
| `Nightglass-SevenChapters-v1` | 3.490 |
| `Nightglass-SevenChapters-v2` | 3.490 |
| `Nightglass-SixChapters-v2` | 3.109 |
| `Nightglass-ThreeChapters-v1` | 2.034 |

### B. Eight completed extraction copies: 23.34 GB

Remove **only the `extracted` child directories below**. Preserve each parent directory's `verification.json`, screenshots, review notes and failure/retry history. The current default reader entry remains the separate Nine-v1 build directory, so its location stays valid.

| Path relative to the longform worktree | GB |
| --- | ---: |
| `production\nightglass-longform\package\output\Nightglass-EightChapters-v1-verification\extracted` | 3.962 |
| `production\nightglass-longform\package\output\Nightglass-NineChapters-v1-verification\extracted` | 4.331 |
| `production\nightglass-longform\package\output\Nightglass-SevenChapters-v2-verification\extracted` | 3.490 |
| `production\nightglass-longform\package\output\Nightglass-SixChapters-v2-verification\extracted` | 3.109 |
| `research\nightglass-longform\assets\package\Nightglass-Chapter1-v1-verification\extracted` | 1.300 |
| `research\nightglass-longform\assets\package\Nightglass-FiveChapters-v1-verification\extracted` | 2.739 |
| `research\nightglass-longform\assets\package\Nightglass-FourChapters-v1-verification\extracted` | 2.373 |
| `research\nightglass-longform\assets\package\Nightglass-ThreeChapters-v1-verification\extracted` | 2.034 |

Chapter1's original extraction passed its manifest-file checks but its first browser check failed; later browser-r2 evidence exists separately. Preserve both records with their actual results. Do not relabel the failed check as a pass. Seven-v1's failed extraction is excluded from this group and handled in phase 2.

### C. Two confirmed exact ZIP duplicates: 0.653 GB

SHA256 was freshly calculated for both files in each pair:

- Main worktree: `loras-trained_2026-08-30_2022.zip` and `loras-trained_2026-08-31_0048.zip`, each 127,455,364 bytes, both SHA256 `b88812a63aab1ff7216ec575093687c991f5f187222805bc1c1da15e09d686cd`. Prefer retaining the 2026-08-31 archive; check references before retiring the 2026-08-30 filename and record it as an alias. Preserve the trained LoRAs themselves.
- Structural worktree, `research\structural-pilot\asset-bundle\local\`: `rebuilt-assets.zip` and `SC-20260907-01-preserved-assets.zip`, each 525,081,219 bytes, both SHA256 `14caa4b1b284c83e9406e1f74825122df929657bacd26da4e24825a420e7382e`. Prefer retaining the named `SC-20260907-01-preserved-assets.zip`; check references before retiring the redundant filename.

Equal names, timestamps or sizes alone are not sufficient evidence. These two pairs have matching full-file hashes.

After the approved removal pass, check the current reader entry and its local dependencies, record actual free-space change and append the exact actions to the cleanup ledger. Historical receipts remain historical; the ledger explains where their removable extraction paths went. Simply moving copies elsewhere on C: does not reclaim space.

## 2. Check failed and partial build copies: another 6.60 GB

Both are under `production\nightglass-longform\package\output\`:

- `Nightglass-SevenChapters-v1-verification\extracted`: **3.490 GB**. Preserve the failed Seven-v1 ZIP and its case-alias failure evidence; the extracted diagnostic copy can be retired after identifying any unique additions.
- `Nightglass-SixChapters-v1`: **3.108 GB**. This partial build has no completed manifest/ZIP beside it. Compare its files against retained Six-v2, Nine-v1 and live source, preserving any unique files and path/hash mapping before removing the directory. Do not assume an incomplete directory is empty or redundant.

These are conditional candidates, not yet approved deletions. Phase 1 plus both would recover approximately **53.08 GB**.

## 3. Consolidate historical ZIP storage: another 20.94 GB on C:

Keep the immutable **Nine-v1 ZIP (3.958 GB)** and one unpacked current reader on C:. Keep its existing SHA256 `948d2571f5f5d193c61c41223679a41fdbd6a9dc8408a23eb7c691ea67969b5d` and the final handoff/verification evidence.

Preferred preservation approach: place the other eight distinct Nightglass ZIPs on an existing backup/archive volume outside C:, verify the copied bytes, record their destination and then remove the C: copies. Moving them to a new folder on C: would improve organization but free no space. Do not assume a second drive or backup has already been verified.

If exact old ZIP preservation is no longer desired, a separate option is to retain Nine-v1 plus each earlier manifest and the distinct historical payload files. That preserves earlier file content and reader states, but it does **not** preserve the original ZIP byte stream or automatically reproduce its old SHA256. This option needs a restore demonstration and an explicit change to the previous preservation policy. It is not the recommended first pass, and it does not justify building another giant all-in-one ZIP.

## 4. Reduce folder sprawl without losing independent work

Start with one small catalog linking to current assets at their existing paths. Avoid a mass rename while old absolute paths and Windows/WSL worktree registrations still exist.

Proposed logical organization:

```text
C:\AgentWorkspaces\
  anime-pipeline\                         shared Git repository and local tooling
  anime-pipeline-nightglass-longform-...\  canonical Nightglass source, kept in place
  anime-library\
    INDEX.md                              one human entry point
    releases\                             current release links and archive-location index
    evidence\                             manifests, receipts and review index
    experiments\                          one catalog entry per independent project
```

Initially those catalog entries link to existing locations; they do not copy the underlying folders again. Physical moves can follow once dependencies are understood. Keep the current reader link stable through phase 1.

Classify each worktree as active, retained source reference, or retired experiment. Keep the main repository and Nightglass source. Treat the recent AWS editorial worktree and any other ongoing work as potentially active until checked. For each retired experiment:

1. Preserve its branch/commit and check uncommitted, untracked and ignored files. Git history alone does not preserve ignored native artwork or raw generation results.
2. Identify unique artwork, prompts, failed attempts, training assets and reports. Retain one verified canonical copy, with original path/hash provenance. Avoid another full copy of shared tools/models or every earlier worktree.
3. Retire the physical checkout through Git's worktree mechanism only after its unique material is retained. Keep the independent branch and catalog entry; do not merge unrelated experiments merely to reduce folder count.

There are **eight Windows-style worktree registrations** shown as “prunable” by WSL while their corresponding folders still exist. Resolve the Windows/WSL registration mismatch before any pruning or moves; do not delete them based on that label.

The other 25 folders total 30.47 GB, but that is an inventory total, **not a promised saving**. Some contain unique independent work, and some duplicate-archive savings already appear above. Do not add the whole total to the 74.03 GB estimate.

## 5. Separate optional environment/model cleanup

The main workspace contains:

- `ComfyUI\models`: **62.51 GB**.
- `models\Anima-Diffusers`: **5.64 GB**.
- `ComfyUI\venv`: **6.38 GB** and `ai-toolkit\venv`: **5.89 GB**.
- `ai-toolkit\venv_py314_dead`: **4.65 GB**.
- `experiments\review-packets`: **4.69 GB**.

The folder named `venv_py314_dead` is a promising candidate, but its name does not prove it is unused. Confirm launch scripts/processes do not rely on it and preserve environment specifications before removing it. Keep working environments initially.

Audit model use and hashes separately. Two ControlNet files have the same 2.513 GB size and similar names; that is only a duplicate candidate, not a verified match. Other same-size checkpoints can contain different models. Preserve trained LoRAs, unique checkpoints and datasets; do not delete models solely because this recent run used built-in generation. Do not hardlink mutable environments or artwork to force deduplication.

No model or environment savings are included in the recommended 46.49 GB or the 74.03 GB phased estimate.

## Prevent recurrence

- Keep one current unpacked delivery and one current ZIP. Delete temporary verification extractions after evidence is saved and the retained ZIP is checked, under an agreed retention policy.
- Create full preservation releases at owner-review milestones, rather than packaging the entire production history after every chapter. Intermediate chapters can retain scripts, selected sources, commits and small receipts.
- Separate a future **reading package** from the **production preservation archive**. Nine-v1 currently carries 0.87 GB of reader-check evidence and 0.19 GB of pilot-lettering evidence among its sources. The nine chapters' 387 unique selected image paths total about **0.612 GB**, before HTML, copy and any optional pilot/comparison/history dependencies. That supports a substantially smaller future reader package; it is not a finished package-size promise. Include or deliberately adjust all required links, and verify the new package once. Leave Nine-v1 unchanged.
- Record active worktrees and retire completed temporary checkouts after unique ignored material is preserved. Limit new worktrees to active independent work, rather than retaining every checkout indefinitely.
- Retain small failure reports and exact provenance; discard only proven duplicate bulk copies. Do not regenerate artwork or cosmetically reroll anything for this cleanup.

## Measured workspace inventory

| Folder | GB |
| --- | ---: |
| `anime-pipeline` | 95.55 |
| `anime-pipeline-nightglass-longform-20260909-2110` | 86.54 |
| `anime-pipeline-pilot-chapters-20260909-1310` | 4.80 |
| `anime-pipeline-structural-20260907-054652` | 3.27 |
| `anime-pipeline-nightglass-refinement-20260908-1015` | 2.34 |
| `anime-pipeline-anchor-return-20260909-1030` | 2.32 |
| `anime-pipeline-encounter-lab-20260909-0430` | 1.99 |
| `anime-pipeline-reimagining-20260903` | 1.91 |
| `anime-pipeline-combat-depth-20260908-2310` | 1.88 |
| `anime-pipeline-refinement-20260907-1600` | 1.80 |
| `anime-pipeline-impact-clarity-20260909-0245` | 1.65 |
| `anime-pipeline-scale-conflict-20260908` | 1.41 |
| `anime-pipeline-world-components-20260907-1830` | 1.03 |
| `anime-pipeline-world-combat-20260908-0300` | 0.93 |
| `anime-pipeline-reimagining-clean-webtoon-20260903-213010` | 0.91 |
| `anime-pipeline-directions-20260907-1230` | 0.90 |
| `anime-pipeline-litrpg-manhwa-20260904-001211` | 0.62 |
| `anime-pipeline-aws-editorial-20260910` | 0.56 |
| `anime-pipeline-combat-exploration-20260908-0100` | 0.54 |
| `anime-pipeline-ember-lattice-editorial-gear-20260904` | 0.35 |
| `anime-pipeline-sequence-pilot-20260907-035400` | 0.32 |
| `anime-pipeline-total-review-20260907-014149` | 0.32 |
| `anime-pipeline-ember-lattice-premium-rd-20260904-150943` | 0.32 |
| `anime-pipeline-texture-kit-20260908` | 0.16 |
| `anime-pipeline-total-review-20260906-211925` | 0.05 |
| `anime-pipeline-total-review-20260905-092558` | 0.04 |
| `anime-pipeline-reimagining` | 0.03 |

The adjacent [evidence JSON](WORKSPACE-CONSOLIDATION-EVIDENCE-20260911.json) contains measured paths/sizes, candidate lists, manifest overlap analysis and the exact-duplicate hashes. The existing [Chapter 9 final handoff](FINAL-CHAPTER9-HANDOFF.md) remains the production completion record. This plan proposes future cleanup; it does not modify the preservation policy or authorize further comic production.
