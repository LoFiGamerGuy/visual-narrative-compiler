# ADR-0013: Native repair and deterministic exterior compositing are separate assertions

Date: 2026-09-01

## Context

Illustrious XL v2 plus the verified Xinsir ProMax `repaint` ControlNet can perform a fictional masked teal-to-green token edit when the ComfyUI mask is alpha-encoded and the Xinsir-specific black-pixel preprocessing is enabled. The uncomposited renderer still changes pixels outside the target through VAE decoding and generation.

## Decision

Keep native inpaint target correctness and deterministic exterior preservation as two independently measured stages. A final mask composite may guarantee unchanged exterior pixels, but it must never be used as evidence that the renderer performed the requested target edit. The no-change control must assess the target region separately.

## Consequences

The r3 edit establishes only fictional localized-edit mechanics. The r4 no-change control changes the target token despite an unchanged prompt, so this route is not yet a reliable repair method. This ADR applies to comic execution adapters only; it does not define animation-shot direction.
