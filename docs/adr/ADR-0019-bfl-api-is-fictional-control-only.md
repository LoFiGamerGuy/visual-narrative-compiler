# ADR-0019: BFL FLUX API is fictional-control-only

Date: 2026-09-01  
Status: accepted

## Context

The project may compare BFL FLUX.2 against other image-editing mechanisms, but
adult likeness/reference material is local by default and requires an exact
provider review before any external use.

The current BFL FLUX API Service Terms, last revised 2026-08-04, grant BFL a
right to use developer Inputs and Outputs to operate and improve services and
to train and improve its AI models and related technology.

## Decision

BFL FLUX API may receive only original fictional geometry controls for the
controlled G07 renderer bakeoff. It must never receive adult likeness images,
adult-likeness LoRA output, real-person imagery, biometric data, child
imagery, or other sensitive material. Its pinned `flux-2-pro` endpoint remains
an experimental comparison, not a commercial production approval.

The BFL adapter additionally verifies that a configured external input URL
has exactly the frozen local fictional-control hash before it calls BFL.

## Consequences

BFL can contribute useful role/no-change/edit evidence but cannot become the
adult-reference production route under the current terms. Any future changed
terms require a new primary-source review and ADR before this boundary could
be reconsidered.
