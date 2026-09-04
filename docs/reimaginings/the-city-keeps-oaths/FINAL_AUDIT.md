# The City Keeps Oaths — final production audit

## Outcome

Exactly ten complete chapters, 40 sequences, and 240 selected panels are authored, illustrated, locally lettered, assembled, and linked from `START_HERE.md`. Structural validation, prompt/source/output reconciliation, density review, manual phone review, and protected-worktree integrity pass.

## Quantitative record

- Manual sequence status: {'PASS': 29, 'WARN': 11}
- Manual exact warning classes: {'metric_density_above_pilot_in_story_readable_panels': 9, 'lettering_encroaches_character_head': 3, 'sfx_encroaches_character_head': 1, 'tarin_bent_spear_geometry_inconsistently_visible': 1, 'metric_density_above_pilot_in_climax_but_story_readable': 1}
- Metric proxy panel status: {'PASS': 54, 'WARN': 186}
- Metric proxy classes: {'edge_density_above_pilot_class': 144, 'high_frequency_occupancy_above_pilot_class': 160, 'global_entropy_above_pilot_class': 98, 'focal_luminance_proxy_below_pilot': 54}
- Generation requests: {'total': 91, 'production': 80, 'bounded_style_and_topology_pilot': 9, 'reference_assets': 2}
- Summed measured request latency: 28172.185 seconds; not wall-clock time.
- Direct paid/cloud spend: $0.
- Model, endpoint, request ID, usage, provider cost, and seed were unavailable and remain null.
- Generated pixels tracked by Git: 0.

## Repair wave

PASS_REPAIRS_EXECUTED: 7 hard lettering-clearance defects were repaired by deterministic safe-zone relocation only. Before/after comparisons are preserved for 2 chapters; generated source-panel changes: 0; non-target changes: 0; image regeneration requests: 0.

## Known limitations

- Every generated candidate remains owner-review-pending, unaccepted, commercially uncleared, not an exact production base, and non-reproducible unless proven.
- Pilot-relative density proxies produce conservative WARNs even when manual 390-pixel review passes; exact classes remain visible rather than being collapsed into a beauty score.
- Three initial concurrent style probes lack individual latency; their measured batch wall time is recorded and per-request latency remains null rather than invented.

## Integrity

Integrity status: PASS. Protected `main`, `origin/main`, both earlier reimagining branches/worktrees, and all 159 pre-existing untracked files retain their baseline heads, branches, statuses, paths, sizes, and hashes.
