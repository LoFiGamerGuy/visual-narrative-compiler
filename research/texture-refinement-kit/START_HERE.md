# Texture refinement — saved workflow and sharing kit

Open [the illustrated guide](../../docs/texture-refinement-kit/index.html), [all ten prompts](../../docs/texture-refinement-kit/PROMPTS.txt), or [the portable ZIP](../../docs/texture-refinement-kit-share.zip). Extract the ZIP before opening its index.html. It contains 49 files and is approximately 22.3 MB.

The owner's September 8, 2026 approval is preserved verbatim in the kit's `provenance/owner-feedback.json`. This records global approval of the texture process, without changing previous ratings or declaring cast/canon selections.

The durable project instruction is root `AGENTS.md`. Its reusable workflow is `docs/texture-refinement-kit/skill/texture-refinement/SKILL.md`, also installed byte-for-byte at `/home/gosnerp/.codex/skills/texture-refinement`. This gives future sessions a discoverable local skill as well as a versioned project rule. Isolated older branches retain their original instructions; the installed local skill provides continuity across them. Neither mechanism guarantees a generation will preserve every source detail.

The ten adapted prompts cover standard, gentle and strong passes; characters; places; creatures; equipment; effects; cover art; and recovery from over-smoothing. The guide distinguishes these newly written adaptations from the five exact tested prompts. Before/after images and call records are copied without transformation from completed NR-20260908-01. No new artwork was generated, no paid API was used, and direct paid spend for this documentation task was $0.

## Verification

- All ten native example images, five original prompts and five call records match their sources by SHA-256. The original sources remain unchanged.
- The ZIP passed integrity testing, extraction and verification of all manifest hashes; every local HTML link resolves in the extracted copy.
- The actual guide and extracted copy ran with browser networking disabled at 390×844, 1024×768 and 1440×1000. All ten images loaded uncropped; all ten textarea prompts match their TXT files. Copy handling and denied-clipboard/manual-copy fallback were exercised.
- Phone and desktop screenshots were visually reviewed. The phone snow pair shows both complete images and their labels together; the prompt card has readable text, copy action and TXT fallback.
- The installed skill passed the skill validator and matches the packaged version. No new image generation was used to test the ten adapted templates; their behavior on the wife's source images remains untested.

See `package-verification.json`, `browser-verification.json`, `source-baseline.json` and `screenshots/` for measured evidence. The initial screenshot capture was too early during smooth scrolling; the capture routine now disables smooth scrolling in its test page and the corrected captures were inspected.

## Retained limits

The surface redraw is a preferred finishing method, not a construction repair. Keep identity, anatomy, handling, depth and material checks separate. The snow example is markedly calmer but its weather becomes more stylized; the creature still retains some jaw and paving texture. Preserve exact cover typography in the original layout rather than relying on a generated redraw of lettering.

The completed artwork gallery and Black Petal cover kit remain in their protected original worktrees. This isolated documentation branch contains the complete guide and its examples, without copying all older galleries' ignored assets. It is not a replacement artwork delivery.

Branch: `docs/texture-refinement-kit-20260908`, based on `83b06de9812176c8614fc6d09a058f5ff12a912b`. Commit and push only this branch; do not merge or deploy. The share ZIP is locally available and gitignored; all files needed for this guide and its native examples are versioned, and `package_kit.py` rebuilds the ZIP in the current installed-skill environment.
