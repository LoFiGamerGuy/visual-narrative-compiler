# ADR-0048: boundary width is mask-scale-specific and the P044 control uses 5px

- Status: accepted
- Date: 2026-09-01

## Context

The fixed 16-pixel boundary collapses the P044 blade/twine fully replaced core. A smaller width can retain fine topology, but selecting an arbitrary narrow value would trade away smoothing without an explicit constraint.

## Decision

On the exact hash-pinned P044 support, compare 1, 2, 3, 4, 5, 6, 8, 10, 12, and 16 pixels. Select the widest width retaining one core/nonzero-alpha component, at least 15% union/blade/twine core, zero protected-hand and lettering overlap, and exact exterior.

Five pixels is the widest pass: 18.496% union core, 22.945% blade core, and 18.170% twine core. Six pixels is the first larger failure. Geometry is unchanged from the fixed stress.

## Consequences

- Boundary width must be evaluated against mask scale; P036's 16 pixels cannot be inherited by P044.
- Five pixels is a local abstract-control result, not a universal width formula or a P044 production policy.
- Visual seam quality remains unmeasured because no approved P044 base/candidate exists.
- Any reusable selector must keep topology retention and visual discontinuity as separate evidence dimensions.
