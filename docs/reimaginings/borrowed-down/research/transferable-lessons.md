# Transferable engineering lessons

This is a read-only audit of the protected North Garden baseline, not an adoption of its canon or appearance.

Retained mechanics:

1. Stable immutable panel IDs and chronological sequence grouping.
2. `ComicPanelPlan` as the sole visual planning structure; `AnimationShotPlan` and E-Conte remain null.
3. Story intent, render execution, candidate review, acceptance, and commercial clearance remain distinct states.
4. Generated source pixels stay text-free; lettering is deterministic and local.
5. Normalized safe zones are `[left, top, right, bottom]` rectangles.
6. Adjacent state-critical panels share a generation request where practical.
7. Exact hashes bind prompts, generated sheets, panel crops, and review artifacts.
8. A localized defect triggers a localized repair, never a broad chapter reroll.
9. Phone-size review is a first-class gate.
10. Provider fields unavailable from the built-in product remain `null`; no seed or reproducibility claim is invented.

Rejected controls:

- North Garden canon, characters, settings, wardrobe, progression, and palette.
- Its mature clear-line/painterly appearance.
- Any direct paid provider, local model, LoRA, dataset, or reference asset.
- Floating generic game UI.
- A single beauty score that hides continuity or causality failures.

Independent implementation:

The reimagining uses a compact Python/Pillow toolchain in `src/reimaginings/borrowed_down/`. No protected source file is edited or imported at runtime. General engineering ideas above are reimplemented with a new schema and new tests.
