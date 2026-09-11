# Verification and its limits

The reader and local-correction workflow pass their implementation checks. Strict protected-filesystem equality **does not pass** because executing the existing Windows Blender installation created bytecode caches and changed two binary ctimes. The exact discrepancy is retained below; a clean Git status is not presented as complete filesystem preservation.

## Implementation and visual delivery

The persisted-lettering bridge passed ten targeted tests, including stale source/plan rejection, exact-copy preservation, protected-context rejection and successful versioned application. Actual browser exports were applied through that bridge; this is more than a simulated JSON round trip. [Draft QA](../../docs/research/structural-pilot/reader/draft-application-qa.json) and the immutable layout histories preserve the evidence.

Both the [SC reader QA](../../docs/research/structural-pilot/reader/browser-qa.json) and [CF reader QA](../../docs/research/structural-pilot/correction-reader/browser-qa.json) cover 390×844, 1024×768 and 1440×1000. Each available route loads fourteen of fourteen images, with no horizontal overflow or runtime exceptions. P11/P14 exact-copy glyphs fit the canvas and meet the checked lettering geometry. Final S14 tails clear the hair; the independently reported CF14 tail problem was corrected and [rechecked](independent-P14-lettering-recheck.md). Actual-art inspection remains separate from these layout facts.

SC [source links](../../docs/research/structural-pilot/reader/source-link-qa.json), CF [source links](../../docs/research/structural-pilot/correction-reader/source-link-qa.json) and [comparison bindings](../../docs/research/structural-pilot/comparison-bindings.json) bind selected display pixels to the recorded source. Final S09/S14 portable SVGs use external PNGs and reproduce the inline originals' PNG and RGBA bytes exactly. The [asset bundle validation](asset-bundle/validation.json) verifies all 613 members, complete empty-directory restoration, collision refusal and deterministic archive rebuilding.

The [handoff browser check](handoff-browser-qa.json) passes for both entry and comparison pages at all three sizes: twelve comparison images decode, eighteen local links resolve, and no target-page overflow or browser error occurs. Actual screenshots show uncropped stacked phone canvases and paired desktop canvases. The first run's prior-reader `beforeunload` intervention is preserved separately; final checks used a fresh tab. This was a test-state issue, not a suppressed target error.

The saved Blender scene passed 154 deterministic control checks. Actual saved-mesh and alpha inspection confirmed exactly three semantic legs, canonical intact/broken staff lengths, the shared P08/P09 restraint anchor and a solid shutter partition spanning the gallery. These checks did not prevent the final S artwork from looking diagram-like, or the G artwork from losing exact contact. [Control verification](../../production/structural-pilot/control/verification.json) is therefore not an art score.

The reused [raw attempt ledger](evidence/ledger-final-status.json) has no integrity failures and retains thirteen candidates, thirteen actual observation events and eleven failed attempts. No raw draft is falsely selected as a finished composite. Its pending phone-review field applies to that backend's unselected raw draft; the separately bound reader has actual phone QA. No human or owner acceptance is manufactured by either record.

## Protected-state finding

The initial baseline covers eleven prior worktrees. [The full comparison](evidence/protected-comparison.json) checks the same file list and metadata/content-hash policy, not a newly relaxed baseline. All ten sibling worktrees match. Every prior HEAD, Git status and pre-existing branch/remote ref matches. All previously hashed code/text and delivered pilot art match. No old file was deleted, and no existing file changed size, mtime or mode.

The protected root differs in exactly **93 entries**: [91 newly created Python bytecode cache files](evidence/runtime-additions.json) inside the Blender installation, plus ctime-only changes on `blender.exe` and `5.2/python/DLLs/libffi-8.dll`. [Both binaries match the bytes in the preserved original installation ZIP](evidence/runtime-existing-changes.json). Their binary contents were not hashed in the initial proportionate baseline, so the archive match is supporting evidence rather than a retroactive baseline hash. The exact cause of Windows ctime changes was not independently established. The bytecode paths and timing are consistent with the embedded Python imports used by this task.

Factory startup and task-owned Blender config/temp paths did not prevent embedded Python from writing its import caches beside the installed modules. This was an isolation shortfall. All additions and the original failed comparison are retained; no cleanup is used to hide them. Future use of a protected executable should suppress bytecode before startup and isolate the executable itself if metadata immutability is required. No further Blender execution is needed for this delivery.

The [final Git/ref recheck](evidence/final-protected-status.json) supplements this full scan. Its `pass` means prior Git states and refs match; it does not override the full scan's `pass:false`. The final delivery separately records exact new-branch remote parity and clean tracked checkout.

## Acceptance still absent

Independent AI reviewers saw actual source and phone images before the author's preferred new-candidate verdict. They were exposed to some historical baseline findings, which is disclosed in their records. Neutral route labels and AI review are not an independent human study. Continuous inspection found repeated gallery, flask and threat design changes; P11's motion redirection and P13's tiny pin detail remain limited at phone scale. Owner preference, independent human comprehension and commercial clearance remain null. No named quality-target equivalence is claimed.
