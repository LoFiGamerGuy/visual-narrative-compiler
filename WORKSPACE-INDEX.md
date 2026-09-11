# Consolidated anime-pipeline workspace

Open [START-HERE.html](START-HERE.html) for current readers and galleries. On Windows, double-click `start-library.cmd`. On Linux/WSL, run `python scripts/serve_library.py --open`. The local server also exposes exact historical workspace views and remaps old browser links without rewriting historical evidence.

All 26 former sibling workspaces are consolidated here. Their Git branches remain, and their unique local files are preserved. The current source includes Nightglass, both earlier independent stories, AWS editorial work, and both versions of the pipeline review.

| Location | Contents |
| --- | --- |
| `production/` | Current production sources, native art and releases |
| `docs/` | Readers, galleries and guides |
| `research/` | Experiments, prompts, reviews and evidence |
| `reimaginings/`, `src/`, `scripts/` | Story bibles and reusable source |
| `archive/workspace-variants/` | Conflicting historical file contents, stored once by SHA256 |
| `research/workspace-consolidation-20260911/` | Inventory, original branches, path mapping, execution and verification records |

The local `inventory.sqlite3` maps every original file to its retained destination. `preservation-map.jsonl.gz` is an independent, compressed JSONL export of that mapping. Each row includes the former workspace, original path, retained destination and SHA256. The archive and full local inventory remain outside public Git; Git is not a backup of ignored artwork.

For a historical file, query the mapping or open its `/workspaces/<old-folder>/<original-path>` URL through the library server. Historical absolute symlink targets (browser locks and security fixtures) are recorded unchanged and are not active runtime paths. Old execution receipts describe their original locations and are intentionally retained as evidence.

Avoid creating another permanent sibling checkout. Keep routine work in this consolidated tree. If concurrent work needs isolation, create a temporary worktree under `.worktrees/`, preserve its unique local output and retire it when finished. Do not merge independent story canon merely because its source shares a repository.

## Retained branches

| Former workspace | Branch | Original commit |
| --- | --- | --- |
| anime-pipeline-anchor-return-20260909-1030 | `autonomous/anchor-return-20260909-1030` | `407750b0e74a` |
| anime-pipeline-aws-editorial-20260910 | `codex/aws-editorial-20260910` | `55b37497152c` |
| anime-pipeline-combat-depth-20260908-2310 | `autonomous/nightglass-combat-depth-20260908-2310` | `45cb51416613` |
| anime-pipeline-combat-exploration-20260908-0100 | `autonomous/combat-exploration-20260908-0100` | `6d9072cb22b0` |
| anime-pipeline-directions-20260907-1230 | `autonomous/visual-directions-20260907-1230` | `92a7642da726` |
| anime-pipeline-ember-lattice-editorial-gear-20260904 | `autonomous/ember-lattice-editorial-gear-20260904` | `99cb5e9e37c2` |
| anime-pipeline-ember-lattice-premium-rd-20260904-150943 | `autonomous/ember-lattice-premium-rd-20260904-150943` | `fb10c87f974d` |
| anime-pipeline-encounter-lab-20260909-0430 | `autonomous/encounter-lab-20260909-0430` | `4ce4ba4f01e5` |
| anime-pipeline-impact-clarity-20260909-0245 | `autonomous/nightglass-impact-clarity-20260909-0245` | `7c09ecd8c310` |
| anime-pipeline-litrpg-manhwa-20260904-001211 | `autonomous/ten-chapter-litrpg-manhwa-20260904-001211` | `023330e8b623` |
| anime-pipeline-nightglass-longform-20260909-2110 | `autonomous/nightglass-longform-20260909-2110` | `7cababad1636` |
| anime-pipeline-nightglass-refinement-20260908-1015 | `autonomous/nightglass-refinement-20260908-1015` | `83b06de98121` |
| anime-pipeline-pilot-chapters-20260909-1310 | `autonomous/pilot-chapters-20260909-1310` | `4611831b8ca6` |
| anime-pipeline-refinement-20260907-1600 | `autonomous/visual-refinement-20260907-1600` | `dfc8f2390947` |
| anime-pipeline-reimagining | `autonomous/ten-chapter-reimagining` | `40e7940016ea` |
| anime-pipeline-reimagining-20260903 | `autonomous/ten-chapter-reimagining-20260903` | `fa6650a4f8e5` |
| anime-pipeline-reimagining-clean-webtoon-20260903-213010 | `autonomous/ten-chapter-clean-webtoon-20260903-213010` | `d1cfa464be35` |
| anime-pipeline-scale-conflict-20260908 | `autonomous/nightglass-scale-conflict-20260908` | `e2d14ab965c2` |
| anime-pipeline-sequence-pilot-20260907-035400 | `autonomous/sequence-pilot-20260907-035400` | `0c1a8fb337d8` |
| anime-pipeline-structural-20260907-054652 | `autonomous/structural-20260907-054652` | `8212771a5344` |
| anime-pipeline-texture-kit-20260908 | `docs/texture-refinement-kit-20260908` | `3a9a48ce464f` |
| anime-pipeline-total-review-20260905-092558 | `autonomous/anime-pipeline-total-review-20260905-092558` | `99cb5e9e37c2` |
| anime-pipeline-total-review-20260906-211925 | `autonomous/anime-pipeline-total-review-20260906-211925` | `9e2fff7b0367` |
| anime-pipeline-total-review-20260907-014149 | `autonomous/anime-pipeline-total-review-20260907-014149` | `9a911fd80250` |
| anime-pipeline-world-combat-20260908-0300 | `autonomous/world-combat-20260908-0300` | `ccc23de8dec2` |
| anime-pipeline-world-components-20260907-1830 | `autonomous/world-components-20260907-1830` | `9753cceac0c2` |
