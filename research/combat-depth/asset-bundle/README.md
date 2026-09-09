# Portable combat-depth delivery

Generation is closed for CD-20260908-01: 54 retained native artworks (24P, 6R1, 24F1), 55 invocations including one rejected W06 input and its corrected resubmission, and no pending calls. Strict preflight passed; create the final archive only after the lead freezes and commits the complete source delivery. The frozen budget is 24 primaries, at most 6 structural repairs and 24 source-only surface finishes: at most 54 native artworks and 56 service invocations. Up to two no-art failures may each receive one retry. Transport retries are unchanged. The single typed W06-P input-validation exception may remove only redundant W01 from its rejected six-reference request, yielding five; no other creative changes are permitted. No budget amendment is supported.

From the new experiment root:

```sh
python3 research/combat-depth/asset-bundle/bundle_assets.py self-test
python3 research/combat-depth/asset-bundle/bundle_assets.py inspect
# Only after the lead freezes all artwork, selections, notes and reader output:
python3 research/combat-depth/asset-bundle/bundle_assets.py create --expected-art 54 --output research/combat-depth/asset-bundle/local/final-v1
```

`inspect` permits missing planned primaries but rejects broken registered bindings. `create` requires all 24 primaries and selected displays plus the explicitly supplied actual native count. It preserves each output version and verifies archive SHA256, bytes, CRC and every member hash, then restores into a fresh folder and rebuilds the copied reader. Both data.json and data.js must remain byte-identical. Exact inventory is checked before and after rebuilding; HTML/CSS/data paths resolve locally, respecting query strings and fragments. Failed integration evidence is retained, with no automatic rerun or overwrite.

Payload: all classified files in production/combat-depth, research/combat-depth and docs/combat-depth; root AGENTS.md; the saved textual texture skill and guide; root-mapped Windows launcher and instructions. Native art includes every retained attempt, copied reference and editable control render. Control PNGs are bound separately to their SVG sources and never counted as generated art. All prompts, calls, jobs, prior choices, reports and review sources in these namespaces are included. Unknown file types fail inspection. Exclusions are explicit runtime/cache/browser/venv, .scratch, local, Git directories and self archives; no previous galleries or external original tool-return files are copied. Root final receipts are external to avoid circular hashes.

Actual calls must bind the exact prompt, local references, control SVGs and frozen plan version. Current plan.json and preserved plan-history/plan-vN.json are indexed by exact SHA256. Each full version requires a matching .sha256 sidecar, exact CD identity/24 IDs and unchanged budget. Every call hash must resolve to one preserved full version; the report records its path without rewriting older calls. A superseded unrun job may bind its embedded prompt to exactly one preserved identical prompt under production/combat-depth/unrun; actual calls have no such fallback. One F1 per candidate must reference only its exact retained native. All returned calls must be registered at final closure; failed service requests count toward 56 but are not native artworks. Retry failure hashes, prompt/reference equality and limits are validated. Browser behavior and visual acceptance remain separate checks.

```sh
python3 research/combat-depth/asset-bundle/bundle_assets.py verify --archive PATH/combat-depth-portable.zip --receipt PATH/archive-receipt.json
python3 research/combat-depth/asset-bundle/bundle_assets.py restore --archive PATH/combat-depth-portable.zip --receipt PATH/archive-receipt.json --target NEW_OR_MATCHING_CHECKOUT
python3 research/combat-depth/asset-bundle/bundle_assets.py rebuild-check --target NEW_OR_MATCHING_CHECKOUT
python3 research/combat-depth/asset-bundle/check_preservation.py --output research/combat-depth/asset-bundle/local/preservation-post-push-v1.json
```

The lead may commit frozen sources first, then create the archive and export that exact Git commit into a new ignored directory for additive restore/rebuild verification. Keep post-freeze receipts ignored. Existing byte-identical files are skipped; any different hash, symlink, case collision or file/directory conflict rejects the complete restore preflight before writing. New files use exclusive creation. Run against a quiescent target; restore is not a transaction against concurrent hostile filesystem changes. Never rebuild the original source root.

Archive limits are 5000 files, 256 MiB each, 8 GiB total and 8 MiB manifest. Absolute/traversal/Windows-reserved paths, duplicate/case-colliding entries, encryption, symlinks and unexpected members fail. Integrity receipts are not cryptographic signatures; share the trusted archive hash separately. The viewer needs no account, server or paid API. Optional verification/rebuild uses Python standard library.

The preservation checker uses the exact status argv recorded in protected-initial.json: git status --porcelain=v1 --untracked-files=all --ignored=matching. It checks all 20 prior HEAD/status digests, 65 saved original content hashes, old local refs and precreation worktree topology. Exactly one new active worktree and its fixed branch/tracking refs are permitted; no other topology/ref changes. Git pointer normalization handles Windows roots, with optional locks and fsmonitor disabled. Ignored path inventory is covered at Git reporting granularity; arbitrary ignored/cache bytes and unsaved dirty-file content are not hashed. Remote server parity is a separate lead check. This read-only audit spans an interval, not an atomic snapshot.

W06 input-validation failure is preserved separately from transport failures, including its exact raw six-reference request, old prompt, archived plan and caught-error sidecar. The corrected request binds that failure SHA and a distinct new prompt. Validation requires exact remaining reference order/hashes, unchanged W06 scene/state, and prompt equality after only removing Image 5 and renumbering Image 6. One corrected invocation consumes one of the existing two no-art retry slots; the rejected request and retry both count toward 56, while a returned W06-P remains one primary artwork. No ordinary request/job may exceed five references; only the exact preserved rejected job is retained as historical evidence.
