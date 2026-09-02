# ADR-0152: Owner-response validation does not ingest or expand authority

Date: 2026-09-01

Status: Accepted

## Context

The six pilot roots need exact values before prompt compilation. A broad reply or malformed local file must not silently set route values, deferred decisions, candidate acceptance, commercial rights, exact-base status, or plan revisions.

## Decision

Define a standalone null template and two-mode CLI validator. Template mode requires all response fields null. Response mode requires exactly six unique roots, one exact allowed value per root, a reviewer, and positive live review minutes. Always require deferred/promotion/plan/cross-medium fields null. Validation never ingests.

## Evidence

- The null template passes in template mode.
- Two complete synthetic response arms pass in response mode.
- Twenty/twenty malformed fixtures are rejected.
- Nineteen/nineteen evidence-state mutations are rejected.
- Owner decisions, review events, provider calls, uploads, spend, acceptance, clearance, and executable state remain zero/null.

## Consequences

Later review can produce an exact validated response without broadening authority. A separate hash-chained ingestion step remains required before any lifecycle transition or prompt compilation.
