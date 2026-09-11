# Chapter8 promotion-header audit

**PASS: administrative wording only.** I inspected the actual promotion-ready JSON/text diffs against the exact reviewed v2. No official files, reader, selection, gate or artwork were modified or invoked.

Promotion-ready JSON SHA-256: `0a3d3a441efd5017d84347c2e5849c514f313a00f6bfdb0df898cd93ea1982fc`. All45 complete panel objects, all53 copy entries and every metadata value other than `status` remain exact. Status now correctly says reviewed before art rather than awaiting this completed review. `owner_approval` remains null.

The Markdown changes only its introductory paragraph; the entire body from N8-01 through N8-45 is byte-exact. The state map changes only its administrative introduction; the complete clock, geography, custody, authorities, gear and production-risk body is byte-exact. The production order changes only its introductory paragraph and final administrative paragraph. Its allocation/coverage table, dependencies, per-image preservation limits and caution about actual mechanical evidence remain unchanged.

I recomputed each actual unified diff and matched it to `PROMOTION-READY-RECEIPT.json`; source/destination hashes also match. All45 JSON action/copy/camera/current-state fields remain verbatim in promotion-ready Markdown. Thus the full v1 reading plus approved narrow v2 review carries forward without another story revision.

The new wording does not authorize image calls by itself: it explicitly defers to a separate gate binding verified SevenChapters delivery and finite allowance. Qualification and owner approval are not granted. The existing note that23 coverage entries include01 reuse/no call still applies; active accounting must count actual invocations.

These files remain excluded promotion preparation until root activates them after the portable gate. Review scope is exact header/administrative promotion; no fresh artwork or phone-reading claim.
