# ADR-R002: Extend ComicPanelPlan for force-state continuity

Status: accepted

The isolated `BorrowedDownComicPanelPlan/1.0` extends the baseline concept with:

- `force_before`, `force_action`, and `force_after` for causal staging;
- `irreversible_state` for injuries, damage, debt, equipment, promises, and environmental changes;
- `density` and `panel_role` for cadence;
- `safe_zones` as `[left, top, right, bottom]`;
- `lettering` with review-only speaker metadata;
- `sequence_sheet` and crop coordinates for deterministic extraction.

`AnimationShotPlan` and E-Conte are explicitly null in every chapter manifest. The extension exists only under the `borrowed-down` namespace and does not modify shared schemas.

Thirty panels per chapter is selected: exactly six five-panel sequence sheets per chapter, 300 selected panels total. The lower edge of the suggested range is deliberate: five-panel sheets give consistent deterministic extraction, phone-readable silent beats, and feasible continuity review across a complete volume. Chronological breadth takes priority over redundant variants.
