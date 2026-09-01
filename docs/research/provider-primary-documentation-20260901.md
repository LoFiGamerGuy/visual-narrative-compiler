# G07 provider primary-documentation record

Retrieved 2026-09-01 before any paid bakeoff execution. All links are official provider sources. The HTML hashes below are SHA-256 over the UTF-8 response body retrieved locally with normal TLS verification. Some legal pages rejected the local non-browser client; those pages were opened and reviewed through the web retrieval path and are marked `web-reviewed, unhashed` rather than assigned a fabricated hash.

This record establishes model/endpoint and budget preflight evidence only. It does not approve a renderer, accept output, expand an upload boundary, or decide commercial-release eligibility.

## OpenAI GPT Image 2

- Model: `gpt-image-2-2026-04-21`; official model page lists the snapshot and image-edit endpoint. The bakeoff uses `POST /v1/images/edits` with one hash-pinned fictional geometry control.
- Output request: `1536x1024`, medium, PNG. Official output estimate is $0.041 at this size/quality, plus text and high-fidelity image-input tokens. The reservation ceiling is conservatively $0.50 per request.
- Data/terms: official OpenAI business/API guidance says API inputs and outputs are not used for training by default unless the organization opts in. Service terms and usage policies still apply; this experiment contains no personal data or likeness.
- Sources: [model](https://developers.openai.com/api/docs/models/gpt-image-2) (`c4352be4…6bd30f`), [image guide](https://developers.openai.com/api/docs/guides/image-generation) (`2a72f320…8847d8`), [pricing](https://developers.openai.com/api/docs/pricing) (`43689b65…dadf9`), [data use](https://openai.com/policies/how-your-data-is-used-to-improve-model-performance/) (web-reviewed, unhashed), [service terms](https://openai.com/policies/service-terms/) (web-reviewed, unhashed).

## Google Gemini 3.1 Flash Image

- Model: stable `gemini-3.1-flash-image`; official image-edit examples use `POST https://generativelanguage.googleapis.com/v1beta/interactions` with base64 image input and `response_format` image controls.
- Output request: 1K, 3:2. Official standard paid output price is $0.067 for a 1K image, plus $0.50/M input text/image tokens and possible text/thinking output. No grounding tool is enabled. The reservation ceiling is $0.20 per request.
- Data/terms: the paid-service terms say Google does not use paid-service prompts/files/responses to improve products. The adapter must use the billing-associated paid API project represented by the configured credential; this does not authorize AI Studio or unpaid-quota handling of sensitive material.
- Sources: [model](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-image) (`d105a6a9…1ca699`), [image guide](https://ai.google.dev/gemini-api/docs/image-generation) (`d764d716…acf0db3`), [pricing](https://ai.google.dev/gemini-api/docs/pricing) (`35267a75…558347d`), [additional terms](https://ai.google.dev/gemini-api/terms) (`7733b2ab…65660f`).

## SpaceXAI Grok Imagine Image 2.0

- Model/endpoint: `grok-imagine-image-2.0` at `POST /v1/images/edits`. The endpoint accepts a base64 data URI. The adapter pins 1K and medium quality because the 2026-08-28 release changed omitted quality to `auto`.
- Price: image edit at 1K medium is $0.01 per input image plus $0.06 output. The response's `usage.cost_in_usd_ticks` is exact billed cost, with 10^10 ticks per USD. The reservation ceiling is $0.10 per request; returned ticks are reconciled automatically.
- Output transport: official image-generation guidance supports `response_format: b64_json` for direct bytes and states that default hosted URLs are temporary. The adapter uses base64 after an immediate hosted-URL retrieval returned HTTP 403 on the first paid attempt.
- Data/terms: official API security guidance says API inputs/outputs are not trained on without explicit permission and default API retention is 30 days. The current enterprise terms govern API use and assign output to the customer; no sensitive input is in this bakeoff.
- Sources: [model](https://docs.x.ai/developers/models/grok-imagine-image-2.0) (`94712e95…f954bb`), [editing](https://docs.x.ai/developers/model-capabilities/images/editing) (`bf24322e…c83718`), [pricing](https://docs.x.ai/developers/pricing) (`9d554f5f…d6a9b9`), [release notes](https://docs.x.ai/developers/release-notes) (`eddb49ca…bc955`), [security](https://docs.x.ai/developers/faq/security) (`8e6ca72a…16bf`), [enterprise terms](https://x.ai/legal/terms-of-service-enterprise) (web-reviewed, unhashed).

## Black Forest Labs FLUX.2 Pro

- Model/endpoint: pinned `flux-2-pro`; the official guide distinguishes the pinned endpoint from `flux-2-pro-preview`. It accepts a public input-image URL and returns an asynchronous request ID/polling URL. Each configured URL is downloaded and byte-hash checked before submission.
- Output request: 1536x1024 image edit. Official FLUX.2 Pro editing pricing begins at $0.045 and scales with megapixels. A $0.25 per-request reservation ceiling covers this fixed 1.573 MP request conservatively pending exact returned/billed credits.
- Data/terms: API terms revised 2026-08-04 grant BFL a license to use inputs/outputs for improving services and training. ADR-0019 therefore remains unchanged: only the two published hash-pinned fictional geometry controls may be sent. No likeness, personal data, LoRA output, character reference, or child-related material is permitted.
- Sources: [overview](https://docs.bfl.ai/flux_2/flux2_overview) (`28e80285…e19d58`), [editing](https://docs.bfl.ai/flux_2/flux2_image_editing) (`54891db6…41abb1`), [pricing](https://docs.bfl.ai/quick_start/pricing) (`993ca0de…d0eb3`), [API terms](https://bfl.ai/legal/flux-api-service-terms) (`9e80e714…a466`).

## Aggregate reservation result

| Adapter | Requests | Ceiling/request | Maximum held |
| --- | ---: | ---: | ---: |
| OpenAI GPT Image 2 | 4 | $0.50 | $2.00 |
| Gemini 3.1 Flash Image | 4 | $0.20 | $0.80 |
| Grok Imagine Image 2.0 | 4 | $0.10 | $0.40 |
| BFL FLUX.2 Pro | 4 | $0.25 | $1.00 |
| **Full bakeoff** | **16** |  | **$4.20 maximum reserved** |

The $4.20 maximum simultaneous reservation is 4.2% of the authorized aggregate $100 cap. This is a ceiling, not a spend forecast or target. Submitted requests with unknown exact cost retain their full ceiling until billing reconciliation; only proven-unsubmitted reservations may be released at zero cost.
