# Production and research time/cost ledger

As of 2026-09-01, completed local experiments total **79 renderer generations** and **2,568.448 seconds (0.713 hours)** of measured renderer time. External API/service spend is **$0**. Local electricity/depreciation and timed human-review minutes remain unmeasured.

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

Before external execution, ADR-0023 validation measured exactly one successful and one denied competing $6 reservation against a $10 test cap; after a $1.25 reconciliation and a proven-unsubmitted release, available test capacity was $8.75. This used temporary test ledgers and no provider call. The real ledger remains committed $0, held $0, available $100. Officially documented ceilings allow at most $4.20 held for the complete 16-request bakeoff.

Historical accepted CH01 narrative material is intentionally excluded because its source-generation and human-review timings were not captured; it must not distort current throughput metrics.

The first external execution attempt ended before HTTP submission at TLS handshake validation. Its $0.50 reservation was released with explicit `not_submitted:tls_handshake_failed_before_http_submission` evidence: actual spend $0, elapsed 0.332 seconds, no request ID, no uploaded bytes, no output. This operational failure is not a renderer-quality result.
