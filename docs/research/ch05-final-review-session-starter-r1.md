# CH05 final review-session starter r1

Start here: [owner hub r7](C:/AgentWorkspaces/anime-pipeline/experiments/review-packets/ch05-owner-review-index-r7/index.html)
Priority art/results: [closeout r1](C:/AgentWorkspaces/anime-pipeline/docs/research/ch05-overnight-closeout-r1.md)
Exact six defaults: [owner defaults](C:/AgentWorkspaces/anime-pipeline/docs/research/ch05-owner-decision-defaults-r1.md)
Response guide: [owner response guide](C:/AgentWorkspaces/anime-pipeline/docs/research/ch05-owner-response-guide-r1.md)

## Minimum dependency order

1. `open_review_hub` — READY: Open the current local owner hub and use its nested prior hubs for art, sequence, continuity, lettering, capacity, and evidence review.
2. `review_priority_art` — OWNER_ACTION: Review the 14 strongest candidates, three generated sequences, cadence scrolls, continuity atlases, lettering comparisons, and non-canon concept sheet.
3. `review_six_defaults` — OWNER_ACTION: Review six exact pilot defaults separately from four deferred candidate/lettering/non-canon/rights choices.
4. `capture_live_root_time` — OWNER_ACTION: Create an ignored local six-root event log using only live timer events; do not backfill prior review.
5. `fill_response_copy` — OWNER_ACTION: Copy the null template to an ignored local response and fill exactly six roots, reviewer, and minutes from the valid live log.
6. `validate_local_inputs` — BLOCKED_FILES_ABSENT: Run the two exact validators.
7. `hash_chained_ingestion` — INTENTIONALLY_NOT_IMPLEMENTED: A future append-only compiler must bind the valid response and event-log hashes, then update decision state without rewriting the contracts.
8. `next_lifecycle_transition` — BLOCKED_INGESTION_ABSENT: Only after ingestion, transition DRAFT_BLUEPRINTED to OWNER_ROOTS_RESOLVED; production prompts remain a separate later transition.

## Important boundary

The six-root fast path can only make metadata prompt compilation eligible after a future hash-chained ingestion step. It does not accept candidates, clear rights, select an exact base, or replace the full 39-subject promotion review. The ingestion compiler is intentionally absent.
