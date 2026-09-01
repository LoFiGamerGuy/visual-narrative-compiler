# G07 fictional-control provider bakeoff comparison

Status: complete execution and non-gating instrumentation; authorized human review pending. No candidate is accepted and no geometry proxy is final art.

## Measured arm summary

| Arm | Required candidates | Required-arm cost | Mean elapsed | Independent repeat drift | Target-change drift | No-change drift | Operational/structural limitation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| OpenAI GPT Image 2 | 4/4 | $0.198621 estimated from usage/rates | 32.087 s | 76.33% | 10.78% | 51.42% | Slowest; no seed; invoice confirmation pending |
| Gemini 3.1 Flash Image | 4/4 | $0.268756 estimated from usage/rates | 11.759 s | 71.04% | 9.38% | 99.59% | First response needed no-regeneration recovery; no-change globally redraws |
| xAI Grok Imagine Image 2 | 4/4 | $0.280000 exact provider ticks | 12.506 s | 34.62% | 63.19% | 49.60% | Added central object in 3/4; one separate $0.07 hosted-URL failure |
| BFL FLUX.2 Pro | 4/4 | $0.240000 exact returned credits | 18.647 s | 99.78% | 99.97% | 99.92% | Global restyling; restrictive training-use boundary; labels in 3/4 |

Drift is the fraction of pixels whose maximum channel difference exceeds 8/255 after the reference is resized to the candidate. It is a full-frame diagnostic, not a semantic score. Required-arm total is $0.987377; the separate xAI transport failure makes aggregate experiment cost $1.057377. The ledger holds $0 and leaves $98.942623 available.

Non-gating visual triage finds the declared two proxies, orange-left role, right teal/green role, common table, and non-contact in all 16 candidates. All four target-change cases turn the right proxy green, and all four no-change cases retain teal. OpenAI and Gemini add no salient new object; xAI adds a central object in three cases; BFL and xAI sometimes add role labels. Authorized human-review state remains `not_yet_performed`, minutes remain null, and every acceptance value remains false.

## Mechanism decision basis

OpenAI GPT Image 2 is the strongest route for the next bounded hardening experiment because it combines:

- the lowest required-arm cost;
- 4/4 clean structural proxy cases without a salient extra object;
- low target-change global drift, within 1.40 percentage points of the best observed arm;
- materially lower no-change drift than Gemini or BFL;
- a pinned model snapshot and complete request/usage provenance.

This selection is not based on visual appeal and does not accept any output. It is an engineering mechanism choice for targeted-repair hardening. Gemini remains the latency leader and target-drift comparator; xAI remains the repeat/no-change pixel comparator but carries structural side effects and a transport failure; BFL remains fictional-control-only and is not eligible for expanded input.

## Reproducibility limitations

No arm exposed a deterministic seed. Two independent samples are evidence of observed variance, not a reproducibility rate. OpenAI/Gemini costs are documented-rate calculations pending invoice-level confirmation. Neutral geometry controls cannot establish character continuity, lettering, page rhythm, narrative-panel quality, or commercial-release eligibility. Those remain separate gates.
