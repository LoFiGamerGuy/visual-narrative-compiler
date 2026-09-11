# Chapter9 package helper support

Checked 2026-09-11T00:32:56.038305+00:00. Changed only three routine declarations in `production/nightglass-longform/package/pack.py`: add `ninechapters` to required reviewed chapters1–9, its starter label, and CLI milestone choices. All previous choices remain. No collector, copy, archive, alias or strict-verifier behavior changed.

Pack SHA-256 before: `8c17ed6c33adb717929586229d93fae952c82e6474237782aea804a123183f17`.
Pack SHA-256 after: `f47b38cc440668fbe6d15ef39949fd6bc0b528b2f97acae800b620c787e9857e`.
Strict verifier unchanged SHA-256: `51839fa317168db31114a4191c861da496f0735ad06e03b867511018df71054b`.

Validation: in-memory Python syntax compile PASS; exact three-declaration diff against Git HEAD PASS; AST gate/list/label/CLI consistency PASS; collector and build function ASTs unchanged. Static required list is exactly1–9. Existing build still calls completion gate before collector/copy/output creation. No gate/build/browser/ZIP was invoked. Current reader9 at this check: 24/42, complete=False; no claim of final Chapter9 completion.

Future supported invocation, ONLY after root’s completed-reading/source-freeze release:

```bash
python production/nightglass-longform/package/pack.py build --source /mnt/c/AgentWorkspaces/anime-pipeline-nightglass-longform-20260909-2110 --version Nightglass-NineChapters-v1 --milestone ninechapters --output /mnt/c/AgentWorkspaces/anime-pipeline-nightglass-longform-20260909-2110/production/nightglass-longform/package/output
```

At this check the unique version staging/ZIP/verification paths were all absent: True. Recheck uniqueness when actually released. Earlier outputs were neither opened for mutation nor rebuilt. Strict verifier already derives chapter routes from the snapshot; nine complete chapters would give23 routes including the existing fixed routes and two dialogs. This is readiness only, not an executed package or portability claim.
