# ADR-0131: Prompt blueprints are hashed drafts, not production prompts

Date: 2026-09-01

Status: Accepted

## Context

P010–P013 needs concrete continuity and causal-language review before any production prompt is compiled. The current production manifest intentionally has four null prompts because exact owner roots remain unresolved.

## Decision

Create a separate non-executable blueprint with four exact draft strings and hashes. Bind each draft to its ComicPanelPlan hash, style/format role, planning canvas, authorized reference hypothesis, adult/hair/wardrobe/role constraints, causal mechanics, density target, and quiet lettering-safe region. Do not copy drafts into production prompt fields.

## Evidence

- Four/four draft rows pass lint.
- Three reference uses span only P040 and P050; one no-person object insert is text-only.
- Every referenced local file matches its owner-authorized SHA-256 and `upload_performed` remains false.
- P036 is unused.
- All four production manifest prompts and prompt hashes remain null; execution-ready rows, uploads, calls, renders, and paid spend remain zero.
- Fifteen/fifteen mutations are rejected.

## Consequences

The drafts expose prompt risks early but do not authorize execution or become production RenderRecord inputs. A later compiler may promote them only after exact unlock decisions and a fresh immutable prompt hash record.
