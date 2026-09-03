# Production and research time/cost ledger

As of 2026-09-01, completed local experiments total **79 renderer generations** and **2,568.448 seconds (0.713 hours)** of measured renderer time. The controlled external bakeoff has **16 completed candidates** plus **1 paid candidate-download failure**, with **308.894 seconds** of measured provider/attempt/recovery time and **$1.057377** committed. OpenAI/Gemini costs are documented-rate estimates; xAI/BFL reported exact values. Local electricity/depreciation, invoice-level confirmation for estimated arms, and timed human-review minutes remain unmeasured.

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

Before external execution, ADR-0023 validation measured exactly one successful and one denied competing $6 reservation against a $10 test cap; after a $1.25 reconciliation and a proven-unsubmitted release, available test capacity was $8.75. This used temporary test ledgers and no provider call. After all required candidates plus one paid xAI failure, the real ledger is committed $1.057377, held $0, available $98.942623. Officially documented ceilings allowed at most $4.20 held for the complete run.

Historical accepted CH01 narrative material is intentionally excluded because its source-generation and human-review timings were not captured; it must not distort current throughput metrics.

The first external execution attempt ended before HTTP submission at TLS handshake validation. Its $0.50 reservation was released with explicit `not_submitted:tls_handshake_failed_before_http_submission` evidence: actual spend $0, elapsed 0.332 seconds, no request ID, no uploaded bytes, no output. This operational failure is not a renderer-quality result.

OpenAI's four completed requests total 128.347 seconds and a $0.198621 documented token-rate estimate. Gemini's four provider generations total 46.173 seconds and $0.268756; an additional 0.863-second GET recovered its first already-created interaction after a local response-parser failure. xAI's four required direct-base64 candidates total 50.025 seconds and exact $0.28; its separate first 8.899-second request cost $0.07 but produced no candidate because the temporary hosted URL returned HTTP 403. Formula provenance and failures live in their RenderRecords, and invoice-level variance remains a stated limitation for estimated arms.

BFL's four candidates total 74.587 seconds and exact returned cost $0.24. The subsequent selected-route mask/no-change experiment used only local existing bytes, added no renderer generation and $0 external cost, and remains unaccepted.

The CH05 overnight built-in ImageGen run adds 20 candidates and 919.389 observed seconds. The built-in product exposed no cost or usage, so its monetary value is recorded as unavailable—not `$0`. No direct paid API, cloud GPU, purchase, BFL request, or G07-budget reuse occurred. Human minutes remain null and accepted candidates remain zero.

The CH05 cadence-hardening run adds six candidates and 310.669 observed seconds under the same built-in-only boundary. Combined new overnight/hardening generation is 26 candidates and 1,230.058 seconds. Monetary cost remains unavailable, no paid API was used, human minutes remain null, and accepted candidates remain zero.

The separately non-canon future LitRPG concept trio adds 154.978 exact candidate seconds. Total new built-in generation is 29 candidates, 39 reference uses, and 1,385.036 seconds. ADR-0109 records the 0.788-second correction from the earlier narrative totals without rewriting historical evidence. Monetary cost remains unavailable; no paid API, BFL, cloud GPU, purchase, or G07-budget reuse occurred.

The variable-cadence assembly and transparent-lettering rehearsal add no renderer generation and no external cost. They produce 13 and 25 ignored local review artifacts respectively from existing unaccepted pixels. Provider calls/uploads are zero; human minutes remain null; accepted panels, sequences, and lettering treatments remain zero.

The lettering width/copy sensitivity sweep adds 30 local layout cases and 31 ignored review artifacts with no renderer generation or external cost. Provider calls/uploads remain zero; human minutes and acceptance remain null/zero.

The outside-art lettering-band comparison adds two local 14-panel scroll alternatives, six band instances, and five ignored artifacts with no renderer generation or external cost. Provider calls/uploads remain zero; human minutes and acceptance remain null/zero.

The instrumented handoff compiler and owner index add no renderer generation or external cost. Fourteen exact rows and 42 ignored index/thumbnail artifacts compile with zero executable/accepted state. Provider calls/uploads remain zero; human minutes remain null.

