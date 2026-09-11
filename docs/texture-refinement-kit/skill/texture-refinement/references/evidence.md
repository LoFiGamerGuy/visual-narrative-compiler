# Tested origin and limits

Source delivery: NR-20260908-01, commit 83b06de9812176c8614fc6d09a058f5ff12a912b. Built-in image generation, source-only edits. Model snapshot and seed were not exposed. Four controlled texture edits T01–T04 improved surface hierarchy; S05-R1 substantially simplified snow but made weather more stylized. These results support a preferred method, not guaranteed identity preservation or deterministic reproduction.

The owner explicitly endorsed the overall texture change on 2026-09-08 and asked for ongoing reuse. No per-image preference export was supplied with that endorsement. A04-R1 is a counterexample: surface relief did not fix incorrect shield mechanics. New-composition prompts alone continued to reintroduce texture.

Archived exact prompt hashes and source/return hashes:

## T01-P — City traversal
- before: `7f0cae1cbb3dff5e40c9bd7f5f3078861c7dd39d0ed9e87ce84d28650c1236cc`
- after: `b9c49074705d14ab571f374e904e57d0d73fd70892edf462f78215168b85c0ec`
- prompt: `2e4e23a179e5fa6e988b303505fcd5c4e4b5adfa00cc9820fd7e6a350a5ad883`

## T02-P — Giant encounter
- before: `b0d8c064fab38820ff0cba772618e4324008039cfcf5a978451bc68f52e1cedc`
- after: `2fcf3ace15e29385c38990ec9dfc040c6155d231030813c5337e3b1670c7b713`
- prompt: `1a10f5c0eb1a40366598d944ae93ccb406e48d563d38f27bb18ee457d654c572`

## T03-P — Character
- before: `6776b7769c246b0d476e18d60614b7fb199bc58c7eb8e9b0568112cfe1835234`
- after: `6be7239a1d5d44df7d7f2cb66dbe494d5935e04341babbdf97c4d1e08e99114b`
- prompt: `3f23a2cbd6e008e598371804391eec6ad458f42ba40d38cc036d8fca6a3539c0`

## T04-P — Creature
- before: `ac385674aa3296d03a12351a95ff66de6a2cc4069189bc568bf31006a2a2ada3`
- after: `98a640c4141125e405872d5d0801a645f84b484c3801dd99d999cb469129ebdc`
- prompt: `519f45a7ea4603599464026366461c4f9142f54faf3632bfd824c30c42643d27`

## S05-R1 — Snow shelter
- before: `b17ff7da2f93fe26547b8c5cbee24fc0a1f181a53b342fa46a736336d0d3bf91`
- after: `c9c663aadcb544715a4dadbed62395c5b12252cfe2d15f56b9ad0c0177c7bed9`
- prompt: `679d4361a6f34843eb25e7d8e702df7b17f3e554dbf96deba41f5bb11829b60c`

Exact tested prompts are included beside this file: T01-P.txt, T02-P.txt, T03-P.txt, T04-P.txt, S05-R1.txt. They contain historical subject and output-size constraints, not defaults for new source images. The portable guide includes the actual before/after images and unmodified call records. The master prompt is a newly written adaptation of those tested instructions.
