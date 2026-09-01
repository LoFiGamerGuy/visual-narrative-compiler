# Production time and cost measurements

All unavailable values are deliberately recorded as `unmeasured`; estimates must not be substituted for observations.

| Record | Scope | GPU generation | Human minutes | API/cloud cost | Acceptance |
| --- | --- | ---: | ---: | ---: | --- |
| baseline_legacy Stage A, 2026-08-31 | 24 renderer candidates | 903.79 s total | unmeasured | $0 API/cloud | 0 accepted |
| CH01 kitchen sequence v1 | 4 archival composite panels | historical source timings unmeasured | unmeasured | historical local only | internal research accepted |
| CH02 treeline-return sequence v1 | 3 archival single-render panels | historical source timings unmeasured | unmeasured | historical local only | internal research accepted; non-commercial |
| CH03 ridge-signal legacy_duo3 demo | 3 new local candidates | 117.312 s total | unmeasured | $0 API/cloud | 0 accepted; all rejected in triage |
| CH03 ridge-signal built-in frontier-art draft | 4 frontier candidates (1 targeted repair) | 170.5 s observed tool elapsed total | unmeasured | not exposed by service | 0 accepted; 3 narrative candidates pending human review; repair preliminarily rejected |
| CH04 dawn-trail built-in frontier-art draft | 3 frontier candidates | 152.9 s observed tool elapsed total | unmeasured | not exposed by service | 0 accepted; all 3 narrative candidates pending human review |
| CH05 Mill Signal built-in visual smoke | 4 frontier candidates across a non-canon 50-panel script | 194.1 s observed tool elapsed total | unmeasured | not exposed by service | 0 accepted; all 4 candidates pending human review; not a current chapter draft |
| sequential inpaint P07 preflight | 4 renderer passes / 2 seeds | 108.42 s total | unmeasured | $0 API/cloud | 1 mechanics smoke accepted; 0 production accepted |
| sequential inpaint P07 provenance replay | 2 renderer passes / deterministic seed-101 replay | 54.165 s total | unmeasured | $0 API/cloud | hashes reproduced; no independent candidate decision |
| sequential inpaint G07 controls | 4 no-change diagnostic/reconstruction passes | 12.19 s total | unmeasured | $0 API/cloud | control protocol corrected; no production candidate |
| sequential inpaint G07 role-swap smoke | 8 renderer passes / 2 cases × 2 seeds | 216.70 s total | unmeasured | $0 API/cloud | 0 production accepted |
| actor-matte G07 deterministic control | 2 local composite outputs | execution time not instrumented (sub-second) | unmeasured | $0 API/cloud | 0 semantic-smoke accepted |

Future runs must start a human-review timer at candidate inspection and stop it at accepted/rejected decision, including repair time.
