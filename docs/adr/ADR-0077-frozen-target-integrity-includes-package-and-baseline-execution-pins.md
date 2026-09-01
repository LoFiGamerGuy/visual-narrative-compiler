# ADR-0077: frozen-target integrity includes package and baseline execution pins

- Status: accepted
- Date: 2026-09-01

## Context

Repeated validators showed the frozen research package still passed, but the hard boundary also prohibits tuning `baseline_legacy`. A current audit must compare both the complete tracked package and the tracked execution/configuration surface across time, while being honest that the legacy bundle, workflow, and result are local untracked files.

## Decision

Compare exact path/byte/hash inventories between safe-source commits `f505788` and `00498df` for all v2.1.1 files and four tracked baseline execution/configuration files. Separately hash-check the local bundle/workflow/result against their declarations and validate the unchanged failure-profile summary without rerendering.

## Consequences

- All 16 frozen package paths and four baseline tracked paths are byte-identical; changed counts are zero.
- The gauntlet remains `f826b0f1…e9ae`; local `garden/gen3.py` remains `004298df…db8` and matches the baseline bundle.
- The local Stage-A result remains 12 cases/24 generations/0 assertion-conformant/0 accepted and rejected for further benchmarking with no tuning.
- Fifteen/fifteen path/hash/promotion/tuning/activity mutations fail.
- Local untracked artifacts are explicitly not given Git-history claims, and no renderer rerun or imagery inspection occurs.
