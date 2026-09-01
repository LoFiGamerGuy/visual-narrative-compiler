# ADR-0037: restoration archives are local and do not authorize rerenders

- Status: accepted
- Date: 2026-09-01

## Context

A hash manifest detects missing or changed G07 evidence but cannot itself restore the original provider records and candidate bytes. A local archive can rehearse portable recovery, but it must not become a hidden source expansion, a Git payload, or an excuse to regenerate lost evidence.

## Decision

Create a deterministic uncompressed ZIP containing exactly the manifest, two approved public controls, 19 provider records, and 16 candidate rasters. Use fixed metadata and sorted safe paths. Keep the archive below ignored `experiments/`, validate all members directly without extraction, and refuse to overwrite a differing archive.

Treat absence or corruption as a restoration gate. Neither condition grants provider access, spend, upload, rerender, review, or acceptance authority.

## Consequences

- The 38-member archive is byte-repeatable in the pinned local runtime.
- Missing, extra, corrupt, path-escaping, and duplicate members fail validation.
- Provider evidence can be copied to separately authorized durable storage later without changing source-control scope.
- Same-disk local archival does not prove off-device disaster recovery.
- The current archive is 19,879,277 bytes with SHA-256 `64bea215c1d340684046b951507018fe7d5c657d4a8d04ac99e6d24aca69cad7`.
