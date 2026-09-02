# CH05 chapter production operating playbook r1

Current state: `DRAFT_BLUEPRINTED`; zero lifecycle transitions are enabled. This playbook is operational documentation, not execution authority.

## 1. Source And Remote Preflight

Status: `READY_LOCAL_ONLY`.

Commands:

- `python src/north_garden/validate_tracked_source_scope.py`
- `python src/north_garden/validate_ch05_remote_lineage.py`

Pass: zero failures and HEAD/origin parity

Fail closed on: any tracked generated/prohibited/credential path or remote mismatch

## 2. Integrated Evidence Preflight

Status: `READY_LOCAL_ONLY`.

Commands:

- `python src/north_garden/validate_ch05_overnight_integrated_release_gate_r9.py`
- `python src/north_garden/validate_frozen_gauntlet_baseline_integrity.py`

Pass: r9 reproduces 58 checks and frozen 16 + baseline 4 remain exact

Fail closed on: any semantic, stdout, frozen, or baseline mismatch

## 3. Exact Owner Root Intake

Status: `OWNER_ACTION_REQUIRED`.

Commands:

- `python src/north_garden/validate_ch05_p010_p013_owner_unlock_contract.py`

Pass: six exact structured roots or exact alternate revisions are bound

Fail closed on: broad approval alone; current 0/6 structured roots

## 4. Production Prompt Promotion

Status: `BLOCKED_NOT_IMPLEMENTED_AND_OWNER_ROOTS`.

Pass: future compiler writes four immutable production prompt hashes without mutating blueprint evidence

Fail closed on: compiler intentionally absent; production manifest prompts remain null

## 5. Reference And Prompt Preflight

Status: `READY_DRAFT_VALIDATION_ONLY`.

Commands:

- `python src/north_garden/validate_ch05_prompt_blueprint_draft.py`
- `python src/north_garden/validate_ch05_prompt_blueprint_adversarial_fixtures.py`

Pass: 4/4 drafts pass, 28/28 malformed fail, exact P040/P050 or text-only references

Fail closed on: age/likeness, hair/wardrobe/role, causal, lettering, reference, or execution regression

## 6. Openai Builtin Imagegen

Status: `BLOCKED_PRODUCTION_PROMPTS`.

Agent-only action: Use only OpenAI built-in ImageGen after production prompt hashes exist; upload only exact authorized reference hashes per row; no paid API.

Pass: four local ignored candidate files and tool-visible execution metadata

Fail closed on: provider unavailable, prompt gate unresolved, reference mismatch, or any expanded upload class

## 7. Renderrecord Finalization

Status: `BLOCKED_RENDER_OUTPUTS`.

Pass: one complete RenderRecord per candidate with exact nulls for unavailable service fields

Fail closed on: missing prompt/input/output hash, dimensions, elapsed time, failure, candidate file, or human-review state

## 8. Review Packet Build

Status: `READY_DRY_RUN_ONLY`.

Commands:

- `python src/north_garden/build_ch05_p010_p013_review_packet.py --dry-run`

Future command after gates: `python src/north_garden/build_ch05_p010_p013_review_packet.py`.

Pass: dry run writes nothing now; actual build later creates five ignored deterministic artifacts

Fail closed on: any of four candidates absent for actual build or nonignored output path

## 9. Live Human Review

Status: `BLOCKED_PACKET`.

Commands:

- `python src/north_garden/validate_ch05_human_review_time_event_log.py <event-log.json>`

Pass: 44 candidate checks, sequence review, explicit decisions, and valid non-backfilled timer log

Fail closed on: missing check, invalid event chain, inferred minutes, or unresolved FAIL/WARN disclosure

## 10. Targeted Repair Loop

Status: `BLOCKED_EXACT_FAILURE`.

Commands:

- `python src/north_garden/validate_ch05_p010_p013_lifecycle_state_machine.py`

Pass: at most two one-class repairs; passing rows and diagnostic failure preserved

Fail closed on: broad reroll, multi-class change, missing repair RenderRecord, or skipped packet/review

## 11. Provisional And Rights Decisions

Status: `BLOCKED_HUMAN_REVIEW`.

Pass: provisional engineering decision, commercial clearance, and exact-base eligibility recorded separately

Fail closed on: group acceptance, implied rights, reproducibility claim, or exact-base/commercial conflation

## 12. Safe Evidence Release

Status: `READY_SAFE_SOURCE_ONLY`.

Commands:

- `python src/north_garden/validate_ch05_production_cost_ledger_r26.py`

Operator release actions:

- `git diff --check`
- `git push origin main`

Pass: only safe source/evidence committed and HEAD equals origin/main

Fail closed on: generated pixels, credentials, weights, datasets, references, runtimes, caches, or unrelated material staged

## Current review entry points

- Hub: `C:\AgentWorkspaces\anime-pipeline\experiments\review-packets\ch05-owner-review-index-r5\index.html`
- Exact links: `C:\AgentWorkspaces\anime-pipeline\docs\research\ch05-review-links-r3.md`
- Six-root checklist: `C:\AgentWorkspaces\anime-pipeline\docs\research\ch05-p010-p013-owner-unlock-checklist-r1.md`
