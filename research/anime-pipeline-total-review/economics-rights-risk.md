# Production economics, rights and risk

Research/access date: **2026-09-06**. This report distinguishes sourced policy facts, unknown project facts and proposed planning estimates. It is not commercial clearance of any asset. Citation metadata is in [industry-citations.json](evidence/industry-citations.json).

**Decision implication:** a route is economical only if it repeatedly produces approved sequences within total correction capacity and the intended publisher can accept its provenance. Generation speed and a $0 incremental tool bill do not establish either condition.

## Economics: use accepted output as the denominator

**Sourced fact — IND-18.** WEBTOON's ORIGINALS FAQ says there is no single episode rate. Its $1,000/episode example explains a guarantee calculation; it is not a market rate card or an offer to this project. Although marked updated May 8, 2025, the body still anticipates 2023 features, so current payment practices cannot be inferred wholesale. [Official episode-fee explanation](https://webtoon.zendesk.com/hc/en-us/articles/9482697214996-ORIGINALS-Creators-Update-Increasing-transparency-and-improving-processes-at-WEBTOON)

**Sourced fact — IND-19 (2026-01-06).** WEBTOON's ad terms list Viewer Ads eligibility over 40,000 global monthly page views and over 1,000 subscribers; Reward Ads require Viewer Ads and over 100,000 monthly page views. Eligibility and approval do not guarantee revenue. These are admission conditions, not demand forecasts. [Current ad terms](https://www.webtoons.com/en/terms/adRevenueSharingPolicy)

**Sourced fact — IND-20 (date unknown).** Tapas describes approximately 70% of ad revenue going to creators. This is a share, not a guaranteed CPM, income or recovery of production expense. It does not override the platform's content restrictions. [Tapas ad documentation](https://help.tapas.io/hc/en-us/articles/360007703773-Ad-Revenue)

**Recommendation.** Assume pilot revenue $0. Preserve separate counters for machine runtime, wall-clock elapsed time, human creative labor, technical support, revisions and attributable incremental spend. A subscription already held may produce no additional charge while still having a cost and provider dependence. Do not relabel unknown historical costs as $0.

Proposed accounting:

```text
accepted_sequence_cost =
    recorded incremental cash
  + human hours × explicitly chosen internal planning rate
  + attributed local compute/energy/depreciation (only if measured or modeled)

route throughput =
    panels accepted in an approved sequence / total human hours for that sequence
```

Keep rates and unmeasured compute costs `null` until chosen or evidenced. Do not silently convert machine/agent execution time into human labor. Count rejected candidates and redraws. A 95% candidate acceptance metric can be misleading if the acceptance bar is weak; owner/independent sequence approval is the controlling denominator.

## A bounded capacity model for the next 14-panel pilot

These are **planning estimates**, not measured repository timings, quotations from contractors, industry averages or promises. They assume skilled practitioners, one original adult-cast scene, existing authorized tools, no training run, one primary candidate and at most one hard-failure retry, one editorial revision round, one correction pass, and no full chapter. The same frozen benchmark is used across routes.

| Work package | Estimated human effort | What changes the range |
|---|---:|---|
| Common brief, copy and evaluation freeze | 3–6 hours | Already-approved copy versus unresolved story beats |
| Shared thumbnails, action map and review | 6–12 hours | Choreography complexity and reviewer availability |
| Current-route candidate/selection/targeted correction | 8–20 hours | Whether existing contracts yield suitable acting and camera continuity |
| Modular-route asset/layout setup and final art | 18–42 hours | Reusable clean character assets; degree of manual redraw |
| Human-directed asset/layout/drawing and finishing route | 30–70 hours | Drawing speed, complexity, existing original assets and finishing standard |
| Per-route lettering/export/QA | 4–8 hours | Editable copy, collision repair, font and slicing behavior |
| Common blind comparisons and synthesis | 3–6 hours | Reviewers' availability and disagreement |

