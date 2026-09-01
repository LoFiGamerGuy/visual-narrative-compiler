# Provider bakeoff readiness — 2026-09-01

## Safe configuration check

The local configuration check confirms that credentials are present for OpenAI, Gemini, xAI, and BFL. It deliberately did not print, transmit, or store any credential values.

The fictional-control G07 adapters and frozen input hashes validate. OpenAI has completed 4/4 requests and Gemini 1/4; the aggregate documented-rate estimate is $0.265809, with $0 held and $99.734191 available.

## Remaining mechanical gates

1. **Closed:** `NORTH_GARDEN_APPROVED_BAKEOFF_CAP_USD=100` is authorized and configured.
2. **Closed:** BFL's two public static HTTPS control URLs are configured for the two published fictional controls; byte hashes remain mandatory preflight checks.
3. **Closed:** ADR-0023 and `bakeoff_budget.py` now enforce a single atomic aggregate reservation ledger across all four adapters. Concurrency validation proves competing reservations cannot each consume the cap.
4. **Closed:** current primary pricing, model/endpoint, data-use, and terms evidence is recorded in `provider-primary-documentation-20260901.md`. Documented ceilings reserve at most $4.20 for all 16 requests against the $100 aggregate cap.

## Current execution gate

Run each adapter's credential, data-boundary, source-hash, documented endpoint, and aggregate-ledger preflight immediately before its four requests. Preserve any provider rejection as a failure RenderRecord and retain possibly billable reservations until reconciled.

The first OpenAI attempt exposed a local TLS-chain compatibility issue before HTTP submission. Its reservation is released and cost reconciled to $0. The three standard-library adapters now use the OS-native trust store with certificate and hostname verification preserved; live preflight and the OpenAI retry passed. Gemini's first response exposed a local REST-schema parser mismatch after provider completion; official interaction retrieval recovered the output without repeat generation, and the repaired parser now has deterministic fixture coverage.

## Recommended execution order after the gates close

1. Run OpenAI, Gemini, and xAI first, using the exact four-request fictional proxy protocol.
2. Build their immutable review packets and compare role order, count/blocking, requested target change, and paired no-change behavior before moving to narrative art.
3. Run BFL only if its explicit fictional-control-only boundary and public-control URL process remain acceptable.

No adult likeness, real-person reference, child reference, character LoRA, or sensitive asset is in this external bakeoff protocol.
