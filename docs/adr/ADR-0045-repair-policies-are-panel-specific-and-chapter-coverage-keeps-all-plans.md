# ADR-0045: repair policies are panel-specific and chapter coverage keeps all plans

- Status: accepted
- Date: 2026-09-01

## Context

P036 has a measured local mechanics policy, while CH05 contains 50 approved ComicPanelPlans. Treating P036's policy as generally applicable would hide panel-specific topology and authority requirements; reporting only repair candidates would hide the chapter denominator.

## Decision

Compile all 50 panels into chapter repair-policy coverage. Identify an explicit causal-repair candidate only when the plan declares both `practical_action` and the exact causal hand/object direction note. Bind a policy only by exact panel/revision; never inherit P036's policy.

Record panels without explicit plan-level applicability rather than omitting them. Do not infer masks. Motion mode may identify a future local-policy question but cannot select a policy target or make a panel executable.

## Consequences

- Four panels are explicit causal candidates: P019, P026, P036, and P044.
- Only P036 has a panel-specific local mechanics policy; three candidates remain policy-absent.
- Forty-six panels remain in the denominator with no explicit targeted-repair applicability.
- Approved bases/masks, executable panels, requests, uploads, human minutes, and accepted panels remain 0/0/0/0/0/null/0.
- Ten/ten denominator, order, policy-leak, execution, input, selection, and medium mutations fail.
