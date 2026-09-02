# ADR-0097: Full-denominator priority extends rather than rewrites release r1

- Status: accepted
- Date: 2026-09-01

## Context

Release r1 validated 16 overnight evidence/integrity commands before the 50-plan remaining-priority record existed. Rewriting r1 would erase that chronology.

Release r2 invokes the exact r1 reproducer and adds only the priority manifest and priority-evidence validators. Three orchestrator commands pass in 5.308 observed seconds, representing 18 effective checks. Thirteen/thirteen r2 mutations fail.

## Decision

Preserve release r1 byte-for-byte and issue append-only r2. Later milestones follow the same extension rule.

## Consequences

- Full 50-plan coverage now joins the release chain without changing prior results.
- Frozen/source integrity remains inherited through the reproduced r1 gate.
- Tier A remains review-only; passing r2 grants no generation or production authority.
