# Changed files and integrity

This review is isolated at `/mnt/c/AgentWorkspaces/anime-pipeline-total-review-20260907-014149`, on `autonomous/anime-pipeline-total-review-20260907-014149`, from the exact approved source commit **99cb5e9e37c211965a01213a6f7af7103aee8cf3**. All new analysis, tools, static vector proof and report builds reside under this checkout's two review namespaces. No prior comic source, raster cache, private reference, model, dataset or credential is included in the change.

## Protected state

The [initial snapshot](evidence/protected-state-initial.json.gz), [original final snapshot](evidence/protected-state-final.json.gz), [original comparison](evidence/protected-state-comparison.json) and [handoff recheck](evidence/protected-state-comparison-handoff.json) preserve the measured result. **The strict all-trees-unchanged result is FAIL.** Eight of nine prior trees pass; the other prior review branch advanced apparently through concurrent activity, with actor unverified. The owner subsequently authorized finishing subject to independent analysis. [Exact incident](evidence/external-change-incident.md), [independence and authorization](evidence/independence-and-authorization.md), [machine disposition](evidence/preservation-exception-disposition.json).

`main`, `origin/main`, all seven original prompt-listed production trees, and the other dormant review tree are unchanged. The original dirty root retains all 180,630 files and their compared metadata; 36,749 eligible content hashes were checked. Across protected trees, every file's size/mtime/ctime/mode and selected hashes were compared. Files over 32 MiB and excluded model/dataset/private-reference/vendor trees have metadata protection, not complete content digests. Access times and shared mutable Git object/log administration are outside the comparison; prior worktree HEAD/index/admin hashes are included. This is a precise non-interference check with explicit limits, not an impossible guarantee against all outside activity.

## Exact changed-file inventory

The [file manifest](evidence/changed-files.json) enumerates every new tracked file relative to this checkout. All are additions under `research/anime-pipeline-total-review/` or `docs/research/anime-pipeline-total-review/`; no existing tracked file is edited. The manifest is reconciled against Git before handoff. Built report HTML, JSON evidence, small deterministic tools and the original inline-SVG rough are included. The two compressed preservation snapshots contain evidence metadata/hashes, not source images or model data.

Ignored scratch contains local dependencies, browser profiles and internal screenshots; it is not staged. The review-specific ignore file permits only its own analysis tools despite the inherited broad `tools/` ignore. No prior-work ignore policy is edited.

## Commit and parity receipt

The source commit is recorded above. The payload commit and its verified push are recorded in the delivery receipt added after the first commit. The enclosing final delivery commit is resolved by `git rev-parse HEAD`; its exact SHA and remote parity are reported in the final owner handoff and local ignored `.scratch/handoff-final.json`. A tracked file cannot contain its own final commit hash without changing that hash, so no self-referential or stale SHA is presented as current parity. The final receipt explicitly distinguishes payload verification from the enclosing receipt commit.

Only this isolated branch is pushed to the existing authorized origin. No merge, main edit, prior branch checkout, cleanup or protected-file restoration occurs. Final handoff requires the isolated worktree to be clean and `git ls-remote origin refs/heads/autonomous/anime-pipeline-total-review-20260907-014149` to equal local HEAD.

## Package checks

[Browser QA](browser-qa.md) covers phone and two desktop sizes, all report pages, 120 scorecard combinations and four strategy views per viewport, static-proof controls and synthetic lettering expansion. [Package checks](evidence/package-checks.json) verify JSON/local references and no external runtime dependencies; [four deterministic tests](evidence/deterministic-tests.json) pass. No production art bakeoff, human preference or commercial clearance is claimed. Incremental direct paid/cloud spend is [zero](evidence/session-spend.json).
