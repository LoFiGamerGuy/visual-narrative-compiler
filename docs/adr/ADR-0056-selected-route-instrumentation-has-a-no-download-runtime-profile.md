# ADR-0056: selected-route instrumentation has a no-download runtime profile

- Status: accepted
- Date: 2026-09-01

## Context

The runtime manifest previously described documentation, frozen baseline, and Blender-stage prerequisites but not the selected route's growing offline instrumentation suite. Bootstrap also created `.env` by default, so it lacked a true no-write inspection mode.

## Decision

Add a distinct `instrumentation` profile without changing `baseline_legacy`. Pin the currently measured Python 3.14.6, Pillow 12.3.0, and numpy 2.5.1 environment, exact bootstrap/manifest/suite and interpreter hashes, suite entry point, and explicit no-download/no-network/no-credential requirements. Add `-DryRun` so bootstrap performs no environment/template writes.

## Consequences

- The exact local inventory records CPython 3.14.6 and executable SHA-256 `03168c01…a0c38`; all three pinned requirements match.
- Ten/ten source, interpreter, dependency, download, network, credential, install, and provider mutations fail.
- A full instrumentation dry run passes 43/43 checks in 26.524 seconds without package install, model download, provider call, upload, or spend.
- The ignored older local manifest remains preserved and validates with four legacy-format warnings; the tracked example is strictly current.
- This snapshot is not a cross-platform wheel lock. A different runtime requires a reviewed inventory revision.
