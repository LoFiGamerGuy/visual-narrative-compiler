# ADR-0024: Git main is the safe-source provenance anchor

- Status: accepted; supersedes ADR-0021's temporary no-worktree condition
- Date: 2026-09-01

## Context

ADR-0021 correctly recorded that no Git worktree was detected at that time and prohibited silently inventing history. The repository is now initialized, `origin/main` is configured and pushed, and the user explicitly requires regular safe evidence commits.

## Decision

Use Git commit IDs on `main` as the source-provenance anchor for subsequent provider and hardening evidence. Continue to stage only explicit paths that pass `scripts/test-git-scope.ps1`. Never commit `.env`, credentials, private URLs, model weights, LoRAs, datasets, installed runtimes, private references, or unreviewed generated material.

## Consequences

ADR-0021 remains valid historical evidence of the earlier gap but is no longer the current repository state. RenderRecords may cite source commits after the applicable safe evidence commit exists. The broad untracked workspace remains user-owned and outside the default source scope.
