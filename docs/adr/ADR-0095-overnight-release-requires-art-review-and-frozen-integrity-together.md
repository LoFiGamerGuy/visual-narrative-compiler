# ADR-0095: Overnight release requires art-review and frozen-integrity gates together

- Status: accepted
- Date: 2026-09-01

## Context

The overnight work spans generation evidence, targeted hardening, non-canon concepts, cadence assembly, three lettering experiments, a production handoff, an owner review index, density diagnostics, and nine style-direction revisions. A local release could appear coherent while silently breaking a frozen research target, tracking generated pixels, or promoting a review selection.

A 16-command no-network orchestrator now validates every overnight evidence family plus style lineage, frozen v2.1.1/`baseline_legacy` integrity, and tracked source scope. All 16 pass in 5.259 observed seconds and reproduce from exact script/stdout hashes. Fifteen/fifteen release-evidence mutations fail.

## Decision

Require the integrated release gate for overnight handoff. Visual/production evidence and frozen/source integrity must pass together; neither substitutes for the other.

Normalize only the live tracked-path count in source-scope stdout, while retaining its return state and exact stable result. Keep every command explicitly non-network-capable.

## Consequences

- The current release has 16/16 local commands passing, frozen/baseline unchanged, and safe source scope valid.
- Passing does not accept art, clear commercial use, bind copy, or make any row executable.
- Provider calls/uploads/downloads/cost for the gate remain 0/0/0/$0.
- Future evidence changes must rerun the gate and record a new append-only revision rather than rewriting r1.
