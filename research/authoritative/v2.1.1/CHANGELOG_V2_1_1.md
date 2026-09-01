# CHANGELOG — v2.1.1
**Package-integrity pass. No new research.** 2026-08-31.

`ngvnc_research_v2_1_1.zip` supersedes v2.1 and v2.0. Both earlier zips should be discarded.

## Validation

`scripts/validate_research_package.py` — **0 failures, 0 warnings.** It found **30 defects** on
first run, including four the audit did not list. `PACKAGE_STATUS.md` is generated, never hand-edited.

The validator fails the build on: inconsistent conflict order · stale prohibited phrases · duplicate
ids · missing control/injection parents · Stage-A ids that do not exist · prose counts disagreeing
with computed counts · seed arrays inconsistent with declared generation math · hard-coded pair
counts · restricted-weight entries named by architecture family · unsafe child-safety wording.

## Computed counts (from `bench/gauntlet.json`)

| | |
|---|---|
| render cases | **40** — 10 N / 10 O / 10 I / 6 SET / 4 VFX |
| paired-variant relations | **10** (20 cases) |
| Stage A smoke | 12 cases × 2 seeds = **24** generations |
| Stage B full | 40 × 3 = **120** renderer generations per finalist |
| QA no-change controls | 4 templates × 3 seeds = **12 comparisons** (derived) |
| QA error injections | **8 cases** (derived) |
| spatial modes | 33 grounded / 3 cheated / 4 2d_only |

**The 132-generation figure was wrong**, and so was "44 shots" and "12 mirrored pairs".

## Applied

**P0** — one canonical conflict order in README, CORRECTIONS and HANDOFF (corrections now rank
**above** the research package, per the README) · all v2.0 claims purged from source documents,
not merely annotated elsewhere · `gauntlet.json` restructured into `render_cases` / `qa_controls` /
`qa_error_injection` · seed math made consistent · **paired variants retyped**: the ten relations
span five axes (`left_right_swap` 6, `interaction_role_swap` 6, `near_far_swap` 4,
`depth_role_swap` 2, `focus_role_swap` 2), each with a `variant_discriminator` naming the manifest
key that must differ — the validator fails if a pair's discriminator is absent or identical, so
"mirror" is executable rather than prose · `executable_bundle_status: NOT_YET_FROZEN` with its
required fields and bootstrapping order recorded.

**P1** — `SceneRecord.cast[].placement` restricted to a **named semantic mark**; explicit
transforms are forbidden in the shared layer · `locked_at` replaced by immutable published
revisions plus an edition manifest · opaque stable ids (ULID/UUIDv7) with a separate human alias
and a recalculable integer order key; the float-gap trick withdrawn · `environment_fingerprint`
added to RenderRecord (node commits, model/VAE/TE/LoRA/control hashes, sampler impl, python/torch/
CUDA, GPU class, input asset hashes, compiler + adapter versions) and "a render is a pure function
of its inputs" softened to **traceable reproduction** · Illustrious LoRA retraining made a stated
prerequisite of Arm A, not conditional · child-safety wording corrected to "no **real-person
likeness/biometric** identity data" · QA error-injection suite added.

## Disagreements — recorded, not silently changed

**1. The injection suite will flatter the QA sensor, and the docs now say so.** Injected errors are
clean, localised and deliberate; real drift is diffuse and correlated. **Recall on synthetic
injections will overstate real-world recall.** I have written two rules into the gauntlet: report it
as *"recall on synthetic injections"*, never as "detection recall"; and derive injection classes
from this project's **own observed failure log** rather than inventing plausible ones. The honest
framing is that injections give a **lower bound on blindness** — a class missed on a clean synthetic
example will certainly be missed in the wild.

**2. Excluded from the benchmark count is not excluded from the compute budget.** The 12 control
comparisons are real re-renders costing real GPU time. Correct to keep them out of the benchmark
denominator; wrong to omit them from the budget. Noted explicitly so nobody under-budgets.

**3. The executable bundle cannot be authored yet, and that is a sequencing fact, not an omission.**
The control-asset set is adapter-dependent, so the bundle needs at least one renderer arm to exist
first. Order recorded in `gauntlet.json`: semantic freeze (done) → build arm 1 → author and version
`BenchmarkCaseBundle` v1 → only then call the harness frozen. Calling it frozen today would be the
same class of error as the count drift this pass fixed.

**Otherwise I accept the audit in full.** The count inconsistency, the mirror mislabelling and the
mixed control semantics were real defects, and the mirror one was a straightforward mistake on my
part: I wrote "12 mirrored L/R pairs" in prose while the data held ten relations spanning five
different experimental operations.

## The method lesson, now enforced rather than stated

v2.0's lesson: *tags describe provenance, not currency.*
v2.1's lesson: **narrative research artifacts need machine-checkable internal consistency.** A
correction announced in one document and not applied in six others is indistinguishable from no
correction at all. That is now a build failure rather than a matter of diligence.