The continuity/style/density analysis adds four ignored diagnostic sheets from 14 existing selected candidates and no renderer generation or external cost. Provider calls/uploads remain zero; human minutes and acceptance remain null/zero.

The overnight integrated release gate runs 16 no-network commands in 5.259 observed seconds with no renderer generation or external cost. Provider calls/uploads/downloads remain zero; accepted candidates/executable panels/human minutes remain 0/0/null.

The remaining-panel priority compiler adds one ignored coverage chart and an exact 50-row metadata partition with no renderer generation or external cost. Provider calls/uploads remain zero; new accepted/executable panels and human minutes remain 0/0/null.

The Tier A effort record adds no generation or external cost. Its 12/16/24 candidate counts and derived seconds are nonexecuted scenarios from 26 observed CH05 timings. Monetary cost and human minutes remain null; prompts/decisions/calls/uploads/acceptance remain zero.

The offline owner-decision worksheet adds no generation or external cost. It links 39 existing subjects and can export only a local uningested draft. Network calls/uploads/repository writes/recorded decisions remain zero and human minutes remain null.

The owner-decision draft validator adds no generation or external cost. It exercises 17 synthetic fixtures only; owner drafts read, events, decisions, contract writes, plan revisions, calls, and uploads remain zero. Human minutes remain null.

The character-assertion and prompt-lint compiler adds no generation or external cost. It binds 50 existing ComicPanelPlans and scans 26 existing prompts; prompts created, plans revised, identity inferences, calls, uploads, and acceptance remain zero.

The manual continuity atlas adds two ignored local comparison images from 26 existing candidates and no renderer generation or external cost. Face crops, identity inferences, owner decisions, calls, and uploads remain zero; human minutes remain null.

The panel-scale/cadence policy adds one ignored 50-row chart and tracked conditional metadata with no generation or external cost. Final copy, accepted layouts, ComicPanelPlan revisions, calls, and uploads remain zero; human minutes remain null.

The failure-class repair matrix adds one ignored diagnostic chart and no generation or external cost. Its four/six-candidate next-experiment envelopes are median-only, unexecuted scenarios; prompts/renders/uploads/plans/acceptances remain zero and future built-in monetary cost remains null.

The P010–P013 preflight adds one ignored text storyboard and tracked null-prompt metadata with no generation or external cost. Three reference hypotheses produce zero uploads; prompts/renders/executable rows/decisions/copy remain zero and human minutes remain null.

Owner review index r2 adds one ignored HTML page and five ignored thumbnails from existing local artifacts with no generation or external cost. Decisions, acceptances, calls, uploads, and publication remain zero; human minutes remain null.

Integrated release r3 adds no generation or external cost. Attempt 1 is preserved as a failed local validation; the successful 13-command/30-effective gate runs in 6.202 seconds. Calls/uploads/downloads/acceptances/executable panels remain zero and human minutes remain null.

The chapter-scale envelope adds no generation or external cost. Its 36/49/72 candidate counts and 1,844.172/2,510.123/3,688.344 median seconds are unexecuted generation-only scenarios. Money and human review remain null; prompts/renders/uploads/plans/acceptances remain zero.

The RenderRecord completeness audit adds no generation or external cost. It reconciles all 29 candidates to 1,385.036 observed seconds and 39 exact reference uses. Model, endpoint, request ID, provider usage, monetary cost, and seed remain explicit null in every record; all 29 candidates remain pending and unaccepted.

Integrated release r4 adds no generation or external cost. Its four local commands represent 33 effective checks and run in 6.934 seconds. Calls, uploads, downloads, accepted candidates, executable panels, and owner decisions remain zero; human minutes remain null.

Owner review index r3 and the 99-artifact link manifest add no generation or external cost. They compile ignored local HTML/thumbnails and tracked metadata only. Publication, calls, uploads, owner decisions, and acceptances remain zero; human minutes remain null.