Shared work totals 12–24 hours. Route-specific totals are 12–28, 22–50 and 34–78 hours respectively. Thus a single pilot route including shared work is approximately **24–52 hours current**, **34–74 hours modular**, or **46–102 hours human-directed**. Running all three with shared preparation is approximately **80–180 hours**; do not triple the common work. A greenfield story adds an estimated 8–20 hours of concept/cast exploration before comparable asset production. None of these ranges includes hiring, learning a drawing discipline, external contract negotiation, a new GPU or model training.

The proposed budgets are ceilings to expose uncertainty, not permission to spend. **Incremental paid/cloud/asset-store budget for this assignment is $0.** This researcher incurred no paid purchases or paid generation calls. Whole-audit spend and historical project spend are the lead's ledger responsibility.

Human artist, editor, letterer, localization reviewer and independent reader availability are **unknown**. An AI agent cannot certify that a human artist or the owner approved a result. If skilled correction is unavailable within existing resources, deliver the frozen storyboard and test plan, record the route as unrun, and resolve staffing before a later commissioned pilot. Do not report AI self-review as human review.

## Separate five rights questions

| Question | Evidence required before production claim | Current assessment in this research |
|---|---|---|
| May this tool/model be used commercially? | Exact provider/model/license/version, applicable terms at generation date, account entitlement and restrictions | Unknown for repository assets unless the technical audit supplies it |
| May the reference, LoRA dataset, font, mesh or texture be used this way? | Source, copyright/license grant, modification/derivative permissions, seat/embedding/redistribution rules where relevant | Asset-specific; no blanket clearance |
| Is the resulting expression protectable? | Jurisdiction and evidence of human expressive contribution; assess actual output | No automatic protection inferred from prompting or metadata |
| Does the image infringe or misuse another right? | Asset/reference provenance and appropriate output review; relevant agreements | No automated similarity or hash test can certify clearance |
| Will the chosen platform accept this production route? | Current platform policy and actual publisher agreement for that territory | Tapas AI-generated prohibition verified; others bounded below |

These are operational review questions; the table does not make a legal conclusion about an individual output.

**Sourced legal position — IND-15 (2025-01-29).** The U.S. Copyright Office distinguishes human-authored expression and sufficiently creative arrangement/modification from purely AI-generated material. It assesses human contribution case by case and states prompts alone do not provide sufficient control under the technology analyzed. This does not mean an entire mixed work is necessarily unprotectable, nor does it establish freedom from infringement. This is the USCO's U.S. analysis, not a global ruling. [Copyrightability report, executive summary and sections II.D–F](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf)

**Sourced license distinction — IND-17 (date unknown).** Blambot permits specified free indie comic uses flattened into graphics, while webfont use and embedding have distinct licenses. The existence of a free font file does not permit every distribution method. No claim is made that the project's actual fonts satisfy these terms. [Blambot license categories](https://blambot.com/pages/licenses)

