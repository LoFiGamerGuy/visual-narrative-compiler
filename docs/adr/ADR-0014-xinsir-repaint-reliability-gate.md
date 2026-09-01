# ADR-0014: Target no-change is a reliability gate for native repaint

Date: 2026-09-01

## Context

The local Illustrious XL v2 plus source-verified Xinsir repaint route made one fictional teal-to-green edit at d1.0/strength 0.8, but its paired no-change control drifted. Low-denoise, lower-strength, and higher-strength matrices failed both edit and no-change. A paired replication at the original configuration failed the edit (teal remained teal) and drifted blue under no-change.

## Decision

Treat target-region no-change as a required reliability gate for any native repaint candidate. Exact exterior compositing remains a useful deterministic continuity mechanism, but it cannot compensate for target semantic instability. Do not optimize mask boundaries for this route until a differently bounded experiment establishes both target edit and target no-change behavior.

## Consequences

The current route is retained as a fictional, local research artifact with one-of-two observed edit success and zero-of-two no-change success. It is not eligible for a benchmark score, actor assets, production repair, or commercial claim. The next local goal should strengthen assertion/provenance foundations and prepare a genuinely different renderer mechanism for a future approved evaluation.
