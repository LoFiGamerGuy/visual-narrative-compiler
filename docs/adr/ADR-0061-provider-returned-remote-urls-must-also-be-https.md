# ADR-0061: provider-returned remote URLs must also be HTTPS

- Status: accepted
- Date: 2026-09-01

## Context

All configured endpoints used native trust-store TLS verification, but Gemini image URIs and BFL polling/sample URLs come from provider responses. Passing those values directly to `urlopen` could accept a non-HTTPS scheme even though the configured API endpoint is HTTPS.

## Decision

Fail closed unless every provider-returned remote URL begins with `https://`, then continue using the native verified `SSL_CONTEXT`. Retain the existing BFL public-control URL/hash preflight and reject every insecure TLS override token.

## Consequences

- Four/four endpoints are HTTPS, every `urlopen` has the verified context, and Gemini/BFL returned URLs have explicit scheme guards.
- The observed provider-input universe is still exactly the two published fictional-control hashes.
- Child imagery/reference, real-person likeness, biometrics, adult-likeness LoRA output, sensitive personal data, and unapproved adult-likeness upload remain prohibited.
- Nine/nine endpoint, TLS, guard, input, data-boundary, authority, and activity mutations fail.
- The audit/hardening made no network request, upload, or spend.
