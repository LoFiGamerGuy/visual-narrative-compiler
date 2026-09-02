# ADR-0140: Delivery bundle r2 binds production hardening without promotion

Date: 2026-09-01

Status: Accepted

## Context

Delivery bundle r1 predates the current owner hub, exact-link inventory, pilot lifecycle, chapter lifecycle, duration capacity, operating playbook, release r9, and cost ledger r26. Rewriting r1 would destroy the historical handoff boundary.

## Decision

Create append-only delivery bundle r2. Bind the current artifacts and source hashes, preserve r1 through an exact `supersedes` link, and distinguish ranked engineering recommendations from owner acceptance, commercial clearance, and exact-base selection.

## Evidence

- The bundle reconciles 29 candidates, 50 ComicPanelPlans, 12 batches, 112 review links, 14 strongest candidates, ten route/rights decisions, six pilot roots, 58 integrated checks, and 12 operating steps.
- It carries the 49-candidate remaining-plan and 68-candidate fresh-arm capacity envelopes without calling them forecasts.
- Ten limitations explicitly cover unavailable service fields, reproducibility, sample imbalance, visual-review needs, rights, copy, human time, non-canon status, and local-link scope.
- Twenty-seven/twenty-seven adversarial mutations are rejected.
- Provider calls, uploads, paid spend, owner decisions, acceptance, clearance, executable panels, and ComicPanelPlan revisions remain zero; built-in cost and review minutes remain null.

## Consequences

The owner now has one current handoff surface with direct review links and exact measured denominators. The record does not unlock the four-panel pilot or promote any art.
