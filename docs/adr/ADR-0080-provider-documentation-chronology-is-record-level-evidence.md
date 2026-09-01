# ADR-0080: provider-documentation chronology is record-level evidence

- Status: accepted
- Date: 2026-09-01

## Context

The budget policy records that official model, endpoint, pricing, and terms evidence was retrieved before spend, but a closeout should not rely on prose chronology alone. Nineteen retained provider records expose exact start times and documentation URLs.

## Decision

Bind the dated primary-document record, budget policy, vault manifest, and all 19 exact provider-record hashes. Require every adapter documentation URL to occur in the primary record and every request start to follow the recorded retrieval time.

## Consequences

- Four provider sections contain model/endpoint, pricing, data/terms, and source evidence across 19 official links.
- All 19/19 provider records start after documentation retrieval; the lead is 490 seconds before the earliest attempt and 695 seconds before the earliest positive-cost request.
- Provider denominators remain OpenAI/Gemini/xAI 5 each and BFL 4; 16 completed candidates and $1.057377 paid remain unchanged.
- Sixteen/sixteen chronology/source/denominator/spend/activity mutations fail.
- Future CH05 execution still requires a fresh then-current primary review; this audit performs no web or provider activity.
