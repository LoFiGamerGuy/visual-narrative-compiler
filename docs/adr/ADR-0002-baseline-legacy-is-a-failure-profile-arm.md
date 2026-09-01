# ADR-0002: baseline_legacy is a failure-profile arm, not a promotable renderer

Date: 2026-08-31  
Status: accepted

## Context

The first Stage-A run used the unchanged `garden/gen3.py` Anima graph and existing adult LoRAs. It completed all 24 frozen requests after two operational restarts and a prompt-compiler correction that was made before scoring the affected paired variant.

## Decision

Keep `baseline_legacy` as an archival, reproducible failure-profile arm. Do not tune it, promote it, or use it for further gauntlet stages. Its adapter-specific case bundle remains `DRAFT_LEGACY_LIMITED_NOT_FROZEN` because it lacks canonical stage/camera/control assets.

## Evidence

`experiments/results/baseline_legacy_stage_a_20260831.json` records zero fully assertion-conformant candidates out of 24. Recurrent failures include photographic regression, role/identity collapse, set discontinuity, interaction failure, and two extra-child outputs in G11a.

## Consequences

The existing calibrated plate-compositing workflow remains available for internal narrative production material, but neither it nor the full-frame legacy arm is commercial-ready until identity/base-model provenance completes review.