The route recommendation, ComicStyleDirection r10, and ten-row decision matrix add no generation or external cost. Prompts, executable rows, plan revisions, owner decisions, acceptances, commercial clearance, calls, and uploads remain zero; human minutes remain null.

The P010–P013 production-manifest dry run adds no generation or external cost. Its four slots and five planned artifacts are metadata only; prompts, renders, executable rows, calls, uploads, accepted candidates, and plan revisions remain zero, while human minutes and provider cost remain null.

The P010–P013 review-contract dry run adds no generation or external cost. Forty-four check fields, five artifact slots, and all candidate/sequence review fields remain empty; pixels, decisions, repairs, calls, uploads, and acceptances remain zero, while human minutes remain null.

Integrated release r5 adds no generation or external cost. Its six commands represent 38 effective checks in 9.346 seconds. Calls, uploads, downloads, decisions, accepted candidates, and executable panels remain zero; human minutes remain null.

The 50-plan readiness matrix and local map add no generation or external cost. They join existing metadata only; next prompts, copy, acceptance, commercial clearance, executable rows, revisions, calls, and uploads remain zero, while human minutes remain null.

The reference-use/continuity-risk plan and local map add no generation or external cost. Its 42 reference uses are metadata hypotheses only; actual uploads, automated identity inferences, prompts, calls, acceptances, and execution remain zero, while human minutes and cost remain null.

The human-review timer contract adds no measured review time or external cost. Its fixtures are synthetic only; live events, completed subjects, decisions, acceptances, calls, and uploads remain zero, and actual human minutes remain null.

Final review hardening through release r12 is recorded by cost ledger r29 as 82 local zero-external-cost milestones. CH05 external requests/uploads/paid API-cloud spend remain 0/0/$0; built-in ImageGen service cost is still unavailable rather than treated as zero, and live human review minutes remain null.

Final integrated delivery through r13 is recorded by cost ledger r30 as 91 local zero-external-cost milestones. External requests/uploads/paid API-cloud spend remain 0/0/$0; built-in product monetary cost and live human review minutes remain unavailable/null rather than inferred.

The owner dependency checklist adds no measured review time or external cost. Its 24 tasks are read-only links; completed tasks, decisions, accepted candidates, calls, and uploads remain zero, while human minutes remain null.

Integrated release r6 adds no generation or external cost. Its five commands represent 42 effective checks in 9.946 seconds. Prompts, live review, decisions, acceptance, execution, calls, uploads, and downloads remain zero; minutes remain null.

The 12-sequence production-batch manifest and local map add no generation or external cost. Its 48 planned artifacts are names only; prompts, renders, acceptance, executable sequences, calls, and uploads remain zero, while minutes and cost remain null.

The 50-plan lettering-semantics matrix and map add no generation or external cost. Final copy, overlap permission, lettering acceptance, plan revisions, calls, and uploads remain zero, while human minutes and cost remain null.

Owner hub r4 and link manifest r2 add no generation or external cost. They build local HTML/thumbnails and tracked link metadata only; publication, decisions, acceptance, calls, and uploads remain zero, while human minutes remain null.

Integrated release r7 adds no generation or external cost. Its five commands represent 46 effective checks in 14.531 seconds. Prompts, review, decisions, acceptance, execution, calls, uploads, and downloads remain zero; minutes remain null.

Delivery-bundle r1 is appended as a zero-external-cost milestone in ledger r24. It makes zero provider requests/uploads and incurs $0 paid API/cloud cost; the CH05 production cap remains null and disabled. Built-in product cost is unavailable and is not entered as zero.

Safe-source delivery parity r1 makes zero provider requests/uploads/downloads and incurs $0 paid API/cloud cost. It inventories an already-pushed commit locally and does not retrieve or publish generated material.

Integrated release r8 adds no generation or external cost. Ledger r25 appends safe-source parity and release r8 as two local zero-external-cost milestones, bringing the chain to 54 while leaving the CH05 cap null and disabled.

