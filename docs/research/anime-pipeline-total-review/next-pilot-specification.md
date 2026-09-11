# Next-pilot specification

Machine-readable: `next-pilot-plan.json`. Direct spend default: **$0**. No ten-chapter authorization. No upload of protected or third-party art.

## What this pilot is

A **14-panel frozen sequential-art benchmark** with optional Ember Lattice faces. Purpose: prove visible page quality of a storyboard-first route against the current hybrid **before** any further long-form production.

It is **not** a new IP by default. Ember CH01 premium *beats* may be the payload if every panel is newly staged. If the owner wants story isolated from craft, use the neutral beats below with original adult characters that are not Elian/Mira.

## Hypotheses (pre-registered)

H1: A complete phone storyboard that later stages must match will raise panel-to-panel causality and action contact versus current hybrid on the same beats.

H2: Human correction of faces, hands, and contact (even a few hours) will beat denoise+relettering on blinded review.

H3: Ember’s premise is not the blocking factor; if H1+H2 pass and the owner still rejects the pages, the remaining dislike is story/desire → trigger fallback D.

## Frozen before any generation

- 14 beats (below)
- Two adult fictional characters (Ember Elian/Mira **or** new originals; no children)
- One monster/threat with a single locked silhouette
- One environment (one stage; no cream-studio inserts)
- Camera/action intent per beat
- Lettering copy (final)
- System state deltas
- Rubric: `common-rubric.json` v1 (already frozen)
- Attempt budget: one primary candidate per panel per route; one retry only for hard fail; no beauty-variant loop

## 14 beats

1. Extreme-wide: adults enter a dangerous space (hook, genre-legible).
2. Adult close-up with acting (not a stock scowl).
3. Two-character emotional exchange (eyelines, tails).
4. Quiet breath / geography lock (the stage the fight will use).
5. System/progression beat (one number changes a choice).
6. Monster reveal (silhouette first).
7. Anticipation (weight shift, not the hit).
8. Attack (contact readable without text).
9. Counter.
10. Reversal.
11. Impact (force, not a poster).
12. Aftermath (injury/object on the same stage).
13. Vertical reveal (height change that only scroll can do).
14. Chapter-end image that asks a question (no “volume” speech).

## Visual-direction contract (no title/artist imitation)

- Original clean action-anime/manhwa **line**, two-step cel, spare backgrounds on low-density beats.
- One accent color for the supernatural, not a global ember wash.
- Distinct silhouettes; mature adult faces; practical gear.
- Forbidden: named-living-artist prompts; named-title style; blue holographic RPG chrome; painterly fog-prestige; extra digits; baked blank lettering boxes.

## Routes (must differ materially)

1. **Current hybrid control** — existing Ember ImageGen+SVG method, new plates only, no reuse of prior rasters.
2. **Storyboard-first modular** — drawn or 3D-block thumbnails locked; generate or draw into those layouts; SVG lettering after.
3. **Optional third, only if hours exist:** human line/cleanup on route 2’s layouts (the C package). If hours do not exist, skip route 3 and treat route 2 as the B-inside-C test.

Do not treat prompt synonyms as a third route. Do not ship identical overlay bytes under three folder names.

## Budgets

- Attempts: 1+1 hard-fail retry per panel per route
- Repair: faces/hands/contact only
- Paid/cloud: $0 unless owner separately authorizes
- Tools: existing authorized local or in-product only
- Preserve all fails and exact instructions

## Human review

Roles: storyboard/action, cleanup/acting, letterer, owner. Timed minutes must be non-null. Two independent reviewers score with the frozen rubric **without** seeing route labels (blinded files). Owner answers only:

1. Which set would you continue?
2. Did you understand the fight without reading?
3. Did you want panel 15?
4. Is this closer to the feeling you want from the named bar, without copying those titles?

## Hard pass / fail

**Pass (all required):**

- Both blinded reviewers prefer route 2 (or 3) over route 1 on sequential storytelling **and** action choreography by ≥1.0 mean, and the owner prefers it.
- Action beats 7–12 keep one stage.
- No extra digits on shipped plates.
- Phone 390×844: min dialogue ≥14 CSS px; no horizontal overflow; tails unambiguous.
- Human minutes recorded.

**Fail / kill:**

- Generator ignores layouts on >3/14 after one retry → B-as-destination dies; full C layered finish required or stop.
- Owner prefers route 1 → H1 rejected; do not scale C on faith.
- Owner rejects *after* H1+H2 pass → fallback D (new story, same spine).
- Owner will not review → stop. Do not batch `REVIEWED_PASS`.

**Approval authorizes:** one 16–40 panel episode using the winning route, still not ten chapters.

**Rejection teaches:** whether the gap is story, craft, or staffing.

## Files to preserve

Storyboard SVGs, all candidates, prompts, hashes, review sheets, minutes, this spec. No overwrite of prior pipeline outputs.
