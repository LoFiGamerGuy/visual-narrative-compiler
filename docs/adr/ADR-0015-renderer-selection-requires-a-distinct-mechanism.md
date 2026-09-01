# ADR-0015: The next renderer test must use a distinct mechanism

Date: 2026-09-01

## Context

Native Illustrious XL v2 plus Xinsir repaint retained exact exterior pixels after deterministic compositing, but achieved only one of two requested target edits and zero of two target no-change controls. FLUX.2 Klein is a useful local composition diagnostic but its exact VAE is non-commercial and its no-change behavior globally drifts. Legacy adult capture cannot supply a usable two-role set.

## Decision

Do not invest in further parameter/mask optimization of the current native repaint route or reuse it as the next comparative renderer arm. Preserve its evidence and the geometry/provenance foundations. The next renderer evaluation must be a distinct model mechanism with a versioned profile, fictional controls, paired role-order cases, target no-change, and injection calibration.

## Consequences

Qwen-Image-Edit-2511 is the highest-information currently identified distinct mechanism, but the current 24 GiB local GPU cannot support the official 53.75 GiB BF16 artifact set before runtime overhead. Acquiring/executing it requires a capacity/profile decision. This ADR does not authorize cloud spend, sensitive upload, adult references, or any commercial claim.
