# ADR-0132: Prompt-blueprint validation is semantic and adversarial

Date: 2026-09-01

Status: Accepted

## Context

Compiler-time lint summaries can be self-consistent while missing semantic regressions. The four prompt drafts need an independent reusable validator before any later compiler can consume them.

## Decision

Validate exact plan/style/format/canvas/cast bindings, prompt hashes, adult and no-likeness language, character hair/wardrobe, dual-role order, causal geometry, quiet lettering regions, reference set/hash/authorization state, summary derivation, null production prompts, and non-executable state. Exercise in-memory malformed fixtures across those classes.

## Evidence

- The current four-row blueprint passes independent validation.
- An initial validator overconstraint requiring viewer-left language on a single-character panel failed and was narrowed; dual-character role order remains mandatory.
- Twenty-eight/twenty-eight malformed fixtures are rejected.
- Fixtures cover two age/likeness, five continuity/role, three causal/lettering, four reference-boundary, and 14 promotion/schema cases.
- Provider calls, uploads, renders, and cost remain zero.

## Consequences

Future blueprint revisions have a reusable fail-closed semantic gate. Passing still does not compile production prompts or authorize execution.
