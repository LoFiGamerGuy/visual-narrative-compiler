# Ember Lattice premium R&D tooling

This package is a deterministic, standard-library-only authoring, SVG-first build,
reconciliation, and audit path for the premium CH01 benchmark. It deliberately does
not contain final story or art. The tiny SVG under `fixtures/` exists only to exercise
the renderer and link auditor.

## Data contracts

`PremiumBenchmarkManifest/1.0` preserves the existing `ComicPanelPlan/1.0` planning
record for every panel. Benchmark validation requires at least 24 panels; the
integrated `premium_ch01` deliverable requires 40–60 unless a tracked rationale
supports another count. Both profiles require one
six-beat-or-longer causal action sequence, all required benchmark scenarios, exactly
one baseline route, one or more premium routes, hash-pinned assets, normalized
`[left, top, right, bottom]` zones, deterministic lettering units, and explicit
failure/repair provenance.

Every active workflow variant must have a distinct hash, every asset must reconcile
to exactly one `RenderRecord` (including its exact prompt hash and nullable provider
metadata), and the selected non-baseline route must win while improving both median
and weakest-panel score. Open hard failures block build.

`PremiumRubric/1.0` locks the 21 required quality criteria and weights before
evaluation. Every workflow/panel pair must be scored from 0–5. Results expose median,
weakest-panel, and mean weighted scores. Any recorded hard failure makes a workflow
ineligible; ties resolve deterministically.

Asset paths are POSIX-relative to `--content-root`, cannot traverse above it, and are
verified against lowercase SHA-256 values. Build outputs receive a
`PremiumBuildLedger/1.0`; audit re-hashes every ledger entry, parses every output JSON,
parses every SVG, and resolves every local HTML/SVG asset or navigation link.

## Entry points

Run from the repository root with `PYTHONPATH=src` (PowerShell syntax shown):

```powershell
$env:PYTHONPATH = 'src'
python -m reimaginings.ember_lattice.premium_rd author --output-dir <data-dir>
python -m reimaginings.ember_lattice.premium_rd validate --manifest <manifest.json> --rubric <rubric.json> --content-root <root>
python -m reimaginings.ember_lattice.premium_rd build --manifest <manifest.json> --rubric <rubric.json> --content-root <root> --output-dir <site>
python -m reimaginings.ember_lattice.premium_rd audit --manifest <manifest.json> --rubric <rubric.json> --content-root <root> --site-root <site> --report <audit.json>
python -m reimaginings.ember_lattice.premium_rd all --manifest <manifest.json> --rubric <rubric.json> --content-root <root> --output-dir <site>
```

`author` writes an intentionally unfinished 48-panel CH01 starter: placeholder paths,
hashes, copy, recommendations, and zero scores must be replaced with evidence. The
production `build` and `all` commands fail closed until all assets and data validate.

The site builder creates:

- premium hub and blind/normalized rubric results;
- phone, full-size, compact, and action-only readers;
- per-workflow direct art layers with transparent SVG lettering/UI overlays;
- grayscale/value, safe-zone/focal-overlap, and UI-density diagnostics;
- complete-set baseline-versus-premium comparisons;
- preserved failure/repair gallery;
- canonical rubric summary and build hash ledger.

## Verification

```powershell
$env:PYTHONPATH = 'src'
python -m unittest reimaginings.ember_lattice.premium_rd.tests.test_premium_rd -v
python -m compileall -q src/reimaginings/ember_lattice/premium_rd
python -m reimaginings.ember_lattice.premium_rd.integrity before --before <before.json>
python -m reimaginings.ember_lattice.premium_rd.integrity after --before <before.json> --output <after.json>
```
