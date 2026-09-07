# Browser and package QA

**Final review UI checks pass at 390 × 844, 1024 × 768 and 1440 × 1000.** Chromium 151.0.7922.34 used local file URLs; phone runs use mobile metrics. This is not Safari, real-device accessibility, or mobile-network performance certification. [Machine browser evidence](evidence/final-browser-qa.json) records every page and interaction; [local package checks](evidence/package-checks.json) records link/JSON validation.

All built report pages, the hub and proof are opened at each size. The hub exercises every section navigation link, 20 pipelines × 6 score categories, and all four strategy views at each size. Keyboard Tab reaches visible navigation; table regions are focusable and scroll within their containers. Text remains selectable, disclosure controls work, and charts use explicit numbers/labels rather than color alone. Zero broken images, horizontal document overflow, external runtime dependencies or package-caused console errors/warnings remain in the completed pass. Outbound citations are the only network links; protected readers open local originals.

The initial browser pass exposed long-label/identifier overflow on seven phone pages. Wrapping and select sizing were corrected and the failed evidence was [preserved](evidence/browser-package-first-pass.json). The initial package-link check ran before three final reports and the preservation recheck existed; its [failed result](evidence/package-checks-first-pass.json) is also preserved. Final checks supersede these draft failures without erasing them.

## Original proof and synthetic expansion

| At 390px | Original | +30% synthetic copy | +50% synthetic copy |
|---|---:|---:|---:|
| Art height, 14 panels | 5,360px | 5,360px | 5,360px |
| Story strip | 6,821px | 6,856px | 6,876px |
| Whole audit page including controls/footer | 7,595px | 7,677px | 7,697px |
| Dialogue / system type | 16 / 14px | 16 / 14px | 16 / 14px |
| Horizontal overflow / text-container overflow | 0 / 0 | 0 / 0 | 0 / 0 |

The frozen 5,800–7,600px story scroll budget is met by the original proof; synthetic expansion increases page height without shrinking type. These live text lanes prevent art overlap by construction; they do **not** prove finished balloon tails, natural translation, or premium comic lettering. The text stress is artificial padding by character count, not a translated script. Guides, grayscale, contracts and fourteen panel links were exercised. Full-size and phone screenshots of contact/escape/aftermath were visually inspected. Adult figures are schematic; grip/contact mechanics still need skilled storyboard review before final art.

## Protected readers and sampling corrections

The separate production-reader review covers 22 true-mobile jobs plus a corrected editorial full-decode recheck. At editorial52, all 104 art/overlay images load, scroll height is 32,639px, and source image bytes total 129,375,574. This is addressed local file weight, not transferred network bytes or latency. Some old pilot SVGs load while nested raster art remains invisible; source art exists and is evaluated separately. That preserved defect is not a new-package broken image.

Initial volume captures accidentally repeated the header because a `figure` selector missed `article.panel`; corrected captures supersede them. Desktop-at-phone-width captures with a scrollbar remain stress evidence, not true mobile proof. An initial cold editorial pass had 85 pending lazy images; the explicit scroll/decode recheck loaded all of them. It is incorrect to report 85 missing assets.

Internal screenshots remain local in ignored `.scratch/final-qa` and the earlier screenshot folders. They are not portable Git artifacts; the JSON evidence and original protected reader paths are tracked. The browser helpers are session-specific, while built HTML uses system fonts and requires no dependencies to read.

Four [deterministic measurement tests](evidence/deterministic-tests.json) pass. They verify meaningful false-pass boundaries, not aesthetics. Machine scorecards preserve unassessed fields and 109 differences between independent AI passes; no test output constitutes owner acceptance.
