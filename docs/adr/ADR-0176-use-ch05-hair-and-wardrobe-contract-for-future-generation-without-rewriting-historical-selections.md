# ADR-0176: Use the CH05 hair/wardrobe contract for future generation without rewriting historical selections

- Status: Accepted as an engineering continuity policy; owner canon review pending
- Date: 2026-09-02

## Context

The CH01-CH05 regression packet reveals a material design discontinuity. CH02-CH04 frequently depict Soren with very dark hair and Sigrid with long auburn/red hair. The current approved CH05 direction instead specifies Soren with light-brown to dark-blond swept hair and a pale oatmeal coat, and Sigrid with dark-brown to near-black tied hair and a practical blue-brown plaid wrap. CH01 figures are often too distant or heavily stylized for reliable hair comparison.

Some CH01/CH02 images are historical internal research selections. They are immutable evidence and must not be silently relabeled, overwritten, or treated as if they had always followed the CH05 contract.

## Decision

1. Use the CH05 r14 contract as the provisional future-generation identity/wardrobe target: light-brown/dark-blond swept hair and oatmeal coat for Soren; dark tied hair and blue-brown plaid wrap for Sigrid.
2. Preserve all historical selections, hashes, acceptance states, and edition records unchanged.
3. Treat CH01-CH04 art as renderer-era/style evidence, not as visual identity references for new generation.
4. Any replacement of an earlier accepted panel requires a new PanelRevision and edition selection plus owner canon review; never overwrite the original.
5. Armor, weapons, upgraded clothing, and monsters remain separate proposed progression material until an explicit ComicPanelPlan/canon record introduces them.

## Consequences

- New chapter work gets a stable hair/wardrobe target and avoids accidental color-role swapping.
- The historical-to-current discontinuity remains visible and auditable.
- This policy does not revoke historical research acceptance, accept CH05 art, decide commercial rights, or establish an exact production base.
