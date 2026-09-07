# Validation and Goodhart audit

Companion matrix: `evidence/validation-map.json` (41 rows from the pipeline engineer). Leaner stack at the end.

## What current gates actually prove

| Current validation | Proves | Does not prove | False-pass example | Disposition |
| --- | --- | --- | --- | --- |
| JSON schema / hash chain | Byte identity of records | Beauty, acting, causality | Hardening N/N mutation rejection on null-filled templates | Retain as integrity |
| Duplicate-art exact hash | Exact file copies | Near-duplicate poses, lettering-hidden reuse | Volume sources: 225 unique hashes while compositions repeat (two-on-a-bridge) | Keep exact hash; add human pose review |
| Protected-zone collision | Overlay box vs declared region | Whether the region was the right place to letter | Volume 9-line cards inside “safe” corners that still brick a two-shot | Modify: collision + max lines + phone px |
| Lettering density / phone type | Geometry vs thresholds | Whether copy is comics dialogue | Volume 14px-ish type in 9-line cloned rects; premium original 32/52 < 12px at 390 | Keep as hard gate at 390px; add max lines |
| State arithmetic | XP/HP/item conservation | Reader understands the cost | CH07 protection gate explained in balloons over a kneeling glow | Retain arithmetic; do not treat as drama |
| Action-sequence assertions | Plan fields exist | Pixels show attack/counter/reversal | Phase B fight-causality PASS vs CH01 cream cutouts | Modify: require visible contact on named action IDs |
| Complexion/identity contracts | Prompt contains phrases | Face is the same person | Three CH05 refs across 50 panels; Mira hair flip in premium | Prompt gates → pixel review |
| Clean-art / noise metrics | Entropy, edge density | Beauty or “busy filter” gone | Editorial-clean denoise leaves extra fingers | Diagnostic only; never a pass |
| Rubric / agent triage | An LLM or hardcoded PASS | Owner preference | 47 PASS / 3 WARN / 0 FAIL then ten more chapters | Remove as a ship gate |
| `REVIEWED_PASS` | A script wrote a note | A human looked at each panel | `mark_art_review.py` stamps one note on 8 or 24 rows; 224/225 PASS; 11 unique notes | Hard-fail batch notes; require per-panel or timed session |
| HTML link / build ledger | Overlay files exist | Rasters exist in a clean checkout | Tracked volume PASS; `experiments/` absent here | Modify: reader must declare missing rasters |
| Browser QA | No overflow/console at a served URL on a cache-rich machine | Portable reader | `browser-verification.json` PASS with 0 broken images where rasters were present | Retain; add clean-checkout broken-image test |
| Owner-approval state | Explicit JSON | Later “not like ToG/SL” | Pilot APPROVED + Candidate B praise, then this assignment’s felt gap | Owner later rejection outranks earlier praise |

## Goodharted metrics

1. **Mutation-rejection count.** Validators prove they reject corrupted JSON. They became the programme’s throughput metric (`docs/REPOSITORY_REVIEW_2026-09-06.md` in the dirty root: 317 validators, 1 accepted artifact post-instrumentation).
2. **Chapter-batch `REVIEWED_PASS`.** Optimizes “all rows green.”
3. **Prompt-substring / semantic-gate phrases.** Optimizes the English contract, not pixels.
4. **Density labels (low/moderate/high).** ADR-0094 already said measure rendered panels; volume still ships planned density that P005 violated in the pilot.
5. **Identical overlay folders named hybrid/baseline/raw.** Optimizes “three routes exist.” Bytes are the same (lettering specialist: 52/52).
6. **Built-in spend recorded as $0.** Optimizes the $0 constraint while the live renderer’s cost is **null**, not zero.

## Leaner acceptance stack (recommendation)

**Hard gates (machine):** schema, hashes, exact-duplicate, missing-raster, phone min type at **390px**, max spoken lines per balloon, overlay-outside-viewBox, irreversible state arithmetic, no child-coded tags.

**Diagnostics (never ship-green):** entropy, edge density, CLIP, agent triage, planned density labels, mutation counts as a dashboard.

**Human (timed, blinded where practical):** acting, contact, identity, chapter-end desire-to-continue, phone scroll of the actual reader. Until `human_minutes != null`, no ten-chapter authorization.

**Remove:** hardcoded Phase B PASS markdown as evidence of craft; agent-triage compiler as a ranking instrument.
