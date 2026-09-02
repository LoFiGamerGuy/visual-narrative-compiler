# ADR-0161: Candidate visual disposition does not equal acceptance

Date: 2026-09-01

Status: Accepted

## Context

The owner handoff identifies 14 strongest engineering candidates, but the existing dependency checklist provides only a coarse disposition field. Tomorrow's visual review needs explicit continuity, action, lettering, and phone-readability observations while keeping acceptance, rights, exact-base, route, and plan authority separate.

## Decision

Create a null 14-candidate worksheet with eight required checks per candidate and four visual-only dispositions. `REQUEST_ONE_TARGETED_REPAIR` requires exactly one bounded repair class; all other dispositions require no repair class. Keep shortlist rollup, route decision, candidate acceptance, commercial clearance, exact-base selection, ComicPanelPlan revision, and cross-medium fields null in both template and response modes.

## Evidence

- Fourteen exact candidate paths and hashes reconcile with the dependency checklist and link r6.
- 112 required checks cover role identity, hair style/color, wardrobe, causal action, hands, lettering clearance, phone readability, and style/density fit.
- One complete synthetic response passes; 14/14 malformed/authority-expanding responses fail.
- Sixteen/sixteen evidence mutations fail.
- The tracked template contains zero filled checks, dispositions, repairs, reviewers, minutes, acceptance, rights, or exact-base state.

## Consequences

Owner feedback can be specific enough to drive the smallest repair or next comparison without promoting any candidate. A separate later rollup and separate commercial/exact-base authority remain required.
