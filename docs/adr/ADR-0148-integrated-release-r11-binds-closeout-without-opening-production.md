# ADR-0148: Integrated release r11 binds closeout without opening production

Date: 2026-09-01

Status: Accepted

## Context

Release r10 predates the current safe-source capture, final reproducer, owner defaults, final hub/link inventory, and closeout bundle.

## Decision

Use final reproducer r2 as the compatibility path over immutable r10, then add eight current validators for source, decisions, review navigation, closeout, cost, frozen integrity, and tracked scope. Normalize only two live decimal tracked-path diagnostics.

## Evidence

- Nine/nine commands pass in 133.281 seconds, representing 66 + 8 = 74 effective checks.
- Independent replay passes and rejects 29/29 adversarial mutations.
- Effective state binds 29 candidates, 50 plans, 12 batches, 122 review resources, 67 direct links, ten defaults, 835 captured safe paths, and 73 zero-cost milestones.
- Frozen 16 plus baseline 4 remain exact and baseline remains 0/24 accepted with no tuning.
- Provider calls, uploads, downloads, paid spend, owner decisions, production prompts, acceptance, clearance, and executable panels remain zero; human review minutes remain null.

## Consequences

R11 is the final current engineering gate. Passing does not unlock ImageGen execution, ingest decisions, promote art, clear rights, select an exact base, or revise a ComicPanelPlan.