**Sourced provenance limitation — IND-16 (v2.2; date unknown).** C2PA describes verifiable provenance structures and explicitly avoids judging the underlying content as true/good. A signed history does not itself clear copyrights or make a panel original. [C2PA explainer](https://spec.c2pa.org/specifications/specifications/2.2/explainer/Explainer.html)

## Platform policy findings

**Tapas — verified restrictive policy (IND-11).** Its live Content and Community Guidelines say “AI generated content is not allowed on Tapas.” The policy generally covers app and web unless specified otherwise. The page displays “Last Modified: March 09th, 2022”; that label cannot establish when the AI sentence was added. Treat the live wording as the access-date policy. The text does not precisely define every assistive cleanup, hybrid or manually redrawn case. Its copyright rationale is platform wording, not a substitute for the more nuanced USCO analysis above. [Tapas policy](https://help.tapas.io/hc/en-us/articles/115005323707-Content-and-Community-Guidelines)

**WEBTOON CANVAS — bounded negative finding (IND-12/13/14).** The English Community Policy inspected here was posted November 25, 2025 with implementation January 6, 2026; CANVAS terms are dated January 6, 2026. In those checked documents, no standalone blanket AI-art permission, prohibition or specific AI-label rule was found. Their copyright and origin-misrepresentation obligations still matter. Absence of a found clause is **not** approval for this pipeline or proof that no other contract/program rule applies. [CANVAS terms](https://www.webtoons.com/en/terms/canvasTermsOfUsePolicy), [Community Policy](https://www.webtoons.com/en/terms/canvasPolicy), [effective-date notice](https://www.webtoons.com/en/notice/detail?noticeNo=3547)

**AI translation is a different policy surface (IND-22).** WEBTOON's March 26, 2026 localized FAQ announced optional AI translation, terminology setup and phased beta availability. It does not provide a general AI-illustration clearance. Actual account availability and eventual translated-output review remain unverified. [Official FAQ](https://webtooncanvas.zendesk.com/hc/zh-tw/articles/47592439172884-WEBTOON-Entertainment-%E5%AE%A3%E5%B8%83%E6%95%B4%E5%90%88%E5%85%A8%E7%90%83-CANVAS-%E5%B9%B3%E5%8F%B0-%E5%8A%A9%E5%8A%9B%E5%89%B5%E4%BD%9C%E8%80%85%E6%8B%93%E5%B1%95%E8%AE%80%E8%80%85%E4%B8%A6%E6%8F%90%E5%8D%87%E6%94%B6%E7%9B%8A-%E5%92%8C-FAQ)

**Kakao, Manta, Tappytoon and other licensed distribution.** General acceptance of this project's generation routes is `null`; no verified public policy or individual publishing agreement establishes it. Do not infer permission from a platform carrying licensed, conventionally produced comparables.

**Recommendation.** Preserve truthful process descriptions. Before a later distribution decision, determine the exact destination, asset origins and publisher requirements. This audit does not upload or publish any source art. A neutral benchmark remains commercially uncleared and owner-review-pending until separate decisions actually occur.

## Reproducibility and dependency risks

The following are **risk hypotheses and proposed controls**, to reconcile with the technical audit:

| Risk | Why it matters to a serial | Minimal proof/control |
|---|---|---|
| Provider/model unspecified | A successful panel cannot define a repeatable production recipe | Preserve known request/response/artifact hashes; provider, model, version, seed and revision fields remain `null` unless recorded |
| Provider changes or access loss | Cost and visual behavior may change between episodes | Run one repeated frozen scene after a version change; retain editable masters and export independence |
| LoRA or reference provenance incomplete | Tool functionality does not establish permitted training/use | Record dataset/license evidence without uploading private material; uncleared assets cannot become a cleared production base |
| Fused source image | Small editorial changes may require wide redraw/regeneration | Time a face/weapon/copy correction and inspect collateral changes |
| Generic visual resemblance | Audience trust and project distinction may suffer | Blind original-character recognition and preference review; this research measures no population-level reputational penalty |
| High setup cost mistaken for throughput | Automation investment may never amortize | Compare setup+correction costs over actual accepted sequences; stop after failed budgeted pilot |
| Analytics collection changes | Before/after engagement differences may reflect instrumentation | Record source, dates and definitions; never infer art improvement solely from dashboard totals |

The last risk has a current primary example: WEBTOON's April 21, 2026 dashboard FAQ says page-view collection changed at that update. That notice does not validate any local quality metric. [Dashboard measurement note](https://webtooncanvas.zendesk.com/hc/en-us/articles/48452348349332)

## What would change the production decision

A cheap route wins only if the owner and independent reviewers prefer its **complete sequence**, its repair work fits the declared capacity, and the desired distribution remains feasible. A human-directed route loses its practical advantage if no capable practitioner is available or its correction hours exceed the agreed ceiling. A greenfield restart loses its economic rationale if the same visual bottleneck persists under a new title.

A failed pilot is useful when it distinguishes these causes. Preserve attempt count, all failures, edits, hours, tool fields, source licenses and reviewer identity/type. Retain nulls and dissent. Do not purchase scale before the actual bottleneck and the publishing route are known.

