# ADR-0068: the authority frontier is a dependency graph, not a grant

- Status: accepted
- Date: 2026-09-01

## Context

Local hardening has produced substantial mechanics and governance evidence, while G07 human review and real CH05 production remain incomplete. A flat blocker list obscures which items are independent human/user authority roots and which are downstream evidence that can exist only after an authorized provider outcome.

## Decision

Compile a directed acyclic dependency graph over G07 review and selected-route P036 production readiness. Classify each node by its actual authority source. Keep the five root authority items explicit, leave `next_external_action` null, and preserve the prohibition on reusing remaining G07 capacity for CH05.

## Consequences

- The graph has 20 nodes and 20 edges and is acyclic.
- The root frontier is one G07 identified-human review session, two exact human-reviewed P036 inputs, exact user upload authority, and a distinct user-approved CH05 aggregate cap.
- G07 remains 0/20 review decisions; P036 remains four root preflight blockers and nine total finalization blockers.
- Current-primary terms/pricing/data-use refresh remains a prerequisite immediately before any future CH05 paid execution, not a permission to execute now.
- Eighteen/eighteen graph/authority/activity mutations fail. No request, upload, production cap, external spend, RenderRecord, or acceptance is created.
