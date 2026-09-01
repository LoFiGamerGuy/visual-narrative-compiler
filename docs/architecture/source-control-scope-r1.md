# Source-control scope r1

## Current remote

`origin` is configured as `https://github.com/LoFiGamerGuy/visual-narrative-compiler.git`. A read-only remote-head check on 2026-09-01 found no branch heads. No commit or push has been made from this workspace.

## Why an indiscriminate initial commit is unsafe

The workspace is approximately 96 GB before Git metadata. Major local-runtime areas include ComfyUI (~67.0 GiB), AI Toolkit (~10.1 GiB), models (~5.3 GiB), tools (~2.1 GiB), and LoRAs (~0.8 GiB), alongside logs, archives, historical material, and research outputs. A blanket `git add .` would be slow, likely exceed normal hosting limits, and risks uploading files that have not yet passed provenance/license review.

## Intended first tracked scope

- architecture, ADRs, research documentation, registries, manifests, validators, adapter source, and reproducible workflow/configuration definitions;
- small, hash-pinned review/evidence artifacts only where their provenance and external-sharing boundary are clear;
- `.env.example`, never `.env` or credential material.

## Explicitly excluded pending review

- model/checkpoint/LoRA weights, installed applications, package caches, generated logs, and installer archives;
- datasets, external-reference inputs, and historical materials not cleared for repository distribution;
- any file containing credentials, private URLs, personal data, or adult-likeness material.

## Next source-control action

Build a reviewed allowlist and a machine-checkable sensitive/large-file preflight before making the initial commit. This preserves the Git remote as a durable project home without falsely treating the entire local GPU workstation as a publishable source tree.
