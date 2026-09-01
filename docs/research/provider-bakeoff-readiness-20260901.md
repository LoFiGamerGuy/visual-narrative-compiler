# Provider bakeoff readiness — 2026-09-01

## Safe configuration check

The local configuration check confirms that credentials are present for OpenAI, Gemini, xAI, and BFL. It deliberately did not print, transmit, or store any credential values.

The fictional-control G07 adapters, their frozen input hashes, and their no-network/no-write preflights all validate. No API request has been made and external spend remains $0.

## Remaining mechanical gates

1. `NORTH_GARDEN_APPROVED_BAKEOFF_CAP_USD` is not currently a plain numeric value in the supported range `0` through `20`. Set it to a number only, for example `15` or `20`; omit `$`, prose, comments, and URL/code snippets on that line.
2. BFL's two control fields are not currently HTTPS URLs. BFL's image-edit endpoint requires two public, static HTTPS URLs whose downloaded bytes exactly equal the corresponding hash-pinned fictional control PNG. A code snippet is not an input URL. Leave BFL out of the first run, or provide both URLs after choosing a publication method for the two non-sensitive proxy images.
3. A per-adapter cap is not yet a cross-provider aggregate-spend control. Before executing multiple providers, add a single bakeoff-level reservation/ledger gate so four independently invoked adapters cannot each interpret the same `$20` as their own allowance.

## Recommended execution order after the gates close

1. Run OpenAI, Gemini, and xAI first, using the exact four-request fictional proxy protocol.
2. Build their immutable review packets and compare role order, count/blocking, requested target change, and paired no-change behavior before moving to narrative art.
3. Run BFL only if its explicit fictional-control-only boundary and public-control URL process remain acceptable.

No adult likeness, real-person reference, child reference, character LoRA, or sensitive asset is in this external bakeoff protocol.
