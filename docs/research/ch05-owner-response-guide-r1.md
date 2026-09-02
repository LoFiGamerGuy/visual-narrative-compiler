# CH05 owner response guide r1

Template: `production/comic/review/ch05-owner-response-template-r1.json`.

1. Copy the template to an untracked local response file.
2. Set state to `OWNER_RESPONSE_COMPLETE_NOT_INGESTED` and `valid_for_ingestion` to `true`.
3. For all six rows, choose one exact `allowed_values` entry, add reviewer, and record positive live review minutes.
4. Leave all four deferred decisions plus candidate/commercial/exact-base/plan/cross-medium fields null.
5. Validate with `python src/north_garden/validate_ch05_owner_response.py <response.json> --mode response`.

Validation never ingests the response; a later hash-chained ingestion step remains required.
