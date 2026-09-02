# ADR-0118: Live-only human-review time instrumentation

Date: 2026-09-01

Status: Accepted as an empty instrumentation contract

## Context

Human-review minutes are currently null. Backfilling estimates from prior untimed review would fabricate measured labor, while chapter-scale production needs consistent candidate, sequence, lettering, and decision timing.

## Decision

Use an append-only `LIVE_TIMER_ONLY` event log with four transitions: started, paused, resumed, and completed. Pause/completion deltas must come from a monotonic live timer; a reviewer may have only one active subject; completion requires an allowed decision. Derive minutes from active deltas and never accept supplied/backfilled minutes.

## Evidence

- Contract binds all 39 exact owner-decision subjects, four event types, seven fields, and six rules.
- Three valid synthetic logs pass: empty, open-start, and start/pause/resume/complete.
- Twelve malformed logs fail, including backfill mode, unknown subject, duplicate ID, invalid transition/delta/decision/type/timestamp/chronology, concurrent reviewer session, and supplied minutes.
- Synthetic 20 active seconds derive to 0.333333 minutes.
- 16/16 evidence mutations are rejected.

## Consequences

- Prior reviews remain untimed; current human minutes stay null.
- Schema validation does not ingest an event or alter the owner decision contract.
- Future timed review can be measured without conflating wall-clock pauses with active work.
- Live events, decisions, acceptance, provider activity, and cost remain zero.
