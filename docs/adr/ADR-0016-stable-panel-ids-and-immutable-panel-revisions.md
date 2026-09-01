# ADR-0016: stable panel IDs and immutable panel revisions

Date: 2026-09-01  
Status: accepted

## Context

The first linked CH01 archival records use identifiers such as
`ng-ch01-sc01-p006-r1` in the `panel_id` field. They successfully link the
historical source assets, but the suffix conflates a persistent panel identity
with a selected revision. That prevents a correction from remaining visibly
the same narrative panel and conflicts with the adopted rule that internal IDs
are independent from display ordering and revision.

## Decision

Preserve the original v1 plan and edition unchanged. New comic plans use a
stable `panel_id` (for example `ng-ch01-sc01-p006`) and a separate
`plan_revision_id`. Each accepted raster is described by an immutable
`PanelRevision` record with its own `panel_revision_id`, content hash, source
limitation, acceptance state, and provenance boundary. An edition selects
revision IDs, rather than making a filename or a plan ID the revision.

`ComicPanelPlan` continues to contain no animation-shot fields beyond the
explicit `animation_shot_plan: null` boundary. A new edition can migrate a
record structure without claiming that an archival source render has become
reproducible or commercially cleared.

## Consequences

Corrections create a new `PanelRevision` and a new edition selection while
leaving all previous edition and revision records immutable. Stable IDs can be
referenced by canon, lettering, QA, repair, and future animation-adjacent
asset records without making comic direction an animation-shot schema.
