# ADR-0171: Complete chapter sequence strips before panel-local repair

- Status: Accepted engineering direction; visual and commercial review pending
- Date: 2026-09-02

## Context

Earlier CH05 work produced strong isolated panels and extensive instrumentation but did not provide a complete chapter reading experience. The owner asked to improve the pipeline in parallel with complete-chapter production rather than serially polishing disconnected art.

The current run generated 11 ordered sequence strips covering all 50 approved ComicPanelPlans, deterministically split them into 50 panel candidates, assembled clean/lettered/phone/continuity packets, and then applied two bounded repair steps: P001 alone, followed by the contiguous P031-P033 clue chain. Generated pixels remain ignored local evidence.

## Decision

Adopt sequence-strip-first complete chapter coverage as the current CH05 production mechanism, with these controls:

1. Generate coherent three-to-five-panel story sequences against exact ComicPanelPlans and explicit adult/hair/wardrobe/set constraints.
2. Deterministically crop and hash each panel, assemble the entire chapter, and review at phone width before spending effort on repairs.
3. Preserve source strips and failed crops as diagnostic evidence.
4. Replace only the smallest panel or contiguous causal sequence that fails a declared requirement.
5. Prove non-target stability by exact source hashes and keep human acceptance, rights, and exact-base decisions separate.
6. Keep ComicPanelPlan as the only active planning structure; AnimationShotPlan and E-Conte remain null.

The mechanism is selected on coverage, role/count/order, cast continuity, causal legibility, lettering clearance, phone readability, target-change behavior, and hash-exact no-change stability—not visual appeal alone.

## Evidence

- 50/50 plans represented in canonical order.
- Initial full-draft triage identified one opening failure and seven later warnings.
- P001 repair changed one panel and preserved 49/49 non-target hashes.
- P031-P033 repair changed three contiguous panels and preserved 47/47 non-target hashes.
- Current r3 agent triage is 45 PASS / 5 WARN / 0 FAIL; owner review remains pending.
- Hair/wardrobe continuity is visually stable across the 32 cast-bearing panels.
- Twenty review-only lettering beats use eight in-art safe zones and twelve outside-art gutters.
- Thirteen built-in ImageGen raster outputs produce 54 panel-level candidates: 50 initial crops and four repair candidates.
- No direct paid API, BFL call, cloud GPU, new provider, or unapproved upload was used. Built-in model, endpoint, request ID, usage, monetary cost, and seed remain unavailable.

## Consequences

The project now has a coherent chapter-scale review unit and a repair workflow whose unchanged outputs are measurable. The route is faster for narrative learning than isolated beauty-shot iteration and retains evidence for every miss.

Sequence strips can couple mistakes across panels and do not prove stochastic reproducibility. Subtle clue orientation and multi-object causal staging remain the hardest cases; P032, P036, P039, P043, and P029 remain WARN. Generated art is not accepted, commercially cleared, or selected as an exact production base.

## Next bounded milestone

Test one P036 causal-leverage repair using the existing authorized composition reference, then reassemble and compare it inside the complete chapter. Do not broaden upload, provider, model, or spending authority.
