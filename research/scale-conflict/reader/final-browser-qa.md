# Final reader browser QA

PASS on the final selected study dataset `5064c970acc9777859d13bd8248359efa01747502e27422c8443247d22b09202`. This is reader verification, not artwork or owner acceptance.

Actual Chromium checks ran at390×844,1024×768 and1440×1000. All24 selected images and51 retained native attempts decoded. Landscape and portrait images retained their full native aspect ratios with no page overflow. The phone entry screenshot shows the first complete scene within the initial viewport; responses stay collapsed, and full image comparisons stack on phone and align at equal widths on desktop. Actual1024 comparison and1440 Q02/Q03/Q04 comparison screenshots were inspected for layout and readable captions. Portrait V03 remained fully visible in its selected/history phone captures.

All24 AI observation lists matched final source-bound data exactly and remained separate from owner responses. Expanded T05 and Q01 notes were inspected at allthree widths. T05 describes surface competition rather than owner comfort; Q01 describes broad geography while retaining the arch-variation caveat. Q03's failed HTTP503 request appears as one separate no-artwork record with distinct failed-request and raw-output links. It adds no native image or response target.

The201 functional assertions cover exact category/scale/subject/story filters, shared-subject comparison, native zoom, keyboard activation/Escape, retained histories, references, exact previous-export bytes, report links, blank defaults, real exported-file/imported-file roundtrip and reload, atomic stale/tampered import rejection, and actual missing-source fallback with disabled updates. Final choices are blank and unchanged. Browser console is clean apart from the intentionally isolated missing-image test error.

Required validation:22 builder tests and18 preference import-rejection cases pass. Two initial harness errors were corrected: a quote in the intentional missing-source selector and reused download directory detection. Their failed receipts remain as `browser-qa-harness-error.json` and `browser-qa-download-reuse-error.json`; neither was a gallery defect. The focused notes helper also received an evaluation-scope correction before its passing run.

Evidence:

- `browser-qa.json` SHA `ef82732dc5ee1f5bb06a0340a9ecc9491bc3d0332c72009f58a729feb1cd5fea`.
- `final-details-browser-qa.json` SHA `7d9bebea344057b98239b82008fa3516c41f239542f6f4d1e37b4e11a341d480`.
- All24 final selected phone captures: `phone-captures/5064c970acc9-e4391e52-9461ad9e/`; receipt SHA `4cddaeab4a3a3f35a3c944b06e70375b52dc60b2634776c8b912d482fb8fcc9e`. The added reader-data hash suffix preserves the prior last-four receipt unchanged despite identical artwork dataset and app hashes.
- Final review-notes SHA `38c1064e441f1ab0e50dcf8721c6262d0f3fc55ae527efc42922dd28069be756`; data.json SHA `9461ad9ec3595b2bfd436c80d4ba19b372be01c3d68c1b09f7f0719a6bb85dda`.
- Service-failure UI evidence: `service-failure-browser-qa.json` and final-details checks.

Source frozen after this report. Browser port9381/PID236129 remains owned by this study for root-authorized restored-package and committed-checkout smoke checks. Their outputs must go only to root-specified ignored locations. No production source was mutated by this final QA.
