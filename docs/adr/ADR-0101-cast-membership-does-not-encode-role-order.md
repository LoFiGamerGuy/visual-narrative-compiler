# ADR-0101: Cast membership does not encode role order

- Status: accepted
- Date: 2026-09-01

## Context

All 50 CH05 ComicPanelPlans declare visible adult cast, but the cast array records membership. It does not say who leads, stands foreground, braces a plank, watches an exterior, or changes the target. Treating its stable `SOREN,SIGRID` order as staging would create silent role-order drift.

The 26 generated CH05 prompts already carry explicit Soren/Sigrid hair, wardrobe, adult, cast, and P036 composition-only text. These strings can be linted, but string presence cannot prove rendered identity or continuity.

## Decision

Compile exact role assertions for every plan from the continuity profile and treat narrative beat plus composition intent as the source for role-order translation. Require a literal prompt constraint whenever both adults are visible; never infer staging from cast-array order.

Keep P050/P040 as identity anchors and P036 as composition-only. Keep prompt lint and manual rendered-art review separate; perform no face detection, biometric comparison, or automated identity inference.

## Consequences

- The 50 plans partition into 18 no-person, eight Soren-only, seven Sigrid-only, and 17 dual-cast records.
- All 26 existing CH05 prompts pass exact adult/hair/wardrobe/cast/hash checks; all four P036-using prompts carry the composition-only guard.
- Sixteen/sixteen evidence mutations fail.
- The manifest creates no prompt, generation authority, upload, plan revision, acceptance, or future armor/weapon/monster canon.
