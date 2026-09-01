# ADR-0003: Sequential inpainting is a separate repair arm

## Status

Accepted for local-only experiment execution on 2026-08-31.

## Decision

Treat per-character sequential masked inpainting as a distinct renderer/repair adapter. It may consume a `ComicPanelPlan` and existing panel plate, but it does not alter `baseline_legacy`, benchmark semantics, canon, or any future animation-shot schema.

## Evidence and limits

The two-seed P07 mechanical smoke produced one two-adult result and one result in which the second pass omitted Sigrid and substantially changed set geometry. The fixed plate and rectangular masks are 2D legacy controls, not canonical spatial authority. Therefore this adapter is not yet a scoring benchmark arm and its bundle is not frozen.

## Consequences

Future use must record per-pass input/output hashes, workflow, model hashes, runtime, target/non-target change measurements, and review decision. It must add case-specific stage/camera/control assets before executing frozen Stage-A requests. No external reference upload, new model download, or commercial claim is authorized by this ADR.