Ledger r26 appends ten post-r8 compatibility, reproduction, pilot-hardening, chapter, owner-link, and release-r9 milestones. The chain now contains 64 zero-external-cost milestones with zero CH05 external requests/uploads and $0 paid API/cloud spend; built-in product cost remains unavailable.

## 2026-09-02 complete-chapter continuation

The current continuation adds 13 built-in ImageGen raster outputs: 11 base sequence strips, one P001 repair, and one P031-P033 repair strip. Deterministic crops yield 54 panel-level candidates, but the run remains 13 service/tool calls and must not be counted as 54 calls. Twenty-seven authorized reference uses resolve to exactly three unique hash-pinned fictional-adult files.

Approximate unique client-observed generation wall time is 1,025.7 seconds after avoiding double-counting parallel call pairs. Shared strip elapsed values must not be summed once per crop. Direct paid API/cloud spend remains `$0`; the built-in product's monetary cost is unavailable, not zero. Human review minutes remain `null`, and accepted/commercially cleared/exact-base candidates remain zero.

The P036 repair adds one 37.2-second client-observed built-in call, one raster output, one panel-level candidate, and three reference uses. Current totals are 14 outputs, 55 panel candidates, 30 uses across three hashes, and approximately 1,062.9 unique observed seconds. Direct paid API/cloud spend remains `$0`; built-in monetary cost and human minutes remain unavailable/null.

The P039/P043 repair adds one 88.0-second built-in call, one raster strip, two panel-level candidates, and two reference uses. Current totals are 15 outputs, 57 panel candidates, 32 reference uses across three hashes, and approximately 1,150.9 unique observed seconds. Direct paid API/cloud spend remains `$0`; built-in monetary cost and human minutes remain unavailable/null.

The P029/P032 final strip adds one 49.8-second built-in call, one raster, two panel candidates, and two reference uses. Current totals are 16 outputs, 59 panel candidates, 34 uses across three hashes, and approximately 1,200.7 unique observed seconds. P032's diagnostic status does not remove it from candidate accounting. Direct paid API/cloud spend remains `$0`; built-in monetary cost and human minutes remain unavailable/null.

The r6 release binder and 63-plan chapter inventory add no provider call, upload, generated pixel, or external cost. They reconcile the existing 16 executions as 1,592.908 summed per-execution observations versus approximately 1,200.7 seconds of overlap-adjusted wall time. Direct paid API/cloud spend remains `$0`; built-in monetary cost and human minutes remain unavailable/null, and accepted/commercially-cleared/exact-base counts remain zero.

The 23-panel cross-chapter regression packet adds two deterministic local derivatives from existing pixels and no renderer generation, provider call, upload, or external cost. It changes no historical or CH05 acceptance state. Human review minutes remain null.

The complete-chapter authoring contract/template adds no story beat, panel plan, prompt, renderer generation, provider call, upload, candidate, acceptance, or external cost. Its validation uses local metadata and synthetic mutations only; human minutes remain null.

The semantic graph validator adds one in-memory synthetic positive and 23 in-memory adversarial cases with no North Garden story, prompt, generation, provider call, upload, candidate, or external cost. Human minutes remain null.

Post-CH05 integrated release r1 runs ten local no-network commands in 4.481 seconds and adds no prompt, renderer generation, provider call, upload, candidate, acceptance, or external cost. Human minutes remain null.

The r6 owner start-here pointer adds no renderer generation, provider call, upload, candidate, acceptance, publication, or external cost. Human minutes remain null.

The complete alternate-graphic preflight creates 11 exact prompt records but makes zero executions/uploads/outputs and incurs zero direct paid API/cloud cost. Twenty-three reference uses are planned, not yet performed. Built-in future cost and human review minutes remain unavailable/null.
## 2026-09-02 alternate-graphic full-chapter execution

Eleven OpenAI built-in ImageGen tool calls produced 11 sequence rasters and 50 deterministic panel crops using 23 authorized reference uses across the same three exact hashes. Six timing batches total 954.3 seconds of overlap-adjusted tool-call wall; this includes any queue, generation, and transfer time visible to Codex and is not pure model inference. Only S01 has individual timing (91.5 seconds); paired-call times remain null.

