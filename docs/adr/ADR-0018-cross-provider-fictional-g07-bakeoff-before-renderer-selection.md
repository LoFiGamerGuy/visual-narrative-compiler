# ADR-0018: execute a fictional cross-provider G07 bakeoff before renderer selection

Date: 2026-09-01  
Status: accepted

## Context

The immutable `baseline_legacy` Stage A and later local repair/production arms
established multiple failures: unreliable character/role binding, target
no-change drift, legacy asset leakage, and incorrect wardrobe/blocking. The
fresh `legacy_duo3` CH03 attempt added three rejected candidates and does not
justify more prompt tuning of that configuration. Local Qwen evaluation is
capacity-gated on a 24 GiB GPU.

The project must not select a long-term renderer based on one attractive
output. A provider-neutral, frozen-semantic G07 protocol already exists with
fictional adults and geometry controls that can be safely sent to a reviewed
API or managed-GPU adapter.

## Decision

Before selecting a production-oriented renderer, execute the unchanged
four-request G07 protocol for each available adapter: two independent
two-role renders, one target-change edit, and one paired no-change control.
Initial arms are Gemini 3.1 Flash Image, Grok Imagine Image 2.0, OpenAI GPT
Image 2, BFL FLUX.2 where current terms permit it, and Qwen-Image-Edit-2511
on approved sufficient compute.

Only original fictional adult design controls and original geometry controls
may leave the workspace in this round. Each arm must retain input/output
hashes, request/response identifiers, declared/pinned model version where
available, provider terms artifact, timing, cost, hard-assertion review,
human-review status/minutes, and acceptance/rejection decision. The draft
BenchmarkCaseBundle remains unfrozen; this is not a frozen Stage-A score.

## Consequences

No more same-route `legacy_duo3` or native-repaint tuning is planned. The
baseline remains immutable. API output nondeterminism is recorded as an
adapter property, not hidden behind a seed claim. Selection comes only after
the cross-arm failure profile and cost/time evidence are compared.

Configured credentials and an explicit spend cap are still operational
requirements; their absence does not authorize a substitute paid service or
model download.
