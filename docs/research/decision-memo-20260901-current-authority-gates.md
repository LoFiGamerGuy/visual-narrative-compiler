# Decision memo — current North Garden authority gates

Date: 2026-09-01  
Status: action required; no unapproved operation performed

## Evidence now available

- The frozen v2.1.1 package and all local validators continue to pass.
- Four API adapters have no-network/no-write conformance checks. No provider key,
  approved spend-cap variable, or managed-GPU account credential is configured.
- CH03/CH04 have six pending-review visual samples. CH05 now has a clean,
  separate 50-panel development script plus four pending-review visual samples.
  CH05 coverage is 4/50 generated (8%), 0 accepted, 46 unrendered.
- The historical Garden's Anchor pilot is hash-pinned and quarantined: it has an
  unresolved 92-vs-96 count conflict, different lead names, and photo-derived
  design provenance concerns. It is not a safe implicit chapter source.

## Decision 1 — chapter source

**Recommendation: promote/revise the clean CH05 Mill Signal option, not the
historical pilot.** It starts only from the existing fictional CH04 hook and
has no inherited name, count, image, or photo-reference ambiguity.

Required owner decision: approve it for current canon and ComicPanelPlan
development, approve it with named rewrites, or reject it. The required
template is `production/templates/narrative-development-promotion-decision-template.json`.

## Decision 2 — controlled renderer bakeoff access

**Recommendation: execute the existing four-request fictional-control smoke
for Gemini, GPT Image 2, Grok Imagine, and BFL FLUX.2 once local credentials
and a bounded cap are configured.** It uses only hash-pinned abstract geometry
controls—never adult likeness or personal inputs. BFL remains fictional-control
only under ADR-0019.

The practical access requirements are:

- Gemini: `GEMINI_API_KEY` or `GOOGLE_API_KEY` and the cap variable.
- OpenAI: `OPENAI_API_KEY` and the cap variable.
- xAI: `XAI_API_KEY` and the cap variable.
- BFL: `BFL_API_KEY`, the cap variable, and two separately hash-verified public
  HTTPS URLs for the two fictional control images.
- all: `NORTH_GARDEN_APPROVED_BAKEOFF_CAP_USD` (the prepared adapters refuse a
  value above $20).

No key should be pasted into chat or committed. Current provider terms/paths
are documented in the model/license registry and renderer decision memo.
The root `.env` has been created with blank values and is ignored by Git;
`.env.example` is the shareable template. The four prepared API adapters now
load the local `.env` without a third-party dependency and still require an
explicit `--execute` flag.

## Separate governance gap

No Git worktree is detected. Establishing an owner-approved VCS baseline remains
necessary before calling a selected production route fully source-reproducible;
ADR-0021 deliberately avoids silently initializing project history.
Recommended remote repository name: `north-garden-visual-narrative-compiler`.
