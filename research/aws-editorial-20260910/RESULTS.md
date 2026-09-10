# Chapter 1 editorial experiment and review edition

The useful outcome is a small, reversible copy revision and evidence that these
Bedrock models should not approve continuity automatically. The original 48
illustrations, source chapter and prior reading edition are preserved.

Open [the edited chapter](reader/index.html). Its navigation switches between the
frozen original copy and the edited copy. The editable changes are in
[revision.json](revision.json); rebuild with `python3 scripts/build_aws_review_edition.py`.
Owner acceptance remains unset. The review edition is a local draft.

## Changes implemented

| Panel | Before | Review edition | Evidence and judgment |
|---|---|---|---|
| N1-09 | No time caption after the earlier-evening sequence | “Now. The upper gate.” | Makes the return from N1-02's explicit flashback unambiguous. Optional integrator clarification, not a proved reader defect. |
| N1-29 | “Hold I learned” | “Hold I unlocked” | Separates selecting the branch from learning to use it: the poor stop at N1-34 precedes the clean stop at N1-45. A model raised the distinction, but its proposed extra teaching scene was unnecessary. |
| N1-46 | Action/alt text says “a repaired kettle handle” | “her repaired kettle” | The frozen art shows a complete wrapped kettle with a handle. Intent/alt text correction only. |

No extra exposition, additional panels or art regeneration was needed. The
motivation (N1-06/07), costly rescue (N1-11/12/21), learning sequence
(N1-27/29/34/35/45), and delivery/pay/meal payoff (N1-42/48) remain coherent.

## What AWS actually tested

Fourteen paid requests, $0.050787 in measured token charges. Models: Amazon Nova
Lite v1, Nova Pro v1 and Nova 2 Lite via its US inference profile. The frozen
48-panel packet was supplied for text review. Nova 2 Lite also received all 48
unlettered images in six consecutive eight-image groups, plus clean and injected
continuity tests and one review of the edited packet. Models did not receive the
integrator's initial reading notes or injected-error answer key.

The two planted contradictions were missed: N1-35 swapped the newly torn left
sleeve to the right while claiming the left was intact; N1-08 claimed Hold was
already mastered and required no concentration before the branch choice and
later practice. Neither response identified its planted inconsistency. This
0/2 result is a small sensitivity probe, not a population accuracy estimate.

Four of six image-group responses passed structural citation checks; two cited
unattached images and were rejected. Other high-confidence statements were
plainly wrong: the N1-08 and N1-34 cyan lines are visible in the actual images,
despite claims that they were absent. Structural validity does not prove truth.
Narrative responses may have a single whole-response Markdown fence removed;
that tolerance is recorded. Raw output is retained. Extraction scoring uses a
stricter raw-JSON rule, so the two tasks' format measures differ.

## Adjudication of consequential suggestions

| Model suggestion | Decision and source evidence |
|---|---|
| Deepen Aren's motivation with flashbacks | Reject. Wage, private room and time to rest are already explicit in N1-06/07. |
| Rescue violates a power that pulls its user | Reject. N1-08 says his body carries the load; N1-13 excludes pulling the car; N1-19 explicitly carries Pell. |
| Explain the ray's origin or resolve the empty district immediately | Reject as a required fix. The opening art establishes the creature, and N1-39/43 supplies the job payoff while leaving the larger mystery open. |
| The lift must visibly detach to fall | Not established. The failed brake is explicit at N1-11. A descending lift need not detach; do not invent a cable break solely to satisfy this claim. |
| Add a scene showing Aren's anger at losing admission | Reject. His anger is already explicit in N1-21. |
| Explain Hold through dialogue | Already present in N1-28/29. Accept only the smaller unlocked/learned clarification above. |
| Make the line visible in N1-08 and N1-34 | Reject. It is visibly present in both frozen images, including at 390px width. |
| Treat the hem tear as an unmotivated new detail | Reject. N1-16 explicitly snags and tears the hem during rescue. Persistent-state intent is not proof of visibility in every crop. |
| Add more action frames to show drawing/sheathing | No change. N1-32 shows the weapon drawn and N1-33 uses it; N1-35 is a reaction insert. Comics can omit routine intermediate motions. |
| A close crop proves the elbow tear is clearly shown | Reject that certainty. N1-35 is extremely shallow and does not show the elbow clearly at phone size. No anatomy or damage certification follows from it. |
| The edited wallet is never referenced again | Reject. N1-21 returns the unstamped, unopened wallet. The revised review also requested mystery exposition; neither claim warranted another change. |

These models generated review questions, not trustworthy acceptance decisions.
The edited packet's different findings are not a controlled preference test or
proof that readers prefer the revision. Further art work should use explicit
panel-specific source comparison and owner judgment.

## Reading and reproducibility checks

The actual lettered reader loaded 48/48 images at 390×844, with no JavaScript
errors, horizontal page overflow or offscreen balloons. The original and edited
readings were both captured. The edited edition also passed layout checks at
320, 430 and 1024px widths. Manual phone-size inspection covered N1-08, N1-09,
N1-29, N1-32, N1-34, N1-35, N1-36 and N1-46, including both edited lettering
panels. This is not a complete panel-by-panel anatomical audit or an audience test.
All 48 native image hashes still match the frozen packet.

The reusable state/copy evidence is in [packet.json](packet.json) and
[revised-packet.json](revised-packet.json). Local captures and layout receipts are
under `previews/` (ignored). Native sources are under `assets/` (ignored). To
recapture, install Playwright and use `scripts/capture_aws_review_edition.py`.
This WSL setup also uses `LD_LIBRARY_PATH=/tmp/nightglass-pilot-browser-libs/usr/lib/x86_64-linux-gnu`.

Raw paid responses, model IDs, request hashes, exact packet hashes, usage and
structural validation are preserved in the sibling sprint repository's
`results/narrative/`. Its `run_narrative.py` is dry-run by default and requires
`--live` plus current AWS authorization to invoke a model. Completed identical
requests reuse the durable ledger cache.
