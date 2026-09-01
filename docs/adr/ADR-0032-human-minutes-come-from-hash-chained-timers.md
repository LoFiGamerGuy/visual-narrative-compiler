# ADR-0032: human minutes come from hash-chained timers

- Status: accepted
- Date: 2026-09-01

## Context

Human minutes are a primary production metric but can be understated or backfilled if review records accept a manually entered duration. Pauses, multiple subjects, retries, and rejection decisions also need auditable timing and assertion linkage.

## Decision

Use `TimedHumanReviewSession` records with ordered SHA-256-chained START/PAUSE/RESUME/COMPLETE events. Active minutes are calculated from UTC intervals and never supplied as an input. Completion covers every hash-pinned subject exactly once and records hard-assertion outcomes plus failure tags for rejections.

Terminal `ComicPanelRunLedger` decisions reference the exact timed-session digest. Reviewer, subject, decision, and computed minutes must agree across both chains. Validation fixtures remain explicitly ineligible for real evidence and their minutes are reported separately.

Chapter progress always retains the 50-panel denominator. It reports submitted panels and attempts, retries, completed/failed/accepted/rejected attempts, accepted panels, real measured minutes, fixture minutes, and reconciled cost as separate fields.

## Consequences

- No real CH05 human minutes or acceptances currently exist.
- A session summary cannot be edited without invalidating its chain/derived calculation.
- Attempted-only success rates cannot replace accepted-per-planned.
- Synthetic transition tests may exercise calculations without entering real metrics.
