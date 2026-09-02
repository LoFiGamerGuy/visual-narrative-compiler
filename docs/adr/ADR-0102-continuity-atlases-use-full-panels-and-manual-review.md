# ADR-0102: Continuity atlases use full panels and manual review

- Status: accepted
- Date: 2026-09-01

## Context

Prompt lint cannot prove rendered hair, wardrobe, role staging, anatomy, or continuity. Automated face crops or identity similarity would also overstate the evidence and create an unnecessary biometric-style mechanism.

The 26 CH05 candidates span 14 plans, multiple styles, reference/text-only arms, aspect ratios, and scales. Reviewers need plan-grouped and sequence-ordered comparisons with exact existing engineering results.

## Decision

Build deterministic full-panel atlases: one groups all 26 candidates by the 14 ComicPanelPlans and one presents the selected 14 in narrative order. Attach a manual checklist for hair color/style, oatmeal coat, plaid wrap, literal role staging, mature anatomy, hands/story objects, and lettering clearance.

Do not crop faces, detect people, calculate identity similarity, infer biometrics, or convert existing engineering labels into owner acceptance.

## Consequences

- Existing labels are 17 all-pass, three warn, and six fail; hair/wardrobe is 26/26 pass and role order is 25 pass/one fail.
- Both atlases build byte-identically and 16/16 evidence mutations fail.
- A visual-QA pass corrected selected-atlas plan labels from sequence positions to actual P001/P002/P003/P009/.../P050 identifiers before release.
- Owner decisions, review minutes, provider calls, uploads, and cost remain 0/null/0/0/$0.
