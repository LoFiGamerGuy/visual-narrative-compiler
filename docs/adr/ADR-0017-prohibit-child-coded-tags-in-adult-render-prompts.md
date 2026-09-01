# ADR-0017: prohibit child-coded tags in adult render prompts

Date: 2026-09-01  
Status: accepted

## Context

Historical local adult-only legacy renders embedded `1boy` and `1girl` tags
alongside explicit adult character descriptions. The selected CH02 raster
artifacts contain two adult fictional protagonists and no child image,
likeness, reference, or training data. Nevertheless, the tags are ambiguous
and incompatible with the project's child-safety boundary.

## Decision

All future adult render adapters and prompt compilers must use unambiguous
adult language (`adult man`, `adult woman`, or declared adult role IDs) and
must reject child-coded tags such as `boy`, `girl`, `child`, `kid`, and
equivalent age-ambiguous aliases unless a separately reviewed fictional-child
geometry-only protocol explicitly applies. No current adult workflow may use
the historical tags as a reusable prompt fragment.

## Consequences

The CH02 artifacts remain preserved as historical local-only evidence, with
their exact embedded graphs unchanged. They cannot become a clean production
prompt source. This does not claim that an ambiguous token is real child data;
it removes an avoidable ambiguity from all future runs.
