# ADR-0182: Retain r6 with cross-panel semantic gates after alternate-graphic comparison

## Status

Accepted as an engineering recommendation; owner visual acceptance, rights, and exact-production-base decisions remain open.

## Context

The complete alternate-graphic arm produced 11 hash-pinned strips and 50 deterministic ComicPanelPlan crops. Non-gating review measured 36 PASS, 7 WARN, and 7 FAIL. Hair and wardrobe held across all 50 crops, but P001, P029, P032, P036, P039, P041, and P043 fail story, causal, role, or prop-continuity requirements. Equal-panel complexity proxies differ only slightly from r6: edge density -0.004286, grayscale entropy -0.051381 bits, and PNG bytes/native pixel -0.015096. The requested lower-density hypothesis is therefore non-separating.

Complete-chapter comparison also exposed two cross-panel omissions in the frozen r6 panel-local triage: P001 shows chimney smoke and a lit window before P048/P049's reversal, and P041 retains visible hot material/plume after the drum should be out. P032 remains WARN. Frozen r6 records are evidence and remain unchanged.

## Decision

Retain r6 as the strongest current engineering base, supplemented by a new pre-prompt cross-panel semantic gate contract. Do not promote the alternate-graphic arm wholesale. Preserve its strong individual panels as review evidence. Require future full-chapter prompts to encode the cold-farmhouse reversal, departure vector, independent entry roles, impossible-print geometry, continuous leverage path, three-mark clue, fully extinguished drum, and map possession.

## Consequences

Selection is based on measured causal/continuity behavior rather than visual appeal alone. The new contract can prevent known prompt omissions but cannot prove that generated pixels comply. Visual inspection remains mandatory. No art is accepted, commercially cleared, or selected as an exact production base.
