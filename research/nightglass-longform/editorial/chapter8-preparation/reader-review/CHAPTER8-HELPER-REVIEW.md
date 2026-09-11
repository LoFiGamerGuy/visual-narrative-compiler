# Chapter8 staged lead-helper audit

**PASS after the bounded return-preservation fix.** Preparation and tests remain excluded; no image tool, real call record, official gate, source selection or reader was changed. Root made the staged recorder fix; I inspected the exact diff and ran isolated fixtures.

Bindings:
- `lead-setup/prepare_call.py`: `e15147ddfecb5357278c5571358fc31540a7bdfcc7a9bc384117787350be5c8a`
- Corrected `lead-setup/record_return.py`: `02263b135ed2b42a2f1747cefade4c6d27a3aed72c498742aaf5e0ef05c159c2`
- Preserved original `record_return-before-preservation-guard.py`: `f10b51ab6bbc5ddafc36ab5ada81e44b1c35603c3430bbeaff967881c610e26a`

## Allocation and original caps

The intended installed `chapter8/lead/notes` location gives the correct worktree root (`parents[5]`) and lead return root (`parents[1]`). Staged placement is deliberately not production installation.

The allowlist is exactly02–14 and33–43.01 and mixed01+02 attempts fail, as do15–32/44–45 and Chapter7 IDs. Ordinary permitted grouped IDs and R1/F1 suffixes parse correctly. Accurate reused01 therefore does not consume a new lead call. Proposed local ceilings33+24+3 total60;23 coverage units include01 reuse, leaving22 proposed new primaries.

Prepare verifies active gate status and exact script hash before recording submission, then counts all invoked local records against the lead ceiling. A new primary cannot overlap any previously invoked primary panel, including regrouped/renamed units. R1/F1 requires its own returned primary; exact call/request filenames cannot be overwritten. R1 must reference originalP; F1 requires recorded justification and exactly one own P/R1 source. Supported suffixes are onlyP/R1/F1. These preserve original unit caps without routine resets.

Global chapter/cumulative ceilings, authorized transfers, preceding ZIP verification and actual visual reference inspection remain root/gate duties. The helper enforces its local ceiling and script binding; its reference-review sentence is an assertion, not automated visual evidence. Its pre-invocation submitted/invoked record must still be reconciled with the immediate exact tool call, including failures. This matches the existing Chapter7 lane.

## Preservation fix and actual fixture results

The inherited recorder refused an existing candidate but could overwrite an orphan raw-return file; it also copied the candidate before validating call/metadata. Root preserved that original, then moved validation before writes, checked BOTH candidate/raw existence, and used exclusive `xb`/`x` creation. It now requires matching submitted call ID/status, string output_hint and matching encoded-image length before creating outputs.

Eight isolated scenarios passed under `reader-review/helper-fixture-v1/`: orphan raw stays byte-exact with no candidate; invalid metadata length and invalid hint type create no outputs; wrong call ID/status create no outputs; existing candidate stays exact; ordinary return preserves source/candidate/base64 bytes and updates the correct call to returned; repeat invocation leaves every fixture file unchanged. Test data are one fixed1×1 PNG and explicitly isolated fake records. No generation tool or production call was invoked. Runner and exact receipt: `check_return_fixture.py`, `CHAPTER8-HELPER-FIXTURE-RECEIPT.json`.

The diff is narrow: validation/order/nonoverwrite protections replace copy-first behavior. Native bytes are preserved without raster editing. Raw JSON remains reconstructed from source bytes and supplied output_hint/length, so upstream tool-return provenance remains necessary; this helper is not an independent authenticity verifier. It is also not a transactional filesystem/recovery service: any I/O-created partial evidence must remain preserved and reviewed, not deleted to obtain a retry.

## Other checks actually performed

Both staged scripts compile in memory without execution/pycache. Exact source comparison confirms prepare differs from Chapter7 only by chapter paths/gate/allowlist; preserved original return is byte-identical to Chapter7. Thirteen pure in-memory ID boundary/group examples pass. Intended installed root calculations pass. Prepare was not invoked against real or simulated production and no call allowance was created. No further helper change requested before root’s installation/gate decision.
