# Production and research time/cost ledger

As of 2026-09-01, completed local experiments total **79 renderer generations** and **2,568.448 seconds (0.713 hours)** of measured renderer time. The controlled external bakeoff has **5 completed generations** and **139.353 seconds** of provider generation time, with **$0.265809** committed as documented usage-rate estimates. Local electricity/depreciation, invoice-level external confirmation, and timed human-review minutes remain unmeasured.

| Arm | Generations | Renderer time | Production accepted outputs |
| --- | ---: | ---: | ---: |
| `baseline_legacy` Stage A | 24 | 903.790 s | 0 |
| Sequential inpaint controls/smoke | 12 | 325.120 s | 0 |
| Controlled actor capture | 6 | 175.921 s | 0 |
| FLUX proxy/edit/no-change controls | 5 | 140.984 s | 0 |
| FLUX geometry/tile controls | 11 | 567.787 s | 0 |
| FLUX Blender-kitchen paired control | 2 | 102.026 s | 0 |
| FLUX Blender-kitchen no-change | 1 | 43.085 s | 0 |
| Illustrious XL v2 Blender-kitchen smoke | 3 | 40.391 s | 0 |
| Illustrious XL v2 masked proxy edit | 1 | 11.604 s | 0 |
| Illustrious XL v2 + Xinsir native repaint controls | 4 | 86.683 s | 0 |
| Illustrious XL v2 + Xinsir low-denoise matrix | 4 | 65.172 s | 0 |
| Illustrious XL v2 + Xinsir strength matrix | 4 | 64.807 s | 0 |
| Illustrious XL v2 + Xinsir d1.0/s0.8 replication | 2 | 41.078 s | 0 |

The complete sourced local ledger is `experiments/results/research-time-cost-ledger-20260901.json`. The live aggregate API ledger is `docs/research/evidence/g07-bakeoff-cost-ledger-r1.json`.

Before external execution, ADR-0023 validation measured exactly one successful and one denied competing $6 reservation against a $10 test cap; after a $1.25 reconciliation and a proven-unsubmitted release, available test capacity was $8.75. This used temporary test ledgers and no provider call. After OpenAI 4/4 and Gemini 1/4, the real ledger is committed $0.265809 by documented usage-rate calculation, held $0, available $99.734191. Officially documented ceilings allow at most $4.20 held for the complete 16-request bakeoff.

Historical accepted CH01 narrative material is intentionally excluded because its source-generation and human-review timings were not captured; it must not distort current throughput metrics.

The first external execution attempt ended before HTTP submission at TLS handshake validation. Its $0.50 reservation was released with explicit `not_submitted:tls_handshake_failed_before_http_submission` evidence: actual spend $0, elapsed 0.332 seconds, no request ID, no uploaded bytes, no output. This operational failure is not a renderer-quality result.

OpenAI's four completed requests total 128.347 seconds and a $0.198621 documented token-rate estimate. Gemini's first provider generation took 11.006 seconds and reconciles to $0.067188; an additional 0.856-second GET recovered its already-created interaction after a local response-parser failure. Formula provenance lives in each RenderRecord, and invoice-level variance remains a stated limitation.