Direct paid API/cloud calls, BFL calls, and paid API/cloud spend are 0/0/$0. Built-in product monetary cost, model, endpoint, request ID, usage, and seed remain unavailable, not zero. Cost ledger r31 preserves 91 prior local milestones, appends seven local instrumentation milestones, and separately records the 11 built-in calls so they are not mislabeled as local work or multiplied into 50 provider calls.

## 2026-09-02 clear-line-watercolor full-chapter execution

Eleven OpenAI built-in ImageGen tool calls produced 11 sequence rasters and 50 deterministic panel crops using 23 authorized reference uses. Six overlap-adjusted timing batches total 1,090.0 seconds. Only S01 has an individual duration (104.6 seconds); paired-request individual durations remain null rather than sharing or duplicating batch wall time.

Across the alternate-graphic and clear-line-watercolor complete-chapter arms, the continuation now totals 22 built-in outputs, 100 deterministic crops, 46 authorized reference uses, and 2,044.3 seconds of overlap-adjusted tool-call wall. Direct paid API/cloud calls, BFL calls, and direct paid API/cloud spend remain 0/0/$0. Built-in monetary cost, model, endpoint, request IDs, usage, and seeds remain unavailable. Human-review minutes, acceptance, commercial clearance, and exact-base status remain null/zero.

## 2026-09-02 premium-cel and targeted-repair continuation

Premium cel adds 11 built-in tool calls/outputs, 50 local crops, 23 authorized reference uses, six timing batches, and 1,234.0 seconds of overlap-adjusted tool-call wall. Across the three complete comparison arms, cumulative activity is 33 calls/outputs, 150 crops, 69 reference uses, 18 batches, and 3,278.3 seconds. Cost ledger r33 keeps crops separate from service-call/output counts.

The targeted repair trio adds three concurrently issued built-in calls/outputs, six reference uses, one timing batch, and 169.0 seconds of overlap-adjusted wall. Direct paid API/cloud and BFL activity remain 0/$0. Built-in monetary cost and service metadata remain unavailable; human review, acceptance, commercial clearance, and exact-base counts remain zero/pending.

## 2026-09-03 flat-gouache and reduced-palette controls

Flat graphic-gouache adds 11 built-in calls/outputs, 50 deterministic crops, and 23 authorized reference uses. Nine known individual walls total 1,063.921 seconds; one S10/S11 concurrent-pair wall is 227.068 seconds. Their 1,290.989-second sum is non-overlap observed arithmetic, not actual end-to-end elapsed time. Actual end-to-end wall is unavailable because parallel caller lanes lacked one shared stopwatch.

Reduced-palette text control adds 11 built-in calls/outputs and 50 deterministic crops with zero references and zero uploads. Six known individual walls total 568.300 seconds and two concurrent-batch walls total 459.352 seconds. Their 1,027.652-second sum is likewise non-overlap observed arithmetic; actual end-to-end elapsed time is unavailable.

Across the five new complete style/control arms—alternate graphic, clear-line watercolor, premium cel, flat graphic-gouache, and reduced-palette text control—the ledger records 55 built-in calls/outputs, 250 crops, and 92 reference uses across three unique authorized hashes. Timing scopes are incompatible and are not added into a synthetic combined total. Direct paid provider API calls and paid API/cloud spend remain 0/`$0`; built-in monetary cost, model, endpoint, request IDs, usage, and seed remain unavailable. Human review, acceptance, rights/commercial clearance, and exact-production-base counts remain zero/pending. The six-route comparison and cadence assembly are local derivatives with no additional provider activity or spend.

Cost ledger r35 appends eight local six-route/cadence milestones over r34 and binds nine exact current evidence sources. The chain now contains 117 local zero-external-cost milestones. This revision itself adds zero provider calls, uploads, generation calls, candidates, or paid spend; it preserves the existing built-in activity totals and unavailable service metadata without reclassifying them as zero. Human-review minutes remain null and acceptance, rights/commercial clearance, and exact-production-base counts remain zero.
