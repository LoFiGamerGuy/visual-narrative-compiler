# ADR-0043: local repair-mechanics policy cannot authorize production inputs

- Status: accepted
- Date: 2026-09-01

## Context

The selected route now has measured boundary and causal-shape mechanics. Encoding them in a reusable policy is useful, but a policy that cites proxy paths could accidentally make those controls look like approved panel inputs or self-authorize execution.

## Decision

Version the 16-pixel inward boundary, 8-pixel causal context, exact-exterior requirement, no-change short circuit, and evidence hashes in a local `ComicTargetedRepairPolicy`. Mark every abstract control categorically ineligible as a production base, production mask, or external upload.

Bind the policy into P036 offline preflight, but keep approved panel-specific base/mask, exact external upload authority, and a distinct CH05 production reservation as separate required gates. The policy contains no request body or executor. Validation-fixture mode may exercise metadata compilation; the same proxy raster outside fixture mode must fail.

## Consequences

- Measured mechanics can be reused without granting approval or authority.
- Real P036 preflight retains exactly four blockers and no request envelope.
- Proxy controls cannot self-promote even when wrapped in superficially approved fixture fields.
- Eleven/eleven input, policy, proxy, authority, reservation, and executor mutations fail.
- Production budget remains disabled and external execution remains unauthorized.
