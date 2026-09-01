# ADR-0021: record absent detected VCS worktree as a provenance gap

Date: 2026-09-01  
Status: accepted

## Context

The workspace root is not a detected Git worktree (`git status` reports that
there is no repository). The research records can and do retain file hashes,
adapter/workflow hashes, and environment data, but they cannot currently name
a source revision or demonstrate that all source files came from one committed
state.

## Decision

Treat source-control revision as `UNAVAILABLE_NO_DETECTED_WORKTREE` in new
records when it would otherwise be required. Preserve hashes and exact paths as
the available evidence. Do not run `git init`, import history, or alter the
workspace layout autonomously: doing so would create a new repository history
whose intended ownership and remote policy are unknown.

## Consequences

The current artifacts remain reviewable but have a reproducibility limitation.
Before a production renderer is selected or a chapter-scale draft is called
reproducible, the project should establish an owner-approved VCS baseline and
record its initial commit in subsequent RenderRecords. This is a repository
governance decision, not a renderer result.
