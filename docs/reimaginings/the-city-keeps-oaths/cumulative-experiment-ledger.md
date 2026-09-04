# Cumulative experiment ledger

## Evidence inspected

North Garden evidence includes ADR-0016 (stable IDs), ADR-0090 (lettering footprint), ADR-0094 (per-panel density), ADR-0102 (manual review), ADR-0109 and ADR-0151 (exact RenderRecords and null metadata), ADR-0171 (breadth before repair), ADR-0177/0178 (story before prompts and fail-closed semantics), ADR-0188 (measured cadence), and ADR-0191 (causal repair isolation). Borrowed Down evidence includes its final audit, transferable-lessons record, style-probe review, schema/route ADR, two repair ADRs and comparisons, all 60 RenderRecords, compact CH01/CH10 reviews, and representative sequence sheets. These sources were inspected read-only in their protected worktrees.

## Retained lessons

- Stable panel IDs plus separate revision IDs enable repair without erasing history.
- `ComicPanelPlan` alone keeps narrative intent separate from rendering.
- Source art, crops, lettering, phone previews, and reviews require separate hashes.
- Phone review is a hard gate; safe-zone geometry and opacity cannot rescue poor placement.
- Density must be measured per rendered panel; a style label is not a density guarantee.
- Local defects receive local repair, with non-target hashes proved unchanged.
- Completion, owner acceptance, commercial clearance, exact-base status, and reproducibility are distinct.
- Unavailable provider fields remain null. Direct paid/cloud spend is reported separately.

## Rejected assumptions

- Prior canon, palettes, reference art, and visual identity are not reusable.
- A 3×2 sheet is not automatically optimal: it supported deterministic crops but was never compared fairly and produced crowded equal-weight compositions.
- Generated blank safe-area rectangles are not helpful; they visibly distract.
- Attractive isolated frames cannot compensate for chapter-scale fatigue.
- Structural and hash validity do not imply visual acceptance or commercial clearance.
- A single beauty score or vague manual-review label is adequate.

## New hypotheses and measurable decisions

1. Three-panel vertical strips will preserve more continuity than individual generation and more focus than six-moment grids. Pilot measures identity, causal order, crop independence, density, and phone clarity against individual and two-panel routes.
2. A fixed 16/5/3 low/moderate/high rhythm per 24 panels will reduce eye strain. Review measures edges, entropy, high-frequency occupancy, focal separation, and adjacency.
3. One cyan-gold effect family, bounded by dark navy/pearl values, will make progression readable without effect fog.
4. One local lettering unit per panel in LTRB safe zones will remain readable at 390 px without masking story information.

## Results to date

- Isolation established at the protected baseline; 159 pre-existing untracked files are hash-pinned.
- Four premise candidates were scored with a preregistered rubric; Premise A won 97/100 and is locked.
- Complete CH01–CH10 structured authorship compiles to 40 sequences, 240 immutable panels, 80 prompts, and 240 local-lettering entries.
- Structural, chronology, null cross-medium, safe-zone, prompt-hash, density-budget, and cross-chapter state checks pass with zero warnings.

Pilot, production, repair, and final owner-review results will be appended rather than rewriting these observations.

## Pilot result

Candidate A won the three-way style comparison at 93/100 without a refinement probe. The topology pilot compared six exact requests and selected the three-panel vertical strip at 94/100. Individual generation changed geometry across beats; the two-plus-one route preserved the quiet pair but drifted in the separately generated action; the three-strip retained identity, tool, direction, and causality while its thirds stayed phone-readable. Pilot-relative density thresholds are now locked in `production/reimaginings/the-city-keeps-oaths/pilot/density-calibration.json`.

## CH01 process check

CH01 is complete at 24 lettered panels. Manual source and 390-pixel review passes identity, mature appearance, chronology, action causality, effect restraint, focal clarity, and lettering clearance. Automated pilot-relative metrics WARN on 17 panels, chiefly because the generated stone/cloud rendering exceeds the low-class edge and entropy ceilings; visual inspection finds those panels clear and non-adjacent in spectacle. The warnings remain specific evidence and do not trigger aesthetic rerendering. Local dialogue size was increased from 28 to 36 source pixels (about 11.4 to 14.6 pixels at phone width) before later chapters were assembled.

## Final production and repair result

- Exactly CH01–CH10 are complete: 40 chronological sequences, 240 selected source panels, 240 deterministic lettering entries, and 80 production generation requests. All 80 used the locked three-panel vertical topology and the same three registered, experiment-native reference assets.
- Reconciliation passes for 91 total requests: 80 production, nine bounded style/topology pilot requests, and two reference-sheet requests. It verifies exact prompt text and hashes, 240 crop candidates, all output/reference hashes, crop coordinates, owner-review states, and null unavailable provider metadata with zero reconciliation errors.
- Summed independent measured generation latency is 28,172.185 seconds; it is explicitly not wall-clock duration. Direct paid/cloud spend is $0. No model, endpoint, provider request ID, usage, cost, or deterministic seed was available or invented.
- Manual volume review records 29 PASS and 11 WARN sequences, with no remaining FAIL. Specific retained warnings are story-readable pilot-density deviations, minor non-eye-covering lettering/head encroachment, one SFX/head encroachment, and intermittent visibility of Tarin's already-bent spear geometry.
- The automated pilot-relative proxies classify 54 panels PASS and 186 WARN. Their exact excursions remain visible: 144 edge-density, 160 high-frequency-occupancy, 98 global-entropy, and 54 focal-luminance proxy flags. This conservative result teaches that per-class pilot thresholds identify review candidates but over-flag a full volume with varied lighting and architecture; direct source, grayscale, contact-sheet, and 390-pixel inspection must retain control.
- One bounded repair wave found seven hard lettering-clearance failures in CH03–CH04. It moved only those deterministic LTRB safe zones, preserved before/after reviews, issued zero image-generation requests, and proved all 240 generated source-panel hashes unchanged. Post-repair manual inspection passes eyes, expressions, injury cues, progression effects, and causal objects.
- The final density rhythm remains 16 low / 5 moderate / 3 high panels in every chapter, with no undocumented adjacent maximum-density pair. Variable gutters add longer pauses after consequential choices and sequence consequences.

## What a future attempt should retain

Retain story-first immutable plans, a tiny hash-pinned reference set, three-moment vertical continuity strips, restrained one-family effects, deterministic local lettering, and phone review as the acceptance surface. Improve the next metric calibration with stratified samples from dialogue, architecture, night action, and bright climax panels rather than one compact pilot alone. Add composition-aware lettering placement before first assembly; fixed role-position safe zones are a useful default but cannot predict generated face location. Preserve the same anti-churn rule: finish breadth, repair only hard defects, and leave story-readable WARN evidence visible.
