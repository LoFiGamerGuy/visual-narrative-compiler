# ADR-0087: P036 is a single-plank reach and brace, not a lever

- Status: accepted
- Date: 2026-09-01

## Context

P036 says Soren reaches the tin with a fallen plank while Sigrid braces it. Earlier direction and prompts called the action a lever. c011 left the object chain incomplete, while h005's explicit lever/fulcrum language produced two converging plank segments despite a single-plank request. The smallest correction removed lever, fulcrum, hinge, and V-shape semantics and described one rigid straight reach pole.

## Decision

Interpret P036 literally as one straight fallen plank used to reach the elevated tin. Sigrid braces the lower end and Soren controls the middle/upper reach. Require one unbroken floor-to-tin line and reject any second plank, bend, hinge, fork, fulcrum, or V shape.

h006 is the engineering reference for this causal interpretation. It is not an accepted production base.

## Consequences

- Causal prompt language becomes plan-literal and mechanically minimal.
- h005 is retained as evidence that extra mechanism vocabulary can create extra geometry.
- The general repair rule is to remove unsupported mechanism nouns before adding style or atmosphere.
- No ComicPanelPlan semantics, frozen gauntlet, baseline, provider, upload boundary, budget, or commercial status changes.
