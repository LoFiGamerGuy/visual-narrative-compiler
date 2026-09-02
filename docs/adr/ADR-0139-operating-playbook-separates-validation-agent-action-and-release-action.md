# ADR-0139: Operating playbook separates validation, agent action, and release action

Date: 2026-09-01

Status: Accepted

## Context

Production evidence now defines gates and estimates, but operators need an exact ordered workflow that does not make blocked steps look runnable.

## Decision

Define 12 ordered steps with explicit pass and fail-closed criteria. Separate 11 reproducible shell validation commands, one agent-only OpenAI built-in ImageGen action, and two Git operator release actions. Mark the intentionally absent production-prompt promotion compiler rather than inventing it.

## Evidence

- Five steps are local-ready or dry-run-only, one requires exact owner action, and six production/review steps are blocked.
- Current lifecycle state is draft with zero enabled transitions.
- Data, source-control, diagnostic-repair, timing, RenderRecord, and rights boundaries are explicit.
- The readable playbook links the current hub, exhaustive links, and six-root checklist.
- Eighteen/eighteen mutations are rejected.

## Consequences

The project has a command-level handoff without implying that validation commands authorize the agent-only render step or that Git release actions are ordinary read-only checks.
