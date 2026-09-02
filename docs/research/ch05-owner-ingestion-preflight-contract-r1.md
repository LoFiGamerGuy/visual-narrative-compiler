# CH05 owner-ingestion preflight contract r1

This fail-closed command checks a future six-root response against its live timer log. It verifies root, decision, reviewer, and per-root minute parity and records exact hashes. It never performs ingestion or a lifecycle transition.

```powershell
python src/north_garden/preflight_ch05_owner_ingestion.py experiments/review-inputs/ch05-owner-pilot-root-response-r1.json experiments/review-inputs/ch05-pilot-root-review-events-r1.json
```

Exit 2 is the expected current result because both ignored local inputs are intentionally absent. Exit 0 means only that a separate future hash-chained ingestion milestone may be prepared.
