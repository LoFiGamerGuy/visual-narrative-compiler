# Portable artwork and committed code

Share `research/visual-refinement/asset-bundle/local/final-v3/visual-refinement-portable.zip`. Extract the entire ZIP into a new folder, then open `START_HERE.cmd` on Windows or `docs/research/visual-refinement/index.html` directly. The sequence is beside it as `sequence.html`. No installation, server or account is needed to view the extracted readers.

The initial final-v1 package exposed a relative-path bug in the restoration rebuild command. Its files remain preserved. The corrected final-v2 package passed viewing and rebuild checks, but a completeness audit then found omitted .mjs verification scripts and source ignore/attribute files. It is also preserved. Final-v3 includes those files and is the delivery target. No art changed during these packaging repairs.

The archive contains all50 native generated attempts,13 original reference copies, editable controls, exact prompts, call receipts, source manifests, reviews and both offline readers. Original generation paths remain untouched. The embedded member manifest hashes every payload file; the external `archive-receipt.json` hashes the ZIP and embedded manifest. Share that receipt alongside the ZIP if byte verification is needed.

The final archive receipt and fresh-restoration verification are also copied into the tracked `research/visual-refinement/asset-bundle/` folder after the archive is frozen. Those post-freeze delivery receipts are intentionally outside the archive's own payload, avoiding a self-hash cycle. Native images and ZIPs remain ignored by Git.

The delivery branch is `autonomous/visual-refinement-20260907-1600`. The final local `research/visual-refinement/asset-bundle/local/delivery-final.json` records the exact committed HEAD, authorized remote parity, clean status, restored committed-checkout verification, final scoped preservation result and task-owned browser cleanup. These checks occur after the archive snapshot and commit; the final user handoff reports their actual results.

To restore the native assets into the matching committed code, use `bundle_assets.py restore` with the frozen ZIP, its external receipt and a fresh destination. Existing identical files are skipped; any different overlapping file aborts before writes. See the [portable helper instructions](asset-bundle/README.md). Do not run the original-return registration helper on another machine: its absolute original tool paths document this generation session. Use `verify_delivery.py --portable --output research/visual-refinement/local/restored-verification.json` to check restored native hashes and frozen inputs without requiring this machine's original tool directory.

The old Black Petal cover starter and ten cover examples remain in their previous delivered workspace, with exact locations in [START_HERE](START_HERE.md). They are preserved separately rather than silently replaced by this later study.
