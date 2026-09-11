# Borrowed Down — final production audit

## Outcome

The isolated branch contains one complete ten-chapter owner-review volume: 60 active sequences, 300 selected panels, and 300 locally applied lettering entries. Structural validation, render-record reconciliation, repair isolation, generated-pixel tracking checks, automated tests, and protected-branch checks pass.

## Quantitative record

- Active chapters / sequences / selected panels: 10 / 60 / 300
- Active sequence review status: 34 PASS / 26 WARN / 0 FAIL
- Preserved diagnostic failures: 2
- Generation requests: 67 total — 62 sequence or repair requests, 4 style probes, 1 character-reference request
- Summed measured generation latency: 15,939.808 seconds; overlapping agent calls are summed, not treated as wall-clock time
- Direct paid/cloud spend: $0
- Provider usage, cost, model snapshot, request ID, and deterministic seed: unavailable and recorded as null
- Generated pixels tracked by Git: 0

## Targeted repairs

1. CH08-S01 was rerendered to prevent reuse of Dax's irreversibly spent breath knot. All 295 then-non-target panel hashes remained exact.
2. CH10-S04-P05 alone was replaced to remove incorrect toothed reptilian anatomy from the adult keelback mother. All other 299 selected-panel hashes remained exact.

Both failed originals, their RenderRecords, and their pre-repair hash snapshots remain under `production/reimaginings/borrowed-down/diagnostics/` and the ignored local diagnostics-art folder.

## Known limitations retained for owner review

- The 26 WARN sequences remain story-readable. Ten are explicitly marked for identity or cape-state drift; sixteen retain conservative `manual_visual_review_required` classification.
- Generated safe-area rectangles are part of the unlettered candidates. Final lettering is applied locally in bands outside the artwork; an owner may elect to mask or redesign the blank regions.
- Some later sheets are visually dense at phone size even though their assembled lettering bands remain readable.
- The images are generated candidates, not accepted production masters. Commercial clearance and exact reproducibility are not established.

## Integrity

The work was produced only in `C:\AgentWorkspaces\anime-pipeline-reimagining-20260903` on `autonomous/ten-chapter-reimagining-20260903`. At audit time, the original worktree, local `main`, and `origin/main` all remained at protected commit `40e7940016ea3c3966752b61f55a931f91a13ac7`; the original worktree's pre-existing untracked files remained present and untouched.
