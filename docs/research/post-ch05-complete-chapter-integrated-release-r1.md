# Post-CH05 complete-chapter integrated release r1

The current chapter-production stack passes one no-network integrated gate.

- Commands: 10/10 PASS.
- Effective checks: 93.
- Observed wall time: 4.481 seconds.
- CH05: 50 selected panels, 59 candidates, 49 PASS / 1 WARN / 0 FAIL agent triage.
- Inventory: 63 current ComicPanelPlans across CH01-CH05.
- Cross-chapter packet: 23 exact visual rows.
- Contract tests: 15/15 malformed authoring cases and 23/23 semantic graph cases rejected.
- Frozen integrity: 16 frozen and four baseline paths exact; baseline remains 0/24 accepted with no tuning.
- Provider calls/uploads/new generation/acceptance/commercial decisions/spend: 0/0/0/0/0/$0 for this release.
- Human review minutes: null.

Evidence: [integrated release record](C:/AgentWorkspaces/anime-pipeline/docs/research/evidence/post-ch05-complete-chapter-integrated-release-r1.json), SHA-256 `a95fd52847aa2e4f4fe17b9362b532329ac228e53e21b9af1e6e3c0bd119395b`.

The release validator binds all scripts and stdout hashes and rejects 12/12 adversarial mutations. ADR-0179 records the release policy.
