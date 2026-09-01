# ADR-0033: selected-route preflight has no network executor

- Status: accepted
- Date: 2026-09-01

## Context

P036 is the smallest narrative repair target for the selected OpenAI mechanism, but it lacks approved base art, an approved mask, exact expanded upload authority, and a distinct production reservation. A preflight that imports a provider client or builds a request body too early could turn local readiness work into an accidental upload path.

## Decision

Keep `preflight_openai_p036_submission.py` metadata-only and offline. It may compile plan intent, exact hashes, scope, authority, and reservation identity after all gates pass, but it does not import a network/client module, read an API credential, build multipart/request bytes, or implement submission.

The current real record stops on four independent blockers and leaves the input-package hash and request envelope null. Synthetic fixtures can validate envelope metadata, but their state is explicit and no request body/executor exists. A future network executor is a separate architecture/authority milestone.

## Consequences

- Current P036 provider requests/uploads/cost remain 0/0/$0.
- Missing gates cannot be hidden by one aggregate `ready` flag.
- Adding network capability requires explicit review of data scope, budget, idempotency/recovery, and RenderRecord handling.
- G07 credentials and remaining bakeoff capacity cannot make this preflight executable.
