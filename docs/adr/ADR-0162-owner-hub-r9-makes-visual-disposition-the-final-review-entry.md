# ADR-0162: Owner hub r9 makes visual disposition the final review entry

Date: 2026-09-01

Status: Accepted

## Context

Hub r8 exposes the response and ingestion contracts but predates closeout r3, the final consistency audit, and the 14-candidate visual worksheet. The review entry should foreground specific visual dispositions while retaining the complete earlier art and evidence surface.

## Decision

Extend r8 append-only with six links: immutable r8, closeout r3, candidate worksheet, consistency audit, release r12, and safe-source r4. Extend exact link manifest r6 by the r9 index and five tracked resources, preserving all 128 earlier bindings.

## Evidence

- Two consecutive hub builds produce byte-identical index and packet hashes.
- Hub r9 has six links (one HTML/five text) and rejects 22/22 mutations.
- Link r7 reaches 134 = 128 + 6 resources: 111 ignored local and 23 tracked metadata.
- Categories include ten hubs, ten contact sheets, nine sequence packets, 34 lettering resources, 14 strongest candidates, three non-canon concepts, 18 diagnostic/policy resources, 24 packet records, and 12 review checklists.
- Nineteen/nineteen link-manifest mutations fail.

## Consequences

Tomorrow's first click reaches both the full visual body and the strict candidate worksheet. Visual disposition remains separate from owner-root ingestion, acceptance, commercial clearance, exact-base selection, publication, and production execution.
