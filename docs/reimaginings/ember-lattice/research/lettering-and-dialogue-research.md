# Phase B lettering and dialogue research

Research date: 2026-09-04. This research answers the owner's concrete pilot feedback: the balloon shapes cover too much art, the copy is too short, and the system layer is too sparse.

## Sources and transferable findings

| Source | Finding | Ember Lattice application |
|---|---|---|
| [Clip Studio Paint manual — Balloon settings](https://help.clip-studio.com/en-us/manual_en/810_subtools/B.htm) | Balloon tools support line-only, fill-only, combined line/fill, and variable fill opacity. | Normal dialogue may use an 82–88% ivory fill; selected quiet panels may use line-only or no balloon with outlined text. Transparency is a controlled mode, not a universal effect. |
| [Blambot — Comic Book Grammar & Tradition](https://blambot.com/en-gb/pages/comic-book-grammar-tradition) | Tails should aim toward mouths; border-butted balloons save space; same-thought balloons may join; tangencies should be avoided; captions and off-panel speech have distinct grammar. | Use shorter tails, border-butted compact shapes when needed, linked balloons for longer thoughts, and deterministic tangent checks. Do not use thought bubbles for Elian's interior voice. |
| [Clip Studio official — Text tools](https://tips.clip-studio.com/en-us/articles/835) | Long copy needs frame wrapping and an explicit overflow check. | Copy fitting is measured from the final SVG frame; overflow is a hard failure. Line breaks are authored or deterministically balanced. |
| [Clip Studio webtoon lettering guide](https://tips.clip-studio.com/en-us/articles/10294) | Lettering should be placed before art is considered final, with roughly a letter-width of internal margin and tails that identify speakers. | Every panel plan declares a lettering exclusion before generation. The v2 compositor preserves at least 0.7 em around dialogue text. |
| [Clip Studio webtoon guide](https://tips.clip-studio.com/en-us/articles/7417) | Dialogue must be checked on mobile; typical balloon width is a minority of the canvas rather than a dominant block. | Normal balloons target 26–38% panel width, never more than 44% without a documented long-speech exception, and are reviewed at 390 px. |
| [Clip Studio webtoon paneling tips](https://tips.clip-studio.com/en-us/articles/9310) | Phone reading favors instant comprehension, rhythm, and contrast; balloon-only or simplified beats can create pacing. | Text-only overlays occur only on quiet, deliberately simplified art or gutters. System-only beats can provide rhythm without pretending a menu is dialogue. |

## Decision

Fully transparent balloons are not the default because moving art can reduce contrast unpredictably. The locked system has three dialogue modes:

1. **Soft balloon:** irregular compact ivory shape, 84% fill opacity, 4 px charcoal outline at 1024 px source width, short speaker-directed tail, and 0.7–1.0 em padding.
2. **Open dialogue:** no enclosure; ivory text with a 5–7 px charcoal paint-order outline and soft shadow, restricted to a verified low-detail exclusion with adequate luminance separation.
3. **Butted/linked balloon:** compact translucent shape cropped against a panel edge or joined to a second same-speaker unit, used for longer thought groups without spanning the focal action.

Brass Ledger menus remain separate: 76–86% charcoal fill, thin brass rules, compact rows, tabular hierarchy, and no dialogue tails. Menus may be narrower and taller than pilot UI so levels, XP, skill costs, cooldowns, prerequisites, inventory weight, and state deltas can appear together without decorative repetition.

## Copy contract

- Chapter dialogue target: 300–520 spoken/internal words, excluding system UI and SFX.
- Normal dialogue unit target: 10–28 words; documented maximum 42 words in a linked/butted sequence.
- A long sentence is split at a thought turn, not arbitrarily for shape.
- Each speaker retains a distinct register: Elian analytical/dry, Mira concrete/tactical, Orin clinical/wry, Sable compressed/deflective.
- Every chapter includes at least one exchange of three or more turns and at least one line that changes a decision rather than restating visible action.
- Each chapter includes four meaningful Brass Ledger moments. A repeated decorative status bar does not count.
- Phone checks fail if text falls below 15 CSS px equivalent, a unit clips, contrast falls below the local threshold, a tail creates ambiguous ownership, or lettering covers the declared focal region.

This decision supersedes the pilot's under-16-word balloon rule for Phase B. The pilot remains preserved as evidence; CH01 reuses its approved art with revised v2 lettering and expanded copy.
