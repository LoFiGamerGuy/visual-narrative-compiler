# ADR-0156: Owner hub r8 exposes review-session contracts append-only

Date: 2026-09-01

Status: Accepted

## Context

The current r7 hub exposes the visual and final-evidence body but predates the strict response guide, final session starter, cross-file ingestion preflight, final model/license audit, and closeout r2. Review should not require reconstructing those dependencies from Git history.

## Decision

Extend r7 with a local-only r8 hub containing six links: immutable r7 plus five current review-session resources. Extend the exact link inventory from r5 to r6 with those five tracked documents and the ignored local r8 index. Preserve all 122 earlier path/hash/category bindings.

## Evidence

- Hub r8 builds twice to byte-identical index and packet hashes.
- Six links partition as one HTML and five text; 22/22 mutations fail.
- Link r6 reaches 128 = 122 + 6 resources: 110 ignored local and 18 tracked metadata.
- Category counts include nine hubs, ten contact sheets, nine sequence packets, 34 lettering resources, 14 strongest candidates, three non-canon concepts, 18 diagnostic/policy resources, 22 packet records, and nine review checklists.
- Seventeen/seventeen link-manifest mutations fail.

## Consequences

The owner has one current local entry point for pixels, evidence, provenance, response capture, and fail-closed post-response checks. Link inclusion still grants no ingestion, acceptance, commercial clearance, exact-base selection, publication, or production execution.
