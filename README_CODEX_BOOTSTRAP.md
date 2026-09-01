# Codex bootstrap bundle — placement instructions

Copy the CONTENTS of this archive into the root of the existing project repository.

Expected additions:

- `research/authoritative/north-garden-pipeline-brief.pdf`
- `research/authoritative/v2.1.1/...`
- `research/historical/master-research-architecture-brief.md`
- `AGENT_FIRST_PROMPT.md`

Do **not** replace or delete the existing project code, workflows, assets, models, or outputs.
The fresh Codex agent must inspect those in place.

## Authoritative research package

`research/authoritative/v2.1.1/` is the current package and supersedes v2.0 and v2.1.

Run after placement:

```powershell
python .\research\authoritative\v2.1.1\scripts\validate_research_package.py
```

Expected result: **0 failures, 0 warnings**.

## What is intentionally NOT in this archive

- obsolete `ngvnc_research_v2.zip`
- obsolete `ngvnc_research_v2_1.zip`
- intermediate review/audit prompts
- model checkpoints
- LoRA weight files
- raw reference photographs
- generated-output batches
- API keys / credentials / `.env`

Those large/private/local resources should stay where they already live. Codex should inventory
them by path/hash rather than duplicate them into Git.

## Starting Codex

Open a fresh local Codex session at the repository root and paste the contents of
`AGENT_FIRST_PROMPT.md` as the first message.

Do not give the agent the obsolete research archives as competing authorities.
