# ADR-0137: Integrated release r9 binds production hardening without transitioning state

Date: 2026-09-01

Status: Accepted

## Context

Nine post-r8 extensions now cover normalized reproduction, exact owner roots, prompt semantics, adversarial validation, deterministic packet preparation, lifecycle guards, chapter application, and current review access.

## Decision

Use r8 compatibility as the immutable 49-check base and add nine independent validators. Preserve historical raw-r8 failure evidence rather than calling the raw validator. Append all post-r25 work to zero-external-cost ledger r26.

## Evidence

- Ten/ten orchestrator commands pass in 83.926 observed seconds.
- 49 compatible base checks plus nine extensions equals 58 effective checks.
- Thirty/thirty release mutations are rejected.
- Effective state binds 29 candidates, 50 plans, 112 links, four draft prompts, five unbuilt pilot artifacts, 11 lifecycle states, and 12 chapter batches.
- Ledger r26 contains 64 zero-external-cost milestones and rejects 9/9 mutations.
- Provider, upload, render, review, acceptance, commercial, execution, and human-minute state remains zero/null.

## Consequences

R9 is the current integrated engineering gate. It validates production hardening but executes no lifecycle transition and grants no production or rights authority.
