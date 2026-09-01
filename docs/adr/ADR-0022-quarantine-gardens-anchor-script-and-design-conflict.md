# ADR-0022: quarantine the Garden's Anchor script/design conflict from current canon

Date: 2026-09-01  
Status: accepted

## Context

`garden-work/northgarden/pilot.md` is a locally present, substantial panel
script. Its opening calls the pilot 92 panels, while its chapter headings and
footer say CH01: 52 plus CH02: 44, or 96 panels. The individual panels are
numbered 01–52 and 01–44 respectively. This unresolved internal count
contradiction is itself a reason it is not ready for automated import. It is
still valuable evidence that chapter-scale narrative structure has been drafted.
It also conflicts with the current North Garden production records:

- the script calls its adult leads `DIO` and `THAL`; current records use
  `SOREN` and `SIGRID`;
- its accompanying historical art-status/design materials describe
  photo-derived appearance choices and earlier model/LoRA work;
- its story events, setting details, and visual bible have not been approved
  as the current production canon.

## Decision

Classify the entire `garden-work/northgarden/` collection as
`HISTORICAL_NARRATIVE_AND_DESIGN_EVIDENCE_NOT_IMPORTED`. Do not map names,
copy its images, carry its prompts, use its possible photo-derived references,
or create current Canon/StoryState/ComicPanelPlan records from it without an
owner-approved mapping and a separate adult-likeness provenance review.

Its script may be used only as an inventory/research reference: it establishes
that a 52-panel and a 44-panel structure are asserted, with an inconsistent
total, not that either is a current
North Garden chapter, a clean fictional design, or a permitted renderer input.

## Consequences

The current Soren/Sigrid CH03/CH04 drafts remain separate and do not become
chapters of the older pilot. The project has a real chapter-scale source to
review, but it cannot claim a chapter-scale *current production draft* yet.
The required owner decision is whether to (a) adopt/rewrite the pilot into
current canon with an explicit character/story mapping and a clean fictional
design basis, or (b) retain it solely as historical reference and author a new
chapter-scale current script.
