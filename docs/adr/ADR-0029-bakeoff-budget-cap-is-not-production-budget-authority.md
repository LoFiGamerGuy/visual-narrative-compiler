# ADR-0029: bakeoff budget cap is not production budget authority

- Status: accepted
- Date: 2026-09-01

## Context

The authorized $100 cap applies to the four-provider fictional-control G07 bakeoff. After its $1.057377 spend, $98.942623 remains available in that ledger. CH05 narrative-panel inputs, purpose, review state, and external scope are materially different; treating unused bakeoff capacity as production authority would silently expand both spend and upload permission.

## Decision

Use a distinct `NORTH_GARDEN_CH05_PRODUCTION` budget domain, policy, environment variable, and aggregate ledger. The tracked CH05 policy is disabled, has no approved cap or adapters, and forbids reuse of the bakeoff ledger or environment variable. Production preflight also requires an exact input-package hash and separately reviewed provider/model/endpoint authority.

Production reservations are aggregate, locked, and reconciled. Submitted requests keep their full ceiling held until actual cost is committed. Only proven-unsubmitted reservations may be released; actual cost above the reserved ceiling becomes an incident instead of silently exceeding the cap.

## Consequences

- Current CH05 provider preflight fails before reservation or submission.
- Setting the bakeoff cap, or even setting a production environment value alone, grants no authority while the tracked policy is disabled.
- A future production request needs a distinct user-approved cap and exact upload scope.
- G07 committed spend remains $1.057377 and is not copied into the CH05 ledger.
