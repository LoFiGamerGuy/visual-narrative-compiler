# Total anime pipeline review — start here

**Modularly rebuild storyboarding, source selection and acceptance; retain Ember Lattice provisionally and keep the current renderer as a fair control.** Do not start another volume before a short, genuinely comparable reader passes. Renderer replacement and human-first production remain unproven.

Open the [offline review hub](../../docs/research/anime-pipeline-total-review/index.html) directly in a browser. It includes interactive A/B scorecards, the stage failure map, strategy comparison, original static pilot proof and links into the existing local readers. The protected sibling worktrees must remain in their current locations for those reader links; ordinary report review requires no network. Citation links go to publishers and official sources.

Recommended order: [executive decision](executive-decision.md), [strategy matrix](strategy-decision-matrix.md), [next-pilot specification](next-pilot-specification.md), then [red-team objections](red-team-review.md). The [static vector proof](../../docs/research/anime-pipeline-total-review/pilot-proof.html) is a rough layout/lettering test, not completed art or a route comparison.

**Preservation exception:** the raw comparison remains FAIL for one prior review tree/ref that changed concurrently; the other eight trees passed. The owner authorized finishing subject to independent analysis. [Independence disclosure](evidence/independence-and-authorization.md), [incident](evidence/external-change-incident.md), [handoff evidence](changed-files-and-integrity.md).

## Reports

- [causal gap tree ](causal-gap-tree.md)
- [comparable works analysis ](comparable-works-analysis.md)
- [coordination ](coordination.md)
- [economics rights risk ](economics-rights-risk.md)
- [executive decision ](executive-decision.md)
- [industry research ](industry-research.md)
- [inspiration derivation matrix ](inspiration-derivation-matrix.md)
- [lettering ui mobile audit ](lettering-ui-mobile-audit.md)
- [limitations and open questions ](limitations-and-open-questions.md)
- [next pilot specification ](next-pilot-specification.md)
- [owner feedback ledger ](owner-feedback-ledger.md)
- [pipeline inventory ](pipeline-inventory.md)
- [pipeline scorecards ](pipeline-scorecards.md)
- [recommended roadmap ](recommended-roadmap.md)
- [red team review ](red-team-review.md)
- [story progression action audit ](story-progression-action-audit.md)
- [strategy decision matrix ](strategy-decision-matrix.md)
- [technical pipeline audit ](technical-pipeline-audit.md)
- [validation goodhart audit ](validation-goodhart-audit.md)
- [visual sequential audit ](visual-sequential-audit.md)

## Machine-readable evidence and verification

- [causal-gap-tree.json](causal-gap-tree.json)
- [citation-ledger.json](citation-ledger.json)
- [common-rubric.json](common-rubric.json)
- [inspiration-derivation-matrix.json](inspiration-derivation-matrix.json)
- [next-pilot-plan.json](next-pilot-plan.json)
- [pipeline-inventory.json](pipeline-inventory.json)
- [pipeline-scorecards.json](pipeline-scorecards.json)
- [strategy-decision-matrix.json](strategy-decision-matrix.json)

- [Browser and package QA](browser-qa.md), [controlled proofs](controlled-proof-results.md).
- [Reader paths](evidence/reader-paths.json), [technical measurements](evidence/technical-measurements.json), [pixel/hash diagnostics](evidence/deterministic-measurements.json), [structure/lettering diagnostics](evidence/structural-measurements.json).
- [Independent visual B notes](evidence/visual-review-b.md), [A scores](evidence/subjective-scores-a.json), [B scores](evidence/subjective-scores-b.json), [independent red team](evidence/red-team-independent.md).
- [Initial integrity snapshot](evidence/protected-state-initial.json.gz), [original failed comparison](evidence/protected-state-comparison.json), [handoff recheck](evidence/protected-state-comparison-handoff.json), [spend](evidence/session-spend.json).

## Rebuild and reproduce

All custom tools live under `research/anime-pipeline-total-review/tools/`. Run from the isolated checkout. `measure.py` needs Pillow and NumPy; `build_hub.py` and `check_package.py` need Markdown and Beautiful Soup. The session installed dependencies only in ignored `.scratch/python`; use `PYTHONPATH=research/anime-pipeline-total-review/.scratch/python` when running them. That scratch is not portable or tracked. Package JSON/source reports and built HTML are tracked and require no build to read.

Run `python -m unittest discover -s research/anime-pipeline-total-review/tools -p 'test_*.py'` with that PYTHONPATH for the four deterministic measurement tests. `build_hub.py` renders the reports; `check_package.py` checks JSON and local links. Browser QA uses `qa_hub.mjs` and an existing Chromium CDP endpoint. The small browser helper is environment-specific and does not install a system browser.

Internal QA screenshots remain in ignored local scratch, not in Git; original panels remain in protected source trees. Third-party comic panels are neither embedded nor redistributed. Counts and proxy metrics are diagnostic; no synthetic score is human acceptance. Direct incremental paid/cloud spend: **$0**. Source art and future candidates are not commercially cleared; unknown generation metadata remains null.

Owner follow-up: [concrete cleanup, tooling and Astra next steps](cleanup-and-astra-next-steps.md).
