# ADR-0155: Owner-ingestion preflight proves parity but never transitions state

Date: 2026-09-01

Status: Accepted

## Context

A future six-root owner response must agree with a separate live timer log before any lifecycle transition can be considered. Running the two validators independently is insufficient because it does not prove root coverage, decision, reviewer, or per-root minute parity across the files.

## Decision

Add a fail-closed preflight that validates both contracts, checks six-root coverage and decision/reviewer/minute parity, verifies the lifecycle source remains `DRAFT_BLUEPRINTED` with zero enabled transitions, and reports exact response/log hashes. Use distinct exit codes for eligible, invalid, and absent inputs. Never write ingestion evidence or modify production state.

## Evidence

- The real workspace returns `BLOCKED_INPUTS_ABSENT`/exit 2 for two intentionally absent ignored inputs.
- Two/two identical valid synthetic replays match byte-for-byte at the result level.
- Twelve/twelve malformed cross-file cases are rejected.
- Nineteen/nineteen evidence state and denominator mutations are rejected.
- Live response/log/decisions/minutes/ingestion/transition remain 0/0/0/null/0/0.

## Consequences

Future review inputs can prove cross-file consistency before a separate append-only ingestion milestone is authored. A passing preflight is eligibility evidence only: it does not ingest decisions, advance lifecycle state, compile production prompts, authorize rendering, or grant acceptance, rights, or exact-base status.
