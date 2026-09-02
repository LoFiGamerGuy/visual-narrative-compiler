# ADR-0133: Pre-render packet builder fails closed until four candidates exist

Date: 2026-09-01

Status: Accepted

## Context

The P010–P013 review contract names five artifacts but previously had no deterministic implementation or exact post-render measurement slots.

## Decision

Add a local Pillow-based builder and a pre-render blueprint. Bind four candidate paths, planning/phone dimensions, cadence widths, proposed normalized quiet zones, protected content, density target ranges, 11 checks per candidate, 11 failure classes, two repair slots, and 16 required RenderRecord fields. Dry-run must write nothing and actual build must fail unless all four ignored candidate files exist.

## Evidence

- Dry-run reports four slots/four missing candidates and five ignored outputs still `NOT_BUILT`.
- Forty-four candidate checks, sequence review, decisions, times, output hashes, and dimensions remain empty.
- Four phone previews and four proposed safe zones are predeclared; zones require post-render human clearance.
- The builder is local/non-network-capable, preserves source pixels, and writes only ignored paths.
- Seventeen/seventeen mutations are rejected.

## Consequences

After a valid render, one deterministic command can build the packet. No current candidate, artifact, prompt, provider request, acceptance, or promotion is created by this milestone.
