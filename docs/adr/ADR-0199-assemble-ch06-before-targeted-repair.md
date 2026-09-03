# ADR-0199: Assemble CH06 before targeted repair

## Status

Accepted as the current production/review baseline. Owner review, acceptance, rights, commercial clearance, and exact-production-base selection remain pending.

## Context

The prior workflow spent too much production effort on repeated style variants of one chapter. ADR-0198 instead promotes one chronological route per panel and allows a repair only after the complete chapter reveals whether the defect matters in story context.

## Decision

1. Preserve all eight CH06 built-in ImageGen sequence outputs and deterministically crop them into 40 ordered panel candidates.
2. Assemble the complete reading draft, phone preview, sequence/contact sheets, and canonical lettering-safe-zone overlay before rerendering anything.
3. Keep P020 as a non-gating role-separation warning because Tamsin and Sigrid have similar dark-haired facial rendering despite distinct garments.
4. Mark P030 as the one exact failure because the generator rendered forbidden prose on the physical Ledger mechanism.
5. Treat the S08 source's panel numerals as an external white-footer artifact and exclude them through recorded deterministic cropping; do not alter the underlying source evidence.
6. Permit one narrow P030 no-text repair after full-chapter assembly. Do not reroll the sequence, passing panels, or a wholesale style arm.
7. Continue directly into CH07 production and CH08–CH09 authoring rather than holding story breadth for that repair.

## Evidence

Eight source strips produce 40 unique candidates with exact input/output hashes and exact prompts. The review packet has 38 PASS / 1 WARN / 1 FAIL, five required review artifacts, zero alternate arms, and zero repairs executed. The validator passes and rejects 16/16 adversarial mutations.

Service model, endpoint, provider request ID, usage, monetary cost, seed, and per-request elapsed time were not exposed; each field remains null/unavailable. Paid API/cloud spend is $0.

## Consequences

CH06 is the first complete new story chapter after CH05 and is now reviewable as a whole. The one repair target is precise and bounded. Generated pixels remain ignored local evidence and are not accepted, commercially cleared, reproducible, or an exact production base.

