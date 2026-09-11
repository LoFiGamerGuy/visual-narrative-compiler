# Final reader QA — CD-20260908-01

PASS. The workspace reader passed 302 actual browser assertions at 390×844, 1024×768 and 1440×1000. Builder validation passed 34 tests; preferences validation passed 18 atomic rejection cases plus independent ratings, blank/N/A distinction and persistence checks. The subsequent report-link-only rebuild passed 50 focused metadata/browser checks. No artwork or managed data was changed by QA.

Selected dataset: `7d50da6e380457e4ee25daea3b652797bf1fd9be374cd1a3dfbae4bd475502ad`. All 24 displayed artworks are F1; all 54 native attempts remain accessible. One separately labelled input-validation rejection produced no artwork; its original six-reference request, error, prompt, frozen plan and revised five-reference request remain accessible in W06 history. It adds no rating target. Total calls: 55.

Actual screenshot inspection confirmed complete uncropped art, readable controls, quiet inter-panel gaps and no horizontal overflow. Phone Read duel opens with art at approximately y334 and continues without response forms or AI observations between panels. All 12 duel, six group and six war panels were captured continuously with captions off, plus per-panel phone screenshots. Portrait W04 keeps its native ratio. The three-column tablet comparison preserves complete images; phone comparisons stack. Expanded technical observations are readable and separate from owner choices. Combat continuity findings remain in the source-bound observations and independent reviews; UI QA does not assert story acceptance.

Independent rating/comfort choices start blank; N/A is separate. Notes, shortlist, browser export/download/import, stale/tampered rejection, source failure handling, previous exact CE export, native zoom, retained history, related subjects and reading controls passed. Choices were restored to their original blank state. No runtime errors remained. The focused metadata helper initially encountered a QA-script lexical-variable redeclaration; scoping the temporary variable fixed the helper without changing the reader.

Evidence:

- [Full browser receipt](browser-qa.json), 302 assertions and 15 screenshots.
- [Final metadata receipt](final-metadata-qa.json), exact current data/notes/report hashes and 50 checks.
- [Final selected D10–D12 phone receipt](phone-captures/7d50da6e3804-74c7bc21-a5cbe089/receipt.json).
- [Last five retained-attempt receipt](phone-captures/history/c42c65433efd-b38a3d0d/receipt.json).
- [All 24 continuous phone receipt](phone-captures/continuous-7d50da6e3804-a5cbe089-74c7bc21/receipt.json), with `duel-continuous-390.png`, `squad-continuous-390.png` and `war-continuous-390.png`.
- [Last five equal-width strip](phone-captures/strip-7d50da6e3804-D10-F1-D11-P-D11-F1-D12-P-D12-F1/new-art-strip-390.png).
- [Readable W06 failure history receipt](input-failure-browser-qa.json); earlier spacing evidence is separately preserved.

Full art/functional receipts bind the data before the final report-link refresh. The focused metadata receipt binds the refreshed data; selected dataset, artwork and reader application code are unchanged. Portable extraction and exact-commit restore checks follow separately in ignored delivery output paths. Browser 9382 remains available for those checks.
