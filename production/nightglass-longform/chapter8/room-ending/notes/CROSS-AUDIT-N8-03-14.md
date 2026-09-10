# Bounded Chapter8 root03–14 preservation audit

PASS. Eleven explicitly frozen root call IDs were checked:03–04P/R1,05–06P/R1,07P,08–09P,10–11P/R1,12–13P,14P/R1. This is seven primaries and four sole repairs. All eleven returned; every primary and failed/repaired whole native remains preserved. No second primary or repair was found for any lead panel.

For each chain, submitted request JSON equals the args in its call record, exact prompt text matches its recorded SHA, all27 reference occurrences match their actual source hashes, and the default PNG, preserved native and decoded two-field raw return are byte-identical. Status/invocation and ordered local timestamps are consistent. Model snapshot, seed, billing and owner approval remain null. The stored digest is a prompt digest; the audit additionally computes whole request-file SHA256 without pretending that field was recorded at submission.

All12 selected records03–14 match their hashes. Ten selected crops are within bounds and match the exact recorded source rectangles, image modes, dimensions and pixels without scaling.07P and14R1 are direct whole-native selections.10 correctly uses the original primary crop while11 uses the repair; preservation does not erase failed intermediate artwork or imply a repair left another tier untouched. The eleven call records and audited selection projection stayed unchanged during the checks.

Metadata-only reconciliation at audit completion: lead13 returned, room2 returned, relay1 submitted/pending, totaling16 invoked/15 returned/1 pending.02 and the room calls were counted only, not re-audited. The new relay call is excluded from these eleven chains. This observation is time-bound and does not block further authorized production.

Exact per-call hashes, all reference occurrences, crop rectangles and selected hashes are in CROSS-AUDIT-N8-03-14.json. This audit does not claim renewed native, phone, causal or full-story acceptance; those reviews are separate. No artwork, source references, shared selections or reader files were mutated, and no image call was made.
