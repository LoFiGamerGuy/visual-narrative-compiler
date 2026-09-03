# CH05 active-goal art/output reconciliation r1

This package reconciles non-overlapping output denominators from tracked manifests. ComicPanelPlan is the only planning structure; no pixel, provider, upload, spend, acceptance, or rights action occurs here.

## Reconciled totals

| Metric | Count |
| --- | ---: |
| Service raster outputs | 76 |
| Panel-level candidates/crops | 312 |
| Authorized reference uses | 132 |
| Zero-reference outputs | 13 |
| Unsplit ablation diagnostics | 2 |

## Components

| Component | Service rasters | Panel candidates/crops | Reference uses | Zero-reference | Timing scope |
| --- | ---: | ---: | ---: | ---: | --- |
| `base_ch05_r6` | 16 | 59 | 34 | 0 | TWO_REPORTED_NON_EQUIVALENT_SCOPES: 1592.908 s summed observations; ~1200.7 s overlap-adjusted |
| `alternate_graphic` | 11 | 50 | 23 | 0 | OVERLAP_ADJUSTED_TOOL_CALL_BATCH_WALL: 954.3 s |
| `clear_line_watercolor` | 11 | 50 | 23 | 0 | OVERLAP_ADJUSTED_TOOL_CALL_BATCH_WALL: 1090.0 s |
| `premium_cel` | 11 | 50 | 23 | 0 | OVERLAP_ADJUSTED_TOOL_CALL_BATCH_WALL: 1234.0 s |
| `flat_graphic_gouache` | 11 | 50 | 23 | 0 | NON_OVERLAP_OBSERVED_ARITHMETIC: 1290.989 s |
| `reduced_palette_text_control` | 11 | 50 | 0 | 11 | NON_OVERLAP_OBSERVED_ARITHMETIC: 1027.652 s |
| `premium_targeted_repair_trio` | 3 | 3 | 6 | 0 | ONE_CONCURRENT_BATCH_WALL: 169.0 s |
| `ng-ch05-s01-flat-gouache-reference-ablation-execution-r1` | 1 | 0 | 0 | 1 | INDIVIDUAL_TOOL_CALL_WALL: 110.4 s |
| `ng-ch05-s11-flat-gouache-reference-ablation-execution-r1` | 1 | 0 | 0 | 1 | INDIVIDUAL_TOOL_CALL_WALL: 48.2 s |

## Six-route subset relationship

300 = 50 selected r6 + 250 five-arm crops; 312 = 300 + 9 additional r6 candidates + 3 premium targeted-repair candidates.

The two no-reference ablation strips are service outputs but were never split into panel candidates. Their five-plus-three plan coverage must not be counted as eight crops.

## Timing boundary

Aggregate end-to-end time is deliberately `null`. The source records mix summed per-execution observations, approximate overlap-adjusted client wall, overlap-adjusted batch wall, non-overlap arithmetic, one concurrent-batch wall, and individual call walls. A mechanical sum is prohibited because it would not represent elapsed production time.

## Exact source bindings

| Path | SHA-256 | Git blob OID | Bytes |
| --- | --- | --- | ---: |
| `docs/research/evidence/ch05-complete-chapter-release-r6.json` | `62e4d4bac75a16470055d31a05c639acbfd18523bf80b9f7711fdaa717898d24` | `e0ae33debd4a95d45243d9c153b6938347c6d762` | 9331 |
| `production/comic/run-manifests/ch05-complete-chapter-production-manifest-r6.json` | `a4cfadd90282e408ba00f407608d3c09637be2ef3eddb2f2045901738dce27c9` | `8362be8d041dbbfcb83f825c0f839aab9d98f4c7` | 339430 |
| `production/comic/run-manifests/ch05-complete-chapter-alt-graphic-execution-manifest-r1.json` | `e0a3d34840788822455b9a8c57fba8caac3ae0628c038d084c1da7eabd390cf7` | `5071fe6206f573b483f63fffa0392ff2c2809e54` | 69274 |
| `production/comic/run-manifests/ch05-complete-chapter-alt-graphic-crops-r1.json` | `6f07eebc29c399945e68c8aea821872368990c5fece91bdc29269d3580032b48` | `93828f4e5f21700ab872099f75d4eb18119d8b09` | 18956 |
| `production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-execution-manifest-r1.json` | `d06bdeeb9e756944665966f49ab3f3b2a94871ac5fc15935544a2ec6d1a45aec` | `589ba945cd430921b45c5ff2630b09276a311bc8` | 72721 |
| `production/comic/run-manifests/ch05-complete-chapter-clear-line-watercolor-crops-r1.json` | `9beb49a361d62783a59f4139f421ccd16f6388a69c53739d7de438cd50762995` | `24231a72a97ae3aa5a1676688c5256aa95f07621` | 19648 |
| `production/comic/run-manifests/ch05-complete-chapter-premium-cel-execution-manifest-r1.json` | `acff13c33ec311a78fe8e6007bd46549cc2e633a37db8c11a387cda01d6f3e71` | `2357e0f639835f4e5cf164eba62e88687ebd41f8` | 75568 |
| `production/comic/run-manifests/ch05-complete-chapter-premium-cel-crops-r1.json` | `d78c91832835e09096a6eefe342dc6e5f01a17046a58a2031ed2e0a8fe7687e1` | `9d6d75af19d65ffa671740fe95c1398c4b844ea1` | 26635 |
| `production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-execution-manifest-r1.json` | `66c389df75bea35ec7cf9165fda1c10293f48b1c11444e4b41d418b1d1223f3c` | `26b46afe029962267f4f82146a98edd0f632f428` | 79917 |
| `production/comic/run-manifests/ch05-complete-chapter-flat-graphic-gouache-crops-r1.json` | `c731393f250d801a072ed712beec04421abd59f6cdbdf256d0134bac2e6caa6b` | `d80d0ebfcc64b4ff2b3146d5608373d0401d36ae` | 27082 |
| `production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-execution-manifest-r1.json` | `2e978b4f04d1cd7b7a660105d2e230a880d3df3e1d27a22c6bc78fa0639aa663` | `1cb0076fb55f4bc2cb6c0eb1303c937874f9692d` | 76316 |
| `production/comic/run-manifests/ch05-complete-chapter-reduced-palette-text-control-crops-r1.json` | `5b02a8912aa0dd888e9199f0df6d2654f680417f49c29b53d96278f751dba31c` | `eab0ef21c207eddbd358ae6020b5750c08813484` | 29015 |
| `production/comic/run-manifests/ch05-premium-cel-targeted-repair-trio-execution-r1.json` | `23e399329bfe22cb0732f7ba5d147a56e178c081709340926f6e9fa18b81b28f` | `2ffaf5cd48f8bc06fc030ba36097126e342d2bd7` | 22590 |
| `production/comic/run-manifests/ch05-s01-flat-gouache-reference-ablation-execution-r1.json` | `5aadac1d124a9ff82b36b952962ea0ebeeaeae1071f3fb368bb2bf0a67a3e7b1` | `c5131fb2b00c55d1e368b87c4c9e1f9769eee7d6` | 8884 |
| `production/comic/run-manifests/ch05-s11-flat-gouache-reference-ablation-execution-r1.json` | `db354de35eb9672be42329419fe9b122c15b301111ebe360e9ff8919e2294619` | `58a71bf98348b5f024199d1af06bf26c80fc1257` | 8481 |

## Boundary

Deterministic accounting evidence only. No pixels, provider call, upload, spend, acceptance, rights, or production state is created by this package.
