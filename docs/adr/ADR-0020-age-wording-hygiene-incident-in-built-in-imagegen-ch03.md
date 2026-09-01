# ADR-0020: record age-wording hygiene incident in built-in ImageGen CH03

Date: 2026-09-01  
Status: accepted

## Context

The three new CH03 built-in image-generation prompts described only fictional
adults and supplied no child image, likeness, reference, or training data.
They nevertheless used a generic negative age-category word while excluding
unwanted extra subjects.

## Decision

This is not child data and does not change the allowed-safety classification
of the generated candidates. It is recorded because ADR-0017 prohibits
child-coded/age-ambiguous wording in future adult prompts. The immutable
execution records preserve the incident; future built-in frontier-art prompts
must say `exactly two adult humans; no extra people` without age-category
negative wording.

## Consequences

CH03 is reviewable research evidence but not a reusable clean-prompt template.
No existing raster or provenance object is altered. The next prompt compiler
must mechanically reject the prohibited terms before generation.
