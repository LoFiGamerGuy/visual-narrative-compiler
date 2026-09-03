# Complete-chapter ComicPanelPlan authoring contract r1

The next full chapter now has a reusable planning contract, but no story has been invented. The companion template is intentionally empty and cannot be mistaken for a production plan.

## What the contract carries forward from CH05

- Six required narrative phases from opening state through changed-state closure or cliffhanger.
- Eighteen required panel fields, including stable identity/revision, causal beat, cast, sequence, scale/density role, continuity carry-in/out, and lettering geometry.
- Three cadence classes and nine measured panel-scale roles.
- Measured 3-5-panel sequence guidance, with complete non-overlapping chapter coverage.
- Sequence-first generation only after plan, prompt, upload, and provider preflight; deterministic crops and panel-local repair afterward.
- Separate human acceptance, commercial-clearance, and exact-production-base gates.

## Progression support

Armor, weapons, upgraded clothing, monsters, classes, and system UI each have an explicit nullable contract field. A future chapter can introduce them deliberately through story/canon evidence; leaving a field null means the element is absent and cannot leak into prompts by assumption.

## Current state

- Contract: [complete-chapter authoring contract](C:/AgentWorkspaces/anime-pipeline/production/comic/contracts/complete-chapter-comicpanelplan-authoring-contract-r1.json), SHA-256 `e112fcd5d2b450746a6a6ad827ba6dff4ff77a0bf10c212f4718a334dc3e9d4e`.
- Blank template: [non-executable template](C:/AgentWorkspaces/anime-pipeline/production/comic/templates/complete-chapter-comicpanelplan-template-r1.json), SHA-256 `84852bd42384682977eb915d5fd3fca321b7ec979e712dae46dbaa603c11e264`.
- Validator: 15/15 malformed authority/schema/story/progression mutations rejected.
- Authored story beats, plans, prompts, calls, uploads, candidates, and acceptances: all zero.

ADR-0177 records why story authoring stays separate from render prompts.
