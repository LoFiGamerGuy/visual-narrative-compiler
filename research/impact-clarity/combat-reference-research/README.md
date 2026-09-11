# Combat reference selection board

Open [the offline board](../../../docs/impact-clarity/combat-references/index.html). Sixteen small attributed excerpts from eight official/licensed series, exact source locators and independent blank preferences. External comics never enter image generation.

39 browser checks passed across the main QA and actual-download QA. Actual native inspection covers all sixteen chosen sources; rendered visual QA samples the phone opening, first card/ratings, comparison/footer and desktop opening. See `visual-review.json` for exact scope.

`data.json` in the board is bound to exports by SHA-256 and excerpt hashes. Wrong dataset, missing/extra IDs, duplicate/bad bindings, unknown fields and invalid ratings are rejected. Notes preserve exact text and unanswered values remain null.

The limited excerpts are portable. Full source context requires the official online readers. No complete episodes or working download cache enter the portable package. `local/` is ignored and excluded. Source publication dates not independently verified remain null.

`report-source.md` is the canonical research source; `research-summary.md` is its linked readable companion. `source-ledger.json` carries source/gap/search evidence; `plan.json` records the unavailable update_plan tool fallback and completed phases.
