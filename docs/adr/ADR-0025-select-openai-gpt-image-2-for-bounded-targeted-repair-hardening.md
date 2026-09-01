# ADR-0025: select OpenAI GPT Image 2 for bounded targeted-repair hardening

- Status: accepted for research hardening; production acceptance pending
- Date: 2026-09-01

## Context

The four-provider fictional G07 bakeoff completed 16 required candidates under one aggregate ledger. All arms preserve the basic proxy roles in non-gating agent triage, so visual appeal alone cannot distinguish the production mechanism. Measured cost, latency, independent-repeat drift, target-change drift, no-change drift, structural side effects, provider data boundaries, and provenance must determine the next experiment.

## Decision

Use pinned `gpt-image-2-2026-04-21` as the mechanism for the smallest local, no-new-upload hardening experiment. First test a deterministic no-change short circuit and target-mask post-composite using the already-returned fictional-control evidence. Do not issue another provider call or upload CH05 material in this milestone.

The selection basis is 4/4 clean structural proxy cases, lowest required-arm cost ($0.198621), 10.78% target-change global drift, 51.42% no-change drift, and complete snapshot/request/usage provenance. Its 32.087-second mean latency is the worst observed and remains a throughput risk.

## Alternatives measured

- Gemini is fastest (11.759 seconds mean) and has the lowest target-change drift (9.38%), but its no-change output changes 99.59% of pixels.
- xAI has the lowest independent-repeat/no-change drift (34.62%/49.60%), but its target edit changes 63.19%, a central object appears in 3/4 candidates, and one extra paid attempt lost its hosted candidate.
- BFL returns exact credits but changes at least 99.78% in all three drift diagnostics and remains absolutely restricted to the two public fictional controls under ADR-0019.

## Consequences

- No output becomes accepted, final art, commercially cleared, or character-continuity evidence.
- Authorized human review remains pending with minutes null.
- Hardening is local and uses only existing generated evidence; a new external upload or CH05 provider request remains an authority gate.
- CH05 continues only through `ComicPanelPlan`; no `AnimationShotPlan` or E-Conte record is created.
